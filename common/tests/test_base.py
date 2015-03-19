#!/usr/bin/env python

"""Tests Application Base module"""

from common.tests.pyunit_helpers import *
from unittest import TestCase, main

from gnosis.xml.objectify import XML_Objectify
import yaml

from common.base import *

class AppBaseTests(TestCase):
    """Tests Application Base module."""

    def setUp(self):
        self.base = AppBase()
        self.base.prop1 = 1
        self.base.prop2 = 'Two'
        self.base.prop3 = True
        self.base.__class__.entity_atts = ['prop1','prop2','prop3']

    def test_logger(self):
        self.assertEqual(self.base.log.name, 'root')

    def test_methodize_label(self):
        self.assertEqual(methodize_label('This Is a Test'), 'this_is_a_test')
        self.assertEqual(methodize_label('Hyphen-Test'), 'hyphen_test')
        self.assertEqual(methodize_label('Wild!@#$%^&*()-+Characters'), 'wild_characters')
        self.assertEqual(methodize_label('Big       Space'), 'big_space')
        self.assertEqual(methodize_label('Wild  !@#$   %^&*()-+  Characters     and    SPACE'), 'wild_characters_and_space')
        
    def test_append_reference(self):
        a = AppBase()
        a.__name__ = 'My name is a'
        b = AppBase()
        b.__name__ = 'My name is b'
        append_reference(a, 'Here Is My Friend b', b)
        
        # Check target reference
        self.assertEqual(a.__dict__.has_key('here_is_my_friend_b'), True)
        self.assertEqual(a.here_is_my_friend_b.__name__, 'My name is b')

        # Ensure that assignment applies only to the target instance
        self.assertEqual(b.__dict__.has_key('here_is_my_friend_b'), False)

    def test_current_instance_state(self):
        """Test retrieving the current state of an object instance as a dictionary"""
        r = self.base.current_instance_state()

        self.assertEqual(r['prop1'], 1)
        self.assertEqual(r['prop2'], 'Two')
        self.assertEqual(r['prop3'], True)

    def test_repr(self):
        """Test retrieving the current state of an object as a representation string"""
        r = None
        exec('r = ' + repr(self.base))
        self.assertEqual(r['prop1'], 1)
        self.assertEqual(r['prop2'], 'Two')
        self.assertEqual(r['prop3'], True)

    def test_xml_as_obj(self):
        # Test using a file path as a seed
        xml_seed = exepath('mocks/xml_as_object_seed.xml')
        xml = xml_as_obj(xml_seed)
        self.assertEqual(xml[0].var[0].description.PCDATA, 'file foo')
        
        # Test using raw xml as a seed
        xml_seed = '''<group>
                        <var><description>raw foo</description></var>
                        <var><description>raw bar</description></var>
                      </group>'''
        xml = xml_as_obj(xml_seed)
        self.assertEqual(xml[0].var[0].description.PCDATA, 'raw foo')
        
        # Test using an instance of gnosis
        xml_seed = '''<group>
                        <var><description>gnosis foo</description></var>
                        <var><description>gnosis bar</description></var>
                      </group>'''
        xml_obj = XML_Objectify(xml_seed).make_instance()
        xml = xml_as_obj(xml_obj)
        self.assertEqual(xml[0].var[0].description.PCDATA, 'gnosis foo')
        
   
    def test_to_xml(self):
        """Test conversion to XML format"""
        # Request as objectified XML document
        xml = self.base.to_xml()
        self.assertEqual(xml.prop1.PCDATA, '1')
        self.assertEqual(xml.prop2.PCDATA, 'Two')
        self.assertEqual(xml.prop3.PCDATA, 'True')
        
        # Request as string
        xml_string = self.base.to_xml(output='str')
        self.assertEqual(xml_string, '<?xml version="1.0" encoding="UTF-8"?>\n<app_base><prop1>1</prop1><prop2>Two</prop2><prop3>True</prop3></app_base>')
        xml = XML_Objectify(xml_string).make_instance()
        self.assertEqual(xml.prop1.PCDATA, '1')
        self.assertEqual(xml.prop2.PCDATA, 'Two')
        self.assertEqual(xml.prop3.PCDATA, 'True')
        
        # Request as file
        xml_file = exepath('mocks/my_test.xml')
        self.base.to_xml(output=xml_file, indent = True)
        xml = XML_Objectify(xml_file).make_instance()
        self.assertEqual(xml.prop1.PCDATA, '1')
        self.assertEqual(xml.prop2.PCDATA, 'Two')
        self.assertEqual(xml.prop3.PCDATA, 'True')

        # Request as DOM
        xml_dom = self.base.to_xml(output='dom')
        self.assertEqual(xml_dom.firstChild.childNodes[0].firstChild.nodeValue, '1')
        self.assertEqual(xml_dom.firstChild.childNodes[1].firstChild.nodeValue, 'Two')
        self.assertEqual(xml_dom.firstChild.childNodes[2].firstChild.nodeValue, 'True')
        
    def test_to_yaml(self):
        """Test conversion to YAML format"""
        y = yaml.load(self.base.to_yaml())
        self.assertEqual(y['app_base']['prop1'], 1)
        self.assertEqual(y['app_base']['prop2'], 'Two')
        self.assertEqual(y['app_base']['prop3'], True)

    def test_int_to_bin(self):
        """Integer to binary conversion int_to_bin"""        
        self.assertEqual(int_to_bin(0, 4), '0000')
        self.assertEqual(int_to_bin(1, 4), '0001')
        self.assertEqual(int_to_bin(2, 4), '0010')
        self.assertEqual(int_to_bin(3, 4), '0011')
        self.assertEqual(int_to_bin(4, 4), '0100')
        self.assertEqual(int_to_bin(5, 4), '0101')
        self.assertEqual(int_to_bin(6, 4), '0110')
        self.assertEqual(int_to_bin(7, 4), '0111')
        self.assertEqual(int_to_bin(8, 4), '1000')
        self.assertEqual(int_to_bin(9, 4), '1001')
        self.assertEqual(int_to_bin(10, 4), '1010')
        self.assertEqual(int_to_bin(11, 4), '1011')
        self.assertEqual(int_to_bin(12, 4), '1100')
        self.assertEqual(int_to_bin(13, 4), '1101')
        self.assertEqual(int_to_bin(14, 4), '1110')
        self.assertEqual(int_to_bin(15, 4), '1111')
        # Make sure padding works
        self.assertEqual(int_to_bin(15, 10), '0000001111')
        

    def test_bin_to_int(self):
        """Binary to integer conversion"""
        self.assertEqual(bin_to_int('0'), 0)
        self.assertEqual(bin_to_int('1'), 1)
        self.assertEqual(bin_to_int('10'), 2)
        self.assertEqual(bin_to_int('11'), 3)
        self.assertEqual(bin_to_int('100'), 4)
        self.assertEqual(bin_to_int('101'), 5)
        self.assertEqual(bin_to_int('110'), 6)
        self.assertEqual(bin_to_int('111'), 7)
        self.assertEqual(bin_to_int('1000'), 8)
        self.assertEqual(bin_to_int('1001'), 9)
        self.assertEqual(bin_to_int('1010'), 10)
        self.assertEqual(bin_to_int('1011'), 11)
        self.assertEqual(bin_to_int('1100'), 12)
        self.assertEqual(bin_to_int('1101'), 13)
        self.assertEqual(bin_to_int('1110'), 14)
        self.assertEqual(bin_to_int('1111'), 15)
        # Make sure padding works
        self.assertEqual(bin_to_int('0000001111'), 15)

    def test_hex_to_int(self):
        """Hexidecimal to integer conversion"""
        self.assertEqual(hex_to_int('0'), 0)
        self.assertEqual(hex_to_int('1'), 1)
        self.assertEqual(hex_to_int('2'), 2)
        self.assertEqual(hex_to_int('3'), 3)
        self.assertEqual(hex_to_int('4'), 4)
        self.assertEqual(hex_to_int('5'), 5)
        self.assertEqual(hex_to_int('6'), 6)
        self.assertEqual(hex_to_int('7'), 7)
        self.assertEqual(hex_to_int('8'), 8)
        self.assertEqual(hex_to_int('9'), 9)
        self.assertEqual(hex_to_int('A'), 10)
        self.assertEqual(hex_to_int('B'), 11)
        self.assertEqual(hex_to_int('C'), 12)
        self.assertEqual(hex_to_int('D'), 13)
        self.assertEqual(hex_to_int('E'), 14)
        self.assertEqual(hex_to_int('F'), 15)


    def test_data_to_int(self):
        """Hex, binary, or integer conversion"""
        
        self.assertEqual(data_to_int('b1100'), 12)
        self.assertEqual(data_to_int('b1101'), 13)
        self.assertEqual(data_to_int('b1110'), 14)
        self.assertEqual(data_to_int('b1111'), 15)
        
        self.assertEqual(data_to_int('hC'), 12)
        self.assertEqual(data_to_int('hD'), 13)
        self.assertEqual(data_to_int('hE'), 14)
        self.assertEqual(data_to_int('hF'), 15)

        self.assertEqual(data_to_int('12'), 12)
        self.assertEqual(data_to_int('13'), 13)
        self.assertEqual(data_to_int('14'), 14)
        self.assertEqual(data_to_int('15'), 15)


    def test_val_to_type_unit(self):
        self.assertEqual(val_to_type_unit('TESTENUM'),('TESTENUM',None))
        self.assertEqual(val_to_type_unit('1sec'),(1,'sec'))
        self.assertEqual(val_to_type_unit('1.1 SEC'),(1.1, 'SEC'))
        self.assertEqual(val_to_type_unit('1.1 S'),(1.1, 'S'))
        self.assertEqual(val_to_type_unit('1.1'),(1.1, None))
        self.assertEqual(val_to_type_unit(1),(1, None))
        self.assertEqual(val_to_type_unit(1.1),(1.1, None))

    def test_time_to_sec(self):
        """Inspect wait_for time calculation results"""
        self.assertEqual(time_to_sec(5), 5)
        self.assertEqual(time_to_sec('1s'), 1.0)
        self.assertEqual(time_to_sec('1sec'), 1.0)
        self.assertEqual(time_to_sec('0.5m'), 30.0)
        self.assertEqual(time_to_sec('1 m'), 60.0)
        self.assertEqual(time_to_sec('2.5 hours'), 9000.0)

    def test_xhz_to_hz(self):
        # Test base hertz to hertz
        self.assertEqual(xhz_to_hz(1), 1)
        self.assertEqual(xhz_to_hz('10'), 10)
        self.assertEqual(xhz_to_hz('100 Hz'), 100)

        # kHz (kilohertz)  10^3 Hz
        self.assertEqual(xhz_to_hz('1kHz'), 1000)
        self.assertEqual(xhz_to_hz('1.3453 kHz'), 1345.3)
        self.assertEqual(xhz_to_hz('13453kHz'), 13453000)
        
        # MHz (megahertz)  10^6 Hz
        self.assertEqual(xhz_to_hz('1MHz'), 1000000)
        self.assertEqual(xhz_to_hz('1.3453 MHz'), 1345300)
        self.assertEqual(xhz_to_hz('13453MHz'), 13453000000)
        
        # GHz (gigahertz)  10^9 Hz
        self.assertEqual(xhz_to_hz('1GHz'), 1000000000)
        self.assertEqual(xhz_to_hz('1.3453 GHz'), 1345300000)
        self.assertEqual(xhz_to_hz('13453GHz'), 13453000000000)
        
        # THz (terahertz)  10^12 Hz
        self.assertEqual(xhz_to_hz('1THz'), 1000000000000)
        self.assertEqual(xhz_to_hz('1.3453 THz'), 1345300000000)
        self.assertEqual(xhz_to_hz('13453THz'), 13453000000000000)

if __name__ == '__main__':
    main()
    
    
    