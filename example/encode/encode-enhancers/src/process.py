#!/usr/bin/env python

import sys
import pybedtools
from pybedtools.contrib.bigbed import bigbed

source = sys.argv[1]
target = sys.argv[2]

f = open(source)
f.readline()
def gen():
    for line in f:
        chrom, start = line.strip().split()
        yield pybedtools.create_interval_from_list(
            [chrom, start, str(int(start) + 1)])
x = pybedtools.BedTool(gen()).sort().saveas()
bigbed(x, genome='dm3', output=target)
