#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    'bleach',
    'pybedtools',
    'fabric',
    'colorama',
    'trackhub',
    'pyaml',
    'sh',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='hubward',
    version='0.1.0',
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
    test_suite='tests',
    tests_require=test_requirements
)
