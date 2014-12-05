Hub Masonry
===========

Have you ever wished the UCSC Genome Browser had more tracks relevant to your
work?

Have you ever been asked "I read this great paper, but I can't get the BAM file
I downloaded to open in Word.  So how do I look at their data?"

This package might help.  The goal is to manage genomic data (called peaks,
RNA-seq signal, variants, microarray data, etc etc) from many published studies
and maintain them as a track hub on UCSC.  This package recognizes that
`working with other people's data can get messy
<http://nsaunders.wordpress.com/2014/07/30/hell-is-other-peoples-data/>`_.
It allows lots of flexibility at a low level for doing the
custom manipulation and conversion of raw data for each study, but also
provides high-level tools for managing many studies at once to make maintenance
and keeping track of data provenance as painless as possible.

It is currently used in practice to manage hundreds of tracks across dozens of
experiments of interest to multiple lab groups working in different model
systems.

The general idea
----------------

The command-line tool ``hubmasonry`` handles each step.

``hubmasonry new <study name>``:  Creates a new directory and populates it with
files you then need to edit. These files do things like download the raw data
and perform processing steps to get the raw data into a usable form.

``hubmasonry process <directory>``:  Looks for any ``metadata.yaml`` files in
the directory and reads the configuration. If an output file needs update, it
will re-run the assigned processing script; otherwise it will report that the
file is up-to-date.

``hubmasonry build-trackhub <directory>``:  Builds a track hub of all the
configured tracks in all the subdirectories and uploads everything to the host
configured in ``~/.hubmasonry.yaml``.


Design
------
`hub-masonry` separates the messy part of using other people's data (cleaning,
sorting, filtering, format conversion) from parts that are in common across
multiple data sets (uploading, organizing, generating HTML files).

Each study will have one or more raw data files.  These need to be converted
into a format suitable for uploading into a track hub on UCSC, which currently
is bigBed, bigWig, VCF, or BAM formats.  This conversion is highly dependent on
the particular study.  The schema is that each raw data filename is mapped to
a conversion script that is called with the input file as the first argument
and the output file as the second argument.  It's up to the script to do all
the custom work. For example, the easiest case is if the raw data is a bigBed
file -- then all the script has to do is copy the input to the output.  Usually
though, lots of conversion and manipulation has to happen in the script.
Luckily, this is all hidden at the configuration level -- at this level, all we
need to know is the name of the script and the input and output filenames.

To keep things organized, flexible, and manageable, each study has
a ``metadata.yaml`` file.  This file contains lots of information about the
study, but in particular it defines how to go from raw data to processed files
ready for upload. In ``metadata.yaml`` there is a block for each desired output
file.  At its core, this block has three fields: "original", "processed", and
"script".  The high-level driver script (``hubmasonry process`` command)
searches for files called ``metadata.yaml``, reads their data section, and
simply calls the script with the original and processed files as its only
arguments.  This gets you files ready for uploading to UCSC.

Since the ``metadata.yaml`` file can get repetitive, there's
a ``metadata-builder.py`` script to help build it.  In fact, **you shouldn't
edit the metadata.yaml file by hand** because ``metadata-builder.py`` will
frequently get called by the driver script in order to refresh the data.

In general, the workflow is the following:

    - initialize a new study using the ``hubmasonry new`` command
    - change to that new directory
    - edit the ``src/get-data.bash`` script to download raw data
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


Workflow
--------

.. note::

    A working example will be added here.

Here's the directory structure of a typical ChIP-seq experiment with called
peaks and signal for two celltypes.  More info is provided below; this is just
to give you an overview for now::

    lab/
      study_1/

        README
        metadata-builder.py  # script to programmatically build metadata.yaml
        metadata.yaml        # authoritative description of all data;
                             #   created by metadata-builder.py

        processed-data/      # contains final data ready for uploading
                             #   to a trackhub
          bigbed/
            peaks-celltype1.bigbed
            peaks-celltype2.bigbed
          bigwig/
            signal-celltype1.bigwig
            signal-celltype2.bigwig

          raw-data/         # raw data as downloaded from journal, author's
                            # website, GEO, etc
            Supplemental_Table_S1.xlsx
            signal1.bedgraph
            signal2.bedgraph

          src/
            get-data.bash   # downloads and unpacks data
            process.py      # converts raw data to processed data

#. Run ``hubmasonry new lab/study_1``.  This will create a skeleton directory
   structure as well as some template files, particularly
   ``metadata-builder.py``, ``process.py``, and ``get-data.bash``.

#. Figure out how to get the raw data for the new study, and write this into
   ``src/get-data.bash``.  The goal is to get unpacked data into the
   ``raw-data`` directory.  Run this script to get the data.

#. Start editing ``metadata-builder.py`` (which was created from a template to
   help get you started) with relevant information from the study like
   citation, description, PMID, etc.  When you get to the section that
   populates the ``data`` array, you'll need to decide what script will be
   called to convert raw data to processed data.  The template is set up to use
   the ``src/process.py`` script, but it can be anything you want.  I'll assume
   you'll be using ``src/process.py``.

#. Start working on the ``src/process.py`` script.  In general:

    - it should accept exactly two positional arguments: original data file,
      and processed data file
    - it should do any manipulation needed -- this might include running
      external R scripts and lots of reformatting and manipulation, or if
      you're lucky enough to have bigBed files as raw input, it can just copy
      the raw file to the processed filename.

#. Run ``hubmasonry process lab/study_1``.  This script:

    - searches for ``metadata-builder.py`` files
    - runs the ``metadata-builder.py`` script to get a fresh ``metadata.yaml``
      file (this is why you don't want to edit ``metadata.yaml`` by hand!)
    - iterates through the list of defined data files, checking for anything
      that needs updates
    - for anything that needs an update, calls ``$script $original $processed`` to
      generate the processed data file

   Now you have processed data files for all configured studies, ready for
   upload to UCSC.


#. Run ``hubmasonry build-trackhub``.  This script:

    - reads the ``metadata.yaml`` files, and builds a composite track for each
    - creates bigbed and/or bigwig views on the composite track that point to
      the processed data files
    - creates HTML documentation based on the README for the study, adding
      citation info and PubMed link
    - combines composite tracks into a track hub
    - uploads the hub and syncs all processed data files to a server you
      specify

``~/.hubmasonry.yaml``
----------------------

This file contains configuration information needed for uploading the track
hub.  It is in YAML format, and needs the following fields:

::

    hub_url_pattern: 'http://example.com/webapps/%s/compiled/compiled.hub.txt'
    hub_remote_pattern: '/home/me/apps/%s/compiled/compiled.hub.txt'
    host: example.com
    user: me
    email: me@example.com

