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
        print('\nChoose a data set.')
        for i, file in enumerate(files):
            print(str(i+1) + '. ' + str(file))
    
        file_number = input('Please enter a number between 1 and ' +str(len(files)) 
                  + '\n>> ')
    
        try:
            file_number = int(file_number)
            not_int = False
            not_in_range = (file_number < 1) | (file_number > len(files))
        except ValueError:
            pass
    
        if not_int or not_in_range:
            print('\nThat is not a valid number.')
    
    data_set = files[int(file_number)-1]

    return clu.import_data(data_set), data_set

def main_meny(data_set):
    not_int = True
    not_in_range = True
    choice = None
    while (not_int or not_in_range):
        print('\n|*|*|*|*|*|*||| MAIN MENY |||*|*|*|*|*|*|')
        print('Current data-set: ' + data_set + '\n')
        print('1. Change data set')
        print('2. Perform an analysis')
        print('3. Quit')
    
        choice = input('Please enter a number between 1 and 3.\n>> ')
        
        try:
            choice = int(choice)
            not_int = False
            not_in_range = (choice < 1) | (choice > 3)
        except ValueError:
            pass
    
        if not_int or not_in_range:
            print('\nThat is not a valid number.')
    
    return choice
    


print()
print('************************************************')
print('************************************************')
print('MULTI-GRID: MESYTEC IMPORT, CLUSTER AND ANALYSIS')
print('************************************************')
print('************************************************')

dirname = os.path.dirname(__file__)
folder = os.path.join(dirname, '../Data/')
files = os.listdir(folder)
files = [file for file in files if file[-9:] != '.DS_Store']

clusters, data_set = choose_data_set()


      
not_done = True
while not_done:
    choice = main_meny(data_set)
    if choice == 1:
        clusters, data_set = choose_data_set()
    elif choice == 2:
        pass
    elif choice == 3:
        not_done = False
    
    
    


print(clusters)


print('\nChoose an analysis type: \n' + '1. 2D PHS all channels\n' +
      '2. 1D PHS specific channels\n' + '3. 2D coincidence histogram')

analysis_type = input('Insert number between 1-3.\n>> ')

try:
   analysis_type = int(analysis_type)
except ValueError:
   print("That's not an int!")

if analysis_type == 1:
    print()
    print('********* 2D PHS all channels **********')
    print('Further specifications?\n' + '1. Number of bins for ADC channels\n' 
          + '2. Max value: ')
    
    
    


