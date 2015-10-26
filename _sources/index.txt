.. hubward documentation master file, created by
   sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


.. include:: ../README.rst

`hubward` uses the following concepts:

:track:
    Data that can be represented as a single track in the UCSC Genome Browser.
    Examples include a file of called peaks; read pileup from a single RNA-seq
    sample; CNV scores for one sample; or anything that can be converted into
    bigBed, bigWig, BAM, or VCF format.

:study:
    A collection of tracks, typically all from the same published article.

:group:
    A collection of studies, typically related in some way.

Studies
-------
The minimal definition of a `hubward` "study" is a directory with
a `metadata.yaml` file. In practice, the directory contains raw data and
conversion scripts. A study generally corresponds to data from a single
published paper, but this is not required.  The `metadata.yaml` file describes
and configures one or many `tracks` grouped together. These are uploaded to
a track hub as a single `composite track
<https://genome.ucsc.edu/goldenPath/help/hubQuickStartGroups.html#composite>`_.

The `metadata.yaml` file consists of several sections. The `study` section
stores bibliographic information. It is converted to HTML documentation and
added to the study's configuration page in the UCSC Genome Browser.

.. code-block:: yaml

    study:
      reference: 'Ho, J. W. K. et al. Nature 512, 449-452 (2014).'
      PMID: 25164756
      description: 'ENCODE predicted enhancers'
      label: encode-enhancers
      processing: "Downloaded data were converted to bigBed format"

The `tracks` section is a list, with one item for each track to be included in
the hub. Here is one such item in the `tracks` list:

.. code-block:: yaml

    tracks:
      -
        label: "enhancers [K562]"
        description: "K562 enhancers"
        genome: hg19
        original: "raw-data/p300_enhancers_K562.txt"
        processed: "processed-data/p300_enhancers_K562.bigbed"
        script: "scr/process.py"
        source:
          fn: "comparative_enhancer_calls.tar.gz"
          url: "http://compbio.med.harvard.edu/modencode/webpage/enh_calls_final/comparative_enhancer_calls.tar.gz"
        trackinfo:
           tracktype: "bigBed 3"
           visibility: "dense"
           itemRgb: "on"
           color: "#FF0000"
        type: bigbed

The config file format and fields are described in detail later in the
documentation. In summary, this block defines the source data, an output file
to create, and a conversion script to create a bigBed file with features
colored red, for enhancers in K562 cells from the ENCODE project.  A logical
extension of this would be to include additional tracks for other cell lines in
this data set.

To process the data for a study, use::

    hubward process <directory>

where `directory` contains the `metadata.yaml` file. For each defined track, this will:

- ensure original data exist. If not, the `source` url is downloaded to the
  `source` fn and extracted
- ensure processed file exists and is up-to-date. If it is older than
  `original` or older than `script`, the script is re-run.

Groups
------
Multiple studies can be grouped together using a higher-level config file,
here called `group.yaml`. Each study can have multiple tracks; each group can
have multiple studies. 

For example, if the path to the above `metadata.yaml` file is
`encode/hg19/encode-enhancers`, then that directory can be included in the
`studies` list so that the K562 enhancers track will be uploaded:

.. code-block:: yaml

    group: encode
    genome: hg19
    name: "encodetracks"
    short_label: "Supp. ENCODE"
    long_label: "Supplemental ENCODE tracks"
    hub_url: "http://localhost/encode/hg19/compiled.hub.txt"

    server:
      hub_remote: "/root/encode/hg19/compiled.hub.txt"
      host: "localhost"
      user: "www"
      email: "www@localhost"

    studies:
      - encode/hg19/encode-enhancers

To process all studies in a group, run::

    hubward process <group YAML file>

This processes all configured studies to ensure their output is up-to-date.

To create the track hub files and upload to a remote server, run::

    hubward upload <group YAML file>

After it runs, it will show the URL that can be used to load the hub into the
Genome Browser.

Workflow
--------
To visualize a new dataset, the workflow is the following:

1. Write a `metadata.yaml` file and the corresponding scripts to perform
   conversion.
2. Write a `group config` file file that groups together individual studies.
3. Run `hubward process <group config>`. This parses the group config file, and
   for each defined study, parses its `metadata.yaml` file, downloads data if
   needed, runs conversion scripts if necessary.
4. Run `hubward upload <group config>`. This builds the track hub config
   files using the `trackhub` Python package, and uploads to the server
   configured in the group config.


Going further
-------------

Use `hubward skeleton` to create a template study including directories,
and a `metadata-builder.py` script to aid in programmatic generation of
`metadata.yaml`.

`hubward` includes many helper functions which can be imported into the
processing script.

Contents:

.. toctree::
   :maxdepth: 2

   installation
   hubward
   contributing
   authors
   history



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

