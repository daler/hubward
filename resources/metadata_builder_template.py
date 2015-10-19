#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import yaml
import os

# Study configuration
d = {
    'study':

        # This will be included in HTML documentation
        'reference': "CHANGE ME (copy from citation manager)",

        # If provided, HTML documentation will link to this PubMed entry
        'PMID': None,

        # 
        'description': "CHANGE ME (brief study description)",

        # Label 
        'label': "CHANGE ME (unique label)",
        'processing': open('README').read()
}

FILENAMES = [
    'suhw_kc.bed',
    'shep_bg3.bed',
]

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
