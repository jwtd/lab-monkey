#!/usr/bin/env python

"""
Dimensions
"""

from common.base import *

from sqlalchemy import join
from sqlalchemy.orm import mapper, relation, synonym
from orm import Session
from orm.models import dimensions_table, dimension_values_table


# Dimension and DimensionValue ORM
class Dimension(object): pass
class DimensionValue(object): pass

mapper(Dimension, dimensions_table, 
       properties={
       'valid_values':relation(DimensionValue, lazy=False)
})
mapper(DimensionValue, dimension_values_table, 
       properties={
       'dimension':relation(Dimension, lazy=False)
})


class AliasableKey(object):
    """Class that provides flexible key matching to a standardized value"""
    def __init__(self, name, aliases = []):
        self.name    = name
        self.aliases = aliases
    
    def __eq__(self, name):
        """Operator support for == which is equivalent to .equales()."""
        return self.equales(name)
        
    def equales(self, name):
        """
        Returns True or False reflecting whether or not the key provided 
        matches the name or one of the aliases associated with it.
        """
        name = name.lower()
        if name == self.name:
            return True
        if name in self.aliases:
            return True
        else:
            return False

class Dimensions(AppBase):
    """
    Encapsulates a collection of environmental dimensions
    """

    entity_name = 'dimensions'
    entity_atts = []
    
    def __init__(self, dim_dictionary = None):
        """
        """
        # Prepare Logger
        super(Dimensions, self).__init__()
        
        self._valid_dims       = [] # Aliasable key list for matching
        self._valid_dim_data   = {} # Default, Best Case, Worst Case keyed to standardized dim name
        self._valid_dim_values = {} # List of aliasable values keyed to standardized dim name
        self._dim_values       = {} # Current instance's standardized values keyed to standardized dim name
        
        # Load data structure from database
        dbs = Session()
        for dim in dbs.query(Dimension).all():
            
            # Save the dim and it's metadata
            dim_ref = AliasableKey(dim.name, dim.name_aliases.split(','))
            self._valid_dims.append(dim_ref)
            self._valid_dim_data[dim.name] = {'default':None, 'best_worst':dim.best_worst, 'weigth':dim.weight}
           
            # Prepare to store the valid values
            self._valid_dim_values[dim.name] = []
            for value in dim.valid_values:
                
                value_ref = AliasableKey(value.value, value.value_aliases.split(','))
                self._valid_dim_values[dim.name].append(value_ref)
                if value.default:
                    self._valid_dim_data[dim.name]['default'] = value.value

            self._dim_values[dim.name] = [self._valid_dim_data[dim.name]['default']]
                    
        # Close the session
        dbs.close()
        
        # Load the inital value if provided
        if dim_dictionary:
            self.value = dim_dictionary

    @rw_property
    def value(self):
        """Returns a dictionary containing the values of all the dimensions."""
        def fget(self):
            return self._dim_values
        def fset(self, dim_dictionary):
            for dim, value in dim_dictionary.items():
                self[dim] = value            
        def fdel(self):
            raise ValueError("Dimension value can not be deleted.")

    def __repr__(self):
        return str(self._dim_values)

    def __setitem__(self, dim, values):
        """Assigns the specificed dimension with the one or more values provided."""
        # Validate dimension
        invalid = True
        for dim_ref in self._valid_dims:
            if dim_ref == dim:
                dim = dim_ref.name
                invalid = False
        if invalid:
            raise ValueError("Dimension '%s' is not recognized." % dim)

        # Ensure we have a list
        if isinstance(values, str):
            values = [values]

        # Validate values supplied for dimension
        if values == []:
            # If no value provided, set to default
            self._dim_values[dim] = [self._valid_dim_data[dim]['default']]
        else:           
            # Reset and rebuild the dimension value list
            self._dim_values[dim] = []
            for value in values:
                invalid = True
                for value_ref in self._valid_dim_values[dim]:
                    if value_ref.equales(value):
                        # Dim and value are valid and standardized
                        if value_ref.name not in self._dim_values[dim]:
                            self._dim_values[dim].append(value_ref.name)
                        invalid = False
                if invalid:
                    raise ValueError("Value '%s' is not valid for '%s' dimension." % (value, dim))
            
        # Sort for consistency
        self._dim_values[dim].sort()

    def __getitem__(self, dim):
        """Returns the values associated with the dimension."""
        # Validate dimension
        invalid = True
        for dim_ref in self._valid_dims:
            if dim_ref.equales(dim):
                dim = dim_ref.name
                invalid = False
        if invalid:
            raise ValueError("Dimension '%s' is not recognized." % dim)
        
        # Return value for valid dim
        return self._dim_values[dim]

    def reset(self):
        """Resets all dimension values to their default values."""
        for dim in self._valid_dims:
            self._dim_values[dim.name] = [self._valid_dim_data[dim.name]['default']]
                
if __name__ == '__main__':

    #d = Dimensions()
    #d['t'] = ['c','h']
    #print d['p']
    #print d['v']
    #print d['t']

    #print 'd[t]: %s' % d['t']
    #print 'd.value: %s' % d.value
    #print 'repr(d): %s' % repr(d)

    pass
