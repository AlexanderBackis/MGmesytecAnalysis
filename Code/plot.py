#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 13:18:00 2018

@author: alexanderbackis
"""
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
# =======  LIBRARIES  ======= #
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cmx
import matplotlib.patheffects as path_effects
import plotly.io as pio
import plotly as py
import plotly.graph_objs as go
import scipy
import peakutils
from scipy.optimize import curve_fit
import h5py

    
# =============================================================================
# 1. PHS (1D)
# =============================================================================
    
def plot_PHS_bus_channel(df, bus, Channel):
    df_red = df[df.Channel == Channel]
    plt.hist(df_red.ADC, bins=50, range=[0,4400])  
    
def plot_PHS_several_channels(fig, name, df, bus, ChVec, data_set, 
                              loglin, count_range):
    fig1 = fig
    df_red = df[df.Bus == bus]
    
    for Channel in ChVec:
        df_ch = df_red[df_red.Channel == Channel]
        plt.hist(df_ch.ADC, bins=100, range=[0,4400], log=loglin, alpha = 1, 
                 label = 'Channel ' + str(Channel), histtype='step')
        
    if count_range!= None:
        plt.ylim(count_range[0], count_range[1])
    
    plt.legend(loc='upper right')
    plt.xlabel("Charge  [ADC channels]")
    plt.ylabel("Counts")
    name = name + '\nBus ' + str(bus) + ', Channels: ' + str(ChVec)
    plt.title(name)

    plot_path = get_plot_path(data_set) + name  + '.pdf'
    return fig1, plot_path

 
# =============================================================================
# 2. PHS (2D)
# =============================================================================

def plot_PHS(df, bus, loc, number_of_detectors, fig, count_range = [1, 3000],
             buses_per_row = 3):
    df_red = df[df.Bus == bus]
    plt.subplot(1*number_of_detectors, buses_per_row, loc+1)
    plt.hist2d(df_red.Channel, df_red.ADC, bins=[120, 120], norm=LogNorm(), 
               range=[[-0.5, 119.5], [0, 4400]], vmin=count_range[0], 
               vmax=count_range[1], cmap='jet')
    plt.ylabel("Charge [ADC channels]")
    plt.xlabel("Channel [a.u.]")
    plt.colorbar()
    name = ('Bus ' + str(bus) + ', ' + str(df_red.shape[0]) + ' events\n' + 
            'Wire events = ' + str(df_red[df_red.Channel < 80].shape[0]) + 
            ', Grid events = ' + str(df_red[df_red.Channel >= 80].shape[0]))
    
    plt.title(name)
    
def plot_PHS_buses(fig, name, df, bus_vec, data_set, count_range):
    
    fig2 = fig
        
    buses_per_row = None
    number_of_detectors = None
    if len(bus_vec) < 3:
        buses_per_row = len(bus_vec)
        number_of_detectors = 1
        figwidth = 14 * len(bus_vec) / 3
    else:
        number_of_detectors = np.ceil(len(bus_vec) / 3)
        buses_per_row = 3
        figwidth = 14
        
    fig.suptitle(name + '\n\n', x=0.5, y=1.08)
    fig.set_figheight(4 * number_of_detectors)
    fig.set_figwidth(figwidth)
    
    for loc, bus in enumerate(bus_vec):
        plot_PHS(df, bus, loc, number_of_detectors, fig, count_range, 
                 buses_per_row)
        
    plt.tight_layout()
    plot_path = (get_plot_path(data_set) + name + ', Count range: ' 
                 + str(count_range) + ', Buses: ' + str(bus_vec) + '.pdf')
    return fig2, plot_path
    

# =============================================================================
# 3. PHS (3D)
# =============================================================================  

def plot_3D_new(fig, name, df, bus, data_set):    
    df_red = df[df.Bus == bus]
                    
    histW, xbinsW, ybinsW, imW = plt.hist2d(df_red.Channel, df_red.ADC,
                                        bins=[80, 50], range=[[0, 79], 
                                              [0, 4400]])
    
    histG, xbinsG, ybinsG, imG = plt.hist2d(df_red.Channel, df_red.ADC,
                                        bins=[40, 50], range=[[80, 120], 
                                              [0, 4400]])
    histVec = [histW, histG]
    xbinsVec = [xbinsW, xbinsG]
    ybinsVec = [ybinsW, ybinsG]
    nameVec =  ['Wires', 'Grids']
    xlimVec =  [ [0, 80], [80, 120]]
    
    plt.close()
    
    fig = plt.figure()

    fig.set_size_inches(15, 6)

    name = name + '\nBus: ' + str(bus)
    plt.suptitle(name, x=0.5, y=1)
    for i in range(0,2):
        ax = fig.add_subplot(1, 2, i+1, projection='3d')
        Z = histVec[i].T
        X, Y = np.meshgrid(xbinsVec[i][:-1], ybinsVec[i][:-1])
        color_dimension = Z
        m = plt.cm.ScalarMappable(norm=LogNorm(), cmap='jet')
        m.set_array([])
        fcolors = m.to_rgba(color_dimension)
        ax.plot_surface(X,Y,Z, rstride=1, cstride=1, facecolors=fcolors, 
                        shade=True)
        ax.set_xlabel('Channel [a.u.]')
        ax.set_ylabel('Charge [ADC Channels]')
        ax.set_zlabel('Counts')
        ax.set_xlim(xlimVec[i])
    
        plt.title(nameVec[i], x=0.5, y=1.02)
        

    plot_path = get_plot_path(data_set) + name  + '.pdf'
    return fig, plot_path
 
    
# =============================================================================
# 4. Coincidence Histogram (2D)
# =============================================================================

def plot_2D_hit(df_clu, bus, number_of_detectors, loc, fig, count_range, 
                buses_per_row, ADC_filter):
    df = df_clu[(df_clu.wCh != -1) & (df_clu.gCh != -1)]
    
    df_clu_red = df
    
    if ADC_filter != None:
        minADC = ADC_filter[0]
        maxADC = ADC_filter[1]
    
        df_clu_red = df[  (df.wADC >= minADC) & (df.wADC <= maxADC) 
                        & (df.gADC >= minADC) & (df.gADC <= maxADC)]
    
    plt.subplot(number_of_detectors,buses_per_row,loc+1)
    plt.hist2d(df_clu_red.wCh, df_clu_red.gCh, bins=[80, 40], 
               range=[[-0.5,79.5],[79.5,119.5]], norm=LogNorm(), 
                       vmin=count_range[0], vmax=count_range[1],
               cmap='jet')
    plt.xlabel("Wire [Channel number]")
    plt.ylabel("Grid [Channel number]")
    
    plt.colorbar()
    name = 'Bus ' + str(bus) + '\n(' + str(df_clu_red.shape[0]) + ' events)'
    plt.title(name)
    
def plot_2D_hit_buses(fig, name, clusters, bus_vec, number_of_detectors, 
                      data_set, count_range, ADC_filter, m_range, ts_range):
    
    if m_range != None:
        minWM = m_range[0]
        maxWM = m_range[1]
        minGM = m_range[2]
        maxGM = m_range[3]
    
        clusters = clusters[  (clusters.wM >= minWM) & (clusters.wM <= maxWM) 
                            & (clusters.gM >= minGM) & (clusters.wM <= maxGM)]
    
    buses_per_row = None
    number_of_detectors = None
    if len(bus_vec) < 3:
        buses_per_row = len(bus_vec)
        number_of_detectors = 1
        figwidth = 14 * len(bus_vec) / 3
    else:
        number_of_detectors = np.ceil(len(bus_vec) / 3)
        buses_per_row = 3
        figwidth = 14
            
    name = (name + '\nTimestamp range: ' + str(ts_range))
    fig.suptitle(name, x=0.5, y=1.09)
    fig.set_figheight(4 * number_of_detectors)
    fig.set_figwidth(figwidth)
    for loc, bus in enumerate(bus_vec):
        df_clu = clusters[clusters.Bus == bus]
        plot_2D_hit(df_clu, bus, number_of_detectors, loc, fig, count_range, 
                    buses_per_row, ADC_filter)
    plt.tight_layout()

    plot_path = (get_plot_path(data_set) + name + ', Count range: ' 
                 + str(count_range) + ', ADC filter: ' + str(ADC_filter) 
                 + ', Multiplicity filter: ' + str(m_range) + '.pdf')
    
    return fig, plot_path

    
# =============================================================================
# 5. Coincidence Histogram (3D)
# =============================================================================  
    
def plot_all_sides_3D(fig, name, coincident_events, bus_order, countThres, alpha, 
                      data_set, number_of_detectors, ADC_filter, m_range,
                      isAnimation=False):
    
    df_tot = pd.DataFrame()
    
    for i, bus in enumerate(bus_order):
        df_clu = coincident_events[coincident_events.Bus == bus]
        df_clu = df_clu[(df_clu.wCh != -1) & (df_clu.gCh != -1)]
        
        if ADC_filter != None:
            minADC = ADC_filter[0]
            maxADC = ADC_filter[1]
            df_clu = df_clu[  (df_clu.wADC >= minADC) & (df_clu.wADC <= maxADC) 
                            & (df_clu.gADC >= minADC) & (df_clu.gADC <= maxADC)]
            
        df_clu['wCh'] += (80 * i)
        df_tot = pd.concat([df_tot, df_clu])
    
    if m_range != None:
        minWM = m_range[0]
        maxWM = m_range[1]
        minGM = m_range[2]
        maxGM = m_range[3]
    
        df_tot = df_tot[  (df_tot.wM >= minWM) & (df_tot.wM <= maxWM) 
                        & (df_tot.gM >= minGM) & (df_tot.wM <= maxGM)]
    
    x = np.floor(df_tot['wCh'] / 20).astype(int)
    y = df_tot['gCh'] - 80
    z = df_tot['wCh'] % 20
    
    df_3d = pd.DataFrame()
    df_3d['x'] = x
    df_3d['y'] = y
    df_3d['z'] = z
        
    H, edges = np.histogramdd(df_3d.values, bins=(12*number_of_detectors, 40, 20), range=((0,12*number_of_detectors), 
                                             (0,40), (0,20)))
    minCount = None
    maxCount = None
    if countThres != None:
        minCount = countThres[0]
        maxCount = countThres[1]
    else:
        minCount = 0
        maxCount = np.inf
        countThres = [0,np.inf]

    hist = np.empty([4, H.shape[0]*H.shape[1]*H.shape[2]], dtype='int')
    loc = 0
    for i in range(0,12*number_of_detectors):
        for j in range(0,40):
            for k in range(0,20):
                if H[i,j,k] > minCount and H[i,j,k] <= maxCount:
                    hist[0][loc] = i + 1
                    hist[1][loc] = j + 1
                    hist[2][loc] = k + 1
                    hist[3][loc] = H[i,j,k]
                    loc = loc + 1
    
    if isAnimation:
        hist[0][loc] = 1000
        hist[1][loc] = 1000
        hist[2][loc] = 1000
        hist[3][loc] = 1
        loc = loc + 1
        hist[0][loc] = 1001
        hist[1][loc] = 1000
        hist[2][loc] = 1000
        hist[3][loc] = 300
        loc = loc + 1
        
                        
    return scatter3d(fig, hist[0][0:loc], hist[2][0:loc], hist[1][0:loc], 
                     hist[3][0:loc], countThres, data_set, alpha, name, 
                     number_of_detectors, ADC_filter, m_range, isAnimation)

    
def scatter3d(fig, x, y, z, cs, countThres, data_set, alpha, name, 
              number_of_detectors, ADC_filter, m_range, isAnimation, 
              colorsMap='jet'):
    
    
    cm = plt.get_cmap(colorsMap)
    #norm = Normalize(vmin=1, vmax=50, clip=False)

    scalarMap = cmx.ScalarMappable(norm=LogNorm(), cmap=cm)


    name = (name + '\nCount limit: ' 
            + str(countThres) + ' counts')
    fig.suptitle(name ,x=0.5, y=1.06)
    
    if isAnimation:
        ax1 = fig.add_subplot(121, projection='3d')
    else:
        ax1 = Axes3D(fig)

    
    ax1.scatter(x, y, z, c=scalarMap.to_rgba(cs), marker= "o", s=50, 
               alpha = alpha)
   
    ax1.set_xlabel('Layer')
    ax1.set_ylabel('Wire')
    ax1.set_zlabel('Grid')
    
#    ax.set_xticks(np.arange(0, 12*number_of_detectors + 2, step=2))
#    ax.set_xticklabels(np.arange(0, 12*number_of_detectors + 2, step=2))
    ax1.set_xlim([0,12*number_of_detectors])
#    
#    ax.set_yticks(np.arange(0, 25, step=5))
#    ax.set_yticklabels(np.arange(0, 25, step=5))
    ax1.set_ylim([0,20])
#   
#    ax.set_zticks(np.arange(0, 50, step=10))
#    ax.set_zticklabels(np.arange(0, 50, step=10))
    ax1.set_zlim([0,40])
    
    
    scalarMap.set_array(cs)
    fig.colorbar(scalarMap)
#    cbar = plt.colorbar(cs, ax1)
#    cbar.set_clim(vmin=1, vmax=50)
    
    plot_path = (get_plot_path(data_set) + name + ', ADC filter: ' 
                 + str(ADC_filter) + ', Multiplicity filter: ' 
                 + str(m_range) + '.pdf')
    
    return fig, plot_path
    
# =============================================================================
# 6. Coincidence Histogram (Front, Top, Side)
# =============================================================================
    
def plot_2D_side_1(bus_vec, df, fig, number_of_detectors, count_range,
                   ADC_filter):
    name = 'Front view'
    df_tot = pd.DataFrame()
    
    locs = []
    ticks = []
    for i, bus in enumerate(bus_vec):
        df_clu = df[df.Bus == bus]
        df_clu = df_clu[(df_clu.wCh != -1) & (df_clu.gCh != -1)]
        
        if ADC_filter != None:
            minADC = ADC_filter[0]
            maxADC = ADC_filter[1]
            df_clu = df_clu[  (df_clu.wADC >= minADC) & (df_clu.wADC <= maxADC) 
                            & (df_clu.gADC >= minADC) & (df_clu.gADC <= maxADC)]
            
        df_clu['wCh'] += (80 * i) + (i // 3) * 80
        df_clu['gCh'] += (-80 + 1)
        df_tot = pd.concat([df_tot, df_clu])
    
    if df.shape[0] > 1:
        plt.hist2d(np.floor(df_tot['wCh'] / 20).astype(int) + 1, df_tot.gCh, bins=[12*number_of_detectors + 8, 40], 
                   range=[[0.5,12*number_of_detectors + 0.5 + 8],[0.5,40.5]], norm=LogNorm(), vmin=count_range[0], vmax=count_range[1],
                   cmap = 'jet')
        plt.colorbar()
    
    plt.xlabel("Layer")
    plt.ylabel("Grid")
        
    locs_x = [1, 12, 17, 28, 33, 44]
    ticks_x = [1, 12, 13, 25, 26, 38]
    plt.xticks(locs_x, ticks_x)
    
    plt.title(name)
    
def plot_2D_side_2(bus_vec, df, fig, number_of_detectors, count_range,
                   ADC_filter):
    name = 'Top view'
    df_tot = pd.DataFrame()

    for i, bus in enumerate(bus_vec):
        df_clu = df[df.Bus == bus]
        df_clu = df_clu[(df_clu.wCh != -1) & (df_clu.gCh != -1)]
        
        if ADC_filter != None:
            minADC = ADC_filter[0]
            maxADC = ADC_filter[1]
            df_clu = df_clu[  (df_clu.wADC >= minADC) & (df_clu.wADC <= maxADC) 
                            & (df_clu.gADC >= minADC) & (df_clu.gADC <= maxADC)]
        
        df_clu['wCh'] += (80 * i) + (i // 3) * 80
        
        df_tot = pd.concat([df_tot, df_clu])  
    
    if df.shape[0] > 1:
        plt.hist2d(np.floor(df_tot['wCh'] / 20).astype(int) + 1, df_tot['wCh'] % 20 + 1, 
                   bins=[12*number_of_detectors + 8, 20], range=[[0.5,12*number_of_detectors + 0.5 + 8],[0.5,20.5]], norm=LogNorm(), vmin=count_range[0], 
                   vmax=count_range[1], cmap = 'jet')
        plt.colorbar()
    
    plt.xlabel("Layer")
    plt.ylabel("Wire")
    
    
    locs_x = [1, 12, 17, 28, 33, 44]
    ticks_x = [1, 12, 13, 25, 26, 38]
    plt.xticks(locs_x, ticks_x)
    
    plt.title(name)
    
def plot_2D_side_3(bus_vec, df, fig, number_of_detectors, count_range,
                   ADC_filter):
    name = 'Side view'
    df_tot = pd.DataFrame()
    
    for i, bus in enumerate(bus_vec):
        df_clu = df[df.Bus == bus]
        df_clu = df_clu[(df_clu.wCh != -1) & (df_clu.gCh != -1)]
        
        if ADC_filter != None:
            minADC = ADC_filter[0]
            maxADC = ADC_filter[1]
            df_clu = df_clu[  (df_clu.wADC >= minADC) & (df_clu.wADC <= maxADC) 
                            & (df_clu.gADC >= minADC) & (df_clu.gADC <= maxADC)]
            
        df_clu['gCh'] += (-80 + 1)
        df_tot = pd.concat([df_tot, df_clu])
    
    if df.shape[0] > 1:
        plt.hist2d(df_tot['wCh'] % 20 + 1, df_tot['gCh'],
                   bins=[20, 40], range=[[0.5,20.5],[0.5,40.5]], norm=LogNorm(), 
                   vmin=count_range[0], vmax=count_range[1], cmap = 'jet')
        plt.colorbar()
        
    plt.xlabel("Wire")
    plt.ylabel("Grid")
    plt.title(name)
    
def plot_all_sides(fig, name, bus_vec, df, data_set, number_of_detectors, 
                   count_range, ADC_filter, m_range, tof_range, 
                   isAnimation=False):
    
    if isAnimation:
        fig.set_figheight(8)
        fig.set_figwidth(14)
    else:
        fig.set_figheight(4)
        fig.set_figwidth(14)
    
    if m_range != None:
        minWM = m_range[0]
        maxWM = m_range[1]
        minGM = m_range[2]
        maxGM = m_range[3]
    
        df = df[  (df.wM >= minWM) & (df.wM <= maxWM) 
                 & (df.gM >= minGM) & (df.wM <= maxGM)]
    
    height = 1
    if isAnimation:
        height=2
    
        
    plt.subplot(height,3,1)
    plot_2D_side_1(bus_vec, df, fig, number_of_detectors, count_range,
                   ADC_filter)
    plt.subplot(height,3,2)
    plot_2D_side_2(bus_vec, df, fig, number_of_detectors, count_range,
                   ADC_filter)
    plt.subplot(height,3,3)
    plot_2D_side_3(bus_vec, df, fig, number_of_detectors, count_range,
                   ADC_filter)
    
    name = (name)
    fig.suptitle(name, x=0.5, y=1.08)
    plt.tight_layout()

    plot_path = (get_plot_path(data_set) + name + 'Count range: ' 
                 + str(count_range) + ', ADC filter: ' 
                 + str(ADC_filter)  
                 + ', Multiplicity filter: ' + str(m_range) 
                 + ', ToF range: ' + str(tof_range) + '.pdf')
    
    return fig, plot_path
    
# =============================================================================
# 7. Multiplicity
# =============================================================================       
    
def plot_2D_multiplicity(coincident_events, number_of_detectors, bus, loc, 
                         fig, m_range, count_range, ADC_filter, buses_per_row):
    df_clu = coincident_events[coincident_events.Bus == bus]
    
    if ADC_filter != None:
            minADC = ADC_filter[0]
            maxADC = ADC_filter[1]
            df_clu = df_clu[  (df_clu.wADC >= minADC) & (df_clu.wADC <= maxADC) 
                            & (df_clu.gADC >= minADC) & (df_clu.gADC <= maxADC)]
    
    plt.subplot(number_of_detectors, buses_per_row, loc+1)
    hist, xbins, ybins, im = plt.hist2d(df_clu.wM, df_clu.gM, bins=[m_range[1]-m_range[0]+1, m_range[3]-m_range[2]+1], 
                                        range=[[m_range[0],m_range[1]+1],[m_range[2],m_range[3]+1]],
                                        norm=LogNorm(), vmin=count_range[0], vmax=count_range[1], 
                                        cmap = 'jet')
    tot = df_clu.shape[0]
    font_size = 7
    for i in range(len(ybins)-1):
        for j in range(len(xbins)-1):
            if hist[j,i] > 0:
                text = plt.text(xbins[j]+0.5,ybins[i]+0.5, 
                         str(format(100*(round((hist[j,i]/tot),3)),'.1f')) + 
                         "%", color="w", ha="center", va="center", 
                         fontweight="bold", fontsize=font_size)
                text.set_path_effects([path_effects.Stroke(linewidth=1, foreground='black'),
                       path_effects.Normal()])
        
    ticks_x = np.arange(m_range[0],m_range[1]+1,1)
    locs_x = np.arange(m_range[0] + 0.5, m_range[1]+1.5,1)
    ticks_y = np.arange(m_range[2],m_range[3]+1,1)
    locs_y = np.arange(m_range[2] + 0.5, m_range[3]+1.5,1)
    
    plt.xticks(locs_x,ticks_x)
    plt.yticks(locs_y,ticks_y)
    plt.xlabel("Wire Multiplicity")
    plt.ylabel("Grid Multiplicity")

    plt.colorbar()
    plt.tight_layout()
    name = 'Bus ' + str(bus) + '\n(' + str(df_clu.shape[0]) + ' events)' 
    plt.title(name)

def plot_2D_multiplicity_buses(fig, name, coincident_events, module_order, 
                               number_of_detectors, data_set, m_range, 
                               count_range, ADC_filter, ts_range):
    
    if count_range == None:
        count_range = [1, 1e6]
    if m_range == None:
        m_range = [0,8,0,8]
    
    buses_per_row = None
    number_of_detectors = None
    if len(module_order) < 3:
        buses_per_row = len(module_order)
        number_of_detectors = 1
        figwidth = 14 * len(module_order) / 3
    else:
        number_of_detectors = np.ceil(len(module_order) / 3)
        buses_per_row = 3
        figwidth = 14
    
    
    
    name = name + '\nTimestamp range: ' + str(ts_range)
    fig.suptitle(name, x=0.5, y=1.08)
    fig.set_figheight(4*number_of_detectors)
    fig.set_figwidth(figwidth)
    for loc, bus in enumerate(module_order):
        plot_2D_multiplicity(coincident_events, number_of_detectors, bus, loc, 
                             fig, m_range, count_range, ADC_filter, 
                             buses_per_row)

    plt.tight_layout()
    plot_path = (get_plot_path(data_set) + name + ' Multiplicity range: ' 
                 + str(m_range) + ', Count range: ' + str(count_range) 
                 + ', ADC filter: ' + str(ADC_filter) + 
                 ', Buses: ' + str(module_order) + '.pdf')
    
    return fig, plot_path


# =============================================================================
# 8. Scatter Map (collected charge in wires and grids)
# =============================================================================

def charge_scatter(df, bus, number_of_detectors, loc, fig, minWM, 
                   maxWM, minGM, maxGM, exclude_channels, buses_per_row):

    df_red = df[(df.Bus == bus) & (df.gM >= minWM) &
                (df.wM <= maxWM) & (df.gM >= minGM) & (df.gM <= maxGM)]
    
    for Channel in exclude_channels:
        if Channel < 80:
            df_red = df_red[df_red.wCh != Channel]
        else:
            df_red = df_red[df_red.gCh != Channel]
    
    plt.subplot(number_of_detectors, buses_per_row, loc+1)

    plt.hist2d(df_red.wADC, df_red.gADC, bins=[200, 200], 
               norm=LogNorm(),range=[[0, 5000], [0, 5000]], vmin=1, vmax=10000,
               cmap='jet')
    plt.xlabel("wADC [ADC channels]")
    plt.ylabel("gADC [ADC channels]")
    plt.colorbar()
    name = 'Bus ' + str(bus) + '\n(' + str(df_red.shape[0]) + ' events)'
    plt.title(name)
    
def plot_charge_scatter_buses(fig, name, df, bus_order, number_of_detectors, data_set, 
                              minWM = 0, maxWM = 100, minGM = 0, maxGM = 100,
                              exclude_channels = [-1], ts_range = [0, np.inf]):
    
    buses_per_row = None
    number_of_detectors = None
    if len(bus_order) < 3:
        buses_per_row = len(bus_order)
        number_of_detectors = 1
        figwidth = 14 * len(bus_order) / 3
    else:
        number_of_detectors = np.ceil(len(bus_order) / 3)
        buses_per_row = 3
        figwidth = 14

    name = (name + '\n' 
            + '(wm_min: ' + str(minWM) + 
            ', wm_max: ' + str(maxWM) +
            ', gm_min: ' + str(minGM) +
            ', gm_max: ' + str(maxGM) +
            ', excluded channels: ' + str(exclude_channels) +
            ')' + '\nTimestamp range: ' + str(ts_range))
    
    fig.suptitle(name, x=0.5, y=1.12)
    fig.set_figheight(4 * number_of_detectors)
    fig.set_figwidth(figwidth)
    for loc, bus in enumerate(bus_order):
        df_clu = df[df.Bus == bus]
        charge_scatter(df_clu, bus, number_of_detectors, loc, fig, minWM, maxWM, 
                       minGM, maxGM, exclude_channels, buses_per_row)

    plt.tight_layout()

    plot_path = (get_plot_path(data_set) + name + ', Buses: ' + str(bus_order) 
                + '.pdf')
    
    return fig, plot_path
    

# =============================================================================
# 9. ToF histogram
# =============================================================================
    
def plot_ToF_histogram(fig, name, df, data_set, number_bins = None, rnge=None,
                       ADC_filter = None, log = False):
    
    if ADC_filter != None:
        minADC = ADC_filter[0]
        maxADC = ADC_filter[1]
        df = df[  (df.wADC >= minADC) & (df.wADC <= maxADC) 
                & (df.gADC >= minADC) & (df.gADC <= maxADC)]
    
    
    hist, bins, patches = plt.hist(df.ToF, bins=number_bins, range=rnge, 
                                   log=log, color='b')
    plt.title(name)
    plt.xlabel('ToF [TDC channels]')
    plt.ylabel('Counts  [a.u.]')
    plot_path = (get_plot_path(data_set) + name + ' Range: ' + str(rnge) +
                 'Number of bins: ' + str(number_bins) + '.pdf')
             
    return fig, plot_path

    

# =============================================================================
# 10. Events per Channel
# =============================================================================

def plot_event_count(fig, name, module_order, number_of_detectors, data_set, events, 
                     log=False, v_range=[1,100000], ADC_filter = None):
    
    
    buses_per_row = None
    number_of_detectors = None
    
    if len(module_order) < 3:
        buses_per_row = len(module_order)
        number_of_detectors = 1
        figwidth = 14 * len(module_order) / 3
    else:
        number_of_detectors = np.ceil(len(module_order) / 3)
        buses_per_row = 3
        figwidth = 14

    fig.suptitle(name, x=0.5, y=1.08)
    fig.set_figheight(4 * number_of_detectors)
    fig.set_figwidth(figwidth)
    for i, bus in enumerate(module_order):
        plt.subplot(number_of_detectors, buses_per_row, i+1)
        plt.title('Bus ' + str(bus))
        
        if ADC_filter != None:
            minADC = ADC_filter[0]
            maxADC = ADC_filter[1]
            events = events[(events.ADC >= minADC) & (events.ADC <= maxADC)]
        
        plt.hist(events[events.Bus == bus].Channel, range= [-0.5,119.5], 
                 bins=120, log=log, color = 'b')
        plt.xlabel('Channel [a.u.]')
        plt.ylabel('Number of events [a.u.]')
        plt.ylim(v_range)
    plt.tight_layout()

    plot_path = (get_plot_path(data_set) + name + ', module order: ' + 
                 str(module_order) + ', count range: ' + str(v_range) 
                 + ', is log: ' + str(log) + '.pdf')
    
    return fig, plot_path

# =============================================================================
# 11. Timestamp and Trigger
# =============================================================================

def plot_timestamp_and_trigger(fig, name, data_set, coincident_events, 
                               triggers):
    
    fig.suptitle(name, x=0.5, y=1.08)
    
    fig.set_figheight(4)
    fig.set_figwidth(8)
    
    df = coincident_events

    event_number = np.arange(0, df.shape[0],1)
    trigger_number = np.arange(0,len(triggers),1)
    
    plt.subplot(1,2,1)
    plt.title('Timestamp vs. Event number', x=0.5, y=1.04)
    plt.xlabel('Event number')
    plt.ylabel('Timestamp')
    plt.plot(event_number, df.Time, color='blue', label='All events')
    glitches = df[(df.wM >= 80) & (df.gM >= 40)].Time
    plt.plot(glitches.index.tolist(), glitches, 'rx', label='Glitch events')
    plt.legend()
    
    plt.subplot(1,2,2)
    plt.title('Trigger-time vs. Trigger number', x=0.5, y=1.04)
    plt.xlabel('Trigger number')
    plt.ylabel('Trigger time')
    plt.plot(trigger_number, triggers, color='blue')
    
    plt.tight_layout()
    
    plot_path = get_plot_path(data_set) + name + '.pdf'
        
    return fig, plot_path

# =============================================================================
# 12. Delta E histogram (compare filters)
# =============================================================================
    
def dE_histogram(fig, name, df, data_set, E_i, ToF_min, ToF_max):
    T_0 = get_T0(calibration, E_i)
    t_off = get_t_off(E_i)
    

    df = df[df.d != -1]
    df = df[(df.wM == 1) & (df.gM < 5)]
        
    name = ('12. Histogram of $E_i$ - $E_f$, ' + str(E_i) + 'meV')
    fig.suptitle(name, x=0.5, y=1.05)
    dE_bins = 500
    dE_range = [-E_i, E_i]
    plt.subplot(2, 1, 1)
    plt.grid(True, which='major', zorder=0)
    plt.grid(True, which='minor', linestyle='--',zorder=0)
    plt.hist(df.dE, bins=dE_bins, range=dE_range, log=LogNorm(), 
             color='black', histtype='step', label='Without filter', 
             zorder=3)
    plt.hist(df[(df.wADC >= 500) & (df.gADC >= 400) 
                & (df.ToF >= ToF_min) & (df.ToF <= ToF_max)].dE, bins=dE_bins, 
             range=dE_range, log=LogNorm(), color='red', histtype='step', 
             label='With filter', zorder=3)
    plt.legend()
    plt.xlabel('$E_i$ - $E_f$ [meV]')
    plt.ylabel('Intensity [Counts]')
    plt.title('Histogram of $E_i$ - $E_f$')
    
    plt.subplot(2, 1, 2)
    plt.grid(True, which='major', zorder=0)
    plt.grid(True, which='minor', linestyle='--',zorder=0)
    plt.hist(df.ToF * 62.5e-9 * 1000, bins=1000, range=[0, 30], log=LogNorm(), 
             histtype='step', color='black', zorder=2, label='Without filter')
    plt.hist(df[(df.ToF >= ToF_min) & (df.ToF <= ToF_max)].ToF * 62.5e-9 * 1000, 
                bins=1000, range=[0, 30], log=LogNorm(), histtype='step', 
                color='red', zorder=2, label='With filter')
    plt.xlabel('ToF [$\mu$s]')
    plt.ylabel('Intensity [Counts]')
    plt.title('ToF histogram')
    plt.legend()

    
        
    plt.tight_layout()
    plot_path = get_plot_path(data_set) + name + '.pdf'
        
    return fig, plot_path

# =============================================================================
# 13. Delta E
# =============================================================================
    
def dE_single(fig, name, df, data_set, E_i, sample, 
              left_edge=175, right_edge=220):
        df = filter_clusters(df)
        
        def find_nearest(array, value):
            idx = (np.abs(array - value)).argmin()
            return idx

        bus_ranges = [[0,2], [3,5], [6,8]]
        color_vec = ['darkorange', 'magenta', 'blue']
        detectors = ['ILL', 'ESS_1', 'ESS_2']
        dE_bins = 400
        dE_range = [-E_i, E_i]
        
        name = ('13. ' + sample + ', ' + str(E_i) + 'meV')
        plt.grid(True, which='major', zorder=0)
        plt.grid(True, which='minor', linestyle='--',zorder=0)
                
        hist, bins, patches = plt.hist(df.dE, bins=dE_bins, range=dE_range, 
                                       log=LogNorm(), color='black', 
                                       histtype='step', zorder=2, 
                                       label='All detectors')
        
        bin_centers = 0.5 * (bins[1:] + bins[:-1])
        
        # Calculate background level
        x_l = bin_centers[left_edge]
        y_l = hist[left_edge]
        x_r = bin_centers[right_edge-1]
        y_r = hist[right_edge-1]
        par_back = np.polyfit([x_l, x_r], [y_l, y_r], deg=1)
        f_back = np.poly1d(par_back)
        xx_back = np.linspace(x_l, x_r, 100)
        yy_back = f_back(xx_back)
        
        plt.plot(xx_back, yy_back, 'orange', label='Background')
        
        bins_under_peak = abs(right_edge - 1 - left_edge)
        
        area_noise = ((abs(y_r - y_l) * bins_under_peak) / 2 
                      + bins_under_peak * y_l)
        
        area = sum(hist[left_edge:right_edge])
        peak_area = area - area_noise
        
        # Calculate HM
        peak = peakutils.peak.indexes(hist[left_edge:right_edge])
        plt.plot(bin_centers[left_edge:right_edge][peak],
                 hist[left_edge:right_edge][peak], 'bx', label='Maximum', 
                 zorder=5)
        M = hist[left_edge:right_edge][peak]
        xM = bin_centers[left_edge:right_edge][peak]
        print(xM)
        noise_level = yy_back[find_nearest(xx_back, xM)]
        print(noise_level)
        HM = (M-noise_level)/2 + noise_level

        # Calculate FWHM
        left_idx = find_nearest(hist[left_edge:left_edge+peak[0]], HM)
        right_idx = find_nearest(hist[left_edge+peak[0]:right_edge], HM)
        
        sl = []
        sr = []
        
        if hist[left_edge+left_idx] > HM:
            sl = [-1, 0]
        else:
            sl = [0, 1]
        
        if hist[left_edge+peak[0]+right_idx] < HM:
            rl = [-1, 0]
        else:
            rl = [0, 1]
        
        left_x = [bin_centers[left_edge+left_idx+sl[0]], 
                  bin_centers[left_edge+left_idx+sl[1]]]
        left_y = [hist[left_edge+left_idx+sl[0]], hist[left_edge+left_idx+sl[1]]]
        right_x = [bin_centers[left_edge+peak[0]+right_idx+rl[0]], 
                   bin_centers[left_edge+peak[0]+right_idx+rl[1]]]
        right_y = [hist[left_edge+peak[0]+right_idx+rl[0]], 
                   hist[left_edge+peak[0]+right_idx+rl[1]]]

        par_left = np.polyfit(left_x, left_y, deg=1)
        f_left = np.poly1d(par_left)
        par_right = np.polyfit(right_x, right_y, deg=1)
        f_right = np.poly1d(par_right)
        
        xx_left = np.linspace(left_x[0], left_x[1], 100)
        xx_right = np.linspace(right_x[0], right_x[1], 100)
        yy_left = f_left(xx_left)
        yy_right = f_right(xx_right)
        plt.plot(xx_left, yy_left, 'blue', label=None)
        plt.plot(xx_right, yy_right, 'blue', label=None)
        
        left_idx = find_nearest(yy_left, HM)
        right_idx = find_nearest(yy_right, HM)
        
        
        
        plt.plot([xx_left[left_idx], xx_right[right_idx]], 
                 [HM, HM], 'g', label='FWHM')
        
        L = xx_left[left_idx]
        R = xx_right[right_idx]
        FWHM = R - L
#        noise_level = ((hist[right_edge] + hist[left_edge])/2) 
#        peak_area = (area - 
#                     noise_level
#                     * (bin_centers[right_edge] - bin_centers[left_edge])
#                     )
        
        
        plt.text(0, 1, 'Area: ' + str(int(peak_area)) + ' [counts]' + '\nFWHM: ' + str(round(FWHM,3)) + '  [meV]', ha='center', va='center', 
                 bbox={'facecolor':'white', 'alpha':0.8, 'pad':10})
#        
#        plt.plot([bin_centers[left_edge], bin_centers[right_edge]], 
#                 [hist[left_edge], hist[right_edge]], 'bx', mew=3, ms=10,
#                 label='Peak edges', zorder=5)
                 
        plt.plot(bin_centers[left_edge:right_edge], hist[left_edge:right_edge],
                 'r.-', label='Peak')
        
        plt.legend(loc='upper left')
        plt.xlabel('$\Delta E$ [meV]')
        plt.ylabel('Counts')
        name = name + ', Histogram of $E_i$ - $E_f$'
        plt.title(name)
        
#        folder = get_output_path(data_set)
#        hist_path = folder + name + ', histogram.dat'
#        bins_path = folder + name + ', bins.dat'
#        np.savetxt(hist_path, hist, delimiter=",")
#        np.savetxt(bins_path, bins, delimiter=",")
            
        
        plot_path = get_plot_path(data_set) + name + '.pdf'

        
        return fig, plot_path
    
    
# =============================================================================
# 14. ToF vs d + dE
# =============================================================================
        
    
def ToF_vs_d_and_dE(fig, name, df, data_set, E_i, plot_separate):
        df = df[df.d != -1]
        df = df[df.tf > 0]
        df = df[(df.wADC > 300) & (df.gADC > 300)]
        bus_ranges = [[0,2], [3,5], [6,8]]
        
        name = ('14. Histogram of $E_i$ - $E_f$, Vanadium, ' + str(E_i) + 'meV')
        
        detectors = ['ILL', 'ESS (Natural Al)', 'ESS (Pure Al)']
            
        color_vec = ['darkorange', 'magenta', 'blue']
        
        dE_bins = 1000
        dE_range = [-E_i, E_i]
        
        ToF_bins = 200
        ToF_range = [0, 20e3]
        
        d_bins = 100
        d_range = [5.9, 6.5]
        
        tf_bins = 200
        tf_range = [0, 20e3]
        if plot_separate:
            fig.set_figheight(9)
            fig.set_figwidth(12)
            fig.suptitle(name, x=0.5, y=1.05)
            for i, bus_range in enumerate(bus_ranges):
#                # Plot ToF vs d
                title = detectors[i]
                plt.subplot(3, 3, i+1)
                bus_min = bus_range[0]
                bus_max = bus_range[1]
                df_temp = df[(df.Bus >= bus_min) & (df.Bus <= bus_max)]
                plt.hist2d(df_temp.tf * 1e6, df_temp.d, 
                           bins = [ToF_bins, d_bins],
                           norm=LogNorm(), vmin=1, vmax=6e3, cmap='jet')
                plt.xlabel('$t_f$ [$\mu$s]')
                plt.ylabel('d [m]')
                plt.title(title + ', $t_f$ vs d')
                plt.colorbar()
                # Plot dE
                plt.subplot(3, 3, 3+i+1)
                plt.grid(True, which='major', zorder=0)
                plt.grid(True, which='minor', linestyle='--',zorder=0)
                plt.hist(df_temp.dE, bins=dE_bins, range=dE_range, log=LogNorm(), 
                         color=color_vec[i], histtype='step', label=title, 
                         zorder=3)
                plt.hist(df.dE, bins=dE_bins, range=dE_range, log=LogNorm(), 
                         color='black', histtype='step', label='All detectors', 
                         zorder=2)
                plt.legend(loc='upper left')
                plt.xlabel('$E_i$ - $E_f$ [meV]')
                plt.ylabel('Counts')
                plt.title(title)
                # Plot ToF
                plt.subplot(3, 3, 6+i+1)
                plt.grid(True, which='major', zorder=0)
                plt.grid(True, which='minor', linestyle='--',zorder=0)
                plt.hist(df_temp.ToF * 62.5e-9 * 1e6, bins=1000,
                         log=LogNorm(), 
                         color=color_vec[i], histtype='step', 
                         zorder=3)
                plt.xlabel('ToF [$\mu$s]')
                plt.ylabel('Counts')
                plt.title(title + ', Histogram of ToF')
        else:
            plt.grid(True, which='major', zorder=0)
            plt.grid(True, which='minor', linestyle='--',zorder=0)
            plt.xlabel('$E_i$ - $E_f$ [meV]')
            plt.ylabel('Counts')
            for i, bus_range in enumerate(bus_ranges):
                title = detectors[i]
                bus_min = bus_range[0]
                bus_max = bus_range[1]
                df_temp = df[(df.Bus >= bus_min) & (df.Bus <= bus_max)]
                plt.hist(df_temp.dE, bins=dE_bins, range=dE_range, log=LogNorm(), 
                         color=color_vec[i], histtype='step', label=title, 
                         zorder=3)
            plt.hist(df.dE, bins=dE_bins, range=dE_range, log=LogNorm(), 
                     color='black', histtype='step', label='All detectors', 
                     zorder=2)
            plt.legend(loc='upper left')
            plt.title(name)
        
        plt.tight_layout()
        plot_path = get_plot_path(data_set) + name + '.pdf'
                
                
                
        
        return fig, plot_path
    
# =============================================================================
# 15. Compare cold and thermal
# =============================================================================
        
def compare_cold_and_thermal(fig, name, data_set, E_i):
    dirname = os.path.dirname(__file__)
    clusters_folder = os.path.join(dirname, '../Clusters/')
    clu_files = os.listdir(clusters_folder)
    clu_files = [file for file in clu_files if file[-3:] == '.h5']

    
    name = ('15. Vanadium, ' + str(E_i) + 'meV\n Comparrison between cold and'
            + ' thermal')
    
    dE_bins = 400
    dE_range = [-E_i, E_i]
    
    print()
    print('**************** Choose cold data ***************')
    print('-------------------------------------------------')
    not_int = True
    not_in_range = True
    file_number = None
    while (not_int or not_in_range):
        for i, file in enumerate(clu_files):
            print(str(i+1) + '. ' + file)
    
        file_number = input('\nEnter a number between 1-' + 
                            str(len(clu_files)) + '.\n>> ')
    
        try:
            file_number = int(file_number)
            not_int = False
            not_in_range = (file_number < 1) | (file_number > len(clu_files))
        except ValueError:
            pass
    
        if not_int or not_in_range:
            print('\nThat is not a valid number.')
    
    clu_set = clu_files[int(file_number) - 1]
    clu_path_cold = clusters_folder + clu_set
    
    print()
    print('*************** Choose thermal data *************')
    print('-------------------------------------------------')
    not_int = True
    not_in_range = True
    file_number = None
    while (not_int or not_in_range):
        for i, file in enumerate(clu_files):
            print(str(i+1) + '. ' + file)
    
        file_number = input('\nEnter a number between 1-' + 
                            str(len(clu_files)) + '.\n>> ')
    
        try:
            file_number = int(file_number)
            not_int = False
            not_in_range = (file_number < 1) | (file_number > len(clu_files))
        except ValueError:
            pass
    
        if not_int or not_in_range:
            print('\nThat is not a valid number.')
    
    clu_set = clu_files[int(file_number) - 1]
    clu_path_thermal = clusters_folder + clu_set
    
    print('Loading...')
    tc = pd.read_hdf(clu_path_thermal, 'coincident_events')
    cc = pd.read_hdf(clu_path_cold, 'coincident_events')
    tc = filter_clusters(tc)
    cc = filter_clusters(cc)
    
    size_cold = cc.shape[0]
    size_thermal = tc.shape[0]
    

    plt.title(name)
    plt.grid(True, which='major', zorder=0)
    plt.grid(True, which='minor', linestyle='--',zorder=0)
    
    plt.hist(tc.dE, bins=dE_bins, range=dE_range, log=LogNorm(), 
                     color='red', histtype='step', density=True,
                     zorder=2, label='Thermal sample')
    
    plt.hist(cc.dE, bins=dE_bins, range=dE_range, log=LogNorm(), 
                     color='blue', histtype='step', density=True,
                     zorder=2, label='Cold sample')
    
    plt.legend(loc='upper left')
    
    plt.xlabel('$E_i$ - $E_f$ [meV]')
    plt.ylabel('Normalized counts')
    
    plot_path = get_plot_path(data_set) + name + '.pdf'
    
    return fig, plot_path
    
# =============================================================================
# 16. Compare MG and Helium-tubes
# =============================================================================
    
def compare_MG_and_He3(fig, name, df, data_set, E_i, MG_offset, He3_offset,
                       only_pure_al, MG_l, MG_r):
    
    def find_nearest(array, value):
        idx = (np.abs(array - value)).argmin()
        return idx
    
    name = ('16. Vanadium, ' + str(E_i) + 'meV\n Comparrison between He3 and'
            + ' Multi-Grid')
    
    use_peak_norm = True
    
    dirname = os.path.dirname(__file__)
    he_folder = os.path.join(dirname, '../Tables/Helium3_spectrum/')
    energies_path = he_folder + 'e_list_HR.dat'
    dE_path = he_folder + 'energy_HR.dat'
    hist_path = he_folder + 'histo_HR.dat'
    
    energies = np.loadtxt(energies_path)
    dE = np.loadtxt(dE_path, delimiter=',', ndmin=2)
    hist = np.loadtxt(hist_path, delimiter=',', ndmin=2)
    
    energy_dict = {}
    for i, energy in enumerate(energies):
        hist_dict = {'bins': dE[:, i], 'histogram': hist[:, i]}
        energy_dict.update({energy: hist_dict})
    
    dE_bins = 390
    dE_range = [-E_i, E_i]
    df = filter_clusters(df)
    MG_label = 'Multi-Grid'
    if only_pure_al:
        df = df[(df.Bus >= 6) | (df.Bus <= 8)]
        MG_label += ' (Pure Aluminium)'
        name += ' (Pure Aluminium)'
    hist, bins, patches = plt.hist(df.dE, bins=dE_bins, range=dE_range)
    plt.clf()
    plt.title(name)
    plt.grid(True, which='major', zorder=0)
    plt.grid(True, which='minor', linestyle='--',zorder=0)
    
    binCenters = 0.5 * (bins[1:] + bins[:-1])
    norm_MG = 1 / sum(hist)
    if use_peak_norm:
        norm_MG = calculate_peak_norm(binCenters, hist, MG_l, MG_r)
        
    plt.plot(binCenters+MG_offset, hist / norm_MG, color='crimson', zorder=3, 
             label='Multi-Grid')
    
    data = energy_dict[E_i]
    print('Number of bins: ' + str(len(data['bins'])))
    norm_he3 = 1 / sum(data['histogram'])
    if use_peak_norm:
        He3_l = find_nearest(data['bins']+He3_offset, binCenters[MG_l]+MG_offset)
        He3_r = find_nearest(data['bins']+He3_offset, binCenters[MG_r]+MG_offset)
        norm_he3 = calculate_peak_norm(data['bins']+He3_offset, 
                                       data['histogram'], He3_l, He3_r)
    
        plt.plot([binCenters[MG_l]+MG_offset, data['bins'][He3_l]+He3_offset], 
                 [hist[MG_l]/norm_MG, data['histogram'][He3_l]/norm_he3], 'b-x', 
                 label='Peak edges', zorder=20)
        plt.plot([binCenters[MG_r]+MG_offset, data['bins'][He3_r]+He3_offset], 
                 [hist[MG_r]/norm_MG, data['histogram'][He3_r]/norm_he3], 'b-x', 
                 label=None, zorder=20)
    
    plt.plot(data['bins']+He3_offset, data['histogram'] / norm_he3, color='teal',
             label='He3', zorder=2)
    
    plt.xlabel('$E_i$ - $E_f$ [meV]')
    plt.ylabel('Normalized counts')
    plt.yscale('log')
    
    plt.legend(loc='upper left')
    
    text_string = r"$\bf{" + 'MultiGrid' + "}$" + '\n'
    text_string += 'Area: ' + str(int(norm_MG)) + ' [counts]\n'
    text_string += 'FWHM: ' + '\n'
    text_string += r"$\bf{" + 'He3' + "}$" + '\n'
    text_string += 'Area: ' + str(round(norm_he3,3)) + ' [counts]\n'
    text_string += 'FWHM: '
    
    
    plt.text(0.6*E_i, 0.04, text_string, ha='center', va='center', 
                 bbox={'facecolor':'white', 'alpha':0.8, 'pad':10}, fontsize=8)
    
    plot_path = get_plot_path(data_set) + name + '.pdf'
    
    return fig, plot_path

# =============================================================================
# 17. Plotly interactive ToF
# =============================================================================
    
def plotly_interactive_ToF(df, data_set, E_i, test_type):
    df = df[df.d != -1]
   # df = df[df.tf > 0]
    #df = df[(df.wADC > 300) & (df.gADC > 300)]
    df = df[(df.wM == 1) & (df.gM < 5)]

    nbr_bins = 500
    thres_range = np.arange(0, 600, 10)
    
    data = []
    
    if test_type == 'Wire ADC threshold':
        data = [go.Histogram(visible = False,
                             name = str(thres),
                             x = df[df.wADC >= thres].ToF,
                             xbins=dict(
                                     start=0,
                                     end=3e5,
                                     size=(3e5)/nbr_bins
                            ))
                            for thres in thres_range]
        
    elif test_type == 'Grid ADC threshold':
        data = [go.Histogram(visible = False,
                             name = str(thres),
                             x = df[df.gADC >= thres].ToF,
                             xbins=dict(
                                     start=0,
                                     end=3e5,
                                     size=(3e5)/nbr_bins
                            ))
                            for thres in thres_range]
        
   
    elif test_type == 'Grid and Wire ADC threshold':
        data = [go.Histogram(visible = False,
                             name = str(thres),
                             x = df[(df.gADC >= thres) & (df.wADC >= thres)].ToF,
                             xbins=dict(
                                     start=0,
                                     end=3e5,
                                     size=(3e5)/nbr_bins
                            ))
                            for thres in thres_range]
    
    
    

    
    data[10]['visible'] = True
    
#    bin_vec = np.arange(-E_i, E_i, 2*E_i/nbr_bins) + (2*E_i/nbr_bins)/2
    
#    hist_and_bins_vec = [np.histogram(df[df.wADC >= thres].dE, bins=nbr_bins, 
#                             range=[-E_i, E_i]) for thres in thres_range]
#        
#    bin_vec = hist_and_bins_vec[0][1]
#    bin_vec += (hist_and_bins_vec[0][1][1] - hist_and_bins_vec[0][1][0])/2
#    bin_vec = bin_vec[0:-1]
    
    
    
    
    
 #   hist_and_bins = [[bin_vec, hist] for hist in hist_vec]
    
    
    
#    data2 = [go.Histogram(visible = False,
#                         name = str(thres),
#                         x = df[df.wADC >= thres].dE,
#                         xbins=dict(
#                            start=-E_i,
#                            end=E_i,
#                            size=2*E_i/nbr_bins),
#                        )
#            for thres in thres_range]
#    
#    data2[10]['visible'] = True
    
#    
#    def exponenial_func(x, a, b, c):
#        return a*np.exp(b*x)+c
#    
#    paras_vec = []
#    bins_1 = bin_vec[:150]
#    bins_2 = bin_vec[250:]
#    bins =np.append(bins_1, bins_2)
#    for hist_and_bins in hist_and_bins_vec:
#        hist = hist_and_bins[0][-100:]
#        #paras, __ = curve_fit(exponenial_func, bins, hist, p0=(1, 0.00001, 100))
#        #paras_vec.append(paras)
#        hist_1 = hist_and_bins[0][:150]
#        hist_2 = hist_and_bins[0][250:]
#        hist = np.append(hist_1, hist_2)
##        z = np.polyfit(bins, hist, 3, w=np.sqrt(hist))
##        f = np.poly1d(z)
##        paras_vec.append(f)
#        paras, __ = curve_fit(exponenial_func, bins, hist, p0=(100, 0.001, 1))
#        print(paras)
#        paras_vec.append(paras)
#        
#        
#    
#    data3 = [go.Scatter(visible=False,
#                        x=bins,
#                        y=exponenial_func(bins, *[5, 1, 50]),
#                        mode='markers',
#                        marker=dict(
#                                size=3,
#                                color='rgb(0, 0, 0)',
#                                symbol='circle-open'
#                                ),
#                        name='Baseline'
#                        ) for paras in paras_vec]
#    
#    data3[10]['visible'] = True
    
    
    
    steps = []
    for i in range(len(data)):
        step = dict(
                method = 'restyle',  
                args = ['visible', [False] * len(data)],
                label = str(i*600//len(data))
        )
        step['args'][1][i] = True # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [dict(
        active = 10,
        currentvalue = {"prefix": test_type + " [ADC channels]: "},
        pad = {"t": 50},
        steps = steps,
    )]

#    fig = py.tools.make_subplots(rows=1, cols=2, subplot_titles=('ToF Histogram', 
#                                'Histogram of E<sub>i</sub> - E<sub>f')) 
    
#    for trace in enumerate(data):
#        fig.append_trace(trace, 1, 1)
    
#    for trace in data2:
#        fig.append_trace(trace, 1, 2)
    
#    for trace in data3:
#        fig.append_trace(trace, 1, 2)
        
#    fig['layout']['xaxis1'].update(title='ToF [TDC channels]', range=[0, 3e5], 
#                                   showgrid=True)
#    fig['layout']['yaxis1'].update(title='Counts', range=[.1, 5], type='log')
#    fig['layout']['xaxis2'].update(title='dE [meV]', range=[-E_i, E_i], 
#                                   showgrid=True)
#    fig['layout']['yaxis2'].update(title='Counts', range=[.1, 5], type='log')
#    fig.layout.sliders = sliders
#    fig.layout.title = ('Interactive ToF and dE Histograms, Vandadium, ' 
#                        + str(E_i) + ' meV') 
#    fig.layout.showlegend = False
    
   # fig = dict(data=data, layout=layout)
   
    layout = dict(sliders=sliders)
    
    layout = dict(sliders=sliders,
                  title='Interactive ToF and dE Histograms, ' + str(E_i) + 'meV, ' + str(test_type),
                  xaxis=dict(
                          title='ToF [TDC channels]',
                          range=[0, 3e5],
                          ),
                  yaxis=dict(
                          title='Counts',
                          range=[.1, 5.5],
                          type='log')
                  )

    fig = dict(data=data, layout=layout)
#    fig.layout.title = ('Interactive ToF and dE Histograms, ' + str(E_i) + 'meV')
#    fig.layout.xaxis.update(title='ToF  [TDC channels]', range=[0, 3e5])
#    fig.layout.yaxis.update(title='Counts', range=[.1, 5], type='log')
    
    filename = ('../Plot/PlotlyInteractive, ' + str(data_set) + ', ' + 
                str(E_i) + ' meV, ' + str(test_type) + '.html')
    py.offline.plot(fig, filename=filename)
    

# =============================================================================
# 18. dE - loglog-plot
# =============================================================================   

def de_loglog(fig, name, df_vec, data_set, E_i_vec):
    
    dE_bins = 500
        
    name = ('18. $C_4 H_2 I_2 S$, Histogram of $E_i$ - $E_f$' )
    
    count = 0
    end = [440, 470, 465, 475, 470, 475, 470, 475]
    multi = [4, 3, 3, 1, 1, 1, 1, 0.5]
    hists = []
    bins_vec = []
    for df, E_i in zip(df_vec, E_i_vec):
        dE_range = [-E_i, E_i]
        df = filter_clusters(df)
        weights = np.ones(df['dE'].shape[0]) * 4 ** count
        hist, bins, __ = plt.hist(df.dE, bins=dE_bins, range=dE_range, log=LogNorm(), 
                 histtype='step', weights=weights, zorder=2, label=str(E_i) + ' meV')
        bin_centers = 0.5 * (bins[1:] + bins[:-1])
        hists.append(hist)
        bins_vec.append(bin_centers)
        count += 1
    
    plt.clf()
    plt.grid(True, which='major', zorder=0)
    plt.grid(True, which='minor', linestyle='--',zorder=0)
    count = 0
    for hist, bins in zip(hists, bins_vec):
        plt.plot(bins[:end[count]], hist[:end[count]]*multi[count], zorder=2, 
                 label=str(E_i_vec[count]) + ' meV')
        count += 1

    plt.legend(loc='lower left')
    plt.xlabel('$\Delta E$ [meV]')
    plt.ylabel('Intensity [a.u.]')
    plt.xlim(0.1, max(E_i_vec))
    plt.ylim(1e3, 5e7)
    plt.xscale('log')
    plt.yscale('log')
    plt.title(name)
        
    plot_path = get_plot_path(data_set) + name + str(E_i_vec) + '.pdf'
        
    return fig, plot_path


# =============================================================================
# 19. Neutrons vs Gammas scatter plot
# ============================================================================= 
    
def neutrons_vs_gammas(fig, name, df, data_set, g_l, g_r, n_l, n_r):
    df = df[df.d != -1]
    df = df[(df.wM == 1) & (df.gM < 5)]
    bins = 1000
    ToF_range = [0, 300000]
    noise_l = 600
    noise_r = 700
    print('Calculating...')
    thres_vec = np.arange(0, 1010, 10)
    n_vec = []
    g_vec = []
    for i, thres in enumerate(thres_vec):
        df_temp = df[(df.wADC >= thres) & (df.gADC >= thres)]
        hist, __, __ = plt.hist(df_temp.ToF, bins=bins, range=ToF_range)
        background_per_bin = sum(hist[noise_l:noise_r])/(noise_r - noise_l)
        print('Background per bin: ' + str(background_per_bin))
        n_counts = sum(hist[n_l:n_r]) - background_per_bin * (n_r - n_l)
        g_counts = sum(hist[g_l:g_r]) - background_per_bin * (g_r - g_l)
        n_vec.append(n_counts)
        g_vec.append(g_counts)
        plt.clf()
        percentage_finished = str(int(round((i/len(thres_vec))*100, 1))) + '%'
        print(percentage_finished)
    print('Done!')
        
    
    fig.set_figheight(4)
    fig.set_figwidth(12)
    fig.suptitle(name, x=0.5, y=1.05)
    
    plt.subplot(1, 3, 1)
    plt.grid(True, which='major', zorder=0)
    plt.grid(True, which='minor', linestyle='--',zorder=0)
    hist, bins, __ = plt.hist(df.ToF, bins=bins, range=ToF_range, 
                              log=LogNorm(), 
                              color='black', histtype='step',  
                              zorder=3, label='All events')
    bin_centers = 0.5 * (bins[1:] + bins[:-1])
    plt.plot(bin_centers[g_l:g_r], hist[g_l:g_r], 'r-', label='Gamma peak', 
             zorder=5, linewidth=3.0)
    plt.plot(bin_centers[n_l:n_r], hist[n_l:n_r], 'b-', label='Neutron peak', 
             zorder=5, linewidth=3.0)
    plt.plot(bin_centers[noise_l:noise_r], hist[noise_l:noise_r], 'g-', 
             label='Background', zorder=5, linewidth=3.0)
    plt.legend()
    plt.xlabel('ToF [TDC channels]')
    plt.ylabel('Couns')
    plt.title('ToF histogram')
    
    plt.subplot(1, 3, 2)
    plt.plot(thres_vec, n_vec, 'b-',label='Neutrons', linewidth=3.0)
    plt.plot(thres_vec, g_vec, 'r-',label='Gammas', linewidth=3.0)
    plt.legend()
    plt.yscale('log')
    plt.xlabel('Threshold [ADC channels]')
    plt.ylabel('Events [Counts]')
    plt.title('Neutrons and Gammas vs ADC threshold')
    
    plt.subplot(1, 3, 3)
    cm = plt.cm.get_cmap('jet')
    sc = plt.scatter(n_vec, g_vec, c=thres_vec, vmin=thres_vec[0], 
                     vmax=thres_vec[-1], cmap=cm)
    plt.colorbar(sc)
    plt.xlabel('Neutron events [Counts]')
    plt.ylabel('Gamma events [Counts]')
    plt.title('Neutrons vs Gammas scatter map')
#    plt.xscale('log')
#    plt.yscale('log')
#    plt.xlim(1e5, 1e7)
#    plt.ylim(1e2, 1e4)

    plt.tight_layout()
    
    plot_path = get_plot_path(data_set) + name + '.pdf'
    
    return fig, plot_path

# =============================================================================
# 20. Rate Repetition Mode
# =============================================================================
    
def RRM(fig, name, df, data_set, border, E_i_vec):
    df = df[df.d != -1]
    df = df[(df.wADC > 500) & (df.gADC > 400)]
    df = df[(df.wM == 1) & (df.gM < 5)]
    dE_bins = 1000
        
    fig.set_figheight(8)
    fig.set_figwidth(12)
    ToF_bins = 1000
    
    fig.suptitle(name, x=0.5, y=1.07)
    
    df_vec = [df[df.ToF * 62.5e-9 * 1e6 <= border], 
              df[df.ToF * 62.5e-9 * 1e6  > border]]
    color_vec = ['red', 'blue']
    
    for i, E_i in enumerate(E_i_vec):
        plt.subplot(2,2,i+1)
        df_temp = df_vec[i]
        calibration = 'Van__3x3_RRM_Calibration_' + str(E_i)
        t_off = get_t_off(calibration) * np.ones(df_temp.shape[0])
        T_0 = get_T0(calibration, E_i) * np.ones(df_temp.shape[0])
        frame_shift = get_frame_shift(E_i) * np.ones(df_temp.shape[0])
        E_i = E_i * np.ones(df_temp.shape[0])
        ToF = df_temp.ToF.values
        d = df_temp.d.values
        dE, t_f = get_dE(E_i, ToF, d, T_0, t_off, frame_shift)
        df_temp_new = pd.DataFrame(data={'dE': dE, 't_f': t_f})
    
        plt.grid(True, which='major', zorder=0)
        plt.grid(True, which='minor', linestyle='--',zorder=0)
        plt.hist(df_temp_new[df_temp_new['t_f'] > 0].dE, 
                 bins=dE_bins, log=LogNorm(), range=[-E_i[0], E_i[0]],
                 histtype='step', color=color_vec[i], zorder=2, 
                 label=str(E_i[0]) + ' meV')
        plt.xlabel('$\Delta$E [meV]')
        plt.ylabel('Intensity [Counts]')
        plt.title('$E_i$ - $E_f$ histogram, ' + str(E_i[0]) + ' meV')
        plt.legend()
    
    plt.subplot2grid((2, 2), (1, 0), colspan=2)
    plt.grid(True, which='major', zorder=0)
    plt.grid(True, which='minor', linestyle='--',zorder=0)
    df_temp = df[df.ToF * 62.5e-9 * 1e6 <= border]
    plt.hist(df_temp.ToF * 62.5e-9 * 1e6, bins=ToF_bins, range=[0, 17e3],
             log=LogNorm(), histtype='step', color='red', zorder=2, 
             label=str(float(E_i_vec[0])) + ' meV')
    df_temp = df[df.ToF * 62.5e-9 * 1e6 > border]
    plt.hist(df_temp.ToF * 62.5e-9 * 1e6, bins=ToF_bins, range=[0, 17e3],
             log=LogNorm(), histtype='step', color='blue', zorder=2, 
             label=str(float(E_i_vec[1])) + ' meV')
    plt.xlabel('ToF [$\mu$s]')
    plt.ylabel('Intensity [Counts]')
    plt.title('ToF histogram')
    plt.legend()
    
    plt.tight_layout()
    
    plot_path = get_plot_path(data_set) + name + '.pdf'
    
    return fig, plot_path


# =============================================================================
# 21. Helium3 data
# =============================================================================
    
def plot_He3_data(fig, df, data_set, calibration, measurement_time,
                  p_left, p_right, E_i):    
    # Import He3 data
    measurement_id = find_He3_measurement_id(calibration)
    dirname = os.path.dirname(__file__)
    folder = '../Archive/2018_06_06_SEQ_He3/'
    nxs_file = 'SEQ_' + str(measurement_id) + '_autoreduced.nxs'
    nxspe_file = 'SEQ_' + str(measurement_id) + '_autoreduced.nxspe'
    nxs_path = os.path.join(dirname, folder + nxs_file)
    nxspe_path = os.path.join(dirname, folder + nxspe_file)
    nxs = h5py.File(nxs_path, 'r')
    nxspe = h5py.File(nxspe_path, 'r')
    # Extract values
    he3_bins = nxs['mantid_workspace_1']['event_workspace']['axis1'].value
    he3_min = he3_bins[0]
    he3_max = he3_bins[-1]
    He3_bin_centers = 0.5 * (he3_bins[1:] + he3_bins[:-1])
    dE = nxs['mantid_workspace_1']['event_workspace']['tof'].value
    He3_dE_hist, __ = np.histogram(dE, bins=390, range=[he3_min, he3_max])
    
    # Initial filter
    df = df[df.d != -1]
    df = df[(df.wADC > 500) & (df.gADC > 400)]
    df = df[(df.wM == 1) & (df.gM < 5)]
    # Calculate MG spectrum
    t_off = get_t_off(calibration) * np.ones(df.shape[0])
    T_0 = get_T0(calibration, E_i) * np.ones(df.shape[0])
    frame_shift = get_frame_shift(E_i) * np.ones(df.shape[0])
    E_i = E_i * np.ones(df.shape[0])
    ToF = df.ToF.values
    d = df.d.values
    dE, t_f = get_dE(E_i, ToF, d, T_0, t_off, frame_shift)
    df_temp = pd.DataFrame(data={'dE': dE, 't_f': t_f})
    dE = df_temp[df_temp['t_f'] > 0].dE
    # Get MG dE histogram
    dE_bins = 390
    dE_range = [he3_min, he3_max]
    MG_dE_hist, MG_bins = np.histogram(dE, bins=dE_bins, range=dE_range)
    MG_bin_centers = 0.5 * (MG_bins[1:] + MG_bins[:-1])
    
    
    # Get MG and He3 normalisation
    norm_MG = calculate_peak_norm(MG_bin_centers, MG_dE_hist, p_left, p_right)
    norm_He3 = calculate_peak_norm(He3_bin_centers, He3_dE_hist, p_left, p_right)
    
    # Plot MG and He3
   # MG_dE_hist = He3_dE_hist/norm_MG
    #He3_dE_hist = MG_dE_hist/norm_He3
    plt.plot(He3_bin_centers, He3_dE_hist)
    plt.plot(MG_bin_centers, MG_dE_hist)
    
    # Visualize peak edges
    plt.plot([MG_bin_centers[p_left], He3_bin_centers[p_left]], 
             [MG_dE_hist[p_left], He3_dE_hist[p_left]], 'b-x', 
             label='Peak edges', zorder=20)
    plt.plot([MG_bin_centers[p_right], He3_bin_centers[p_right]], 
             [MG_dE_hist[p_right], He3_dE_hist[p_right]], 'b-x', 
             label=None, zorder=20)
    

    
    # Plot text box
    text_string = r"$\bf{" + 'MultiGrid' + "}$" + '\n'
    text_string += 'Area: ' + str(int(norm_MG)) + ' [counts]\n'
    text_string += 'FWHM: ' + '\n'
    text_string += r"$\bf{" + 'He3' + "}$" + '\n'
    text_string += 'Area: ' + str(round(norm_He3,3)) + ' [counts]\n'
    text_string += 'FWHM: '
    
    
    plt.text(0.6*E_i[0], 0.04, text_string, ha='center', va='center', 
                 bbox={'facecolor':'white', 'alpha':0.8, 'pad':10}, fontsize=8)
        
    plt.yscale('log')
    plt.xlabel('$\Delta$E [meV]')
    plt.ylabel('Intensity [a.u.]')
    plt.title('Comparrison between He3 and MG')
    
    plt.show()
    
    
    
    
    path = get_plot_path(data_set) + nxs_file + '.pdf'
    
    return fig, path
    
    
    
    

# =============================================================================
# Helper Functions
# ============================================================================= 
    
def get_plot_path(data_set):
    dirname = os.path.dirname(__file__)
    folder = os.path.join(dirname, '../Plot/' + data_set + '/')
    return folder

def get_output_path(data_set):
    dirname = os.path.dirname(__file__)
    folder = os.path.join(dirname, '../Output/' + data_set + '/')
    return folder

def import_helium_tubes():
    pass

def filter_clusters(df):
    df = df[df.d != -1]
    df = df[df.tf > 0]
    df = df[(df.wADC > 500) & (df.gADC > 400)]
    df = df[(df.wM == 1) & (df.gM < 5)]
    return df

def calculate_peak_norm(bin_centers, hist, left_edge, right_edge):
    x_l = bin_centers[left_edge]
    y_l = hist[left_edge]
    x_r = bin_centers[right_edge-1]
    y_r = hist[right_edge-1]
    area = sum(hist[left_edge:right_edge])
    print('Area: ' + str(area))
    bins_under_peak = abs(right_edge - 1 - left_edge)
    print('Bins under peak: ' + str(bins_under_peak))
    area_noise = ((abs(y_r - y_l) * bins_under_peak) / 2
                  + bins_under_peak * min([y_l, y_r]))
    print('Area noise: ' + str(area_noise))
    peak_area = area - area_noise
    print('Peak area: ' + str(peak_area))
    return peak_area


def get_dE(E_i, ToF, d, T_0, t_off, frame_shift):
    # Declare parameters
    L_1 = 20.01                                # Source to sample
    m_n = 1.674927351e-27                      # Neutron mass
    meV_to_J = 1.60218e-19 * 0.001             # Convert meV to J
    J_to_meV = 6.24150913e18 * 1000            # Convert J to meV
    # Calculate dE
    E_i_J = E_i * meV_to_J                     # Convert E_i to J
    v_i = np.sqrt((E_i_J*2)/m_n)               # Get velocity of E_i
    t_1 = (L_1 / v_i) + T_0 * 1e-6             # Use velocity to find t_1
    ToF_real = ToF * 62.5e-9 + (t_off * 1e-6)  # Time from source to detector
    ToF_real += frame_shift
    t_f = ToF_real - t_1                        # Time from sample to detector
    E_J = (m_n/2) * ((d/t_f) ** 2)              # Energy E_f in Joule
    E_f = E_J * J_to_meV                        # Convert to meV
    return (E_i - E_f), t_f
    

def import_T0_table():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../Tables/' + 'T0_vs_Energy.xlsx')
    matrix = pd.read_excel(path).values
    t0_table = {}
    for row in matrix:
        t0_table.update({str(row[0]): row[1]})
    return t0_table


def get_T0(calibration, energy):
    T0_table = import_T0_table()
    return T0_table[calibration]


def get_t_off_table():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../Tables/' + 'time_offset.xlsx')
    matrix = pd.read_excel(path).values
    t_off_table = {}
    for row in matrix:
        t_off_table.update({row[0]: row[1]})
    return t_off_table


def get_t_off(calibration):
    t_off_table = get_t_off_table()
    return t_off_table[calibration]


def get_frame_shift(E_i):
    frame_shift = 0
    if E_i == 2:
        frame_shift += 2 * (16666.66666e-6) - 0.0004475
    if E_i == 8:
        frame_shift += (16666.66666e-6) - 0.0043893
    if E_i == 21:
        frame_shift += (16666.66666e-6) - 0.01227875
    if E_i == 20:
        frame_shift += 0
    if E_i == 25:
        frame_shift += (16666.66666e-6) - 0.013340625
    if E_i == 35:
        frame_shift += (16666.66666e-6) - 0.01514625
    return frame_shift


def find_He3_measurement_id(calibration):
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../Tables/experiment_log.xlsx')
    matrix = pd.read_excel(path).values
    measurement_table = {}
    for row in matrix:
        measurement_table.update({row[1]: row[0]})
    return measurement_table[calibration]

#
#def get_MG_and_He3_norm(p_left, p_right, MG_bin_centers, MG_dE_hist,
#                        He3_bin_centers, He3_dE_hist):
#    norm_MG = calculate_peak_norm(MG_bin_centers, MG_dE_hist, p_left, p_right)









    
    
    