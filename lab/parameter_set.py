#!/usr/bin/env python

"""
ParameterSet
"""

import re

SECTION_RE = re.compile('[ \t]*-{3,}[ \t]*(.*?)[ \t]*-{3,}[ \t]*')
COMMENT_RE = re.compile('^[ \t]*(\#|/\*.*|.*\*/)')
KEY_VALUE_RE = re.compile(r'([\w\. _-]+)\s*=\s*(.*)', re.IGNORECASE) 

CONFIG_PRECEDENCE = ['product', 'spec', 'user']

class ParameterSet(dict):

    def __init__(self, prod = None, spec = None, user = None, section = None):
        
        self._sets = {}
        self._sets['product'] = ParameterSet.read_param_file(prod, section)
        self._sets['spec']    = ParameterSet.read_param_file(spec, section)
        self._sets['user']    = ParameterSet.read_param_file(user, section)
        
        self._params = {}
        for config in CONFIG_PRECEDENCE:
            self._params.update(self._sets[config])

    @property
    def product_params(self):
        return self._sets['product']
    
    @property
    def spec_params(self):
        return self._sets['spec']
    
    @property
    def user_params(self):
        return self._sets['user']

    def __getitem__(self, key):
        return self._params[key]

    def source(self, key):
        """
        Returns the path by which the key provided had it's value
        determined through the series of configuration steps.
        """
        value = []
        for config in CONFIG_PRECEDENCE:
            value.append('%s = %s' % (config, self._sets[config].get(key,None)))
        return value

    @staticmethod
    def read_param_file(filepath, section = None):
        """Opens a text file and saves the input."""
        params = {}
        file = open(filepath, 'r')
        try:
            comment = False
            cv      = None
            key     = None
            value   = None
            cur_sec = 'DEFAULT'
            
            if section != None:
                section = section.upper()
            
            # Loop over each line
            for line in file:

                # Look for the section
                s = re.search(SECTION_RE, line)
                if s:
                    cur_sec = s.group(1).strip().upper()
                    continue

                if section == None or section == cur_sec:
                    
                    # Look for comments
                    c = re.search(COMMENT_RE, line)
                    if c:
                        cv = c.group(1).strip()
                        if '/*' in cv:
                            comment = True
                        elif '*/' in cv:
                            comment = False
                        continue
                    
                    # If not a comment, look for key / values
                    if not comment:
                        kv = re.search(KEY_VALUE_RE, line)
                        if kv and line.strip() != '':
                            # If new key is found store current key / value
                            if key:
                                params[key] = eval(value)
                            # Begin compiling next ky / value
                            key   = kv.group(1).strip()
                            value = kv.group(2).strip()
                        else:
                            # No key on this line, so append line to current value
                            value = '%s%s' % (value, line.strip())

            # Add final param
            if key:
                params[key] = eval(value)
            
        finally:
            file.close()

        return params


    def has_key(self, key):
        return self._params.has_key(key)
    
    def keys(self):
        return self._params.keys()

    def values(self):
        return self._params.values()

    def items(self):
        return self._params.items()

    def __iter__(self):
        return self._params.iterkeys()
    
    def iterkeys(self):
        return self._params.iterkeys()
    
    def iteritems(self):
        return self._params.iteritems()
    
    def itervalues(self):
        return self._params.itervalues()


if __name__ == '__main__':

    prod = 'parameters/products/65nm_fujitsu.txt'
    spec = 'parameters/specs/pci2.txt'
    user = 'parameters/user.txt'

    set = ParameterSet(prod, spec, user, 'Jitter Tolerance')

    #params = ParameterSet.read_param_file('specs/line_test.txt', 'Jitter Tolerance')
    #for param in params:
    #    print '%s = %s' % (param, params[param])

    params = set.keys()
    params.sort()
    for param in params:
        print '%s = %s' % (param, set[param])

    print set.source('test2.var2')

