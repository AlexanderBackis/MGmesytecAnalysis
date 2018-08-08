#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 11:57:13 2018

@author: alexanderbackis
"""

import os
import h5py

dir_name = os.path.dirname(__file__)
folder = os.path.join(dir_name, '../HDF5/')
files = os.listdir(folder)
files = [file for file in files if file[-9:] != '.DS_Store']

for i, file in enumerate(files):
    print(str(i+1) + '. ' + str(file))
        
file_number = input('\nEnter a number between 1-' + str(len(files)) + '.\n>> ')
file_name = files[int(file_number) - 1]
file_path = os.path.join(dir_name, '../HDF5/' + file_name)

f = h5py.File(file_path,'r')
print(list(f))