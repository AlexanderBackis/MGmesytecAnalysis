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
import re

# =======    MASKS    ======= #
TypeMask      =   0xC0000000     # 1100 0000 0000 0000 0000 0000 0000 0000
DataMask      =   0x30000000     # 0011 0000 0000 0000 0000 0000 0000 0000

ChannelMask   =   0x00FFF000     # 0000 0000 1111 1111 1111 0000 0000 0000
BusMask       =   0x0F000000     # 0000 1111 0000 0000 0000 0000 0000 0000
ADCMask       =   0x00000FFF     # 0000 0000 0000 0000 0000 1111 1111 1111
TimeStampMask =   0x3FFFFFFF     # 0011 1111 1111 1111 1111 1111 1111 1111
NbrWordsMask  =   0x00000FFF     # 0000 0000 0000 0000 0000 1111 1111 1111
GateStartMask =   0x0000FFFF     # 0000 0000 0000 0000 1111 1111 1111 1111
ExTsMask      =   0x0000FFFF     # 0000 0000 0000 0000 1111 1111 1111 1111
TriggerMask   =   0x0F000000     # 0000 1111 0000 0000 0000 0000 0000 0000


# =======  DICTONARY  ======= #
Header        =   0x40000000     # 0100 0000 0000 0000 0000 0000 0000 0000 
Data          =   0x00000000     # 0000 0000 0000 0000 0000 0000 0000 0000
EoE           =   0xC0000000     # 1100 0000 0000 0000 0000 0000 0000 0000

DataEvent     =   0x10000000     # 0001 0000 0000 0000 0000 0000 0000 0000
DataExTs      =   0x20000000     # 0010 0000 0000 0000 0000 0000 0000 0000
Trigger       =   0x41000000     # 0100 0001 0000 0000 0000 0000 0000 0000

# =======  BIT-SHIFTS  ======= #
ChannelShift  =   12
BusShift      =   24
ExTsShift     =   30



# =============================================================================
#                                IMPORT DATA
# =============================================================================

def import_data(filename):
    dirname = os.path.dirname(__file__)
    filepath = os.path.join(dirname, '../Data/' + filename)
    with open(filepath, mode='rb') as binfile:
        content = binfile.read()
                
        #Skip configuration text
        match = re.search(b'}\n}\n[ ]*', content)
        start = match.end()
        content = content[start:]
        
        #Group data into 'uint'-words of 4 bytes length
        data = struct.unpack('I' * (len(content)//4), content)
        
        #Remove invalid and non-relevant words
        s = pd.Series(np.array(data))
        s_red = s[   ((s & TypeMask) == Header)
                   | ((s & (TypeMask | DataMask)) == DataEvent)
                   | ((s & (TypeMask | DataMask)) == DataExTs)
                   | ((s & TypeMask) == EoE)  
                 ]
        s_red.reset_index(drop=True, inplace=True)  
    return s_red


# =============================================================================
#                               CLUSTER DATA
# =============================================================================

def cluster_data(data):
    
    size = data.size
    parameters = ['Bus', 'Time', 'ToF', 'wCh', 'gCh', 'wADC', 'gADC', 'wM', 
                  'gM']
    clusters = create_dict(size, parameters)
    
    #Declare variables
    TriggerTime =    0
    index       =   -1
    
    #Declare temporary variables
    isOpen      =    False
    isData      =    False
    isTrigger   =    False
    tempBus     =   -1
    maxADCw     =   -1
    maxADCg     =   -1
    nbrBuses    =   -1
    Time        =    0
    
    #Four possibilities in each word: Header, DataEvent, DataExTs or EoE
    for word in data:
        if (word & TypeMask) == Header:
            isOpen = True
            if (word & (TypeMask | TriggerMask)) == Trigger:
                isTrigger = True
               
        elif ((word & (TypeMask | DataMask)) == DataEvent) & isOpen:
            isData = True
            Bus = (word & BusMask) >> BusShift
            Channel = ((word & ChannelMask) >> ChannelShift)
            ADC = (word & ADCMask)
            if tempBus != Bus:
                #Initialize temporary variables
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
        
        elif ((word & (TypeMask | DataMask)) == DataExTs) & isOpen & isData:
            Time = (word & ExTsMask) << ExTsShift
        
        elif ((word & (TypeMask | DataMask)) == DataExTs) & isOpen & isTrigger:
            TriggerTime = (word & ExTsMask) << ExTsShift
        
        elif ((word & TypeMask) == EoE) & isOpen:
            Time = Time | (word & TimeStampMask)
#            print('Time: ' + str(Time))
            if isTrigger:
                TriggerTime = TriggerTime | (word & TimeStampMask)
#                print('TriggerTime: ' + str(TriggerTime))
          #  print('Number of buses: ' + str(nbrBuses))
            for i in range(0,nbrBuses):
#                print('Count' + str(i))
                clusters['Time'][index-i] = Time
                ToF = (Time - TriggerTime)
#                print('Time: ' + str(Time))
#                print('TriggerTime: ' + str(TriggerTime))
#                print('ToF: ' + str(ToF))
                clusters['ToF'][index-i] = ToF
            
#            print('ToF: ' + str(Time - TriggerTime))
#            print('ToF in Clusters: ' + str(clusters['ToF'][index]))
            
            
            #Reset temporary variables
            nbrBuses  = 0
            tempBus   = -1
            isOpen    = False
            isData    = False
            isTrigger = False
            Time      = 0
    
    df = pd.DataFrame(clusters)
    df = df.drop(range(index, size, 1))
    
    return df

def cluster_data_ch(data):
    
    size = data.size
    parameters = ['Bus', 'Time', 'Bus', 'Channel', 'ADC']
    clusters = create_dict(size, parameters)
    index = -1
    
    isOpen = False
    isData = False
    Time = 0
    eventCount = 0
    for word in data:
        if (word & TypeMask) == Header:
            isOpen = True
        
        elif ((word & (TypeMask | DataMask)) == DataEvent) & isOpen:
            isData = True
            index += 1
            eventCount += 1
            clusters['Bus'][index] = (word & BusMask) >> BusShift
            clusters['ADC'][index] = (word & ADCMask)
            
            Channel = ((word & ChannelMask) >> ChannelShift)
            if Channel < 80:
                clusters['Channel'][index] = Channel ^ 1 #Shift odd and even Ch
            else:
                clusters['Channel'][index] = Channel
        
        elif ((word & (TypeMask | DataMask)) == DataExTs) & isOpen & isData:
            Time = (word & ExTsMask) << ExTsShift
            
        elif ((word & TypeMask) == EoE) & isOpen:
            Time = Time | (word & TimeStampMask)
            for i in range(0,eventCount):
                clusters['Time'][index-i] = Time
            eventCount = 0
            isOpen = False
            isData = False
            Time = 0
    
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
    
    