#!/usr/bin/env python

"""
StatelessBitAddress
"""

from common.hierarchy import *

class BitAddress(Node):
    """Represents a single binary value"""

    entity_name = 'bit_address'
    entity_atts = ['label', 'default']

    def __init__(self, label, default_value = 0):
        """Creates a Bit Address"""
        
        # Prepare Parent
        super(BitAddress, self).__init__(label = label.upper(), allows_children = False)
                
        self._validate_value(default_value)
        self._default_value = '%s' % default_value               
        
        
    # Overide Node Property -----------------------------
    
    
    def __str__(self):
        return '(E) %s = %s' % (self.label, self.default)


    # Unique --------------------------------------------


    def is_value_valid(self, test_value):
        """Checks to determine if the value is a 1 or a 0"""
        if test_value == None:
            return False
        test_value = '%s' % test_value
        if test_value != '0' and test_value != '1':
            return False
        return True

    def _validate_value(self, test_value):
        """Checks to determine if the value is is a 1 or a 0"""
        if test_value == None:
            raise ValueError("Value assigned to %s cannot be None." % self.label)
        test_value = '%s' % test_value
        if test_value != '0' and test_value != '1':
            raise ValueError("Value \'%s\' assigned to %s must be a 1 or a 0." % (test_value, self.label))


    # State property accessors --------------------------------------------


    @property
    def connected(self):
        """Whether or not this bit address is associated with a SCR session."""
        if self.parent == None or not self.root.connected:
            return False
        else:
            return True

    @rw_property
    def value(self):
        """
        If connected, value returns the most recently sent value, or the default value if not connected.
        Assigning a value is equivalent to .set(value) and will cause an immediate update in the device
        """
        def fget(self):            
            if self.connected and self.is_sent:
                return self.root.session.sent[self.global_index]
            else:
                return self.default
        def fset(self, value):
            if self.connected and self.value != value:
                self.set(value)
        def fdel(self):
            self._prepared = None

    @property
    def bits(self):
        """Returns the elements binary default"""
        return self._default_value

    @property
    def default(self):
        """Returns the elements default"""
        return int(self._default_value, 2)

    @property
    def sent(self):
        """Returns the last value that was sent for this element"""
        print self.connected
        if self.connected:
            return int(self.root.session.sent[self.global_index])
        else:
            return None

    @property
    def retrieved(self):
        """Returns most recently retrieved value for this element"""
        if self.connected:
            return int(self.root.session.retrieved[self.global_index])
        else:
            return None

    @rw_property
    def prepared(self):
        """Returns the value which has been prepared for transmission"""
        def fget(self):
            if self.connected:
                if self.is_prepared:
                    return int(self.root.session.prepared[self.global_index])
                else:
                    return int(self.root.session.sent[self.global_index])
        def fset(self, value):
            self.prepare(value)
        def fdel(self):
            self._prepared = None


    # State property interrogation helpers --------------------------------------------


    @property
    def is_sent(self):
        """Returns True if the value has been sent, False if not"""
        if self.connected:
            return (self.root.session.sent[self.global_index] != None)
        else:
            return False

    @property
    def is_prepared(self):
        """Returns True if a value has been prepared for sending, False if not"""
        if self.connected:
            return (self.root.session.prepared[self.global_index] != None)
        else:
            return False

    @property
    def is_retrieved(self):
        """Returns True if the value has been retrieved, False if not"""
        if self.connected:
            return (self.root.session.retrieved[self.global_index] != None)
        else:
            return False


    # Delayed Input Management --------------------------------------------
 
 
    def prepare(self, value):
        """
        Prepares to set this elements value
            PC -> Gate   DUT
        """
        if self.connected:
            self._validate_value(value)
            self.root.connection.prepare(self.root.label, self.global_index, value)

    def set(self, value):
        """
        Immediately sets this elements value from the device
            PC -> Gate -> DUT
        """
        if self.connected:
            self._validate_value(value)
            self.root.connection.set(self.root.label, self.global_index, value)


if __name__ == '__main__':
    pass

    