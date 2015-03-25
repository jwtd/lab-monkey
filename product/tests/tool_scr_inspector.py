#!/usr/bin/env python

"""
Procedure
"""
from common.base import exepath
from product.package import Package

dut = Package.from_txt_file(exepath('../repository/DES_65nm_Fuji.txt'), connect = 'Parallel FPGA')
scr = dut.top

scr.reset()
scr.refresh()

s = scr.sent
r = scr.retrieved



print 'Sent vs Default'
results = scr.translate_register_string_delta(s, scr.default)
deltas = results['deltas']
b = deltas.keys()
b.sort()
for block in b:
    print 'Block --------------------------------------- %s' % block
    for result in deltas[block]:
        if result['register'].direction == 'I':
            reg = result['register'].label
            reg_def = result['register'].default
            if block == 'common_block':
                sent = scr.cb[result['register'].label].sent
            else:
                sent = scr.lanes[0][result['register'].label].sent
            
            print '%s: %s -> %s' % (reg, reg_def, sent)

print 'D: %s' % results['b_scr']
print 'S: %s' % results['a_scr']
print 'C: %s' % results['delta_map']

print 'Retrieved vs Default'
results = scr.translate_register_string_delta(r, scr.default)
deltas = results['deltas']
b = deltas.keys()
b.sort()
for block in b:
    print 'Block --------------------------------------- %s' % block
    for result in deltas[block]:
        if result['register'].direction == 'I':
            reg = result['register'].label
            reg_def = result['register'].default
            if block == 'common_block':
                retrieved = scr.cb[result['register'].label].retrieved
            else:
                retrieved = scr.lanes[0][result['register'].label].retrieved
            
            print '%s: %s -> %s' % (reg, reg_def, retrieved)


print 'D: %s' % results['b_scr']
print 'R: %s' % results['a_scr']
print 'C: %s' % results['delta_map']

print 'Retrieved vs Sent'
results = scr.translate_register_string_delta(s, r)
deltas = results['deltas']
b = deltas.keys()
b.sort()
for block in b:
    print 'Block --------------------------------------- %s' % block
    for result in deltas[block]:
        if result['register'].direction == 'I':
            reg = result['register'].label
            sent = result['register'].sent
            if block == 'common_block':
                retrieved = scr.cb[result['register'].label].retrieved
            else:
                retrieved = scr.lanes[0][result['register'].label].retrieved
            
            print '%s: %s -> %s' % (reg, sent, retrieved)

print 'S: %s' % results['a_scr']
print 'R: %s' % results['b_scr']
print 'C: %s' % results['delta_map']

        