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

def import_data(file_name, max_size = np.inf):
    """ Goes to sister-folder '/Data/' and imports '.mesytec'-file with name
        'file_name'. Does this in three steps:
            
            1. Reads file as binary and saves data in 'content'
            2. Finds the end of the configuration text, i.e. '}\n}\n' followed
               by 0 to n spaces, then saves everything after this to 
               'reduced_content'.
            3. Groups data into 'uint'-words of 4 bytes (32 bits) length
        
    Args:
        file_name (str): Name of '.mesytec'-file that contains the data
            
    Returns:
        data (tuple): A tuple where each element is a 32 bit mesytec word
            
    """
    print('\nImporting...')
    print('0%')
    
    dir_name = os.path.dirname(__file__)
    file_path = os.path.join(dir_name, '../Data/' + file_name)
    
    with open(file_path, mode='rb') as bin_file:
        piece_size = 0
        
        if max_size > 1000:
            piece_size = 1000
        else:
            piece_size = max_size
        
        content = bin_file.read(piece_size * (1 << 20))
        
        # Skip configuration text
        match = re.search(b'}\n}\n[ ]*', content)
        start = match.end()
        content = content[start:]
        
        data = struct.unpack('I' * (len(content)//4), content)
        
        moreData = True
        imported_data = piece_size
        
        file_size = os.path.getsize(file_path)
        
        while moreData and imported_data <= max_size:
            imported_data += piece_size
            piece = bin_file.read(piece_size * (1 << 20))
            if not piece:  # Reached EOF
                moreData = False
            else:
                data += struct.unpack('I' * (len(piece)//4), piece)

    print('100%!')
    print('Done!')
    return data


# =============================================================================
#                               CLUSTER DATA
# =============================================================================

def cluster_data(data, ILL_buses = [], E_i = -1, 
                 calibration = 'High_Resolution'):
    """ Clusters the imported data and stores it two data frames: one for 
        individual events and one for coicident events (i.e. candidate neutron 
        events). 
        
        Does this in the following fashion for coincident events: 
            1. Reads one word at a time
            2. Checks what type of word it is (Header, BusStart, DataEvent, 
               DataExTs or EoE).
            3. When a Header is encountered, 'isOpen' is set to 'True',
               signifying that a new event has been started. Data is then
               gathered into a single coincident event until a different bus is
               encountered (unless ILL exception), in which case a new event is
               started.
            4. When EoE is encountered the event is formed, and timestamp is 
               assigned to it and all the created events under the current 
               Header. This event is placed in the created dictionary.
            5. After the iteration through data is complete, the dictionary
               containing the coincident events is convereted to a DataFrame.
                    
        And for events:
            1-2. Same as above.
            3. Every time a data word is encountered it is added as a new event
               in the intitally created dicitionary.
            4-5. Same as above
           
    Args:
        data (tuple)    : Tuple containing data, one word per element.
        ILL_buses (list): List containg all ILL buses
            
    Returns:
        data (tuple): A tuple where each element is a 32 bit mesytec word
        
        events_df (DataFrame): DataFrame containing one event (wire or grid) 
                               per row. Each event has information about:
                               "Bus", "Time", "Channel", "ADC".
        
        coincident_events_df (DataFrame): DataFrame containing one neutron
                                          event per row. Each neutron event has
                                          information about: "Bus", "Time", 
                                          "ToF", "wCh", "gCh", "wADC", "gADC",
                                          "wM", "gM", "Coordinate".
                                        
                                            
            
    """
    print('Clustering...')
    
#    t_d = get_td(E_i)
#    T_0 = get_T0(calibration, E_i)
#    t_off = get_t_off(calibration)
#    print('t_off: ' + str(t_off))
    
    offset_1 = {'x': -0.907574, 'y': -3.162949, 'z': 5.384863}
    offset_2 = {'x': -1.246560, 'y': -3.161484, 'z': 5.317432}
    offset_3 = {'x': -1.579114, 'y': -3.164503,  'z': 5.227986}
    
    corners = {'ESS_2': {1: [-1.579114, -3.164503, 5.227986],
                         2: [-1.252877, -3.162614, 5.314108]},
               'ESS_1': {3: [-1.246560, -3.161484, 5.317432],
                         4: [-0.916552, -3.160360, 5.384307]},
               'ILL':   {5: [-0.907574, -3.162949, 5.384863],
                         6: [-0.575025, -3.162578, 5.430037]}
                }
    
    ILL_C = corners['ILL']
    ESS_1_C = corners['ESS_1']
    ESS_2_C = corners['ESS_2']
    
    theta_1 = np.arctan((ILL_C[6][2]-ILL_C[5][2])/(ILL_C[6][0]-ILL_C[5][0]))
    theta_2 = np.arctan((ESS_1_C[4][2]-ESS_1_C[3][2])/(ESS_1_C[4][0]-ESS_1_C[3][0]))
    theta_3 = np.arctan((ESS_2_C[2][2]-ESS_2_C[1][2])/(ESS_2_C[2][0]-ESS_2_C[1][0]))
    
    detector_1 = create_ill_channel_to_coordinate_map(theta_1, offset_1)
    detector_2 = create_ess_channel_to_coordinate_map(theta_2, offset_2)
    detector_3 = create_ess_channel_to_coordinate_map(theta_3, offset_3)
    
    detector_vec = [detector_1, detector_2, detector_3]

    size = len(data)
    coincident_event_parameters = ['Bus', 'Time', 'ToF', 'wCh', 'gCh', 
                                    'wADC', 'gADC', 'wM', 'gM']
    coincident_events = create_dict(size, coincident_event_parameters)
    coincident_events.update({'d': np.zeros([size], dtype=float)})
#    coincident_events.update({'dE': np.zeros([size], dtype=float)})
#    coincident_events.update({'tf': np.zeros([size], dtype=float)}) 
    
    event_parameters = ['Bus', 'Time', 'Channel', 'ADC']
    events = create_dict(size, event_parameters)
    
    triggers = np.empty([size],dtype=int)
    
    #Declare variables
    TriggerTime   =    0
    index         =   -1
    index_event   =   -1
    trigger_index =    0
    
    #Declare temporary variables
    isOpen              =    False
    isData              =    False
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
            isData = True
            if (previousBus in ILL_buses) and (Bus in ILL_buses):
                pass
            else:                
                previousBus = Bus
                maxADCw = 0
                maxADCg = 0
                nbrCoincidentEvents += 1
                nbrEvents += 1
                index += 1
                
                coincident_events['wCh'][index] = -1
                coincident_events['gCh'][index] = -1
                coincident_events['Bus'][index] = Bus  
        elif ((word & DataMask) == DataEvent) & isOpen:
            Channel = ((word & ChannelMask) >> ChannelShift)
            ADC = (word & ADCMask)
            index_event += 1
            nbrEvents   += 1
            events['Bus'][index_event] = Bus
            events['ADC'][index_event] = ADC   
            
            if Channel >= 120:
                pass
            elif Channel < 80:
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
                triggers[trigger_index] = TriggerTime
                trigger_index += 1
            #Assign timestamp to coindicent events
            ToF = Time - TriggerTime
            for i in range(0,nbrCoincidentEvents):
                coincident_events['Time'][index-i] = Time
                coincident_events['ToF'][index-i] = ToF
            #Assign timestamp to events
            for i in range(0,nbrEvents):
                events['Time'][index_event-i] = Time
            #Assign d
            for i in range(0, nbrCoincidentEvents):
                wCh = coincident_events['wCh'][index-i]
                gCh = coincident_events['gCh'][index-i]
                if (wCh != 0 and gCh != 0) and (wCh != -1 and gCh != -1):
                    eventBus = coincident_events['Bus'][index]
                    ToF = coincident_events['ToF'][index-i]
                    d = get_d(eventBus, wCh, gCh, detector_vec)
#                    dE, t_f = get_dE(E_i, ToF, d, T_0, t_off)
                    coincident_events['d'][index-i] = d
#                    coincident_events['dE'][index-i] = dE
#                    coincident_events['tf'][index-i] = t_f
                else:
                    coincident_events['d'][index-i] = -1
#                    coincident_events['tf'][index-i] = -1
#                    coincident_events['dE'][index-i] = np.nan
                
            #Reset temporary variables
            nbrCoincidentEvents  =  0
            nbrEvents            =  0
            Bus                  =  -1
            previousBus          =  -1
            isOpen               =  False
            isData               =  False
            isTrigger            =  False
            Time                 =  0

        
        if count % 1000000 == 1:
            percentage_finished = str(round((count/number_words)*100)) + '%'
            print(percentage_finished)
#            for i in range(0,len(percentage_finished)):
#                print('\r', end='')
    
    if percentage_finished != '100%':
        print('100%')
        
    #Remove empty elements and save in DataFrame for easier analysis
    for key in coincident_events:
        coincident_events[key] = coincident_events[key][0:index]
    coincident_events_df = pd.DataFrame(coincident_events)
    
    for key in events:
        events[key] = events[key][0:index_event]
    events_df = pd.DataFrame(events)
    
    triggers_df = None
    if trigger_index == 0:
        triggers_df = pd.DataFrame([0])
    else:
        triggers_df = pd.DataFrame(triggers[0:trigger_index-1])
    
    print('Done!')
    
    return coincident_events_df, events_df, triggers_df, detector_vec

# =============================================================================
# Helper Functions
# =============================================================================         
            
    
def create_dict(size, names):
    clu = {names[0]: np.zeros([size],dtype=int)}
    
    for name in names[1:len(names)]:
        clu.update({name: np.zeros([size],dtype=int)}) 
    
    return clu

def create_ess_channel_to_coordinate_map(theta, offset):
    dirname = os.path.dirname(__file__)
    file_path = os.path.join(dirname, 
                             '../Tables/Coordinates_MG_SEQ_ESS.xlsx')
    matrix = pd.read_excel(file_path).values
    coordinates = matrix[1:801]
    ess_ch_to_coord = np.empty((3,124,80),dtype='object')
    coordinate = {'x': -1, 'y': -1, 'z': -1}
    axises =  ['x','y','z']
    
    c_offset = [[-1, 1, -1], [-1, -1, 1], [-1, 1, 1]]
    c_count = 0
    
    for i, row in enumerate(coordinates):
        grid_ch = i // 20 + 80
        for j, col in enumerate(row):
            module = j // 12
            layer = (j // 3) % 4
            wire_ch = (19 - (i % 20)) + (layer * 20)
            coordinate_count = j % 3
            coordinate[axises[coordinate_count]] = col
            if coordinate_count == 2:
                x = coordinate['x']
                y = coordinate['y']
                z = coordinate['z']
                # Convert from [mm] to [m]
                x = x/1000
                y = y/1000
                z = z/1000
                # Insert corners of vessels
                if wire_ch == 0 and grid_ch == 80 and module == 0:
                    ess_ch_to_coord[0][120][0] = {'x': offset['x'], 'y': offset['y'], 'z': offset['z']}
                if (  (wire_ch == 0 and grid_ch == 119 and module == 0)
                    | (wire_ch == 60 and grid_ch == 80 and module == 2)
                    | (wire_ch == 60 and grid_ch == 119 and module == 2)
                    ):
                    x_temp = x + 46.514/1000 * c_offset[c_count][0] + np.finfo(float).eps
                    y_temp = y + 37.912/1000 * c_offset[c_count][1] + np.finfo(float).eps
                    z_temp = z + 37.95/1000 * c_offset[c_count][2] + np.finfo(float).eps
                    z_temp, x_temp, y_temp = x_temp, y_temp, z_temp
                    x_temp, z_temp = get_new_x(x_temp, z_temp, theta), get_new_y(x_temp, z_temp, theta)
                    # Apply translation
                    x_temp += offset['x']
                    y_temp += offset['y']
                    z_temp += offset['z']
                    ess_ch_to_coord[0][121+c_count][0] = {'x': x_temp, 
                                                          'y': y_temp,
                                                          'z': z_temp}
                    c_count += 1
                
                # Shift to match internal and external coordinate system
                z, x, y = x, y, z
                # Apply rotation
                x, z = get_new_x(x, z, theta), get_new_y(x, z, theta)
                # Apply translation
                x += offset['x']
                y += offset['y']
                z += offset['z']

                ess_ch_to_coord[module, grid_ch, wire_ch] = {'x': x, 'y': y,
                                                             'z': z}
                coordinate = {'x': -1, 'y': -1, 'z': -1}

    return ess_ch_to_coord
    
def create_ill_channel_to_coordinate_map(theta, offset):
        
    WireSpacing  = 10     #  [mm]
    LayerSpacing = 23.5   #  [mm]
    GridSpacing  = 23.5   #  [mm]
    
    x_offset = 46.514     #  [mm]
    y_offset = 37.912     #  [mm]
    z_offset = 37.95      #  [mm]
    
    corners =   [[0, 80], [0, 119], [60, 80], [60, 119]]
    corner_offset = [[-1, -1, -1], [-1, -1, 1], [-1, 1, -1], [-1, 1, 1]]
    
    # Make for longer to include the for corners of the vessel
    ill_ch_to_coord = np.empty((3,124,80),dtype='object')
    for Bus in range(0,3):
        for GridChannel in range(80,120):
            for WireChannel in range(0,80):
                    x = (WireChannel % 20)*WireSpacing + x_offset
                    y = ((WireChannel // 20)*LayerSpacing 
                         + (Bus*4*LayerSpacing) + y_offset)
                    z = ((GridChannel-80)*GridSpacing) + z_offset 
                    # Convert from [mm] to [m]
                    x = x/1000
                    y = y/1000
                    z = z/1000
                    # Shift to match internal and external coordinate system
                    z, x, y = x, y, z
                    # Apply rotation
                    x, z = get_new_x(x, z, theta), get_new_y(x, z, theta)
                    # Apply translation
                    x += offset['x']
                    y += offset['y']
                    z += offset['z']
                                        
                    ill_ch_to_coord[Bus,GridChannel,WireChannel] = {'x': x,
                                                                    'y': y,
                                                                    'z': z}
        if Bus == 0:
            for i, corner in enumerate(corners[1:2]):
                WireChannel = corner[0]
                GridChannel = corner[1]
                x = (WireChannel % 20)*WireSpacing + x_offset
                y = ((WireChannel // 20)*LayerSpacing + (Bus*4*LayerSpacing) + y_offset)
                z = ((GridChannel-80)*GridSpacing) + z_offset 
                x += corner_offset[i+1][0] * x_offset
                y += corner_offset[i+1][1] * y_offset
                z += corner_offset[i+1][2] * z_offset
                x = x/1000 + np.finfo(float).eps
                y = y/1000 + np.finfo(float).eps
                z = z/1000 + np.finfo(float).eps
                z, x, y = x, y, z

                x, z = get_new_x(x, z, theta), get_new_y(x, z, theta)
                x += offset['x']
                y += offset['y']
                z += offset['z']
                ill_ch_to_coord[0, 121+i, 0] = {'x': x, 'y': y, 'z': z}
        
            ill_ch_to_coord[Bus, 120, 0] = {'x': offset['x'], 'y': offset['y'], 'z': offset['z']}

            
        if Bus == 2:
            for i, corner in enumerate(corners[2:]):
                WireChannel = corner[0]
                GridChannel = corner[1]
                x = (WireChannel % 20)*WireSpacing + x_offset
                y = ((WireChannel // 20)*LayerSpacing + (Bus*4*LayerSpacing) + y_offset)
                z = ((GridChannel-80)*GridSpacing) + z_offset 
                x += corner_offset[i+2][0] * x_offset
                y += corner_offset[i+2][1] * y_offset
                z += corner_offset[i+2][2] * z_offset
                x = x/1000
                y = y/1000
                z = z/1000
                z, x, y = x, y, z
                x, z = get_new_x(x, z, theta), get_new_y(x, z, theta)
                x += offset['x']
                y += offset['y']
                z += offset['z']
                ill_ch_to_coord[0, 122+i, 0] = {'x': x, 'y': y, 'z': z}
            
    return ill_ch_to_coord

def get_d(Bus, WireChannel, GridChannel, detector_vec):
    coord = None
    d = None
    if 0 <= Bus <= 2:
        coord = detector_vec[0][Bus%3, GridChannel, WireChannel]
    elif 3 <= Bus <= 5:
        coord = detector_vec[1][Bus%3, GridChannel, WireChannel]
    elif 6 <= Bus <= 8:
        coord = detector_vec[2][Bus%3, GridChannel, WireChannel]
            
    return np.sqrt((coord['x'] ** 2) + (coord['y'] ** 2) + (coord['z'] ** 2))

def get_new_x(x, y, theta):
    return np.cos(np.arctan(y/x)+theta)*np.sqrt(x ** 2 + y ** 2)
    
def get_new_y(x, y, theta):
    return np.sin(np.arctan(y/x)+theta)*np.sqrt(x ** 2 + y ** 2)


def get_dE(E_i, ToF, d, T_0, t_off):
    # Declare parameters
    L_1 = 20.01                                # Source to sample
    m_n = 1.674927351e-27                      # Neutron mass
    meV_to_J = 1.60218e-19 * 0.001             # Convert meV to J
    J_to_meV = 6.24150913e18 * 1000            # Convert J to meV
    # Calculate dE
    E_i_J = E_i * meV_to_J                     # Convert E_i to J
    v_i = np.sqrt((E_i_J*2)/m_n)               # Get velocity of E_i
    t_1 = (L_1 / v_i) + T_0 * 1e-6             # Use velocity to find t_1
    ToF_real = ToF * 62.5e-9 + (t_off * 1e-6)  # Time from source to detector
    if E_i == 8:
        ToF_real += (16666.66666e-6) - 0.0043893
    if E_i == 21:
        ToF_real += (16666.66666e-6) - 0.01227875
    if E_i == 2:
        ToF_real += 2 * (16666.66666e-6) - 0.0004475
    if E_i == 25:
        ToF_real += (16666.66666e-6) - 0.013340625
    if E_i == 35:
        ToF_real += (16666.66666e-6) - 0.01514625
    t_f = ToF_real - t_1                        # Time from sample to detector
    E_J = (m_n/2) * ((d/t_f) ** 2)              # Energy E_f in Joule
    E_f = E_J * J_to_meV                        # Convert to meV
    return (E_i - E_f), t_f


def get_td(E_i):
    td_table = import_td_table()
    return td_table[E_i]


def import_td_table():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../Tables/' + 'Delay_table.xlsx')
    matrix = pd.read_excel(path).values
    td_table = {}
    for row in matrix:
        td_table.update({int(row[0]): row[1]})
    return td_table


def import_T0_table():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../Tables/' + 'T0_vs_Energy.xlsx')
    matrix = pd.read_excel(path).values
    t0_table = {}
    for row in matrix:
        t0_table.update({str(row[0]): row[1]})
    return t0_table


def get_T0(calibration, energy):
    T0_table = import_T0_table()
    return T0_table[calibration]


def get_t_off_table():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../Tables/' + 'time_offset.xlsx')
    matrix = pd.read_excel(path).values
    t_off_table = {}
    for row in matrix:
        t_off_table.update({row[0]: row[1]})
    return t_off_table


def get_t_off(E_i):
    t_off_table = get_t_off_table()
    return t_off_table[E_i]
    
    


    

    
    
    
    
    
    
    
