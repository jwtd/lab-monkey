#!/usr/bin/env python

"""
Register
"""

from common.hierarchy import *
from product.bit_address import *

class Register(Node):
    """
    Register represents a collection of bit address whose binary sequence conveys a value.
    """

    entity_name = 'register'
    entity_atts = ['label','direction','enable_index','start_index','width','default', 'bits']

    def __init__(self, label, direction, enable_index, start_index, width, default_value):
        """Creates a Register object."""
                
        # Set non-validated properties
        self.label      = label.upper()
        self._direction = direction.upper()

        # Prepare Parent
        super(Register, self).__init__(label = self.label, allows_children = False)

        # Validate direction
        if self._direction != 'I' and self._direction != 'O':
            raise ValueError("'%s' is not a valid Register direction. The value must be either 'I' for Input or 'O' for output." % self._direction)

        # Validate default and prepare bit addresses width
        width = int(width)
        if width <= 0:
            raise ValueError("Register width specified (%s) must be greater than zero." % width)
        if default_value == None:
            raise ValueError("Value assigned to %s cannot be None." % self.label)
        if len(default_value) != width:
            if len(default_value) > width:
                raise ValueError("Value '%s' of length (%s) assigned to %s cannot exceed the registers width (%s)." % (default_value, len(default_value), self.label, width))
            if len(default_value) < width:
                raise ValueError("Value '%s' of length (%s) assigned to %s cannot be shorter than registers width (%s)." % (default_value, len(default_value), self.label, width))
        
        # The FPGA shifts bits from the front of the SCR instead of popping them from the end.
        # As such, the FPGA effectively becomes an array with a right sided zero base index. 
        # This requiers all binary sequences to be mirrored prior to storage.         
        # Example:  Integer value 1, whose binary sequence would normaly be 001, needs to 
        # be stored as 100. The indexes remain the same.
        
        self._default_value = default_value[::-1]

        # Add a child node for each bit addresses
        bs = ''
        for i in range(width):
            bit_label = '%s_%s' % (self.label, i)
            bs += self._default_value[i]
            ba = BitAddress(bit_label, self._default_value[i])
            self._children.append(ba)
            
        # Validate start_index
        start_index  = int(start_index)
        if start_index < 0:
            raise ValueError("Register start index specified (%s) must be greater than zero." % start_index)
        self._start_index = start_index
        
        # Validate enable_index
        if direction == 'I':
            enable_index = int(enable_index)
            if enable_index < 0:
                raise ValueError("Register enable bit index specified (%s) must be greater than zero." % enable_index)
            if enable_index == start_index:
                raise ValueError("Register enable bit index and Register start index cannot be the same value (%s)." % enable_index)
            self._enable_index = enable_index
            self.enable_bit  = None
        else:
            self._enable_index = None
            self.enable_bit  = None

 
    # Overide Node Property -----------------------------
    
    
    def __str__(self):
        return '(%s) %s = %s' % (self.direction, self.label, self.default)


    # Unique --------------------------------------------


    def reg_value_as_bin(self, value):
        """Takes a user value and converts it to this registers binary value and returns it."""
        # Lookup constants
        if value in self.root.package.register_value_aliases:
            value = self.root.package.register_value_aliases[value]
            
        # Transform the value to an integer
        integer_value = data_to_int(value)
        # Transform the integer to a binary sequence
        binary_value = int_to_bin(integer_value, self.width)       
        #self._validate_value(binary_value)
        return binary_value[::-1]
 
    def inverted_bit_array_to_int(self, bit_array):
        """
        The FPGA shifts bits from the front of the SCR instead of popping them from the end.
        As such, the FPGA effectively becomes an array with a right sided zero base index. 
        This requiers all binary sequences to be mirrored prior to storage and reversed upon retrieval.        
        Example:  Integer value 1, whose binary sequence would normaly be 001, needs to 
        be stored as 100. When reading, the 100 needs to be inverted to 001 to cast as an integer.
        """
        normalized_binary = ''.join(bit_array)[::-1]
        return bin_to_int(normalized_binary)

    def is_value_valid(self, test_value):
        """Checks to determine if the value is longer than the width of the register."""
        # TODO: Add constant lookups here
        if test_value == None:
            return False
        if len(test_value) != self.width:
            return False
        for c in test_value:
            if c != '0' and c != '1':
                return False
        return True

    def _validate_value(self, test_value):
        """Checks to determine if the value is not None, is of the correct width, and is binary."""
        if test_value == None:
            raise ValueError("Value assigned to %s cannot be None." % self.label)
        if len(test_value) != self.width:
            if len(test_value) > self.width:
                raise ValueError("Value '%s' of length (%s) assigned to %s cannot exceed the registers width (%s)." % (test_value, len(test_value), self.label, self.width))
            if len(test_value) < self.width:
                raise ValueError("Value '%s' of length (%s) assigned to %s cannot be shorter than registers width (%s)." % (test_value, len(test_value), self.label, self.width))
        for c in test_value:
            if c != '0' and c != '1':
                raise ValueError("Value '%s' assigned to %s must be binary." % (test_value, self.label))


    # Activation Management --------------------------------------------
    

    @property
    def start_index(self):
        """What index this registers value begins at within it's parent block."""
        return self._start_index

    @property
    def enable_index(self):
        """What index this registers enable bit exists at within it's parent block."""
        return self._enable_index

    @property
    def direction(self):
        """Whether the register is for INPUT (I) or OUTPUT (O)."""
        return self._direction

    @rw_property
    def enabled(self):
        """
        Enabled returns or recieves True or False and represents the enabled state of this register. 
        Note that output registers always return True, and ignore any assignements.
        """
        def fget(self):
            if self.enable_bit != None:
                return ('%s' % self.enable_bit.value == '1')
            else:
                return True
        def fset(self, bool):
            if bool != True and bool != False:
                raise ValueError("enabled can only recieve True or False as a value, '%s' is invalid." % bool)
            if self.enable_bit != None:                
                value = '1' if bool else '0'
                self.enable_bit.value = value
        def fdel(self):
            raise AttributeError('enabled can not be deleted')
        
    def enable(self):
        """Sets enable state of the register to True, by setting the enbale bit to 1."""
        if self.enable_bit != None:
            self.enable_bit.value = '1'
        
    def disable(self):
        """Sets enable state of the register to False, by setting the enbale bit to 0."""
        if self.enable_bit != None:
            self.enable_bit.value = '0'


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
        If connected, value returns the most recently sent value, or the 
        default value if not connected. Assigning a value is equivalent 
        to .set(value) and will cause an immediate update in the device.
        """
        def fget(self):
            if self.connected: # and self.is_sent:
                # TODO: Test that this conversion doesn't break anything
                return self.get()
            else:
                return self.default
        def fset(self, value):
            self.set(value)
        def fdel(self):
            self.clear()
    
    @property
    def bits(self):
        """Returns the elements binary default."""
        return self._default_value

    @property
    def default(self):
        """Returns an integer value derived from the elements binary default."""
        return self.inverted_bit_array_to_int(self._default_value)

    @property
    def sent(self):
        """Returns the last value that was sent for this element."""
        if self.connected:
            s,e = self.global_extents
            if None not in self.root.session.sent[s:e]:
                return self.inverted_bit_array_to_int(self.root.session.sent[s:e])
            else:
                return None
        else:
            return None

    @property
    def retrieved(self):
        """Returns most recently retrieved value for this element."""
        if self.connected:
            s,e = self.global_extents
            return self.inverted_bit_array_to_int(self.root.session.retrieved[s:e])
        else:
            return None
        
    @rw_property
    def prepared(self):
        """Returns the value which has been prepared for transmission."""
        def fget(self):
            if self.connected:
                if self.is_prepared:
                    s,e = self.global_extents
                    return self.inverted_bit_array_to_int(self.root.session.prepared[s:e])
                else:
                    return None
        def fset(self, value):
            self.prepare(value)
        def fdel(self):
            self.clear()


    # State property interrogation helpers --------------------------------------------


    @property
    def is_sent(self):
        """Returns True if the value has been sent, False if not."""
        if self.connected:
            s,e = self.global_extents
            return (None not in self.root.session.sent[s:e])
        else:
            return False

    @property
    def is_prepared(self):
        """Returns True if a value has been prepared for sending, False if not."""
        if self.connected and self.direction == 'I':
            s,e = self.global_extents
            return (None not in self.root.session.prepared[s:e])
        else:
            return False

    @property
    def is_retrieved(self):
        """Returns True if the value has been retrieved, False if not."""
        if self.connected:
            s,e = self.global_extents
            return (None not in self.root.session.retrieved[s:e])
        else:
            return False

       
    # Input Management --------------------------------------------


    def reset(self):
        """
        Immediately returns this register's value to it's default in the device .
            PC -> Gate -> DUT (DEFAULT)
        """
        if self.connected:
            self.root.connection.set(self.root.label, self.global_index, self.bits)

    def prepare(self, value):
        """
        Prepares to set this elements value.
            PC -> Gate Input
        """
        if self.connected:
            binary_value = self.reg_value_as_bin(value)
            # Auto-enable if necesary
            if not self.enabled and self.root.autoenable:
                global_index = self.global_index - 1
                binary_value = '1%s' % binary_value
            else:
                global_index = self.global_index
            self.root.connection.prepare(self.root.label, global_index, binary_value)

    def check(self):
        """
        Retrieves this registers value from the gate's input buffer.
            PC <- Gate Input
        """
        if self.connected:
            if self.is_prepared:
                s,e = self.global_extents
                self.root.connection.check(self.root.label, self.global_extents)
                return self.inverted_bit_array_to_int(self.root.session.prepared[s:e])
            else:
                return self.value
        else:
            return None

    def clear(self):
        """
        Throws out the prepared value.
            PC x  Gate   DUT
        """
        if self.connected:
            self.root.connection.clear(self.root.label, self.global_extents)

    def commit(self):
        """
        Commits this element's prepared value. 
            Gate Input -> DUT

        NOTE - On a single register, a call to commit() is equivalent to set(prepared_value).
        """
        if self.connected:
            self.root.connection.commit(self.root.label, self.global_extents)

    def set(self, value):
        """
        Immediately sets this elements value from the device.
            PC -> Gate -> DUT
        """
        if self.connected:
            binary_value = self.reg_value_as_bin(value)
            # Auto-enable if necesary
            if not self.enabled and self.root.autoenable:
                global_index = self.global_index - 1
                binary_value = '1%s' % binary_value
            else:
                global_index = self.global_index
            self.root.connection.set(self.root.label, global_index, binary_value)
            
    def toggle(self):
        """
        Immediately turns the value from all ones to all zeros.
            register.set(0)
            register.set(1)
            register.set(0)
        """
        if self.connected:
            self.set(0)
            self.set(1)
            self.set(0)
        else:
            return None

    # Output Management --------------------------------------------


    def refresh(self):
        """
        Updates the gate's output buffer with fresh data from the device.
            PC   Gate <- DUT
        """
        if self.connected:
            self.root.connection.refresh(self.root.label)

    def inspect(self):
        """
        Retrieves this registers value from the gate's output buffer.
            PC <- Gate Out
        """
        if self.connected:
            self.root.connection.inspect(self.root.label, self.global_extents)
            if self.is_retrieved:
                s,e = self.global_extents
                return self.inverted_bit_array_to_int(self.root.session.retrieved[s:e])
            else:
                return None
        else:
            return None

    def get(self):
        """
        Immediately gets this elements value from the device.
            PC <- Gate <- DUT
        """
        if self.connected:
            s,e = self.global_extents
            self.root.connection.get(self.root.label, self.global_extents)
            v = self.inverted_bit_array_to_int(self.root.session.retrieved[s:e])
            return v
        else:
            return None
        
        
if __name__ == '__main__':
    pass

    