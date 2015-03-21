#!/usr/bin/env python

"""
StationManager
"""

import socket

from common.base import *
from common.insensitive_dict import InsensitiveDict
from io_ports.io_port_visa import VisaSocket
from product.package import *
from equipment.device_instance_factory import *

DES_REPOSITORY = '../product/repository/'

class StationManager(object):
    """
    Controls the activities of a station.
    """

    entity_name = 'station_manager'
    entity_atts = ['label', 'address', 'devices']

    def __new__(cls, *p, **k):
        """Forces StationManger to act as Singleton."""
        if not '_single_instance' in cls.__dict__:
            cls._single_instance = object.__new__(cls)
            
            # Get network properties
            np = socket.gethostbyaddr(socket.gethostname())
            cls._single_instance._network_id = np[0]
            cls._single_instance._ip_address = np[-1][0]

            # Setup the equipment            
            cls._single_instance.connect_to_equipment()
            
        return cls._single_instance

        
    def retrieve_test(self):
        """Retrieves the next test from the lab manager."""
        pass

    def __getitem__(self, key):
        """
        'Device Under Test' will return the dut currently loaded on the bench.
        Any other key will trigger a search of the environment variables and 
        the attached devices. If found, a reference to the object is returned.
        """
        if key.upper() == 'DEVICE UNDER TEST':
            return self._dut
        elif self._env_variable_map.has_key(key):
            # return self._env_variable_map[key]
            return self._get_env_variable(key)
        elif self.devices.has_key(key):
            return self.devices[key]['instance']
        else:
            raise LookupError('Unrecognized bench asset requested: %s' % key)        

    def __str__(self):
        """Returns the stations label, network id, and ip address"""
        return '%s : %s (%s)' % (self.label, self.network_id, self.ip_address)

    @property
    def label(self):
        """Returns the label which identifies this station."""
        return self._label

    @property
    def ip_address(self):
        """Returns the network ip address of the computer that manages this station."""
        return self._ip_address

    @property
    def network_id(self):
        """Returns the network hostname of the computer that manages this station."""
        return self._network_id

    def initialize_dut(self, product_id):
        """Initializes a package from the product_id."""
        # TODO: Move this into central database       
        des_path = exepath('%s/DES_%s.txt' % (DES_REPOSITORY, product_id))
        if not os.path.exists(des_path):
            raise LookupError('Poduct DES file not found: %s' % des_path)
        else:
            self._dut = Package.from_txt_file(des_path, self._adapter)
            #self._dut.connect(self._adapter)
            
            for var in self._dut.limits:
                # TODO: Add way to limit current and other properties
                #device_key, device_pointer = self._env_variable_map[var]
                #self._devices[device_key]['instance'][device_pointer].max_voltage = self._dut.limits[var]
                self._set_env_variable(var, self._dut.limits[var])

            for var in self._dut.levels:
                # TODO: Add way to set current and other properties
                #device_key, device_pointer = self._env_variable_map[var]
                #self._devices[device_key]['instance'][device_pointer].voltage = self._dut.levels[var]
                self._set_env_variable(var, self._dut.levels[var])

    @property
    def dut(self):
        """Returns a reference to the currently initalized device under test."""
        return self._dut

    def connect_to_equipment(self):
        """Gets a list of all the equipment attached to the station."""
        
        # Load initial list from status file
        xml = xml_as_obj(exepath('station_setup_%s.xml' % self.ip_address))

        self._label   = xml.label.PCDATA
        self._adapter = xml.adapter.PCDATA

        self._devices = InsensitiveDict()
        self._env_variable_map = InsensitiveDict()      
        for device in xml.devices.device:
            manufacturer = device.manufacturer.PCDATA
            model        = device.model.PCDATA
            address      = device.address.PCDATA
            part_code    = device.part_code.PCDATA
            device_key   = '%s %s' % (manufacturer, model)
            instance     = DeviceInstanceFactory.request(device_key)
            
            # Use an explicit identifer when more than one 
            # device of the same make and model is present
            if hasattr(device, 'identifier'):
                identifier = device.identifier.PCDATA
            else:
                identifier = device_key
            
            # Store environment variable pointers
            if hasattr(device, 'env_variable'):
                for env_var in device.env_variable:
                    name           = env_var.name.PCDATA
                    device_pointer = env_var.device_pointer.PCDATA
                    property       = env_var.property.PCDATA
                    #self._env_variable_map[name] = (identifier, device_pointer, property)
                    self._env_variable_map[name] = (identifier, instance[device_pointer], property)
            
            # Store the device
            self._devices[identifier] = {'address' : address, 'manufacturer' : manufacturer, 'model' : model, 'part_code' : part_code, 'instance': instance}
            print 'Device loaded: %s is a %s' % (device_key, instance)

        # Verify network connections
        #self.check_equipment_connections()

        # Get an instance of the device and connect to it
        if not VisaSocket.detect():
            print 'VISA network was not detected.'
        else:
            for device_key in self._devices:
                # TODO: Only connect to device if found on the network
                self._devices[device_key]['instance'].connect(self._devices[device_key]['address'])
                
    @property
    def connected(self):
        """Returns True or False reflecting whether the station has connected to the equipment."""
        c = True
        for device_key in self._devices:
            if not self._devices[device_key]['instance'].connected:
                c = False
                break
        return c
    
    @property
    def devices(self):
        """Returns a collection of the devices connected to this station."""
        return self._devices

    def has_device(self, device_key):
        """Returns True or False reflecting whether or not the device key exists on the bench."""
        return self._devices.has_key(device_key)
    
    @property
    def env_variable_equipment_map(self):
        """
        Returns a dictionary that contains the bench's environment variables as keys to 
        a string identifying the devices that manage them.
        """
        map = {}
        for var in self._env_variable_map:
            #device_key, device_pointer = self._env_variable_map[var]
            #hook = self._devices[device_key][device_pointer]
            #map[var] = '%s of %s at %s' % (hook.label, hook.owner, hook.address)
            device_key, device_pointer, property = self._env_variable_map[var]
            map[var] = '%s of %s' % (device_pointer.label, device_key)
        return map

    @property
    def env_variables(self):
        """
        Returns a dictionary that contains the bench's environment variables as keys to the values.
        """
        map = {}
        for var in self._env_variable_map:
            device_key, device_pointer, property = self._env_variable_map[var]
            map[var] = getattr(device_pointer, property)
        return map

    def _set_env_variable(self, var, value):
        device_key, device_pointer, property = self._env_variable_map[var]
        setattr(device_pointer, property, value)

    def _get_env_variable(self, var):
        device_key, device_pointer, property = self._env_variable_map[var]
        return getattr(device_pointer, property)


    def check_equipment_connections(self):
        """Interogates the network addresses of the devices that are supposed to be attached to the station"""
        # Query network devices to confirm setup
        detected_equipment = VisaSocket.identify_attached_visa_devices()

        # Verify attached equipment ID's match inventory file
        for address in detected_equipment:
            print '%s %s' % (address, detected_equipment[address])
            # GPIB0::23 {'manufacturer': 'Agilent Technologies', 'model': 'E3631A',   'part_code': '0'}
            # GPIB0::2  {'manufacturer': 'Agilent Technologies', 'model': 'E3631A',   'part_code': '0'}
            # GPIB0::1  {'manufacturer': 'Agilent Technologies', 'model': 'E3648A',   'part_code': '0'}
            # GPIB0::12 {'manufacturer': 'Agilent Technologies', 'model': '81134A',   'part_code': 'DE42800167'}
            # GPIB0::11 {'manufacturer': 'Keithley Instruments', 'model': '2400',     'part_code': '0824122'}
            # GPIB0::9  {'manufacturer': 'TEMPTRONIC',           'model': 'TP04300A', 'part_code': '4000'}


if __name__ == '__main__':
    #sm1 = StationManager()
    #sm2 = StationManager()
    #print '%s = %s' % (id(sm1),id(sm2))
    pass    
    
    