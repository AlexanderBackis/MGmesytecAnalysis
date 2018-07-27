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
TriggerMask   =   0x0F000000     # 0000 1111 0000 0000 0000 0000 0000 0000


# =======  DICTONARY  ======= #
Header        =   0x40000000     # 0100 0000 0000 0000 0000 0000 0000 0000 
Data          =   0x00000000     # 0000 0000 0000 0000 0000 0000 0000 0000
EoE           =   0xC0000000     # 1100 0000 0000 0000 0000 0000 0000 0000

DataEvent     =   0x10000000     # 0001 0000 0000 0000 0000 0000 0000 0000
DataExTs      =   0x20000000     # 0010 0000 0000 0000 0000 0000 0000 0000
Trigger       =   0x41000000     # 0100 0001 0000 0000 0000 0000 0000 0000

# =======  BIT-SHIFTS  ======= #
ChannelShift  =   12
BusShift      =   24
ExTsShift     =   30




#print('\n\n\n')
#print('************************************************')
#print('************************************************')
#print('MULTI-GRID: MESYTEC IMPORT, CLUSTER AND ANALYSIS')
#print('************************************************')
#print('************************************************')
#print('\n\n\n')
#
#
#
#file_name = input('Please enter name of file. \n>> ')
#
#
#print('\nChoose an analysis type: \n' + '1. 2D PHS all channels\n' +
#      '2. 1D PHS specific channels\n' + '3. 2D coincidence histogram')
#
#analysis_type = input('Insert number between 1-3.\n>> ')
#
#try:
#   analysis_type = int(analysis_type)
#except ValueError:
#   print("That's not an int!")
#
#if analysis_type == 1:
#    print()
#    print('********* 2D PHS all channels **********')
#    print('Further specifications?\n' + '1. Number of bins for ADC channels\n' 
#          + '2. Max value)
   






start_time = time.time()
file_name = 'mvmelst_015.mvmelst'
data = clu.import_data(file_name)

#for word in data.head(200):
#    if (word & TypeMask) == Header:
#        print('Header')
#    if (word & (TypeMask | TriggerMask)) == Trigger:
#        print('Trigger')
#    if ((word & (TypeMask | DataMask)) == DataEvent):
#        print('Data')
#        print('Channel: ' + str(((word & ChannelMask) >> ChannelShift)))
#        print('Bus: ' + str((word & BusMask) >> BusShift))
#        print('ADC: ' + str((word & ADCMask)))
#    if ((word & (TypeMask | DataMask)) == DataExTs):
#        print('ExTs: ' + str(word))
#    if (word & TypeMask) == EoE:
#        print('Time: ' + str((word & TimeStampMask)))
#        print('EoE')

#
clusters = clu.cluster_data(data)
##clustersCh = clu.cluster_data_ch(data)
#thresADC = 0
#bus_vec = [0, 1, 2, 3, 4, 5]
#Bus = 0
#ChVec = [61]
#ylim = [1,1e4]
#
#indices = np.arange(0,clusters.shape[0],1)
#print(clusters)
##
plt.plot(clusters.Time,clusters.ToF)
plt.title('Time vs ToF')
plt.xlabel('Time')
plt.ylabel('ToF')
plt.show()
#    print('Time: ' + str(event.Time))
#    print('ToF: ' + str(event.ToF))
    
#pl.plot_2D_hit_buses(clusters, bus_vec, thresADC)

#pl.plot_PHS_buses(clustersCh, bus_vec)
#pl.plot_PHS_several_channels(clustersCh, Bus, ChVec, ylim)
#pl.plot_2D_hit_buses(clusters, bus_vec, thresADC)




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
