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
        
    def test_refresh_inspect_at_register(self):
        """Set a value, refresh anc verify at the register"""

        # Set a value
        self.dut.top.lane_1.bist_mode.set(10)
        
        # Verify value with inspect
        self.assertEqual(self.dut.top.lane_1.bist_mode.inspect(), 1)
        
        # Refresh the output buffer
        self.dut.top.lane_1.bist_mode.refresh()
        
        # Verify value with inspect
        self.assertEqual(self.dut.top.lane_1.bist_mode.inspect(), 10)
        

    def test_get_inspect_at_register(self):
        """Set a value, get and inspect at the register"""
        # Set a value
        self.dut.top.lane_1.bist_mode.set(10)
        
        # Verify value with inspect
        self.assertEqual(self.dut.top.lane_1.bist_mode.inspect(), 1)
        
        # Refresh the output buffer
        self.assertEqual(self.dut.top.lane_1.bist_mode.get(), 10)
        
        # Verify value with inspect
        self.assertEqual(self.dut.top.lane_1.bist_mode.inspect(), 10)
        

    def test_refresh_inspect_at_block(self):
        """Set a value, refresh anc verify at the block"""

        # Set a value
        self.dut.top.lane_1.set('BIST_MODE',10)
        
        # Verify value with inspect
        self.assertEqual(self.dut.top.lane_1.inspect('BIST_MODE'), 1)
        
        # Refresh the output buffer
        self.dut.top.lane_1.refresh()
        
        # Verify value with inspect
        self.assertEqual(self.dut.top.lane_1.inspect('BIST_MODE'), 10)
        

    def test_get_inspect_at_block(self):
        """Set a value, get and inspect at the block"""
        # Set a value
        self.dut.top.lane_1.set('BIST_MODE', 10)
        
        # Verify value with inspect
        self.assertEqual(self.dut.top.lane_1.inspect('BIST_MODE'), 1)
        
        # Refresh the output buffer
        self.assertEqual(self.dut.top.lane_1.get('BIST_MODE'), 10)
        
        # Verify value with inspect
        self.assertEqual(self.dut.top.lane_1.inspect('BIST_MODE'), 10)
        

    def test_refresh_inspect_at_scr(self):
        """Set a value, refresh anc verify at the scr"""

        # Set a value
        self.dut.top.set('BIST_MODE',10)
        
        # Verify value with inspect
        results = self.dut.top.inspect('BIST_MODE')
        for lane in self.dut.top.lanes:
            self.assertEqual(results[self.dut.top.lanes[lane].label], 1)

        # Refresh the output buffer
        self.dut.top.refresh()
        
        # Verify value with inspect
        results = self.dut.top.inspect('BIST_MODE')
        for lane in self.dut.top.lanes:
            self.assertEqual(results[self.dut.top.lanes[lane].label], 10)

    def test_get_inspect_at_scr(self):
        """Set a value, get and inspect at the scr"""
        # Set a value
        self.dut.top.set('BIST_MODE', 10)
        
        # Verify value with inspect
        results = self.dut.top.inspect('BIST_MODE')
        for lane in self.dut.top.lanes:
            self.assertEqual(results[self.dut.top.lanes[lane].label], 1)
        
        # Refresh the output buffer
        results = self.dut.top.get('BIST_MODE')
        for lane in self.dut.top.lanes:
            self.assertEqual(results[self.dut.top.lanes[lane].label], 10)
        
        # Verify value with inspect
        results = self.dut.top.inspect('BIST_MODE')
        for lane in self.dut.top.lanes:
            self.assertEqual(results[self.dut.top.lanes[lane].label], 10)
        
        
    def test_refresh_inspect_at_package(self):
        """Set a value, refresh anc verify at the package"""

        # Set a value
        self.dut.set('BIST_MODE',10)
        
        # Verify value with inspect
        results = self.dut.inspect('BIST_MODE')
        for orientation in self.dut.orientations:
            for lane in self.dut[orientation].lanes:
                self.assertEqual(results[orientation][self.dut[orientation].lanes[lane].label], 10)

        # Refresh the output buffer
        self.dut.refresh()
        
        # Verify value with inspect
        results = self.dut.inspect('BIST_MODE')
        for orientation in self.dut.orientations:
            for lane in self.dut[orientation].lanes:
                self.assertEqual(results[orientation][self.dut[orientation].lanes[lane].label], 10)


    def test_get_inspect_at_package(self):
        """Set a value, get and inspect at the package"""
        # Set a value
        self.dut.set('BIST_MODE', 10)
        
        # Verify value with inspect
        results = self.dut.inspect('BIST_MODE')
        for orientation in self.dut.orientations:
            for lane in self.dut[orientation].lanes:
                self.assertEqual(results[orientation][self.dut[orientation].lanes[lane].label], 10)
        
        # Refresh the output buffer
        results = self.dut.get('BIST_MODE')
        for orientation in self.dut.orientations:
            for lane in self.dut[orientation].lanes:
                self.assertEqual(results[orientation][self.dut[orientation].lanes[lane].label], 10)
        
        # Verify value with inspect
        results = self.dut.inspect('BIST_MODE')
        for orientation in self.dut.orientations:
            for lane in self.dut[orientation].lanes:
                self.assertEqual(results[orientation][self.dut[orientation].lanes[lane].label], 10)
                   
        
if __name__ == '__main__':
    main()