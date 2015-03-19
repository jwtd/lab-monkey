#!/usr/bin/env python

"""
Common helpers needed to run PyUnit tests
"""
import os, sys

def exepath(filename):
    """
    Takes a relative filepath and returns the correct execution path 
    regaurdless of where the containing file is run from
    """
    return os.path.abspath(os.path.join(os.path.dirname(sys._getframe(1).f_code.co_filename), filename))
                          
                          
if __name__ == '__main__':
    #print exepath('../equipment/definitions/Agilent_81134A.xml')
    pass
