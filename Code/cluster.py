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
DataMask      =   0xF0000000     # 1111 0000 0000 0000 0000 0000 0000 0000

ChannelMask   =   0x00FFF000     # 0000 0000 1111 1111 1111 0000 0000 0000
BusMask       =   0x0F000000     # 0000 1111 0000 0000 0000 0000 0000 0000
ADCMask       =   0x00000FFF     # 0000 0000 0000 0000 0000 1111 1111 1111
TimeStampMask =   0x3FFFFFFF     # 0011 1111 1111 1111 1111 1111 1111 1111
NbrWordsMask  =   0x00000FFF     # 0000 0000 0000 0000 0000 1111 1111 1111
GateStartMask =   0x0000FFFF     # 0000 0000 0000 0000 1111 1111 1111 1111
ExTsMask      =   0x0000FFFF     # 0000 0000 0000 0000 1111 1111 1111 1111
TriggerMask   =   0xCF000000     # 1100 1111 0000 0000 0000 0000 0000 0000


# =======  DICTONARY  ======= #
Header        =   0x40000000     # 0100 0000 0000 0000 0000 0000 0000 0000 
Data          =   0x00000000     # 0000 0000 0000 0000 0000 0000 0000 0000
EoE           =   0xC0000000     # 1100 0000 0000 0000 0000 0000 0000 0000

DataBusStart  =   0x30000000     # 0011 0000 0000 0000 0000 0000 0000 0000
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

    print('100%')
    return data


# =============================================================================
#                               CLUSTER DATA
# =============================================================================

def cluster_data(data, ILL_buses = []):
    print('Clustering...')
    ch_to_coord = import_coordinates()
    

    size = len(data)
    coincident_event_parameters = ['Bus', 'Time', 'ToF', 'wCh', 'gCh', 
                                    'wADC', 'gADC', 'wM', 'gM']
    event_parameters = ['Bus', 'Time', 'Channel', 'ADC']
    coincident_events = create_dict(size, coincident_event_parameters)
    coincident_events.update({'Coordinate': np.empty([size],dtype=dict)})
    events = create_dict(size, event_parameters)
    
    #Declare variables
    TriggerTime =    0
    index       =   -1
    index_event =   -1
    
    #Declare temporary variables
    isOpen              =    False
    isTrigger           =    False
    Bus                 =    -1
    previousBus         =    -1
    maxADCw             =    0
    maxADCg             =    0
    nbrCoincidentEvents =    0
    nbrEvents           =    0
    Time                =    0
    extended_time_stamp =    None

    
    number_words = len(data)
    #Five possibilities in each word: Header, DataBusStart, DataEvent, 
    #DataExTs or EoE.
    for count, word in enumerate(data):
        if (word & TypeMask) == Header:
            isOpen = True
            isTrigger = (word & TriggerMask) == Trigger
        
        elif ((word & DataMask) == DataBusStart) & isOpen:
            
            Bus = (word & BusMask) >> BusShift
            
            if (previousBus in ILL_buses) and (Bus in ILL_buses):
                pass
            else:
                if previousBus != Bus and previousBus != -1:
                    wCh = coincident_events['wCh'][index]
                    gCh = coincident_events['gCh'][index]
                    if wCh != -1 and gCh != -1 and previousBus != -1:
                        coincident_events['Coordinate'][index] = ch_to_coord[previousBus%3,gCh,wCh]
                    else:
                        coincident_events['Coordinate'][index] = None
                
                previousBus             = Bus
                maxADCw                 = 0
                maxADCg                 = 0
                nbrCoincidentEvents    += 1
                index                  += 1
                
                coincident_events['wCh'][index] = -1
                coincident_events['gCh'][index] = -1
                coincident_events['Bus'][index] = Bus
            
        elif ((word & DataMask) == DataEvent) & isOpen:
            
            Channel = ((word & ChannelMask) >> ChannelShift)
            ADC = (word & ADCMask)
            
            index_event += 1
            events['Bus'][index_event] = Bus
            events['ADC'][index_event] = ADC   
                 
            if Channel < 80:
                coincident_events['Bus'][index] = Bus #Remove if trigger is on wire
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
        
        elif ((word & DataMask) == DataExTs) & isOpen:
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
            ToF = Time - TriggerTime
            for i in range(0,nbrCoincidentEvents):
                coincident_events['Time'][index-i] = Time
                coincident_events['ToF'][index-i] = ToF
            
            #Assign timestamp to events
            for i in range(0,nbrEvents):
                events['Time'][index-i] = Time
                
            #Assign coordinate
            wCh = coincident_events['wCh'][index]
            gCh = coincident_events['gCh'][index]
            if wCh != -1 and gCh != -1:
                eventBus = coincident_events['Bus'][index]
                coincident_events['Coordinate'][index] = ch_to_coord[eventBus%3,gCh,wCh]
            else:
                coincident_events['Coordinate'][index] = None
                
            #Reset temporary variables
            nbrCoincidentEvents  =  0
            nbrEvents            =  0
            Bus                  =  -1
            previousBus          =  -1
            isOpen               =  False
            isTrigger            =  False
            Time                 =  0

        
        if count % 1000000 == 1:
            percentage_finished = str(round((count/number_words)*100)) + '%'
            print(percentage_finished)
    
    if percentage_finished != '100%':
        print('100%')
        
    #Remove empty elements and save in DataFrame for easier analysis
    for key in coincident_events:
        coincident_events[key] = coincident_events[key][0:index]
    coincident_events_df = pd.DataFrame(coincident_events)
    
    for key in events:
        events[key] = events[key][0:index_event]
    events_df = pd.DataFrame(events)
    
    return coincident_events_df, events_df

# =============================================================================
# Helper Functions
# =============================================================================         
            
    
def create_dict(size, names):
    clu = {names[0]: np.zeros([size],dtype=int)}
    
    for name in names[1:len(names)]:
        clu.update({name: np.zeros([size],dtype=int)}) 
    
    return clu

def import_coordinates():
    dirname = os.path.dirname(__file__)
    file_path = os.path.join(dirname, '../Coordinates/Coordinates_MG_SEQ.xlsx')
    matrix = pd.read_excel(file_path).values
    coordinates = matrix[1:801]
    ch_to_coord = np.empty((3,120,80),dtype='object')
    coordinate = {'x': -1, 'y': -1, 'z': -1}
    axises =  ['x','y','z']

    for i, row in enumerate(coordinates):
        grid_ch = i // 20 + 80
        for j, col in enumerate(row):
            module = j // 12
            layer = (j // 3) % 4
            wire_ch = (19 - (i % 20)) + (layer * 20)
            coordinate_count = j % 3
            coordinate[axises[coordinate_count]] = col
            if coordinate_count == 2:
                ch_to_coord[module, grid_ch, wire_ch] = coordinate
                coordinate = {'x': -1, 'y': -1, 'z': -1}

    return ch_to_coord