#!/usr/bin/env python
"""
Represents a physical socket or plug
"""

from common.base import *


class Connector(AppBase):
    """Represents a physical socket or plug"""
    
    entity_name = 'connector'
    entity_atts = ['accessor', 'device_label', 'lab_label', 'visual_identifier', 'type', 'gender', 'direction', 'stackable']


    # Class Constructors -----------------------------


    @classmethod
    def from_xml(cls, xml_string):
        """
        Constructor which initalizes a connector instance from xml
        """
        # Convert XML to object
        xml = xml_as_obj(xml_string)
        
        accessor          = xml.accessor.PCDATA
        visual_identifier = xml.visual_identifier.PCDATA.lower()
        device_label      = xml.device_label.PCDATA
        lab_label         = xml.lab_label.PCDATA
        
        type       = xml.type.PCDATA
        gender     = xml.gender.PCDATA
        direction  = xml.direction.PCDATA
        stackable  = xml.stackable.PCDATA

        # Initialize self and return self
        return cls( type, gender, 
                    direction = direction, 
                    stackable = stackable,
                    visual_identifier = visual_identifier, 
                    device_label = device_label, 
                    lab_label = lab_label, 
                    accessor = accessor)


    def __init__(self, type, gender, **keyw):

        # Prepare Parent
        super(Connector, self).__init__()
      
        # Validate gender
        gender = gender.upper()        
        if gender == 'M' or gender == 'MALE':
            self._gender = 'M'
        elif gender == 'F' or gender == 'FEMALE':
            self._gender = 'F'
        else:
            raise ValueError('Invalid connector gender: %s' % gender)

        # Validate direction
        direction = keyw.get('direction', 'N').upper()
        if direction == 'I' or direction == 'INPUT':
            self._direction = 'I'
        elif direction == 'O' or direction == 'OUTPUT':
            self._direction = 'O'
        elif direction == 'N' or direction == 'NEUTRAL':
            self._direction = 'N'
        else:
            raise ValueError('Invalid connector direction: %s' % direction)

        # Validate stackable
        stackable = keyw.get('stackable', False)
        if stackable == 'True':
            stackable = True
        elif stackable == 'False':
            stackable = False
        if stackable != True and stackable != False:
            raise ValueError('Stackable must be True or False. %s is invalid.' % stackable)
        else:
            self._stackable = stackable

        self._type              = type
        self._visual_identifier = keyw.get('visual_identifier', None)
        self._device_label      = keyw.get('device_label', None)
        self._lab_label         = keyw.get('lab_label', None)
        self._accessor          = keyw.get('accessor', None)

        # Determin the value used when referencing this connectors label property
        # If an accessor wasn't provided, create one that is derived from the label
        if self._lab_label != None:
            self._label = self._lab_label
            if self._accessor == None:
                self._accessor = methodize_label(self._label)
        elif self._device_label != None:
            self._label = self._device_label
            if self._accessor == None:
                self._accessor = methodize_label(self._label)
        else:
            self._label = '%s %s' % (self.gender, self.type)

        self._owner  = None
        self._to     = None
        

    def __str__(self):
        """Returns a string containing the size, gender, and type of the connector (6mm male SMA)"""
        return '%s %s' % (self.gender, self._type)

    @rw_property
    def owner(self):
        """
        Returns a reference to the connector or asset that this connection belongs to
        """
        def fget(self):
            return self._owner
        def fset(self, instance):
            self._owner = instance
        def fdel(self):
            self._owner = None

    @property
    def label(self):
        """
        Returns the first of the following values that exists:
            1) The lab label
            2) The device label
            3) The gender + type        
        """
        return self._label
        
    @property
    def visual_identifier(self):
        """
        Returns a description of how to identify this connector within it's surroundings.
        """
        if self._visual_identifier != None:
            return self._visual_identifier
        elif self.owner != None:
            return '%s on %s' % (self.label, self.owner.label)
        else:
            return None

    @property
    def device_label(self):
        """
        Returns the vissible label which the manufactur applied
        """
        return self._device_label

    @property
    def lab_label(self):
        """
        Returns the label which applied by the lab staff to identify this connector.
        """
        return self._lab_label

    @property
    def accessor(self):
        """
        Returns a string containing the value used by the connector's owner to access this connector.
        """
        return self._accessor

    @property
    def type(self):
        """Returns the type of the conneciton (SMA for example)"""
        return self._type

    @property
    def gender(self):
        """Returns the gender of the conneciton (Male or Female)"""
        return 'Male' if (self._gender == 'M') else 'Female'

    @property
    def direction(self):
        """Returns the direction of the conneciton (Input, Output, or Neutral)"""
        if self._direction == 'I':
            return 'Input'
        elif self._direction == 'O':
            return 'Output'
        else:
            return 'Neutral'

    @property
    def stackable(self):
        """Returns True or False, depending on whether the connection is stackable (allows daisy chaining) or not."""
        return self._stackable

    @property
    def connected(self):
        """Returns True or false depending on if the connector is attached to something"""
        return (self._to != None)

    @rw_property
    def to(self):
        """
        Recieves and connects a connector instance or returns the current connection
        """
        def fget(self):
            return self._to
        def fset(self, cnn):
            self.connect_to(cnn)
        def fdel(self):
            raise AttributeError('A connector cannot be deleted')

    def connect_to(self, cnn):
        """Recieves another connector instance and if the mating can occur, associates the provided instance as it's connection"""
        errors = []

        if cnn.type != self._type:
            errors.append('Type mismatch \'%s\' is not \'%s\'.' % (cnn.type, self.type))

        if cnn.gender == self.gender:
            errors.append('Genders are identical:  \'%s\' cannot connect to \'%s\'.' % (cnn.gender, self.gender))

        # Testing direction, requires we travel across cables
        if cnn.direction == 'Neutral':
            if cnn.owner != None:
                test_socket = cnn.owner.connected_to_from(cnn)
            else:
                test_socket = None
        else:
            test_socket = cnn

        if test_socket != None and test_socket.direction == self.direction:
            errors.append('Directions are incompatible:  \'%s\' cannot connect to \'%s\'.' % (cnn.direction, self.direction))

        if errors:
            err_msg = 'Cannot connect '            
            if self._owner == None:
                err_msg += self.label
            else:
                err_msg += '%s on %s' % (self.label, self.owner.label)                
            if cnn.owner == None:
                err_msg += cnn.label
            else:
                err_msg += '%s on %s' % (cnn.label, cnn.owner.label)
            err_msg += ': ' + ' '.join(errors)
            raise ValueError(err_msg)
        else:
            self._to = cnn
            # Ensure bi-direction coupling
            if cnn.to != self:
                cnn.to = self



if __name__ == '__main__':
    pass