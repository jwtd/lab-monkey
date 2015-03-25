#!/usr/bin/env python

"""
Register Collection
"""

from common.hierarchy import *
from product.bit_address import *


class RegisterCollection(Node):
    """
    RegisterCollection is a collection of registers that conceptualy associated
        Ex. Common Block or Lane
    """

    entity_name = 'register_collection'
    entity_atts = ['type', 'label', 'registers']

    def __init__(self, registers, type, label = None):
        
        # Validate
        if not registers:
            raise ValueError('Cannot create register collection. No registers were supplied.')
        
        # Metadata
        self.__type = type
        self.label = label if label else type
        
        # Prepare Parent
        super(RegisterCollection, self).__init__(label = label)
        #self.log.info('Creating %s' % type)
        
        # Sort registers by start_index
        sorted_regs = [(getattr(r, 'start_index'), r) for r in registers]
        sorted_regs.sort()
        self.__registers_by_start_index = {}
        for a,r in sorted_regs:
            self.__registers_by_start_index[r.start_index] = r
            if r.direction == 'I':
                # TODO: This is kludgy because we are assuming that the enable_bit comes immediately before the register
                if r.enable_index == r.start_index-1:
                    node_id = '%s_ENABLE' % r.label
                    enable_bit = BitAddress(node_id, '1') # Default is enabled
                    self.add_node(enable_bit)
                    # Cross hierarchy branch association to assist with auto-enable
                    r.enable_bit = enable_bit
                    # Metaprogram reference to children
                    append_reference(self, node_id, enable_bit)
                else:
                    raise ValueError('The enable bit index does not immediately precede the register')
            self.add_node(r)
            # Metaprogram reference to children
            append_reference(self, r.label, r)

        # Build bit address association map
        self.__registers_by_bit_address = {}
        for r in registers:
            i = r.start_index
            while i < r.start_index + r.width:
                self.__registers_by_bit_address[i] = r
                i+=1
            if r.direction == 'I':
                self.__registers_by_bit_address[r.enable_index] = r #.enable_bit_node

        self.bit_count = max(self.__registers_by_bit_address.keys())
        #self.log.info('%s has %s registers using %s bit addresses' % (type, len(self), self.bit_count))
        #self.to_log()
        
    def __len__(self):
        """Returns the number of registers in the collection (NOT the number of bits in the SCR)."""
        return len(self.__registers_by_start_index)

    def __getitem__(self, label_or_index):
        """Returns a reference to the node with the index or label specified."""
        if isinstance(label_or_index, int):
            n = self._children[label_or_index]
        else:
            try:
                i = self.index_of_first_child_with('label', label_or_index.upper())
                if i != None:
                    n = self._children[i]
                else:
                    raise LookupError('Could not find node %s' % label_or_index)
            except ValueError:
                n = self._children[int(label_or_index)]
            except:
                raise LookupError('Could not find node %s' % label_or_index)
        return n

    def has_register(self, label):
        """Returns True or False reflecting whether or not a register with the label provided exists within this collection"""
        return (self.index_of_first_child_with('label', label.upper()) != None)

    def to_log(self):
        """Write the register collection's bit address maps to the logger"""
        # Write out enable and start positions
        self.log.debug('----------------------------- Inspect Register Start Locations')
        for bit_address, register in enumerate(self):
            self.log.debug('%s = %s' %(bit_address, register.label))
        # Write out every bit address to register association in the collection
        self.log.debug('----------------------------- Inspect Bit Ownership') 
        for bit_address in self.__registers_by_bit_address.keys():
            self.log.debug('%s = %s' %(bit_address, self.__registers_by_bit_address[bit_address].label))

    @property
    def type(self):
        """Returns the type designation assigned at creation."""
        return self.__type

    @property
    def registers(self):
        """A reference the all of the registers in this collection."""
        def only_regs(n):
            if n.entity_name == 'register': return n
        return filter(only_regs, self.children)

    def register(self, key):
        """Returns the register identified by the key provided."""
        return self[key]

    def register_at_bit_address(self, bit_address):
        """Returns the label of the register at the offset provided."""
        return self.__registers_by_bit_address[bit_address]
        
    def translate_register_string(self, scr_string):
        """
        Takes a SCR string and if it conforms to this block's model, returns
        a human readable translation of the registers and there values.
        """
        scr_string = list(scr_string)
        if len(scr_string) != self.width:
            raise ValueError('The block string provided has %s bit addresses, and this block model has %s bit addresses.' % (len(scr_string), self.width))

        result = []
        for register in self:
            reg_state = {}
            reg_state['register'] = register
            reg_state['value']    = register.inverted_bit_array_to_int(scr_string[register.start_index : register.start_index + register.width])
            reg_state['enabled']  = False if register.direction == 'I' and scr_string[register.enable_index] == '0' else True
            reg_state['modified'] = True if reg_state['value'] != register.default else False
            result.append(reg_state)
            #print '%s : %s = %s' % (register.start_index, register.start_index+register.width, scr_string[register.start_index : register.start_index+register.width])

        return result



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
    def is_retrieved(self):
        """Returns True if the value has been retrieved, False if not."""
        if self.connected:
            s,e = self.global_extents
            return (None not in self.root.session.retrieved[s:e])
        else:
            return False
        
        
    # State property accessors --------------------------------------------
 

    @property
    def connected(self):
        """Whether or not this bit address is associated with a SCR session."""
        if self.parent == None or not self.root.connected:
            return False
        else:
            return True

    @property
    def value(self):
        """
        If connected, value returns the most recently sent value, or the default value if not connected.
        """
        if self.connected:
            return self.sent
        else:
            return self.default

    @property
    def default(self):
        """
        Returns the unifed default values for all elements in the register collections.
        """
        return ''.join([child.bits for child in self._children])

    @property
    def sent(self):
        """
        In a stateful register collection, value returns the unifed values 
        last sent for each element in the collection.
        """
        if self.connected and self.is_sent:
            s,e = self.global_extents
            return ''.join(self.root.session.sent[s:e])
        else:
            return None

    @property
    def retrieved(self):
        """
        Returns the unifed value most recently retrieved for all elements 
        in this register collection.
        """
        if self.connected and self.is_retrieved:
            s,e = self.global_extents
            return ''.join(self.root.session.retrieved[s:e])
        else:
            return None
        
    @property
    def prepared(self):
        """Returns the unifed value which has been prepared for transmission."""
        if self.connected:
            s,e = self.global_extents
            send = []
            for bit in self.root.session.prepared[s:e]:
                if bit != None:
                    send.append(bit)
                else:
                    send.append('x')
            return ''.join(send)

    @property
    def pending(self):
        """Returns a list of elements which have prepared values waiting to be sent."""
        if self.connected:
            pending = []
            for register in self:
                if register.is_prepared:
                    pending.append('%s : %s => %s' % (register.path, register.value, register.prepared))
            return pending
        else:
            return None
        
        
    # Input Management --------------------------------------------


    def reset(self):
        """
        Immediately returns all registers in this collection to their default values in the device.
            PC -> Gate -> DUT (DEFAULT)
        """
        if self.connected:
            self.root.connection.set(self.root.label, self.global_index, self.default)

    def prepare(self, key, value):
        """
        Prepares to set the element identified by key within this collection to the value provided.
            PC -> Gate   DUT
        """
        if self.connected:
            self[key].prepare(value)

    def check(self, key):
        """
        Retrieves the identified register's value from the gate's input buffer.
            PC <- Gate Input
        """
        if self.connected:
            return self[key].check()
        else:
            return None

    def clear(self):
        """
        Throws out the prepared value
            X -> Gate Input <- X
        """
        if self.connected:
            self.root.connection.clear(self.root.label, self.global_extents)

    def commit(self):
        """
        Commits the prepared values of all element's within this register collection. 
            PC    Gate -> DUT
        """
        if self.connected:
            self.root.connection.commit(self.root.label, self.global_extents)

    def set(self, key, value):
        """
        Immediately sets element identified by key within this collection to the value provided at the device.
            PC -> Gate -> DUT
        """
        if self.connected:
            self[key].set(value)


    # Output Management --------------------------------------------


    def refresh(self):
        """
        Updates the gate's output buffer with fresh data from the device.
            PC   Gate <- DUT
        """
        if self.connected:
            self.root.connection.refresh(self.root.label)

    def inspect(self, key):
        """
        Retrieves this registers value from the gate's output buffer.
            PC <- Gate Out
        """
        if self.connected:
            return self[key].inspect()

    def get(self, key):
        """
        Immediately gets this elements value from the device.
            PC <- Gate <- DUT
        """
        if self.connected:
            return self[key].get()
        

    def __iter__(self):
        return RegisterIterator(self, self.__registers_by_start_index)



class RegisterIterator(object):
    
    def __init__(self, target, lookup):
        self.target = target
        self.__lookup = lookup
        self.__lookup_keys = lookup.keys()
        self.__lookup_keys.sort()
        self.count  = -1
        
    def __iter__(self):
        return self
    
    def next(self):
        count = self.count + 1
        self.count = count
        if count >= len(self.__lookup):
            raise StopIteration
        return self.__lookup[self.__lookup_keys[self.count]]


if __name__ == '__main__':
    pass

    
    
        