#!/usr/bin/env python

"""Tests of the PhysicalConnection class"""

from common.tests.pyunit_helpers import *
from unittest import TestCase, main

import yaml

from equipment.connector import Connector
from equipment.physical_connection import PhysicalConnection

class PhysicalConnectionTests(TestCase):
    """Tests of the PhysicalConnection class"""

    def setUp(self):
        self.c = PhysicalConnection.from_xml(exepath('mocks/physical_connection.xml'))

    def test_create(self):
        """Create and check values"""
        self.assertEqual(self.c.manufacturer, 'Astrolab')
        self.assertEqual(self.c.model, 'minibend L-8')
        self.assertEqual(self.c.type, 'Low loss flexible coaxial cable')
        self.assertEqual(self.c.visual_identifier, '8in Male to Male SMA Cable')
        self.assertEqual(self.c.length, '8in')
        self.assertEqual(self.c.asset_class, 'Cable')
        self.assertEqual(self.c.part_code, 'PC6')
        # Test meta references
        self.assertEqual(self.c.a.label, 'A')
        self.assertEqual(self.c.b.label, 'B')

    def test_create_using_invalid_properties(self):
        """Create with invalid values"""
        cm = Connector('SMA', 'M', direction = 'N', visual_identifier='male end')
        cf = Connector('SMA', 'F', direction = 'N', visual_identifier='female end')
        
        self.assertRaises(TypeError, PhysicalConnection, '8in', cm, cf)       # Invalid asset_class
        self.assertRaises(TypeError, PhysicalConnection, 'Cable', cm, cf)     # Invalid length
        self.assertRaises(TypeError, PhysicalConnection, 'Cable', '8in', cf)  # Invalid connectors

    def test_connected_to_from(self):
        """Connect through the cable to the device on the other end"""
        # self.c.connected_to_from(self.c.a)
        # TODO: Implement test when device class is done
        pass
        
    def test_reference_as_string(self):
        """Physical Connection referenced as string"""
        expecting = 'Astrolab minibend L-8 8in Male to Male SMA Cable (PC6)'
        self.assertEqual('%s' % self.c, expecting)
        
    def test_representation(self):
        """Physical Connection referenced as representation"""
        r = None
        exec('r = ' + repr(self.c))       
        self.assertEqual(r['manufacturer'], 'Astrolab')
        self.assertEqual(r['model'], 'minibend L-8')
        self.assertEqual(r['type'], 'Low loss flexible coaxial cable')
        self.assertEqual(r['visual_identifier'], '8in Male to Male SMA Cable')
        self.assertEqual(r['length'], '8in')
        self.assertEqual(r['asset_class'], 'Cable')
        self.assertEqual(r['part_code'], 'PC6')

    def test_yaml_format(self):
        """Physical Connection YAML format"""
        #y = yaml.load(self.c.to_yaml())
        #self.assertEqual(y['physical_connection']['manufacturer'], 'Astrolab')
        #self.assertEqual(y['physical_connection']['model'], 'minibend L-8')
        #self.assertEqual(y['physical_connection']['type'], 'Low loss flexible coaxial cable')
        #self.assertEqual(y['physical_connection']['visual_identifier'], '8in Male to Male SMA Cable')
        #self.assertEqual(y['physical_connection']['length'], '8in')
        #self.assertEqual(y['physical_connection']['asset_class'], 'Cable')
        #self.assertEqual(y['physical_connection']['part_code'], 'PC6')
        pass

    def test_xml_format(self):
        """Physical Connection XML format"""
        xml = self.c.to_xml()
        self.assertEqual(xml.manufacturer.PCDATA, 'Astrolab')
        self.assertEqual(xml.model.PCDATA, 'minibend L-8')
        self.assertEqual(xml.type.PCDATA, 'Low loss flexible coaxial cable')
        self.assertEqual(xml.visual_identifier.PCDATA, '8in Male to Male SMA Cable')
        self.assertEqual(xml.length.PCDATA, '8in')
        self.assertEqual(xml.asset_class.PCDATA, 'Cable')
        self.assertEqual(xml.part_code.PCDATA, 'PC6')

if __name__ == '__main__':
    main()