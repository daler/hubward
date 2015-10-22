import subprocess
import pybedtools
import os
import pkg_resources
import tempfile
import conda_build.utils
from docutils.core import publish_string
import bleach
from conda.fetch import download
import string

def makedirs(dirnames):
    """
    Recursively create the given directory or directories without reporting
    errors if they are present.
    """
    if isinstance(dirnames, str):
        dirnames = [dirnames]
    for dirname in dirnames:
        if not os.path.exists(dirname):
            os.makedirs(dirname)



def unpack(filename, dest):
    if filename.lower().endswith(
        ('.tar.gz', '.tar.bz2', '.tgz', '.tar.xz', '.tar', 'tar.z')
    ):
        conda_build.utils.tar_xf(filename, dest)
    elif filename.lower().endswith('.zip'):
        conda_build.utils.unzip(filename, dest)



def link_is_newer(x, y):
    return os.lstat(x).st_mtime > os.lstat(y).st_mtime


def is_newer(x, y):
    return os.stat(x).st_mtime > os.stat(y).st_mtime


def get_resource(fn):
    try:
        return pkg_resources.resource_string('hubward', fn)
    except IOError:
        return open(os.path.join(
            os.path.dirname(__file__), '..', 'resources', fn)).read()


def reST_to_html(s):
    """
    Convert ReST-formatted string `s` into HTML.

    Output is intended for uploading to UCSC configuration pages, so this uses
    a whitelist approach for HTML tags.
    """
    html = publish_string(
        source=s,
        writer_name='html',
        settings=None,
        settings_overrides={'embed_stylesheet': False},
    )
    safe = bleach.ALLOWED_TAGS + [
        'p', 'img', 'pre', 'tt', 'a', 'h1', 'h2', 'h3', 'h4'
    ]

    attributes = {
        'img': ['alt', 'src'],
        'a': ['href'],
    }

    return bleach.clean(html, tags=safe, strip=True, attributes=attributes)


def sanitize(s, strict=False):
    """
    If strict, only allow letters and digits -- spaces will be stripped.

    Otherwise, convert spaces to underscores.
    """
    if strict:
        allowed = string.letters + string.digits
    else:
        allowed = string.letters + string.digits + ' '
    return ''.join([i for i in s if i in allowed]).replace(' ', '_')


# copied over from metaseq.colormap_adjust to avoid pulling in all of
# metaseq...
def smart_colormap(vmin, vmax, color_high='#b11902', hue_low=0.6):
    """
    Creates a "smart" colormap that is centered on zero, and accounts for
    asymmetrical vmin and vmax by matching saturation/value of high and low
    colors.

    It works by first creating a colormap from white to `color_high`.  Setting
    this color to the max(abs([vmin, vmax])), it then determines what the color
    of min(abs([vmin, vmax])) should be on that scale.  Then it shifts the
    color to the new hue `hue_low`, and finally creates a new colormap with the
    new hue-shifted as the low, `color_high` as the max, and centered on zero.

    Parameters
    ----------
    color_high : color
        Can be any format supported by matplotlib. Try "#b11902" for a nice
        red.
    hue_low : float in [0, 1]
        Try 0.6 for a nice blue
    vmin : float
        Lowest value in data you'll be plotting
    vmax : float
        Highest value in data you'll be plotting
    """
    import matplotlib
    import colorsys
    # first go from white to color_high
    orig_cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        'test', ['#FFFFFF', color_high], N=2048)

    # For example, say vmin=-3 and vmax=9.  If vmin were positive, what would
    # its color be?
    vmin = float(vmin)
    vmax = float(vmax)
    mx = max([vmin, vmax])
    mn = min([vmin, vmax])
    frac = abs(mn / mx)
    rgb = orig_cmap(frac)[:-1]

    # Convert to HSV and shift the hue
    hsv = list(colorsys.rgb_to_hsv(*rgb))
    hsv[0] = hue_low
    new_rgb = colorsys.hsv_to_rgb(*hsv)
    new_hex = matplotlib.colors.rgb2hex(new_rgb)

    zeropoint = -vmin / (vmax - vmin)

    # Create a new colormap using the new hue-shifted color as the low end
    new_cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        'test', [(0, new_rgb), (zeropoint, '#FFFFFF'), (1, color_high)],
        N=2048)

    return new_cmap


def fix_macs_wig(fn, genome, output=None, add_chr=False, to_ignore=None):
    """
    wig files created by MACS often are extended outside the chromsome ranges.
    This function edits an input WIG file to fit within the chromosome
    boundaries defined by `genome`.

    If `add_chr` is True, then prefix each chromosome name with "chr".

    Also gets rid of any track lines so the file is ready for conversion to
    bigWig.

    Returns the output filename.

    fn : str
        Input WIG filename. Can be gzipped, if extension ends in .gz.

    genome : str or dict

    output : str or None
        If None, writes to temp file

    to_ignore : list
        List of chromosomes to ignore.
    """

    if output is None:
        output = pybedtools.BedTool._tmp()
    if to_ignore is None:
        to_ignore = []
    genome = pybedtools.chromsizes(genome)
    with open(output, 'w') as fout:
        if fn.endswith('.gz'):
            f = gzip.open(fn)
        else:
            f = open(fn)
        for line in f:
            if line.startswith('track'):
                continue
            if line.startswith('variableStep'):
                a, b, c = line.strip().split()
                prefix, chrom = b.split('=')
                if add_chr:
                    chrom = 'chr' + chrom
                if chrom in to_ignore:
                    continue
                fout.write(' '.join([a, prefix + '=' + chrom, c]) + '\n')
                span = int(c.split('=')[1])
                continue
            pos, val = line.strip().split()
            if chrom in to_ignore:
                continue
            if (int(pos) + span) >= genome[chrom][1]:
                continue
            fout.write(line)
    return output
def colored_bigbed(x, color, genome, target, autosql=None, bedtype=None):
    """
    if color is "smart", then use metaseq's smart colormap centered on zero.

    otherwise, use singlecolormap.

    assumes that you have scores in BedTool x; this will zero all scores in the
    final bigbed
    """
    norm = x.colormap_normalize()
    if color == 'smart':
        cmap = smart_colormap(norm.vmin, norm.vmax)
    else:
        cmap = singlecolormap(color)

    def func(f):
        f = add_color(f, cmap, norm)
        f.score = '0'
        return f

    x = x\
        .sort()\
        .each(func)\
        .saveas()
    bigbed(x, genome=genome, output=target, _as=autosql, bedtype=bedtype)


def singlecolormap(color, func=None, n=64):
    """
    Creates a linear colormap where `color` is the top, and func(color) is the
    bottom.

    `func` should take an RGB tuple as its only input.  If `func` is None, then
    use a light gray as the min.

    `n` is the number of levels.
    """
    if func is None:
        def func(x):
            return '0.9'

    rgb = np.array(matplotlib.colors.colorConverter.to_rgb(color))
    return matplotlib.colors.LinearSegmentedColormap.from_list(
        name='colormap',
        colors=[func(rgb), rgb],
        N=n,
    )


def colortuple(col):
    """
    Given a color in any format supported by matplotlib, return
    a comma-separated string of R,G,B uint8 values.
    """
    rgb = np.array(matplotlib.colors.colorConverter.to_rgb(col))
    rgb = [int(i * 255) for i in rgb]
    return ','.join(map(str, rgb))


def add_chr(f):
    """
    Prepend "chr" to the beginning of chromosome names.

    Useful when passed to pybedtool.BedTool.each().
    """
    f.chrom = 'chr' + f.chrom
    return f


def chromsizes(assembly):
    url = ("http://hgdownload.cse.ucsc.edu/goldenPath/"
           "{0}/bigZips/{0}.chrom.sizes")
    dest = tempfile.NamedTemporaryFile(delete=False).name
    download(url.format(assembly), dest)
    return dest


def bigbed(filename, genome, output, blockSize=256, itemsPerSlot=512,
           bedtype=None, _as=None, unc=False, tab=False):
    """
    Parameters
    ----------
    :filename:
        BED-like file to convert


    :genome:
        Assembly string (e.g., "mm10" or "hg19")

    :output:
        Path to bigBed file to create.

    Other args are passed to bedToBigBed.  In particular, `bedtype` (which
    becomes the "-type=" argument) is automatically handled for you if it is
    kept as the default None.

    Assumes that a recent version of bedToBigBed from UCSC is on the path.
    """
    x = pybedtools.BedTool(filename)
    chromsizes_file = chromsizes(genome)
    if bedtype is None:
        bedtype = 'bed%s' % x.field_count()
    cmds = [
        'bedToBigBed',
        filename,
        chromsizes_file,
        output,
        '-blockSize=%s' % blockSize,
        '-itemsPerSlot=%s' % itemsPerSlot,
        '-type=%s' % bedtype
    ]
    if unc:
        cmds.append('-unc')
    if tab:
        cmds.append('-tab')
    if _as:
        cmds.append('-as=%s' % _as)
    p = subprocess.check_call(cmds, stderr=subprocess.STDOUT)

    return output

def bigwig(filename, genome, output, blockSize=256, itemsPerSlot=512,
           bedtype=None, _as=None, unc=False, tab=False):
    """
    Parameters
    ----------
    :filename:
        BEDGRAPH-like file to convert

    :genome:
        Assembly string (e.g., "mm10" or "hg19")

    :output:
        Path to bigWig file to create.

    Other args are passed to bedGraphToBigWig.

    """
    chromsizes_file = chromsizes(genome)
    cmds = [
        'bedGraphToBigWig',
        filename,
        chromsizes_file,
        output,
    ]
    p = subprocess.check_call(cmds, stderr=subprocess.STDOUT)
    return output

