#!/usr/bin/env python

"""Tests of the DeviceInstanceFactory class"""

from common.tests.pyunit_helpers import *
from unittest import TestCase, main

from equipment.device_instance_factory import DeviceInstanceFactory

class DeviceInstanceFactoryTests(TestCase):
    """Tests of the DeviceInstanceFactory class"""

    def test_request(self):
        """Test requesting all valid devices"""
        
        device_keys = {
            'Keithley Instruments 2400'   : 'Keithley Instruments 2400 Series Digital Source Meter',
            'Agilent Technologies E3648A' : 'Agilent Technologies E3648A Dual Output DC Power Supply',
            'Agilent Technologies E3631A' : 'Agilent Technologies E3631A Triple Output DC Power Supply',
            'BERTScope 7500A'             : 'BERTScope 7500A Bit Error Analyzer',
            'BERTScope 12500A'            : 'BERTScope 12500A Bit Error Analyzer',
            'Temptronic TP04300A'         : 'TEMPTRONIC TP04300A ThermoStream',
            'Agilent Technologies 81134A' : 'Agilent Technologies 81134A 3.35 GHz Pulse/Pattern Generator',
            'Lecroy 12500A'               : 'LeCroy SDA100G Digital Sampling Oscilloscope',
            'Tektronix TDS8000'           : 'Tektronix TDS8000 Digital Sampling Oscilloscope'
            }
        
        for device_key in device_keys:
            d = DeviceInstanceFactory.request(device_key)
            self.assertEqual('%s' % d, device_keys[device_key])

if __name__ == '__main__':
    main()