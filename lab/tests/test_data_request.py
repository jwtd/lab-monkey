#!/usr/bin/env python

"""
Tests DataRequest
"""

from common.tests.pyunit_helpers import exepath
from unittest import TestCase, main
from lab.data_request import DataRequest

import time
import datetime

class DataRequestTests(TestCase):
    """Tests of the DataRequest class."""

    def x_test_valid_creation(self):
        """Create valid DataRequests"""
        dr = DataRequest()
        dr.created_by = 'aduser01'
        dr.type       = 'Debug'
        dr.subject    = '65nm_Fuji'
        dr.priority   = 2
        dr.deadline   = '2011-01-01'
        dr.test       = 'Jitter Generation'
        dr.dimensions = {'t':['H', 'A', 'C']}
        dr.initial_conditions = {'Some Param':'My Value'}

        self.assertEqual(dr.created_by, 'aduser01')
        self.assertEqual(dr.type, 'debug')
        self.assertEqual(dr.subject, '65nm_Fuji')
        self.assertEqual(dr.execution_status, -1)
        self.assertEqual(dr.priority, 2)
        self.assertEqual(dr.deadline, '2011-01-01')
        self.assertEqual(dr.estimated_completion_date, None)
        self.assertEqual(dr.dimensions, {'processes': ['typical'], 'temperatures': ['ambient', 'cold', 'hot'], 'voltages': ['typical']})
        self.assertEqual(dr.initial_conditions, {'Some Param':'My Value'})

        # Not saved yet, so dates are empty
        self.assertEqual(dr.created_at, None)
        self.assertEqual(dr.updated_at, None)

        # Save to the database and recheck values
        dr.store()

        # After saving, verify that dates were saved
        today = datetime.datetime.today().strftime('%Y-%m-%d %H:%M')
        ca = datetime.datetime(*time.strptime(dr.created_at, '%Y-%m-%d %H:%M:%S')[0:5]).strftime('%Y-%m-%d %H:%M')
        ua = datetime.datetime(*time.strptime(dr.updated_at, '%Y-%m-%d %H:%M:%S')[0:5]).strftime('%Y-%m-%d %H:%M')
        self.assertEqual(ca, today)
        self.assertEqual(ua, today)

        # Verify new record identity
        new_id = dr.id
        self.assertTrue(new_id != None)
        
        # Delete and verify
        dr.delete()
        drs = DataRequest.find(new_id)
        self.assertTrue(drs == None)

    def x_test_initial_conditions(self):
        """Set initial conditions using dictionary and file"""
        dr = DataRequest()
        dr.created_by = 'aduser01'
        dr.type       = 'Debug'
        dr.subject    = '65nm_Fuji'
        dr.priority   = 2
        dr.deadline   = '2011-01-01'
        dr.test       = 'Jitter Generation'
        dr.initial_conditions = exepath('mocks/user.txt')
        
        expecting = {'test1.var2': 'user_2', 'test1.var3': 'user_3', 'test1.var1': 'user_1'}
        self.assertEqual(dr.initial_conditions, expecting)

        dr.store()
        record_id = dr.id

        # Get new instance and verify dimensions
        dr2 = DataRequest().find(record_id)        
        self.assertEqual(dr2.initial_conditions, expecting)

        
    def test_dimension_manipulation(self):
        """Dimension Manipulation"""
        dr = DataRequest()
        dr.created_by = 'aduser01'
        dr.type       = 'Debug'
        dr.subject    = '65nm_Fuji'
        dr.priority   = 2
        dr.deadline   = '2011-01-01'
        dr.test       = 'Jitter Generation'
        dr.dimensions = {'t':['H', 'A', 'C']}
        #dr.initial_conditions = {'Some Param':'My Value'}
        
        dr.store()
        record_id = dr.id

        # Verify Dimensions
        self.assertEqual(dr.dimensions, {'processes': ['typical'], 'temperatures': ['ambient', 'cold', 'hot'], 'voltages': ['typical']})

        # Get new instance and verify dimensions
        dr2 = DataRequest().find(record_id)
        self.assertEqual(dr2.dimensions, {'processes': ['typical'], 'temperatures': ['ambient', 'cold', 'hot'], 'voltages': ['typical']})

        # Change dimensions and save
        dr2.dimensions = {'processes': ['f', 'typical'], 'temperatures': ['ambient'], 'voltages': ['h', 'l']}
        dr2.store()

        # Get new instance and verify change of dimensions
        dr2 = DataRequest().find(record_id)
        self.assertEqual(dr2.dimensions, {'processes': ['fast', 'typical'], 'temperatures': ['ambient'], 'voltages': ['high', 'low']})

    def x_test_invalid_creation(self):
        """Create invalid DataRequests"""
        dr = DataRequest()
        # Invalid priority
        try:
            dr.priority = -1
        except ValueError:
            pass
        else:
            self.fail('ValueError not raised.')

    def x_test_is_valid(self):
        """Check is_valid"""
        #dr.is_valid()
        #dr.estimate()
        #dr.submit()
        #dr.request_status()
        #dr.cancel_request()
        pass

    def x_test_estimate(self):
        """Estimate"""
        pass
    
    def x_test_submit(self):
        """Submit"""
        pass

    def x_test_status_of(self):
        """Status of"""
        pass
    
    # estimated_completion_date
    # execution_status
    
    def x_test_cancel(self):
        """Cancel"""
        pass
    
if __name__ == '__main__':
    main()