import os
import stat
import shutil
import tempfile
from colorama import init, Fore, Back, Style
from textwrap import dedent
import yaml
import jsonschema
import subprocess
from trackhub import Track, default_hub, CompositeTrack, ViewTrack
from trackhub.upload import upload_hub, upload_track, upload_file
from hubward import utils, liftover
from hubward.log import log


class Data(object):
    def __init__(self, obj, reldir):
        """
        Represents a single track destined for upload to UCSC as part of
        a track hub.

        Parameters
        ----------
        obj : dict
            One entry from the `tracks` list in the metadata.yaml file

        reldir : str
            The directory name of the metadata file. All paths within the
            metadata file are assumed to be relative to `reldir`.
        """
        self.obj = obj
        self.reldir = reldir
        self.original = os.path.join(reldir, obj['original'])
        self.source_url = obj['source']['url']
        self.source_fn = os.path.join(reldir, 'raw-data', obj['source']['fn'])
        self.processed = os.path.join(reldir, obj['processed'])
        self.description = obj.get('description', "")
        self.label = obj['short_label']
        self.obj.setdefault('long_label', self.label)
        self.type_ = obj['type']
        self.genome = obj['genome']
        self.script = os.path.join(reldir, obj['script'])
        self.trackinfo = obj.get('trackinfo', {})

    def __str__(self):
        return yaml.dump(self.obj)

    def _needs_download(self):
        if not os.path.exists(self.original):
            return True

    def _was_lifted_over(self):
        if os.path.exists(os.path.join(self.reldir, 'ORIGINAL-STUDY')):
            return True

    def _download(self):
        """
        Downloads and unpacks the source to `raw-data`.

        After doing so, if self.original still does not exist, then raises
        a ValueError.
        """
        log(
            "Downloading '%s' -> '%s'" %
            (self.source_url, self.source_fn), indent=4)
        if not os.path.exists(os.path.dirname(self.source_fn)):
            os.makedirs(os.path.dirname(self.source_fn))
        utils.download(self.source_url, self.source_fn)
        utils.unpack(self.source_fn, os.path.dirname(self.source_fn))

        if self._needs_download():
            raise ValueError(
                "Downloading and unpacking '%s' did not result in '%s'"
                % (self.source_url, self.source_fn))

    def _needs_update(self):
        """
        Decides if we need to update the processed file.
        """
        do_update = False
        if self._was_lifted_over():
            log(
                "This file appears to have been lifted over from another "
                "study, in which case we assume it does not need updating",
                style=Fore.YELLOW
            )
            return False
        if self._needs_download():
            log("{0.original} does not exist; downloading"
                .format(self, indent=4))
            self._download()
            do_update = True

        if not os.path.exists(self.processed):
            log("{0.processed} does not exist".format(self), indent=4)
            do_update = True

        # if processed is a link, then check the LINK time
        if (
            os.path.exists(self.processed) and
            utils.link_is_newer(self.script, self.processed)
        ):
            log("{0.script} is newer than {0.processed}, need to re-run"
                .format(self), indent=4)
            do_update = True

        # but for the original data, we want to FOLLOW the link
        if (
                os.path.exists(self.original) and
                os.path.exists(self.processed) and
                utils.is_newer(self.original, self.processed)
        ):
            log("{0.original} is newer than {0.processed}, need to re-run"
                .format(self), indent=4)
            do_update = True

        if not do_update:
            log("{0.processed} is up to date"
                .format(self), indent=4, style=Style.DIM)

        return do_update

    def process(self):
        """
        Run the conversion script if the output needs updating.
        """
        # Note: _needs_update() does the logging.
        if not self._needs_update():
            return

        if not os.path.exists(self.script):
            raise ValueError(
                "Processing script {0.script} does not exist".format(self))

        if not (stat.S_IXUSR & os.stat(self.script)[stat.ST_MODE]):
            raise ValueError(
                Fore.RED +
                "Processing script {0.script} not executable".format(self) +
                Fore.RESET)

        utils.makedirs(os.path.dirname(self.processed))

        cmds = [
            self.script,
            self.original,
            self.processed
        ]
        retval = subprocess.check_call(cmds)
        if self._needs_update():
            raise ValueError(
                Fore.RED + 'The following command did not update '
                '{1}:\n\n{0}\n'.format(' \\\n'.join(cmds), self.processed) +
                Fore.RESET
            )

    def _needs_liftover(self, from_assembly, to_assembly, newfile):

        # Sentinel file encodes
        sentinel = self._liftover_sentinel(from_assembly, to_assembly, newfile)
        if not os.path.exists(sentinel):
            return True
        elif utils.is_newer(self.processed, newfile):
            return True
        return False

    def _liftover_sentinel(self, from_assembly, to_assembly, newfile):
        return os.path.join(
            os.path.dirname(newfile),
            '.{0}-to-{1}.' +
            os.path.basename(newfile)
        ).format(from_assembly, to_assembly)

    def liftover(self, from_assembly, to_assembly, newfile):
        """
        Lifts over the processed file to a new file, but only if needed.

        Uses a hidden sentinel file to indicate whether it's been lifted over.

        Parameters
        ----------

        from_assembly : str
            Existing data are in this assembly's coordinates

        to_assembly : str
            Lift over existing data to this assembly's coordinates

        newfile : str
            Target filename of the lifted-over data
        """

        if not from_assembly == self.genome:
            log(
                "{0} not from assembly {1}. Skipping liftover from {1} to {2} "
                "and simply copying the file as-is to {3}"
                .format(self.label, from_assembly, to_assembly, newfile)
            )
            shutil.copy(self.processed, newfile)

        if not self._needs_liftover(from_assembly, to_assembly, newfile):
            log("{0} is already lifted over and up-to-date. Skipping."
                .format(newfile))
            return

        tmp = tempfile.NamedTemporaryFile(delete=False).name
        log("Lift over {0} to {1}".format(self.processed, tmp))
        liftover.liftover(
            from_assembly, to_assembly, self.processed, tmp, self.type_)
        utils.makedirs(os.path.dirname(newfile))
        log("Moving {0} to {1}".format(tmp, newfile))
        shutil.move(tmp, newfile)

        # CrossMap.py seems to `chmod go-rw` on lifted-over file. So we copy
        # permissions from the original one.
        shutil.copymode(self.processed, newfile)

        # Write the sentinel file to indicate genome we lifted over to.
        sentinel = self._liftover_sentinel(from_assembly, to_assembly, newfile)
        with open(sentinel, 'w') as fout:
            pass


class Study(object):
    def __init__(self, dirname):
        """
        Represents a single metadata.yaml file.

        Parameters
        ----------

        fn : filename of YAML- or JSON-formatted config file
        """
        self.dirname = dirname
        self._build_metadata()
        fn = os.path.join(self.dirname, 'metadata.yaml')

        if not os.path.exists(fn):
            raise ValueError("Can't find {0}".format(fn))

        self.metadata = yaml.load(open(fn))
        schema = yaml.load(utils.get_resource('metadata_schema.yaml'))
        jsonschema.validate(self.metadata, schema)
        self.study = self.metadata['study']
        self.label = self.metadata['study']['label']

        self.study.setdefault('short_label', self.label)
        self.study.setdefault('long_label', self.study['short_label'])
        self.study['PMID'] = str(self.study.get('PMID', ''))
        self.tracks = [Data(d, self.dirname) for d in self.metadata['tracks']]

        # If description is blank or missing, fill in the contents of the
        # README.
        if not self.study.get('description', ''):
            readme = self._find_readme()
            if readme:
                self.study['description'] = open(readme).read()


    def _find_readme(self):
        contents = os.listdir(self.dirname)

        valid_readmes = [
            'README.rst',
            'README',
            'readme.rst',
            'readme']
        if 'ORIGINAL-STUDY' in contents:
            prefix = os.path.join(self.dirname, 'ORIGINAL-STUDY')
        else:
            prefix = self.dirname

        for filename in contents:
            if filename in valid_readmes:
                return os.path.join(prefix, filename)

    def __str__(self):
        return yaml.dump(self.metadata)

    def _was_lifted_over(self):
        if os.path.exists(os.path.join(self.dirname, 'ORIGINAL-STUDY')):
            return True

    def _build_metadata(self):
        """
        If metadata-builder.py exists, always run it.
        """
        builder = os.path.join(self.dirname, 'metadata-builder.py')
        if not os.path.exists(builder):
            return

        log("{0} exists. Running it...".format(builder))
        metadata = os.path.join(self.dirname, 'metadata.yaml')
        if os.path.exists(metadata):
            backup = os.path.join(self.dirname, 'metadata.yaml.bak')
            shutil.copy(metadata, backup)
            log("Existing {0} backed up to {1}"
                .format(metadata, backup))

        if not (stat.S_IXUSR & os.stat(builder)[stat.ST_MODE]):
            raise ValueError(
                Fore.RED +
                "{0} not executable".format(builder) +
                Fore.RESET)
        cmds = ['./metadata-builder.py']
        retval = subprocess.check_call(cmds, cwd=self.dirname)

        if not os.path.exists(metadata):
            raise ValueError("Expected {0} but was not created by {1}"
                             .format(metadata, builder))

    def process(self, force=False):
        log('Study: {0.study[label]}, in "{0.dirname}"'.format(self),
            style=Fore.BLUE)
        for d in self.tracks:
            d.process()

    def reference_section(self):
        """
        Creates a ReST-formatted reference section to be appended to the end of
        the documentation for the composite track config page.

        If no configured reference or PMID, then return an empty string.
        """
        reference = self.study.get('reference', "")

        # Allow "0001111", "PMID:0001111", "PMID: 0001111"
        pmid = self.study.get('PMID', "").split(':')[-1].strip()

        if not (reference or pmid):
            return ""

        if pmid:
            pmid = 'http://www.ncbi.nlm.nih.gov/pubmed/{0}'.format(pmid)
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
        bigwigs = [i for i in self.tracks if i.type_ == 'bigwig']
        bigbeds = [i for i in self.tracks if i.type_ == 'bigbed']

        # Build the HTML docs
        last_section = self.reference_section()
        html_string = utils.reST_to_html(
            self.metadata['study'].get('description', '') + '\n' + last_section)

        sanitized_label = utils.sanitize(self.label, strict=True)

        # Composite track to hold all subtracks for the study
        composite = CompositeTrack(
            name=sanitized_label,
            short_label=self.study['short_label'],
            long_label=self.study['long_label'],
            tracktype='bigBed',

            # Add all the documentation
            html_string=html_string)

        # If there are any bigWigs defined for this study, make a new "signal"
        # subtrack in the composite and then add the bigWigs to it.
        #
        # Uses the sanitized label for the study to ensure uniqueness among
        # tracks.
        #
        def _add_tracks(data_list, view, default_tracktype):
            for data_obj in data_list:
                kwargs = data_obj.obj.get('trackinfo', {})
                kwargs = dict((k, str(v)) for k, v in kwargs.items())
                kwargs.setdefault('tracktype', default_tracktype)
                view.add_tracks(
                    Track(
                        name=sanitized_label + utils.sanitize(data_obj.label),
                        short_label=data_obj.label,
                        long_label=data_obj.obj['long_label'],
                        local_fn=data_obj.processed,
                        **kwargs))

        if len(bigwigs) > 0:
            signal_view = ViewTrack(
                name=sanitized_label + 'signalviewtrack',
                view=sanitized_label + 'signalview',
                short_label=self.label + ' signal view',
                long_label=self.label + ' signal view',
                visibility='full',
                maxHeightPixels='100:25:8',
                autoScale='off',
                tracktype='bigWig',
            )
            composite.add_view(signal_view)

            _add_tracks(bigwigs, signal_view, 'bigWig')

        # Same thing with bigBeds
        if len(bigbeds) > 0:
            bed_view = ViewTrack(
                name=sanitized_label + 'bedviewtrack',
                view=sanitized_label + 'bed_view',
                short_label=self.label + ' bed view',
                long_label=self.label + ' bed view',
                visibility='dense',
            )
            composite.add_view(bed_view)
            _add_tracks(bigbeds, bed_view, 'bigBed 9')

        return composite


class Group(object):
    def __init__(self, fn):
        self.group = yaml.load(open(fn))
        self.filename = fn
        self.dirname = os.path.dirname(fn)
        self.group.setdefault('short_label', self.group['name'])
        self.group.setdefault('long_label', self.group['name'])

        schema = yaml.load(utils.get_resource('group_schema.yaml'))
        jsonschema.validate(self.group, schema)
        self.studies = [
            Study(os.path.join(self.dirname, s))
            for s in self.group['studies']
        ]

    def process(self):
        hub, genomes_file, genome_, trackdb = default_hub(
            hub_name=self.group['name'],
            genome=self.group['genome'],
            short_label=self.group['short_label'],
            long_label=self.group['long_label'],
            email=self.group['email'],
        )
        hub.url = self.group['hub_url']

        # Process each study, and have it generate its own composite track to
        # be added to the trackdb.
        for study in self.studies:
            study.process()
            composite = study.composite_track()
            trackdb.add_tracks(composite)


        self.hub = hub
        self.genomes_file = genomes_file
        self.genome_ = genome_
        self.trackdb = trackdb

    def upload(self, hub_only=False, host=None, user=None, rsync_options=None,
               hub_remote=None):
        self.process()

        if 'server' in self.group:
            host = host or self.group['server'].get('host')
            user = user or self.group['server'].get('user')
            rsync_options = rsync_options or self.group['server'].get('rsync_options')
            hub_remote = hub_remote or self.group['server'].get('hub_remote')

        self.hub.remote_fn = hub_remote
        self.hub.remote_dir = os.path.dirname(hub_remote)

        self.hub.render()

        if user == '$USER':
            user = os.environ.get('USER')
        kwargs = dict(host=host, user=user, rsync_options=rsync_options)

        upload_hub(hub=self.hub, **kwargs)
        if not hub_only:
            for track, level in self.hub.leaves(Track):
                upload_track(track=track, **kwargs)

        log("Hub can now be accessed via {0}"
            .format(self.hub.url), style=Fore.BLUE)
