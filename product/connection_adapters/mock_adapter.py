#!/usr/bin/env python

"""
Mock adapter to use when testing package connectivity methods without a bench
"""

from product.connection_adapters.abstract_adapter import *

VALID_TARGETS = ['top', 'bottom']

class MockAdapter(AbstractAdapter):
    """Mock ConnectionAdapter class exposes an I/O API which will be uniform across all connection adapters"""
 
    entity_name = 'mock_adapter'
    entity_atts = []

    def __init__(self):
        # Prepare Parent
        super(MockAdapter, self).__init__()
        
        # Set abstract properties
        self._type      = 'Mock'

        # Which SCR was targeted last
        self._cur_target    = None
        
        self._input_buffer  = None
        self._output_buffer = None
        
        self._byte_counts = {}
        
               
    # Connection Management --------------------------
    
    
    @staticmethod
    def detect():
        """Pretends to have sniffed out a mock adapter"""
        return True

    @property
    def state(self):
        """Returns the connection state of the protocol."""
        if self._connected:
            return 'active'
        else:
            return 'no connection'

    def log_adapter_state(self):
        """
        Writes out the complete state of the adapter to the log
        """
        log_msg = 'Connection Adapter State:\nTYPE: %s' % self._type
        #for i in range(number_of_adapter_registers):
            #data = self._read(i)
            #log_msg += '\n%s %s %s' % (i, data, int2bin(data, 8))
        self.log.debug(log_msg)

    def connect(self, package):
        """
        Initializes the FPGA and creates a new session for each SCR in the package
        """
        if self._connected == True:
            #self.log.info('Already connected.')
            pass
        else:
            #self.log.debug('CONNECTING via Mock Adapter')
            # Initialize the buffers
            self._prepare_adapter()

            # Initialize the buffers
            scr_length = package[0].width
            self._input_buffer  = list(package[0].value)
            self._output_buffer = list(package[0].value)

            # Fake the physical state in this Mock
            self.fake_buffers = {}
            self.fake_physical_scrs = {}            
            self.fake_device_state = None

            # Connect the adapter to the SCR
            # ... manipulate adapter registers here or in submethod ...
    
            # Set global adapter defaults
            # ... like ... set_scr_clock_divider

            # Initialize a session for each SCR
            for scr in package:
                                
                # Validate target
                if not self._is_valid_target(scr.label):
                    raise ValueError('Could not create session for %s, the FPGA does not recognize it as a valid target.' % scr.label)
    
                # Create a virtual SCR session to manage state                
                self._scr_sessions[scr.label] = SerialControlRegisterSession(scr)

                # Calculate and save the number of bytes it will take to represent this scr 
                self._byte_counts[scr.label]  = self._num_bytes(scr.width)

                # Fake initializing the physical buffers
                self.fake_physical_scrs[scr.label]     = self._bit_array_to_byte_array_for_fake(list(scr.default))
                self.fake_buffers[scr.label] = {}
                self.fake_buffers[scr.label]['input']  = self.fake_physical_scrs[scr.label][:]
                self.fake_buffers[scr.label]['output'] = self.fake_physical_scrs[scr.label][:]
 

                # Set target specific adapter defaults
                # ... like ... self.set_clock_source(scr.label, 'sma')

            # Set connection state
            self._connected = True

            # Initialize the buffers to a target
            self._set_target(package[0].label)


    def _bit_array_to_byte_array_for_fake(self, bit_array):
        """This method converts a sequence of bits into a byte array"""
        bytes = []
        bit_array_length = len(bit_array)
        byte_count = self._num_bytes(bit_array_length)       
        for byte_index in range(byte_count):
            # Make sure we end early on the last byte            
            s = byte_index * 8
            if s+8 < bit_array_length:
                e = s + 8
                bits = bit_array[s:e]
            else:
                e = bit_array_length
                bits = bit_array[s:e] + (['0'] * (8-(e-s)))
            # Reverse the bit string so that Pythons byte casting will work
            bits = bits[::-1]         
            # Transform the bit array to an integer
            byte = bin_to_int(bits)
            # Store the byte
            bytes.append(byte)

        # Return the bytes
        return bytes

    def _num_bytes(self, bit_count):
        """
        Calculates the number of bytes that it will take to represent the bit_string provided
        """
        byte_count, remainder = divmod(bit_count, 8)  
        if remainder > 0:
            byte_count += 1
        return byte_count
    
    def _prepare_adapter(self):
        """
        Performs and boot up requierments necesary to prepare the gate for operation
        """
        #self.log.debug('Preparing Gate')
        pass

    def _clear_errors(self):
        """
        Clear any protocol or internal gate errors and prepares the gate for a command
        """
        pass

    def _is_valid_target(self, target):
        """
        Whether or not the target is valid for this adapter
        """
        return (target in VALID_TARGETS)

    def _set_target(self, target):
        """
        Controls which target the adapter is performing SCR functions on
        """
        if self._cur_target == target:
            #self.log.debug('Same target as last, no updates performed.')
            pass
        else:
            # New target, so update the local buffers
            #self.log.debug('Switching targets and updating buffers.')

            if target == 'top':
                # ... manipulate adapter registers here ...
                pass
            elif target == 'bottom':
                # ... manipulate adapter registers here ...
                pass

            # Swap current physical buffers
            if self._cur_target != None:
                self.fake_physical_scrs[self._cur_target] = self.fake_device_state[:]
                self.fake_device_state = self.fake_physical_scrs[target][:]
            else:
                self.fake_device_state = self.fake_physical_scrs[target]
            
            # Update current target
            self._cur_target = target

            # Update the adapter buffers
            self._populate_output_buffer()
            # Update the local buffer so that it reflects the current target's state
            self._read_output_buffer()
            # Setup the input buffer
            self._write_input_buffer(self._scr_sessions[self._cur_target].value)


    # Mock Protocol I/O Methods --------------------------------

   
    def _read(self):
        """Protocol level read"""
        #self.log.debug('Gate READ')
        pass

    def _write(self, data):
        """Protocol level write"""
        #self.log.debug('Gate WRITE: %s' % data)
        pass


    # Global Package API Hooks --------------------------------


    def set_clock_source(self, target, source):
        """
        Sets the clock source for this SCR:
        source :    sma      = Take clock source from SMA connector
                    internal = Take clock source from internal clock
                    stop     = No clock source
        """
        # ... manipulate adapter registers here or in submethod ...
        self.log.debug('% set_clock_source %' % (target, source))


    # Global Package API Hooks --------------------------------


    # Package, SCR, Block, Register API Hooks   

    
    def _build_prepared(self, target):
        # Begin with last sent values or the defaults if the buffer has never been commited
        if self._scr_sessions[target].sent[0] != None:
            send = list(self._scr_sessions[target].sent)
        else:
            send = list(self._scr_sessions[target].default)
        # Update last sent with the surviving prepared values
        for i, bit in enumerate(self._scr_sessions[target].prepared):
            if bit != None:         
                send[i] = bit
        return send

    def prepare(self, target, global_index, value):
        """
        Writes the value provided at the index in the gate's input buffer, but does not commit it
            PC -> Gate Input
        """
        # Set the target
        self._set_target(target)
        #self.log.debug('Gate.prepare %s (%s) : %s' % (target, global_index, value))
        
        # Update the session's prepared array with the data
        data_width = len(value)        
        if len(value) == len(self._scr_sessions[target].default):
            for i, bit in enumerate(list(value)):
                if bit == self._scr_sessions[target].sent[global_index + i]:
                    self._scr_sessions[target].prepared[global_index + i] = None
        else:
            self._scr_sessions[target].prepared[global_index : global_index + data_width] = list(value)      
        
    def check(self, target, global_extents):
        """
        Returns the prepared value at the index provided from the gate's input buffer
            PC <- Gate Input
        """
        # Set the target
        self._set_target(target)
        s,e=global_extents
        return self._scr_sessions[target].prepared[s:e]
        #self.log.debug('Gate.check %s (%s - %s)' % (target, s, e))
        
    def clear(self, target, global_extents):
        """
        Throws away all of the prepared value sets
        """
        # Set the target
        self._set_target(target)
        s,e=global_extents
        self._scr_sessions[target].prepared[s:e] = [None for i in range(e-s)]     
        
        
    def commit(self, target, global_extents):
        """
        Sends the value at the index specified from the gate's input buffer into the device 
            Gate Input -> DUT
        """
        # Set the target
        self._set_target(target)
        s,e = global_extents
        #self.log.debug('Gate.commit %s (%s - %s)' % (target, s, e)) 

        # Begin with last sent values or the defaults if the buffer has never been commited
        if self._scr_sessions[target].sent[0] != None:
            send = list(self._scr_sessions[target].sent)
        else:
            send = list(self._scr_sessions[target].default)

        # Update last sent with prepared values in the range being commited       
        i = s
        while i < e:
            bit = self._scr_sessions[target].prepared[i]
            if bit != None:
                send[i] = bit
            i +=1
        
        # Commit the values
        self._write_input_buffer(send)
        self._commit_input_buffer()
        
        # Clear the prepared commands
        self._scr_sessions[target].prepared[s:e] = [None for i in range(e-s)]


    def set(self, target, global_index, value):
        """
        Immediately sets the data at the index specified in the device (equivalent to a prepare + commit)
            PC -> Gate -> DUT
        """
        # Set the target
        self._set_target(target)
        # Begin with last sent values or the defaults if the buffer has never been commited
        if self._scr_sessions[target].sent[0] != None:
            send = list(self._scr_sessions[target].sent)
        else:
            send = list(self._scr_sessions[target].default)            
        # Add in the set value
        data_width = len(value)       
        send[global_index : global_index + data_width] = value
        #self.log.debug('Gate.set %s [%s..%s] = %s' % (target, global_index, global_index+data_width, value))
        
        self._write_input_buffer(send)
        self._commit_input_buffer()


    # Output Management


    def refresh(self, target):
        """
        Populates the gate's output buffer with data from the device        
            Gate Output <- DUT
        """
        #self.log.debug('Gate.refresh %s' % target)
        # Get the data no matter what
        if self._cur_target == target:
            self._populate_output_buffer()
        else:
            self._set_target(target)
    
    def inspect(self, target, global_extents):
        """
        Prepares to return the data at the index specified from the gate's output buffer
            PC <- Gate Out
        """
        #self.log.debug('Gate.inspect %s' % target)
        s,e = global_extents
        if self._cur_target == target:
            self._read_output_buffer(s, e)
        else:
            self._set_target(target)

        
    def get(self, target, global_extents):
        """
        Immediately returns the data at the index specified from the device (equivalent to a refresh + inspect)
            PC <- Gate <- DUT
        """
        # Get the data no matter what
        s,e = global_extents
        #self.log.debug('Gate.get %s (%s - %s)' % (target, s, e))   
        if self._cur_target == target:
            self._populate_output_buffer()
            self._read_output_buffer(s, e)
        else:
            self._set_target(target)


    # FPGA I/O Buffer Management -------------------------------------------
          
    # Input Buffer Read / Write / Commit

    def _read_input_buffer(self, start_bit_index=0, end_bit_index = None):
        """
        Retrieve data from FPGA input buffer (RAM_0)
        """
        byte_count = self._byte_counts[self._cur_target]
        if start_bit_index==0 and end_bit_index == None:
            # Loop over all bytes requested
            start_byte = 0
            end_byte   = byte_count
        else:
            # Loop over the bytes requested
            start_byte, remainder = divmod(start_bit_index, 8)
            end_byte, remainder   = divmod(end_bit_index, 8)
            if remainder > 0:
                end_byte += 1
        
        for byte_index in range(start_byte, end_byte):
            # Fake getting the bytes from the I/O
            byte = self.fake_buffers[self._cur_target]['input'][byte_index]
            # Make sure we end early on the last byte            
            s = byte_index * 8
            if byte_index < byte_count-1:
                e = s + 8                
            else:
                e = len(self._scr_sessions[self._cur_target].default)                
            # Transform the integer to a binary sequence
            bit_string = int_to_bin(byte, 8)
            # Reverse the bit string so that Pythons byte casting will work
            bit_string = bit_string[::-1][0:e-s]
            # Populate the input buffer
            self._input_buffer[s:e] = list(bit_string)
            
            #self.log.debug('RI: %s (%s..%s) = %s = %s' % (byte_index, s, e, ''.join(bit_string), byte))


    def _write_input_buffer(self, bit_array):
        """
        Send an array of bits from the PC to FPGA input buffer (RAM_0)
        """
        # Only update what needs to change
        bit_array_length = len(bit_array)
        updated_byte_indexs = self._modified_byte_indexes(self._input_buffer, bit_array)
        for byte_index in updated_byte_indexs:
            # Make sure we end early on the last byte            
            s = byte_index * 8
            if s+8 < bit_array_length:
                e = s + 8
                bits = bit_array[s:e]
            else:
                e = bit_array_length
                bits = bit_array[s:e] + (['0'] * (8-(e-s)))
            # Reverse the bit string so that Pythons byte casting will work
            bits = bits[::-1]         
            # Transform the bit array to an integer
            byte = bin_to_int(bits)
            
            #self.log.debug('WI: %s (%s..%s) = %s = %s' % (byte_index, s, e, ''.join(bits), byte))
            
            # Fake sending the writes
            self.fake_buffers[self._cur_target]['input'][byte_index] = byte
            
        # Update the output buffer
        self._input_buffer = bit_array


    def _commit_input_buffer(self):
        """
        Triggers a commit from the adapter's input buffer into the device
        """
        #self.log.debug('commit_INPUT_buffer: %s' % self._input_buffer)
        # Fake sending the data to the device
        # ... manipulate adapter registers here ...
        self.fake_device_state = self.fake_buffers[self._cur_target]['input'][:]
        # Save in local buffer
        self._scr_sessions[self._cur_target].sent = self._input_buffer[:]
    
    # Output Buffer Read / Write / Populate


    def _populate_output_buffer(self):
        """
        Triggers a retrieval of the adapter's output buffer with data from the device
        """
        #self.log.debug('populate_OUTPUT_buffer')
        # Fake getting the data from the device
        # ... manipulate adapter registers here ...
        self.fake_buffers[self._cur_target]['output'] = self.fake_device_state[:]


    def _read_output_buffer(self, start_bit_index=0, end_bit_index = None):
        """
        Retrieves every byte from the FPGA's output buffer (RAM_1)
        """
        byte_count = self._byte_counts[self._cur_target]
        if start_bit_index==0 and end_bit_index == None:
            # Loop over all bytes requested
            start_byte = 0
            end_byte   = byte_count
        else:
            # Loop over the bytes requested
            start_byte, remainder = divmod(start_bit_index, 8)
            end_byte, remainder   = divmod(end_bit_index, 8)
            if remainder > 0:
                end_byte += 1
                
        for byte_index in range(start_byte, end_byte):
            # Fake getting the bytes from the I/O
            byte = self.fake_buffers[self._cur_target]['output'][byte_index]
            
            # Make sure we end early on the last byte            
            s = byte_index * 8
            if byte_index < byte_count-1:
                e = s + 8
            else:
                e = len(self._scr_sessions[self._cur_target].default)  
            
            # Transform the integer to a binary sequence
            bit_string = int_to_bin(byte, 8)                     
            # Reverse the bit string so that Pythons byte casting will work
            bit_string = bit_string[::-1][0:e-s]
            
            #self.log.debug('RO: %s (%s..%s) = %s = %s' % (byte_index, s, e, bit_string, byte))
            
            # Populate the output buffer
            self._output_buffer[s:e] = list(bit_string)
            
        # Update the session to reflect the retrieved data
        self._scr_sessions[self._cur_target].retrieved = self._output_buffer[:]


    def _read_output_buffer_byte(self, byte_index):
        """
        Retrieve a single byte from the FPGAs output buffer (RAM_1)
        """
        # Fake getting the bytes from the I/O
        byte = self.fake_buffers[self._cur_target]['output'][byte_index]

        # Make sure we end early on the last byte
        s = byte_index * 8
        if byte_index < self._byte_counts[self._cur_target]-1:
            e = s + 8
        else:
            e = len(self._scr_sessions[self._cur_target].default)
        # Transform the integer to a binary sequence
        bit_string = int_to_bin(byte, 8)
        # Reverse the bit string so that Pythons byte casting will work
        bit_string = bit_string[::-1][0:e-s]
        # Populate the output buffer
        self._output_buffer[s:e] = list(bit_string)
        # Update the session to reflect the retrieved data
        self._scr_sessions[self._cur_target].retrieved[s:e] = self._output_buffer[s:e]
        return bit_string


    def _write_output_buffer(self, bit_array):
        """
        Send an array of bits to the adapter's output buffer
        """
        # Loop over every byte
        byte_count = self._num_bytes(len(bit_array))
        bit_array_length = len(bit_array)
        for byte_index in range(byte_count):
            # Make sure we end early on the last byte            
            s = byte_index * 8
            if s+8 < bit_array_length:
                e = s + 8
                bits = bit_array[s:e]
            else:
                e = bit_array_length
                bits = bit_array[s:e] + (['0'] * (8-(e-s)))
            # Clip the bits and reverse the bit string so that Pythons byte casting will work
            bits = bits[s:e][::-1]
            # Transform the bit array to an integer
            byte = bin_to_int(bits)      
            # Fake sending the writes
            self.fake_buffers[self._cur_target]['output'][byte_index] = byte
            
        self._output_buffer = bit_array


    # Buffer Efficiency Helpers -------------------------------------------


    def _modified_byte_indexes(self, bit_array_1 , bit_array_2):
        """
        Takes two bit arrays of the same length, and compares the values of every byte 
        in one string to the same coresponding byte index in the other, returning a collection 
        of byte indexes for the bytes that are not identical.
        """
        return range(self._num_bytes(len(bit_array_1)))

        # Validate
        if len(bit_array_1) != len(bit_array_2):
            raise ValueError('Byte sequences cannot be compared. Bit arrays are of differing lengths (%s != %s).' % (len(bit_array_1), len(bit_array_2)))
        # Return deltas
        modified_byte_indexes = []
        for byte_index in range(self._num_bytes(len(bit_array_1))):
            s = byte_index * 8
            e = s + 8
            if bit_array_1[s:e] != bit_array_2[s:e]:
                modified_byte_indexes.append(byte_index)
        return modified_byte_indexes


if __name__=='__main__' :
    pass