#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 14:01:55 2018

@author: alexanderbackis
"""

# =======  LIBRARIES  ======= #
import os
import pandas as pd
import numpy as np
import cluster as clu
import plot as pl
import matplotlib.pyplot as plt
import zipfile
import shutil
import imageio
import warnings

def choose_specifications(options):
    
    def get_count_range():
        count_min = input('Lower count boundary: ')
        count_max = input('Upper count boundary: ')
        count_min = int(count_min)
        count_max = int(count_max)
        
        if count_min <= 0:
            count_min = 1
        
        return [count_min, count_max]
    
    def get_multiplicity_filter():
        mw_min = input('Minimum wire multiplicity: ')
        mw_max = input('Maximum wire multiplicity: ')
        mw_min = int(mw_min)
        mw_max = int(mw_max)
        mg_min = input('Minimum grid multiplicity: ')
        mg_max = input('Maximum grid multiplicity: ')
        mg_min = int(mg_min)
        mg_max = int(mg_max)
        return [mw_min, mw_max, mg_min, mg_max]
    
    def get_count_threshold():
        lower_thres = input('Lower count threshold: ')
        upper_thres = input('Upper count threshold: ')
        lower_thres = int(lower_thres)
        upper_thres = int(upper_thres)
        return [lower_thres, upper_thres]
    
    def get_exclude_channels():
        exclude_channels = [int(x) for x in 
                            input('Enter channels to exclude, ' +
                                  'use spaces to separate: ').split()]
        return exclude_channels
    
    def get_include_channels():
        include_channels = [int(x) for x in 
                            input('Enter channels to include, ' +
                                  'use spaces to separate: ').split()]
        return include_channels
    
    def get_log_lin_scale():
        log_lin = input('Use logarithmic scale? (y/n): ')
        if log_lin == 'y':
            return True
        else:
            return False
    
    def get_ADC_threshold():
        ADC_threshold = input('ADC threshold: ')
        ADC_threshold = int(ADC_threshold)
        return ADC_threshold
    
    def get_transparacy_factor():
        alpha = input('Insert transparancy factor (0 minimum, 1 maximum): ')
        alpha = float(alpha)
        return alpha
    
    def get_number_of_bins():
        number_bins = input('Number of bins: ')
        number_bins = int(number_bins)
        return number_bins
    
    def get_range():
        min_ToF = input('Minimum ToF: ')
        max_ToF = input('Maximum ToF: ')
        min_ToF = int(min_ToF)
        max_ToF = int(max_ToF)
        return [min_ToF, max_ToF]
    
    def get_buses():
        buses = [int(x) for x in input('Enter buses to include, ' + 
                                       'uses spaces to separate: ').split()]
        return buses
    
    def get_ADC_filter():
        min_ADC = input('Minimum ADC: ')
        max_ADC = input('Maximum ADC: ')
        min_ADC = int(min_ADC)
        max_ADC = int(max_ADC)
        
        return  [min_ADC, max_ADC]
    
    def get_timestamp_filter():
        min_ts = input('Minimum timestamp: ')
        max_ts = input('Maximum timestamp: ')
        min_ts = int(min_ts)
        max_ts = int(max_ts)
        return [min_ts, max_ts]
    
    def get_ToF_filter():
        min_tof = input('Minimum ToF: ')
        max_tof = input('Maximum ToF: ')
        min_tof = int(min_tof)
        max_tof = int(max_tof)
        return [min_tof, max_tof]
    
    def get_E_range():
        min_ToF = input('Minimum energy [meV]: ')
        max_ToF = input('Maximum energy [meV]: ')
        min_ToF = int(min_ToF)
        max_ToF = int(max_ToF)
        return [min_ToF, max_ToF]

    get_spec =  {'Count range': get_count_range, 
                 'ADC filter': get_ADC_filter,
                 'Multiplicity filter': get_multiplicity_filter,
                 'Time-stamp filter': get_timestamp_filter,
                 'Lower and upper count threshold': get_count_threshold,
                 'Exclude channels': get_exclude_channels,
                 'Include channels': get_include_channels,
                 'Log/Lin-scale': get_log_lin_scale,
                 'ADC threshold': get_ADC_threshold,
                 'Transparacy factor': get_transparacy_factor,
                 'Number of bins': get_number_of_bins,
                 'Range': get_range,
                 'Choose specific bus(es)': get_buses,
                 'ToF filter': get_ToF_filter,
                 'Energy range': get_E_range}
    
    spec_type_names = ['Count range', 'ADC filter', 'Multiplicity filter', 
                       'Lower and upper count threshold', 'Time-stamp filter',
                       'Exclude channels', 'Include channels', 'Log/Lin-scale',
                       'ADC threshold', 'Transparacy factor', 'Number of bins',
                       'Range', 'Choose specific bus(es)', 'ToF filter', 
                       'Energy range']
    
    specifications = {}
    for specification in spec_type_names:
        specifications.update({specification: None})
    
    print()
    print('***************** specifications ****************')
    print('-------------------------------------------------')
    for i, spec in enumerate(spec_type_names):
        if spec in options:
            print(str(i+1) + '. ' + str(spec))
    
    print('\nChoose specification(s). Use space(s) to separate choices.')

    choices = [int(x) for x in input('>> ').split()]
        
    for choice in choices:
        spec_type = spec_type_names[choice-1]
        specifications[spec_type] = get_spec[spec_type]()
        
    return specifications
    

def print_key_numbers(module_order, events, coincident_events):
        
    for i, bus in enumerate(module_order):
        if i % 3 == 0:
            print('\nDetector ' + str(bus // 3 + 1) )
            print('......................')
        
        print('-- Bus ' + str(bus) + ' --')
        print('Number of events ' + '          : ' + str(events[events.Bus == bus].shape[0])
                + ' (Wire events: ' + str(events[(events.Channel < 80) & (events.Bus == bus)].shape[0]) 
                + '; Grid events: ' + str(events[(events.Channel >= 80) & (events.Bus == bus)].shape[0]) 
                + ')')
        print('Number of coincident events: ' 
              + str(coincident_events[coincident_events.Bus == bus].shape[0]))
        
        no_events_ch = []
        for channel in range(0,120):
            if(events[(events.Channel == channel) & 
                      (events.Bus == bus)].shape[0] == 0):
                no_events_ch.append(channel)
        
        print('Channels with no events    : ' + str(no_events_ch))
        print()
            
    input('\nPress "Enter" when done.\n>> ')
    
    

def create_plot_folder(data_set):
    dirname = os.path.dirname(__file__)
    folder = os.path.join(dirname, '../Plot/' + data_set + '/')
    mkdir_p(folder)
    
    
def create_output_folder(data_set):
    dirname = os.path.dirname(__file__)
    folder = os.path.join(dirname, '../Output/' + data_set + '/')
    mkdir_p(folder)
    
    
def find_He3_measurement_id(calibration):
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../Tables/experiment_log.xlsx')
    matrix = pd.read_excel(path).values
    measurement_table = {}
    for row in matrix:
        measurement_table.update({row[1]: row[0]})
    return measurement_table[calibration]
    
    
    
def mkdir_p(mypath):
    '''Creates a directory. equivalent to using mkdir -p on the command line'''

    from errno import EEXIST
    from os import makedirs,path

    try:
        makedirs(mypath)
    except OSError as exc: # Python >2.5
        if exc.errno == EEXIST and path.isdir(mypath):
            pass
        else: raise

def initialise_detector_types(number_of_detectors):
    print('Enter detector type(s), type "ESS" or "ILL".')
    
    detector_types = []
    for i in range(0, number_of_detectors):
        detector_type = input('Detector ' + str(i+1) + ': ')
        detector_types.append(detector_type)
    
    exceptions = []
    for i, detector in enumerate(detector_types):
        if detector == "ILL":
            temp = np.arange(3*i,3*i+3,1)
            for exception in temp:
                exceptions.append(exception)
    
    return detector_types, exceptions
    

def choose_data_set():
    not_int = True
    not_in_range = True
    while (not_int or not_in_range):
        print()
        print('*************** Choose a data set ***************')
        print('-------------------------------------------------')
        for i, file in enumerate(files):
            print(str(i+1) + '. ' + str(file))
        print('---------------------------------------------')
        print(str(len(files)+1) + '. Select several data sets')
        print(str(len(files)+2) + '. Select interval of data sets')
        print('---------------------------------------------')
    
        file_number = input('\nEnter a number between 1-' + 
                            str(len(files)+2) + '.\n>> ')
    
        try:
            file_number = int(file_number)
            not_int = False
            not_in_range = (file_number < 1) | (file_number > len(files)+2)
        except ValueError:
            pass
    
        if not_int or not_in_range:
            print('\nThat is not a valid number.')
    
    data_sets = []
    number_of_files = 1
    if file_number <= len(files):
        data_sets.append(files[int(file_number) - 1])
    elif file_number == len(files) + 1:
        print('Enter data sets to import, use space(s) to separate choices.')
        choices = [int(x) for x in input('>> ').split()]
        for choice in choices:
            data_sets.append(files[choice-1])
    elif file_number == len(files) + 2:
        start = input('Start file: ')
        end = input('End file: ')
        start = int(start)
        end = int(end)
        number_of_files = end - start + 1
        for choice in range(start, end+1):
            data_sets.append(files[choice-1])
    
    print('Use standard module order and detector types (y/n)?')
    answer = input('>> ')
    
    number_of_detectors = None
    module_order = None
    detector_types = None
    if answer == 'y':
        number_of_detectors = 3
        module_order = [0,1,2,3,4,5,6,7,8]
        detector_types = ['ILL', 'ESS', 'ESS']
        exceptions = [0,1,2]
    else:
        number_of_detectors, module_order = choose_number_modules()
        detector_types, exceptions = initialise_detector_types(number_of_detectors)
        print()
    
    
    print('Import full file(s) (y/n)?')
    ans = input('>> ')
    
    max_size = np.inf
    if ans == 'n':
        print('Enter amount of data in MB to import (minimum size is 1 MB).')
        max_size = input('>> ')
        max_size = int(max_size)
    
    discard_glitch = False
    print('Discard glitch events (y/n)?')
    glitch_ans = input('>> ')
    glitch_mid = np.ones(number_of_files) * 0.5
    if glitch_ans == 'y':
        discard_glitch = True
        print('Change glitch mid (y/n)?')
        glitch_mid_ans = input('>> ')
        if glitch_mid_ans == 'y':
            print('Enter ' + str(number_of_files) + ' fractions of max: ')
            glitch_mid = [float(x) for x in input('>> ').split()]
        
        
    print('Keep only coincident events (y/n)?')
    ce_ans = input('>> ')
    keep_only_ce = False
    if ce_ans == 'y':
        keep_only_ce = True 
    print('Enter incident neutron energy E_i:')
    E_i = input('E_i [meV]: ')
    E_i = float(E_i)
    print(E_i)
    
    print('Choose calibration: ')
    calibrations =  ['High_Resolution', 'High_Flux', 'RRM']
    for i, calibration in enumerate(calibrations):
        print('    ' + str(i+1) + '. ' + calibration)
    print('Enter a number between 1-3.')
    selection = input('>> ')
    selection = int(selection)
    calibration = calibrations[selection-1]
    calibration = 'Van__3x3_' + calibration + '_Calibration_' + str(E_i)
    
    
    coincident_events = pd.DataFrame()
    events = pd.DataFrame()
    triggers = pd.DataFrame()
    measurement_time = 0
    for i, data_set in enumerate(data_sets):
        print()
        print('-- File ' + str(i+1) + '/' + str(len(data_sets)) + ' --')
        data_temp = clu.import_data(data_set, max_size)
        ce_temp, e_temp, t_temp = clu.cluster_data(data_temp, exceptions, E_i,
                                                   calibration)
        
        
        if discard_glitch:
            ce = ce_temp
            e = e_temp
            ce_red = ce[(ce['wM'] >= 80) & (ce['gM'] >= 40)]
            if len(ce_red.index) == 0:
                pass
            else:
                # Filter glitch events in begining and end by diving data
                # in two parts (f: first, s: second) and finding first 
                # and last glitch event.
                
                mid_point = ce.tail(1)['Time'].values[0] * glitch_mid[i]
                ce_f = ce_temp[(ce_temp['Time'] < mid_point)]
                ce_s = ce_temp[(ce_temp['Time'] > mid_point)]
                ce_red_f = ce_f[(ce_f['wM'] >= 80) & (ce_f['gM'] >= 40)]
                ce_red_s = ce_s[(ce_s['wM'] >= 80) & (ce_s['gM'] >= 40)]
                
                data_start = None
                data_end = None
                if ce_red_f.shape[0] > 0:
                    data_start = ce_red_f.tail(1)['Time'].values[0]
                else:
                    data_start = 0
                
                if ce_red_s.shape[0] > 0:
                    data_end = ce_red_s.head(1)['Time'].values[0]
                else:
                    data_end = np.inf
                print('Data start: ' + str(ce.head(1)['Time'].values[0]))
                print('Data end: ' + str(ce.tail(1)['Time'].values[0]))
                print('No-glitch-data start: ' + str(data_start))
                print('No-glitch-data end: ' + str(data_end))
                print('Size ce before reduction: ' + str(ce.shape[0]))
                ce = ce_temp[  (ce_temp['Time'] > data_start)
                             & (ce_temp['Time'] < data_end)]
                print('Size ce after reduction: ' + str(ce.shape[0]))
                print('Size e before reduction: ' + str(e_temp.shape[0]))
                e = e_temp[  (e_temp['Time'] > data_start)
                           & (e_temp['Time'] < data_end)]
                print('Size e after reduction: ' + str(e.shape[0]))
            
            start_time = 0
            end_time = 0
            if ce.shape[0] > 0:
                start_time = ce.head(1)['Time'].values[0]
                end_time = ce.tail(1)['Time'].values[0]
            
            coincident_events = coincident_events.append(ce)
            if not keep_only_ce:
                events = events.append(e)
            measurement_time += (end_time - start_time) * 62.5e-9
            print('Measurement time: ' + str(measurement_time))
        else:
            start_time = ce_temp.head(1)['Time'].values[0]
            end_time = ce_temp.tail(1)['Time'].values[0]
            measurement_time += (end_time - start_time) * 62.5e-9
            coincident_events = coincident_events.append(ce_temp)
            if not keep_only_ce:
                events = events.append(e_temp)
                

        triggers = triggers.append(t_temp)
            
        print('len(e): ' + str(events.shape[0]))
        print('len(triggers): ' + str(triggers.shape[0]))
                
    if len(data_sets) < 2:
        pass
    else:
        data_sets = [data_sets[0], '...']
    
    data_sets = str(data_sets)
    
    coincident_events.reset_index(drop=True, inplace=True)
    events.reset_index(drop=True, inplace=True)
    triggers.reset_index(drop=True, inplace=True)
    
    return (coincident_events, events, data_sets, triggers, 
            number_of_detectors, module_order, detector_types, 
            measurement_time, E_i, calibration)

def choose_number_modules():
    modules = [0,1,2,3,4,5,6,7,8]
    not_int = True
    not_in_range = True
    while (not_int or not_in_range):
        number_of_detectors = input('\nHow many detectors? (' +
                                    'Enter a number between 1-3)\n>>')
    
        try:
            number_of_detectors = int(number_of_detectors)
            not_int = False
            not_in_range = not (0 < number_of_detectors < 4)
        except ValueError:
            pass
    
        if not_int or not_in_range:
            print('\nThat is not a valid number.\n')
    
    return number_of_detectors, modules[0:3*number_of_detectors]

def choose_analysis_type(module_order, data_set, E_i, measurement_time, 
                         calibration):
    
    finished_with_analysis = False
    analysis_name_vec = ['PHS (1D)', 'PHS (2D)', 'PHS (3D)', 
                         'Coincidence Histogram (2D)', 
                         'Coincidence Histogram (3D)', 
                         'Coincidence Histogram (Front, Top, Side)',
                         'Multiplicity',
                         'Scatter Map (collected charge in wires and grids)', 
                         'ToF Histogram', 'Events per channel', 
                         'Timestamp and Trigger', 
                         'Delta E (compare filters)', 
                         'Delta E',
                         'ToF vs d + dE',
                         'Compare cold and thermal',
                         'Compare MG and Helium-tubes',
                         'Plotly interactive ToF Histogram',
                         'dE - loglog-plot',
                         'Neutrons vs Gammas scatter plot',
                         'Rate Repetition Mode',
                         'Plot Helium data',
                         'ToF per voxel']
    
    figs = []
    paths = []
    
    while(not finished_with_analysis):
        print()
        print('******************* analysis ********************')
        print('-------------------------------------------------')
        for i, name in enumerate(analysis_name_vec):
            print(str(i+1) + '. ' + name)
        print('-------------------------------------------------')
        print(str(len(analysis_name_vec)+1) + '. ' + 'Plot')
        print(str(len(analysis_name_vec)+2) + '. ' + 'Back to main meny')
        print('-------------------------------------------------')
        print('\nChoose an analysis by entering a number between 1-' 
                              + str(len(analysis_name_vec)) + '.\nEnter ' + 
                              str(len(analysis_name_vec)+1) + ' to plot ' +
                              'and ' + str(len(analysis_name_vec)+2) + ' to '
                              + 'go back to main meny.')
        analysis_type = input('>> ')

        try:
            analysis_type = int(analysis_type)
        except ValueError:
            print("That's not an int!")
            
        fig = None
        
        if analysis_type <= len(analysis_name_vec):
            fig = plt.figure()
            name = (str(analysis_type) + '. ' 
                   + analysis_name_vec[analysis_type-1] + '\nData set: ' 
                   + data_set)
        
        if analysis_type == 1:
            bus = input('Module ID (select a number between ' 
                        + str(min(module_order)) + '-' 
                        + str(max(module_order)) + '): ')
            bus = int(bus)
            ChVec = [int(x) for x in input('Channel(s) (use spaces to separate): ').split()]
            choice = input('\nFurther specifications? (y/n).\n>> ')
            
            loglin = False
            count_range = None
            temp_events = events
            if choice == 'y':
                options = ['Log/Lin-scale', 'Count range']
                specs = choose_specifications(options)
                loglin = specs['Log/Lin-scale']
                count_range = specs['Count range']
                    
            
            print('Loading...')
            fig, path = pl.plot_PHS_several_channels(fig, name, temp_events, bus, 
                                                     ChVec, data_set, 
                                                     loglin = loglin,
                                                     count_range = count_range)
            print('Done!')
        
        if analysis_type == 2:
            choice = input('\nFurther specifications? (y/n).\n>> ')
            
            count_range = [1, 3000]
            buses = module_order
            temp_events = events
           
            if choice == 'y':
                options = ['Count range', 'Choose specific bus(es)']
                specs = choose_specifications(options)
                
                if specs['Choose specific bus(es)'] != None:
                    buses = specs['Choose specific bus(es)']
                
                if specs['Count range'] != None:
                    count_range = specs['Count range']
                
            print('Loading...')
            fig, path = pl.plot_PHS_buses(fig, name, temp_events, buses, 
                                          data_set, count_range=count_range)
 
            print('Done!')
    
        if analysis_type == 3:
            bus = input('Which module? Enter a number between ' 
                        + str(min(module_order)) + '-' +
                        str(max(module_order)) + '\n>>')
            bus = int(bus)
            print('Loading...')
            fig, path = pl.plot_3D_new(fig, name, events, bus, data_set)
            print('Done!')

        if analysis_type == 4:
            choice = input('\nFurther specifications? (y/n).\n>> ')
            count_range = [1, 10000]
            ADC_filter = None
            buses = module_order
            m_range = None
            ce_temp = coincident_events
            ts_range = [0,np.inf]
            if choice == 'y':
                options = ['Count range', 'Choose specific bus(es)', 
                           'ADC filter', 'Multiplicity filter',
                           'Time-stamp filter', 'ToF filter']
                specs = choose_specifications(options)
                
                if specs['Count range'] != None:
                    count_range = specs['Count range']
                
                if specs['Choose specific bus(es)'] != None:
                    buses = specs['Choose specific bus(es)']
                
                if specs['ADC filter'] != None:
                    ADC_filter = specs['ADC filter']
                
                if specs['Multiplicity filter'] != None:
                    m_range = specs['Multiplicity filter']
                
                if specs['Time-stamp filter'] != None:
                    ts_range = specs['Time-stamp filter']
         
                    min_ts = ts_range[0]
                    max_ts = ts_range[1]

                    ce_temp = ce_temp[(ce_temp['Time'] >= min_ts) &
                                      (ce_temp['Time'] <= max_ts)]
               
                if specs['ToF filter'] is not None:
                    tof_range = specs['ToF filter']

                    min_tof = tof_range[0]
                    max_tof = tof_range[1]

                    ce_temp = ce_temp[(ce_temp['ToF'] >= min_tof) &
                                      (ce_temp['ToF'] <= max_tof)]

            print('Loading...')
            fig, path = pl.plot_2D_hit_buses(fig, name, ce_temp, 
                                             buses, number_of_detectors, 
                                             data_set, count_range,
                                             ADC_filter, m_range, ts_range)
                
            print('Done!')
            
        if analysis_type == 5:
            choice = input('\nFurther specifications? (y/n).\n>> ')
            alpha = 1
            count_thres = None
            ADC_filter = None
            m_range = None
            ce_temp = coincident_events
            if choice == 'y':
                options = ['Transparacy factor', 'Lower and upper count threshold',
                           'ADC filter', 'Multiplicity filter', 'ToF filter']
                specs = choose_specifications(options)
                if specs['Lower and upper count threshold'] != None:
                    count_thres = specs['Lower and upper count threshold']
                
                if specs['Transparacy factor'] != None:
                    alpha = specs['Transparacy factor']
                
                if specs['ADC filter'] != None:
                    ADC_filter = specs['ADC filter']
                
                if specs['Multiplicity filter'] != None:
                    m_range = specs['Multiplicity filter']
                
                if specs['ToF filter'] is not None:
                    tof_range = specs['ToF filter']

                    min_tof = tof_range[0]
                    max_tof = tof_range[1]

                    ce_temp = ce_temp[(ce_temp['ToF'] >= min_tof) &
                                      (ce_temp['ToF'] <= max_tof)]
                   
            print('Loading...')
            fig, path = pl.plot_all_sides_3D(fig, name, ce_temp, 
                                                 module_order, count_thres, 
                                                 alpha, data_set, 
                                                 number_of_detectors,
                                                 ADC_filter, m_range)
            print('Done!')
        
        if analysis_type == 6:
            choice = input('\nFurther specifications? (y/n).\n>> ')
            
            count_range = [1e2, 3e4]
            ADC_filter = None
            m_range = None
            tof_range = None
            ce_temp = coincident_events
            if choice == 'y':
                options = ['Count range', 'ADC filter', 'Multiplicity filter',
                           'ToF filter']
                specs = choose_specifications(options)
                if specs['Count range'] != None:
                    count_range = specs['Count range']
                
                if specs['ADC filter'] != None:
                    ADC_filter = specs['ADC filter']
                
                if specs['Multiplicity filter'] != None:
                    m_range = specs['Multiplicity filter']
                
                if specs['ToF filter'] is not None:
                    tof_range = specs['ToF filter']

                    min_tof = tof_range[0]
                    max_tof = tof_range[1]

                    ce_temp = ce_temp[(ce_temp['ToF'] >= min_tof) &
                                      (ce_temp['ToF'] <= max_tof)]
                    
            
            print('Loading...')
            fig, path = pl.plot_all_sides(fig, name, module_order, ce_temp, 
                                  data_set, number_of_detectors, count_range,
                                  ADC_filter, m_range, tof_range)
            
            print('Done!')
    
        if analysis_type == 7:
            choice = input('\nFurther specifications? (y/n).\n>> ')
            m_range = [0,8,0,8]
            count_range = [1, 1e6]
            buses = module_order
            ADC_filter = None
            ce_temp = coincident_events
            ts_range = [0,np.inf]
            if choice == 'y':
                options = ['Multiplicity filter', 'Count range', 
                           'Choose specific bus(es)', 'ADC filter',
                           'Time-stamp filter']
                specs = choose_specifications(options)
                if specs['Multiplicity filter'] != None:
                    m_range = specs['Multiplicity filter']
                
                if specs['Count range'] != None:
                    count_range = specs['Count range']
                
                if specs['Choose specific bus(es)'] != None:
                    buses = specs['Choose specific bus(es)']
                
                if specs['ADC filter'] != None:
                    ADC_filter = specs['ADC filter']
                
                if specs['Time-stamp filter'] != None:
                    ts_range = specs['Time-stamp filter']
                    min_ts = ts_range[0]
                    max_ts = ts_range[1]
       
                    
           
                    ce_temp = ce_temp[(ce_temp['Time'] >= min_ts) &
                                      (ce_temp['Time'] <= max_ts)]
    
                
            
            print('Loading...')
            fig, path = pl.plot_2D_multiplicity_buses(fig, name, 
                                      ce_temp, buses, 
                                      number_of_detectors, data_set, m_range, 
                                      count_range, ADC_filter, ts_range)

            print('Done!')
    
        if analysis_type == 8:
            choice = input('\nFurther specifications? (y/n).\n>> ')
            
            
            if choice == 'y':
                options = ['Multiplicity filter', 'Exclude channels', 
                           'Choose specific bus(es)', 'Time-stamp filter']
                
                specs = choose_specifications(options)
                ce_temp = coincident_events
                
                minWM = 0
                maxWM = 100
                minGM = 0
                maxGM = 100
                
                if specs['Multiplicity filter'] != None:
                    minWM = specs['Multiplicity filter'][0]
                    maxWM = specs['Multiplicity filter'][1]
                    minGM = specs['Multiplicity filter'][2]
                    maxGM = specs['Multiplicity filter'][3]
                    
                exclude_channels = [-1]
                if specs['Exclude channels'] != None:
                    exclude_channels = specs['Exclude channels']
                
                buses = module_order
                if specs['Choose specific bus(es)'] != None:
                    buses = specs['Choose specific bus(es)']
                
                if specs['Time-stamp filter'] != None:
                    ts_range = specs['Time-stamp filter']
                    min_ts = ts_range[0]
                    max_ts = ts_range[1]
       
                    
                    ce_temp = ce_temp[(ce_temp['Time'] >= min_ts) &
                                      (ce_temp['Time'] <= max_ts)]
                
                print('Loading...')
                fig, path = pl.plot_charge_scatter_buses(fig, name, ce_temp, buses, 
                                     number_of_detectors, data_set, minWM, maxWM, minGM, 
                                     maxGM, exclude_channels, ts_range)
            else:
                print('Loading...')
                fig, path = pl.plot_charge_scatter_buses(fig, name, coincident_events, module_order, 
                                             number_of_detectors, data_set)
            print('Done!')

        if analysis_type == 9:
            choice = input('\nFurther specifications? (y/n).\n>> ')
            
            rnge = None
            number_bins = 1000
            
            if choice == 'y':
                options = ['Number of bins', 'Range', 'ADC filter', 
                           'Log/Lin-scale']
                specs = choose_specifications(options)
                ADC_filter = None
                if specs['Number of bins'] != None:
                    number_bins = specs['Number of bins']
                
                if specs['Range'] != None:
                    rnge = specs['Range']
                
                if specs['ADC filter'] != None:
                    ADC_filter = specs['ADC filter']
                
                if specs['Log/Lin-scale'] is not None:
                    log = specs['Log/Lin-scale']
                    
                
                print('Loading...')
                fig, path = pl.plot_ToF_histogram(fig, name, coincident_events, 
                                                  data_set, number_bins, rnge,
                                                  ADC_filter, log)
            else:
                print('Loading...')
                fig, path = pl.plot_ToF_histogram(fig, name, coincident_events, 
                                                  data_set, number_bins, rnge)
            print('Done!')
        
        if analysis_type == 10:
            choice = input('\nFurther specifications? (y/n).\n>> ')
            
            count_range = [1, 100000]
            log = False
            buses = module_order
            ADC_filter = None
                
            if choice == 'y':
                options = ['Count range', 'Log/Lin-scale', 
                           'Choose specific bus(es)', 'ADC filter']
                specs = choose_specifications(options)

                if specs['Count range'] != None:
                    count_range = specs['Count range']
                
                if specs['Log/Lin-scale'] != None:
                    log = specs['Log/Lin-scale']
                
                if specs['Choose specific bus(es)'] != None:
                    buses = specs['Choose specific bus(es)']
                    
                if specs['ADC filter'] != None:
                    ADC_filter = specs['ADC filter']
                
            
            print('Loading...')
            fig, path = pl.plot_event_count(fig, name, buses, 
                                            number_of_detectors, 
                                            data_set, events, log, 
                                            count_range, ADC_filter)

            print('Done!')
        
        if analysis_type == 11:
            choice = input('\nFurther specifications? (y/n).\n>> ')
            temp_ce = coincident_events
            if choice == 'y':
                options = ['Multiplicity filter']
                
                specs = choose_specifications(options)
                if specs['Multiplicity filter'] is not None:
                    m_range = specs['Multiplicity filter']
                    mw_min = m_range[0]
                    mw_max = m_range[1]
                    mg_min = m_range[2]
                    mg_max = m_range[3]
                    temp_ce = temp_ce[  
                              (temp_ce.wM >= mw_min) & (temp_ce.wM <= mw_max) 
                            & (temp_ce.gM >= mg_min) & (temp_ce.gM <= mg_max)
                                     ]
                
                
            print('Loading...')
            fig, path = pl.plot_timestamp_and_trigger(fig, name, data_set, 
                                    temp_ce, triggers)
            print('Done!')
            
        
        if analysis_type == 12:
            print('Adjust ToF-filter (y/n)?')
            adjust_ans = input('>> ')
            ToF_min = -np.inf
            ToF_max = np.inf
            if adjust_ans == 'y':
                ToF_min = input('ToF min: ')
                ToF_max = input('ToF max: ')
                ToF_min = int(ToF_min)
                ToF_max = int(ToF_max)

            print('Loading...')
            fig, path = pl.dE_histogram(fig, name, coincident_events, 
                                        data_set, E_i, ToF_min, ToF_max)

            print('Done!')
        
        if analysis_type == 13:
            print('Change left and right edge (y/n)?')
            edge_ans = input('>> ')
            if edge_ans == 'y':
                left_edge = input('Left edge [0<...<400]: ')
                right_edge = input('Right edge [0<...<400]: ')
                left_edge = int(left_edge)
                right_edge = int(right_edge)
            else:
                left_edge = 175
                right_edge = 220
            
            samples = ['Vanadium', 'C4H2I2S']
            print('Select a sample: ')
            for i, sample in enumerate(samples):
                print('    ' + str(i+1) + '. ' + sample)
            idx = input('>> ')
            idx = int(idx)
            sample = samples[idx-1]
                
            print('Loading...')
            fig, path = pl.dE_single(fig, name, coincident_events, 
                                           data_set, E_i, sample, left_edge, 
                                           right_edge)
            print('Done!')
        
        if analysis_type == 14:
            print('Plot separate (y/n)?')
            sep_ans = input('>> ')
            plot_separate = False
            if sep_ans == 'y':
                plot_separate = True
                
            print('Loading...')
            fig, path = pl.ToF_vs_d_and_dE(fig, name, coincident_events, 
                                           data_set, E_i, plot_separate)
            print('Done!')
            
        if analysis_type == 15:
            fig, path = pl.compare_cold_and_thermal(fig, name, data_set, E_i)
            print('Done!')
            
        if analysis_type == 16:
            print('Change MG and He3 offset (y/n)?')
            edge_ans = input('>> ')
            if edge_ans == 'y':
                MG_offset = input('MG offset [meV]: ')
                He3_offset = input('He3 offset [meV]: ')
                MG_offset = float(MG_offset)
                He3_offset = float(He3_offset)
            else:
                MG_offset = 0
                He3_offset = 0
            print('Use only pure aluminium vessel (y/n)?')
            al_ans = input('>> ')
            only_pure_al = False
            if al_ans == 'y':
                only_pure_al = True
            print('Adjust peak edges (y/n)?')
            adjust_ans = input('>> ')
            if adjust_ans == 'y':
                MG_l = input('MG left edge: ')
                MG_r = input('MG right edge: ')
                MG_l = int(MG_l)
                MG_r = int(MG_r)
            else:
                MG_l = 175
                MG_r = 220
                
                
            print('Loading...')
            fig, path = pl.compare_MG_and_He3(fig, name, coincident_events, 
                                              data_set, E_i, MG_offset, 
                                              He3_offset, only_pure_al,
                                              MG_l, MG_r)
            print('Done!')
        
        if analysis_type == 17:
            test_types = ['Wire ADC threshold', 'Grid ADC threshold', 
                          'Grid and Wire ADC threshold']
            print('*** Select a test type ***')
            for i, test_type in enumerate(test_types):
                print(str(i+1) + '. ' + test_type)
            test_ans = input('>> ')
            test_type = test_types[int(test_ans)-1]
            print('Loading...')
            pl.plotly_interactive_ToF(coincident_events, data_set, E_i, 
                                      test_type)
            print('Done!')
            
        if analysis_type == 18:
            print('Plot multiple energies (y/n)?')
            df_vec = []
            E_i_vec = []
            plot_ans = input('>> ')
            if plot_ans == 'y':
                clusters_folder = os.path.join(dirname, '../Clusters/')
                clu_files = os.listdir(clusters_folder)
                clu_files = [file for file in clu_files if file[-3:] == '.h5']
    
                print()
                print('************ Choose clusters to plot ************')
                print('-------------------------------------------------')
                for i, file in enumerate(clu_files):
                    print(str(i+1) + '. ' + file)
                print('Enter data sets to plot, use space(s) to separate choices.')
                choices = [int(x) for x in input('>> ').split()]
                for choice in choices:
                    file_name = clu_files[choice-1]
                    clu_path = clusters_folder + file_name
                    df_temp = pd.read_hdf(clu_path, 'coincident_events')
                    E_i_temp = pd.read_hdf(clu_path, 'E_i')['E_i'].iloc[0]
                    df_vec.append(df_temp)
                    E_i_vec.append(E_i_temp)
            else:
                df_vec = [coincident_events]
                E_i_vec = [E_i]
            
            
            
            print('Loading...')
            fig, path = pl.de_loglog(fig, name, df_vec, data_set, E_i_vec)
            print('Done!') 
        
        if analysis_type == 19:
            print('Adjust peak edges (y/n)?')
            adjust_ans = input('>> ')
            if adjust_ans == 'y':
                g_l = input('Gamma left edge: ')
                g_r = input('Gamma right edge: ')
                n_l = input('Neutron left edge: ')
                n_r = input('Neutron right edge: ')
                g_l = int(g_l)
                g_r = int(g_r)
                n_l = int(n_l)
                n_r = int(n_r)
            else:
                g_l = 240
                g_r = 253
                n_l = 300
                n_r = 450
            print('Loading...')
            fig, path = pl.neutrons_vs_gammas(fig, name, coincident_events,
                                              data_set, g_l, g_r, n_l, n_r)
            print('Done!') 
            
        
        if analysis_type == 20:
            print('Energies (use a space to separate): ')
            E_i_vec = [float(x) for x in input('>> ').split()]
            border = input('Border [us]: ')
            border = int(border)
            
            print('Loading...')
            fig, path = pl.RRM(fig, name, coincident_events, data_set, border,
                               E_i_vec)
            print('Done!')
            
        if analysis_type == 21:
            print('Calculate FWHM (y/n)?')
            FWHM = False
            FWHM_ans = input('>> ')
            if FWHM_ans == 'y':
                FWHM = True
            print('Use visualisation help (y/n)?')
            vis_help = False
            vis_help_ans = input('>> ')
            if vis_help_ans == 'y':
                vis_help = True
            print('Plot background (y/n)?')
            back_yes = False
            back_yes_ans = input('>> ')
            if back_yes_ans == 'y':
                back_yes = True
            
            print('Loading...')
            fig, path = pl.plot_He3_data(fig, coincident_events, data_set, 
                                         calibration, measurement_time, 
                                         E_i, FWHM, vis_help, back_yes)
            print('Done!')
        
        if analysis_type == 22:
            Bus = input('Bus: ')
            Bus = int(Bus)
            print('Loading...')
            pl.ToF_per_voxel(coincident_events, data_set, Bus)
            print('Done!')
            
        if ((analysis_type <= len(analysis_name_vec)) 
            and (analysis_type != 17) and (analysis_type != 22)):
            figs.append(fig)
            paths.append(path)
        
        if analysis_type == len(analysis_name_vec)+1:
            if len(figs) > 0:
                plt.show()
                print('\nSaving...')
                count = 1
                print('0%')
                for fig, path in zip(figs, paths):
                    fig.savefig(path, bbox_inches='tight')
                    print(str(round((float(count)/len(figs))*100)) + '%')
                    count += 1
                finished_with_analysis = True
            else:
                print('\nNothing to plot yet!')
                input('\nPress "Enter" to continue.\n>> ')
            
            
        if analysis_type == len(analysis_name_vec)+2:
            plt.close('all')
            finished_with_analysis = True
        

        

            
            
                

def main_meny(data_sets):
    not_int = True
    not_in_range = True
    choice = None
    while (not_int or not_in_range):
        print()
        print('******************* main menu *******************')
        print('-------------------------------------------------')
        print('Data set(s)      : ' + data_sets)
        print('Module order     : ' + str(module_order))
        print('Detector type(s) : ' + str(detector_types))
        print('Measurement time : ' + str(round((measurement_time), 4)) + ' seconds')
        print('-------------------------------------------------')
        print('1. Change module order')
        print('2. Perform an analysis')
        print('3. Create animation')
        print('4. Save clusters')
        print('5. Export clusters')
        print('6. Print events/s')
        print('7. Quit')
    
        choice = input('\nChoose an alternative by entering a number \n' +
                       'between 1-7.\n>> ')
        
        try:
            choice = int(choice)
            not_int = False
            not_in_range = (choice < 1) | (choice > 7)
        except ValueError:
            pass
    
        if not_int or not_in_range:
            print('\nThat is not a valid number.')
    
    return choice

def save_clusters(coincident_events, events, triggers, number_of_detectors,
                  module_order, detector_types, data_set, measurement_time, 
                  E_i, calibration):
    print('Saving...')
    print('0%')
    dirname = os.path.dirname(__file__)
    folder = os.path.join(dirname, '../Clusters/')
    path = folder + data_set + '.h5'
    
    coincident_events.to_hdf(path, 'coincident_events', complevel = 9)
    print('25%')
    events.to_hdf(path, 'events', complevel = 9)
    print('50%')
    
    triggers.to_hdf(path, 'triggers', complevel = 9)
    print('75%')
    
    number_det = pd.DataFrame({'number_of_detectors': [number_of_detectors]})
    mod_or     = pd.DataFrame({'module_order': module_order})
    det_types  = pd.DataFrame({'detector_types': detector_types})
    da_set     = pd.DataFrame({'data_set': [data_set]})
    mt         = pd.DataFrame({'measurement_time': [measurement_time]})
    ca         = pd.DataFrame({'calibration': [calibration]})
    ei = pd.DataFrame({'E_i': [E_i]})
        
    number_det.to_hdf(path, 'number_of_detectors', complevel = 9)
    mod_or.to_hdf(path, 'module_order', complevel = 9)
    det_types.to_hdf(path, 'detector_types', complevel = 9)
    da_set.to_hdf(path, 'data_set', complevel = 9)
    mt.to_hdf(path, 'measurement_time', complevel=9)
    ei.to_hdf(path, 'E_i', complevel=9)
    ca.to_hdf(path, 'calibration', complevel=9)
    print('100%')
    print('Done!')
    
def export_clusters(coincident_events, triggers, data_sets):
    print('Exporting...')
    mw_min = 0
    mw_max = 10
    mg_min = 0
    mg_max = 10
    temp_ce = coincident_events
    temp_ce = temp_ce[  (temp_ce.wM >= mw_min) & (temp_ce.wM <= mw_max) 
                      & (temp_ce.gM >= mg_min) & (temp_ce.gM <= mg_max)]
    np_matrix = temp_ce[['Time', 'ToF', 'wCh', 'wADC', 'gCh', 'gADC', 'd',
                         'dE']].values
    
       
    folder = get_output_path(data_sets)
    print('0%')
    ce_path = folder + 'coincident_events.dat'
    np.savetxt(ce_path, np_matrix, delimiter=",")
    print('25%')
    ToF_path = folder + 'ToF.dat'
    np.savetxt(ToF_path, temp_ce['ToF'], delimiter=",")
    print('50%')
    trigpath = folder + 'triggers.dat'
    np.savetxt(trigpath, triggers, delimiter=",")
    print('75%')
    stamppath = folder + 'timestamps.dat'
    np.savetxt(stamppath, temp_ce['Time'], delimiter=",")
    print('100%')
    print('Done!')
    
def get_output_path(data_set):
    dirname = os.path.dirname(__file__)
    folder = os.path.join(dirname, '../Output/' + data_set + '/')
    return folder

def get_plot_path(data_set):
    dirname = os.path.dirname(__file__)
    folder = os.path.join(dirname, '../Plot/' + data_set + '/')
    return folder
    
    
def intro_meny():
    
    isDone = False    
    while not isDone:
        print('*************** Choose an action ****************')
        print('-------------------------------------------------')
        print('1. Import and cluster')
        print('2. Load saved clusters')
        print('3. Unzip file(s)')
        print()
        print('Enter a number between 1-3.')
        ans = input('>> ')
        ans = int(ans)
    
        if ans == 1:
            isDone = True
        elif ans == 2:
            isDone = True
        elif ans == 3:
            unzip_meny()
        
        print()
    
    
    if ans == 1:
        return 'n'
    else:
        return 'y'
            
            
def unzip_meny():
    dirname = os.path.dirname(__file__)
    zip_folder = os.path.join(dirname, '../Zips/')
    zips = os.listdir(zip_folder)
    zips = [Zip for Zip in zips if Zip[-4:] == '.zip']
    print()
    print('************ Choose file(s) to unzip ************')
    print('-------------------------------------------------')
    for i, Zip in enumerate(zips):
        print(str(i+1) + '. ' + Zip)
    print('-------------------------------------------------')
    print(str(len(zips)+1) + '. Unzip all')
    
    print(  '\nEnter a numbers between 1-' + str(len(zips)) 
          + ' to chooose\nfile(s). Use spaces to separate choices.\n' 
          + 'Press ' + str(len(zips)+1) + ' to unzip all.')
    to_unzip = [int(x) for x in input('>> ').split()]
    
    if len(to_unzip) == 1 and to_unzip[0] == len(zips)+1:
        to_unzip = np.arange(1,len(zips)+1,1)
    
    print('Unzipping...')
    print('0%')
    for index in to_unzip:
        zip_file = zips[index-1]
        zip_path = zip_folder + zip_file

        with zipfile.ZipFile(zip_path,"r") as zip_ref:
            zip_temp_folder = zip_folder + str(zip_file[0:-4]) + '/'    
            zip_ref.extractall(zip_temp_folder)
            
            temp_list = os.listdir(zip_temp_folder)
            source_file = None
            for temp_file in temp_list:
                if temp_file[-8:] == '.mvmelst':
                    source_file = temp_file
            
            
            source      = zip_temp_folder + source_file
            destination = os.path.join(dirname, '../Data/') + zip_file
            shutil.move(source, destination)
            shutil.rmtree(zip_temp_folder, ignore_errors=True)
        
        percentage_finished = str(int(round((index/len(to_unzip))*100,1))) + '%'
        print(percentage_finished)
    
    print('Done!')

def perspectives_animation(coincident_events, data_sets, start, stop, step):
    tof_vec = range(start, stop, step)
    ce = coincident_events
    ce = ce[(ce.wM < 80) & (ce.gM < 40)]
    
    print('Further specification (y/n)?')
    ansAni = input('>> ')
    count_range = None
    if ansAni == 'y':
        count_min = input('Lower count boundary: ')
        count_max = input('Upper count boundary: ')
        count_min = int(count_min)
        count_max = int(count_max)
        
        if count_min <= 0:
            count_min = 1
        
        count_range = [count_min, count_max]
    else:
        count_range = [0, 100]
    ADC_filter = None
    m_range = None
    name = ('Coincidence Histogram (Front, Top, Side)\n' + 'Data set: '
            + str(data_sets))
    temp_folder = get_plot_path('temp_folder')
    mkdir_p(temp_folder)
    number_bins = 500
    isAnimation=True
    print()
    print('Animating...')
    for i in range(0, (stop-start)//step-1):
        print( str(round((i/(((stop-start)//step)-2))*100)) + '%')
        fig = plt.figure()
        min_tof = tof_vec[i]
        max_tof = tof_vec[i+1]
        tof_range = [min_tof, max_tof]
        ce_temp = ce[(ce['ToF'] >= min_tof) & (ce['ToF'] <= max_tof)]
        
        plt.subplot2grid((2, 3), (1, 0), colspan=3)
        plt.hist(ce.ToF, bins=number_bins, range=[start, stop], color='b')
        plt.hist(ce_temp.ToF, bins=number_bins, range=[start, stop], color='r')
        plt.title('ToF')
        plt.xlabel('ToF [TDC channels]')
        plt.ylabel('Counts  [a.u.]')


        fig, path = pl.plot_all_sides(fig, name, module_order, ce_temp,
                                      data_sets, number_of_detectors,
                                      count_range, ADC_filter, m_range,
                                      tof_range, isAnimation)
        fig.savefig(temp_folder + str(i) + '.png')
        plt.close()
    
    images = []
    files = os.listdir(temp_folder)
    files = [file[:-4] for file in files if file[-9:] != '.DS_Store' 
             and file != '.gitignore']
    
    output_path = get_output_path(data_sets) + 'Perspectives_ToF_sweep.gif'
    
    
    for filename in sorted(files, key=int):
        images.append(imageio.imread(temp_folder + filename + '.png'))
    imageio.mimsave(output_path, images)
    
    shutil.rmtree(temp_folder, ignore_errors=True)
    print('Done!')

def animation_3D(coincident_events, data_sets, start, stop, step):
    tof_vec = range(start, stop, step)
    ce = coincident_events
    ce = ce[(ce.wM < 80) & (ce.gM < 40)]
    ADC_filter = None
    m_range = None
    name = ('Coincidence Histogram (3D)\n' + 'Data set: '
            + str(data_sets))
    temp_folder = get_plot_path('temp_folder')
    mkdir_p(temp_folder)
    number_bins = 500
    alpha = 1
    isAnimation = True
    countThres = [1, np.inf]
    ADC_filter = None
    print()
    print('Animating...')
    for i in range(0, (stop-start)//step-1):
        print( str(round((i/(((stop-start)//step)-2))*100)) + '%')
        fig = plt.figure()
        fig.set_size_inches(14, 7)
        min_tof = tof_vec[i]
        max_tof = tof_vec[i+1]
        tof_range = [min_tof, max_tof]
        ce_temp = ce[(ce['ToF'] >= min_tof) & (ce['ToF'] <= max_tof)]
        
        plt.subplot(1,2,2)
        plt.hist(ce.ToF, bins=number_bins, range=[start, stop], color='b')
        plt.hist(ce_temp.ToF, bins=number_bins, range=[start, stop], color='r')
        plt.title('ToF')
        plt.xlabel('ToF [TDC channels]')
        plt.ylabel('Counts  [a.u.]')

        plt.subplot(1,2,1)
        pl.plot_all_sides_3D(fig, name, ce_temp, module_order, 
                             countThres, alpha, data_sets, number_of_detectors,
                             ADC_filter, m_range, isAnimation)
        
        plt.tight_layout()
        
        fig.savefig(temp_folder + str(i) + '.png')
        plt.close()

    
    images = []
    files = os.listdir(temp_folder)
    files = [file[:-4] for file in files if file[-9:] != '.DS_Store' 
             and file != '.gitignore']
    
    output_path = get_output_path(data_sets) + '3D_ToF_sweep.gif'
    
    
    for filename in sorted(files, key=int):
        images.append(imageio.imread(temp_folder + filename + '.png'))
    imageio.mimsave(output_path, images)
    
    shutil.rmtree(temp_folder, ignore_errors=True)
    print('Done!')
    
    

def animation_menu(coincident_events, data_sets, E_i, measurement_time):
    
    analysis_name_vec = ['PHS (1D)', 'PHS (2D)', 'PHS (3D)', 
                         'Coincidence Histogram (2D)', 
                         'Coincidence Histogram (3D)', 
                         'Coincidence Histogram (Front, Top, Side)',
                         'Multiplicity',
                         'Scatter Map (collected charge in wires and grids)', 
                         'ToF Histogram', 'Events per channel', 
                         'Timestamp and Trigger']
    
    animationDone = False
    while animationDone is False:
        print()
        print('************ Choose animation type **************')
        print('-------------------------------------------------')
        print('1. Time-of-Flight sweep')
        print('2. Time-stamp sweep')
        print('-------------------------------------------------')
        print('3. Back to main menu')
        print()
        print('Enter a number between 1-2. Press 3 to go back to\nthe main menu.')
        ans = input('>> ')
        ans = int(ans)

        if ans == 1:
            ToF_menu(analysis_name_vec)
            animationDone = True
        elif ans == 2:
            TS_menu(analysis_name_vec)
            animationDone = True
        elif ans == 3:
            animationDone = True

def ToF_menu(analysis_name_vec):
    
    animationSelected = False
    while animationSelected is False:
        print()
        print('*************** Choose plot type ****************')
        print('-------------------------------------------------')
        for i in range(4, 6):
            print(str(i+1) + '. ' + analysis_name_vec[i])
        print('-------------------------------------------------')
        print('7. Back to previous menu.')
        print()
        print('Enter a number between 5-6. Press 7 to go back.')
        selection = input('>> ')
        selection = int(selection)
        
        if selection == 5:
            start, stop, step = get_ToF_start_stop_step()
            animation_3D(coincident_events, data_sets, start, stop, step)
            animationSelected = True
        elif selection == 6:
            start, stop, step = get_ToF_start_stop_step()
            perspectives_animation(coincident_events, data_sets, start, stop,
                                   step)
            animationSelected = True
        elif selection == 7:
            animationSelected = True


def TS_menu(analysis_name_vec):
    animationSelected = False
    while animationSelected is False:
        print()
        print('*************** Choose plot type ****************')
        print('-------------------------------------------------')
        for i in range(5, 6, 1):
            print(str(i+1) + '. ' + analysis_name_vec[i])
        print('-------------------------------------------------')
        print(str(i+2) + '. Back to previous menu.')
        print()
        print('Enter a number between 6-6. Press 7 to go back.')
        selection = input('>> ')
        selection = int(selection)
        
        if selection == 6:
            start, stop, step = get_TS_start_stop_step()
            perspectives_animation_TS(coincident_events, data_sets, start, 
                                      stop, step)
            animationSelected = True
        
        if selection == i+2:
            animationSelected = True

        
def get_ToF_start_stop_step():
    start = input('Start ToF: ')
    start = int(start)
    stop = input('End ToF  : ')
    stop = int(stop)
    step = input('Step     : ')
    step = int(step)
    return start, stop, step

def get_TS_start_stop_step():
    start = input('Start Time: ')
    start = int(start)
    stop = input('End Time  : ')
    stop = int(stop)
    step = input('Step      : ')
    step = int(step)
    return start, stop, step


def perspectives_animation_TS(coincident_events, data_sets, start, stop, step):
    TS_vec = range(start, stop, step)
    ce = coincident_events
    ce = ce[(ce['Time'] >= start) & (ce['Time'] <= stop)]
    ce = ce[(ce['wCh'] != -1) & (ce['gCh'] != -1)]
    event_numbers = ce.index.tolist()
    count_range = [1, 200]
    ADC_filter = None
    m_range = None
    name = ('Coincidence Histogram (Front, Top, Side)\n' + 'Data set: '
            + str(data_sets))
    temp_folder = get_plot_path('temp_folder')
    mkdir_p(temp_folder)
    isAnimation = True
    tof_range = [0, np.inf]
    print()
    print('Animating...')
    for i in range(0, (stop-start)//step-1):
        print(str(round((i/(((stop-start)//step)-2))*100)) + '%')
        fig = plt.figure()
        min_ts = TS_vec[i]
        max_ts = TS_vec[i+1]
        ce_temp = ce[(ce['Time'] >= min_ts) & (ce['Time'] <= max_ts)]

        plt.subplot2grid((2, 3), (1, 0), colspan=3)
        plt.plot(event_numbers, ce.Time, color='blue', marker='.',
                 linestyle='None', label='Coincident event')
        
        bus6 = ce[(ce['Bus'] == 6) & (ce['wM'] < 80) & (ce['gM'] < 40)]
        bus6_numbers = bus6.index.tolist()
        plt.plot(bus6_numbers, bus6.Time, color='green', marker='o',
                 linestyle='None', label='Bus 6: Good event')
        
        glitches = ce[(ce['Bus'] == 6) & (ce['wM'] >= 80) & (ce['gM'] >= 40)]
       
        glitch_numbers = glitches.index.tolist()
        plt.plot(glitch_numbers, glitches.Time, color='purple', marker='x',
                     linestyle='None', label='Bus 6: Glitch event')
        
        
        
        plt.legend()
        
        event_numbers_temp = ce_temp.index.tolist()
        plt.plot(event_numbers_temp, ce_temp.Time, color='red', marker='.',
                 linestyle='None', label='_nolegend_')
        

        
       
        plt.title('Time stamp vs Event number')
        plt.xlabel('Event numbers [a.u.]')
        plt.ylabel('Time stamp  [TDC channels]')

        if ce_temp.shape[0] > 2:
            fig, __ = pl.plot_all_sides(fig, name, module_order, ce_temp,
                                        data_sets, number_of_detectors,
                                        count_range, ADC_filter, m_range,
                                        tof_range, isAnimation)
       
            fig.savefig(temp_folder + str(i) + '.png')
        plt.close()
    
    images = []
    files = os.listdir(temp_folder)
    files = [file[:-4] for file in files if file[-9:] != '.DS_Store' 
             and file != '.gitignore']
    
    output_path = get_output_path(data_sets) + 'Perspectives_TS_sweep.gif'
    
    
    for filename in sorted(files, key=int):
        images.append(imageio.imread(temp_folder + filename + '.png'))
    imageio.mimsave(output_path, images)
    
    shutil.rmtree(temp_folder, ignore_errors=True)
    print('Done!')
    
        
        
        
        
    
            
        


    
    
    
    
print('\n')
print(' __  __       _ _   _         _____      _     _ \n' + 
      '|  \/  |     | | | (_)       / ____|    (_)   | |\n' +
      '| \  / |_   _| | |_ _ ______| |  __ _ __ _  __| |\n' +
      '| |\/| | | | | | __| |______| | |_ |  __| |/ _` |\n' +
      '| |  | | |_| | | |_| |      | |__| | |  | | (_| |\n' +
      '|_|  |_|\__,_|_|\__|_|       \_____|_|  |_|\__,_|\n')
print('   MESYTEC OUTPUT: IMPORT, CLUSTER AND ANALYSE    ')
print()
    
warnings.filterwarnings("ignore", module="matplotlib")
warnings.simplefilter(action='ignore', category=FutureWarning)
dirname = os.path.dirname(__file__)
coincident_events = None
events = None
triggers = None
number_of_detectors = None
module_order = None
detector_types = None
data_sets = None
temp_events = None
E_i = None

answer = intro_meny()

if answer == 'y':
    clusters_folder = os.path.join(dirname, '../Clusters/')
    clu_files = os.listdir(clusters_folder)
    clu_files = [file for file in clu_files if file[-3:] == '.h5']
    
    not_int = True
    not_in_range = True
    file_number = None
    
    print()
    print('************* Choose saved clusters *************')
    print('-------------------------------------------------')
    while (not_int or not_in_range):
        for i, file in enumerate(clu_files):
            print(str(i+1) + '. ' + file)
    
        file_number = input('\nEnter a number between 1-' + 
                            str(len(clu_files)) + '.\n>> ')
    
        try:
            file_number = int(file_number)
            not_int = False
            not_in_range = (file_number < 1) | (file_number > len(clu_files))
        except ValueError:
            pass
    
        if not_int or not_in_range:
            print('\nThat is not a valid number.')
    
    clu_set = clu_files[int(file_number) - 1]
    
    clu_path = clusters_folder + clu_set
    
    print('Loading...')
    print('0%')
    coincident_events = pd.read_hdf(clu_path, 'coincident_events')
    print('25%')
    events = pd.read_hdf(clu_path, 'events')
    print('50%')
    triggers = pd.read_hdf(clu_path, 'triggers')
    print('75%')
    number_of_detectors = pd.read_hdf(clu_path, 'number_of_detectors')['number_of_detectors'].iloc[0]
    module_order_df = pd.read_hdf(clu_path, 'module_order')
    detector_types_df = pd.read_hdf(clu_path, 'detector_types')
    E_i = pd.read_hdf(clu_path, 'E_i')['E_i'].iloc[0]
    print('100%')
    print('Done!')
    
    detector_types = []
    for row in detector_types_df['detector_types']:
        detector_types.append(row)
    
    module_order =  []
    for row in module_order_df['module_order']:
        module_order.append(row)
         
    data_sets = pd.read_hdf(clu_path, 'data_set')['data_set'].iloc[0]
    measurement_time = pd.read_hdf(clu_path, 'measurement_time')['measurement_time'].iloc[0]
    calibration = pd.read_hdf(clu_path, 'calibration')['calibration'].iloc[0]
    create_plot_folder(data_sets)
    coincident_events.reset_index(drop=True, inplace=True)
    events.reset_index(drop=True, inplace=True)
    triggers.reset_index(drop=True, inplace=True)

else:
    folder = os.path.join(dirname, '../Data/')
    files = os.listdir(folder)
    files = [file for file in files if file[-9:] != '.DS_Store' and file != '.gitignore']
    coincident_events, events, data_sets, triggers, number_of_detectors, module_order, detector_types, measurement_time, E_i, calibration = choose_data_set()
    create_plot_folder(data_sets)

create_output_folder(data_sets)

thresADC = 0
not_done = True
while not_done:
    choice = main_meny(data_sets)
    if choice == 1:
        module_order = [int(x) for x in input('Enter module order, uses spaces to separate.\n>>').split()]
    elif choice == 2:
        choose_analysis_type(module_order, data_sets, E_i, measurement_time, 
                             calibration)
    elif choice == 3:
        animation_menu(coincident_events, data_sets, E_i, measurement_time)
    elif choice == 4:
        save_clusters(coincident_events, events, triggers, number_of_detectors,
                      module_order, detector_types, data_sets, 
                      measurement_time, E_i, calibration)
    elif choice == 5:
        export_clusters(coincident_events, triggers, data_sets)
    elif choice == 6:
        print('---Without filter---')
        df_nf = coincident_events
        df_nf = df_nf[df_nf.d != -1]
        df_nf = df_nf[df_nf.Time < 1.5e12]
        df_nf = df_nf[(df_nf.gCh >= 80) & (df_nf.gCh <= 85)]
        start_time = df_nf.head(1)['Time'].values[0]
        end_time = df_nf.tail(1)['Time'].values[0]
        duration = (end_time - start_time) * 62.5e-9
 #       print('Duration: ' + str(duration))
        for bus in range(0, 9):
            df_temp = df_nf[df_nf.Bus == bus]
          #  print('Events: ' + str(df_temp.shape[0]))
            events_per_s = df_temp.shape[0] / duration
            print('Bus ' + str(bus) + ': ' + str(events_per_s) + ' [events/s]')
        print('---With filter---')
        df_nf = df_nf[(df_nf.wM == 1) & (df_nf.gM < 5)]
        df_nf = df_nf[(df_nf.wADC > 500) & (df_nf.gADC > 400)]
        for bus in range(0, 9):
            df_temp = df_nf[df_nf.Bus == bus]
            events_per_s = df_temp.shape[0] / duration
            print('Bus ' + str(bus) + ': ' + str(events_per_s) + ' [events/s]')
            
    elif choice == 7:
        print('\nBye!')
        not_done = False
    
    
    
    
    


