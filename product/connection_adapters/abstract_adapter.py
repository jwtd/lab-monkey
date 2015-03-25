#!/usr/bin/env python

"""
Abstract Connection Adapter class

    Connection Adapters abstract the mechanisim by which a particular protocol
    accomplish the population of one or more virtual state buffers
    
    Serial and Parallel:
        The FPGA uses two memory buffers as a temporary swap space when 
        pushing and pulling data from any number of orientations on the test chip.
        
    USB:
        The USB device loops reads over and over to constantly monitor
        the state of the SCRs and to provide a clock ????
"""

from common.base import *

class AbstractAdapter(AppBase):
    """
    Connection Adapters exposes a unifrom I/O API by which serial control registers can be manged
    
    prepare  PC -> Gate In
    check    PC <- Gate In
    commit         Gate In  -> DUT
    set      PC -> Gate -> DUT
    
    refresh        Gate Out <- DUT
    inspect  PC <- Gate Out
    get      PC <- Gate <- DUT
    
    """

    entity_name = 'abstract_adapter'
    entity_atts = []

    def __init__(self):
        # Prepare Parent
        super(AbstractAdapter, self).__init__()
        
        self._type         = 'Abstract'
        self._connected    = False
        self._scr_sessions = {}       

    def __str__(self):
        """Returns a dictionary containing information about this package."""
        return '%s (%s)' % (self._type, self.state)

    def __getitem__(self, session_label):
        """Returns a reference to the SCR session matching the label provided"""       
        if session_label in self._scr_sessions.keys():
            return self._scr_sessions[session_label]
        else:
            return None

    @property
    def type(self):
        """Returns the type of connection this is."""
        return self._type
    
   
    # Connection Management -----------------------------------
    
    
    @staticmethod
    def detect():
        """Sniffs environment and returns true if the connection is found, false if not"""
        raise NotImplementedError()

    def connect(self, package):
        """Creates a new session for each SCR in the package"""
        raise NotImplementedError()
        #for scr in package:
        #    self._scr_sessions[scr.label] = SerialControlRegisterSession(scr)

    @property
    def state(self):
        """Returns the connection state of the protocol."""
        raise NotImplementedError()

    def log_adapter_state(self):
        """
        Writes out the complete state of the adapter to the log
        """
        raise NotImplementedError()

    @property
    def connected(self):
        """Returns the connection state of the protocol."""
        return self._connected


    # Configuration Delegation Hooks ---------------------------------


    def set_clock_source(self, target, source):
        """
        Sets the clock source for this SCR:
        source :    sma      = Take clock source from SMA connector
                    internal = Take clock source from internal clock
                    stop     = No clock source
        """
        raise NotImplementedError()
 
 
    # Package, SCR, Block, Register API Hooks -------------------------


    # Input Management
    
    
    def prepare(self, target, global_index, value):
        """
        Writes the value provided at the index in the gate's input buffer, but does not commit it
            PC -> Gate Input
        """
        raise NotImplementedError()
    

    def check(self, target, global_extents):
        """
        Returns the prepared value at the index provided from the gate's input buffer
            PC <- Gate Input
        """
        raise NotImplementedError()


    def clear(self, target, global_extents):
        """
        Throws away all of the prepared value sets
        """
        raise NotImplementedError()


    def commit(self, target, global_extents):
        """
        Sends the value at the index specified from the gate's input buffer into the device 
            Gate Input -> DUT
        """
        raise NotImplementedError()


    def set(self, target, global_index, value):
        """
        Immediately sets the data at the index specified in the device (equivalent to a prepare + commit)
            PC -> Gate -> DUT
        """
        raise NotImplementedError()
    

    # Output Management


    def refresh(self, target):
        """
        Populates the gate's output buffer with data from the device        
            Gate Output <- DUT
        """
        raise NotImplementedError()
    
    
    def inspect(self, target, global_extents):
        """
        Prepares to return the data at the index specified from the gate's output buffer
            PC <- Gate Out
        """
        raise NotImplementedError()
    

    def get(self, target, global_extents):
        """
        Immediately returns the data at the index specified from the device (equivalent to a refresh + inspect)
            PC <- Gate <- DUT
        """
        raise NotImplementedError()
 



class SerialControlRegisterSession(AppBase):
    """
    An SCR session withing the adapter
    
    Prepared values are sent to the gates input buffer, but may be set aside 
    temporarily by a scoped commit (dut.top.lane_1.commit vs dut.commit). The 
    actual state of the gate is stored in the adapters _gated variable
    """
    def __init__(self, scr):
        # Prepare Parent
        super(SerialControlRegisterSession, self).__init__()

        self._scr      = scr
        self._default  = list(scr.default)
        self.sent      = [None for i in range(scr.width)]
        self.prepared  = [None for i in range(scr.width)]
        self.retrieved = [None for i in range(scr.width)]

    @property
    def label(self):
        """Returns a reference to the SCR"""
        return self._scr.label

    @property
    def scr(self):
        """Returns a reference to the SCR"""
        return self._scr
    
    @property
    def default(self):
        """Returns the default value of the SCR"""
        return self._default

    @property
    def value(self):
        """Returns the most recently sent value or the default value if the SCR has not been sent"""
        if self.sent[0] != None:
            return self.sent
        else:
            return self._default

    def erase(self):
        """Resets the sent, prepared, and retrieved values to None"""
        self.sent      = [None for i in range(self._scr.width)]
        self.prepared  = [None for i in range(self._scr.width)]
        self.retrieved = [None for i in range(self._scr.width)]

    def inspect(self, start=0, end=None):
        """Writes the session state for the range provided to the log"""
        if end == None: end = len(self._default)
        self.log.debug('D: %s\nS: %s\nP: %s\nR: %s' % (self._default[start:end], self.sent[start:end], self.prepared[start:end], self.retrieved[start:end]))

if __name__=='__main__' :
    pass
    
