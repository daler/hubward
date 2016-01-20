Installation
============

`conda`
-------
To most effectively use `hubward`, several command line programs are required
to be on your PATH. The easiest, and recommended, way to install these is with
the ``conda`` package manager, which comes with `Anaconda
<https://www.continuum.io/downloads>`_ Python. Anaconda comes with many
scientific Python packages that are otherwise difficult to install, along with
tools for building isolated environments. It's a very convenient tool.

The following command will install `hubward` plus all optional dependencies
into a new `conda` environment called `hubward-test`::

    conda install -n hubward-test -c r -c bioconda hubward-all

This will install:

- bedtools
- UCSC utilities:
    - wigToBigWig
    - bedGraphToBigWig
    - bedToBigBed
    - bigBedToBed
    - fetchChromSizes
    - liftOver
- CrossMap

To use the new environment (which is isolated and independent from anything you
may already have installed), use::

    source activate hubward-test

Docker
------
The tests are run within a Docker container. Inspect the `docker/Dockerfile` to see how the system is set up, or run::

    docker pull daler/hubward-test
    ./docker-test-wrapper.sh

to perform the test.
