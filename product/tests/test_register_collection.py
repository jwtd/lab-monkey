#!/usr/bin/env python

"""
Tests Register Collection module
"""

from common.tests.pyunit_helpers import *
from unittest import TestCase, main

import yaml

from product.register import *
from product.register_collection import  *

import helpers

class StatelessRegisterCollectionTests(TestCase):
    """Tests of the RegisterCollection class"""
    
    def setUp(self):
                        #label, direction, enable_index, start_index, width, default_value
        r1 = Register('Reg_1', 'I', 0, 1, 1, '0')
        r2 = Register('Reg_2', 'I', 2, 3, 2, '10')
        r3 = Register('Reg_3', 'I', 5, 6, 5, '01110')
        r4 = Register('Reg_4', 'O', 0, 11, 1, '0')
        r5 = Register('Reg_5', 'O', 0, 12, 4, '0000')
        self.registers = [r1,r2,r3,r4,r5]
        self.rc = RegisterCollection(self.registers, 'lane', 'lane_1')

    def test_create(self):
        """Create with valid values"""
        reg_collection = RegisterCollection(self.registers, 'lane', 'lane_1')
        self.assertEqual(reg_collection.type, 'lane')
        self.assertEqual(reg_collection.label, 'lane_1')
        self.assertEqual(reg_collection.value, '1010110111000000')

    def test_create_using_invalid_parameters(self):
        """Create with invalid values"""
        self.assertRaises(ValueError, RegisterCollection, [], 'my_block')  # Create without any registers
        self.assertRaises(AttributeError, RegisterCollection, ['x', 1, 'y'], 'my_block')  # Create with objects that aren't registers

    def test_iterator(self):
        """Iterate over the collection multiple times"""
        #self.rc.to_log()
        # Test first pass through
        index = 0
        for item in self.rc:
            self.assertEqual(item, self.registers[index])
            index += 1
        # Test second pass to ensure iterator is reusable
        index = 0
        for item in self.rc:
            self.assertEqual(item, self.registers[index])
            index += 1

    def test_registers_iteration(self):
        """Registers returns reference to registers only (ensure enable bit nodes aren't included)"""
        for index, item in enumerate(self.rc.registers):
            self.assertEqual(item, self.registers[index])

    def test_register_lookups(self):
        """Look up registers by brackets, register method, and meta methods"""
        self.assertEqual(self.rc['Reg_3'], self.registers[2])
        self.assertEqual(self.rc.register('Reg_3'), self.registers[2])
        self.assertEqual(self.rc.reg_3, self.registers[2])

    def test_register_at_bit_address(self):
        """Look up registers by bit address"""       
        self.assertEqual(self.rc.register_at_bit_address(4), self.registers[1])  # End of value of r2
        self.assertEqual(self.rc.register_at_bit_address(5), self.registers[2])  # Enable bit of r3
        self.assertEqual(self.rc.register_at_bit_address(6), self.registers[2])  # Start of value of r3
        self.assertEqual(self.rc.register_at_bit_address(11), self.registers[3]) # Start of output value for r4

    def test_create_mock_blocks(self):
        """Create mock commong blocks"""
        # From file
        common_block_registers, lane_registers = helpers.register_collections_from_txt_file(exepath('mocks/DES_65nm_Fuji.txt'))
        
        cb = RegisterCollection(common_block_registers, 'common_block', 'common_block')
        self.assertEqual(cb.value, '000000000000000000000000000010000000000010100000101000010100001010111111101010110010101010101111101010')
        
        lane = RegisterCollection(lane_registers, 'lane', 'lane_0')
        self.assertEqual(lane.value, '000000000000000000010001000000101100010101010101010101010100101010101010101111111110100101111011111010101110101000010101001010100110100000100010010101011100000000000000001010000100010001010100111001010')

    def test_translate_register_string(self):
        """Translate a register block string"""

        # 10 101 101110 0 0000

        # Reg_3 Disabled with default value
        mod_r3_ed = '1010100111000000'
        results = self.rc.translate_register_string(mod_r3_ed)
        for i,r in enumerate(self.rc):
            self.assertEqual(results[i]['value'], r.default)
            if i == 2:
                self.assertEqual(results[i]['enabled'], False)                
        
        # Reg_3 Enabled with different value
        mod_r3_en = '1010111111000000'
        results = self.rc.translate_register_string(mod_r3_en)
        for i,r in enumerate(self.rc):
            if i == 2:
                self.assertEqual(results[i]['value'], 15)
                self.assertEqual(results[i]['modified'], True)
            else:
                self.assertEqual(results[i]['value'], r.default)
                if r.direction == 'O': 
                    self.assertEqual(results[i]['enabled'], True)
                
        # Reg_5 Output with different value                     
        mod_r5_on = '1010110111000100' 
        results = self.rc.translate_register_string(mod_r5_on)
        for i,r in enumerate(self.rc):
            if i == 4:                
                self.assertEqual(results[i]['modified'], True)
                self.assertEqual(results[i]['value'], 2)
            else:
                self.assertEqual(results[i]['value'], r.default)
                self.assertEqual(results[i]['modified'], False)


    def test_reference_as_string(self):
        """Register collection referenced as string"""
        expecting = 'lane_1'
        self.assertEqual('%s' % self.rc, expecting)
        
    def test_representation(self):
        """Register collection referenced as representation"""
        r = None
        exec('r = ' + repr(self.rc))
        self.assertEqual(r['type'], 'lane')
        self.assertEqual(r['label'], 'lane_1')
        for i, register in enumerate(r['registers']):
            self.assertEqual(register['label'], self.registers[i].label)

    def test_yaml_format(self):
        """Register collection YAML format"""
        # TODO: Figure out why YAML formatter gets bogged down
        #y = yaml.load(self.rc.to_yaml())
        #self.assertEqual(y['register_collection']['type'],'lane')
        #self.assertEqual(y['register_collection']['label'], 'lane_1')
        #for i, register in enumerate(y['register_collection']['registers']):
        #    self.assertEqual(register['label'], self.registers[i].label)
        pass

    def test_xml_format(self):
        """Register collection XML format"""        
        xml = self.rc.to_xml()
        self.assertEqual(xml.type.PCDATA, 'lane')
        self.assertEqual(xml.label.PCDATA, 'lane_1')
        for i, register in enumerate(xml.registers.register):
            self.assertEqual(register.label.PCDATA, self.registers[i].label)


if __name__ == '__main__':
    main()