"""
Module for converting genomic coordinates from one version of an assembly to
another
"""
import utils


def download_chainfile(source_assembly, target_assembly,
                       config_path=os.path.expanduser('~/.hubward.yaml'),
                       cache_dir=None):
    """
    Download if needed, putting in the cache_dir
    """
    if cache_dir is None:
        cfg = utils.get_config(config_path)
        cfg_dir = os.path.dirname(config_path)
        cache_dir = os.path.relpath(cfg['ucsc_cache_dir'], cfg_dir)
    url = chainfile_url(source_assembly, target_assembly)
    dest = os.path.join(cache_dir, os.path.basename(url))
    utils.download(url, dest)
    return dest


def chainfile_url(source_assembly, target_assembly):
    return ("http://hgdownload.cse.ucsc.edu/"
            "goldenPath/{0}/liftOver/{0}To{1}.over.chain.gz".format(
                source_assembly, target_assembly.title()))


def _liftover_bigwig(src, target, infile, outfile):
    bigWigToBedGraph infile > tempfile
    return _liftover_bed(src, target, tempfile, outfile)


def liftover(from_, to_, infile, outfile, filetype):
    if filetype.lower() == 'bigwig':
        bigWigToBedGraph infile > tempfile
        infile = tempfile

    cmds = ['liftOver', infile, chainfile, newfile, unmapped]
