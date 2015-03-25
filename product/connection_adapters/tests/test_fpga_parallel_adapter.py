#!/usr/bin/env python

"""
Tests FPGAParallelAdapterTests
"""

from common.tests.pyunit_helpers import *
from unittest import TestCase, main

from product.register import *
from product.package import *
from product.connection_adapters.fpga_parallel_adapter import *

class FPGAParallelAdapterTests(TestCase):
    """Tests a Package session via a FPGA Parallel Adapter."""
    
    FOUND = None
    
    def run(self, result=None):
        """Only run the adapter tests when the adapter is detected"""
        if FPGAParallelAdapterTests.FOUND == True or FPGAParallelAdapter.detect():
            super(FPGAParallelAdapterTests, self).run(result)
            FPGAParallelAdapterTests.FOUND = True
        else:
            FPGAParallelAdapterTests.FOUND = False
            #print 'FPGAParallelAdapter not detected.'

    def setUp(self):
        """Loading Package from text file"""
        self.dut = Package.from_txt_file(exepath('../../tests/mocks/DES_65nm_Fuji.txt'), 'Parallel FPGA')

        
    def tearDown(self):
        self.dut.top.reset()
        
    # Verify Constants -------------------------------------------
    
        
    def test_constants_assignment(self):
        """Prepare check and commit at register"""

        bist_mode_defaults = {
            'NO_BIST' : 'b0000',
            'K28.5' : 'b0001',
            'D21.5' : 'b0010',
            'K28.7' : 'b0011',
            'PCI_COMPLIANCE' : 'b0100',
            'D24.3' : 'b0101',
            'ALL0' : 'b0110',
            'ALL1' : 'b0111',
            'PRBS7' : 'b1000',
            'PRBS10' : 'b1001',
            'PRBS15' : 'b1010',
            'PRBS23' : 'b1011',
            'PRBS31' : 'b1100'
            }

        # Verify default
        self.assertEqual(self.dut.top.lane_1['BIST_MODE'].check(), 1)
        
        # Verify all constants
        for constant in bist_mode_defaults:
            self.dut.top.lane_1.bist_mode.prepare(constant)
            #x = self.dut.top.lane_1['BIST_MODE'].check()
            #print x
            self.assertEqual(self.dut.top.lane_1['BIST_MODE'].check(), bin_to_int(bist_mode_defaults[constant][1:]))
        
        
    # Prepare, Check, Commit -------------------------------------------
    
    
    def test_disable_with_prepare(self):
        """Register Disable / Enable and then Prepare / Commit""" 

        # Disable registers
        self.dut.top.cb.vco_cal.disable()

        # Check at register
        self.assertEqual(self.dut.top.lane_1['BIST_MODE'].check(), 1)
        
        # Prepare at SCR and verify with check at register
        self.dut.top.prepare('BIST_MODE','b1010')
        self.assertEqual(self.dut.top.lane_1['BIST_MODE'].check(), 10)
        self.assertEqual(self.dut.top.lane_3['BIST_MODE'].check(), 10)
        
        # Commit at SCR
        self.dut.top.commit()
        
        # Verify with check
        self.assertEqual(self.dut.top.lane_1.bist_mode.is_sent, True)
        self.assertEqual(self.dut.top.lane_1.bist_mode.sent, 10)
        self.assertEqual(self.dut.top.lane_3.bist_mode.sent, 10)   
    
        
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
        
        
        
    # Prepare, Clear -------------------------------------------
    
    
        
        
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
        
        
        
    # Set, Reset -------------------------------------------
    
    
    
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
        
        
        
    # Set, Refresh, Inspect, Get -------------------------------------------
    
    

    def test_refresh_inspect_at_register(self):
        """Set a value, refresh and verify at the register"""

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
        """Set a value, refresh and verify at the block"""

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
        """Set a value, refresh and verify at the scr"""

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
        """Set a value, refresh and verify at the package"""

        # Set a value
        self.dut.set('BIST_MODE',10)

        # NOTE - On packages with more than one SCR, a orientation switch occurs which
        #        causes the output buffers to be updated. On packages with just one orientation
        #        the target switch does not occur. The result is that a call to inspect (and possible other methods)
        #        from will return different results depending on whether or not more than one orientation
        #        is present.
        
        orientation_count = len(self.dut.orientations)
        
        # Verify value with inspect
        results = self.dut.inspect('BIST_MODE')
        for orientation in self.dut.orientations:
            for lane in self.dut[orientation].lanes:
                if orientation_count == 1:
                    self.assertEqual(results[orientation][self.dut[orientation].lanes[lane].label], 1)
                else:
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

        # NOTE - On packages with more than one SCR, a orientation switch occurs which
        #        causes the output buffers to be updated. On packages with just one orientation
        #        the target switch does not occur. The result is that a call to inspect (and possible other methods)
        #        from will return different results depending on whether or not more than one orientation
        #        is present.

        orientation_count = len(self.dut.orientations)
        
        # Verify old value with inspect
        results = self.dut.inspect('BIST_MODE')
        for orientation in self.dut.orientations:
            for lane in self.dut[orientation].lanes:
                if orientation_count == 1:
                    self.assertEqual(results[orientation][self.dut[orientation].lanes[lane].label], 1)
                else:
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

