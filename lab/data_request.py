#!/usr/bin/env python

"""
DataRequest
"""

import os
import time
import datetime

from common.base import *
from lab.dimensions import Dimensions, Dimension, DimensionValue
from lab.parameter_set import ParameterSet

from sqlalchemy.orm import mapper, relation, synonym
from orm import Session
from orm.models import data_requests_table, data_request_dimension_values_table

from lab.procedure_definition import ProcedureDefinition

DATA_REQUEST_TYPES = ['debug', 'characterization']

# TODO: Move this to the database
DES_REPOSITORY = '../product/repository/'

class DataRequest(AppBase):
    """
    Encapsulates a single data request
    """

    entity_name = 'data_request'
    entity_atts = ['type', 'subject', 'dimensions', 'execution_status', 'priority', 'deadline', 'initial_conditions', 'created_by', 'estimated_completion_date']

    @classmethod
    def find(cls, id):
        """Returns a DataRequest instance with the coresponding id or None if one does not exist."""
        dbs = Session()
        obj = dbs.query(cls).get(id)
        dbs.close()
        return obj

    def __init__(self):
        """
        If an id is not provided, a new DataRequest instance is created. 
        If an id is provided, a DataRequest instance using data from the database.
        """

        # Prepare Logger
        super(DataRequest, self).__init__()

        self._dimensions                = Dimensions() # TODO: Move dimension value storage out of validation object
        self._initial_conditions        = None
        self._created_by                = None # TODO: Populate from identity system???
        self._execution_status          = -1
        self._estimated_completion_date = None


    # Persisted attributes ------------------------------------------

    @property
    def id(self):
        """Returns the primary key of the record."""
        return self._id

    @rw_property
    def type(self):
        """Sets or retrieves the type of data request this is."""
        def fget(self):
            return self._type
        def fset(self, type):
            type = type.lower()
            if type in DATA_REQUEST_TYPES:        
                self._type = type
        def fdel(self):
            self._type = None

    @rw_property
    def subject(self):
        """Sets or retrieves the device that is to be tested."""
        def fget(self):
            return self._subject
        def fset(self, subject):
            if self._validate_subject(subject):        
                self._subject = subject
        def fdel(self):
            self._subject = None

    def _validate_subject(self, subject):
        """Verifies that the subject specified exists in the repository."""
        des_path = exepath('%s/DES_%s.txt' % (DES_REPOSITORY, subject))
        if not os.path.exists(des_path):
            raise LookupError('Invalid test subject. The following poduct DES file could not be found: %s' % des_path)
            return False
        else:
            return True

    @rw_property
    def priority(self):
        """Sets or retrieves the numeric priority of this data request."""
        def fget(self):
            return self._priority
        def fset(self, priority):
            # TODO: Validate user permission
            if priority < 0:
                raise ValueError('Priority (%s) is invalid. Value must be greater than 0.' % priority)
            else:
                self._priority = priority
        def fdel(self):
            self._priority = 0

    @rw_property
    def deadline(self):
        """Sets or retrieves the date (in YYYY-mm-dd format) by which this data request should be completed."""
        def fget(self):
            return self._deadline # .strftime('%Y-%m-%d')
        def fset(self, deadline):
            # TODO: Validate user permission
            deadline = datetime.datetime(*time.strptime(deadline, '%Y-%m-%d')[0:5])
            today = datetime.datetime.today()
            if deadline <= today:
                raise ValueError("Deadline '%s' is invalid. Date must be after current date (%s)." % (deadline, today))
            self._deadline = deadline.strftime('%Y-%m-%d')
        def fdel(self):
            self._deadline = None

    @rw_property
    def created_by(self):
        """Returns the LDAP id of the user who created this request."""
        def fget(self):
            return self._created_by
        def fset(self, ad_user):
            self._created_by = ad_user
        def fdel(self):
            self._created_by = None

    @property
    def created_at(self):
        """Returns the date this request was first created."""
        return self._created_at

    @property
    def updated_at(self):
        """Returns the date this request was last modified on."""
        return self._created_at

    @property
    def estimated_completion_date(self):
        """Returns the estimated completion date of this request."""
        return self._estimated_completion_date


    # Delegated attributes ------------------------------------------


    @rw_property
    def dimensions(self):
        """Sets or returns the dimension which the subject will be tested through."""
        def fget(self):
            # Lazy load dimensions
            if not hasattr(self, '_dimensions'):
                d = {}
                for dv in self._stored_dims:
                    v = d.get(dv.dimension.name, [])
                    v.append(dv.value)
                    d[dv.dimension.name] = v
                self._dimensions = Dimensions(d)
            # Return value after loading
            return self._dimensions.value        
        def fset(self, dim_dictionary):
            if not hasattr(self, '_dimensions'):
                self._dimensions = Dimensions(dim_dictionary)
            else:
                self._dimensions.value = dim_dictionary
        def fdel(self):
            self._dimensions.reset()

    @rw_property
    def test(self):
        """Sets or retrieves the name of the test or specification which the subject will be tested against."""
        def fget(self):
            return self._test
        def fset(self, test):
            # TODO: Determine if this is a spec or test request
            if self._validate_test(test):        
                self._test = test
        def fdel(self):
            self._test = None

    def _validate_test(self, test):
        """Verifies that the test is valid and exists in the repository."""
        dbs = Session()
        dbs.query(ProcedureDefinition).filter_by(name=test).all()        
        dbs.close()
        return True

    @rw_property
    def initial_conditions(self):
        """Sets or retrieves the user initial conditions which will overide any subject or spec inital conditions."""
        def fget(self):
            return eval(self._initial_conditions)
        def fset(self, conditions):
            # Check to see if it's a file path            
            if isinstance(conditions, str):
                if os.path.exists(conditions):
                    # Translate conditions from file to a dict
                    conditions = ParameterSet.read_param_file(conditions)
                else:
                    raise ValueError("Condition file does not exist at: %s" % conditions)
            elif not isinstance(conditions, dict):
                raise ValueError("Value for initial_conditions must be a valid file path or a dictionary. Unrecognized condition input type: %s" % conditions)
            
            # Validate and save conditions    
            self._initial_conditions = str(conditions)
            
        def fdel(self):
            self._conditions = None


    # Management Methods ------------------------------------------


    def store(self):
        """
        Saves the DataRequest as a draft without submiting it to the lab for fulfillment.
        """
        #self.log.debug('Storing DataRequest')
        dbs = Session()
        # Start Transaction
        
        # Dimensions
        # Get dimension reference
        dim_values = {}
        values = dbs.query(DimensionValue)
        for dv in dbs.query(DimensionValue):
            #print '(%s) %s = %s' % (dv.id, dv.dimension.name, dv.value)
            dim_values['%s_%s' %(dv.dimension.name, dv.value)] = dv

        # Remove current dimensions       
        self._stored_dims = []
        
        # Load dimensions
        for dim in self.dimensions:
            for value in self.dimensions[dim]:
                #print 'adding: %s_%s' %(dim, value)
                self._stored_dims.append(dim_values['%s_%s' %(dim, value)])

        dbs.save_or_update(self)
        
        # End Transaction
        dbs.commit()
        
        # Return scheudle
        dbs.close()

    def is_valid(self):
        """
        Checks the state of the data request and returns True or False 
        reflecting whether or not it has enough information to be submited.
        """
        # Check required Data Request conditions
        # Check for duplicates in the system
        return True

    def estimate(self):
        """
        Checks the status of the lab queue and returns an estimate of the 
        amount of time it will take to execute the test request.
        """
        self.store()
        # Validate Data Request
        # Send to queue
        # Return scheudle

    def submit(self):
        """
        Submits the Data Request to the lab for fulfillment. Returns a manifest
        of the data request elements with a coresponding estimate of the execution time.
        """
        self.log.debug('Submiting DataRequest to database')
        self.store()
        # Validate Data Request
        
        # Send to queue
        
        
        
        # Return scheudle

    @property
    def execution_status(self):
        """Returns the execution status of this request."""
        return self._execution_status

    def cancel(self):
        """
        Cancels the Data Request identified by the ID provided.
        """
        # Get request details
        # Present request details
        # Request verification of cancelation
        # Perform cancelation

    def delete(self):
        """
        Member method that deletes the Data Request instance.
        """
        #self.log.debug('Deleteing DataRequest')
        dbs = Session()
        obj = dbs.query(self.__class__).get(self.id)
        dbs.delete(obj)
        dbs.commit()
        dbs.close()


# Create the ORM map
props = {
         '_stored_dims' : relation(DimensionValue, secondary = data_request_dimension_values_table, lazy=False),
         '_initial_conditions' : relation(DimensionValue, secondary = data_request_dimension_values_table, lazy=False),
         }
props.update(dict([(col.key, synonym('_'+col.key)) for col in data_requests_table.c]))
mapper(DataRequest, data_requests_table, 
    column_prefix = '_', 
    properties = props
)

if __name__ == '__main__':

    #dbs = Session()
    #values = dbs.query(DimensionValue)

    #print values
    #dim_values = {}
    #for dim_value in dbs.query(DimensionValue):
    #    print '(%s) %s = %s' % (dim_value.id, dim_value.name, dim_value.value)
    #    dim_values['%s_%s' %(dim_value.name, dim_value.value)] = dim_value

    #dbs.close()
    pass

