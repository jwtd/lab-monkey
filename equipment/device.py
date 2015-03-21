#!/usr/bin/env python
"""
Represents a device in the lab
"""
import time

from equipment.asset import Asset
from io_ports.io_port_visa import VisaSocket

class Device(Asset):
    """Represents a device in the lab"""

    entity_name = 'device'
    entity_atts = ['manufacturer', 'model', 'type', 'part_code', 'asset_class', 'firmware']


    # Instance Constructor -----------------------------


    def __init__(self, asset_class = None, manufacturer = None, model = None, type = None, part_code = None):
        """"""        
        # Prepare Parent
        super(Device, self).__init__(asset_class, manufacturer, model, type, part_code)
        self._address  = None
        self._cnn      = None
        self._firmware = None

    def __str__(self):
        """
        Returns a string containing the manufacturer model 
        serial_number and type of the device
        """
        return '%s %s %s' % (self.manufacturer, self.model, self.type)

    @property
    def address(self):
        """
        Returns the network address used by the io port to communicate with the device
        """
        return self._address
    
    @property
    def connected(self):
        """
        Returns True or false depending on if the device is connected
        """
        return (self._cnn != None)

    def connect(self, address):
        """
        Establishes a PC to device connection
        """
        # Connect to the device
        self._cnn = VisaSocket(address)
        self._address = address
        
        # Load the devices metadata
        id_response = self._cnn.ask('*IDN?')
        id = VisaSocket.parse_device_identity(id_response)        
        self._manufacturer = id['manufacturer']
        self._model        = id['model']
        self._part_code    = id['part_code']
        if id['metadata'] != []:
            self._firmware = id['metadata'][0] 
        else:
            self._firmware = None
    
    @property
    def firmware(self):
        """
        Returns the firmware installed on the device
        """
        return self._firmware

    @property
    def error(self):
        """
        Returns any System Error Message that may have occured or False if no errors have occured
        """
        s = self._cnn.ask('SYSTEM:ERROR?')
        if (s[0:3] == '+0,' ):
            return False
        else:
            return s[3:]


    # IEEE Mandatory Commands
    
    # *IDN?    Returns device identity
    # *STB?    Read the status byte.
    # *ESR?    Read the standard event status register.
    # *SRE? / *SRE nnn -- where nnn is 0 - 255
    #          Read or Set the service request enable (mask) register.
    # *ESE? / *ESE nnn -- where nnn is 0 - 255
    #          Read or Set the standard event status enable (mask) register.
    #          NOTE: See *ESR? for the meaning of each bit in the mask.
    # *RST     Reset (force) the System to the Cycle screen.
    # *TST?
    # *OPC? / *OPC
    # *WAI

    def clear_errors(self):
        """
        Clears any system errors by clearing the status (*ESR, TESR) registers.
        """
        self._cnn.write('*CLS')
        return (self.error == False)

    def reset(self):
        """
        Sends a reset command to the device.
        NOTE: Any device-specific errors are reset.
        """
        self._cnn.write('*RST')
        # Wait 4 seconds for the device to cycle the command
        time.sleep(4)
        return (self.error == False)





if __name__ == '__main__':
    pass
    
    
