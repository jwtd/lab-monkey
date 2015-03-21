#!/usr/bin/env python

import parallel

from common.base import *

"""
ParallelFPGAAdapter

FROM PARALLEL < SEE PYPARALLEL for Acknowledgements >

    LPT1 = 0x0378 or 0x03BC
    LPT2 = 0x0278 or 0x0378
    LPT3 = 0x0278

    Data Register (base + 0) ........ outputs

    7 6 5 4 3 2 1 0
    . . . . . . . *  D0 ........... (pin 2), 1=High, 0=Low (true)
    . . . . . . * .  D1 ........... (pin 3), 1=High, 0=Low (true)
    . . . . . * . .  D2 ........... (pin 4), 1=High, 0=Low (true)
    . . . . * . . .  D3 ........... (pin 5), 1=High, 0=Low (true)
    . . . * . . . .  D4 ........... (pin 6), 1=High, 0=Low (true)
    . . * . . . . .  D5 ........... (pin 7), 1=High, 0=Low (true)
    . * . . . . . .  D6 ........... (pin 8), 1=High, 0=Low (true)
    * . . . . . . .  D7 ........... (pin 9), 1=High, 0=Low (true)

    Status Register (base + 1) ...... inputs

    7 6 5 4 3 2 1 0
    . . . . . * * *  Undefined
    . . . . * . . .  Error ........ (pin 15), high=1, low=0 (true)
    . . . * . . . .  Selected ..... (pin 13), high=1, low=0 (true)
    . . * . . . . .  No paper ..... (pin 12), high=1, low=0 (true)
    . * . . . . . .  Ack .......... (pin 10), high=1, low=0 (true)
    * . . . . . . .  Busy ......... (pin 11), high=0, low=1 (inverted)

    ctrl Register (base + 2) ..... outputs

    7 6 5 4 3 2 1 0
    . . . . . . . *  Strobe ....... (pin 1),  1=low, 0=high (inverted)
    . . . . . . * .  Auto Feed .... (pin 14), 1=low, 0=high (inverted)
    . . . . . * . .  Initialize ... (pin 16), 1=high,0=low  (true)
    . . . . * . . .  Select ....... (pin 17), 1=low, 0=high (inverted)
    * * * * . . . .  Unused

"""

#LPT1             = 0
#LPT2             = 1
#LPT1_base        = 0x0378
#LPT2_base        = 0x0278

HIGH             = 1
LOW              = 0

INIT             = 0x04
SELECT_IN        = 0x08


# Monkey patch Parallel
class Parallel(parallel.Parallel):
    """ Monkey patch to add read capabilities to Parallel"""

    # NOTE: Must add 'self.pyparallel = _pyparallel' 
    # to parallel.Parallel.Parallel's __init__ so that we can access it here
    
    def setCtrlReg(self, CtrlRegValue):
        self.ctrlReg = CtrlRegValue
        self.pyparallel.outp(self.ctrlRegAdr, self.ctrlReg)
        
    def getRegData(self):
        return self.pyparallel.inp(self.statusRegAdr)


class ParallelSocket(AppBase):
    """
    FPGA via Parallel Interface
    """

    entity_name = 'parallel_socket'
    entity_atts = []

    def __init__(self, port = None):
        # Prepare Parent
        super(ParallelSocket, self).__init__()
        
        # TODO: May need to push __port assignement down into connect method
        self.__port = Parallel()


    # Connection Management -----------------------------------
    

    @staticmethod
    def detect():
        """Interogates the PC to determine if a parallel port can be established"""
        try:
            Parallel()
        except:
            return False
        else:
            return True

    @property
    def state(self):
        """Returns the connection state of the protocol."""
        raise NotImplementedError()


    # Protocol Read / Write Methods --------------------------------


    def read(self, index):
        """
        Read method which returns data at index from the FPGA register via a parallel interface
        """
        # Point to the correct register
        self.__port.setData(index)
        
        # Set Select-in and INIT (inverted)
        self.__port.setCtrlReg(SELECT_IN)
        
        # process low nibble
        low_nib = self.__port.getRegData()
        low_nib = (low_nib >> 4) & 0xf

        # Clear Select-in and INIT
        self.__port.setCtrlReg(INIT)
        
        # 2 dummy reads
        self.__port.getRegData()
        self.__port.getRegData()
        
        # process high nibble
        high_nib = self.__port.getRegData() & 0xf0
        
        data = high_nib | low_nib
        
        # ???????
        data = data^0x88
        
        #if index in [48,54]:
        #    print 'read: %s = %s' % (index, data)
        
        return data    
    
    def write(self, index, data):
        """
        Write method which write data at index into the FPGA register via a parallel interface
        """
        #if index in [48,54]:
        #    print 'write: %s = %s' % (index, data)
        # Make sure control is in the low state
        # New function to speed up runtime - set everything
        self.__port.setCtrlReg(0)
        
        # Set Register Address on Data Bus
        self.__port.setData(index)
        
        # Set Auto Feed to LOW to capture address
        self.__port.setAutoFeed(LOW)
        
        # Set Data on Data Bus
        self.__port.setData(data)
        
        # Set Strobe Low
        self.__port.setDataStrobe(LOW)
        
        self.__port.setAutoFeed(HIGH)
        self.__port.setDataStrobe(HIGH)

    def dump(self, compare_to = None):
        """
        Diagnostic helpers the reads the every register from the FPGA
        """
        regs = {}
        regs[0] = 'FPGA_ID / DCC'
        regs[1] = 'DC_SEL'
        regs[2] = 'GL_CSR'
        regs[3] = 'reserved'
        regs[4] = 'I2C_CTL'
        regs[5] = 'LED'
        regs[6] = 'S_PAD_0'
        regs[7] = 'S_PAD_1'
        regs[8] = 'reserved'
        regs[9] = 'CLK_SL'
        regs[10] = 'GP_BUS_I_0'
        regs[11] = 'GP_BUS_I_1'
        regs[12] = 'GP_BUS_O_0'
        regs[13] = 'GP_BUS_O_1'
        regs[14] = 'P_L2_xDB'
        regs[15] = 'P_L3_xDB'
        regs[16] = 'P_L0_xDB'
        regs[17] = 'P_L1_xDB'
        regs[18] = 'reserved'
        regs[19] = 'reserved'
        regs[20] = 'reserved'
        regs[21] = 'reserved'
        regs[22] = 'reserved'
        regs[23] = 'reserved'
        regs[24] = 'reserved'
        regs[25] = 'reserved'
        regs[26] = 'reserved'
        regs[27] = 'DCM_CSR_GRX_0'
        regs[28] = 'DCM_CSR_R0'
        regs[29] = 'DCM_CSR_T0'
        regs[30] = 'DCM_CSR_R1'
        regs[31] = 'DCM_CSR_T1'
        regs[32] = 'DCM_CSR_GRX_1'
        regs[33] = 'DCM_CSR_R2'
        regs[34] = 'DCM_CSR_T2'
        regs[35] = 'DCM_CSR_R3'
        regs[36] = 'DCM_CSR_T3'
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
        regs[52] = 'SI_ADDR'
        regs[53] = 'SI_DATA'
        regs[54] = 'SI_CNT_0'
        regs[55] = 'SI_CNT_1'
        regs[56] = 'Reserved'
        regs[57] = 'Reserved'
        regs[58] = 'Reserved'
        regs[59] = 'Reserved'
        regs[60] = 'Reserved'
        regs[61] = 'Reserved'
        regs[62] = 'Reserved'
        regs[63] = 'Reserved'
        
        
        self.log.debug('Dumping Parallel FPGA Registers')
        bits = []
        for i in xrange(64):
            num = p.read(i)
            bin = int_to_bin(num, 8)
            self.log.debug('%s\t%s\t%s\t%s' % (i, p.read(i), bin, regs[i]))
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
    p = ParallelSocket()
    p.dump()
    pass
