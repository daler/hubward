import pyaml
import os
d = dict(study=dict(), data=[])
d['study']['reference'] = "tmp"
d['study']['PMID'] = '001'
d['study']['description'] = 'temp'
d['study']['label'] = 'label'
d['study']['processing'] = ""
d['data'].append(
    dict(
        original='raw-data/a.bed',
        processed='processed-data/bigbed/a.bed',
        script='src/process.py',

