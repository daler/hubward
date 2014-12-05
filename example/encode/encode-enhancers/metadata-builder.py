#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import json
import pyaml
from collections import OrderedDict
import os
d = OrderedDict(study=OrderedDict(), data=[])

d['study']['reference'] = "Ho, J. W. K. et al. Comparative analysis of metazoan chromatin organization. Nature 512, 449-452 (2014)."
d['study']['PMID'] = '25164756'
d['study']['description'] = 'ENCODE predicted enhancers'
d['study']['label'] = 'encode-enhancers'
d['study']['processing'] = open('README').read()

d['data'] = []

def raw(s):
    return os.path.join('raw-data', s)
def proc(s):
    return os.path.join('processed-data', s)


enhancer_template = """

"""
script = 'src/process.py'

enhancer_celltypes = ['S2', 'BG3', 'LE', 'Kc']
for celltype in enhancer_celltypes:
    d['data'].append(
        dict(
            original=raw('DHS_enhancers_%s.txt' % celltype),
            processed=proc('DHS_enhancers_%s.bigbed' % celltype),
            script=script,
            description='%s enhancers' % celltype,
            label='enhancers [%s]' % celltype,
            genome='dm3',
            url='url to supplemental data',
            type='bigbed',
            trackinfo={
                'visibility': 'dense',
                'tracktype': 'bigBed 3',
            },
        )
    )


pyaml.dump(d, open('metadata.yaml', 'w'), vspacing=[1,1])
