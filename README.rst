Hub Masonry
===========

Have you ever wished the UCSC Genome Browser had more tracks relevant to your
work?

This package might help.  The goal is to manage genomic data (called peaks,
RNA-seq signal, variants, microarray data, etc etc) from many published studies
and maintain them as a track hub on UCSC. Despite the existence of standard
data formats for genomics data (e.g. BAM, BED, bigWig), in practice we find
many arbitrary file formats in the supplemental material from published papers
and in GEO.  Sure, the raw data might be available, but often we want to avoid
re-constructing the entire analysis from scratch just to check our favorite
genomic locus.

This package recognizes that `working with other people's data can get messy
<http://nsaunders.wordpress.com/2014/07/30/hell-is-other-peoples-data/>`_. It
allows lots of flexibility at a low level for doing the custom manipulation and
conversion of raw data for each study, but also provides high-level tools for
managing many studies at once to make maintenance and keeping track of data
provenance as painless as possible.

It is currently used in practice to manage hundreds of tracks across dozens of
experiments of interest to multiple lab groups working in different model
systems. So it scales well while providing the flexibility needed to data-munge
on a case-by-case basis.

The general idea
----------------

hubward helps convert raw data to formats that can be used in UCSC track
hubs (bigBed, bigWig, VCF, BAM), and then creates and uploads a track hub.

There are 3 stages:

1. Run the ``hubward new`` command to populate a directory with a skeleton
   of files needed.

2. Edit these files (details below) and then run ``hubward process``
   to convert raw data into files ready for upload to UCSC.

3. Run ``hubward build-trackhub`` to build and upload a UCSC track hub,
   including the automatic uploading of processed files and documentation.

Example
-------

For the impatient: follow `this link
<http://genome.ucsc.edu/cgi-bin/hgTracks?db=dm3&hubUrl=http://helix.nih.gov/~dalerr/encode/compiled/compiled.hub.txt>`_
to load the created hub in the UCSC Genome Browser; look for the "Encode"
section with two composite tracks, "ENCODE predicted enhancers" and "Hi-C
domains [embryo]".

In practice, using ``hubward`` means editing config files and
writing scripts to process the particular raw data that you want to look at.
This is difficult to illustrate in a README format.  Instead, there is an
example script ``run-example.bash`` which will show the process of creating
a track hub showing enhancers and Hi-C data from the ENCODE project.

Data are available at https://www.encodeproject.org/comparative/chromatin/.
Since the files provided there are not bigBed or bigWig format, they cannot be
directly used in a track hub.  This example illustrates how to configure the
conversion and upload of these data. The files that were edited for this
example can be found in the ``examples`` directory.  Most of the work is done
in the ``process.py`` files and the ``metadata-builder.py`` files.


To clarify the exact changes made relative to the skeleton template, this
example script makes a git repo of the skeleton template, copies over the
edited example files, then commits all the changes that were made for this
example.  Then you can look at the git log (say, using ``gitk``) to see what
changed.  See the code in ``run-example.bash`` for details.

To get started from scratch:

1. Clone this repo and get setup::

    git clone https://github.com/daler/hubward.git
    cd hubward
    pip install -r requirements.txt
    python setup.py develop

Note, you will also need the UCSC tool ``bedToBigBed`` in your path for this
example to work.

2. Configure your server information. Because of the way track hubs work, you
   will need a server you can upload to. You can disable this in the example by
   commenting out the last ``hubward build-trackhub`` line in the
   ``run-example.bash`` script.  If you do want to upload the data, write the
   details for your server in the file ``~/.hubward.yaml``. It should have
   the following fields; note that the first two fields have a ``%s``
   placeholder that is filled in later by driver scripts::

        # contents of ~/.hubward.yaml; fill in with your own details
        hub_url_pattern: 'http://example.com/webapps/%s/compiled/compiled.hub.txt'
        hub_remote_pattern: '/home/me/apps/%s/compiled/compiled.hub.txt'
        host: example.com
        user: me
        email: me@example.com

3. Run the ``run-example.bash`` script (and read the comments in it for more
   details).

The output will look something like this::

    + LAB=encode
    + for STUDY in encode-enhancers encode-hic-domains
    + hubward new encode encode-enhancers
    + cd encode
    + git init
    Initialized empty Git repository in <DIR>/encode/.git/
    + cd encode/encode-enhancers
    + git add .
    + git commit -m 'initial template for encode-enhancers'
    [master (root-commit) fb4a1f5] initial template for encode-enhancers
     4 files changed, 80 insertions(+)
     create mode 100644 encode-enhancers/README
     create mode 100644 encode-enhancers/metadata-builder.py
     create mode 100644 encode-enhancers/src/get-data.bash
     create mode 100755 encode-enhancers/src/process.py
    + rsync -arv example/encode/encode-enhancers/ encode/encode-enhancers/
    sending incremental file list
    ./
    README
    metadata-builder.py
    src/
    src/get-data.bash
    src/process.py

    sent 3,386 bytes  received 107 bytes  6,986.00 bytes/sec
    total size is 2,988  speedup is 0.86
    + cd encode
    + git commit -a -m 'changes made by the encode/encode-enhancers example'
    [master fd1e5a7] changes made by the encode/encode-enhancers example
     4 files changed, 90 insertions(+), 75 deletions(-)
     rewrite encode-enhancers/README (100%)
     rewrite encode-enhancers/metadata-builder.py (69%)
     rewrite encode-enhancers/src/process.py (99%)
    + bash encode/encode-enhancers/src/get-data.bash
    --2014-12-05 17:22:56--  http://compbio.med.harvard.edu/modencode/webpage/enh_calls_final/comparative_enhancer_calls.tar.gz
    Resolving compbio.med.harvard.edu (compbio.med.harvard.edu)... 134.174.150.124
    Connecting to compbio.med.harvard.edu (compbio.med.harvard.edu)|134.174.150.124|:80... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 3442816 (3.3M) [application/x-gzip]
    Saving to: ‘comparative_enhancer_calls.tar.gz’

    100%[==========================================================================================>] 3,442,816   6.74MB/s   in 0.5s   

    2014-12-05 17:22:56 (6.74 MB/s) - ‘comparative_enhancer_calls.tar.gz’ saved [3442816/3442816]

    CBP_enhancers_wormEE.txt
    CBP_enhancers_wormL3.txt
    DHS_enhancers_BG3.txt
    DHS_enhancers_Gm12878.txt
    DHS_enhancers_H1.txt
    DHS_enhancers_Hela.txt
    DHS_enhancers_IMR90.txt
    DHS_enhancers_K562.txt
    DHS_enhancers_Kc.txt
    DHS_enhancers_LE.txt
    DHS_enhancers_S2.txt
    p300_enhancers_Gm12878.txt
    p300_enhancers_H1.txt
    p300_enhancers_HeLa.txt
    p300_enhancers_K562.txt
    README.txt
    + for STUDY in encode-enhancers encode-hic-domains
    + hubward new encode encode-hic-domains
    + cd encode
    + git init
    Reinitialized existing Git repository in <DIR>/encode/.git/
    + cd encode/encode-hic-domains
    + git add .
    + git commit -m 'initial template for encode-hic-domains'
    [master 82c0299] initial template for encode-hic-domains
     4 files changed, 80 insertions(+)
     create mode 100644 encode-hic-domains/README
     create mode 100644 encode-hic-domains/metadata-builder.py
     create mode 100644 encode-hic-domains/src/get-data.bash
     create mode 100755 encode-hic-domains/src/process.py
    + rsync -arv example/encode/encode-hic-domains/ encode/encode-hic-domains/
    sending incremental file list
    ./
    README
    metadata-builder.py
    src/
    src/get-data.bash
    src/process.py

    sent 3,024 bytes  received 107 bytes  6,262.00 bytes/sec
    total size is 2,629  speedup is 0.84
    + cd encode
    + git commit -a -m 'changes made by the encode/encode-hic-domains example'
    [master 0d4b0f5] changes made by the encode/encode-hic-domains example
     4 files changed, 81 insertions(+), 75 deletions(-)
     rewrite encode-hic-domains/README (100%)
     rewrite encode-hic-domains/metadata-builder.py (70%)
     rewrite encode-hic-domains/src/process.py (99%)
    + bash encode/encode-hic-domains/src/get-data.bash
    --2014-12-05 17:22:58--  http://compbio.med.harvard.edu/modencode/webpage/hic/HiC_EL.bed
    Resolving compbio.med.harvard.edu (compbio.med.harvard.edu)... 134.174.150.124
    Connecting to compbio.med.harvard.edu (compbio.med.harvard.edu)|134.174.150.124|:80... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 33952 (33K) [text/plain]
    Saving to: ‘HiC_EL.bed’

    100%[==========================================================================================>] 33,952      --.-K/s   in 0.03s   

    2014-12-05 17:22:58 (1.22 MB/s) - ‘HiC_EL.bed’ saved [33952/33952]

    + hubward process encode
    [2014-12-05 17:22:59,750] Study: Hi-C domains [embryo], in "/home/ryan/proj/hub-masonry/encode/encode-hic-domains"
    [2014-12-05 17:22:59,750]     Converting "raw-data/HiC_EL.bed" -> "processed-data/HiC-Active.bigBed"
    [2014-12-05 17:23:01,006]     Converting "raw-data/HiC_EL.bed" -> "processed-data/HiC-HP1_centromeric.bigBed"
    [2014-12-05 17:23:02,235]     Converting "raw-data/HiC_EL.bed" -> "processed-data/HiC-Null.bigBed"
    [2014-12-05 17:23:03,693]     Converting "raw-data/HiC_EL.bed" -> "processed-data/HiC-PcG.bigBed"
    [2014-12-05 17:23:05,016] Study: ENCODE predicted enhancers, in "/home/ryan/proj/hub-masonry/encode/encode-enhancers"
    [2014-12-05 17:23:05,017]     Converting "raw-data/DHS_enhancers_S2.txt" -> "processed-data/DHS_enhancers_S2.bigbed"
    [2014-12-05 17:23:06,220]     Converting "raw-data/DHS_enhancers_BG3.txt" -> "processed-data/DHS_enhancers_BG3.bigbed"
    [2014-12-05 17:23:07,423]     Converting "raw-data/DHS_enhancers_LE.txt" -> "processed-data/DHS_enhancers_LE.bigbed"
    [2014-12-05 17:23:08,662]     Converting "raw-data/DHS_enhancers_Kc.txt" -> "processed-data/DHS_enhancers_Kc.bigbed"
    + hubward build-trackhub encode dm3
    ...
    ... (lots of output from the rsync calls to the server...)

If you were to run ``hubward process encode`` again, the output files are
already up-to-date so nothing further happens, and this is reported to stdout::

    > hubward process encode
    [2014-12-05 17:25:52,667] Study: Hi-C domains [embryo], in "<DIR>/encode/encode-hic-domains"
    [2014-12-05 17:25:52,668]     Up to date: "processed-data/HiC-Active.bigBed"
    [2014-12-05 17:25:52,668]     Up to date: "processed-data/HiC-HP1_centromeric.bigBed"
    [2014-12-05 17:25:52,668]     Up to date: "processed-data/HiC-Null.bigBed"
    [2014-12-05 17:25:52,668]     Up to date: "processed-data/HiC-PcG.bigBed"
    [2014-12-05 17:25:52,761] Study: ENCODE predicted enhancers, in "<DIR>/encode/encode-enhancers"
    [2014-12-05 17:25:52,762]     Up to date: "processed-data/DHS_enhancers_S2.bigbed"
    [2014-12-05 17:25:52,762]     Up to date: "processed-data/DHS_enhancers_BG3.bigbed"
    [2014-12-05 17:25:52,762]     Up to date: "processed-data/DHS_enhancers_LE.bigbed"
    [2014-12-05 17:25:52,762]     Up to date: "processed-data/DHS_enhancers_Kc.bigbed"


To see this example in action, you can follow this link, which will load the
pre-compiled hub in the UCSC genome browser.  Once it loads, look for the
"Encode" section.  It should have two composite tracks, "ENCODE predicted
enhancers" and "Hi-C domains [embryo]".  Note that the README files have been
converted to HTML and are visible on the configuration page for these tracks.

URL: http://genome.ucsc.edu/cgi-bin/hgTracks?db=dm3&hubUrl=http://helix.nih.gov/~dalerr/encode/compiled/compiled.hub.txt

See the "Workflow" section below for more details.

Design
------
`hub-masonry` separates the messy part of using other people's data (cleaning,
sorting, filtering, format conversion) from parts that are in common across
multiple data sets (uploading, organizing, generating HTML files).

Each study will have one or more raw data files.  These need to be converted
into a format suitable for uploading into a track hub on UCSC, which currently
is bigBed, bigWig, VCF, or BAM formats.  This conversion is highly dependent on
the particular study.

I've settled on the strategy that each raw data filename is mapped to
a conversion script that is called with the input file as the first argument
and the output file as the second argument (e.g., ``script.py infile
outfile``).  It's up to the script to do all the custom work.

For example, the easiest case is if the raw data is a bigBed file -- then all
the script has to do is copy the input to the output.  Usually though, lots of
conversion and manipulation has to happen in the script.  Luckily, this is all
hidden at the configuration level -- at this level, all we need to know is the
name of the script and the input and output filenames.

To keep things organized, flexible, and manageable, each study has
a ``metadata.yaml`` file.  This file contains lots of information about the
study, but in particular it defines how to go from raw data to processed files
ready for upload. In ``metadata.yaml`` there is a block for each desired output
file.  At its core, this block has three fields: "original", "processed", and
"script".  The high-level driver script (``hubward process`` command)
searches for files called ``metadata.yaml``, reads their data section, and
simply calls the script with the original and processed files as its only
arguments.  This gets you files ready for uploading to UCSC.

As you can imagine, the ``metadata.yaml`` file can get quite repetitive. So
there's a template ``metadata-builder.py`` script to help build it.  In fact,
**you shouldn't edit the metadata.yaml file by hand** because
``metadata-builder.py`` will frequently get called by the driver script in
order to refresh the data.

In general, the workflow is the following:

- initialize a new study using the ``hubward new`` command
- change to that new directory
- edit the ``src/get-data.bash`` script, and then run it, to download raw data
- write the ``src/process.py`` script to convert raw to processed data
- edit ``metadata-builder.py`` to build a ``metadata.yaml`` file specific
  to the study
- edit the ``README`` file to record the details of what you did.

Armed with this, the driver scripts will:

- search for all ``metadata.yaml`` files
- re-generate any processed files defined in those ``metadata.yaml`` files
  that are out-of-date by calling the defined script on the input file to
  create the desired output file
- create a track hub with a composite track for each study
- create HTML documentation for each study based on the README file
  (additionally including a link to the abstract on PubMed if a PMID is
  supplied)
- upload the data and hub details to the server you specify
- print out the track hub URL that you can load into the UCSC genome
  browser
