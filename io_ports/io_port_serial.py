#!/usr/bin/env python

"""
SerialBridge
"""

#SERDES_REG_BITS_COUNT = 1130

# Serial OpCodes
DLE    = 0xD0
RG_RD  = 0xD1
RG_WR  = 0xD2    # Write
R_CMD3 = 0xD3
R_CMD4 = 0xD4
R_CMD5 = 0xD5
R_CMD6 = 0xD6
R_CMD7 = 0xD7

import serial

from common.base import *

class SerialSocket(AppBase):
    """
    FPGA via Serial Interface
    """

    entity_name = 'serial_socket'
    entity_atts = []

    def __new__(cls, *p, **k):
        """Forces StationManger to act as Singleton"""
        if not '_single_instance' in cls.__dict__:
            cls._single_instance = object.__new__(cls)
            
            # Prepare Parent
            #super(SerialSocket, self).__init__()
            
            cls.__port = serial.Serial(port = 0, baudrate = 19200, parity = 'O', timeout=1)
        else:
            if not cls._single_instance.is_open:
                cls._single_instance.open()
        return cls._single_instance

   #def __init__(self, port = None):
   #     # Prepare Parent
   #     super(SerialSocket, self).__init__()
   #     # TODO: May need to push __port assignement down into connect method
   #     self.__port = serial.Serial(port = 0, baudrate = 19200, parity = 'O', timeout=1)


    # Connection Management -----------------------------------

    # CANT USE THIS DETECT METHOD BECAUSE IT CAUSES FILE LOCKS ON THE OPEN PORT
    @staticmethod
    def detect():
        """Interogates the PC to determine if a serial connection can be established"""
        try:
            s = serial.Serial(port = 0, baudrate = 19200, parity = 'O', timeout=1)
        except Exception, e:
            log = logging.getLogger('root')
            log.exception(e)
            return False
        else:
            return True
        finally:
            s.close()
            
    def open(self):
        """Closes the serial port."""
        self.__port.open()

    def close(self):
        """Closes the serial port."""
        self.__port.close()

    @property
    def is_open(self):
        """Returns True or False reflecting whether or not the connection is open."""
        return self.__port.isOpen()

    @property
    def state(self):
        """Returns the properties associated with the serial port."""
        return {
            'port'     : self.self.__port.port,      #port name/number as set by the user
            'baudrate' : self.self.__port.baudrate,  #current baudrate setting
            'bytesize' : self.self.__port.bytesize,  #bytesize in bits
            'parity'   : self.self.__port.parity,    #parity setting
            'stopbits' : self.self.__port.stopbits,  #stop bit with (1,2)
            'timeout'  : self.self.__port.timeout,   #timeout setting
            'xonxoff'  : self.self.__port.xonxoff,   #if Xon/Xoff flow control is enabled
            'rtscts'   : self.self.__port.rtscts     #if hardware flow control is enabled
            }
    
    # Protocol Read / Write Methods --------------------------------


    def read(self, index):
        """
        Read method which returns data at index from the FPGA register via a serial interface
        """
        # Read Opcode
        isNotFirstCmd = False
        self.__ser_wr_trans(RG_RD, isNotFirstCmd)
        # Read Address
        self.__ser_wr_trans(index)
        rdata = self.__port.read()
        if rdata == '':
            raise ValueError('Serial i/O error - ord() expects a character, but string of length 0 is present.')
        result = ord(rdata)
        return result
    
    def write(self, index, data):
        """
        Write method which write data at index into the FPGA register via a serial interface
        """
        isNotFirstCmd = False
        # Write Opcode
        self.__ser_wr_trans(RG_WR, isNotFirstCmd)
        isNotFirstCmd = True
        # Write Address
        self.__ser_wr_trans(index, isNotFirstCmd)
        # Write Data
        self.__ser_wr_trans(data, isNotFirstCmd)


    def __data_to_ser_str(self, data):
        return chr(int(data))
    
    def __ser_wr_trans(self, transaction, isNotFirstCmd = True):
        dat_str = self.__data_to_ser_str(transaction)
        if isNotFirstCmd :
            self.__send_dle(transaction)
        self.__port.write(dat_str)         
            
    def __send_dle(self, trans_val):
        """ 
        if the Address or Data is between DLE and R_CMD7 then 
        a DLE Command must be sent across the Serial Interface
        """
        if (trans_val >= DLE and trans_val <= R_CMD7):
            dle_str = chr(int(DLE)) 
            self.__port.write(dle_str)

    def dump(self, compare_to = None):
        """
        Diagnostic helpers the reads the every register from the FPGA
        """
        regs = {}     
        regs[0] = 'FPGA_ID '
        regs[1] = 'reserved'
        regs[2] = 'GL_CSR'
        regs[3] = 'CFG'
        regs[4] = 'reserved'
        regs[5] = 'LED'
        regs[6] = 'S_PAD_0'
        regs[7] = 'S_PAD_1'
        regs[8] = 'reserved'
        regs[9] = 'reserved'
        regs[10] = 'GP_OUT'
        regs[11] = 'reserved'
        regs[12] = 'GP_IN'
        regs[13] = 'reserved'
        regs[14] = 'reserved'
        regs[15] = 'reserved'
        regs[16] = 'reserved'
        regs[17] = 'reserved'
        regs[18] = 'reserved'
        regs[19] = 'reserved'
        regs[20] = 'reserved'
        regs[21] = 'reserved'
        regs[22] = 'reserved'
        regs[23] = 'reserved'
        regs[24] = 'reserved'
        regs[25] = 'reserved'
        regs[26] = 'reserved'
        regs[27] = 'reserved'
        regs[28] = 'reserved'
        regs[29] = 'reserved'
        regs[30] = 'reserved'
        regs[31] = 'reserved'
        regs[32] = 'reserved'
        regs[33] = 'reserved'
        regs[34] = 'reserved'
        regs[35] = 'reserved'
        regs[36] = 'reserved'
        regs[37] = 'reserved'
        regs[38] = 'reserved'
        regs[39] = 'reserved'
        regs[40] = 'reserved'
        regs[41] = 'reserved'
        regs[42] = 'reserved'
        regs[43] = 'reserved'
        regs[44] = 'reserved'
        regs[45] = 'reserved'
        regs[46] = 'reserved'
        regs[47] = 'reserved'
        regs[48] = 'SI_CSR'
        regs[49] = 'SI_MCTL'
        regs[50] = 'SI_CFG_0'
        regs[51] = 'SI_CFG_1'
        regs[52] = 'SI_ADDR_0'
        regs[53] = 'SI_ADDR_1'
        regs[54] = 'SI_DATA'
        regs[55] = 'SI_CNT_0'
        regs[56] = 'SI_CNT_1'
        regs[57] = 'Reserved'
        regs[58] = 'Reserved'
        regs[59] = 'Reserved'
        regs[60] = 'Reserved'
        regs[61] = 'Reserved'
        regs[62] = 'Reserved'
        regs[63] = 'Reserved'       

        self.log.debug('Dumping Serial FPGA Registers')
        self.log.debug('REG_INDEX\tINT\tBIN\tNAME')
        bits = []
        for i in xrange(64):
            num = self.read(i)
            bin = int_to_bin(num, 8)
            self.log.debug('%s\t%s\t%s\t%s' % (i, self.read(i), bin, regs[i]))
            bits.append(bin)

        if compare_to:
            delta_index_map = []
            list_a = list(compare_to)
            list_b = list(''.join(bits))

            # Find indexes of deltas
            delta_indexs = []
            for index, value in enumerate(list_a):
                if value != list_b[index]: 
                    delta_indexs.append(index)
                    c = '1' if value == '1' else '0'
                    delta_index_map.append(c)
                else:
                    delta_index_map.append('_')
                    
            return (delta_indexs, ''.join(delta_index_map))
        

if __name__=='__main__' :
    ss1 = SerialSocket()
    #ss2 = SerialSocket()
    #print '%s = %s' % (id(ss1),id(ss2))
    ss1.dump()
    ss1.close()
    pass    