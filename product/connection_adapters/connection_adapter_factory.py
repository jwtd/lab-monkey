#!/usr/bin/env python

"""
ConnectionAdapterFactory
"""

from product.connection_adapters.fpga_serial_adapter import *
from product.connection_adapters.fpga_parallel_adapter import *
from product.connection_adapters.usb_adapter import *
from product.connection_adapters.mock_adapter import *

class ConnectionAdapterFactory(object):
    """
    Factory class which returns an instance of a connection adapter. The factory class 
    method request can detect available adapters or return an explicitly requested adapter type.
    """

    def __init__(self):
        raise Exception('Factory classes cannot be instantiated')

    @staticmethod
    def request(type = None):
        """Sniffs out connection and returns an instance of the bridge for the protocol in use"""
        if type == None:
            # Try to detect
            if (FPGAParallelAdapter.detect()):
                return FPGAParallelAdapter()
            elif (FPGASerialAdapter.detect()):
                return FPGASerialAdapter()
            elif (USBAdapter.detect()):
                return USBAdapter()
            elif MockAdapter.detect():
                return MockAdapter()
            else:
                raise LookupError('Could not detect a PC to Device adapter protocol.')
        else:
            # Try to load the request connection
            type = type.lower()
            if type == 'mock' and MockAdapter.detect():
                return MockAdapter()
            elif type == 'parallel fpga' and FPGAParallelAdapter.detect():
                return FPGAParallelAdapter()
            elif type == 'serial fpga' and FPGASerialAdapter.detect():
                return FPGASerialAdapter()
            elif type == 'usb' and USBAdapter.detect():
                return USBAdapter()
            else:
                raise LookupError('Could not detect a %s adapter protocol.' % type)


if __name__=='__main__' :
    #f = ConnectionAdapterFactory.request()
    #print f.type
    pass