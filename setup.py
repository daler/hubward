#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')
requirements = [i.strip() for i in open('requirements.txt')]
version = open(os.path.join(os.path.dirname(__file__), 'hubward', 'version.py')).readline().split()[-1].replace('"', '')
print(version)

setup(
    name='hubward',
    version=version,
    description='Manage the visualization of large amounts of other people\'s [often messy] genomics data',
    long_description=readme + '\n\n' + history,
    author='Ryan Dale',
    author_email='dalerr@niddk.nih.gov',
    url='https://github.com/daler/hubward',
    packages=[
        'hubward',
    ],
    package_dir={'hubward':
                 'hubward'},
    include_package_data=True,
    data_files=[
        (
            'hubward',
            [
                'resources/metadata_builder_template.py',
                'resources/metadata_schema.yaml',
                'resources/group_schema.yaml',
                'resources/process_template.py',
                'resources/process_template.sh',
                'resources/dat2bigbed.sh',
            ]
        ),
    ],
    scripts=[
        'hubward/hubward',
    ],
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='hubward',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
