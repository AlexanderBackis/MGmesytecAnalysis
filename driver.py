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

def initialise_detector_types(number_of_detectors):
    print('Enter detector types ("ESS" or "ILL") from\n' + 
          'left to right, use spaces to separate.')
    detector_types = [x for x in input('>>').split()]
    
#    detector_types_string = ''
#    detector_types = []
#    for i in range(0,number_of_detectors):
#        detector_type = input('>>')
#        detector_types.append(detector_type)
#        
#        detector_types_string += detector_type
#        if i < (number_of_detectors - 1):
#            detector_types_string += ', '
    
    return detector_types
    

def choose_data_set(detector_types):
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
    
    coincident_events, events = clu.cluster_data(data, detector_types)
    
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

def choose_analysis_type():

    analysis_type = input('Which one? Enter a number between 1-5.\n>> ')

    try:
        analysis_type = int(analysis_type)
    except ValueError:
        print("That's not an int!")
        
    if analysis_type == 1:
        bus = input('Which module? Enter a number between 1-' + 
                    str(number_of_detectors*3 - 1) + '\n>>')
        bus = int(bus)
        ChVec = [int(x) for x in input('Which Channels? Enter numbers ' +
                 'between 0-119, separated by spaces.\n>>').split()]
        
        pl.plot_PHS_several_channels(events, bus, ChVec)
        
    if analysis_type == 2:
        pl.plot_PHS_buses(events, module_order)
    
    if analysis_type == 3:
        bus = input('Which module? Enter a number between 0-' + 
                    str(number_of_detectors*3 - 1) + '\n>>')
        bus = int(bus)
        pl.plot_3D_new(events, bus)

    if analysis_type == 4:
        pl.plot_2D_hit_buses(coincident_events, module_order, 
                             number_of_detectors, thresADC)
    if analysis_type == 5:
        count_thres = input('Insert count threshold.\n>> ')
        count_thres = int(count_thres)
        pl.plot_all_sides_3D(coincident_events, module_order, count_thres)
    
    if analysis_type == 6:
        pl.plot_2D_multiplicity_buses(coincident_events, module_order, 
                                      number_of_detectors, thresADC)
    
    if analysis_type == 7:
        pl.plot_all_sides(module_order, coincident_events, thresADC)

def main_meny(data_set):
    not_int = True
    not_in_range = True
    choice = None
    while (not_int or not_in_range):
        print()
       # print('*************************************************')
        print('******************* Main Meny *******************')
       # print('*************************************************')
        print('-------------------------------------------------')
        print('Current data set: ' + data_set)
        print('Module order    : ' + str(module_order))
        print('Detector type(s): ' + str(detector_types))
        print('-------------------------------------------------')
        print('1. Change data set')
        print('2. Change module order')
        print('3. Perform an analysis')
        print('     3.1 1D Pulse Height Spectrum')
        print('     3.2 2D Pulse Height Spectrum')
        print('     3.3 3D Pulse Height Spectrum')
        print('     3.4 2D coincidence histogram')
        print('     3.5 3D coincidence histogram')
        print('     3.6 2D multiplicity histogram')
        print('     3.7 2D histogram, different perspectives')
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
detector_types = initialise_detector_types(number_of_detectors)
coincident_events, events, data_set = choose_data_set(detector_types)
thresADC = 0

not_done = True
while not_done:
    choice = main_meny(data_set)
    if choice == 1:
        coincident_events, events, data_set = choose_data_set(detector_types)
    elif choice == 2:
        pass
    elif choice == 3:
        choose_analysis_type()
    elif choice == 4:
        print('\nBye!')
        not_done = False
    
    
    
    
    


