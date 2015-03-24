#!/usr/bin/env python

"""
Tests LabManager
"""

from unittest import TestCase, main
from lab.lab_manager import *

class LabManagerTests(TestCase):
    """Tests of the LabManager class."""

    def setUp(self):
        self.test_procedure = '%s/jitter_tolerance.py' % PROCEDURE_REPOSITORY_PATH

    def test_svn_last_modified_revision(self):
        """Retrieve last modified svn revision"""
        last_modified_ver = svn_last_modified_revision(self.test_procedure)
        self.assertTrue(last_modified_ver > 0)

    def test_retrieve_procedure_class_name(self):
        """Retrieve procedure class name"""
        n = retrieve_procedure_class_name(self.test_procedure)
        self.assertEqual(n, 'JitterToleranceProcedure')

    def test_inspect_procedure_repository(self):
        """Inspect procedure repository"""
        lm = LabManager()
        procedures = lm.inspect_procedure_repository()
        
        self.assertTrue(len(procedures) > 0)

        self.assertTrue(procedures[0].has_key('name'))
        self.assertTrue(procedures[0].has_key('required_values'))
        self.assertTrue(procedures[0].has_key('required_setup'))
        self.assertTrue(procedures[0].has_key('name'))
        self.assertTrue(procedures[0].has_key('description'))
        self.assertTrue(procedures[0].has_key('file'))
        self.assertTrue(procedures[0].has_key('class_name'))
        self.assertTrue(procedures[0].has_key('module_name'))
        self.assertTrue(procedures[0].has_key('last_modified_rev'))


if __name__ == '__main__':
    main()