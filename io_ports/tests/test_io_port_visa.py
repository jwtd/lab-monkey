#!/usr/bin/env python

"""Tests of the VisaSocket class"""

from common.tests.pyunit_helpers import *
from unittest import TestCase, main

import yaml

from io_ports.io_port_visa import *

class VisaSocketTests(TestCase):
    """Tests of the VisaSocket class"""
    
    FOUND = None
    
    def run(self, result=None):
        """Only run the adapter tests when the adapter is detected"""
        if VisaSocketTests.FOUND == True or VisaSocket.detect():
            super(VisaSocketTests, self).run(result)
            VisaSocketTests.FOUND = True
        else:
            VisaSocketTests.FOUND = False
            print 'VisaSocket not detected.'

    def x_test_get_list_and_identify_attached_visa_device(self):
        """Get list and identify attached visa device"""
        addresses = VisaSocket.get_instruments_list()
        self.assertEqual((len(addresses) > 0), True)
        cnn = VisaSocket(addresses[0])
        identity = cnn.ask('*IDN?')
        self.assertEqual(cnn.address, addresses[0])
        self.assertEqual((identity != ''), True)


if __name__ == '__main__':
    main()