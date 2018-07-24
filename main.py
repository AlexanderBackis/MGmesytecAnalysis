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
import matplotlib.pyplot as plt

start_time = time.time()
file_name = 'mvmelst_061_180628_140303.mvmelst'
data = clu.import_data(file_name)
clusters = clu.cluster_data(data)

bus = 1
Channel = 61
maxWM = 1
maxGM = 100
pl.charge_scatter(clusters, bus, Channel, maxWM, maxGM)
print(time.time() - start_time)