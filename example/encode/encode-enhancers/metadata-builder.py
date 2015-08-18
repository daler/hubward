#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pyaml                                                                 # [1]
from collections import OrderedDict                                          # [1]
import os                                                                    # [1]

d = OrderedDict(study=OrderedDict(), data=[])                                # [2]

d['study']['reference'] = "Ho, J. W. K. et al. Nature 512, 449-452 (2014)."  # [3]
d['study']['PMID'] = '25164756'                                              # [3]
d['study']['description'] = 'ENCODE predicted enhancers'                     # [3]
d['study']['label'] = 'encode-enhancers'                                     # [3]

d['study']['processing'] = open('README').read()                             # [4]

for celltype in ['S2', 'BG3', 'LE', 'Kc']:                                   # [5]
    d['data'].append(
        dict(
            original=os.path.join(                                           # [6]
                'raw-data', 'DHS_enhancers_%s.txt' % celltype),              # [6]
            processed=os.path.join(                                          # [6]
                'processed-data', 'DHS_enhancers_%s.bigbed' % celltype),     # [6]
            script='src/process.py',                                         # [6]
            description='%s enhancers' % celltype,                           # [6]
            label='enhancers [%s]' % celltype,                               # [6]
            genome='dm3',                                                    # [6]
            url='url to supplemental data',                                  # [6]
            type='bigbed',                                                   # [6]
            trackinfo={                                                      # [6]
                'visibility': 'dense',                                       # [6]
                'tracktype': 'bigBed 3',                                     # [6]
            },
        )
    )

pyaml.dump(d, open('metadata.yaml', 'w'), vspacing=[1,1])                    # [7]
