#!/usr/bin/env python

"""
Tests Dimensions
"""

from unittest import TestCase, main
from lab.dimensions import Dimensions

class DimensionsTests(TestCase):
    """Tests of the Dimensions class."""

    def test_valid_creation(self):
        """Create valid Dimensions"""
        d = Dimensions()
        d['t'] = ['c','h']
        
        # Verify value standardization
        self.assertEqual(d['t'], ['cold', 'hot'])
        
        # Verify defaults load when nothing else has been 
        self.assertEqual(d['p'], ['typical'])
        self.assertEqual(d['v'], ['typical'])
        
        # Verify default injection
        d['t'] = []
        self.assertEqual(d['t'], ['ambient'])

        # Verify single value string assignement
        d['t'] = 'h'
        self.assertEqual(d['t'], ['hot'])

    def test_reset(self):
        """Test reset"""
        d = Dimensions()
        d['t'] = ['c','h']
        
        # Verify value standardization
        self.assertEqual(d['t'], ['cold', 'hot'])
        
        # Reset should push all values back to defaults
        d.reset()
        
        # Verify defaults load when nothing else has been
        self.assertEqual(d['p'], ['typical'])
        self.assertEqual(d['v'], ['typical'])
        self.assertEqual(d['t'], ['ambient'])

    def test_value_assignment(self):
        """Value property assignement"""
        d = Dimensions()
        d.value = {'t':['c','h'], 'p':'s'}

        v = d.value
        self.assertEqual(v['processes'], ['slow'])
        self.assertEqual(v['voltages'], ['typical'])
        self.assertEqual(v['temperatures'], ['cold', 'hot'])

    def test_invalid_assignment(self):
        """Apply invalid values and dimensions"""
        d = Dimensions()
        
        # Invalid dim
        try:
            d['x'] = ['c','h']
        except ValueError:
            pass
        else:
            self.fail('ValueError not raised.')
        
        # Invalid value
        try:
            d['t'] = ['c','hh']
        except ValueError:
            pass
        else:
            self.fail('ValueError not raised.')

        

if __name__ == '__main__':
    main()