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
    
    data_set = files[int(file_number)-1]
    
    data = clu.import_data(data_set)
    
    clusters = clu.cluster_data(data)
    
    return clusters, data_set

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
    
    return modules[0:3*number_of_detectors]

def choose_analysis_type():

    analysis_type = input('Which one? Insert a number between 1-4.\n>> ')

    try:
        analysis_type = int(analysis_type)
    except ValueError:
        print("That's not an int!")

    if analysis_type == 1:
        print()
    

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
        print('Module order: ' + str(module_order))
        print('-------------------------------------------------')
        print('1. Change data set')
        print('2. Change module order')
        print('3. Perform an analysis')
        print('     3.1 1D Pulse Height Spectrum')
        print('     3.2 2D Pulse Height Spectrum')
        print('     3.3 2D coincidence histogram')
        print('     3.4 3D coincidence histogram')
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

clusters, data_set = choose_data_set()
module_order = choose_number_modules()

not_done = True
while not_done:
    choice = main_meny(data_set)
    if choice == 1:
        clusters, data_set = choose_data_set()
    elif choice == 2:
        pass
    elif choice == 3:
        choose_analysis_type()
    elif choice == 4:
        print('\nBye!')
        not_done = False
    
    
    
    
    


