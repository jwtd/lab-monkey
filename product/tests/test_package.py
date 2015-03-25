#!/usr/bin/env python

"""
Tests Package Module
"""

from common.tests.pyunit_helpers import *
from unittest import TestCase, main

import yaml

from product.package import *
from product.register import *

class PackageTests(TestCase):
    """Tests Package class"""

    def setUp(self):
        """Loading Package from text file"""
        self.fuji_dut = Package.from_txt_file(exepath('mocks/DES_65nm_Fuji.txt'))
        self.tsmc_dut = Package.from_txt_file(exepath('mocks/DES_65nm_TSMC.txt'))

    def test_load_from_txt_file(self):
        """Loading Package from text file"""

        # Test to see if orientations are accessible
        self.assertEqual(self.fuji_dut.top.sequence,    '01234567X')
        self.assertEqual(self.tsmc_dut.medium.sequence, 'X0123')
        
        # Test Levels and Limits
        self.assertEqual(self.fuji_dut.limits['vdda'], '1.4')
        self.assertEqual(self.fuji_dut.levels['vdda'], '1')
                
        # Ensure that orientations are unique to instances
        self.assertFalse(self.fuji_dut.__dict__.has_key('medium')) # fuji shouldn't have medium
        self.assertFalse(self.tsmc_dut.__dict__.has_key('top'))    # tsmc shouldn't have top

    def test_load_from_xml(self):
        """Loading package from xml"""
        #dut = Package.from_xml('.xml')
        #fuji_dut = Package.from_xml('mocks/DES_90nm_Fuji.xml', connect=False)
        #tsmc_dut = Package.from_xml('mocks/DES_65nm_TSMC.xml', connect=False)

        # Test to see if orientations are accessible
        #self.assertEqual(fuji_dut.top.sequence,    '01234567X')
        #self.assertEqual(tsmc_dut.medium.sequence, 'X0123')
        
        # Ensure that orientations are unique to instances
        #self.assertFalse(fuji_dut.__dict__.has_key('medium')) # fuji shouldn't have medium
        #self.assertFalse(tsmc_dut.__dict__.has_key('top'))    # tsmc shouldn't have top
        pass

    def test_constants_assignment(self):
        """Prepare check and commit at register"""

        bist_mode_defaults = {
            'NO_BIST' : 'B0',
            'K28.5' : 'B1',
            'D21.5' : 'B10',
            'K28.7' : 'B11',
            'PCI_COMPLIANCE' : 'B100',
            'D24.3' : 'B101',
            'ALL0' : 'B110',
            'ALL1' : 'B111',
            'PRBS7' : 'B1000',
            'PRBS10' : 'B1001',
            'PRBS15' : 'B1010',
            'PRBS23' : 'B1011',
            'PRBS31' : 'B1100'
            }
        
        # Verify presence of constants
        for constant in bist_mode_defaults:
            self.assertEqual((constant in self.fuji_dut.register_value_aliases), True)
            self.assertEqual(self.fuji_dut.register_value_aliases[constant], bist_mode_defaults[constant])

    def test_orientation_accessors(self):
        """Exercise orientation accessors"""

        # Test orientation sequences via meta-method accessors
        self.assertEqual(self.fuji_dut.top.sequence,    '01234567X')
        self.assertEqual(self.fuji_dut.bottom.sequence, '0123X4567')
        self.assertEqual(self.tsmc_dut.big.sequence,    '01234567X')
        self.assertEqual(self.tsmc_dut.small.sequence,  '0X1')
        self.assertEqual(self.tsmc_dut.medium.sequence, 'X0123')
        
        # Ensure that orientations are unique to instances
        self.assertFalse(self.fuji_dut.__dict__.has_key('medium')) # fuji shouldn't have medium
        self.assertFalse(self.tsmc_dut.__dict__.has_key('top'))    # tsmc shouldn't have top

        # Test orientation sequences via bracket accessors
        self.assertEqual(self.fuji_dut['top'].sequence,    '01234567X')
        self.assertEqual(self.fuji_dut['bottom'].sequence, '0123X4567')
        self.assertEqual(self.tsmc_dut['big'].sequence,    '01234567X')
        self.assertEqual(self.tsmc_dut['small'].sequence,  '0X1')
        self.assertEqual(self.tsmc_dut['medium'].sequence, 'X0123')
        
        # Ensure that orientations are unique to instances
        self.assertRaises(KeyError, self.fuji_dut.__getitem__,'big')
        self.assertRaises(KeyError, self.tsmc_dut.__getitem__,'top')

    def test_iterator(self):
        """Exercise connection management"""
        expecting = self.fuji_dut.orientations.keys()
        i = 0
        for scr in self.fuji_dut:
            self.assertEqual(scr.label, expecting[i])
            i += 1

        expecting = self.tsmc_dut.orientations.keys()
        i = 0
        for scr in self.tsmc_dut:
            self.assertEqual(scr.label, expecting[i])
            i += 1

    def test_block_accessors(self):
        """Exercise block accessors"""

        # Test block labels via meta-method accessors
        self.assertEqual(self.fuji_dut.top.common_block.label, 'common_block')
        self.assertEqual(self.fuji_dut.top.lane_0.label, 'lane_0')
        self.assertEqual(self.fuji_dut.top.lane_7.label, 'lane_7')       
        
        # Test block labels via bracket accessors
        self.assertEqual(self.fuji_dut.top['common_block'].label, 'common_block')
        self.assertEqual(self.fuji_dut.top['lane_0'].label, 'lane_0')
        self.assertEqual(self.fuji_dut.top['lane_7'].label, 'lane_7')
        
        # Test block labels via lane collection accessors
        self.assertEqual(self.fuji_dut.top.lanes[0].label, 'lane_0')
        self.assertEqual(self.fuji_dut.top.lanes[7].label, 'lane_7')

    def test_register_accessors(self):
        """Exercise register accessors """
        self.assertEqual(self.fuji_dut.top.lane_0.bist_mode.value, 1)
        self.assertEqual(self.fuji_dut.top.lane_7['bist_mode'].value, 1)

    def test_path_references(self):
        """Verify paths of components"""
        # Orientation
        self.assertEqual(self.fuji_dut.top.path, 'top')
        # Common Block
        self.assertEqual(self.fuji_dut.top.common_block.path, 'top.common_block')
        # Lane
        self.assertEqual(self.fuji_dut.top.lane_0.path, 'top.lane_0')
        self.assertEqual(self.fuji_dut.top.lane_7.path, 'top.lane_7')
        # Register
        self.assertEqual(self.fuji_dut.top.lane_0.bist_mode.path, 'top.lane_0.bist_mode')
        self.assertEqual(self.fuji_dut.top.lane_7.bist_mode.path, 'top.lane_7.bist_mode')

    def test_connection_management(self):
        """Exercise connection management"""
        self.assertEqual(self.fuji_dut.connected, False)
        self.assertEqual(self.fuji_dut.connection, None)
        self.fuji_dut.connect('Mock')
        self.assertEqual(self.fuji_dut.connection.type, 'Mock')
        self.assertEqual(self.fuji_dut.connected, True)


    def test_reference_as_string(self):
        """Package referenced as string"""
        self.assertEqual('%s' % self.fuji_dut, '65nm Fujitsu')
        
    def test_representation(self):
        """Package referenced as representation"""
        r = None
        exec('r = ' + repr(self.fuji_dut))
        self.assertEqual(r['metadata']['process'], 'Fujitsu')
        self.assertEqual(r['metadata']['scale'], '65nm')
        self.assertEqual(len(r['orientations']), 2)
        self.assertEqual(r['orientations']['top']['label'],'top')
        self.assertEqual(r['orientations']['top']['sequence'],'01234567X')
        self.assertEqual(r['orientations']['bottom']['label'],'bottom')
        self.assertEqual(r['orientations']['bottom']['sequence'],'0123X4567')

    def test_yaml_format(self):
        """Package YAML format"""
        # TODO: Figure out why YAML formatter gets bogged down
        #y = yaml.load(self.scr.to_yaml())
        #self.assertEqual(y['register_collection']['type'],'lane')
        #self.assertEqual(y['register_collection']['label'], 'lane_1')
        #for i, register in enumerate(y['register_collection']['registers']):
        #    self.assertEqual(register['label'], self.registers[i].label)
        pass

    def test_xml_format(self):
        """Package XML format"""        
        xml = self.fuji_dut.to_xml()
        self.assertEqual(xml.metadata.process.PCDATA, 'Fujitsu')
        self.assertEqual(xml.metadata.scale.PCDATA, '65nm')
        self.assertEqual(len(xml.orientations.serial_control_register), 2)
        self.assertEqual(xml.orientations.serial_control_register[0].label.PCDATA,'bottom')
        self.assertEqual(xml.orientations.serial_control_register[0].sequence.PCDATA,'0123X4567')
        self.assertEqual(xml.orientations.serial_control_register[1].label.PCDATA,'top')
        self.assertEqual(xml.orientations.serial_control_register[1].sequence.PCDATA,'01234567X')



if __name__ == '__main__':
    main()