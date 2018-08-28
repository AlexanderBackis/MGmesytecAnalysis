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
                 
        
        
        
    get_spec =  {'Count range': get_count_range, 
                 'ADC filter': get_ADC_filter,
                 'Multiplicity filter': get_multiplicity_filter,
                 'Lower and upper count threshold': get_count_threshold,
                 'Exclude channels': get_exclude_channels,
                 'Include channels': get_include_channels,
                 'Log/Lin-scale': get_log_lin_scale,
                 'ADC threshold': get_ADC_threshold,
                 'Transparacy factor': get_transparacy_factor,
                 'Number of bins': get_number_of_bins,
                 'Range': get_range,
                 'Choose specific bus(es)': get_buses}
    
    spec_type_names = ['Count range', 'ADC filter', 'Multiplicity filter', 
                       'Lower and upper count threshold', 
                       'Exclude channels', 'Include channels', 'Log/Lin-scale',
                       'ADC threshold', 'Transparacy factor', 'Number of bins',
                       'Range', 'Choose specific bus(es)']
    
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
        
        
    
        file_number = input('\nEnter a number between 1-' + 
                            str(len(files)) + '.\n>> ')
    
        try:
            file_number = int(file_number)
            not_int = False
            not_in_range = (file_number < 1) | (file_number > len(files))
        except ValueError:
            pass
    
        if not_int or not_in_range:
            print('\nThat is not a valid number.')
    
    data_set = files[int(file_number) - 1]
    data = None
    

    
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
    
    
    print('Import full file (y/n)?')
    ans = input('>> ')
        
    if ans == 'n':
        print('Enter amount of data in MB to import (minimum size is 1 MB).')
        max_size = input('>> ')
        max_size = int(max_size)
        data = clu.import_data(data_set, max_size)
    else:
        data = clu.import_data(data_set)
    
    coincident_events, events, triggers = clu.cluster_data(data, exceptions)
    
    return coincident_events, events, data_set, triggers, number_of_detectors, module_order, detector_types

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

def choose_analysis_type(module_order, data_set):
    
    finished_with_analysis = False
    analysis_name_vec = ['PHS (1D)', 'PHS (2D)', 'PHS (3D)', 
                         'Coincidence Histogram (2D)', 
                         'Coincidence Histogram (3D)', 
                         'Coincidence Histogram (Front, Top, Side)',
                         'Multiplicity',
                         'Scatter Map (collected charge in wires and grids)', 
                         'ToF Histogram', 'Events per channel', 
                         'Timestamp and Trigger']
    
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
            if choice == 'y':
                options = ['Log/Lin-scale', 'Count range']
                specs = choose_specifications(options)
                loglin = specs['Log/Lin-scale']
                count_range = specs['Count range']
            
            print('Loading...')
            fig, path = pl.plot_PHS_several_channels(fig, name, events, bus, 
                                                     ChVec, data_set, 
                                                     loglin = loglin,
                                                     count_range = count_range)
            print('Done!')
        
        if analysis_type == 2:
            choice = input('\nFurther specifications? (y/n).\n>> ')
            
            count_range = [1, 3000]
            buses = module_order
            if choice == 'y':
                options = ['Count range', 'Choose specific bus(es)']
                specs = choose_specifications(options)
                
                if specs['Choose specific bus(es)'] != None:
                    buses = specs['Choose specific bus(es)']
                
                if specs['Count range'] != None:
                    count_range = specs['Count range']
                    
            print('Loading...')
            fig, path = pl.plot_PHS_buses(fig, name, events, buses, 
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
            if choice == 'y':
                options = ['Count range', 'Choose specific bus(es)', 
                           'ADC filter', 'Multiplicity filter']
                specs = choose_specifications(options)
                
                if specs['Count range'] != None:
                    count_range = specs['Count range']
                
                if specs['Choose specific bus(es)'] != None:
                    buses = specs['Choose specific bus(es)']
                
                if specs['ADC filter'] != None:
                    ADC_filter = specs['ADC filter']
                
                if specs['Multiplicity filter'] != None:
                    m_range = specs['Multiplicity filter']
                
            print('Loading...')
            fig, path = pl.plot_2D_hit_buses(fig, name, coincident_events, 
                                             buses, number_of_detectors, 
                                             data_set, count_range,
                                             ADC_filter, m_range)
                
            print('Done!')
            
        if analysis_type == 5:
            choice = input('\nFurther specifications? (y/n).\n>> ')
            alpha = 1
            count_thres = None
            ADC_filter = None
            m_range = None
            if choice == 'y':
                options = ['Transparacy factor', 'Lower and upper count threshold',
                           'ADC filter', 'Multiplicity filter']
                specs = choose_specifications(options)
                if specs['Lower and upper count threshold'] != None:
                    count_thres = specs['Lower and upper count threshold']
                
                if specs['Transparacy factor'] != None:
                    alpha = specs['Transparacy factor']
                
                if specs['ADC filter'] != None:
                    ADC_filter = specs['ADC filter']
                
                if specs['Multiplicity filter'] != None:
                    m_range = specs['Multiplicity filter']
                   
            print('Loading...')
            fig, path = pl.plot_all_sides_3D(fig, name, coincident_events, 
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
            if choice == 'y':
                options = ['Count range', 'ADC filter', 'Multiplicity filter']
                specs = choose_specifications(options)
                if specs['Count range'] != None:
                    count_range = specs['Count range']
                
                if specs['ADC filter'] != None:
                    ADC_filter = specs['ADC filter']
                
                if specs['Multiplicity filter'] != None:
                    m_range = specs['Multiplicity filter']
                    
            
            print('Loading...')
            fig, path = pl.plot_all_sides(fig, name, module_order, coincident_events, 
                                  data_set, number_of_detectors, count_range,
                                  ADC_filter, m_range)
            
            print('Done!')
    
        if analysis_type == 7:
            choice = input('\nFurther specifications? (y/n).\n>> ')
            m_range = [0,8,0,8]
            count_range = [1, 1e6]
            buses = module_order
            ADC_filter = None
            if choice == 'y':
                options = ['Multiplicity filter', 'Count range', 
                           'Choose specific bus(es)', 'ADC filter']
                specs = choose_specifications(options)
                if specs['Multiplicity filter'] != None:
                    m_range = specs['Multiplicity filter']
                
                if specs['Count range'] != None:
                    count_range = specs['Count range']
                
                if specs['Choose specific bus(es)'] != None:
                    buses = specs['Choose specific bus(es)']
                
                if specs['ADC filter'] != None:
                    ADC_filter = specs['ADC filter']
                
            
            print('Loading...')
            fig, path = pl.plot_2D_multiplicity_buses(fig, name, 
                                      coincident_events, buses, 
                                      number_of_detectors, data_set, m_range, 
                                      count_range, ADC_filter)

            print('Done!')
    
        if analysis_type == 8:
            choice = input('\nFurther specifications? (y/n).\n>> ')
            
            if choice == 'y':
                options = ['Multiplicity filter', 'Exclude channels', 
                           'Choose specific bus(es)']
                specs = choose_specifications(options)
                
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
                
                print('Loading...')
                fig, path = pl.plot_charge_scatter_buses(fig, name, coincident_events, buses, 
                                     number_of_detectors, data_set, minWM, maxWM, minGM, 
                                     maxGM, exclude_channels)
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
                options = ['Number of bins', 'Range', 'ADC filter']
                specs = choose_specifications(options)
                ADC_filter = None
                if specs['Number of bins'] != None:
                    number_bins = specs['Number of bins']
                
                if specs['Range'] != None:
                    rnge = specs['Range']
                
                if specs['ADC filter'] != None:
                    ADC_filter = specs['ADC filter']
                    
                
                print('Loading...')
                fig, path = pl.plot_ToF_histogram(fig, name, coincident_events, 
                                                  data_set, number_bins, rnge,
                                                  ADC_filter)
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
            print('Loading...')
            fig, path = pl.plot_timestamp_and_trigger(fig, name, data_set, 
                                    coincident_events, triggers)
            print('Done!')
            
                
        if analysis_type <= len(analysis_name_vec):
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
        

        

            
            
                

def main_meny(data_set):
    not_int = True
    not_in_range = True
    choice = None
    while (not_int or not_in_range):
        print()
       # print('*************************************************')
        print('******************* main meny *******************')
       # print('*************************************************')
        print('-------------------------------------------------')
        print('Data set        : ' + data_set)
        print('Module order    : ' + str(module_order))
        print('Detector type(s): ' + str(detector_types))
        print('-------------------------------------------------')
        print('1. Change module order')
        print('2. Perform an analysis')
        print('3. Save clusters')
        print('4. Quit')
    
        choice = input('\nChoose an alternative by entering a number \n' +
                       'between 1-4.\n>> ')
        
        try:
            choice = int(choice)
            not_int = False
            not_in_range = (choice < 1) | (choice > 4)
        except ValueError:
            pass
    
        if not_int or not_in_range:
            print('\nThat is not a valid number.')
    
    return choice
print('\n')
print(' __  __       _ _   _         _____      _     _ \n' + 
      '|  \/  |     | | | (_)       / ____|    (_)   | |\n' +
      '| \  / |_   _| | |_ _ ______| |  __ _ __ _  __| |\n' +
      '| |\/| | | | | | __| |______| | |_ |  __| |/ _` |\n' +
      '| |  | | |_| | | |_| |      | |__| | |  | | (_| |\n' +
      '|_|  |_|\__,_|_|\__|_|       \_____|_|  |_|\__,_|\n')
print('   MESYTEC OUTPUT: IMPORT, CLUSTER AND ANALYSE    ')
print()


def save_clusters(coincident_events, events, triggers, number_of_detectors,
                  module_order, detector_types, data_set):
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
        
    number_det.to_hdf(path, 'number_of_detectors', complevel = 9)
    mod_or.to_hdf(path, 'module_order', complevel = 9)
    det_types.to_hdf(path, 'detector_types', complevel = 9)
    da_set.to_hdf(path, 'data_set', complevel = 9)
    print('100%')
    print('Done!')


    
    
    
    
    
    

dirname = os.path.dirname(__file__)
coincident_events = None
events = None
triggers = None
number_of_detectors = None
module_order = None
detector_types = None
data_set = None

print('Load saved clusters (y/n)?')
answer = input('>> ')
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
    print('100%')
    print('Done!')
    
    detector_types = []
    for row in detector_types_df['detector_types']:
        detector_types.append(row)
    
    module_order =  []
    for row in module_order_df['module_order']:
        module_order.append(row)
        
    
    data_set = pd.read_hdf(clu_path, 'data_set')['data_set'].iloc[0]
    create_plot_folder(data_set)

else:
    folder = os.path.join(dirname, '../Data/')
    files = os.listdir(folder)
    files = [file for file in files if file[-9:] != '.DS_Store' and file != '.gitignore']
    coincident_events, events, data_set, triggers, number_of_detectors, module_order, detector_types = choose_data_set()
    create_plot_folder(data_set)

create_output_folder(data_set)

thresADC = 0
not_done = True
while not_done:
    choice = main_meny(data_set)
    if choice == 1:
        module_order = [int(x) for x in input('Enter module order, uses spaces to separate.\n>>').split()]
    elif choice == 2:
        choose_analysis_type(module_order, data_set)
    elif choice == 3:
        save_clusters(coincident_events, events, triggers, number_of_detectors,
                      module_order, detector_types, data_set)
    elif choice == 4:
        print('\nBye!')
        not_done = False
    
    
    
    
    


