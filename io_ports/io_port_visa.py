#!/usr/bin/env python
"""
Represents a VISA connection to a device
"""

import visa

from common.base import *

VISA_SUPPORTED_PROTOCOLS = ['GPIB', 'GPIB-VXI', 'RSIB', 'COM', 'LPT', 'ASRL', 'TCPIP', 'USB', 'VXI']
VISA_FALSE_POSITIVE_ADDRESSES = ['COM1', 'COM2', 'LPT1']

# Agilent Power Supplies report themselves as HPs
VISA_ID_TRANSLATIONS = {
    'HEWLETT-PACKARD E3631A':['Agilent Technologies','E3631A'],
    'KEITHLEY INSTRUMENTS INC. MODEL 2400':['Keithley Instruments','2400'],
    'BERTScope 12500':['BERTScope','12500A'],
    'BERTScope 7500':['BERTScope','7500A']
    }

def gpib_bool(bool):
    """Helper method to convert various user supplied boolean values to the GPIB boolean equivalent (1 or 0)"""
    bool = ('%s' % bool).lower()
    if bool in ['true', '1', 'on']:
        return '1'
    elif bool in ['false', '0', 'off']:
        return '0'
    else:
        raise ValueError('Invalid bool flag: %s' % bool)

class VisaSocket(AppBase):
    """
    Represents a connection to a VISA accessible device (includes GPIB)
    http://pyvisa.sourceforge.net/pyvisa/node6.html
    """

    def __init__(self, address, **keyw):
        """
        Constructor method
        Parameters:
            address -- the instrument's resource name or an alias, may be taken from the list from get_instruments_list().
        Keyword arguments:
            timeout -- the VISA timeout for each low-level operation in milliseconds.
            term_chars -- the termination characters for this device, see description of class property "term_chars".
            chunk_size -- size of data packets in bytes that are read from the device.
            lock -- whether you want to have exclusive access to the device. Default: VI_NO_LOCK
            delay -- waiting time in seconds after each write command. Default: 0
            send_end -- whether to assert end line after each write command. Default: True
            values_format -- floating point data value format.  Default: ascii (0)

        """
        # Prepare Parent
        super(VisaSocket, self).__init__()

        # Initialize VISA Instrument
        self._port = visa.Instrument(address) # keyw
        self._address = address

    def _build_visa_cnn_string(self, primary_address, protocol, board, secondary_address = ''):
        """
        Builds the VISA resource name based on the address, protocol, and board
        
        GPIB
            GPIB[board]::primary_address[::secondary_address]::INSTR
        
        GPIB-VXI
            GPIB-VXI[chassis]::VXI_logical_address::INSTR
        
        RSIB
            RSIB::remote_host::INSTR (provided by NI VISA only)
        
        Serial (Applies to COM and LPT ports)
            ASRL[port_number]::INSTR
        
        TCPIP
            TCPIP[board]::remote_host[::lan_device_name]::INSTR
        
        USB
            USB[board]::manid::model_code::serial_No[::interface_No]::INSTR
        
        VXI
            VXI[chassis]::VXI_logical_address::INSTR
        """
        protocol = protocol.upper()
        if protocol == 'GPIB':
            return '%s%s::%s' % (protocol, board, primary_address)
        elif protocol in VISA_SUPPORTED_PROTOCOLS:
            raise NotImplemented('%s has not been implemented.' % protocol)
        else:
            raise ValueError('Unrecognized VISA protocol requested: %s' % protocol)


    # Environment Interrogators -----------------------------------


    @staticmethod
    def get_instruments_list(use_aliases = True):
        """
        Returns a list with all instruments that are known to the local VISA system. 
        If you're lucky, these are all instruments connected with the computer.

        The boolean use_aliases is True by default, which means that the more human-friendly 
        aliases like ``COM1'' instead of ``ASRL1'' are returned. With some VISA systems1 you 
        can define your own aliases for each device, e.g. ``keithley617'' for ``GPIB0::15::INSTR''.
        If use_aliases is False, only standard resource names are returned. 
        """
        # Get addresses and filter out the false positives
        addresses = visa.get_instruments_list()
        for p in VISA_FALSE_POSITIVE_ADDRESSES: 
            del addresses[addresses.index(p)]
        return addresses

    @staticmethod
    def identify_attached_visa_devices(allow_false_positive_addresses = False):
        """
        Returns a dictionary of detected VISA addressess (returned from visa.get_instruments_list())
        and the parsed results from a '*IDN?' call to the address.
        """
        # Get addresses and filter out the false positives
        addresses = visa.get_instruments_list()
        if not allow_false_positive_addresses:
            for p in VISA_FALSE_POSITIVE_ADDRESSES: 
                del addresses[addresses.index(p)]

        # Loop over each address
        equipment = {}
        for address in addresses:
            
            # Initialize the instrument and request it's identity
            i = visa.instrument(address)
            id_response  = i.ask('*IDN?')
            
            # Parse any responses
            id = VisaSocket.parse_device_identity(id_response)

            # Store the instrument's ID components
            equipment[address] = id

        # Return a list of all the equipment
        return equipment

    @staticmethod
    def parse_device_identity(id_string):
        """Given"""
        manufacturer = 'Unknown'
        model        = ''
        part_code    = '0'
        additional   = []
        if id_string != '':
            metadata = str(id_string).split(',')
            i = len(metadata)
            manufacturer = metadata[0].strip()
            model        = metadata[1].strip() if i > 1 else ''
            part_code    = metadata[2].strip() if i > 2 else '0'
            additional   = metadata[3:-1] if i > 3 else []
            
            # Translate ID's of false devices
            device_name = ('%s %s' % (manufacturer, model)).strip()
            if device_name in VISA_ID_TRANSLATIONS.keys():
                manufacturer = VISA_ID_TRANSLATIONS[device_name][0]
                model        = VISA_ID_TRANSLATIONS[device_name][1]

        return {'manufacturer':manufacturer, 'model':model, 'part_code':part_code, 'metadata':additional}

    # Connection Management -----------------------------------


    @staticmethod
    def detect():
        """Interogates the PC to determine if a parallel port can be established"""
        try:
            # Get addresses and filter out the false positives
            addresses = visa.get_instruments_list()
            for p in VISA_FALSE_POSITIVE_ADDRESSES:
                if p in addresses:
                    del addresses[addresses.index(p)]
            if addresses != [''] and len(addresses):
                return True
            else:
                return False
        except:
            return False


    # Connection Properties -----------------------------------


    @property
    def address(self):
        """
        Returns the network address this socket is connected to
        """
        return self._address


    # I/O Commands -----------------------------------


    def write(self, command):
        """
        Write a string message to the device.
        Parameters:
        message -- the string message to be sent.  The term_chars are appended
            to it, unless they are already.
        """
        return self._port.write(command)

    def read(self, query):
        """
        Read a string from the device.

        Reading stops when the device stops sending (e.g. by setting
        appropriate bus lines), or the termination characters sequence was
        detected.  Attention: Only the last character of the termination
        characters is really used to stop reading, however, the whole sequence
        is compared to the ending of the read string message.  If they don't
        match, a warning is issued.

        All line-ending characters are stripped from the end of the string.

        Parameters: None

        Return value:
        The string read from the device.
        """
        return self._port.read(query) 
  
    def read_raw(self):
        """
        Read the unmodified string sent from the instrument to the computer.
        In contrast to read(), no termination characters are checked or
        stripped.  You get the pristine message.
        """
        return self._port.read_raw()
    
    def read_values(self, format=None):
        """
        Read a list of floating point values from the device.

        Parameters:
        format -- (optional) the format of the values.  If given, it overrides
            the class attribute "values_format".  Possible values are bitwise
            disjunctions of the above constants ascii, single, double, and
            big_endian.  Default is ascii.

        Return value:
        The list with the read values.
        """
        return self._port.read_values(format)

    def read_floats(self):
        """This method is deprecated.  Use read_values() instead."""
        return self._port.read_floats()
    
    def ask(self, query):
        """A combination of write(message) and read()"""
        return self._port.ask(query)
    
    def ask_for_values(self, query, format=None):
        """A combination of write(message) and read_values()"""
        return self._port.ask_for_values(query, format)
    
    def clear(self):
        """Resets the device.  This operation is highly bus-dependent."""
        return self._port.clear()    
        
    def trigger(self):
        """Sends a software trigger to the device."""
        return self._port.trigger()


if __name__ == '__main__':
    #VisaSocket.identify_attached_visa_devices()
    #print VisaSocket.detect()
    pass