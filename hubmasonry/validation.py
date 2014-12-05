import yaml
from jsonschema import validate, ValidationError
import pyaml
import json
import os
import glob
import subprocess
from colorama import init, Fore, Back, Style

HERE = os.path.abspath(os.path.dirname(__file__))
SCHEMA = json.load(open(os.path.join(HERE, 'schema.json')))


def link_is_newer(x, y):
    return os.lstat(x).st_mtime > os.lstat(y).st_mtime

def is_newer(x, y):
    return os.stat(x).st_mtime > os.stat(y).st_mtime

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
            link_is_newer(self.script, self.processed)

            # but for the original data, we want to FOLLOW the link
            or is_newer(self.original, self.processed)
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
                '{1}:\n\n{0}\n'.format(' \\\n'.join(cmds), self.processed)
                + Fore.RESET
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

        self.pmid = self.metadata['study']['PMID']
        self.description = self.metadata['study']['description']
        self.reference = self.metadata['study']['reference']
        self.label = self.metadata['study']['label']
        self.dirname = os.path.abspath(os.path.dirname(fn))
        self.processing = self.metadata['study']['processing']

        self.data = [
            Data(d, os.path.dirname(fn)) for d in self.metadata['data']]

    def __str__(self):
        return pyaml.dumps(self.json)
