#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 13:18:00 2018

@author: alexanderbackis
"""

# =======  LIBRARIES  ======= #
import cluster_mesytec as clu
import plot_mesytec as pl
import time
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cmx
import struct

def get_plot_path():
    dirname = os.path.dirname(__file__)
    folder = os.path.join(dirname, '../Plot/')
    return folder

# =======    MASKS    ======= #
TypeMask      =   0xC0000000     # 1100 0000 0000 0000 0000 0000 0000 0000
DataMask      =   0x30000000     # 0011 0000 0000 0000 0000 0000 0000 0000

ChannelMask   =   0x00FFF000     # 0000 0000 1111 1111 1111 0000 0000 0000
BusMask       =   0x0F000000     # 0000 1111 0000 0000 0000 0000 0000 0000
ADCMask       =   0x00000FFF     # 0000 0000 0000 0000 0000 1111 1111 1111
TimeStampMask =   0x3FFFFFFF     # 0011 1111 1111 1111 1111 1111 1111 1111

NbrWordsMask  =   0x00000FFF     # 0000 0000 0000 0000 0000 1111 1111 1111
GateStartMask =   0x0000FFFF     # 0000 0000 0000 0000 1111 1111 1111 1111


# =======  DICTONARY  ======= #
Header        =   0x40000000     # 0100 0000 0000 0000 0000 0000 0000 0000 
Data          =   0x00000000     # 0000 0000 0000 0000 0000 0000 0000 0000
EoE           =   0xC0000000     # 1100 0000 0000 0000 0000 0000 0000 0000

DataPart1     =   0x30000000     # 0011 0000 0000 0000 0000 0000 0000 0000
DataPart2     =   0x10000000     # 0001 0000 0000 0000 0000 0000 0000 0000
DataExTs      =   0x20000000     # 0010 0000 0000 0000 0000 0000 0000 0000


# =======  BIT-SHIFTS  ======= #
ChannelShift = 12
BusShift = 24

start_time = time.time()
filename = 'mvmelst_061_180628_140303.mvmelst'
dirname = os.path.dirname(__file__)
filepath = os.path.join(dirname, '../Data/' + filename)
with open(filepath, mode='rb') as binfile:
    content = binfile.read()
        
    #Skip configuration text
    start = content.find(b'}\n}\n')
    content = content[start+7:]
        
    #Group data into 'uint'-words of 4 bytes length
    data = struct.unpack('I' * (len(content)//4), content)
        
    data = pd.Series(np.array(data))

    data_header = data[(data & TypeMask) == Header]
    data_red_1 = data[(data & (TypeMask | DataMask)) == DataPart1]
    data_red_2 = data[(data & (TypeMask | DataMask)) == DataPart2]
    data_ExTs = data[(data & (TypeMask | DataMask)) == DataExTs]
    data_EoE = data[(data & TypeMask) == EoE]
    
    print('\n')
    print('Number of words: ' + str(data.size))
    print('...........................')
    print('Header: ' + str(data_header.size))
    print('Data (event type 1): ' + str(data_red_1.size))
    print('Data (event type 2): ' + str(data_red_2.size))
    print('Data (extended time stamp): ' + str(data_ExTs.size))
    print('End of Event mark: ' + str(data_EoE.size))
    print('...........................')
    print('\n')
    print('Information in Data (extended time stamp)): ')
    print('...........................')
    print('Extended time stamp:')
    test = data_ExTs & GateStartMask
    print(test)
    print('...........................')
    print('Bus:')
    test2 = (data_ExTs & BusMask)
    print(test2)
#    print('...........................')
#    print('Random:')
#    test3 = (data_ExTs & ChannelMask)
#    print(test3)
    fig = plt.figure()
    plt.hist(test, bins=20, range=[0,20], log=True)
    locs = np.arange(0,21)
    ticks = locs + 0.5
    plt.xticks(ticks, locs)
    plt.xlabel('Time difference Gate start to bus trigger [TDC channels]')
    plt.ylabel('Counts [a.u.]')
    plt.title('Histogram of Time difference Gate start to bus trigger')
    plt.show()
    file_path = get_plot_path() + 'GateStart' + '.pdf'
    fig.savefig(plot_path, bbox_inches='tight')
    
    
    
# =============================================================================
# Helper Functions
# ============================================================================= 
    
def get_plot_path():
    dirname = os.path.dirname(__file__)
    folder = os.path.join(dirname, '../Plot/')
    return folder
    
    

