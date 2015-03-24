#!/usr/bin/env python

"""
Tests ParameterSet
"""

from common.tests.pyunit_helpers import exepath
from unittest import TestCase, main
from lab.parameter_set import ParameterSet

class ParameterSetTests(TestCase):
    """Tests of the ParameterSet class."""

    def test_line_parsing(self):
        """Collect parameters from a config file"""

        params = ParameterSet.read_param_file(exepath('mocks/line_tests.txt'))
        
        #print params
        #for param in params:
        #    print '%s = %s' % (param, params[param])
        
        self.assertEqual(len(params.keys()), 8)
        
        self.assertEqual(params['my param'], 123)
        self.assertEqual(params['my_param'], ['A', 'B'])
        self.assertEqual(params['MYPARAM'], {'A': 1, 'B':'Two'})
        
        self.assertEqual(params['param1'], (1,2,3))
        self.assertEqual(params['param2'], (4,5,6))
        self.assertEqual(params['param3'], (7,8,9))
        
        self.assertEqual(params['ml_param'], [[1,2,3],['a', 'b', 'c'],{'C':1,'D':'Two'}])
        
        self.assertEqual(params['My param'], 'A')
        
        
        keys = params.keys()
        
        # Skip over single line comments
        self.assertFalse('hidden_param_2' in keys)
        
        # Skip over multiline comments
        self.assertFalse('hidden_param' in keys)



    def test_section_isolation(self):
        """Collect parameters from a specific section of a config file"""
        params = ParameterSet.read_param_file(exepath('mocks/line_tests.txt'), 'Jitter Tolerance')

        self.assertEqual(len(params.keys()), 4)

        self.assertEqual(params['param1'], (1,2,3))
        self.assertEqual(params['param2'], (4,5,6))
        self.assertEqual(params['param3'], (7,8,9))
        
        self.assertEqual(params['ml_param'], [[1,2,3],['a', 'b', 'c'],{'C':1,'D':'Two'}])
       
        # Ensure others are not in collection
        keys = params.keys()
        self.assertFalse('my param' in keys)
        self.assertFalse('my_param' in keys)
        self.assertFalse('MYPARAM' in keys)
        self.assertFalse('My param' in keys) 
        self.assertFalse('hidden_param_2' in keys)
        self.assertFalse('hidden_param' in keys)


    def test_load_order_precedence(self):
        """Verify loading order precedence"""
        
        prod = exepath('mocks/65nm_product.txt')
        spec = exepath('mocks/myspec.txt')
        user = exepath('mocks/user.txt')

        set = ParameterSet(prod, spec, user)

        #params = set.keys()
        #params.sort()
        #for param in params:
        #    print '%s = %s' % (param, set[param])

        # User file should be dominant
        self.assertEqual(set['test1.var1'], 'user_1')
        self.assertEqual(set['test1.var2'], 'user_2')
        self.assertEqual(set['test1.var3'], 'user_3')
        
        # Spec file should be dominant
        self.assertEqual(set['test2.var1'], 'spec_21')
        self.assertEqual(set['test2.var2'], 'spec_22')
        self.assertEqual(set['test2.var3'], 'spec_23')
        
        # Product file should be dominant
        self.assertEqual(set['test3.var1'], 'prod_31')
        self.assertEqual(set['test3.var2'], 'prod_32')
        self.assertEqual(set['test3.var3'], 'prod_33')


    def test_determine_variable_source(self):
        """Determine variable source"""

        prod = exepath('mocks/65nm_product.txt')
        spec = exepath('mocks/myspec.txt')
        user = exepath('mocks/user.txt')

        set = ParameterSet(prod, spec, user)

        self.assertEqual(set.source('test1.var1'), ['product = prod_1', 'spec = spec_1', 'user = user_1'])
        self.assertEqual(set.source('test2.var1'), ['product = prod_21', 'spec = spec_21', 'user = None'])
        self.assertEqual(set.source('test3.var1'), ['product = prod_31', 'spec = None', 'user = None'])


if __name__ == '__main__':
    main()