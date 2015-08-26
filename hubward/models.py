import yaml
from textwrap import dedent
from jsonschema import validate, ValidationError
import pyaml
import json
import os
import glob
import subprocess
from colorama import init, Fore, Back, Style
from trackhub import Track, default_hub, CompositeTrack, ViewTrack
import pkg_resources
from hubward import utils
from hubward.log import log

HERE = os.path.abspath(os.path.dirname(__file__))
SCHEMA = json.loads(utils.get_resource('schema.json'))


class Data(object):
    def __init__(self, obj, reldir):
        """
        Represents a single track destined for upload to UCSC as a track hub.

        Parameters
        ----------
        obj : dict
            One entry from the `data` list in a metadata file.

        reldir : str
            The dirname of the metadata file.  All paths (specifically,
            "original", "processed", and "script", are assumed to be relative
            to to `reldir`.
        """
        self.obj = obj
        self.reldir = reldir
        self.original = os.path.join(reldir, obj['original'])
        self.processed = os.path.join(reldir, obj['processed'])
        self.description = obj['description']
        self.label = obj['label']
        self.type_ = obj['type']
        self.genome = obj['genome']
        self.script = os.path.join(reldir, obj['script'])
        try:
            self.trackinfo = obj['trackinfo']
        except KeyError:
            self.trackinfo = {}

    def __str__(self):
        return pyaml.dumps(self.obj)

    def needs_update(self):
        if not os.path.exists(self.processed):
            return True
        if (

            # if processed is a link, then check the LINK time
            utils.link_is_newer(self.script, self.processed) or

            # but for the original data, we want to FOLLOW the link
            utils.is_newer(self.original, self.processed)
        ):
            return True

    def process(self):
        """
        Runs the processing script, which must accept 2 args, the absolute path
        of the original file and absolute path of the processed file.

        It's up to the processing script to handle everything else.
        """
        cmds = [
            self.script,
            self.original,
            self.processed]
        if not os.path.exists(self.original):
            raise ValueError(
                "Original data file %s does not exist" % self.original)
        if not os.path.exists(self.script):
            raise ValueError(
                "Script %s does not exist" % self.script)
        p = subprocess.Popen(
            cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = p.communicate()
        except OSError:
            print "Commands were", ' '.join(cmds)
            raise

        if p.returncode:
            msg = 'CMDS: %s' % (' '.join(cmds))
            msg += '\n'
            msg += 'STDERR: %s' % stderr
            raise ValueError(msg)

        if self.needs_update():
            print(
                Fore.RED + 'The following command did not update '
                '{1}:\n\n{0}\n'.format(' \\\n'.join(cmds), self.processed) +
                Fore.RESET
            )


class Study(object):
    def __init__(self, fn):
        """
        Represents a study documented in a single JSON or YAML file, with
        dictionary keys mapped to easier-to-access attributes.

        Validates against "schema.json" upon loading.

        Parameters
        ----------

        fn : JSON or YAML format file.

        """
        ext = os.path.splitext(fn)[-1]
        if ext == '.json':
            self.metadata = json.load(open(fn))
        elif ext == '.yaml':
            self.metadata = yaml.load(open(fn))

        # validation happens here...
        validate(self.metadata, SCHEMA)
        self.filename = fn
        self.pmid = self.metadata['study']['PMID']
        self.description = self.metadata['study']['description']
        self.reference = self.metadata['study']['reference']
        self.label = self.metadata['study']['label']
        self.sanitized_label = utils.sanitize(self.label, strict=True)
        self.dirname = os.path.abspath(os.path.dirname(fn))
        self.processing = self.metadata['study']['processing']

        self.data = [
            Data(d, os.path.dirname(fn)) for d in self.metadata['data']]

    def __str__(self):
        return pyaml.dumps(self.json)

    def build_metadata(self):
        dirname = os.path.dirname(self.filename)
        cmds = ['cd', dirname, '&&', 'python', 'metadata-builder.py']
        os.system(' '.join(cmds))

    def process(self, force=False):
        log('Study: {0.description}, in "{0.dirname}"'.format(self),
            style=Fore.BLUE)
        for d in self.data:
            if d.needs_update() or force:
                log(
                    'Converting "%s" -> "%s"' %
                    (os.path.relpath(d.original, d.reldir),
                     os.path.relpath(d.processed, d.reldir),
                     ),
                    indent=4)

                d.process()
            else:
                log(
                    'Up to date: "%s"' %
                    os.path.relpath(d.processed, d.reldir), style=Style.DIM,
                    indent=4)
                continue

    def reference_section(self):
        if not (self.reference or self.pmid):
            return ""
        if not self.reference:
            reference = ""
        else:
            reference = self.reference
        if not self.pmid:
            pmid = ""
        else:
            pmid = 'http://www.ncbi.nlm.nih.gov/pubmed/{0}'.format(self.pmid)
        return dedent(
            """
            Reference
            ---------
            {0}

            {1}
            """).format(reference, pmid)

    def composite_track(self):
        """
        Create a composite track ready to be added to a trackhub.TrackDb
        instance.
        """
        bigwigs = [i for i in self.data if i.type_ == 'bigwig']
        bigbeds = [i for i in self.data if i.type_ == 'bigbed']

        # Build the HTML docs
        last_section = self.reference_section()
        html_string = utils.reST_to_html(self.processing + last_section)

        composite = CompositeTrack(
            name=utils.sanitize(self.label, strict=True),
            short_label=self.description,
            long_label=self.description,
            html_string=html_string,
            tracktype='bigBed')

        # If there are any bigWigs defined for this study, make a new "signal"
        # subtrack in the composite and then add the bigWigs to it.
        if len(bigwigs) > 0:
            signal_view = ViewTrack(
                name=self.sanitized_label + 'signalviewtrack',
                view=self.sanitized_label + 'signalview',
                short_label=self.label + ' signal view',
                long_label=self.label + ' signal view',
                visibility='full',
                maxHeightPixels='100:25:8',
                autoScale='off',
                tracktype='bigWig',
            )
            composite.add_view(signal_view)
            for bigwig in bigwigs:

                # See if the config defined a trackinfo section which we
                # interpret as kwargs to trackhub.Track
                try:
                    kwargs = bigwig.trackinfo
                except AttributeError:
                    kwargs = {}
                kwargs = dict((k, str(v)) for k, v in kwargs.items())
                signal_view.add_tracks(
                    Track(
                        # tracks are named after the study and the label to hopefull
                        # ensure uniqueness across the entire hub
                        name=self.sanitized_label + utils.sanitize(bigwig.label),
                        short_label=bigwig.label,
                        long_label=bigwig.description,
                        local_fn=bigwig.processed,
                        tracktype='bigWig',
                        **kwargs
                    )
                )

        # Same thing with bigBeds
        if len(bigbeds) > 0:
            bed_view = ViewTrack(
                name=self.sanitized_label + 'bedviewtrack',
                view=self.sanitized_label + 'bed_view',
                short_label=self.label + ' bed view',
                long_label=self.label + ' bed view',
                visibility='dense',
            )
            composite.add_view(bed_view)
            for bigbed in bigbeds:
                try:
                    kwargs = bigbed.trackinfo
                except AttributeError:
                    kwargs = {}
                track_kwargs = dict(
                        name=self.sanitized_label + utils.sanitize(bigbed.label),
                        short_label=bigbed.label,
                        long_label=bigbed.description,
                        local_fn=bigbed.processed,
                        tracktype='bigBed 9'
                )
                track_kwargs.update(**kwargs)

                bed_view.add_tracks(Track(**track_kwargs))

        return composite


class Lab(object):
    def __init__(self, directory):
        self.studies = []
        for metadata in glob.glob(os.path.join(directory, '*', 'metadata.yaml')):
            self.studies.append(Study(metadata))
