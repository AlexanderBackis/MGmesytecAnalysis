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
import numpy as np

# =======    MASKS    ======= #
TypeMask      =   0xC0000000     # 1100 0000 0000 0000 0000 0000 0000 0000
DataMask      =   0x30000000     # 0011 0000 0000 0000 0000 0000 0000 0000

ChannelMask   =   0x00FFF000     # 0000 0000 1111 1111 1111 0000 0000 0000
BusMask       =   0x0F000000     # 0000 1111 0000 0000 0000 0000 0000 0000
ADCMask       =   0x00000FFF     # 0000 0000 0000 0000 0000 1111 1111 1111
TimeStampMask =   0x3FFFFFFF     # 0011 1111 1111 1111 1111 1111 1111 1111

NbrWordsMask  =   0x00000FFF     # 0000 0000 0000 0000 0000 1111 1111 1111
GateStartMask =   0x0000FFFF     # 0000 0000 0000 0000 1111 1111 1111 1111
ExTsMask      =   0x0000FFFF     # 0000 0000 0000 0000 1111 1111 1111 1111


# =======  DICTONARY  ======= #
Header        =   0x40000000     # 0100 0000 0000 0000 0000 0000 0000 0000 
Data          =   0x00000000     # 0000 0000 0000 0000 0000 0000 0000 0000
EoE           =   0xC0000000     # 1100 0000 0000 0000 0000 0000 0000 0000

DataPart1     =   0x30000000     # 0011 0000 0000 0000 0000 0000 0000 0000
DataPart2     =   0x10000000     # 0001 0000 0000 0000 0000 0000 0000 0000
DataExTs      =   0x20000000     # 0010 0000 0000 0000 0000 0000 0000 0000


# =======  BIT-SHIFTS  ======= #
ChannelShift  =   12
BusShift      =   24
ExTsShift     =   30

start_time = time.time()
file_name = '2018_07_26_mvmelst_007.mvmelst'
data = clu.import_data(file_name)
clusters = clu.cluster_data(data)
print(clusters)




#clusters = clu.cluster_data_ch(data)
#thresADC = 0
#bus_vec = [0, 1, 2]
##pl.plot_2D_hit_buses(clusters, bus_vec, thresADC)
#
#pl.plot_PHS_buses(clusters, bus_vec)
#pl.plot_PHS_several_channels(clusters, 3, [22,97], [1,1e5])




#Thresvec = np.arange(300,2100,100)
#bus_vec = [0,1,2]
#for ADCthreshold in Thresvec:
#    clustersThres = clusters[(clusters.wADC > ADCthreshold) & 
#                    (clusters.gADC > ADCthreshold)]
#    pl.plot_all_sides(bus_vec, clustersThres, ADCthreshold)
#print(time.time() - start_time)





#bus = 1
#Channel = 119
#maxWM = 1
#maxGM = 100
#minGM = 0
#Channelvec = np.arange(80,120,1)
#print(Channelvec)
#for Channel in Channelvec:
#    pl.charge_scatter(clusters, bus, Channel, maxWM, maxGM, minGM)
#print(time.time() - start_time)
