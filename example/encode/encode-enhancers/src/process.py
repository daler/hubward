#!/usr/bin/env python

import sys
import os
import pybedtools
from pybedtools.contrib.bigbed import bigbed
from pybedtools.contrib.bigwig import bedgraph_to_bigwig
from pybedtools import featurefuncs
from hubward import utils
import numpy as np
import sh

source = sys.argv[1]
target = sys.argv[2]

f = open(source)
f.readline()
def gen():
    for line in f:
        chrom, start = line.strip().split()
        yield pybedtools.create_interval_from_list([
            chrom,
            start,
            str(int(start) + 1)])
x = pybedtools.BedTool(gen()).saveas()
bigbed(x, genome='dm3', output=target)


