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
        self.dut.reset()
        # Force the session contents to None
        self.dut.top.session.erase()
        self.dut.bottom.session.erase()
        
    def test_autoenable(self):
        """Test autoenable"""

        # Test at the package
        self.assertEqual(self.dut.autoenable, True)
        self.assertEqual(self.dut.top.autoenable, True)
        self.assertEqual(self.dut.bottom.autoenable, True)

        # Ensure uniqueness
        self.dut.bottom.autoenable = False
        self.assertEqual(self.dut.autoenable, False)
        self.assertEqual(self.dut.top.autoenable, True)
        self.assertEqual(self.dut.bottom.autoenable, False)

        # Check manual toggles at a register
        r = self.dut.top.common_block['VCO_CODE']
        self.assertEqual(r.enabled, True)
        r.disable()
        self.assertEqual(r.enabled, False)
        r.enable()
        self.assertEqual(r.enabled, True)

        # Check autoenables with sets              
        r = self.dut.bottom.common_block['VCO_CODE']
        self.assertEqual(r.enabled, True)
        r.disable()
        self.assertEqual(r.enabled, False)
        
        # Shouldn't do anything, because bottom's autoeanble is off
        r.set('b11111')
        self.assertEqual(r.enabled, False)
        
        # Should enable the bit because top's autoeanble is on
        r = self.dut.top.common_block['VCO_CODE']
        r.disable()
        self.assertEqual(r.enabled, False)
        r.set('b11111')
        self.assertEqual(r.enabled, True)


    def test_set_and_reset_at_register(self):
        """Set and reset at register"""

        # Verify the register has not been sent
        self.assertEqual(self.dut.top.lane_1.bist_mode.is_sent, False)
        self.assertEqual(self.dut.top.lane_1.bist_mode.sent, None)
        
        # Set the value
        self.dut.top.lane_1.bist_mode.set('b1010')
        
        # Verify that the value was sent all the way across
        self.assertEqual(self.dut.top.lane_1.bist_mode.is_sent, True)
        self.assertEqual(self.dut.top.lane_1.bist_mode.sent, 10)
        
        # Reset the value
        self.dut.top.lane_1.bist_mode.reset()

        # Verify that the value is now back at it's default
        self.assertEqual(self.dut.top.lane_1.bist_mode.is_sent, True)
        self.assertEqual(self.dut.top.lane_1.bist_mode.sent, 1)

    def test_set_and_reset_at_block(self):
        """Set and reset at block"""
        
        # Verify the register has not been sent
        self.assertEqual(self.dut.top.lane_1.bist_mode.is_sent, False)
        self.assertEqual(self.dut.top.lane_1.bist_mode.sent, None)
        
        # Set the value
        self.dut.top.lane_1.set('BIST_MODE', 'b1010')

        # Verify uniqueness and that the value was sent all the way across
        for lane in self.dut.top.lanes:
            label = self.dut.top.lanes[lane].label
            self.assertEqual(self.dut.top.lane_1.bist_mode.is_sent, True)
            if label == 'lane_1':
                self.assertEqual(self.dut.top.lanes[lane].bist_mode.sent, 10)
            else:
                self.assertEqual(self.dut.top.lanes[lane].bist_mode.sent, 1)


    def test_set_and_reset_at_scr(self):
        """Set and reset at scr"""
        
        # Verify the register has not been sent
        for lane in self.dut.top.lanes:
            self.assertEqual(self.dut.top.lanes[lane].bist_mode.is_sent, False)
            self.assertEqual(self.dut.top.lanes[lane].bist_mode.sent, None)
        
        # Set the value
        self.dut.top.set('BIST_MODE', 'b1010')
        
        # Verify that it has been set in all blocks
        for lane in self.dut.top.lanes:
            self.assertEqual(self.dut.top.lanes[lane].bist_mode.is_sent, True)
            self.assertEqual(self.dut.top.lanes[lane].bist_mode.sent, 10) #1010
        
        # Reset and check at scr
        self.dut.top.reset()
        
        # Verify that the value is now back at it's default
        for lane in self.dut.top.lanes:
            self.assertEqual(self.dut.top.lanes[lane].bist_mode.is_sent, True)
            self.assertEqual(self.dut.top.lanes[lane].bist_mode.sent, 1)
        
        
    def test_set_and_reset_at_package(self):
        """Set and reset at the package"""
        
        # Verify the register has not been sent
        for orientation in self.dut.orientations:
            for lane in self.dut[orientation].lanes:
                self.assertEqual(self.dut[orientation].lanes[lane].bist_mode.is_sent, False)
                self.assertEqual(self.dut[orientation].lanes[lane].bist_mode.sent, None)
        
        # Prepare
        self.dut.set('BIST_MODE', 'b1010')

        # Verify that it has been set in all scrs
        for orientation in self.dut.orientations:
            for lane in self.dut[orientation].lanes:
                self.assertEqual(self.dut[orientation].lanes[lane].bist_mode.is_sent, True)
                self.assertEqual(self.dut[orientation].lanes[lane].bist_mode.sent, 10)
        
        # Reset and check
        self.dut.reset()
        
        # Verify that the values have been now been sent
        for orientation in self.dut.orientations:
            for lane in self.dut[orientation].lanes:
                self.assertEqual(self.dut[orientation].lanes[lane].bist_mode.is_sent, True)
                self.assertEqual(self.dut[orientation].lanes[lane].bist_mode.sent, 1)


        
if __name__ == '__main__':
    main()