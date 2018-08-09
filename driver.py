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
    
#    choice = input('\nFurther investigations? (y/n).\n>> ')
#
#    if choice == 'y':
#        bus_nbr = input('Module: ')
#        w_ch = input('Wire channel: ')
#        g_ch = input('Grid channel: ')
#        bus_nbr = int(bus_nbr)
#        w_ch = int(w_ch)
#        g_ch = int(g_ch)
#        nbr_events_w = events[events.Channel == w_ch].shape[0]
#        nbr_events_g = events[events.Channel == g_ch].shape[0]
#        nbr_coincident_events = coincident_events[(coincident_events.wCh == w_ch) & (coincident_events.gCh == g_ch)].shape[0]
#        print('Bus ' + str(bus_nbr))
#        print('Events in channel ' + str(w_ch) + ': ' + str(nbr_events_w))
#        print('Events in channel ' + str(g_ch) + ': ' + str(nbr_events_g))
#        print('Coincident events between channel ' + str(w_ch) + ' and ' +
#              str(g_ch) + ': ' + str(nbr_coincident_events))
        
    input('\nPress "Enter" when done.\n>> ')
    
    

def create_plot_folder(data_set):
    dirname = os.path.dirname(__file__)
    folder = os.path.join(dirname, '../Plot/' + data_set + '/')
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
    

def choose_data_set(exceptions):
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
    
    data = clu.import_data(data_set)
    
    coincident_events, events = clu.cluster_data(data, exceptions)
    
    return coincident_events, events, data_set

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
                         'ToF Histogram', 'Events per channel']
    
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
            bus = input('Which module? Enter a number between ' 
                        + str(min(module_order)) + '-' +
                        str(max(module_order)) + '\n>>')
            bus = int(bus)
            ChVec = [int(x) for x in input('Which Channels? Enter numbers ' +
                     'between 0-119, separated by spaces.\n>>').split()]
            print('Working...')
            fig, path = pl.plot_PHS_several_channels(fig, name, events, bus, 
                                                       ChVec, data_set)
        
        if analysis_type == 2:
            choice = input('Further specifications? (y/n).\n>> ')
            if choice == 'y':
                count_min_limit = input('Count min-limit: ')
                count_max_limit = input('Count max-limit: ')
                count_max_limit = int(count_max_limit)
                count_min_limit = int(count_min_limit)
                count_range = [count_min_limit, count_max_limit]
                print('Working...')
                fig, path = pl.plot_PHS_buses(fig, name, events, module_order, 
                                              data_set, count_range)
            else:
                print('Working...')
                fig, path = pl.plot_PHS_buses(fig, name, events, module_order, 
                                              data_set)
            
    
        if analysis_type == 3:
            bus = input('Which module? Enter a number between ' 
                        + str(min(module_order)) + '-' +
                        str(max(module_order)) + '\n>>')
            bus = int(bus)
            print('Working...')
            fig, path = pl.plot_3D_new(fig, name, events, bus, data_set)

        if analysis_type == 4:
            print('Working...')
            fig, path = pl.plot_2D_hit_buses(fig, name, coincident_events, 
                                             module_order, number_of_detectors, 
                                             data_set, thresADC)
        if analysis_type == 5:
            choice = input('Further specifications? (y/n).\n>> ')
            if choice == 'y':
                count_thres = input('Minimum count threshold: ')
                count_thres = int(count_thres)
                alpha = input('Insert transparancy factor (0 minimum, 1 maximum): ')
                alpha = float(alpha)
                print('Working...')
                fig, path = pl.plot_all_sides_3D(fig, name, coincident_events, 
                                                 module_order, count_thres, 
                                                 alpha, data_set, 
                                                 number_of_detectors)
            else:
                count_thres = 0
                alpha = 1
                print('Working...')
                fig, path = pl.plot_all_sides_3D(fig, name, coincident_events, 
                                                 module_order, count_thres, 
                                                 alpha, data_set, number_of_detectors)
        
        if analysis_type == 6:
            choice = input('Further specifications? (y/n).\n>> ')
            if choice == 'y':
                count_min_limit = input('Count min-limit: ')
                count_max_limit = input('Count max-limit: ')
                count_max_limit = int(count_max_limit)
                count_min_limit = int(count_min_limit)
                count_range = [count_min_limit, count_max_limit]
                print('Working...')
                fig, path = pl.plot_all_sides(fig, name, module_order, coincident_events, 
                                  data_set, number_of_detectors, count_range)
            else:
                print('Working...')
                fig, path = pl.plot_all_sides(fig, name, module_order, coincident_events,
                                  data_set, number_of_detectors)
    
        if analysis_type == 7:
            choice = input('Further specifications? (y/n).\n>> ')
            if choice == 'y':
                m_range = input('Multiplicity limit: ')
                m_range = int(m_range)
                count_min_limit = input('Count min-limit: ')
                count_max_limit = input('Count max-limit: ')
                count_max_limit = int(count_max_limit)
                count_min_limit = int(count_min_limit)
                count_range = [count_min_limit, count_max_limit]
                print('Working...')
                fig, path = pl.plot_2D_multiplicity_buses(fig, name, 
                                      coincident_events, module_order, 
                                      number_of_detectors, data_set, m_range, 
                                      count_range, thresADC)
            else:
                print('Working...')
                fig, path = pl.plot_2D_multiplicity_buses(fig, name, 
                                              coincident_events, module_order, 
                                              number_of_detectors, data_set)
    
        if analysis_type == 8:
            choice = input('Further specifications? (y/n).\n>> ')
            if choice == 'y':
                minWM = input('Minimum wire multiplicity: ')
                maxWM = input('Maximum wire multiplicity: ')
                minGM = input('Minimum grid multiplicity: ')
                maxGM = input('Maximum grid multiplicity: ')
                minWM = int(minWM)
                maxWM = int(maxWM)
                minGM = int(minGM)
                maxGM = int(maxGM)
                exclude_channels = [int(x) for x in 
                                    input('Enter channels to exclude, ' +
                                          'use spaces to separate ' + 
                                          '(insert "-1" if none should be omitted): ').split()]
                print('Working...')
                fig, path = pl.plot_charge_scatter_buses(fig, name, coincident_events, module_order, 
                                     number_of_detectors, data_set, minWM, maxWM, minGM, 
                                     maxGM, exclude_channels)
            else:
                print('Working...')
                fig, path = pl.plot_charge_scatter_buses(fig, name, coincident_events, module_order, 
                                             number_of_detectors, data_set)

        if analysis_type == 9:
            choice = input('Further specifications? (y/n).\n>> ')
            if choice == 'y':
                number_bins = input('Number of bins: ')
                rnge = [int(x) for x in input('Range (use a space to separate between min and max): ').split()]
                number_bins = int(number_bins)
                print('Working...')
                fig, path = pl.plot_ToF_histogram(fig, name, coincident_events, 
                                                  data_set, number_bins, rnge)
            else:
                print('Working...')
                fig, path = pl.plot_ToF_histogram(fig, name, coincident_events, 
                                                  data_set)
        
        if analysis_type == 10:
            choice = input('Further specifications? (y/n).\n>> ')
            if choice == 'y':
                lg = input('Logarithmic scale? (y/n):')
                log = (lg == 'y')
                count_min_limit = input('Count min-limit: ')
                count_max_limit = input('Count max-limit: ')
                count_max_limit = int(count_max_limit)
                count_min_limit = int(count_min_limit)
                count_range = [count_min_limit, count_max_limit]
                print('Working...')
                fig, path = pl.plot_event_count(fig, name, module_order, 
                                                number_of_detectors, 
                                                data_set, events, log, count_range)
            else:
                print('Working...')
                fig, path = pl.plot_event_count(fig, name, module_order, 
                                                number_of_detectors, 
                                                data_set, events)
        
        
        
        
        
        
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
        print('Current data set: ' + data_set)
        print('Module order    : ' + str(module_order))
        print('Detector type(s): ' + str(detector_types))
        print('-------------------------------------------------')
        print('1. Change data set')
        print('2. Change module order')
        print('3. Change detector type(s)')
        print('4. Perform an analysis')
        print('5. Print key numbers')
        print('6. Quit')
    
        choice = input('\nChoose an alternative by entering a number \n' +
                       'between 1-6.\n>> ')
        
        try:
            choice = int(choice)
            not_int = False
            not_in_range = (choice < 1) | (choice > 6)
        except ValueError:
            pass
    
        if not_int or not_in_range:
            print('\nThat is not a valid number.')
    
    return choice
print('\n')
print(' __  __       _ _   _         _____      _     _\n' + 
      '|  \/  |     | | | (_)       / ____|    (_)   | |\n' +
      '| \  / |_   _| | |_ _ ______| |  __ _ __ _  __| |\n' +
      '| |\/| | | | | | __| |______| | |_ |  __| |/ _` |\n' +
      '| |  | | |_| | | |_| |      | |__| | |  | | (_| |\n' +
      '|_|  |_|\__,_|_|\__|_|       \_____|_|  |_|\__,_|\n')
print('   MESYTEC OUTPUT: IMPORT, CLUSTER AND ANALYSE    ')
print()

dirname = os.path.dirname(__file__)
folder = os.path.join(dirname, '../Data/')
files = os.listdir(folder)
files = [file for file in files if file[-9:] != '.DS_Store']


number_of_detectors, module_order = choose_number_modules()
detector_types, exceptions = initialise_detector_types(number_of_detectors)
coincident_events, events, data_set = choose_data_set(exceptions)
create_plot_folder(data_set)
thresADC = 0

not_done = True
while not_done:
    choice = main_meny(data_set)
    if choice == 1:
        number_of_detectors, module_order = choose_number_modules()
        detector_types, exceptions = initialise_detector_types(number_of_detectors)
        coincident_events, events, data_set = choose_data_set(exceptions)
        create_plot_folder(data_set)
    elif choice == 2:
        module_order = [int(x) for x in input('Enter module order, uses spaces to separate.\n>>').split()]
    elif choice == 3:
        detector_types, exceptions = initialise_detector_types(number_of_detectors)
    elif choice == 4:
        choose_analysis_type(module_order, data_set)
    elif choice == 5:
        print_key_numbers(module_order, events, coincident_events)
    elif choice == 6:
        print('\nBye!')
        not_done = False
    
    
    
    
    


