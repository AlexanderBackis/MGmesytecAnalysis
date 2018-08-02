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
import cluster_mesytec as clu
import plot_mesytec as pl



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
    print('Enter detector types ("ESS" or "ILL") from\n' + 
          'left to right, use spaces to separate.')
    detector_types = [x for x in input('>>').split()]
    
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
                         'Scatter Map Collected Charge', 'ToF Histogram']
    
    while(not finished_with_analysis):
        print()
        print('******************* analysis ********************')
        print('-------------------------------------------------')
        for i, name in enumerate(analysis_name_vec):
            print(str(i+1) + '. ' + name)
        print('0. Back to main meny')

        analysis_type = input('\nChoose an analysis. Enter a number between 0-' 
                              + str(len(analysis_name_vec)) + '.' + '\n>> ')

        try:
            analysis_type = int(analysis_type)
        except ValueError:
            print("That's not an int!")
    
        if analysis_type == 0:
            finished_with_analysis = True
        
        if analysis_type == 1:
            bus = input('Which module? Enter a number between ' 
                        + str(min(module_order)) + '-' +
                        str(max(module_order)) + '\n>>')
            bus = int(bus)
            ChVec = [int(x) for x in input('Which Channels? Enter numbers ' +
                     'between 0-119, separated by spaces.\n>>').split()]
        
            pl.plot_PHS_several_channels(events, bus, ChVec, data_set)
        
        if analysis_type == 2:
            choice = input('Further specifications? (y/n).\n>> ')
            if choice == 'y':
                count_limit = input('Count limit: ')
                count_limit = int(count_limit)
                pl.plot_PHS_buses(events, module_order, data_set, count_limit)
            else:
                pl.plot_PHS_buses(events, module_order, data_set)
    
        if analysis_type == 3:
            bus = input('Which module? Enter a number between ' 
                        + str(min(module_order)) + '-' +
                        str(max(module_order)) + '\n>>')
            bus = int(bus)
            pl.plot_3D_new(events, bus, data_set)

        if analysis_type == 4:
            pl.plot_2D_hit_buses(coincident_events, module_order, 
                             number_of_detectors, data_set, thresADC)
        if analysis_type == 5:
            count_thres = input('Insert count threshold.\n>> ')
            count_thres = int(count_thres)
            pl.plot_all_sides_3D(coincident_events, module_order, count_thres, 
                                 data_set)
        
        if analysis_type == 6:
            pl.plot_all_sides(module_order, coincident_events, data_set, 
                              thresADC)
    
        if analysis_type == 7:
            choice = input('Further specifications? (y/n).\n>> ')
            if choice == 'y':
                m_range = input('Multiplicity limit: ')
                m_range = int(m_range)
                count_limit = input('Count limit: ')
                count_limit = int(count_limit)
                pl.plot_2D_multiplicity_buses(coincident_events, module_order, 
                                      number_of_detectors, data_set, m_range, 
                                      count_limit, thresADC)
            else:
                pl.plot_2D_multiplicity_buses(coincident_events, module_order, 
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
                pl.plot_charge_scatter_buses(coincident_events, module_order, 
                                     number_of_detectors, data_set, minWM, maxWM, minGM, 
                                     maxGM)
            else:
                pl.plot_charge_scatter_buses(coincident_events, module_order, 
                                             number_of_detectors, data_set)

        if analysis_type == 9:
            choice = input('Further specifications? (y/n).\n>> ')
            if choice == 'y':
                number_bins = input('Number of bins: ')
                rnge = [int(x) for x in input('Range (use a space to separate between min and max): ').split()]
                number_bins = int(number_bins)
                pl.plot_ToF_histogram(coincident_events, data_set, number_bins, 
                                      rnge)
            else:
                pl.plot_ToF_histogram(coincident_events, data_set)

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
        print('5. Quit')
    
        choice = input('\nChoose an alternative by entering a number \n' +
                       'between 1-5.\n>> ')
        
        try:
            choice = int(choice)
            not_int = False
            not_in_range = (choice < 1) | (choice > 5)
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
        print('\nBye!')
        not_done = False
    
    
    
    
    


