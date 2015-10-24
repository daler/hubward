``hubward``
===========

A common question when reading an interesting paper is, "how does relate to my
favorite gene locus?". To address this question, usually we need to download
the supplemental data, figure out what format it's in, convert it to some other
useful format, and visualize it alongside our own data.

`hubward` helps manage this process, lowering the effort required to track,
manage, organize, and upload many studies for cross-comparison in the UCSC
Genome Browser.

Data are organized into `track hubs
<https://genome.ucsc.edu/goldenPath/help/hgTrackHubHelp.html>`_ on the UCSC
Genome Browser, and the name `hubward` indicates the direction in which data
are moved into these track hubs. It can also refer to a direction in `other
complex systems <http://wiki.lspace.org/mediawiki/Hubwards>`_.

The separate repository, `hubward-studies
<https://github.com/daler/hubward-studies>`_, contains examples of prepared
track hubs. Subsets of these can be combined into user-defined hubs, or can
serve as examples for preparing other studies.

Overview
--------
`This poster`_ gives an overview of `hubward`, and provides a worked example.


A "study"
---------
The minimal definition of a `hubward` "study" is a directory with
a `metadata.yaml` file. In practice, the directory contains raw data and
conversion scripts. A study generally corresponds to data from a single
published paper, but this is not required.  The `metadata.yaml` file describes
and configures one or many tracks grouped together in a single composite track
which, along with other related studies, is uploaded as a track hub.

The `metadata.yaml` file consists of several sections. The `study` section
stores bibliographic information. It is converted to HTML documentation and
added to the study's configuration page in the UCSC Genome Browser::

    study:
      reference: 'Ho, J. W. K. et al. Nature 512, 449-452 (2014).'
      PMID: 25164756
      description: 'ENCODE predicted enhancers'
      label: encode-enhancers
      processing: "Downloaded data were converted to bigBed format"

The `data` section is a list, with one item for each track to be included in
the hub. Here is one such item in the `data` list::

    data:
        -
            description: "K562 enhancers"
            label: "enhancers [K562]"
            genome: hg19
            infiles: "raw-data/p300_enhancers_K562.txt"
            outfile: "processed-data/p300_enhancers_K562.bigbed"
            script: "scr/process.py"
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
extension of this would be to include additional items for other cell lines in
this data set.


.. note:: 

    **Implementation notes**

    If you're going to be uploading to the UCSC genome browser, the output files
    must be in VCF, BAM, bigBed, or bigWig format. If an input file doesn't exist,
    we look for the `source` key, which tells us the url of the file to download
    and the filename that we get upon downloading that file. Downloaded tarballs
    and zip files are automatically extracted to `raw-data`.

    The script is expected to handle an arbitrary number of arguments where the
    last argument is the desired output file and the remainder of the arguments are
    input files.

Multiple studies can be grouped together using a higher-level config file,
here called `group.yaml`. Each study can have multiple tracks; each group can
have multiple studies. 

For example, if the path to the above `metadata.yaml` file is
`encode/hg19/encode-enhancers`, then that directory can be included in the
`studies` list so that the K562 enhancers track will be uploaded::

    group: encode
    genome: hg19
    name: "encodetracks"
    short_label: "Supp. ENCODE"
    long_label: "Supplemental ENCODE tracks"
    hub_url: "http://localhost/encode/hg19/compiled.hub.txt"

    hub_remote: "/root/encode/hg19/compiled.hub.txt"
    host: "localhost"
    user: "www"
    email: "www@localhost"

    studies:
        - encode/hg19/encode-enhancers


Workflow
--------
To visualize a new dataset, the workflow is the following:

1. Write a `metadata.yaml` file and the corresponding scripts to perform
   conversion.
2. Write a `group config` file file that groups together individual studies.
3. Run `hubward process <group config>`. This parses the group config file, and
   for each defined study, parses its `metadata.yaml` file, downloads data if
   neede, runs conversion scripts if necessary.
4. Run `hubward trackhub <group config>`. This builds the track hub config
   files using the `trackhub` Python package, and uploads to the server
   configured in the group config.


Going further
-------------

Use `hubward skeleton` to create a template study including directories,
and a `metadata-builder.py` script to aid in programmatic generation of
`metadata.yaml`.

`hubward` includes many helper functions which can be imported into the
processing script.
