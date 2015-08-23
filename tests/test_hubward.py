#!/usr/bin/env python
# -*- coding: utf-8 -*-


import unittest
import os
import hubward


class TestNewStudy(unittest.TestCase):
    lab = '/tmp/lab'
    label = 'label'
    def setUp(self):
        hubward.utils.new_study(self.lab, self.label)

    def test_files_created(self):
        files = [
            '',
            'raw-data',
            'processed-data',
            'processed-data/bed',
            'processed-data/bam',
            'processed-data/bigwig',
            'processed-data/bigbed',
            'src',
            'src/get-data.bash',
            'src/process.py',
            'metadata-builder.py',
            'README',
        ]
        for f in files:
            fn = os.path.join(self.lab, self.label, f)
            assert os.path.exists(fn), fn

    def test_metadata_builder_contents(self):
        """
        makes sure the pkg_resource is getting the right contents
        """
        template = os.path.join(
            os.path.dirname(__file__),
            '..',
            'resources',
            'metadata_builder_template.py')
        expected_contents = open(template).read()
        observed_contents = open(
            os.path.join(self.lab, self.label, 'metadata-builder.py')).read()
        assert len(expected_contents) > 0
        assert len(observed_contents) > 0
        self.assertEqual(expected_contents, observed_contents)


    def tearDown(self):
        #os.system('rm -r %s' % self.lab)
        pass


if __name__ == '__main__':
    unittest.main()
