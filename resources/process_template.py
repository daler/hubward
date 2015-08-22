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
