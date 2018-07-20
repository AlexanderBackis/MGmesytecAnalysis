#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 13:18:00 2018

@author: alexanderbackis
"""

# =======  LIBRARIES  ======= #
import cluster_mesytec as clu
import plot_mesytec as pl
import time


start_time = time.time()
filename = 'mvmelst_061_180628_140303.mvmelst'
data = clu.import_data(filename)
print('Import: ' + str(round(time.time() - start_time)) + ' s')
df = clu.cluster_data(data)
print('Cluster: ' + str(round(time.time() - start_time)) + ' s')
bus_vec = [0,1,2]
pl.plot_all_sides(bus_vec, df)
print('Plot: ' + str(round(time.time() - start_time)) + ' s')

