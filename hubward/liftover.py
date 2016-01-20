"""
Module for converting genomic coordinates from one version of an assembly to
another
"""
import utils
import subprocess
import os
import shutil
import pybedtools
from hubward.log import log


def download_chainfile(source_assembly, target_assembly):
    """
    Download if needed, putting in the cache_dir.

    If the environmental variable HUBWARD_CACHE_DIR does not exist, then use
    ~/.hubward_cache
    """
    cache_dir = os.environ.get(
        'HUBWARD_CACHE_DIR', os.path.expanduser('~/.hubward_cache'))
    utils.makedirs(cache_dir)
    url = chainfile_url(source_assembly, target_assembly)
    dest = os.path.join(cache_dir, os.path.basename(url))
    if not os.path.exists(dest):
        log('Downloading {0} to {1}'.format(url, dest))
        utils.download(url, dest)
    return dest


def chainfile_url(source_assembly, target_assembly):
    return ("http://hgdownload.cse.ucsc.edu/"
            "goldenPath/{0}/liftOver/{0}To{1}.over.chain.gz".format(
                source_assembly, target_assembly.title()))


def _liftover_bam(source_assembly, target_assembly, infile, outfile):
    chainfile = download_chainfile(source_assembly, target_assembly)

    # In the test environment, CrossMap.py causes segfault if output is not
    # STDOUT
    with open(outfile + '.tmp.bam', 'w') as fout:
        cmds = [
            'CrossMap.py',
            'bam',
            chainfile,
            infile,
            'STDOUT']

        p = subprocess.check_call(cmds, stdout=fout)

    with open(outfile, 'w') as fout:
        cmds = [
            'samtools',
            'sort',
            '-T', outfile + '.sorting',
            outfile + '.tmp.bam',
        ]
        print(cmds)
        p = subprocess.check_call(cmds, stdout=fout)

    cmds = [
        'samtools',
        'index',
        outfile]
    print(cmds)
    p = subprocess.check_call(cmds)

    return outfile


def _liftover_bigwig(source_assembly, target_assembly, infile, outfile):
    chainfile = download_chainfile(source_assembly, target_assembly)
    cmds = [
        'CrossMap.py',
        'bigwig',
        chainfile,
        infile,
        outfile]
    p = subprocess.check_call(cmds)
    shutil.move(outfile + '.bw', outfile)
    return outfile


def _liftover_bigbed(source_assembly, target_assembly, infile, outfile):
    chainfile = download_chainfile(source_assembly, target_assembly)

    # Convert bigBed to bed
    cmds = [
        'bigBedToBed',
        infile,
        outfile + '.bed']
    p = subprocess.check_call(cmds)

    # get a tempfile for the unmapped; this wil actually not be returned but
    # needs to be specified for `liftOver`.
    unmapped = pybedtools.BedTool._tmp()

    # There seems to be a bug in crossmap where a BED9 file's thickStart and
    # thickEnd are not lifted over. So use UCSC's liftover directly. Might as
    # well, since it was designed for BED files anyway.
    cmds = [
        'liftOver',
        outfile + '.bed',
        chainfile,
        outfile + '.converted',
        unmapped,
    ]
    p = subprocess.check_call(cmds)

    tmp = pybedtools.BedTool(outfile + '.converted').sort()

    utils.bigbed(tmp.fn, target_assembly, outfile)
    return outfile


_dispatch = {
    'bigwig': _liftover_bigwig,
    'bigbed': _liftover_bigbed,
    'bam': _liftover_bam,
}

def liftover(from_, to_, infile, outfile, filetype):
    try:
        return _dispatch[filetype.lower()](from_, to_, infile, outfile)
    except KeyError:
        raise ValueError("unsupported filetype (%s) to lift over" % filetype)
