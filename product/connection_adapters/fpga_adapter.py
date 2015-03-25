#!/usr/bin/env python

from common.base import *

from product.connection_adapters.abstract_adapter import AbstractAdapter

# FPGA Serial Interface Register Offset Addresses
FPGA_ID    = 0x00 # Offset 0 : Contains two 4 bit fields. The upper identifies the device, the lower contains the revision level
GL_CSR     = 0x02 # Offset 2 : Global control and status register. Setting bit 0 to 1 aborts any pending FPGA operation and resets the FPGA 
CFG        = 0x03 # Offset 3 : Bit 0 of CFG is the Serial Interface Bus Enable bit which controls activation of the the SCR
CLK_SL     = 0x09 # Offset 9 : Clock Select - Sets the clock source on the SCR target specified
SI_CSR     = 0x30 # Offset 48 : Accepts OpCodes to trigger FPGA actions
SI_MCTL    = 0x31 # Offset 49 : Manual mode register that accepts bit banging to create SCR clock
SI_CFG_0   = 0x32 # Offset 50 : Bit indexes 4-5 select clock frequency for the SI for top? Indexes 6-7 for bottom?
SI_CFG_1   = 0x33 # Offset 51 : Accepts reset and SCR mode bit controls
SI_ADDR_0  = 0x34 # Offset 52 : Holds bits 0-7 of the address used to access SI_RAM_0 or SI_RAM_1 
SI_ADDR_1  = 0x35 # Offset 53 : Holds bit 8 of the address used to access SI_RAM_0 or SI_RAM_1  
SI_DATA    = 0x36 # Offset 54 : Holds the lower byte of the data being read or written to SI_RAM_0 or SI_RAM_1
SI_CNT_0   = 0x37 # Offset 55 : Holds lower 8 bits of count specifying number of bits to be R/W
SI_CNT_1   = 0x38 # Offset 56 : Holds upper 4 bits of count specifying number of bits to be R/W

# Sub-Offset Addresses
SI_CSR_ERR = 0x01 # bit 0 from Offset 48 : FPGA sets to 1 when OpCode was invalid
SI_CSR_ST  = 0x02 # bit 1 from Offset 48 : User sets to 1 when submitting an OpCode 

# Opcode values for SI_CSR bit indexes 4-7 (Entire byte should be 0100 + opcode)
OPCODE_READ_SERDES    = 0x10 # 0001 Read SerDes SCR into RAM_1
OPCODE_WRITE_SERDES   = 0x20 # 0010 Write RAM_0 to SerDes SCR
OPCODE_READ_SI_RAM0   = 0x40 # 0100 Read SI_RAM_0 and increment Address
OPCODE_WRITE_SI_RAM0  = 0x50 # 0101 Write SI_RAM_0 and increment Address
OPCODE_READ_SI_RAM1   = 0x60 # 0110 Read SI_RAM_1 and increment Address
OPCODE_WRITE_SI_RAM1  = 0x70 # 0111 Write SI_RAM_1 and increment Address

class FPGAAdapter(AbstractAdapter):
    """
    Encapsulates the behavior by which a test board with an FPGA
    interface to the device under test manages orientation targeting and 
    SCR manipulation.
    """

    entity_name = 'fpga_adapter'
    entity_atts = []

    def __init__(self):
        # Prepare Parent
        super(FPGAAdapter, self).__init__()

        # Set abstract properties
        self._type = 'FPGA'
        self._port = None
        
        # Which SCR was targeted last
        self._cur_target    = None
        
        self._input_buffer  = None
        self._output_buffer = None
        
        # Which RAM address did I talk to last
        self._cur_byte_index_target = 0
        self._byte_counts = {}


    # FPGA Management --------------------------
  

    def _clear_errors(self):
        """
        Clear any protocol or internal gate errors and prepares the gate for a command
        """
        self._update_register(2, 'xxxxxxx1')

    # TODO: What about when orientation SCRS are different lengths? They aren't in this part, 
    # but in order to make the Adapter API uniform we have to make the SCR length setup internal to the Adapter
    def _set_scr_length(self, bit_count):
        """
        SI_CNT_0 = 0x37 # Offset 55 : Holds LOWER 8 bits of count specifying number of bits to be R/W
        SI_CNT_1 = 0x38 # Offset 56 : Holds UPPER 4 bits of count specifying number of bits to be R/W
        """
        #self.log.debug('Setting scr_length to %s' % bit_count)

        upper_bits, lower_bits = divmod(bit_count, 256 )
        upper_bits = int_to_bin(upper_bits, 8)
        lower_bits = int_to_bin(lower_bits, 8)

        self._update_register(55, lower_bits)
        self._update_register(56, upper_bits)

    def _num_bytes(self, bit_count):
        """
        Calculates the number of bytes that it will take to represent the bit_string provided
        """
        byte_count, remainder = divmod(bit_count, 8)  
        if remainder > 0:
            byte_count += 1
        return byte_count

    def _is_valid_target(self, target):
        """
        Whether or not the target is valid for this adapter
        """
        # return (target in VALID_TARGETS)
        pass

    def _set_target(self, target):
        """
        Controls which target the RAM buffers are pointing to
        """
        if self._cur_target == target:
            #self.log.debug('Same target as last, no updates performed.')
            pass
        else:
            # New target, so update the local buffers
            #self.log.debug('Switching targets and updating buffers.')
            # FIXME: These are part sensative. NEED TO CHANGE
            if target == 'top':
                self._top_scr_on()
                self._manual_top()
            elif target == 'bottom':
                self._bot_scr_on()
                self._manual_bot()
                       
            # Update current target
            self._cur_target = target

            # Update the adapter buffers
            self._populate_output_buffer()

            # Update the local buffer so that it reflects the current target's state
            self._read_output_buffer()
            

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
        value = list(value)
        data_width = len(value)
        if len(value) == len(self._scr_sessions[target].default):
            for i, bit in enumerate(value):
                if bit == self._scr_sessions[target].sent[global_index + i]:
                    self._scr_sessions[target].prepared[global_index + i] = None
        else:
            self._scr_sessions[target].prepared[global_index : global_index + data_width] = value
                
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


    # Non-Register API Hooks --------------------------------


    def set_clock_source(self, target, source = 'stop'):
        """
        Sets the clock source on the SCR target specified:
        
        target : top or bottom
        source :    sma      = Take clock source from SMA connector
                    internal = Take clock source from internal clock
                    stop     = No clock source
        """
        targets = {
            'top'    : "xxxxBBxx",
            'bottom' : "xxxxxxBB"
            }        
        source_bits = {
            'sma'      : '11',
            'internal' : '01',
            'stop'     : '00'
            }
        
        # Validate
        source = source.lower()
        if source not in source_bits.keys():
            raise ValueError('Could not set clock, an unrecognized clock source was specified: %s' % source)
        
        target = target.lower()
        if target not in targets.keys():
            raise ValueError('Could not set clock, an unrecognized target was specified: %s' % target)
        
        mask = targets[target].replace('BB', source_bits[source])
        self._update_register(CLK_SL, mask)
       

    # Serial Interface Configuration Zero (SI_CFG_0) : 50    

    def set_scr_clock_divider(self, divider):
        """
        Set the SCR clock divider
        divider :   64 or 'slow'   will divide the clock by 64
                    8  or 'medium' will divide the clock by 8
                    2  or 'fast'   will divide the clock by 2
        """
        divider = '%s' % divider
        divider = divider.lower()
        if divider == '64' or divider == 'slow':
            self._update_register(SI_CFG_0, "xx01xxxx") # clk / 64
        elif divider == '8' or divider == 'medium':
            self._update_register(SI_CFG_0, "xx10xxxx") # clk / 8
        elif divider == '2' or divider == 'fast':
            self._update_register(SI_CFG_0, "xx11xxxx") # clk / 2
        else:
            raise ValueError('Could not set clock divider, an unrecognized divider was specified: %s' % divider)


    # Private FPGA Commands --------------------------------

    # Global Control Status Register (GL_CSR) : Offset 2
  
    # Global Configuration Register (CFG) : Offset 3
    # Bit 0 of CFG is the SBE bit, which enables / disables the buffers driving the Serial Interface signals
    
    def _scr_enable(self):
        self._update_register(CFG, "xxxxxxx1")
        
    def _scr_disable(self):
        self._update_register(CFG, "xxxxxxx0")

    def _manual_top(self):
        self._update_register(SI_CFG_0, "1xxxxxxx")
        
    def _manual_bot(self):
        self._update_register(SI_CFG_0, "0xxxxxxx")
        
    def _top_scr_on(self):
        self._update_register(SI_CFG_1, "x1xxxxxx")
    def _top_scr_off(self):
        self._update_register(SI_CFG_1, "x0xxxxxx")

    def _bot_scr_on(self):
        self._update_register(SI_CFG_1, "xxxxx1xx")
    def _bot_scr_off(self):
        self._update_register(SI_CFG_1, "xxxxx0xx")


    # Unique to Serial Board
    def _scr_si_cfg_1_reset(self):
        self._update_register(SI_CFG_1, "xxxx11xx")
        
    def _scr_si_cfg_1_scr(self):
        self._update_register(SI_CFG_1, "xxxx01xx")
        
    def _scr_si_cfg_0(self):
        self._update_register(SI_CFG_1, "xx11xxxx")


    # Buffer Targeting
    # _set_ram_address
    def _set_byte_index_target(self, byte_index):
        """
        Sets the index of the byte which the FPGA will send to the 
        SI_DATA register so that it can be read out or written to.
        
            SI_ADDR_0 holds bits 0-7 of the address used to access SI_RAM_0 or SI_RAM_1 
            SI_ADDR_1 holds bit   8  of the address used to access SI_RAM_0 or SI_RAM_1 
        
        """
        if self._cur_byte_index_target != byte_index:
            self._port.write(SI_ADDR_0, byte_index & 0xff)    
            self._port.write(SI_ADDR_1, (byte_index >> 8) & 0xff)
            self._cur_byte_index_target = byte_index


    # FPGA OpCode Transmission and Error Handling --------------------------


    def _send_opcode(self, opcode):
        """
        Sends opcode to SI_CSR register and checks for errors 
        
        SI_CSR     = 0x30 # Offset 48 : Accepts OpCodes to trigger FPGA actions
        SI_CSR_ERR = 0x01 # bit 0 from Offset 48 : FPGA sets to 1 when OpCode was invalid
        SI_CSR_ST  = 0x02 # bit 1 from Offset 48 : User sets to 1 when submitting an OpCode 

        The following opcodes perform an action across all bytes. As such the initial byte_index
        in SI_ADDR_0 and SI_ADDR_1 must always be set to 0 before sending these opcodes. After the
        opcodes have been sent, the byte_index represented in SI_ADDR_0 and SI_ADDR_1 will be incremented
        by the number of bytes in the data array (if there are 214 bytes, an inital byte index of 0
        will be incremented up to 214. If you start at 4, it will increment to 218 - past the end of the data).
        
            OPCODE_READ_SERDES   = 0x10 # 0001 Read SerDes SCR into RAM_1
            OPCODE_WRITE_SERDES  = 0x20 # 0010 Write RAM_0 to SerDes SCR
        
        The following opcodes perform an action for a single byte and then increment 
        the current byte_index value represented by SI_ADDR_0 and SI_ADDR_1 by 1
        
            OPCODE_READ_SI_RAM0  = 0x40 # 0100 Read  SI_RAM_0 and increment Address
            OPCODE_WRITE_SI_RAM0 = 0x50 # 0101 Write SI_RAM_0 and increment Address
            OPCODE_READ_SI_RAM1  = 0x60 # 0110 Read  SI_RAM_1 and increment Address
            OPCODE_WRITE_SI_RAM1 = 0x70 # 0111 Write SI_RAM_1 and increment Address
        """
        
        # Always set byte index to zero when reading or writing serdes to avoid 
        if opcode == OPCODE_READ_SERDES or opcode == OPCODE_WRITE_SERDES:
            self._set_byte_index_target(0)
               
        self._port.write(SI_CSR, (opcode | SI_CSR_ST | SI_CSR_ERR))
        # Make sure an error isn't thrown
        timeOut = 0
        while self._port.read(SI_CSR) & SI_CSR_ST:
            timeOut += 1
            if timeOut == 200 :
                self.log.error("ERROR::SI_ST bit in SI_CSR not set to zero")
                sys.exit(0)
        
        # Update the _cur_byte_index_target by one to adjust for the FPGAs auto incrementer
        if opcode == OPCODE_READ_SERDES or opcode == OPCODE_WRITE_SERDES:
            self._cur_byte_index_target += self._byte_counts[self._cur_target]
        else:
            self._cur_byte_index_target += 1

    # Byte manipulation helpers
    
    def _update_register(self, reg_index, bitmask):
        """
        Updates the bit sequence of the register specified by first retrieving 
        it's current value, and then flipping the bits identified in the bit mask
        """
        byte = self._port.read(reg_index)
        byte = self._mask_byte(byte, bitmask)
        self._port.write(reg_index, byte)

    def _mask_byte(self, byte, bitmask):
        """
        Flips bits identified by bitmask in byte provided and returns result
        """
        bitmask = bitmask.lower()
        mask_and = bitmask.replace('x','1')
        mask_and = bin_to_int(mask_and)
        mask_or = bitmask.replace('x','0')
        mask_or = bin_to_int(mask_or)
        return ((byte & mask_and) | mask_or)
        

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
            # Move the collection window to the byte index
            self._set_byte_index_target(byte_index)
            # Populate the SI_DATA register with the byte at the byte_index in the input buffer
            self._send_opcode(OPCODE_READ_SI_RAM0)
            # Get the byte from the I/O
            byte = self._port.read(SI_DATA)
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
           
    def _read_input_buffer_byte(self, byte_index):
        """
        Retrieve a single byte from the FPGAs input buffer (RAM_0)
        """
        # Move the collection window to the byte index
        self._set_byte_index_target(byte_index)
        # Populate the SI_DATA register with the byte at the byte_index in the input buffer
        self._send_opcode(OPCODE_READ_SI_RAM0)
        # Get the byte from the I/O
        byte = self._port.read(SI_DATA)
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
        self._input_buffer[s:e] = list(bit_string)
        return bit_string


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

            # Move the target window to the byte index
            self._set_byte_index_target(byte_index)
            # Send the byte across the I/O
            self._port.write(SI_DATA, byte)
            # Write the the byte to the input buffer at the byte_index
            self._send_opcode(OPCODE_WRITE_SI_RAM0)

        # Update the output buffer
        self._input_buffer = bit_array[:]

    def _commit_input_buffer(self):
        """
        Triggers a commit of the FPGA input buffer (RAM_0) to the SerDes SCR
        """
        self._send_opcode(OPCODE_WRITE_SERDES)
        self._scr_sessions[self._cur_target].sent = self._input_buffer[:]


    # Output Buffer Read / Write / Populate


    def _populate_output_buffer(self):
        """
        Triggers a retrieval of the SerDes SCR into the FPGA's output buffer (RAM_1)
        """
        self._send_opcode(OPCODE_READ_SERDES)


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
            # Move the collection window to the byte index
            self._set_byte_index_target(byte_index)
            # Populate the SI_DATA register with the byte at the byte_index in the input buffer
            self._send_opcode(OPCODE_READ_SI_RAM1)
            # Get the byte from the I/O
            byte = self._port.read(SI_DATA)
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
        # Move the collection window to the byte index
        self._set_byte_index_target(byte_index)
        # Populate the SI_DATA register with the byte at the byte_index in the input buffer
        self._send_opcode(OPCODE_READ_SI_RAM1)
        # Get the byte from the I/O
        byte = self._port.read(SI_DATA)
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
        Send an array of bits from PC to FPGA output buffer (RAM_1)
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
            # Move the collection window to the byte index
            self._set_byte_index_target(byte_index)
            # Send the byte across the I/O
            self._port.write(SI_DATA, byte)        
            # Submit all of the writes
            self._send_opcode(OPCODE_WRITE_SI_RAM1)
            
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
