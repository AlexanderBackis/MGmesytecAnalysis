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
    print('\nImporting...')
    print('0%')
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
    print('100%')
    return s_red


# =============================================================================
#                               CLUSTER DATA
# =============================================================================

def cluster_data(data, detector_types = None):
    print('Clustering...')
    
    exceptions = []
    
    if detector_types != None:
        for i, detector in enumerate(detector_types):
            if detector == "ILL":
                exceptions.append(i * 3 + 1)
            
    size = data.size
    coincident_event_parameters = ['Bus', 'Time', 'ToF', 'wCh', 'gCh', 
                                    'wADC', 'gADC', 'wM', 'gM']
    event_parameters = ['Bus', 'Time', 'Channel', 'ADC']
    coincident_events = create_dict(size, coincident_event_parameters)
    events = create_dict(size, event_parameters)
    
    #Declare variables
    TriggerTime =    0
    index       =   -1
    index_event =   -1
    
    #Declare temporary variables
    isOpen              =    False
    isData              =    False
    isTrigger           =    False
    tempBus             =   -1
    maxADCw             =   -1
    maxADCg             =   -1
    nbrBuses            =    0
    nbrEvents           =    0
    Time                =    0
    extended_time_stamp =    None
    
    number_words = len(data)
    #Four possibilities in each word: Header, DataEvent, DataExTs or EoE
    for count, word in enumerate(data):
        if (word & TypeMask) == Header:
            isOpen = True
            isTrigger = (word & (TypeMask | TriggerMask)) == Trigger
              
        elif ((word & (TypeMask | DataMask)) == DataEvent) & isOpen:
            isData = True
            
            Bus = (word & BusMask) >> BusShift
            Channel = ((word & ChannelMask) >> ChannelShift)
            ADC = (word & ADCMask)
            
            index_event += 1
            events['Bus'][index_event] = Bus
            events['ADC'][index_event] = ADC
            
            #Create new coincident event if different buses (exception for ILL)
            ILL_exception = (Bus in exceptions) and Channel > 79
            if tempBus != Bus and not ILL_exception:
                tempBus = Bus
                maxADCw = -1
                maxADCg = -1
                nbrBuses += 1
                index += 1
                
                coincident_events['wCh'][index] = -1
                coincident_events['gCh'][index] = -1
                coincident_events['Bus'][index] = Bus
            
            if Channel < 80:
                coincident_events['wADC'][index] += ADC
                coincident_events['wM'][index] += 1
                if ADC > maxADCw:
                    coincident_events['wCh'][index] = Channel ^ 1 #Shift odd and even Ch
                    maxADCw = ADC
                
                events['Channel'][index_event] = Channel ^ 1 #Shift odd and even Ch
            else:
                coincident_events['gADC'][index] += ADC
                coincident_events['gM'][index] += 1
                if ADC > maxADCg:
                    coincident_events['gCh'][index] = Channel
                    maxADCg = ADC
                
                events['Channel'][index_event] = Channel
        
        elif ((word & (TypeMask | DataMask)) == DataExTs) & isOpen & (isData | isTrigger):
            extended_time_stamp = (word & ExTsMask) << ExTsShift
         
        elif ((word & TypeMask) == EoE) & isOpen:
            time_stamp = (word & TimeStampMask)
            
            if extended_time_stamp != None:
                Time = extended_time_stamp | time_stamp
            else:
                Time = time_stamp
            
            if isTrigger:
                TriggerTime = Time
            
            #Assign timestamp to coindicent events
            for i in range(0,nbrBuses):
                coincident_events['Time'][index-i] = Time
                coincident_events['ToF'][index-i] = Time - TriggerTime
            
            #Assign timestamp to events
            for i in range(0,nbrEvents):
                events['Time'][index-i] = Time
    
    
            #Reset temporary variables
            nbrBuses  = 0
            nbrEvents = 0
            tempBus   = -1
            isOpen    = False
            isData    = False
            isTrigger = False
            Time      = 0
        
        if count % 1000000 == 1:
            percentage_finished = str(round((count/number_words)*100)) + '%'
            print(percentage_finished)
    
    if percentage_finished != '100%':
        print('100%')
    
    coincident_events_df = pd.DataFrame(coincident_events)
    coincident_events_df = coincident_events_df.drop(range(index, size, 1))
    
    events_df = pd.DataFrame(events)
    events_df = events_df.drop(range(index, size, 1))
    
    return coincident_events_df, events_df

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
    
    