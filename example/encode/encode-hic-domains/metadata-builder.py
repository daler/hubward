#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import json
import pyaml
from collections import OrderedDict
import os
d = OrderedDict(study=OrderedDict(), data=[])

d['study']['reference'] = "Ho, J. W. K. et al. Comparative analysis of metazoan chromatin organization. Nature 512, 449-452 (2014)."
d['study']['PMID'] = '25164756'
d['study']['description'] = 'Hi-C domains [embryo]'
d['study']['label'] = 'Hi-C domains [embryo]'
d['study']['processing'] = open('README').read()

d['data'] = []

def raw(s):
    return os.path.join('raw-data', s)
def proc(s):
    return os.path.join('processed-data', s)

script = 'src/process.py'


for domain in ['Active', 'HP1_centromeric', 'Null', 'PcG']:
    d['data'].append(
        dict(
            original=raw('HiC_EL.bed'),
            processed=proc('HiC-' + domain + '.bigBed'),
            script=script,
            description='Hi-C domain [%s; embryo]' % domain,
            label='Hi-C domain [%s; embryo]' % domain,
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
