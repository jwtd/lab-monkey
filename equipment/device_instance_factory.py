#!/usr/bin/env python

"""
DeviceInstanceFactory
"""

from common.base import *

# Generics
from equipment.multimeter import Multimeter
from equipment.power_supply import PowerSupply
from equipment.bertscope import BERTScope

# Specifics
from equipment.thermal_stream import ThermalStream
from equipment.agilent_81134a import Agilent81134A
from equipment.lecroy_sda100g import LeCroySDA100G
from equipment.tektronix_tds8000 import TektronixTDS8000

class DeviceInstanceFactory(object):
    """
    Factory class which returns an instance of the device coresponding to the manufacturer and model.
    """

    entity_name = 'device_instance_factory'
    entity_atts = []

    def __init__(self):
        raise Exception('Factory classes cannot be instantiated')

    @staticmethod
    def request(device_key):
        """Sniffs out connection and returns an instance of the bridge for the protocol in use"""
        # TODO: Move configs to central database instead of from local XML repository
        device_key = device_key.upper()
        if device_key == 'KEITHLEY INSTRUMENTS 2400':
            return Multimeter.from_xml(exepath('definitions/Keithley_KEI2400.xml'))
        
        elif device_key == 'AGILENT TECHNOLOGIES E3648A':
            return PowerSupply.from_xml(exepath('definitions/Agilent_Technologies_E3648A.xml'))
        
        elif device_key == 'AGILENT TECHNOLOGIES E3631A':
            return PowerSupply.from_xml(exepath('definitions/Agilent_Technologies_E3631A.xml'))
        
        elif device_key == 'BERTSCOPE 7500A':
            return BERTScope.from_xml(exepath('definitions/BERTScope_7500A.xml'))
        
        elif device_key == 'BERTSCOPE 12500A':
            return BERTScope.from_xml(exepath('definitions/BERTScope_12500A.xml'))
        
        elif device_key == 'TEMPTRONIC TP04300A':
            return ThermalStream.from_xml(exepath('definitions/Temptronic_TP04300A.xml'))
        
        elif device_key == 'AGILENT TECHNOLOGIES 81134A':
            return Agilent81134A.from_xml(exepath('definitions/Agilent_Technologies_81134A.xml'))
        
        elif device_key == 'LECROY 12500A':
            return LeCroySDA100G.from_xml(exepath('definitions/LeCroy_SDA100G.xml'))

        elif device_key == 'TEKTRONIX TDS8000':
            return TektronixTDS8000.from_xml(exepath('definitions/Tektronix_TDS8000.xml'))

        elif device_key == 'TEKTRONIX CSA8000':
            return TektronixTDS8000.from_xml(exepath('definitions/Tektronix_CSA8000.xml'))

        else:
            raise LookupError('Unrecognized device key: %s' % device_key)


if __name__=='__main__' :
    pass