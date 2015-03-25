#!/usr/bin/env python

"""
Connection Adapters

The main package for the Connection Adapter.

    Connection Adapters abstract the mechanisim by which a particular protocol
    accomplish the population of one or more virtual state buffers
    
    Serial and Parallel:
        The FPGA uses two memory buffers as a temporary swap space when 
        pushing and pulling data from any number of orientations on the test chip.
        
    USB:
        The USB device loops reads over and over to constantly monitor
        the state of the SCRs and to provide a clock ????
        
"""