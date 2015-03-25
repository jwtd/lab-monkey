#!/usr/bin/env python

"""
Tests Package Session
"""

from common.tests.pyunit_helpers import *
from unittest import TestCase, main

from product.package import *
from product.register import *

class PackageSessionTests(TestCase):
    """Tests a connected package instance"""

    def setUp(self):
        """Loading Package from text file"""
        self.dut = Package.from_txt_file(exepath('mocks/DES_65nm_Fuji.txt'))
        self.dut.connect('Mock')
        
    def test_prepare_check_commit_at_register(self):
        """Prepare check and commit at register"""

        # Prepare and check at register
        self.assertEqual(self.dut.top.lane_1['BIST_MODE'].check(), 1)
        self.dut.top.lane_1.bist_mode.prepare('b1010')        
        self.assertEqual(self.dut.top.lane_1['BIST_MODE'].check(), 10)
        
        # Commit and check sent at register
        self.assertEqual(self.dut.top.lane_1.bist_mode.is_sent, False)
        self.assertEqual(self.dut.top.lane_1.bist_mode.sent, None)
        self.dut.top.lane_1.bist_mode.commit()        
        self.assertEqual(self.dut.top.lane_1.bist_mode.is_sent, True)
        self.assertEqual(self.dut.top.lane_1.bist_mode.sent, 10)

    def test_prepare_check_commit_at_block(self):
        """Prepare check and commit at block"""
        
        # Prepare and check at block
        self.assertEqual(self.dut.top.lane_1.check('BIST_MODE'), 1)
        self.dut.top.lane_1.bist_mode.prepare('b1010')        
        self.assertEqual(self.dut.top.lane_1.check('BIST_MODE'), 10)

        # Verify uniqueness
        results = self.dut.top.check('BIST_MODE')
        for lane in self.dut.top.lanes:
            label = self.dut.top.lanes[lane].label
            if label == 'lane_1':
                self.assertEqual(results[label], 10)
            else:
                self.assertEqual(results[label], 1)

        # Commit and check sent at block
        self.assertEqual(self.dut.top.lane_1.bist_mode.is_sent, False)
        self.assertEqual(self.dut.top.lane_1.bist_mode.sent, None)
        self.dut.top.lane_1.bist_mode.commit()
        self.assertEqual(self.dut.top.lane_1.bist_mode.is_sent, True)
        self.assertEqual(self.dut.top.lane_1.bist_mode.sent, 10)

    def test_prepare_check_commit_at_scr(self):
        """Prepare check and commit at scr"""
        
        # Verify that it's not prepared now
        results = self.dut.top.check('BIST_MODE')
        for lane in self.dut.top.lanes:
            self.assertEqual(results[self.dut.top.lanes[lane].label], 1)
        
        # Prepare
        self.dut.top.prepare('BIST_MODE', 'b1010')
        
        # Verify that it is now prepared
        results = self.dut.top.check('BIST_MODE')
        for lane in self.dut.top.lanes:
            self.assertEqual(results[self.dut.top.lanes[lane].label], 10)
        
        # Verify that none of the values have been sent
        for lane in self.dut.top.lanes:
            self.assertEqual(self.dut.top.lanes[lane].bist_mode.is_sent, False)
            self.assertEqual(self.dut.top.lanes[lane].bist_mode.sent, None)
        
        # Commit and check sent at block
        self.dut.top.commit()
        
        # Verify that the values have been now been sent
        for lane in self.dut.top.lanes:
            self.assertEqual(self.dut.top.lanes[lane].bist_mode.is_sent, True)
            self.assertEqual(self.dut.top.lanes[lane].bist_mode.sent, 10)
        

    def test_prepare_check_commit_at_package(self):
        """Prepare check and commit at the package"""
        
        # Verify that it's not prepared now
        results = self.dut.check('BIST_MODE')
        for orientation in self.dut.orientations:
            for lane in self.dut[orientation].lanes:
                self.assertEqual(results[orientation][self.dut[orientation].lanes[lane].label], 1)
        
        # Prepare
        self.dut.prepare('BIST_MODE', 'b1010')

        # Verify that it is now prepared
        results = self.dut.check('BIST_MODE')
        for orientation in self.dut.orientations:
            for lane in self.dut[orientation].lanes:
                self.assertEqual(results[orientation][self.dut[orientation].lanes[lane].label], 10)

        # Verify that none of the values have been sent
        for orientation in self.dut.orientations:
            for lane in self.dut[orientation].lanes:
                self.assertEqual(self.dut[orientation].lanes[lane].bist_mode.is_sent, False)
                self.assertEqual(self.dut[orientation].lanes[lane].bist_mode.sent, None)
        
        # Commit and check sent at block
        self.dut.commit()
        
        # Verify that the values have been now been sent
        for orientation in self.dut.orientations:
            for lane in self.dut[orientation].lanes:
                self.assertEqual(self.dut[orientation].lanes[lane].bist_mode.is_sent, True)
                self.assertEqual(self.dut[orientation].lanes[lane].bist_mode.sent, 10)
            
        
if __name__ == '__main__':
    main()