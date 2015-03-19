#!/usr/bin/env python

from unittest import TestCase, main

from common.insensitive_dict import InsensitiveDict

class InsensitiveDictTests(TestCase):
    """Test InsensitiveDict Class"""
    
    def test_behavior(self):
        """Ensure InsensitiveDict is Insensitive"""
        d = InsensitiveDict({1:'lane_1', '2':'lane_2'})
        
        d['abc'] = 'Test Case'       
        
        #for item in d:
        #    print 'i: %s' % item
        
        self.assertEqual(d[1], 'lane_1')
        self.assertEqual(d['1'], 'lane_1')
        self.assertEqual(d[2], 'lane_2')
        self.assertEqual(d['2'], 'lane_2')
        self.assertEqual(d['ABC'], 'Test Case')
        self.assertEqual(d['aBc'], 'Test Case')
        self.assertEqual(d['abc'], 'Test Case')
        self.assertEqual(len(d), 3)
        self.assertEqual(d.keys(), [1, '2', 'abc'])
        self.assertEqual(d.values(), ['lane_1', 'lane_2', 'Test Case'])
        self.assertEqual(d.items(), [(1, 'lane_1'), ('2', 'lane_2'), ('abc', 'Test Case')])

        del d['1']

        try:
            t = d['1']
        except KeyError:
            pass
        else:
            self.fail('Did not raise keyerror')

if __name__ == '__main__':
    main()    