#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 13:18:00 2018

@author: alexanderbackis
"""

# =======  LIBRARIES  ======= #
import os
import pandas as pd
import numpy as np
import struct

# =======    MASKS    ======= #
TypeMask      =   0xC0000000     # 1100 0000 0000 0000 0000 0000 0000 0000
DataMask      =   0x30000000     # 0011 0000 0000 0000 0000 0000 0000 0000

ChannelMask   =   0x00FFF000     # 0000 0000 1111 1111 1111 0000 0000 0000
BusMask       =   0x0F000000     # 0000 1111 0000 0000 0000 0000 0000 0000
ADCMask       =   0x00000FFF     # 0000 0000 0000 0000 0000 1111 1111 1111
TimeStampMask =   0x3FFFFFFF     # 0011 1111 1111 1111 1111 1111 1111 1111

NbrWordsMask  =   0x00000FFF     # 0000 0000 0000 0000 0000 1111 1111 1111


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



# =============================================================================
#                                IMPORT DATA
# =============================================================================

def import_data(filename):
    dirname = os.path.dirname(__file__)
    filepath = os.path.join(dirname, '../Data/' + filename)
    with open(filepath, mode='rb') as binfile:
        content = binfile.read()
        
        #Skip configuration text
        start = content.find(b'}\n}\n')
        content = content[start+7:]
        
        #Group data into uint-words of 4 bytes length
        data = struct.unpack('I' * (len(content)//4), content)
        
        #Remove invalid and non-relevant words
        s = pd.Series(np.array(data))
        s_red = s[   ((s & TypeMask) == Header)
                   | ((s & (TypeMask + DataMask)) == DataPart2)                        
                   | ((s & TypeMask) == EoE)  
                 ]
        s_red.reset_index(drop=True, inplace=True)  
    return s_red


# =============================================================================
#                               CLUSTER DATA
# =============================================================================

def cluster_data(data):
    
    size = data.size
    parameters = ['Bus', 'Time', 'wCh', 'gCh', 'wADC', 'gADC', 'wM', 'gM']
    clusters = create_dict(size, parameters)
    
    isOpen = False
    index = -1
    tempBus = -1
    maxADCw = -1
    maxADCg = -1
    nbrBuses = 0
    for i, word in enumerate(data):
        if (word & TypeMask) == Header:
            isOpen = True
        
        elif ((word & (TypeMask + DataMask)) == DataPart2) & isOpen:
            Bus = (word & BusMask) >> BusShift
            Channel = ((word & ChannelMask) >> ChannelShift)
            ADC = (word & ADCMask)
            if tempBus != Bus:
                tempBus = Bus
                maxADCw = -1
                maxADCg = -1
                nbrBuses += 1
                index += 1
                clusters['wCh'][index] = -1
                clusters['gCh'][index] = -1
                clusters['Bus'][index] = Bus
            
            if Channel < 80:
                clusters['wADC'][index] += ADC
                clusters['wM'][index] += 1
                if ADC > maxADCw:
                    clusters['wCh'][index] = Channel ^ 1 #Shift odd and even Ch
                    maxADCw = ADC
            else:
                clusters['gADC'][index] += ADC
                clusters['gM'][index] += 1
                if ADC > maxADCg:
                    clusters['gCh'][index] = Channel
                    maxADCg = ADC
            
        elif ((word & TypeMask) == EoE) & isOpen:
            Time = (word & TimeStampMask)
            for i in range(0,nbrBuses):
                clusters['Time'][index-i] = Time
            nbrBuses = 0
            tempBus = -1
            isOpen = False
    
    df = pd.DataFrame(clusters)
    df = df.drop(range(index, size, 1))
    
    return df
            


# =============================================================================
# Helper Functions
# =============================================================================         
            
    
def create_dict(size, names):
    clu = {names[0]: np.zeros([size],dtype=int)}
    for name in names[1:]:
        clu.update({name: np.zeros([size],dtype=int)}) 
    return clu
    
    