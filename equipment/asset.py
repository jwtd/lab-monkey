#!/usr/bin/env python
"""
Root class which all assets classes inherit from
"""

from common.base import *

class Asset(AppBase):
    """Root class which all assets classes inherit from"""
    
    entity_name = 'asset'
    entity_atts = ['asset_class', 'manufacturer', 'model', 'part_code']

    def __init__(self, asset_class, manufacturer = None, model = None, type = None, part_code = None):
        # Prepare Parent
        super(Asset, self).__init__()
        
        self._asset_class  = asset_class
        self._manufacturer = manufacturer
        self._model        = model
        self._type         = type
        self._part_code    = part_code


    def __str__(self):
        """
        Returns a string containing the manufacturer model 
        serial_number and firmware of the device
        """
        return '%s %s' % (self.manufacturer, self.model)

 
    # Identity Properties -----------------------------

    
    @property
    def identity(self):
        """
        Returns a string containing the manufacturer, model, part code of the asset
        """
        return ('%s %s %s' % (self.manufacturer, self.model, self.part_code)).strip()

    @property
    def asset_class(self):
        """Returns the asset type"""
        return self._asset_class

    @property
    def manufacturer(self):
        """Returns the manufacturer"""
        return self._manufacturer

    @property
    def model(self):
        """Returns the model"""
        return self._model

    @property
    def type(self):
        """Returns the type of pattern generator this is"""
        return self._type

    @property
    def part_code(self):
        """
        Returns a code which uniquely identifies the asset. The code could be 
        a manufacturer's serial_number (SN) or an in-house asset tracking code.
        """
        return self._part_code


if __name__ == '__main__':
    pass