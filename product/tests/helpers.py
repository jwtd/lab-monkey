#!/usr/bin/env python

"""
Tests Helpers
"""

from common.base import *
from product.register import *

def register_collections_from_txt_file(filepath):
    """Test helper that builds register collections from a plain text DES file"""

    # Get the data from the file and close ASAP
    f = open(filepath)
    try:
        lines = []
        for line in f:
            lines.append(line.rstrip('\n').split())
    finally:
        f.close()

    # Create temporary storage collections
    identification         = {}
    orientations           = {}
    constants              = {}
    common_block_registers = []
    lane_registers         = []

    # Read through the lines
    i=0
    while i < len(lines):
        if lines[i][0] == 'ID':
            identification[lines[i][1]] = lines[i][2]
        elif lines[i][0] == 'ORIENTATION':
            orientations[lines[i][1]] = lines[i][2]
        elif lines[i][0] == 'CONSTANT':
            # TODO: Not doing anything with constants now
            constants[lines[i][1]] = lines[i][2]
        elif lines[i][0] == 'NAME':
            # Multiline data structure collection
            reg_name         = lines[i][1]
            reg_width        = lines[i+1][1]
            reg_default      = lines[i+2][1]
            reg_parent       = lines[i+3][1]
            reg_direction    = lines[i+4][1]
            reg_start_index  = lines[i+5][1]
            reg_enable_index = lines[i+6][1]
            #reg_group        = lines[i+7][1]    # Not used
            i += 7

            # Standardize int, hex, and bin, to proper length binary version
            reg_default = data_to_int(reg_default)
            reg_default = int_to_bin(reg_default, int(reg_width))
            
            # Create and bin the register
            r = Register(reg_name, reg_direction, reg_enable_index, reg_start_index, reg_width, reg_default)
            if (reg_parent == 'C'):
                common_block_registers.append(r)
            elif (reg_parent == 'L'):
                lane_registers.append(r)
            else:
                raise ValueError('Unrecognized BLOCK_TYPE specified \'%s\' for register at line %i in file %s' % (reg_parent, i, filepath))
        i+=1

    # Send back collections
    return [common_block_registers, lane_registers]


if __name__ == '__main__':
    pass