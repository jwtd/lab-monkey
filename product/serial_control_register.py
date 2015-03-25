#!/usr/bin/env python

"""
SerialControlRegister
"""

from common.hierarchy import *
from common.insensitive_dict import InsensitiveDict
from product.register import *
from product.register_collection import *



class SerialControlRegister(Node):
    """
    Serial Control Registers are made up of exactly one Common Block and some number of Lanes 
    Examples: 01234567C, 0123C4567, C0123, 0C1
    """

    entity_name = 'serial_control_register'
    entity_atts = ['label', 'sequence', 'common_block', 'lanes']

    def __init__(self, label, common_block_registers, lane_registers, block_orientation):
        """
        Creates an Orientation instance
        label : String identifying the orientation within a package (TOP, BOTTOM, Big, Small, Medium, etc)
        common_block_architype : RegisterCollection that represents a common block
        lane_architype : RegisterCollection that represents a lane in the orientation
        """

        # Prepare Parent
        super(SerialControlRegister, self).__init__(label = label)

        # Default connection state
        self._package = None
        self._autoenable = True
        
        # Verify that one and only one common block was specified
        block_orientation = block_orientation.upper()
        if 'X' not in block_orientation:
            raise ValueError("No common block specified in sequence %s" % block_orientation)
        if block_orientation.count('X') > 1:
            raise ValueError("More than one common block was specified in the sequence %s" % block_orientation)
        self._block_orientation = block_orientation

        # Get path through sequence
        self._scr_sequence = self._calculate_scr_block_path(self._block_orientation)
        # Capture the highest lane id for use in validation
        self._max_lane_id = int(max(self._scr_sequence[1:])) # This will need to change if we move the FPGA mirroring
        
        #self.log.debug('scr_sequence: %s' % self._scr_sequence) 
        #self.log.debug('Greatest lane id: %s' % self._max_lane_id)   

        self._lanes = InsensitiveDict()
        for char in self._scr_sequence:
            if char == 'X':
                unique_common_block_registers = self._clone_block(common_block_registers)
                block = RegisterCollection(unique_common_block_registers, 'common_block', 'common_block')
                self._common_block = block
            else:
                unique_lane_registers = self._clone_block(lane_registers)
                lane_id = 'lane_%s' % char
                block = RegisterCollection(unique_lane_registers, 'lane', lane_id)
                self._lanes[int(char)] = block
                # Metaprogram reference to children
                append_reference(self, lane_id, block)
            self.add_node(block)


    def _clone_block(self, registers):
        """Creats a collection of identical registers to ensure unique object references"""
        clone = []
        for r in registers:
            reg_name         = r.label
            reg_direction    = r.direction
            reg_enable_index = r.enable_index
            reg_start_index  = r.start_index
            reg_width        = r.width
            reg_default      = r.bits[::-1] # Flip so we don't invert twice
            new_r = Register(reg_name, reg_direction, reg_enable_index, reg_start_index, reg_width, reg_default)
            clone.append(new_r)
        return clone
        
 
    # Overide Node Property -----------------------------


    def _calculate_scr_block_path(self, block_orientation):
        """ 
        The SCR index starts with the first lane to the left of the common block and
        proceedes to the left end, where it loops back to the first lane to 
        the right of the common block and proceedes to the right until it reaches the end
        and always passes through the common block last. 
        
        The FPGA shifts bits from the front of the SCR instead of popping them from the end.
        As such, the FPGA effectively becomes an array with a right sided zero base index. 
        This requiers the binary sequence to be mirrored prior to insertion.
        """
        left, right = block_orientation.split('X')
        scr_sequence = left[::-1] + right + 'X'
        
        # Mirror so that the FPGA can get things in the right place
        return scr_sequence[::-1]


    def __str__(self):
        return '%s : %s' % (self.label, self.sequence)

    def __getitem__(self, label_or_index):
        """Returns a reference to the block specified"""
        if isinstance(label_or_index, int):
            n = self._children[label_or_index]
        else:
            try:            
                n = self._children[int(label_or_index)]
            except ValueError:
                label_or_index = label_or_index.lower()
                i = self.index_of_first_child_with('label', label_or_index)
                if i != None:
                    n = self._children[i]
                else:
                    raise LookupError('Could not find node %s' % label_or_index)
            except:
                raise LookupError('Could not find node %s' % label_or_index)
        return n

    def bit_address_map(self, highlight_register = None):
        """Writes the serial control registers bit address map to the logger"""

        blocks = list(self._scr_sequence)
        self.log.debug('----------------------------- Registers Address Map')
        for block in blocks:
            if block == 'X':
                for register in self.common_block.registers:
                    self.log.debug('CB.%s.%s = %s' %(register.direction, register.label, register.default))
            else:
                for register in self['lane_%s' % block].registers:
                    self.log.debug('L%s.%s.%s = %s' %(block, register.direction, register.label, register.default))
                    
        self.log.debug('----------------------------- Bit Address Map')
        highlight = []
        highlight_def  = ''
        highlight_bits = ''
        io        = []
        base = 0
        for block in blocks:
            if block == 'X':
                for i in xrange(self.common_block.width):
                    register = self.common_block.register_at_bit_address(i)
                    self.log.debug('%s CB.%s.%s = %s' %(base, register.direction, register.label, register.default))
                    # Build I/O map
                    io.append(register.direction)
                    # Build highlight map
                    if register.label == highlight_register:
                        highlight_def  = register.default
                        highlight_bits = register.bits
                        if hasattr(register, 'enable_bit') and register.enable_bit.global_index == base:
                            highlight.append('E')
                        else:
                            highlight.append('X')
                    else:
                        highlight.append('_')
                    base +=1
            else:
                for i in xrange(self['lane_%s' % block].width):
                    register = self['lane_%s' % block].register_at_bit_address(i)
                    self.log.debug('%s L%s.%s.%s = %s' %(base, block, register.direction, register.label, register.default))
                    
                    # Build I/O map
                    io.append(register.direction)
                    # Build highlight map
                    if register.label == highlight_register:
                        highlight_def  = register.default
                        highlight_bits = register.bits
                        if hasattr(register, 'enable_bit') and register.enable_bit.global_index == base:
                            highlight.append('E')
                        else:
                            highlight.append('X')
                    else:
                        highlight.append('_')
                    base +=1

        self.log.debug('----------------------------- I/O Map')
        self.log.debug('%s' % ''.join(io))
                        
        self.log.debug('----------------------------- Highlight Map')
        self.log.debug('Register: %s = %s\t%s\n%s\n%s' % (highlight_register, highlight_def, highlight_bits, self.default, ''.join(highlight)))


    # Unique --------------------------------------------


    @property
    def autoenabled(self):
        """Whether or not sets and prepares will automaticaly enable the register"""
        return self._autoenable

    @rw_property
    def autoenable(self):
        """
        Whether or not calls to set() and prepare() within this serial control register 
        will automaticaly enable the registers. Default is True.
        """
        def fget(self):
            return self._autoenable
        def fset(self, autoenable):
            if autoenable == True or autoenable == False:
                self._autoenable = autoenable
            else:
                raise ValueError('Autoenable can only accept True or False as a value. %s is invalid' % autoenable)
        def fdel(self):
            self._autoenable = False

    @rw_property
    def package(self):
        """The connection pool"""
        def fget(self):
            return self._package
        def fset(self, package):
            self._package = package
        def fdel(self):
            self._prepared = None

    @property
    def connection(self):
        """The connection in the package"""
        if self.connected:
            return self.package.connection
        else:
            return None

    @property
    def connected(self):
        """Whether or not this bit address is associated with a SCR session."""
        if self.package == None or not self.package.connected:
            return False
        else:
            return True

    @property
    def session(self):
        """
        If connected, returns a reference to this SCRs session in the adapter, 
        or None if not connected
        """
        if self.connected:
            return self.package.connection[self.label]
        else:
            return None

    @property
    def sequence(self):
        """The physical orientation of the blocks in this serial control register."""
        return self._block_orientation

    @property
    def common_block(self):
        """Returns a reference to the common block."""
        return self._common_block

    @property
    def cb(self):
        """Alias for common_block. Also Returns a reference to the common block."""
        return self._common_block

    @property
    def lanes(self):
        """Returns a reference to the lanes collection."""
        return self._lanes

    
    # SCR Delta Comparitors ---------------------------------


    def translate_register_string(self, scr_string):
        """
        Takes a SCR string and if it conforms to this orientation's model, returns
        a human readable translation of the registers and there values
        """
        scr_string = list(scr_string)
        if len(scr_string) != self.width:
            raise ValueError('The scr string provided has %s bit addresses, and this SCR model has %s bit addresses.' % (len(scr_string), self.width))

        result = {}
        i = 0
        for block in self:
            segment = scr_string[i:i+block.width]
            result[block.label] = block.translate_register_string(segment)
            i += block.width
        return result

    def translate_register_string_delta(self, scr_string_a, scr_string_b = None):
        """
        Compares the first SCR string provided to the second SCR string (or to 
        the current SCR value if a second string is not provided), and returns 
        an evaluation of the difference between them.
        """
        import math
        if scr_string_b == None: 
            scr_string_b = self.default

        # TODO: Result structure for delta is kludgy - rework into class???
        result = {}
        result['a_scr'] = scr_string_a
        result['b_scr'] = scr_string_b
        result['deltas']= {}
        
        delta_index_map = []
        scr_string_a = list(scr_string_a)
        scr_string_b = list(scr_string_b)

        # Find indexes of deltas
        delta_indexs = []
        for index, value in enumerate(scr_string_a):
            bv = scr_string_b[index]
            if value != bv: 
                delta_indexs.append(index)
                delta_index_map.append(bv)
            else:
                delta_index_map.append('_')
        result['delta_map'] = ''.join(delta_index_map)

        scr_path_ref = list(self._scr_sequence)
        
        result['delta_indexs'] = delta_indexs
        
        # Determine what block they are in
        lane_width = self.lanes[0].width
        cb_width   = self.common_block.width
        for index in delta_indexs:
            # Query that block for the register that owns the bit address
            if index < cb_width:
                base = 0
                local_index = index
                block_label = self.common_block.label
                register = self.common_block.register_at_bit_address(local_index)
            else:
                local_index = int((index - cb_width) % lane_width)
                path_index = int(math.floor((index - cb_width) / lane_width))
                base = cb_width + (lane_width * path_index)
                lane_id = int(scr_path_ref[1 + path_index])
                block_label = self.lanes[lane_id].label
                register = self.lanes[lane_id].register_at_bit_address(local_index)

            if register.direction == 'I' and local_index == register.enable_index:
                s,e = index, index+1
                reg_key = '%s (ENABLE BIT)' % register.label
            else:
                s,e = base + register.start_index, base + register.start_index + register.width
                reg_key = register.label

            # Prepare Store the result
            if block_label not in result['deltas'].keys():
                result['deltas'][block_label] = {}

            # Only add new registers
            if reg_key in result['deltas'][block_label].keys():
                continue
            
            reg_delta = {}
            reg_delta['delta_index']  = index
            reg_delta['a_value']      = ''.join(scr_string_a[s:e])
            reg_delta['b_value']      = ''.join(scr_string_b[s:e])
            reg_delta['register']     = register

            # Store the result
            if block_label in result['deltas'].keys():
                result['deltas'][block_label][reg_key] = reg_delta
            else:
                result['deltas'][block_label] = {reg_key : reg_delta}

        return result


    # Configuration Delegation to Adapter ---------------------------------


    def set_clock_source(self, source):
        """
        Sets the clock source for this SCR:
        source :    sma      = Take clock source from SMA connector
                    internal = Take clock source from internal clock
                    stop     = No clock source
        """
        if self.connected:
            self.root.connection.set_clock_source(self.label, source)

    # State property interrogation helpers --------------------------------------------


    @property
    def is_sent(self):
        """Returns True if the value has been sent, False if not"""
        if self.connected:
            s,e = self.global_extents
            return (None not in self.root.session.sent[s:e])
        else:
            return False

    @property
    def is_retrieved(self):
        """Returns True if the value has been retrieved, False if not"""
        if self.connected:
            s,e = self.global_extents
            return (None not in self.root.session.retrieved[s:e])
        else:
            return False
        

    # State property accessors --------------------------------------------
    
    
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
        Returns the unifed default values for all elements in the register collections
        """
        return ''.join([child.default for child in self._children])

    @property
    def sent(self):
        """
        Returns the unifed value last sent for all elements in the register collections
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
        in this register collection
        """
        if self.connected and self.is_retrieved:
            s,e = self.global_extents
            return ''.join(self.root.session.retrieved[s:e])
        else:
            return None

    @property
    def prepared(self):
        """Returns the value which has been prepared for transmission"""
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
        """Returns a list of elements which have prepared values waiting to be sent"""
        if self.connected:
            pending = []
            for child in self._children:
                pending.extend(child.pending)
            return pending
        else:
            return None
       
        
    # Input Management --------------------------------------------

    # TODO: Add Preset method with caching
    
    def reset(self):
        """
        Immediately returns all registers in this collection to their default values in the device
        and reads the output back out.
            PC -> Gate -> DUT (DEFAULT)
        """
        if self.connected:
            self.root.connection.set(self.root.label, self.global_index, self.default)

    def prepare(self, key, value):
        """
        Prepares to set the element identified by key in all blocks to the value provided
            PC -> Gate   DUT
        """
        if self.connected:
            for block in self:
                if block.has_register(key):
                    block[key].prepare(value)

    def check(self, key):
        """
        Retrieves the identified register's value from the gate's input buffer
            PC <- Gate Input
        """
        if self.connected:
            results = {}
            for block in self:
                if block.has_register(key):
                    results[block.label] = block.check(key)
            return results
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
        Commits the prepared values of all element's within the SCR 
            PC    Gate -> DUT
        """
        if self.connected:
            self.root.connection.commit(self.root.label, self.global_extents)

    def set(self, key, value):
        """
        Immediately sets element identified by key within this collection to the value provided at the device
            PC -> Gate -> DUT
        """
        if self.connected:
            # Begin with last sent values or the defaults if the buffer has never been commited
            send = list(self.sent) if self.is_sent else list(self.default)
            for block in self:
                if block.has_register(key):
                    binary_value = block[key].reg_value_as_bin(value)
                    s,e = block[key].global_extents
                    send[s:e] = list(binary_value)
            # Send the whole package
            self.root.connection.set(self.root.label, self.global_index, ''.join(send))
                        

    # Output Management --------------------------------------------


    def refresh(self):
        """
        Updates the gate's output buffer with fresh data from the device
            PC   Gate <- DUT
        """
        if self.connected:
            self.root.connection.refresh(self.root.label)

    def inspect(self, key):
        """
        Retrieves this registers value from the gate's output buffer
            PC <- Gate Out
        """
        if self.connected:
            results = {}
            self.root.connection.inspect(self.root.label, self.global_extents)
            for block in self:
                if block.has_register(key):
                    #s,e = block[key].global_extents
                    results[block.label] = block[key].retrieved
            return results
        else:
            return None

    def get(self, key):
        """
        Immediately gets all of the matching elements values from the device
            PC <- Gate <- DUT
        """
        if self.connected:
            results = {}
            self.root.connection.refresh(self.root.label)
            self.root.connection.inspect(self.root.label, self.global_extents)
            for block in self:
                if block.has_register(key):
                    results[block.label] = block[key].retrieved
            return results        
        else:
            return None



if __name__ == '__main__':
    pass

    