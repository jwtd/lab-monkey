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
        
    def test_prepare_and_clear(self):
        """Prepare and clear at register"""

        # Pending is empty to start with
        self.assertEqual(self.dut.top.lane_1.pending, [])
        
        # Prepare three registers
        self.dut.top.lane_1.tx_rclk_en.prepare('1')      # meta reference
        self.dut.top.lane_1['BIST_MODE'].prepare('b1010') # bracket reference
        self.dut.top.lane_1['SJ_FREQ'].prepared = 'b111'  # Value assignement
        
        # Get results and verify length and contents
        now_pending = self.dut.top.lane_1.pending
        self.assertEqual(len(now_pending), 3)
        self.assertEqual(('top.lane_1.tx_rclk_en : 0 => 1' in now_pending), True)
        self.assertEqual(('top.lane_1.bist_mode : 1 => 10' in now_pending), True)
        self.assertEqual(('top.lane_1.sj_freq : 0 => 7' in now_pending), True)
        
        # Selectively clear and verify
        self.dut.top.lane_1['BIST_MODE'].clear()
        now_pending = self.dut.top.lane_1.pending

        self.assertEqual(len(now_pending), 2)
        self.assertEqual(('top.lane_1.bist_mode : 0001 => 1010' in now_pending), False)
        
        # Clear and verify
        self.dut.top.lane_1.tx_rclk_en.clear()
        self.dut.top.lane_1['SJ_FREQ'].clear()
        now_pending = self.dut.top.lane_1.pending
        self.assertEqual(len(now_pending), 0)
        
    def test_prepare_at_block(self):
        """Prepare and clear at block"""

        # Pending is empty to start with
        self.assertEqual(self.dut.top.lane_1.pending, [])
        
        # Prepare two registers on two seperate lanes
        self.dut.top.lane_1.prepare('TX_RCLK_EN', 'b1')
        self.dut.top.lane_1.prepare('BIST_MODE', 'b1010')
        self.dut.top.lane_7.prepare('TX_RCLK_EN', 'b1')
        self.dut.top.lane_7.prepare('BIST_MODE', 'b1010')
        
        # Get results and verify length and contents
        now_pending = self.dut.top.lane_1.pending
        self.assertEqual(len(now_pending), 2)
        self.assertEqual(('top.lane_1.tx_rclk_en : 0 => 1' in now_pending), True)
        self.assertEqual(('top.lane_1.bist_mode : 1 => 10' in now_pending), True)
        
        now_pending = self.dut.top.lane_7.pending
        self.assertEqual(len(now_pending), 2)
        self.assertEqual(('top.lane_7.tx_rclk_en : 0 => 1' in now_pending), True)
        self.assertEqual(('top.lane_7.bist_mode : 1 => 10' in now_pending), True)

        # Pending at the SCR should show both
        now_pending = self.dut.top.pending
        self.assertEqual(len(now_pending), 4)

        # Selectively clear and verify
        self.dut.top.lane_1.clear()
        now_pending = self.dut.top.lane_1.pending
        self.assertEqual(len(now_pending), 0)
        
        # Lane 7 should still have 2 values
        now_pending = self.dut.top.lane_7.pending
        self.assertEqual(len(now_pending), 2)

        # Clear and verify
        self.dut.top.lane_7.clear()
        now_pending = self.dut.top.lane_7.pending
        self.assertEqual(len(now_pending), 0)

    def test_prepare_at_scr(self):
        """Prepare and clear at SCR"""
        # Pending is empty to start with
        self.assertEqual(self.dut.top.lane_1.pending, [])

        # Prepare two registers on each SCR so that they will be set in all lanes
        self.dut.top.prepare('TX_RCLK_EN', '1')
        self.dut.bottom.prepare('TX_RCLK_EN', '1')

        # Get results from a single lane and verify length and contents
        now_pending = self.dut.top.lane_1.pending
        self.assertEqual(len(now_pending), 1)
        self.assertEqual(('top.lane_1.tx_rclk_en : 0 => 1' in now_pending), True)
        
        # Get results from SCR and verify length and contents
        now_pending = self.dut.top.pending
        self.assertEqual(len(now_pending), 8)
        self.assertEqual(('top.lane_0.tx_rclk_en : 0 => 1' in now_pending), True)
        self.assertEqual(('top.lane_1.tx_rclk_en : 0 => 1' in now_pending), True)
        self.assertEqual(('top.lane_2.tx_rclk_en : 0 => 1' in now_pending), True)
        self.assertEqual(('top.lane_7.tx_rclk_en : 0 => 1' in now_pending), True)

        now_pending = self.dut.bottom.pending
        self.assertEqual(len(now_pending), 8)
        self.assertEqual(('bottom.lane_0.tx_rclk_en : 0 => 1' in now_pending), True)
        self.assertEqual(('bottom.lane_1.tx_rclk_en : 0 => 1' in now_pending), True)
        self.assertEqual(('bottom.lane_2.tx_rclk_en : 0 => 1' in now_pending), True)
        self.assertEqual(('bottom.lane_7.tx_rclk_en : 0 => 1' in now_pending), True)

        # Check pending at the package
        now_pending = self.dut.pending
        self.assertEqual(len(now_pending), 16)

        # Selectively clear and verify
        self.dut.top.clear()
        now_pending = self.dut.top.pending
        self.assertEqual(len(now_pending), 0)
        now_pending = self.dut.bottom.pending
        self.assertEqual(len(now_pending), 8)

        # Clear and verify
        self.dut.clear()
        now_pending = self.dut.pending
        self.assertEqual(len(now_pending), 0)

    def test_prepare_at_package(self):
        """Prepare and clear at Package"""
        # Pending is empty to start with
        self.assertEqual(self.dut.top.lane_1.pending, [])
        
        # Prepare two registers on the package so that they will be set in all SCRs in all lanes        
        self.dut.prepare('TX_RCLK_EN', '1')
        self.dut.prepare('BIST_MODE', 'b1010')

        # Get results from a SCR and verify length and contents
        now_pending = self.dut.top.pending
        self.assertEqual(len(now_pending), 16)
        self.assertEqual(('top.lane_0.tx_rclk_en : 0 => 1' in now_pending), True)
        self.assertEqual(('top.lane_0.bist_mode : 1 => 10' in now_pending), True)
        self.assertEqual(('top.lane_7.tx_rclk_en : 0 => 1' in now_pending), True)
        self.assertEqual(('top.lane_7.bist_mode : 1 => 10' in now_pending), True)

        now_pending = self.dut.bottom.pending
        self.assertEqual(len(now_pending), 16)
        self.assertEqual(('bottom.lane_0.tx_rclk_en : 0 => 1' in now_pending), True)
        self.assertEqual(('bottom.lane_0.bist_mode : 1 => 10' in now_pending), True)
        self.assertEqual(('bottom.lane_7.tx_rclk_en : 0 => 1' in now_pending), True)
        self.assertEqual(('bottom.lane_7.bist_mode : 1 => 10' in now_pending), True)

        # Check pending at the package
        now_pending = self.dut.pending
        self.assertEqual(len(now_pending), 32)
        
        # Selectively clear and verify
        self.dut.top.clear()
        now_pending = self.dut.top.pending
        self.assertEqual(len(now_pending), 0)
        now_pending = self.dut.bottom.pending
        self.assertEqual(len(now_pending), 16)

        # Clear and verify
        self.dut.clear()
        now_pending = self.dut.pending
        self.assertEqual(len(now_pending), 0)

     
        
if __name__ == '__main__':
    main()