#!/usr/bin/env python

import yaml
import os

d = {
    # Bibliographic information about the study
    'study': {
        # Label for this study. The sanitized version of this (non-alphanumeric
        # characters stripped) should be unique among a group.
        'label': 'hubward example',

        # Optional short label for this study. It will be shown in blue link
        # text in the browser. If not provided, the value of 'label' will be
        # used.
        'short_label': 'Hubward example hub',

        # Long-form label for this study. This is shown as a title on the
        # study's configuration page. If not provided, the value of
        # 'short_label' will be used.
        'long_label': 'Example track hub for demonstrating hubward',

        # Optional reference to study, often copied from reference manager.
        # This will be included in the HTML documentation for the study's page
        # in the genome browser.
        'reference': 'See https://github.com/daler/hubward',

        # Optional PubMed ID, e.g. "0001110" or "PMID:001110". If it is
        # present, HTML documentation will create a link to this PubMed entry.
        'PMID': "",

        # Description of the study to be included in the HTML documentation.
        # This is assumed to be in ReStructured Text format, which is converted
        # to HTML. If you're using a metadata-builder.py script, a common
        # pattern is to include the contents of a README file in this field.
        # This is by far the most verbose section, and is used to describe
        # where the data came from as well as any processing that was needed to
        # convert into a format supported by the UCSC Genome Browser.
        'description': open('README.rst').read(),
    }
}

FILENAMES = [
    ('a.dat',  'example interval data'),
    ('b.dat',  'example signal data'),
]

d['tracks'] = []


# This demo script simply does a copy operation, so we can use it for both
# the bigbed and bigwig example data.
script = os.path.join('src', 'dat2bigbed.sh')

for fn, description in FILENAMES:
    original = os.path.join('raw-data', fn)
    if fn.startswith('a'):
        kind = 'bigbed'
        label = 'example features for "a"'

        # See http://genome.ucsc.edu/goldenPath/help/trackDb/trackDbHub.html
        trackinfo = {
            'tracktype': 'bed6',
            'visibility': 'dense',
            'color': '255,0,0',
        }
    elif fn.startswith('b'):
        kind = 'bigwig'
        label = 'example signal for "b"'
        trackinfo = {
            'tracktype': 'bigwig',
            'visibility': 'full',
            'viewLimits': '0:5',
        }

    processed = os.path.join('processed-data/', fn.replace('dat', kind))
    source = {
        'url': ('https://raw.githubusercontent.com/daler/hubward'
                '/master/resources/{0}'.format(fn)),
        'fn': fn,
    }

    d['tracks'].append(
        dict(
            original=original,
            processed=processed,
            script=script,
            description=description,
            short_label=label,
            genome='hg19',
            source=source,
            type=kind,
            trackinfo=trackinfo,
        )
    )

yaml.dump(d, open('metadata.yaml', 'w'), default_flow_style=False)
