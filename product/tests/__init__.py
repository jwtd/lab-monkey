#!/usr/bin/env python

"""Test suite for device module

This test suite consists of a collection of test modules in the
equipment.tests package. Each test module has a name starting with
'test_'.

"""
import unittest

if __name__ == "__main__":
    
    import os
    import sys
    import glob 
    
    root = os.path.abspath('../../')
    if root not in sys.path: 
        sys.path.append(root)
    
    for filename in glob.glob('test_*.py'):
        exec 'from %s import *' % filename[:-3]
    unittest.main()