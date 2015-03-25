#!/usr/bin/env python

"""
Procedure
"""
from common.base import exepath
from product.package import Package

dut = Package.from_txt_file(exepath('../repository/DES_90nm_IBM.txt'), connect = 'Mock')
scr = dut.top

# Prepare Common Block
scr.cb.prepare('SYSCLK_DIV2_SEL', 0)
scr.cb.prepare('IDDQ', 0)
scr.cb.prepare('CLKBUF_L_EN', 1)
scr.cb.prepare('CLKBUF_R_EN', 1)
scr.cb.prepare('SYSCLK_TERM_SEL', 1)
scr.cb.prepare('GRESET', 0)
scr.cb.prepare('VCO_CAL', 0)
scr.cb.prepare('RES_CAL', 0)
scr.cb.prepare('RESET_TSYNC', 0)
scr.cb.prepare('SYSCLK_RATE', 6)
scr.cb.prepare('SYSCLK_SEL', 0)
scr.cb.prepare('SYSCLK_CORE_SEL', 0)
scr.cb.prepare('8BMODE', 0)
scr.cb.prepare('CMU_EN', 1)
scr.cb.prepare('BIAS_EN', 1)
scr.cb.prepare('SYSCLK_EN', 1)
scr.cb.prepare('HVDD_MODE', 0)
scr.cb.prepare('BG_BYP', 0)
scr.cb.prepare('BG_BYP_V', 0)
scr.cb.prepare('RES_CODE_BYP', 0)
scr.cb.prepare('RES_CODE', 0)
scr.cb.prepare('VCO_CODE_BYP', 0)
scr.cb.prepare('VCO_CODE', 0)
scr.cb.prepare('DTB_LR_SEL', 0)
scr.cb.prepare('CATB_SEL', 0)
scr.cb.prepare('READY', 0)
scr.cb.prepare('CMULOCK', 0)
scr.cb.prepare('VCO_CAL_DONE', 0)
scr.cb.prepare('RES_CAL_DONE', 0)
# Prepare Lanes
scr.prepare('RESET_TSYNC_EN', 1)
scr.prepare('GLOBAL_CLKGATE_EN', 0)
scr.prepare('SATA_IDLE_EN', 0)
scr.prepare('ELECIDLE_EN', 0)
scr.prepare('TX_BAND', 0)
scr.prepare('EMP_PRE', 0)
scr.prepare('EMP_POST', 0)
scr.prepare('DRV_LVL', 12)
scr.prepare('TX_HIGHZ', 0)
scr.prepare('TX_REC_DETECT_EN', 0)
scr.prepare('RX_BAND', 0)
scr.prepare('RESET_RSYNC', 0)
scr.prepare('PAR_RATE', 0)
scr.prepare('RX_EQ', 0)
scr.prepare('RX_AC_COUPLE', 0)
scr.prepare('RX_CM', 0)
scr.prepare('RX_TERM', 1)
scr.prepare('RX_HIGHZ', 0)
scr.prepare('CDR_RESET', 0)
scr.prepare('CDR_FREQLOOP_EN', 0)
scr.prepare('CDR_FREQLOOP_GAIN', 3)
scr.prepare('CDR_THRESHOLD', 2)
scr.prepare('TX_EN', 1)
scr.prepare('DRV_EN', 1)
scr.prepare('RX_EN', 1)
scr.prepare('CLKBUF_EN', 1)
scr.prepare('SER_LPB_EN', 0)
scr.prepare('LINE_LPB_EN', 0)
scr.prepare('PAR_LPB_EN', 0)
scr.prepare('RCLK_LPB_EN', 0)
scr.prepare('SERDES_BYP_IN', 0)
scr.prepare('SERDES_BYP_EN', 0)    
scr.prepare('BIST_TX_RESET', 0)
scr.prepare('BIST_RX_RESET', 0)
scr.prepare('BIST_BER_CLEAR', 0)
scr.prepare('BIST_MODE', 1)
scr.prepare('BIST_FORCE_ERR', 0)    
scr.prepare('SERDES_BYP_OUT', 0)
scr.commit()

results = scr.translate_register_string_delta(scr.sent, scr.default)
deltas = results['deltas']

for block in deltas:
    print 'Block ------------- %s' % block
    for result in deltas[block]:
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

        