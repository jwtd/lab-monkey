#!/usr/bin/env python

"""
Tests BitAddress module
"""

from common.tests.pyunit_helpers import *
from unittest import TestCase, main

import yaml

from product.bit_address import *


class StatelessBitAddressTests(TestCase):
    """Tests of BitAddress class"""

    def setUp(self):
        self.ba = BitAddress('My_Test_Register_1')
        
    def test_create_manipulate_value(self):
        self.assertEqual(self.ba.label, 'MY_TEST_REGISTER_1')
        self.assertEqual(self.ba.value, 0)
        
        # Create with default value
        ba = BitAddress('My_Test_Register_2', 1)
        self.assertEqual(ba.value, 1)
        
    def test_create_using_invalid_properties(self):
        """Create with invalid values"""
        self.assertRaises(ValueError, BitAddress, 'MY_TEST_REGISTER_1', 'A')


    def test_representation(self):
        """Register referenced as representation"""
        r = None
        exec('r = ' + repr(self.ba))
        self.assertEqual(r['label'], 'MY_TEST_REGISTER_1')
        self.assertEqual(r['default'], 0)

    def test_reference_as_string(self):
        """Bit address referenced as string"""
        expecting = '(E) MY_TEST_REGISTER_1 = 0'
        self.assertEqual('%s' % self.ba, expecting)

    def test_yaml_format(self):
        """Bit address YAML format"""
        y = yaml.load(self.ba.to_yaml())
        self.assertEqual(y['bit_address']['label'], 'MY_TEST_REGISTER_1')
        self.assertEqual(y['bit_address']['default'], 0)

    def test_xml_format(self):
        """Bit address XML format"""        
        xml = self.ba.to_xml()
        self.assertEqual(xml.label.PCDATA, 'MY_TEST_REGISTER_1')
        self.assertEqual(xml.default.PCDATA, '0')

        

if __name__ == '__main__':
    main()