#!/usr/bin/env python

"""
USB Adapter
"""

from product.connection_adapters.abstract_adapter import *

class USBAdapter(AbstractAdapter):
    """USB Adapter"""

    entity_name = 'usb_adapter'
    entity_atts = []

    def __init__(self):
        # Prepare Parent
        super(USBAdapter, self).__init__()
        
        # Set abstract properties
        self._type = 'USB'
        self.__port = None
        
        # Which SCR was targeted last
        self._cur_target    = None
        
        self._input_buffer  = None
        self._output_buffer = None
        
        # Which RAM address did I talk to last
        self._cur_ram_address = 0
        
        raise NotImplementedError()
    
    @staticmethod
    def detect():
        """Trys to connect via USB and returns True or False if it is able to connect."""
        return False


    @property
    def state(self):
        """Returns the state of the USB connection."""
        if self._connected:
            return 'active'
        else:
            return 'no connection'
        
    
if __name__=='__main__' :
    pass
