#!/usr/bin/env python

import sys
import os
import pybedtools
from pybedtools.contrib.bigbed import bigbed
from pybedtools.contrib.bigwig import bedgraph_to_bigwig
from pybedtools import featurefuncs
from hubmasonry import utils
import numpy as np
import sh

source = sys.argv[1]
target = sys.argv[2]

x = pybedtools.BedTool(source)
domain = os.path.basename(target).split('HiC-')[1].split('.bigBed')[0]
def gen():
    for i in x:
        if i[-1] == domain:
            yield pybedtools.create_interval_from_list(i.fields[:3])

bigbed(pybedtools.BedTool(gen()).saveas(), genome='dm3', output=target)
