#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import json
import pyaml
from collections import OrderedDict
import os
d = OrderedDict(study=OrderedDict(), data=[])

d['study']['reference'] = "CHANGE ME (copy from citation manager)"
d['study']['PMID'] = 'CHANGE ME (format is "00000")'
d['study']['description'] = 'CHANGE ME (study description'
d['study']['label'] = 'CHANGE ME (unique label here)'
d['study']['processing'] = open('README').read()

FILENAMES = """
suhw_kc.bed
shep_bg3.bed
"""

fns = [i for i in FILENAMES.splitlines(False) if len(i) > 0]

d['data'] = []
for fn in fns:
    original = os.path.join('raw-data', fn)
    processed = os.path.join('processed-data/bigbed/', fn.replace('bed', 'bigbed'))
    script = os.path.join('src', 'process.py')

    # example conversion of filenams to description/label fields
    ab, ct = fn.replace('.bed', '').split('_')
    description = '{ab} ChIP-chip in {ct} cells'.format(**locals())
    label = '{ab}-{ct}'.format(**locals())

    # See http://genome.ucsc.edu/goldenPath/help/trackDb/trackDbHub.html
    trackinfo = {
        'visibility': 'dense',
        'itemRgb': '"on"',
        'minGrayLevel': 3,
    }

    d['data'].append(
        dict(
            original=original,
            processed=processed,
            script=script,
            description=description,
            label=label,
            genome='dm3',
            url='url to supplemental data',
            type='bigbed',
            trackinfo=trackinfo,
        )
    )


pyaml.dump(d, open('metadata.yaml', 'w'), vspacing=[1,1])
