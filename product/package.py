#!/usr/bin/env python

"""
StatelessPackageF
"""

from common.base import *
from product.register import *
from product.register_collection import *
from product.serial_control_register import *
from product.connection_adapters.connection_adapter_factory import *

class Package(AppBase):
    """
    A Package represents a test chip, which holds one or more orientations. 
    Instances of the Package object are the top level API for interacting with a chip
    Orientations can be accessed via brackets or via the lable as a method signature.
    Example:
    
    dut = Package.from_txt_file('DES_Fuji_MODIFIED.txt')
    
    # All of the following are equivalent references to the sequence attribute of the orientation labeled 'top'
    
    dut.top.sequence
    dut['top'].sequence
    dut.orientations['top'].sequence

    """

    entity_name = 'package'
    entity_atts = ['metadata', 'orientations']


    # Class Constructors -----------------------------


    # Class method Constructors
    # TODO: Create load from repository   
    @classmethod
    def from_xml(cls, xml):
        """Constructor which initalizes a Package instance from raw XML"""
        #TODO: from_xml Constructor
        pass

    @classmethod
    def from_txt_file(cls, filepath, connect = None, infer_enable = True):
        """
        Constructor which initalizes a Package instance from a plain text DES file
        """

        # Get the data from the file and close ASAP
        f = open(filepath)
        try:
            lines = []
            for line in f:
                lines.append(line.strip().split('\t'))
        finally:
            f.close()

        # Create temporary storage collections
        identification         = {}
        block_orientations     = {}
        constants              = {}
        limits                 = {}
        levels                 = {}
        common_block_registers = []
        lane_registers         = []

        # Read through the lines
        i=0
        while i < len(lines):
            if lines[i][0] == 'ID':
                identification[lines[i][1].lower()] = lines[i][2].strip()
            elif lines[i][0] == 'LIMIT':
                limits[lines[i][1]] = lines[i][2].strip()
            elif lines[i][0] == 'LEVEL':
                levels[lines[i][1]] = lines[i][2].strip()
            elif lines[i][0] == 'ORIENTATION':
                block_orientations[lines[i][1]] = lines[i][2].strip()
            elif lines[i][0] == 'CONSTANT':
                constants[lines[i][1]] = lines[i][2].strip().upper()
            elif lines[i][0] == 'NAME':
                
                # Multiline data structure collection
                reg_name         = lines[i][1].strip()
                reg_width        = lines[i+1][1].strip()
                reg_default      = lines[i+2][1].strip()
                reg_parent       = lines[i+3][1].strip()
                reg_direction    = lines[i+4][1].strip()
                reg_start_index  = lines[i+5][1].strip()
                reg_enable_index = lines[i+6][1].strip()
                #reg_group        = lines[i+7][1]    # Not used
                i += 7
                
                # Standardize int, hex, and bin, to proper length binary version
                reg_default = data_to_int(reg_default)
                reg_default = int_to_bin(reg_default, int(reg_width))
                                
                # Create and bin the register
                r = Register(reg_name, reg_direction, reg_enable_index, reg_start_index, reg_width, reg_default)
                if (reg_parent == 'C'):
                    common_block_registers.append(r)
                elif (reg_parent == 'L'):
                    lane_registers.append(r)
                else:
                    raise ValueError('Unrecognized BLOCK_TYPE specified \'%s\' for register at line %i in file %s' % (reg_parent, i, filepath))
            i+=1
            
        # Initialize self and return self
        return cls(identification, common_block_registers, lane_registers, block_orientations, constants, limits, levels, connect, infer_enable)


    # Instance Constructor -----------------------------


    def __init__(self, metadata, common_block_registers, lane_registers, block_orientations, constants = {}, limits = {}, levels = {}, connection_type = None, infer_enable = True):
        """
        Creates an instance of a Package object
        
        common_block_architype : List of registers which can be loaded into a RegisterCollection to represent the common_block in the package
        
        lane_architype : List of registers which can be loaded into a RegisterCollection to represent one of the lanes in the package
        
        block_orientations : Dictionary containing label:sequence pairs ex. {'top'='01234567X', 'bottom'='X0123'}
        NOTE that labels will be downcased (TOP:1234) will be transformed to (top:1234).

        connect = True : Whether or not to immediately search for and connect to a test board from the computer. 
        Connection is conditional to allow the package class to function as both a model and an interface

        infer_enable = True : Whether or not the action of setting a register value implicitly toggles the register's enable bit.
        """
        # Prepare Logger
        super(Package, self).__init__()
        #self.log.info('Creating Package %s' % metadata)
        
        # Identity & Metadata
        self._scale    = metadata.get('scale', None)
        self._process  = metadata.get('process', None)
        self._metadata = metadata
        
        # Save limits and constants
        self._limits = limits
        self._levels = levels
        self._register_value_aliases = constants
       
        # Build the orientations
        self._orientations = {}
        for label in block_orientations:
            label = label.lower()
            block_orientation = block_orientations[label]
            #self.log.info('Creating orientation %s: %s' % (label, block_orientation))
            o = SerialControlRegister(label, common_block_registers, lane_registers, block_orientation)
            o.package = self
            self._orientations[o.label] = o
            # Metaprogram reference to children
            append_reference(self, o.label, o)
            
        # Retrieve a connection adapter and connect if requested to do so
        self._connection = None
        if connection_type != None:
            self.connect(connection_type)
            
 
    # References -----------------------------


    def __str__(self):
        if self._scale != None and self._process != None:
            return '%s %s' % (self._scale, self._process)
        else:
            return 'Unidentified Package'

    def __len__(self):
        """Returns the number of orientations in the pacakge"""
        return len(self._orientations)

    def __getitem__(self, key):
        """Returns a reference to the block orientation specified"""
        if isinstance(key, int):
            keys = self._orientations.keys()
            return self._orientations[keys[key]]
        else:
            return self._orientations[key.lower()]

    @property
    def orientations(self):
        """Returns the scale of the manufacturing process (65nm, 90nm, etc)."""
        return self._orientations
    

    # Metadata -----------------------------


    @property
    def register_value_aliases(self):
        """Returns a collection of register value constants loaded from the DES file"""
        return self._register_value_aliases

    @property
    def limits(self):
        """
        Returns a collection of environment safety limits such as:
            avdd      power    1.4
            dvdd      power    1.4
            core_vdd  power    1.4
            avddh     power      2
        """
        return self._limits

    @property
    def levels(self):
        """
        Returns a collection of environment levels at which tests should be conducted: 
            temp      low      0
            temp      high   125
            avdd      [0.95, 1.1]
            dvdd      1
            core_vdd  1
            avddh     1
        """
        return self._levels

    @property
    def scale(self):
        """Returns the scale of the manufacturing process (65nm, 90nm, etc)."""
        return self._scale

    @property
    def process(self):
        """Returns the foundry process (TSMC, Fujitsu, etc)."""
        return self._process

    @property
    def metadata(self):
        """Returns a dictionary containing information about this package."""
        return self._metadata

    @property
    def connection(self):
        """Returns the scale of the manufacturing process (65nm, 90nm, etc)."""
        return self._connection

    @rw_property
    def autoenable(self):
        """
        Whether or not calls to set() and prepare() will automaticaly enable the 
        registers. Default is True.
        """
        def fget(self):
            result = True
            for scr in self:
                if not scr.autoenable:
                    result = False
            return result
        def fset(self, autoenable):
            if autoenable == True or autoenable == False:
                for scr in self:
                    scr.autoenable = True
            else:
                raise ValueError('Autoenable can only accept True or False as a value. %s is invalid' % autoenable)
        def fdel(self):
                for scr in self:
                    scr.autoenable = False


    # Connection management -----------------------------


    def connect(self, adapter = None):
        
        # Retrieve or switch connection adapters if requested to do so
        if self._connection == None or (adapter != None and adapter != self._connection.type):
            #try:
            self._connection = ConnectionAdapterFactory.request(adapter)
            #except LookupError, e:
            #self.log.warn(e)                
            #else:
                # TODO: Destroy old session if it existed
            #    pass
        try:
            self._connection.connect(self)
        except LookupError, e:
            msg = 'Could not connect via %s adapter: %s' % (self._connection.type, e)
            self.log.error(msg)
            raise Exception(msg)

    @property
    def connected(self):
        """Whether or not the device is connected"""
        if self._connection != None and self._connection.connected:
            return True
        else:
            return False


    # State property accessors --------------------------------------------
 

    @property
    def default(self):
        """
        Returns a dictionary containing the unifed default value of each SCR in the package
        """
        results = {}
        for scr in self:
            results[scr.label] = scr.default
        return results

    @property
    def sent(self):
        """
        Returns a dictionary containing the unifed value last sent for each SCR in the package
        """
        if self.connected:
            results = {}
            for scr in self:
                results[scr.label] = scr.sent
            return results
        else:
            return None

    @property
    def retrieved(self):
        """
        Returns a dictionary containing the unifed value last retrieved for each SCR in the package
        """
        if self.connected:
            results = {}
            for scr in self:
                results[scr.label] = scr.retrieved
            return results
        else:
            return None

    @property
    def prepared(self):
        """Returns the value which has been prepared for transmission"""
        if self.connected:
            results = {}
            for scr in self:
                results[scr.label] = scr.prepared
            return results
        else:
            return None

    @property
    def pending(self):
        """Returns a list of elements which have prepared values waiting to be sent"""
        if self.connected:
            pending = []
            for scr in self:
                pending.extend(scr.pending)
            return pending
        else:
            return None


    # Input Management --------------------------------------------


    def reset(self):
        """
        Immediately returns all registers in this collection to their default values in the device
            PC -> Gate -> DUT (DEFAULT)
        """
        if self.connected:
            for scr in self:
                scr.reset()

    def prepare(self, key, value):
        """
        Prepares to set the element identified by key within this collection to the value provided
            PC -> Gate   DUT
        """
        if self.connected:
            for scr in self:
                scr.prepare(key, value)

    def check(self, key):
        """
        Retrieves the identified register's value from the gate's input buffer
            PC <- Gate Input
        """
        if self.connected:
            results = {}
            for scr in self:
                results[scr.label] = scr.check(key)
            return results
        else:
            return None
        

    def clear(self):
        """
        Throws out the prepared value
            X -> Gate Input <- X
        """
        if self.connected:
            for scr in self:
                scr.clear()

    def commit(self):
        """
        Commits the prepared values of all element's within the SCR 
            PC    Gate -> DUT
        """
        if self.connected:
            for scr in self:
                scr.commit()

    def set(self, key, value):
        """
        Immediately sets element identified by key within this collection to the value provided at the device
            PC -> Gate -> DUT
        """
        if self.connected:
            for scr in self:
                scr.set(key, value)


    # Output Management --------------------------------------------


    def refresh(self):
        """
        Updates the gate's output buffer with fresh data from the device
            PC   Gate <- DUT
        """
        if self.connected:
            for scr in self:
                scr.refresh()
                
    def inspect(self, key):
        """
        Retrieves this registers value from the gate's output buffer
            PC <- Gate Out
        """
        if self.connected:
            results = {}
            for scr in self:
                results[scr.label] = scr.inspect(key)
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
            for scr in self:
                results[scr.label] = scr.get(key)
            return results
        else:
            return None

    # Iterator

    def __iter__(self):
        """Returns an instance of a BufferIterator for the buffer instance"""
        return PackageIterator(self, self._orientations.keys())


class PackageIterator(object):
    """A reusable iterator for a Package instance"""
    
    def __init__(self, target, orientations):
        """Creates a new PackageIterator for the Package passed in"""
        self._orientations = orientations
        self.target = target
        self.count  = -1
        
    def __iter__(self):
        return self
    
    def next(self):
        """Returns the next SCR in the Package"""
        count = self.count + 1
        self.count = count
        if count >= len(self.target):
            raise StopIteration
        return self.target[self._orientations[count]]


if __name__ == '__main__':
    #dut = Package.from_txt_file('tests/mocks/DES_65nm_Fuji.txt')
    #print dut.top.sequence
    pass

        