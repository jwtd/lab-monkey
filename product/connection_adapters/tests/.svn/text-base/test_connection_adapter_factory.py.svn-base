#!/usr/bin/env python

"""
Tests ConnectionAdapterFactory
"""

from common.tests.pyunit_helpers import *
from unittest import TestCase, main

from product.connection_adapters.connection_adapter_factory import *

class ConnectionAdapterFactoryTests(TestCase):
    """Tests of the ConnectionAdapterFactory."""

    def test_ensure_acts_as_factory(self):
        """Try to create a factory class instance"""
        #f = ConnectionAdapterFactory()
        self.assertRaises(Exception, ConnectionAdapterFactory)

    def test_request(self):
        """Whether a request returns a valid adapter"""
        cnn = ConnectionAdapterFactory.request()
        if cnn.type == 'Mock':
            # Should be mock for now
            self.assertEqual(cnn.type, 'Mock')
            self.assertEqual(cnn.connected, False)
            self.assertEqual(cnn.state, 'no connection')
            self.assertEqual('%s' % cnn, 'Mock (no connection)')
        else:
            print 'Mocking'


if __name__ == '__main__':
    main()