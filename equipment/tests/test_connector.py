#!/usr/bin/env python

"""Tests of the Connector class"""

from common.tests.pyunit_helpers import *
from unittest import TestCase, main

import yaml

from equipment.connector import Connector

class ConnectorTests(TestCase):
    """Tests of the Connector class"""

    def setUp(self):
        self.cmn = Connector('SMA', 'F', direction = 'O', stackable = False, accessor = 'out1_p', visual_identifier='left terminal', device_label = 'Output 1 (+)', lab_label = 'AAAA')
        self.cfn = Connector('SMA', 'F', direction = 'O', stackable = False, accessor = 'out1_n', visual_identifier='right terminal', device_label = 'Output 1 (-)', lab_label = 'BBBBB')

    def test_create_manipulate_value(self):
        """Create and check values"""
        self.assertEqual(self.cmn.device_label, 'Output 1 (+)')
        self.assertEqual(self.cmn.visual_identifier, 'left terminal')
        self.assertEqual(self.cmn.accessor, 'out1_p')
        self.assertEqual(self.cmn.lab_label, 'AAAA')
        self.assertEqual(self.cmn.gender, 'Female')
        self.assertEqual(self.cmn.type, 'SMA')
        self.assertEqual(self.cmn.direction, 'Output')
        self.assertEqual(self.cmn.stackable, False)

    def test_create_from_xml(self):
        """Create from xml file"""
        c = Connector.from_xml(exepath('mocks/connector.xml'))
        self.assertEqual(c.device_label, 'Output 1 (+)')
        self.assertEqual(c.visual_identifier, 'left terminal')
        self.assertEqual(c.accessor, 'out1_p')
        self.assertEqual(c.lab_label, 'AAAA')
        self.assertEqual(c.type, 'SMA')
        self.assertEqual(c.gender, 'Female')
        self.assertEqual(c.direction, 'Output')    
        self.assertEqual(c.stackable, False)      

    def test_create_using_invalid_properties(self):
        """Create with invalid values"""
        self.assertRaises(ValueError, Connector, 'SMA', 'X')                       # Invalid gender
        self.assertRaises(ValueError, Connector, 'SMA', 'I', direction = 'X')      # Invalid direction
        self.assertRaises(ValueError, Connector, 'SMA', 'I', stackable ='asdfasd') # Invalid stackable

    def test_valid_connect_to_method_calls(self):
        """Make connection gender and direction sensitive connection"""
        # Test good connection with direction sensitivity
        cmi = Connector('SMA', 'M', direction = 'I', stackable = True)
        cfo = Connector('SMA', 'F', direction = 'O', stackable = False)        
        cmi.connect_to(cfo)
        self.assertEqual(cmi.to, cfo)
        self.assertEqual(cfo.to, cmi)

    def test_invalid_connect_to_method_calls(self):
        """Invalid connections from one connector to another"""
        # Invalid gender to make connection
        cmi = Connector('SMA', 'M', direction = 'I')
        cmo = Connector('SMA', 'M', direction = 'O')
        self.assertRaises(ValueError, cmi.connect_to, cmo)
        
        # Invalid Type to make connection
        cfi = Connector('SMA', 'F', direction = 'I')
        cmo = Connector('6pin', 'M', direction = 'O')
        self.assertRaises(ValueError, cfi.connect_to, cmo)

        # Invalid direction to make connection
        cmi = Connector('SMA', 'M', direction = 'I')
        cfi = Connector('SMA', 'F', direction = 'I')
        self.assertRaises(ValueError, cmi.connect_to, cfi)

        
    def test_to_assignment(self):
        """Connect via to assignment"""
        cmi = Connector('SMA', 'M', direction = 'I', stackable = True)
        cfo = Connector('SMA', 'F', direction = 'O', stackable = False)    
        cmi.to = cfo
        self.assertEqual(cmi.to, cfo)

    def test_reference_as_string(self):
        """Connector referenced as string"""
        expecting = 'Female SMA'
        self.assertEqual('%s' % self.cmn, expecting)

    def test_representation(self):
        """Connector referenced as representation"""
        r = None
        exec('r = ' + repr(self.cmn))       
        self.assertEqual(r['device_label'], 'Output 1 (+)')
        self.assertEqual(r['visual_identifier'], 'left terminal')
        self.assertEqual(r['accessor'], 'out1_p')
        self.assertEqual(r['lab_label'], 'AAAA')
        self.assertEqual(r['type'], 'SMA')
        self.assertEqual(r['gender'], 'Female')
        self.assertEqual(r['direction'], 'Output')
        self.assertEqual(r['stackable'], False)  
        
    def test_yaml_format(self):
        """Connector YAML format"""
        y = yaml.load(self.cmn.to_yaml())        
        self.assertEqual(y['connector']['device_label'], 'Output 1 (+)')
        self.assertEqual(y['connector']['visual_identifier'], 'left terminal')
        self.assertEqual(y['connector']['accessor'], 'out1_p')
        self.assertEqual(y['connector']['lab_label'], 'AAAA')
        self.assertEqual(y['connector']['type'], 'SMA')
        self.assertEqual(y['connector']['gender'], 'Female')
        self.assertEqual(y['connector']['direction'], 'Output')
        self.assertEqual(y['connector']['stackable'], False)

    def test_xml_format(self):
        """Connector XML format"""
        xml = self.cmn.to_xml()
        self.assertEqual(xml.device_label.PCDATA, 'Output 1 (+)')
        self.assertEqual(xml.visual_identifier.PCDATA, 'left terminal')
        self.assertEqual(xml.accessor.PCDATA, 'out1_p')
        self.assertEqual(xml.lab_label.PCDATA, 'AAAA')        
        self.assertEqual(xml.type.PCDATA, 'SMA')
        self.assertEqual(xml.gender.PCDATA, 'Female')
        self.assertEqual(xml.direction.PCDATA, 'Output')
        self.assertEqual(xml.stackable.PCDATA, 'False')

if __name__ == '__main__':
    main()