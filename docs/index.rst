.. hubward documentation master file, created by
   sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Hubward
=======
The goal of `hubward` is to manage genomic data (called peaks, RNA-seq signal,
variants, microarray data, etc etc) from many published studies and maintain
them as `track hubs on UCSC
<https://genome.ucsc.edu/goldenPath/help/hubQuickStart.html>`_.

Despite the existence of standard data formats for genomics data (e.g. BAM,
BED, bigWig), in practice we find many arbitrary file formats in the
supplemental material from published papers and in GEO.  Sure, the raw data
might be available, but often we want to avoid re-constructing the entire
analysis from scratch just to check our favorite genomic locus.

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

There are 3 stages, each with their own command: `new`, `process` and `build-trackhub`.

1. ``hubward new`` populates a directory with a skeleton of files needed.

2. After editing those files, ``hubward process`` converts raw data into files
   ready for upload to UCSC.

3. ``hubward build-trackhub`` builds and uploads a UCSC track hub.  This
   includes automatic uploading of processed files and documentation.


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


















We will be creating a new track hub for ENCODE data. The "lab" will be `encode`
and the "study" will be `encode-enhancers`::

    hubward new encode encode-enhancers

This generates the following directory structure::

    encode
    └── encode-enhancers
        ├── metadata-builder.py
        ├── processed-data
        │   ├── bam
        │   ├── bed
        │   ├── bigbed
        │   └── bigwig
        ├── raw-data
        ├── README
        └── src
            ├── get-data.bash
            └── process.py


Downloading the raw data
------------------------
The goal for this stage is to acquire and pre-process raw data. Generally
"pre-process" simply means uncompressing downloaded files -- anything
complicated will be handled later.

It's generally easier to download the raw data once. The
:file:`src/get-data.bash` script is a convenient way of storing this
information in a uniform place across all studies.

The template :file:`src/get-data.bash` looks like this:

.. literalinclude:: ../encode/encode-enhancers/src/get-data.bash
    :language: bash
    :caption: ``get-data.bash`` (template)

The ENCODE enhancer data appear to be all contained in a single `.tar.gz` file.
Here we edit the :file:`get-data.bash` script to download the data from the
correct URL, unzip the data in the `raw-data` directory, and clean up the
tarball afterwards:

.. literalinclude:: ../example/encode/encode-enhancers/src/get-data.bash
    :language: bash
    :caption: ``get-data.bash`` (edited version)

Upon running this script, we get the following directory structure::

    encode/encode-enhancers/raw-data/
    ├── CBP_enhancers_wormEE.txt
    ├── CBP_enhancers_wormL3.txt
    ├── DHS_enhancers_BG3.txt
    ├── DHS_enhancers_Gm12878.txt
    ├── DHS_enhancers_H1.txt
    ├── DHS_enhancers_Hela.txt
    ├── DHS_enhancers_IMR90.txt
    ├── DHS_enhancers_K562.txt
    ├── DHS_enhancers_Kc.txt
    ├── DHS_enhancers_LE.txt
    ├── DHS_enhancers_S2.txt
    ├── p300_enhancers_Gm12878.txt
    ├── p300_enhancers_H1.txt
    ├── p300_enhancers_HeLa.txt
    ├── p300_enhancers_K562.txt
    └── README.txt

The first few lines of :file:`DHS_enhancers_BG3.txt` are the following:

::

    chr pos
    chr2L 5800
    chr2L 134775
    chr2L 136385
    chr2L 220595
    chr2L 224480
    chr2L 225110
    chr2L 246950
    chr2L 247580
    chr2L 380020


So these are single-bp positions.

Our goal is to write a script that accepts a file like this and creates
a bigBed file that will be uploaded. After writing such a script, we will map
the input files to output files along with the script to do the work.

Editing the :file:`process.py` script
-------------------------------------
The script to map input (here, text files of single-bp positions) to output
(here, we want bigBed files) can be any language. It just has to accept
2 arguments: input file and output file. It can also live anywhere. For
convenience and provenance, we store the script in the `src` directory:

.. literalinclude:: ../example/encode/encode-enhancers/src/process.py

Equivalently, we could write a bash script to do the same thing:

.. literalinclude:: ../example/encode/encode-enhancers/src/process.sh
    :language: bash

.. note::

    The astute reader will have realized we hard-coded the dm3 genome, but
    there are raw data files for human and worm as well. For simplicity, in
    this example we're only working with *Drosophila melanogaster* data.



``metadata.yaml``
-----------------
The `metadata.yaml` file contains two main sections. The first, `study`,
contains bibliographic information about the dataset. The second, `data`, is
a list of configuration blocks. Each block configures the process of converting
input data to an output file and represents one track in the track hub.

``study`` section
~~~~~~~~~~~~~~~~~
An example should help clarify. Here's what we're aiming for for the `study`
section::

    study:
      PMID: 25164756
      description: 'ENCODE predicted enhancers'
      label: encode-enhancers
      processing: |
        Data were downloaded from https://www.encodeproject.org/comparative/chromatin
        as text files with chromosome and position.  BED3 files were created by
        extending the position by 1 bp, and BED3 files were converted to bigBed format.

        From the site::

            Enhancers were identified using TSS-distal DHSs and p300 and CBP-1 binding
            sites. The positions listed in the files are a subset of TSS-distal DHSs
            (human, fly), p300 (human) and CBP-1 (worm) binding sites that are
            classified as enhancers...  ...The classification was optimized to obtain
            a high confidence set that is not necessarily very inclusive. For
            additional information please see the README file in the archive.

      reference: 'Ho, J. W. K. et al. Comparative analysis of metazoan chromatin organization. Nature 512, 449-452 (2014).'

Field descriptions
++++++++++++++++++

:PMID:
    If provided, a link to the corresponding PubMed entry will be created in
    the track hub documentation.

:description:
    This is the track description, and will show up as the blue link text in
    the genome browser.

:label:
    This label is used internally for creating the track hub

:processing:
    Documentation of how the data were processed for uploading to UCSC. As
    we'll see in the example below, typically this information is written in
    the README file, which is then copied into this `processing` entry.

    Note that the README file can be in reStructuredText format (.rst), which
    will be converted to HTML upon uploading.

:reference:
    The full reference to where the data came from.


``data`` section
~~~~~~~~~~~~~~~~
Here's one entry from the ``data`` section::

    data:
      - description: 'BG3 enhancers'
        genome: dm3
        label: 'enhancers [BG3]'
        original: raw-data/DHS_enhancers_BG3.txt
        processed: processed-data/DHS_enhancers_BG3.bigbed
        script: src/process.py
        trackinfo:
          tracktype: 'bigBed 3'
          visibility: dense
        type: bigbed
        url: 'url to supplemental data'

.. _datafields:

`data` field descriptions
+++++++++++++++++++++++++
:description:
    This will show up in the "description" column on the track config page

:genome:
    Assembly to use

:label:
    This will show up on the left-hand side of tracks in the browser

:original:
    The path, relative to ``metadata.yaml``, containing the original data for
    this track

:processed:
    The path, relative to ``metadata.yaml``, for the final processed file ready
    for upload to UCSC

:script:
    The path, relative to ``metadata.yaml``, for the script that takes
    `original` as the first argument and `processed` as the second argument.

:trackinfo:
    Optional configuration items. These are converted to keyword arguments and
    sent to `trackhub <https://github.com/daler/trackhub>`_ for track hub
    creation.

:type:
    One of the types supported by UCSC track hubs (bigBed, bigWig, BAM, VCF)

:url:
    Optional URL to data. Typically this is the url used in the
    ``get-data.bash`` script.


Screenshots showing effect of config options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With this information, the uploaded hub will look like this on the main browser
page:

.. image:: images/loaded-hub-edit.png

Upon clicking the "ENCODE predicted enhancers" link, the following config page
will be seen:

.. image:: images/enhancer-config-edit.png

Setting all tracks to "dense" will show the data in the browser:

.. image:: images/browser-enhancers-edit.png

Editing the ``metadata-builder.py`` script
------------------------------------------
In practice, editing the :file:`metadata.yaml` file by hand is tedious and
error-prone. Therefore, we use the :file:`metadata-builder.py` script to
generate it for us.

The script is shown below; the commented number (e.g., ``# [1]``) refers to
notes below.

.. literalinclude:: ../example/encode/encode-enhancers/metadata-builder.py
    :linenos:

Script annotations
~~~~~~~~~~~~~~~~~~

:``[1]``:
    These imports are done in the metadata-builder.py template that is created
    with the ``hubward new`` command; it's best to leave them.

:``[2]``:
    An ordered dictionary keeps the created `metadata.yaml` file a little more
    readable. Also note that we create an empty `study` dict and an empty
    `data` list that we'll fill in next

:``[3]``:
    The metadata-builder.py template has placeholders for these items; here the
    details about this particular study have been added.

:``[4]``:
    This line is unchanged from the metadata-builder.py template; it reads in
    the README file and uses it verbatim for the `processing` field. Note that
    the README file can be written in reStructuredText format, which will in
    turn get nicely formatted into HTML in the track config page.

:``[5]``:
    Here we iterate over the cell types of interest. Note that even though we
    have data for human and worm, we're only using the *Drosophila* cell lines.

:``[6]``:
    The remaining information is filled in as appropriate for each cell type.

:``[7]``:
    The final dictionary, ``d``, is written out to file.


Contents:

.. toctree::
   :maxdepth: 2

   readme
   installation
   contributing
   authors
   history

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

