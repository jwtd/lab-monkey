#!/usr/bin/env python

"""
Tests Register module
"""

from common.tests.pyunit_helpers import *
from unittest import TestCase, main

import yaml

from product.register import *


class RegisterTests(TestCase):
    """Tests of the Register class"""

    def setUp(self):
        self.r = Register('MY_TEST_REGISTER', 'I', enable_index = 9, start_index = 10, width = 3, default_value = '010')

    def test_create_manipulate_value(self):
        """Create and manipulate value"""
        r = Register('MY_TEST_REGISTER', 'I', enable_index = 9, start_index = 10, width = 3, default_value = '110')
        self.assertEqual(r.value, 6) # b010 = 2
        self.assertEqual(r.bits, '011') # Bits are reversed because of the way the SCR goes into the FPGA

    def test_create_using_invalid_properties(self):
        """Create with invalid values"""
        self.assertRaises(ValueError, Register, 'MY_TEST_REGISTER', 'I', 9, 10, 3, '0A1')  # Invalid default using nonbinary data
        self.assertRaises(ValueError, Register, 'MY_TEST_REGISTER', 'I', 9, 10, 3, '0110') # Invalid default using too long
        self.assertRaises(ValueError, Register, 'MY_TEST_REGISTER', 'I', 9, 10, -1,'010')  # Invalid width
        self.assertRaises(ValueError, Register, 'MY_TEST_REGISTER', 'I', 9, -1, 3, '010')  # Invalid start_index
        self.assertRaises(ValueError, Register, 'MY_TEST_REGISTER', 'I', -1, 10, 3, '010') # Invalid enable_index
        self.assertRaises(ValueError, Register, 'MY_TEST_REGISTER', 'Z', 9, 10, 3, '010')  # Invalid direction
        self.assertRaises(ValueError, Register, 'MY_TEST_REGISTER', 'I', 9, 9, 3, '010')   # Enable bit index and start index are the same
        # For output registers, the enable bit index and start index can be the same
        try:
            r = Register('MY_TEST_REGISTER', 'O', enable_index = 0, start_index = 0, width = 3, default_value = '010')
        except ValueError:
            self.fail("Output register are allowed to have the enable bit index be the same as the start bit index")

    def test_invalid_value_assignment(self):
        """Invalid value assignment"""
        invalid_values = {
            'too short' : '0',
            'too long' : '0101',
            'not binary' : '0A1',
            'empty' : None
            }
        for k in invalid_values:
            self.assertEqual(self.r.is_value_valid(invalid_values[k]), False)

    def test_enable_bit(self):
        """Test enable bit association"""
        r = Register('MY_TEST_REGISTER', 'I', enable_index = 9, start_index = 10, width = 3, default_value = '101')
        self.assertEqual(r.enable_index, 9)
        self.assertEqual(r.enable_bit, None)
        self.assertEqual(r.enabled, True)
        r.disable() # Will do nothing if not connected
        self.assertEqual(r.enabled, True)
        
        r = Register('MY_TEST_REGISTER', 'O', enable_index = 9, start_index = 10, width = 3, default_value = '101')
        self.assertEqual(r.enable_index, None)
        self.assertEqual(r.enable_bit, None)
        self.assertEqual(r.enabled, True)

    def test_representation(self):
        """Register referenced as representation"""
        r = None
        exec('r = ' + repr(self.r))
        self.assertEqual(r['default'], 2)
        self.assertEqual(r['direction'], 'I')
        self.assertEqual(r['label'], 'MY_TEST_REGISTER')
        self.assertEqual(r['width'], 3)
        self.assertEqual(r['enable_index'], 9)
        self.assertEqual(r['start_index'], 10)

    def test_reference_as_string(self):
        """Register referenced as string"""
        expecting = '(I) MY_TEST_REGISTER = 2'
        self.assertEqual('%s' % self.r, expecting)

    def test_yaml_format(self):
        """Register YAML format"""
        # 'node:\n  allows_children: true\n  id: 1\n  label: Test\n'
        y = yaml.load(self.r.to_yaml())
        self.assertEqual(y['register']['default'], 2)
        self.assertEqual(y['register']['direction'], 'I')
        self.assertEqual(y['register']['label'], 'MY_TEST_REGISTER')
        self.assertEqual(y['register']['width'], 3)
        self.assertEqual(y['register']['enable_index'], 9)
        self.assertEqual(y['register']['start_index'], 10)

    def test_xml_format(self):
        """Register XML format"""        
        xml = self.r.to_xml()
        self.assertEqual(xml.default.PCDATA, '2')
        self.assertEqual(xml.direction.PCDATA, 'I')
        self.assertEqual(xml.label.PCDATA, 'MY_TEST_REGISTER')
        self.assertEqual(xml.width.PCDATA, '3')
        self.assertEqual(xml.enable_index.PCDATA, '9')
        self.assertEqual(xml.start_index.PCDATA, '10')


if __name__ == '__main__':
    main()