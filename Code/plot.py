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
    plt.hist(df_red.ADC, bins=50, range=[0, 4400])  
    
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
        
    H, edges = np.histogramdd(df_3d.values, bins=(12*number_of_detectors, 40, 20), 
                              range=((0,12*number_of_detectors), (0,40), (0,20))
                              )
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
    
def plot_ToF_histogram(fig, name, df, data_set, duration, 
                       number_bins = 1000, rnge=[0, 16666],
                       ADC_filter = None, log = True):
    def find_nearest(array, value):
        idx = (np.abs(array - value)).argmin()
        return idx
    
    
#    rnge = [rnge[0] * 62.5e-9 * 1e6, rnge[1] * 62.5e-9 * 1e6]
    print('Range')
    print(rnge)
    
    # Remove this line, used to only capture coincident events
    df = df[(df.wCh != -1) & (df.gCh != -1)]
    df = df[(df.wADC > 500) & (df.gADC > 400)]
    df = df[(df.wM == 1) & (df.gM <= 5) & (df.gM >= 1)]
    
    if ADC_filter != None:
        minADC = ADC_filter[0]
        maxADC = ADC_filter[1]
        df = df[  (df.wADC >= minADC) & (df.wADC <= maxADC) 
                & (df.gADC >= minADC) & (df.gADC <= maxADC)]
        
    plt.grid(True, which='major', zorder=0)
    plt.grid(True, which='minor', linestyle='--',zorder=0) 
    
    hist, bins, patches = plt.hist(df.ToF * 62.5e-9 * 1e6, 
                                   bins=number_bins, range=rnge, 
                                   log=log, color='darkviolet', zorder = 3, 
                                   alpha=0.4)
    
    
    hist, bins, patches = plt.hist(df.ToF * 62.5e-9 * 1e6, bins=number_bins, 
                                   range=rnge, 
                                   log=log, color='black', zorder = 4, 
                                   histtype='step')
#    
#    bin_centers = 0.5 * (bins[1:] + bins[:-1])
#    maximum = max(hist[50:])
#    peak=np.where(hist == maximum)
#    print(peak)
#    peak = peak[len(peak)//2][0]
#    print(peak)
#    start = find_nearest(hist[:peak], hist[peak]/2)
#    stop = find_nearest(hist[peak:], hist[peak]/2)
#    print('Bincenters')
#    print(bin_centers[start])
#    print(bin_centers[peak+stop])
##        
##    
#    plt.plot([bin_centers[start], bin_centers[peak+stop]], 
#             [hist[start], hist[peak+stop]], 'rx', zorder=7)
##    
#    
#    
#    tot_events = df.shape[0]
#    print('tot_events: ' + str(tot_events))
#    events_per_s = tot_events/duration
#    print('events_per_s' + str(events_per_s))
#    
#    print('signal_events: ' + str(sum(hist[start:peak+stop])))
#    s_time = (bin_centers[peak+stop] - bin_centers[start]) * 1e-6 
#    period_time = 0.016666666666666666
#    print('S_time: ' + str(s_time))
#    s_events_per_s = sum(hist[start:peak+stop])/(duration*(s_time/period_time))
##    
#    
#    
#    text_string = 'Average rate: ' + str(round(events_per_s,1)) + ' [Hz]'
#    text_string += '\nPeak Rate: ' + str(round(s_events_per_s, 1)) + ' [Hz]'
#    
#    plt.text(14e3, maximum/10, text_string, ha='center', va='center', 
#             bbox={'facecolor':'white', 'alpha':0.8, 'pad':10}, fontsize=8, 
#             zorder=5)
#    
    
#    
    plt.title(name)
    plt.xlabel('ToF [$\mu$s]')
    plt.ylabel('Counts')
    plot_path = (get_plot_path(data_set) + name + ' Range: ' + str(rnge) +
                 'Number of bins: ' + str(number_bins) + '.pdf')
#    

#    bin_centers = 0.5 * (bins[1:] + bins[:-1])
#    maximum = max(hist)
#    peak=np.where(hist == maximum)
#    peak = peak[len(peak)//2][len(peak)//2]
#    print('Prompt peak  [TDC channels]: ' + str(bin_centers[peak]))
#    print('Prompt peak  [s]: '  + str(bin_centers[peak] * 62.5e-9))
    
             
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
# 12. Delta E histogram 
# =============================================================================
    
def dE_histogram(fig, name, df, data_set, E_i, calibration, measurement_time,
                 back_yes):
    T_0 = get_T0(calibration, E_i)
    t_off = get_t_off(calibration)
    

    df = df[df.d != -1]
    df = df[(df.wM == 1) & (df.gM <= 5) & (df.gM >= 1)]
    df = df[(df.wADC > 500) & (df.gADC > 400)]
    
    name = 'Histogram of $E_i$ - $E_f$'
    name += ('\nData_set: ' + str(data_set))
    dE_bins = 390
    dE_range = [-E_i, E_i]
    plt.grid(True, which='major', zorder=0)
    plt.grid(True, which='minor', linestyle='--',zorder=0)
    t_off = get_t_off(calibration) * np.ones(df.shape[0])
    T_0 = get_T0(calibration, E_i) * np.ones(df.shape[0])
    frame_shift = get_frame_shift(E_i) * np.ones(df.shape[0])
    E_i = E_i * np.ones(df.shape[0])
    ToF = df.ToF.values
    d = df.d.values
    dE, t_f = get_dE(E_i, ToF, d, T_0, t_off, frame_shift)
    df_temp_new = pd.DataFrame(data={'dE': dE, 't_f': t_f})
    df_temp_new = df_temp_new[df_temp_new['t_f'] > 0]
    hist_MG, bins = np.histogram(df_temp_new.dE, bins=dE_bins, range=dE_range)
    bin_centers = 0.5 * (bins[1:] + bins[:-1])
    
    plt.xlabel('$\Delta$E [meV]')
    plt.xlim([-E_i[0], E_i[0]])
    plt.ylim([1, 1.2 * max(hist_MG)])
    plt.ylabel('Counts')
    plt.yscale('log')
    
    lim_ToF_vec = None
    isPureAluminium = False
    
    hist_background = plot_dE_background(E_i[0], calibration, measurement_time, 
                                         1, -E_i[0], E_i[0], back_yes, 1,
                                         isPureAluminium, lim_ToF_vec)
    
    if back_yes is False:
        hist_MG = hist_MG - hist_background
        name += '\n(Background subtracted)'
    
    plt.plot(bin_centers, hist_MG, color='black', label='Data', zorder=5)
    plt.title(name)
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
    df = df[(df.wM == 1) & (df.gM <= 5)]

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
    df = df[(df.wM == 1) & (df.gM <= 5)]
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
    
def RRM(fig, name, df, data_set, border, E_i_vec, measurement_time,
        back_yes = False, isPureAluminium = False):
    df = df[df.d != -1]
    df = df[(df.wADC > 500) & (df.gADC > 400)]
    df = df[(df.wM == 1) & (df.gM <= 5)]
    if isPureAluminium:
        df = df[(df.Bus <= 8) & (df.Bus >= 6)]
        df = df[  (df.gCh != 119) & (df.gCh != 80) 
                & (df.gCh != 99) & (df.gCh != 101)]
        
    
    dE_bins = 390
        
    fig.set_figheight(8)
    fig.set_figwidth(12)
    ToF_bins = 1000
    
    fig.suptitle(name, x=0.5, y=1.07)
    
    df_vec = [df[df.ToF * 62.5e-9 * 1e6 <= border], 
              df[df.ToF * 62.5e-9 * 1e6  > border]]
    color_vec = ['red', 'blue']
    lim_ToF_vec = [[0, border], [border, np.inf]]
    
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
        df_temp_new = df_temp_new[df_temp_new['t_f'] > 0]
    
        plt.grid(True, which='major', zorder=0)
        plt.grid(True, which='minor', linestyle='--',zorder=0)
        
        MG_norm = 1
        tot_norm = 1
 
        MG_back_dE_hist = plot_dE_background(E_i[0], calibration, measurement_time, 
                                             MG_norm, -E_i[0], E_i[0], back_yes, tot_norm,
                                             isPureAluminium, lim_ToF_vec[i])
        
        
        
        MG_dE_hist, bins = np.histogram(df_temp_new.dE, bins=dE_bins, 
                                      range=[-E_i[0], E_i[0]])
        bin_centers = 0.5 * (bins[1:] + bins[:-1])
        
        
        if back_yes is False:
            MG_dE_hist = MG_dE_hist - MG_back_dE_hist
        
        plt.plot(bin_centers, MG_dE_hist, '-', color=color_vec[i], 
                 label = str(E_i[0]) + ' meV')
                
        
        
        plt.xlabel('$\Delta$E [meV]')
        plt.yscale('log')
        plt.ylabel('Intensity [Counts]')
        title = 'Energy transfer, $E_i$ - $E_f$'
        if isPureAluminium:
            title += '\nPure Aluminium'
        if back_yes is False:
            title += '\n(Background subtracted)'
            
        plt.title(title)
        plt.legend(loc='upper left')
    
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
    
def plot_He3_data(fig, df, data_set, calibration, measurement_time, E_i, FWHM,
                  vis_help, back_yes, isRaw = False, isPureAluminium = False, 
                  isFiveByFive = False):
    MG_SNR = 0
    He3_SNR = 0
    def find_nearest(array, value):
        idx = (np.abs(array - value)).argmin()
        return idx
    
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
    He3_dE_hist = None
    if isRaw:
        path = os.path.join(dirname,'../Archive/SEQ_raw/SEQ_' 
                            + str(measurement_id) + '.nxs.h5')
        He3_file = h5py.File(path, 'r')
        ToF_tot = []
        pixels_tot = []
        for bank_value in range(40, 151):
            bank = 'bank' + str(bank_value) + '_events'
            ToF = He3_file['entry'][bank]['event_time_offset'].value
            pixels = He3_file['entry'][bank]['event_id'].value
            if ToF != []:
                ToF_tot.extend(ToF)
                pixels_tot.extend(pixels)
        distance = np.zeros([len(pixels_tot)], dtype=float)
        __, __, __, d = import_He3_coordinates_NEW()
        for i, pixel in enumerate(pixels_tot):
            distance[i] = d[pixel-39936]
        T_0 = get_T0(calibration, E_i) * np.ones(len(ToF_tot))
        t_off = get_t_off_He3(calibration) * np.ones(len(ToF_tot))
        E_i_vec_raw = E_i * np.ones(len(ToF_tot))
        dE, t_f = get_dE_He3(E_i_vec_raw, np.array(ToF_tot), distance, T_0, t_off)
        df_temp_He3 = pd.DataFrame(data={'dE': dE, 't_f': t_f})
        dE = df_temp_He3[df_temp_He3['t_f'] > 0].dE
        He3_dE_hist, __ = np.histogram(dE, bins=390, range=[he3_min, he3_max])
    else:
        dE = nxs['mantid_workspace_1']['event_workspace']['tof'].value
        He3_dE_hist, __ = np.histogram(dE, bins=390, range=[he3_min, he3_max])
    
    He_duration = nxs['mantid_workspace_1']['logs']['duration']['value'].value[0]
    
    # Initial filter
    df = df[df.d != -1]
    df = df[(df.wADC > 500) & (df.gADC > 400)]
    df = df[(df.wM == 1) & (df.gM <= 5)]
    if isPureAluminium:
        df = df[(df.Bus <= 8) & (df.Bus >= 6)]
        df = df[  (df.gCh != 119) & (df.gCh != 80) 
                & (df.gCh != 99) & (df.gCh != 101)]
    
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

    
    # Get He3 offset
    He3_offset = 0
    if isRaw is False:
        He3_offset = get_He3_offset(calibration)
    
    # Get MG and He3 peak edges
    MG_left, MG_right, He3_left, He3_right = get_peak_edges(calibration)
    if isRaw:
        He3_left = MG_left
        He3_right = MG_right
    
    # Get MG and He3 normalisation
    norm_MG = calculate_peak_norm(MG_bin_centers, MG_dE_hist, MG_left, 
                                  MG_right)
    norm_He3 = calculate_peak_norm(He3_bin_centers, He3_dE_hist, He3_left,
                                   He3_right)
    
    # Declare solid angle for Helium-3 and Multi-Grid
    He3_solid_angle = 0.7449028590952331
    MG_solid_angle = 0
    MG_solid_angle_tot = 0.01660177142644554
    MG_missing_solid_angle_1 = 0.0013837948633069277
    MG_missing_solid_angle_2 = 0.0018453301781999457
    print(calibration[0:30])
    if calibration[0:30] == 'Van__3x3_High_Flux_Calibration':
        print('High Flux')
        print(calibration)
        if E_i[0] < 450:
            MG_solid_angle = (MG_solid_angle_tot - MG_missing_solid_angle_1
                              - MG_missing_solid_angle_2)
        else:
            MG_solid_angle = (MG_solid_angle_tot - MG_missing_solid_angle_1)
    else:
        print('High Resolution')
        print(calibration)
        if E_i[0] > 50:
            MG_solid_angle = (MG_solid_angle_tot - MG_missing_solid_angle_1
                              - MG_missing_solid_angle_2)
        else:
            MG_solid_angle = (MG_solid_angle_tot - MG_missing_solid_angle_1)
            
    if isPureAluminium:
        MG_solid_angle = 0.005518217498193907 - 0.00046026495055297194
    
    # Get charge normalization
    charge_norm = get_charge_norm(calibration)
    
    # Calculate total normalization
    tot_norm = ((MG_solid_angle/He3_solid_angle)*charge_norm)
    if isFiveByFive:
        tot_norm = sum(MG_dE_hist)/sum(He3_dE_hist)
    
    # Plot background level
    hist_back = plot_dE_background(E_i[0], calibration, measurement_time, 
                                   norm_MG, he3_min, he3_max, back_yes, 
                                   tot_norm, isPureAluminium)

    # Plot MG and He3
    if vis_help is not True:
        MG_dE_hist = MG_dE_hist/tot_norm
        He3_dE_hist = He3_dE_hist
    plt.plot(He3_bin_centers+He3_offset, He3_dE_hist, label='He3', color='blue')
    if back_yes is not True:
        MG_dE_hist = MG_dE_hist - hist_back
    plt.plot(MG_bin_centers, MG_dE_hist, label='Multi-Grid'
             ,color='red') 
    
    # Calculate FWHM
    MG_FWHM = ''
    He3_FWHM = ''
    if FWHM:
        MG_FWHM, MG_SNR, MG_MAX = get_FWHM(MG_bin_centers, MG_dE_hist, MG_left, MG_right, 
                                           vis_help, b_label='Background')
        MG_FWHM = str(round(MG_FWHM, 4))
        He3_FWHM, He3_SNR, He3_MAX = get_FWHM(He3_bin_centers+He3_offset, He3_dE_hist, He3_left, 
                                              He3_right, vis_help, b_label=None)
        He3_FWHM = str(round(He3_FWHM, 4))
    
    
    MG_peak_normalised = norm_MG/tot_norm
    He3_peak_normalised = norm_He3
    MG_over_He3 = round(MG_peak_normalised/He3_peak_normalised, 4)
    MG_over_He3_max = 0
    if FWHM:  
        MG_over_He3_max = round((MG_MAX/He3_MAX), 4)
    # Plot text box
    text_string = r"$\bf{" + '---MultiGrid---' + "}$" + '\n'
    text_string += 'Area: ' + str(round(MG_peak_normalised,1)) + ' [counts]\n'
    text_string += 'FWHM: ' + MG_FWHM + ' [meV]\n'
    #text_string += 'SNR: ' + str(round(MG_SNR, 3)) + '\n'
    text_string += 'Duration: ' + str(round(measurement_time,1)) + ' [s]\n'
    text_string += r"$\bf{" + '---He3---' + "}$" + '\n'
    text_string += 'Area: ' + str(round(He3_peak_normalised,1)) + ' [counts]\n'
    text_string += 'FWHM: ' + He3_FWHM + ' [meV]\n'
   # text_string += 'SNR: ' + str(round(He3_SNR, 3)) + '\n'
    text_string += 'Duration: ' + str(round(He_duration,1)) + '  [s]\n'
    text_string += r"$\bf{" + '---Comparison---' + "}$" + '\n'
    text_string += 'Area fraction: ' + str(MG_over_He3)
    
    He3_hist_max = max(He3_dE_hist)
    MG_hist_max = max(MG_dE_hist)
    tot_max = max([He3_hist_max, MG_hist_max])
    plt.text(-0.7*E_i[0], tot_max * 0.07, text_string, ha='center', va='center', 
                 bbox={'facecolor':'white', 'alpha':0.9, 'pad':10}, fontsize=6,
                 zorder=50)
    
    # Visualize peak edges
    plt.plot([He3_bin_centers[He3_left]+He3_offset, 
              He3_bin_centers[He3_right]+He3_offset], 
             [He3_dE_hist[He3_left], He3_dE_hist[He3_right]], 'bx', 
             label='Peak edges', zorder=20)
    plt.plot([MG_bin_centers[MG_left], MG_bin_centers[MG_right]], 
             [MG_dE_hist[MG_left], MG_dE_hist[MG_right]], 'bx', 
             label=None, zorder=20)  
                
    plt.legend(loc='upper right')
    plt.yscale('log')
    plt.xlabel('$\Delta$E [meV]')
    plt.xlim(he3_min, he3_max)
    plt.ylabel('Intensity [a.u.]')
    title = calibration + '_meV' 
    if back_yes is not True:
        title += '\n(Background subtracted)'
    if isPureAluminium:
        title += '\nPure Aluminium'
    if isFiveByFive:
        title += '\n(Van__5x5 sample for Multi-Grid)'
    plt.title(title)
    plt.grid(True, which='major', zorder=0)
    plt.grid(True, which='minor', linestyle='--',zorder=0)    
    
    if back_yes:
        path = get_plot_path(data_set) + calibration + '_meV' + '.pdf'
    else:
        path = get_plot_path(data_set) + calibration + '_meV_background_subtracted' + '.pdf'
    
    return fig, path, MG_over_He3, MG_over_He3_max, He3_FWHM, MG_FWHM

# =============================================================================
# 22. ToF per voxel
# =============================================================================
    
def ToF_per_voxel(df, data_set, Bus):
    df = df[df.d != -1]
    df = df[(df.wADC > 500) & (df.gADC > 400)]
    df = df[(df.wM == 1) & (df.gM <= 5)]
    df = df[df.Time < 1.5e12]
    df = df[df.Bus == Bus]
    folder = get_plot_path(data_set)
    grids = range(80,120)
    for i, grid in enumerate(grids):
        fig = plt.figure()
        df_temp = df[df.gCh == grid]
        plt.title('ToF histogram for Grid Channel ' + str(grid) + ', Bus ' + str(Bus))
        plt.hist2d(df_temp.wCh - 0.5, df_temp.ToF * 62.5e-9 * 1e6,
                   bins=[80, 40], norm=LogNorm(), 
                   range=[[-0.5, 79.5], [0, 1.666e4]], vmin=1, vmax=20, 
                   cmap='jet')
        plt.xlabel('Wire [Channel number]')
        plt.ylabel('ToF [$\mu$s]')
        plt.colorbar()
        path = folder + 'Bus_' + str(Bus) + '_Grid_' + str(grid) + '.pdf'
        fig.savefig(path, bbox_inches='tight')
        percentage_finished = str(int(round((i/len(grids))*100, 1))) + '%'
        plt.close()
        print(percentage_finished)
        
# =============================================================================
# 23. Iterate through all energies and export energies
# =============================================================================     

def plot_all_energies(isPureAluminium = False, isRaw = False):
    # Declare all the relevant file names
    Van_3x3_HF_clusters = ["['mvmelst_1577_15meV_HF.zip'].h5",
                           "['mvmelst_1578_20meV_HF.zip'].h5",
                           "['mvmelst_1579_25meV_HF.zip', '...'].h5",
                           "['mvmelst_1581_31p7meV_HF.zip'].h5",
                           "['mvmelst_1582_34meV_HF.zip', '...'].h5",
                           "['mvmelst_1586_40p8meV_HF.zip'].h5",
                           "['mvmelst_1587_48meV_HF.zip', '...'].h5",
                           "['mvmelst_1591_60meV_HF.zip', '...'].h5",
                           "['mvmelst_1595_70meV_HF.zip', '...'].h5",
                           "['mvmelst_1597_80meV_HF.zip'].h5",
                           "['mvmelst_1598_90meV_HF.zip', '...'].h5",
                           "['mvmelst_1600_100meV_HF.zip', '...'].h5",
                           "['mvmelst_1602_120meV_HF.zip'].h5",
                           "['mvmelst_1603_140meV_HF.zip', '...'].h5",
                           "['mvmelst_1605_160meV_HF.zip'].h5",
                           "['mvmelst_1606_180meV_HF.zip'].h5",
                           "['mvmelst_1607_200meV_HF.zip'].h5",
                           "['mvmelst_1608_225meV_HF.zip'].h5",
                           "['mvmelst_1609_250meV_HF.zip'].h5",
                           "['mvmelst_1610_275meV_HF.zip'].h5",
                           "['mvmelst_1611_300meV_HF.zip', '...'].h5",
                           "['mvmelst_1613_350meV_HF.zip'].h5",
                           "['mvmelst_1614_400meV_HF.zip', '...'].h5",
                           "['mvmelst_153.mvmelst', '...'].h5",
                           "['mvmelst_156.mvmelst'].h5",
                           "['mvmelst_157.mvmelst'].h5",
                           "['mvmelst_158.mvmelst'].h5",
                           "['mvmelst_160.mvmelst'].h5",
                           "['mvmelst_161.mvmelst'].h5",
                           "['mvmelst_162.mvmelst'].h5",
                           "['mvmelst_163.mvmelst'].h5",
                           "['mvmelst_164.mvmelst'].h5",
                           "['mvmelst_165.mvmelst'].h5",
                           "['mvmelst_166.mvmelst'].h5",
                           "['mvmelst_167.mvmelst'].h5",
                           "['mvmelst_168.mvmelst'].h5",
                           "['mvmelst_169.mvmelst'].h5"]
    
    Van_3x3_HR_clusters = ["['mvmelst_125.mvmelst', '...'].h5",
                           "['mvmelst_127.mvmelst'].h5",
                           "['mvmelst_129.mvmelst'].h5",
                           "['mvmelst_130.mvmelst'].h5",
                           "['mvmelst_131.mvmelst'].h5",
                           "['mvmelst_132.mvmelst', '...'].h5",
                           "['mvmelst_134.mvmelst', '...'].h5",
                           "['mvmelst_137.mvmelst'].h5",
                           "['mvmelst_138.mvmelst'].h5",
                           "['mvmelst_139.mvmelst'].h5",
                           "['mvmelst_140.mvmelst'].h5",
                           "['mvmelst_141.mvmelst'].h5",
                           "['mvmelst_142.mvmelst', '...'].h5",
                           "['mvmelst_145.mvmelst', '...'].h5",
                           "['mvmelst_147.mvmelst'].h5",
                           "['mvmelst_148.mvmelst'].h5",
                           "['mvmelst_149.mvmelst'].h5",
                           "['mvmelst_150.mvmelst'].h5",
                           "['mvmelst_151.mvmelst'].h5",
                           "['mvmelst_1556_60meV_HR.zip'].h5",
                           "['mvmelst_1557_70meV_HR.zip', '...'].h5",
                           "['mvmelst_1561_80meV_HR.zip'].h5",
                           "['mvmelst_1562_90meV_HR.zip'].h5",
                           "['mvmelst_1563_100meV_HR.zip'].h5",
                           "['mvmelst_1564_120meV_HR.zip', '...'].h5",
                           "['mvmelst_1566_140meV_HR.zip'].h5",
                           "['mvmelst_1567_160meV_HR.zip', '...'].h5",
                           "['mvmelst_1569_180meV_HR.zip'].h5",
                           "['mvmelst_1570_200meV_HR.zip', '...'].h5",
                           "['mvmelst_1572_225meV_HR.zip'].h5",
                           "['mvmelst_1573_250meV_HR.zip', '...'].h5",
                           "['mvmelst_1575_275meV_HR.zip'].h5",
                           "['mvmelst_1576_300meV_HR.zip'].h5"]
    
    # Declare parameters
    FWHM = True
    vis_help = False
    back_yes_vec = [True, False]
    # Declare input-folder
    dir_name = os.path.dirname(__file__)
    clusters_folder = os.path.join(dir_name, '../Clusters/')
    data_set_names = ['V_3x3_HF', 'V_3x3_HR']
    m_data_sets = [Van_3x3_HF_clusters, Van_3x3_HR_clusters]
    print('Choose data sets:')
    for i, data_set_name in enumerate(data_set_names):
        print('  ' + str(i+1) + '. ' + str(data_set_name))
    choices = [int(x) for x in 
               input('Enter data sets, use space(s) to separate: ').split()]
    
    print('Loading...')
    for choice in choices:
        m_type = data_set_names[choice - 1]
        clusters = m_data_sets[choice - 1]

        print('---'+m_type+'---')
        
        # Declare 2D hist folder
        hist_2D_folder = os.path.join(dir_name, '../../Histograms_2D/')
        
        # Declare output-folder
        with_background_result_folder = os.path.join(dir_name, 
                                                     '../../' + m_type + '/With_Background/')
        without_background_result_folder = os.path.join(dir_name, 
                                                    '../../' + m_type + '/Without_Background/')
        folder_vec = [with_background_result_folder, 
                      without_background_result_folder]
        # Declare overview folder
        overview_folder = os.path.join(dir_name,'../../' + m_type + '_overview/')
        E_i_vec = []
        max_frac_vec = []
        area_frac_vec = []
        He3_FWHM_vec = []
        MG_FWHM_vec = []
        for i, cluster_name in enumerate(clusters):
            # Import clusters
            clusters_path = clusters_folder + cluster_name
            df = pd.read_hdf(clusters_path, 'coincident_events')
            E_i = pd.read_hdf(clusters_path, 'E_i')['E_i'].iloc[0]
            measurement_time = pd.read_hdf(clusters_path, 'measurement_time')['measurement_time'].iloc[0]
            calibration = pd.read_hdf(clusters_path, 'calibration')['calibration'].iloc[0]
            data_sets = pd.read_hdf(clusters_path, 'data_set')['data_set'].iloc[0]
            # Plot clusters
            for back_yes, folder in zip(back_yes_vec, folder_vec):
                fig = plt.figure()
                fig, __, a_frac, max_frac, He3_FWHM, MG_FWHM = plot_He3_data(fig, df, data_sets, calibration, 
                                                                             measurement_time, E_i, FWHM, 
                                                                             vis_help, 
                                                                             back_yes, isRaw, 
                                                                             isPureAluminium)
                path = folder + calibration
                if back_yes is not True:
                    path += '_Background_subtracted'
                    E_i_vec.append(E_i)
                    max_frac_vec.append(max_frac)
                    area_frac_vec.append(a_frac)
                    He3_FWHM_vec.append(float(He3_FWHM))
                    MG_FWHM_vec.append(float(MG_FWHM))
                path += '.pdf'
                fig.savefig(path, bbox_inches='tight')
                plt.close()
            
#            number_of_detectors = 3
#            bus_vec = [0, 1, 2, 3, 4, 5, 6, 7, 8]
#            m_range = None
#            count_range = [1, 5000]
#            ADC_filter = None
#            m_range = None
#            ts_range = [0,np.inf]
#            fig = plt.figure()
#            fig, __ =plot_2D_hit_buses(fig, calibration, df, bus_vec, number_of_detectors, 
#                                       data_sets, count_range, ADC_filter, m_range, 
#                                       ts_range)
#            path = hist_2D_folder + calibration + '.pdf'
#            fig.savefig(path, bbox_inches='tight')
#            plt.close()

            
        
            percentage_finished = str(int(round((i/len(clusters))*100, 1))) + '%'
            print(percentage_finished)

        np.savetxt(overview_folder + 'E_i_vec.txt', E_i_vec, delimiter=",")
        np.savetxt(overview_folder + 'max_frac_vec.txt', max_frac_vec, delimiter=",")
        np.savetxt(overview_folder + 'area_frac_vec.txt', area_frac_vec, delimiter=",")
        np.savetxt(overview_folder + 'He3_FWHM_vec.txt', He3_FWHM_vec, delimiter=",")
        np.savetxt(overview_folder + 'MG_FWHM_vec.txt', MG_FWHM_vec, delimiter=",")
                        

# =============================================================================
# 24. Plot overview of energies
# =============================================================================
    
def plot_overview(fig):
    dir_name = os.path.dirname(__file__)
    data_set_names = ['V_3x3_HR', 'V_3x3_HF']
   # fig.suptitle('Overview', x=0.5, y=1.02)
#    fig.set_figheight(4)
#    fig.set_figwidth(10)
    color_vec = ['blue', 'red']
    for i, data_set_name in enumerate(data_set_names):
        overview_folder = os.path.join(dir_name,'../../' + data_set_name + '_overview/')
        E_i = np.loadtxt(overview_folder + 'E_i_vec.txt', delimiter=",")
        max_frac = np.loadtxt(overview_folder + 'max_frac_vec.txt', delimiter=",")
        area_frac = np.loadtxt(overview_folder + 'area_frac_vec.txt', delimiter=",")
        He3_FWHM = np.loadtxt(overview_folder + 'He3_FWHM_vec.txt', delimiter=",")
        MG_FWHM = np.loadtxt(overview_folder + 'MG_FWHM_vec.txt', delimiter=",")
      #  plt.subplot(1, 2, 1)
#        plt.grid(True, which='major', zorder=0)
#        plt.grid(True, which='minor', linestyle='--',zorder=0) 
#        plt.title('Relative efficiency vs Energy\n(Peak area comparrison, MG/He3)\n(Raw He3 data used)')
#       # plt.plot(E_i, max_frac, '-x', label='Peak maximum fraction (MG/He3)', zorder=5)
#        plt.plot(E_i, area_frac, '-x', color=color_vec[i], label=data_set_name,
#                 zorder=5)
#        plt.xlabel('$E_i$ [meV]')
#        plt.xscale('log')
#        plt.ylabel('Relative efficiency')
        plt.legend()
       # plt.subplot(1, 2, 2)
        plt.grid(True, which='major', zorder=0)
        plt.grid(True, which='minor', linestyle='--',zorder=0) 
        plt.title('FWHM vs Energy\n(Raw He3 data used)')
        plt.plot(E_i, MG_FWHM, '-x', label=data_set_name + ', MG', zorder=5)
        plt.plot(E_i, He3_FWHM, '-x', label=data_set_name + ', He3', zorder=5)
        plt.xlabel('$E_i$ [meV]')
        plt.xscale('log')
        plt.yscale('log')
        plt.ylabel('FWHM [meV]')
        plt.legend()
    
    plt.tight_layout()
    
    
    
    
    # Save file
    dir_name = os.path.dirname(__file__)
    path = os.path.join(dir_name,'../../V_3x3_Overview/V_3x3_Overview.pdf')
    
    return fig, path    


# =============================================================================
# 25. Plot raw He3 data
# =============================================================================
    
def plot_Raw_He3(fig, E_i, calibration):
    # Declare parameters
    m_id = str(find_He3_measurement_id(calibration))
    # Import raw He3 data
    dir_name = os.path.dirname(__file__)
    path = os.path.join(dir_name,'../Archive/SEQ_raw/SEQ_' + m_id + '.nxs.h5')
    He3_file = h5py.File(path, 'r')
    ToF_tot = []
    pixels_tot = []
    for bank_value in range(40, 151):
        bank = 'bank' + str(bank_value) + '_events'
        ToF = He3_file['entry'][bank]['event_time_offset'].value
        pixels = He3_file['entry'][bank]['event_id'].value
        if ToF != []:
            ToF_tot.extend(ToF)
            pixels_tot.extend(pixels)
    pixels_tot = np.array(pixels_tot)
    distance = np.zeros([len(pixels_tot)], dtype=float)
    __, __, __, d = import_He3_coordinates_NEW()
    for i, pixel in enumerate(pixels_tot):
        distance[i] = d[pixel-39936]
    
    T_0 = get_T0(calibration, E_i) * np.ones(len(ToF_tot))
    t_off = get_t_off_He3(calibration) * np.ones(len(ToF_tot))
    E_i = E_i * np.ones(len(ToF_tot))
    dE, t_f = get_dE_He3(E_i, np.array(ToF_tot), distance, T_0, t_off)
    df_temp = pd.DataFrame(data={'dE': dE, 't_f': t_f})
    dE = df_temp[df_temp['t_f'] > 0].dE
    plt.hist(dE, bins=390, range=[-E_i[0], E_i[0]], histtype='step', 
             color='black', zorder=5)
    plt.xlabel('$\Delta$E')
    plt.ylabel('Counts')
    plt.yscale('log')
    plt.title('Raw Helium data\n' + calibration)
    plt.grid(True, which='major', zorder=0)
    plt.grid(True, which='minor', linestyle='--',zorder=0) 
    
    path = os.path.join(dir_name,'../RAW_HELIUM_TEST.pdf')   
    
    return fig, path

# =============================================================================
# 26. Plot 3D plotly histogram
# ============================================================================= 
    
def plot_plotly_3D_histogram(df_tot, df, path, data_set, min_tof=0, max_tof=9100):
    # Declare max and min count
    min_count = 2
    max_count = np.inf
    # Calculate vertical line position
    v_pos_x = (min_tof + max_tof)/2
    # Perform initial filters
    df = df[df.d != -1]
    df = df[(df.wADC > 500) & (df.gADC > 400)]
    df = df[(df.wM == 1) & (df.gM <= 5)]
    # Declare offsets
    offset_1 = {'x': -0.907574, 'y': -3.162949,  'z': 5.384863}
    offset_2 = {'x': -1.246560, 'y': -3.161484,  'z': 5.317432}
    offset_3 = {'x': -1.579114, 'y': -3.164503,  'z': 5.227986}
    # Calculate angles
    corners = {'ESS_2': {1: [-1.579114, -3.164503, 5.227986],
                         2: [-1.252877, -3.162614, 5.314108]},
               'ESS_1': {3: [-1.246560, -3.161484, 5.317432],
                         4: [-0.916552, -3.160360, 5.384307]},
               'ILL':   {5: [-0.907574, -3.162949, 5.384863],
                         6: [-0.575025, -3.162578, 5.430037]}
                }
    ILL_C = corners['ILL']
    ESS_1_C = corners['ESS_1']
    ESS_2_C = corners['ESS_2']
    theta_1 = np.arctan((ILL_C[6][2]-ILL_C[5][2])/(ILL_C[6][0]-ILL_C[5][0]))
    theta_2 = np.arctan((ESS_1_C[4][2]-ESS_1_C[3][2])/(ESS_1_C[4][0]-ESS_1_C[3][0]))
    theta_3 = np.arctan((ESS_2_C[2][2]-ESS_2_C[1][2])/(ESS_2_C[2][0]-ESS_2_C[1][0]))
    # Initiate detector mappings
    detector_1 = create_ill_channel_to_coordinate_map(theta_1, offset_1)
    detector_2 = create_ess_channel_to_coordinate_map(theta_2, offset_2)
    detector_3 = create_ess_channel_to_coordinate_map(theta_3, offset_3)
    detector_vec = [detector_1, detector_2, detector_3]
    # Initiate border lines   
    pairs = [[[80, 0], [80, 60]],
             [[80, 0], [80, 19]],
             [[80, 79], [80, 60]],
             [[80, 79], [80, 19]],
             [[119, 0], [119, 60]],
             [[119, 0], [119, 19]],
             [[119, 79], [119, 60]],
             [[119, 79], [119, 19]],
             [[80, 0], [119, 0]],
             [[80, 19], [119, 19]],
             [[80, 60], [119, 60]],
             [[80, 79], [119, 79]]
            ]
    
    b_traces = []
    for bus in range(3, 9):
        detector = detector_vec[bus//3]
        for pair in pairs:
            x_vec = []
            y_vec = []
            z_vec = []
            for loc in pair:
                gCh = loc[0]
                wCh = loc[1]
                coord = detector[bus%3, gCh, wCh]
                x_vec.append(coord['x'])
                y_vec.append(coord['y'])
                z_vec.append(coord['z'])
                
      
            b_trace = go.Scatter3d(x=z_vec,
                                   y=x_vec,
                                   z=y_vec,
                                   mode='lines',
                                   line = dict(
                                                color='rgba(0, 0, 0, 0.5)',
                                                width=5)
                                    )
            b_traces.append(b_trace)
       
    detector = detector_vec[0]
    pairs_2 = [[[80, 0, 0], [80, 60, 2]],
               [[80, 0, 0], [80, 19, 0]],
               [[80, 79, 2], [80, 60, 2]],
               [[80, 79, 2], [80, 19, 0]],
               [[119, 0, 0], [119, 60, 2]],
               [[119, 0, 0], [119, 19, 0]],
               [[119, 79, 2], [119, 60, 2]],
               [[119, 79, 2], [119, 19, 0]],
               [[80, 0, 0], [119, 0, 0]],
               [[80, 19, 0], [119, 19, 0]],
               [[80, 60, 2], [119, 60, 2]],
               [[80, 79, 2], [119, 79, 2]]
               ]
    for pair in pairs_2:
        x_vec = []
        y_vec = []
        z_vec = []
        for loc in pair:
            gCh = loc[0]
            wCh = loc[1]
            bus = loc[2]
            coord = detector[bus%3, gCh, wCh]
            x_vec.append(coord['x'])
            y_vec.append(coord['y'])
            z_vec.append(coord['z'])
                
      
        b_trace = go.Scatter3d(x=z_vec,
                               y=x_vec,
                               z=y_vec,
                               mode='lines',
                               line = dict(
                                       color='rgba(0, 0, 0, 0.5)',
                                       width=5)
                                           )
        b_traces.append(b_trace)
        
    # Calculate 3D histogram
    H, edges = np.histogramdd(df[['wCh','gCh', 'Bus']].values, 
                              bins=(80, 40, 9), 
                              range=((0, 80), (80, 120), (0,9))
                             )
    # Insert results into an array
    flip_bus = {0: 2, 1: 1, 2: 0}
    def flip_wire(wCh):
        if 0 <= wCh <= 19:
            wCh += 60
        elif 20 <= wCh <= 39:
            wCh += 20
        elif 40 <= wCh <= 59:
            wCh -= 20
        elif 60 <= wCh <= 79:
            wCh -= 60
        return wCh
            
    hist = [[], [], [], []]
    loc = 0
    for wCh in range(0, 80):
        for gCh in range(80, 120):
            for bus in range(0, 9):
                detector = detector_vec[bus//3]
                if H[wCh, gCh-80, bus] > min_count and H[wCh, gCh-80, bus] <= max_count:
                    coord = detector[flip_bus[bus%3], gCh, flip_wire(wCh)]
                    hist[0].append(coord['x'])
                    hist[1].append(coord['y'])
                    hist[2].append(coord['z'])
                    hist[3].append(H[wCh, gCh-80, bus])
                    loc = loc + 1
#    for coord in [[-3.5, -1.6, 5.1, 1], [-3.5, -1.6, 5.1, 100]]:
#        for index in range(4):
#            hist[index].append(coord[index])
                    
    max_val = 50
    min_val = 1
    
    max_val_log = np.log10(max_val)
    min_val_log = np.log10(min_val)
    
    
    for lim_value in [min_val_log, max_val_log]:
        print(lim_value)
        hist[2].append(5.35)
        hist[0].append(-0.9)
        hist[1].append(-3.07)
        hist[3].append(lim_value)
    
    for i in range(4):
        hist[i] = np.array(hist[i])
    
    
    # Produce 3D histogram plot
    MG_3D_trace = go.Scatter3d(x=hist[2],
                               y=hist[0],
                               z=hist[1],
                               mode='markers',
                               marker=dict(
                                       size=5,
                                       color = np.log10(hist[3]),
                                       colorscale = 'Jet',
                                       opacity=1,
                                       colorbar=dict(thickness=20,
                                                     title = 'Intensity [a.u.]',
                                                     tickmode = 'array',
                                                     tickvals = [min_val_log, 
                                                                 (max_val_log - min_val_log)/2, 
                                                                 max_val_log],
                                                     ticktext = ['Low','Medium','High'],
                                                     ticks = 'outside'
                                                     ),
                              cmin = min_val_log,
                              cmax = max_val_log,
                                       ),

                               name='Multi-Grid',
                               scene='scene1'
                               )
                        
    color_lim_trace = go.Scatter3d(x=[5.35],
                                   y=[-0.9],
                                   z=[-3.07],
                                   mode='markers',
                                   marker=dict(
                                           size=5,
                                           color = 'rgb(255,255,255)',
                                           opacity=1,
                                           line = dict(
                                                   color = 'rgb(255,255,255)',
                                                   width = 1
                                                   )
                                        ),
                                    )
                                       
    
                                     
    # Produce histogram
    ToF_hist, ToF_bins = np.histogram(df_tot.ToF * 62.5e-9 * 1e6, bins = 1000, 
                                      range=[0, 16667])
    ToF_bin_centers = 0.5 * (ToF_bins[1:] + ToF_bins[:-1])
    ToF_trace = go.Scatter(
                           x = ToF_bin_centers,
                           y = ToF_hist,
                           #fill = 'tozerox',
                           marker = dict(
                                         color = 'rgb(0, 0, 0)'
                                        ),
                           fillcolor = 'rgba(0, 0, 255, .5)',
                           #opacity = 0.5,
                           line = dict(
                                       width = 2
                                       )
                           )
    # Introduce figure and put everything together
    fig = py.tools.make_subplots(rows=1, cols=2, 
                             specs=[[{'is_3d': False}, 
                                     {'is_3d': True}]]
                                 )
    
    fig.append_trace(ToF_trace, 1, 1)
    fig.append_trace(MG_3D_trace, 1, 2)
    fig.append_trace(color_lim_trace, 1, 2)
    for b_trace in b_traces:
        fig.append_trace(b_trace, 1, 2)
  
    a = 0.92
    camera = dict(
                 up=dict(x=0, y=0, z=1),
                 center=dict(x=0, y=0, z=0),
                 eye=dict(x=-2*a, y=-0.5*a, z=1.3*a)
                 )
    fig['layout']['scene1']['xaxis'].update(title='z [m]') # range=[5.28, 5.66]
    fig['layout']['scene1']['yaxis'].update(title='x [m]') # range=[-1.64, -0.6]
    fig['layout']['scene1']['zaxis'].update(title='y [m]') # range=[-3.13, -2.2]
    fig['layout']['scene1']['camera'].update(camera)
    fig['layout']['xaxis1'].update(title='ToF [µs]', showgrid=True,
                                   range=[0, 16000])
    fig['layout']['yaxis1'].update(title='Intensity [a.u.]', range=[1.7, 5.2], 
                                   showgrid=True, type='log')
    fig['layout'].update(title=str(data_set),
                         height=600, width=1300)
    fig.layout.showlegend = False
    shapes = [
            {'type': 'line', 'x0': v_pos_x, 'y0': -1000, 
             'x1': v_pos_x, 'y1': 20000000,
             'line':  {'color': 'rgb(500, 0, 0)', 'width': 5}, 'opacity': 0.7}
            ]
    fig['layout'].update(shapes=shapes)
    if path == 'hej':
        py.offline.plot(fig, filename='simple-3d-scatter.html', auto_open=True)
    else:
        pio.write_image(fig, path)

                                
    
    

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
    df = df[(df.wM == 1) & (df.gM <= 5)]
    return df

def calculate_peak_norm(bin_centers, hist, left_edge, right_edge):
    x_l = bin_centers[left_edge]
    y_l = hist[left_edge]
    x_r = bin_centers[right_edge-1]
    y_r = hist[right_edge-1]
    area = sum(hist[left_edge:right_edge])
    bins_under_peak = abs(right_edge - 1 - left_edge)
    area_noise = ((abs(y_r - y_l) * bins_under_peak) / 2
                  + bins_under_peak * min([y_l, y_r]))
    peak_area = area - area_noise
    return peak_area

def get_dE_He3(E_i, ToF, d, T_0, t_off):
    # Declare parameters
    L_1 = 20.01                                # Target-to-sample distance
    m_n = 1.674927351e-27                      # Neutron mass [kg]
    meV_to_J = 1.60218e-19 * 0.001             # Convert meV to J
    J_to_meV = 6.24150913e18 * 1000            # Convert J to meV
    # Calculate dE
    E_i_J = E_i * meV_to_J                     # Convert E_i from meV to J
    v_i = np.sqrt((E_i_J*2)/m_n)               # Get velocity of E_i
    t_1 = (L_1 / v_i) + T_0 * 1e-6             # Use velocity to find t_1
    ToF_real = ToF * 1e-6 + (t_off * 1e-6)     # Time from source to detector
    t_f = ToF_real - t_1                       # Time from sample to detector
    E_J = (m_n/2) * ((d/t_f) ** 2)             # Energy E_f in Joule
    E_f = E_J * J_to_meV                       # Convert to meV
    return (E_i - E_f), t_f
    


def get_dE(E_i, ToF, d, T_0, t_off, frame_shift):
    # Declare parameters
    L_1 = 20.01                                # Target-to-sample distance
    m_n = 1.674927351e-27                      # Neutron mass [kg]
    meV_to_J = 1.60218e-19 * 0.001             # Convert meV to J
    J_to_meV = 6.24150913e18 * 1000            # Convert J to meV
    # Calculate dE
    E_i_J = E_i * meV_to_J                     # Convert E_i from meV to J
    v_i = np.sqrt((E_i_J*2)/m_n)               # Get velocity of E_i
    t_1 = (L_1 / v_i) + T_0 * 1e-6             # Use velocity to find t_1
    ToF_real = ToF * 62.5e-9 + (t_off * 1e-6)  # Time from source to detector
    ToF_real += frame_shift                    # Apply frame-shift
    t_f = ToF_real - t_1                       # Time from sample to detector
    E_J = (m_n/2) * ((d/t_f) ** 2)             # Energy E_f in Joule
    E_f = E_J * J_to_meV                       # Convert to meV
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


def get_t_off_He3(calibration):
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../Tables/He3_offset.xlsx')
    matrix = pd.read_excel(path).values
    He3_offset_table = {}
    for row in matrix:
        He3_offset_table.update({row[0]: row[2]})
    offset = float(He3_offset_table[calibration])
    return offset


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
    if E_i == 3:
        frame_shift += 2 * (16666.66666e-6) - 0.00800875
    if E_i == 4:
        frame_shift += 2 * (16666.66666e-6) - 0.0125178125
    if E_i == 5:
        frame_shift += 2 * (16666.66666e-6) - 0.015595
    if E_i == 6:
        frame_shift += (16666.66666e-6) - 0.001190399
    if E_i == 7:
        frame_shift += (16666.66666e-6) - 0.002965625
    if E_i == 8:
        frame_shift += (16666.66666e-6) - 0.0043893
    if E_i == 9:
        frame_shift += (16666.66666e-6) - 0.0055678125
    if E_i == 10:
        frame_shift += (16666.66666e-6) - 0.0065653125
    if E_i == 12:
        frame_shift += (16666.66666e-6) - 0.00817125
    if E_i == 14:
        frame_shift += (16666.66666e-6) - 0.00942
    if E_i == 15:
        frame_shift += (16666.66666e-6) - 0.009948437499999999
    if E_i == 16:
        frame_shift += (16666.66666e-6) - 0.01042562499
    if E_i == 18:
        frame_shift += (16666.66666e-6) - 0.011259375
    if E_i == 21:
        frame_shift += (16666.66666e-6) - 0.01227875
    if E_i == 20:
        frame_shift += (16666.66666e-6) - 0.011965
    if E_i == 25:
        frame_shift += (16666.66666e-6) - 0.013340625
    if E_i == 30:
        frame_shift += (16666.66666e-6) - 0.01435625
    if E_i == 32:
        frame_shift += (16666.66666e-6) - 0.014646875
    if E_i == 34:
        frame_shift += (16666.66666e-6) - 0.015009375
    if E_i == 35:
        frame_shift += (16666.66666e-6) - 0.01514625
    if E_i == 40:
        frame_shift += (16666.66666e-6) - 0.0157828125
    if E_i == 40.8:
        frame_shift += (16666.66666e-6) - 0.015878125
    if E_i == 48:
        frame_shift += (16666.66666e-6) - 0.0165909375
    return frame_shift


def find_He3_measurement_id(calibration):
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../Tables/experiment_log.xlsx')
    matrix = pd.read_excel(path).values
    measurement_table = {}
    for row in matrix:
        measurement_table.update({row[1]: row[0]})
    return measurement_table[calibration]


def get_He3_offset(calibration):
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '../Tables/He3_offset.xlsx')
    matrix = pd.read_excel(path).values
    He3_offset_table = {}
    for row in matrix:
        He3_offset_table.update({row[0]: row[1]})
    
    offset = float(He3_offset_table[calibration])
    
    return offset


def get_FWHM(bin_centers, hist, left_edge, right_edge, vis_help,
             b_label='Background'):
    def find_nearest(array, value):
        idx = (np.abs(array - value)).argmin()
        return idx
    # Calculate background level
    x_l = bin_centers[left_edge]
    y_l = hist[left_edge]
    x_r = bin_centers[right_edge]
    y_r = hist[right_edge]
    par_back = np.polyfit([x_l, x_r], [y_l, y_r], deg=1)
    f_back = np.poly1d(par_back)
    xx_back = np.linspace(x_l, x_r, 100)
    yy_back = f_back(xx_back)
     
    plt.plot(xx_back, yy_back, 'orange', label=b_label)
     
    bins_under_peak = abs(right_edge - 1 - left_edge)
    
    area_noise = ((abs(y_r - y_l) * bins_under_peak) / 2 
                      + bins_under_peak * y_l)
        
    area = sum(hist[left_edge:right_edge])
    peak_area = area - area_noise
        
    # Calculate HM
  #  peak = peakutils.peak.indexes(hist[left_edge:right_edge])
    maximum = max(hist[left_edge:right_edge])
    peak=np.where(hist[left_edge:right_edge] == maximum)
    peak = peak[len(peak)//2][len(peak)//2]
    if vis_help:
        plt.plot(bin_centers[left_edge:right_edge][peak],
                 hist[left_edge:right_edge][peak], 'bx', label='Maximum', 
                 zorder=5)
    M = hist[left_edge:right_edge][peak]
    xM = bin_centers[left_edge:right_edge][peak]
    noise_level = yy_back[find_nearest(xx_back, xM)]
    HM = (M-noise_level)/2 + noise_level
    SNR = M/noise_level
    SNR = SNR

    # Calculate FWHM
    left_idx = find_nearest(hist[left_edge:left_edge+peak], HM)
    right_idx = find_nearest(hist[left_edge+peak:right_edge], HM)
        
    sl = []
    sr = []
        
    if hist[left_edge+left_idx] > HM:
        sl = [-1, 0]
    else:
        sl = [0, 1]
        
    if hist[left_edge+peak+right_idx] < HM:
        rl = [-1, 0]
    else:
        rl = [0, 1]
        
    left_x = [bin_centers[left_edge+left_idx+sl[0]], 
              bin_centers[left_edge+left_idx+sl[1]]]
    left_y = [hist[left_edge+left_idx+sl[0]], hist[left_edge+left_idx+sl[1]]]
    right_x = [bin_centers[left_edge+peak+right_idx+rl[0]], 
               bin_centers[left_edge+peak+right_idx+rl[1]]]
    right_y = [hist[left_edge+peak+right_idx+rl[0]], 
               hist[left_edge+peak+right_idx+rl[1]]]

    par_left = np.polyfit(left_x, left_y, deg=1)
    f_left = np.poly1d(par_left)
    par_right = np.polyfit(right_x, right_y, deg=1)
    f_right = np.poly1d(par_right)
        
    xx_left = np.linspace(left_x[0], left_x[1], 100)
    xx_right = np.linspace(right_x[0], right_x[1], 100)
    yy_left = f_left(xx_left)
    yy_right = f_right(xx_right)
    if vis_help:
        plt.plot(xx_left, yy_left, 'blue', label=None)
        plt.plot(xx_right, yy_right, 'blue', label=None)
        
    left_idx = find_nearest(yy_left, HM)
    right_idx = find_nearest(yy_right, HM)
        
        
    if vis_help:
        plt.plot([xx_left[left_idx], xx_right[right_idx]], 
                 [HM, HM], 'g', label='FWHM')
        
    L = xx_left[left_idx]
    R = xx_right[right_idx]
    FWHM = R - L

    return FWHM, SNR, maximum


def get_peak_edges(calibration):
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, 
                        '../Tables/Van__3x3_He3_and_MG_peak_edges.xlsx')
    matrix = pd.read_excel(path).values
    He3_and_MG_peak_edges_table = {}
    for row in matrix:
        He3_and_MG_peak_edges_table.update({row[0]: [row[1], row[2], row[3], 
                                            row[4]]})
    
    He3_and_MG_peak_edges = He3_and_MG_peak_edges_table[calibration]
    
    MG_left = int(He3_and_MG_peak_edges[0])
    MG_right = int(He3_and_MG_peak_edges[1])
    He3_left = int(He3_and_MG_peak_edges[2])
    He3_right = int(He3_and_MG_peak_edges[3])
    
    return MG_left, MG_right, He3_left, He3_right


def import_He3_coordinates():
    dirname = os.path.dirname(__file__)
    he_folder = os.path.join(dirname, '../Tables/Helium3_coordinates/')
    az_path = he_folder + '145160_azimuthal.txt'
    dis_path = he_folder + '145160_distance.txt'
    pol_path = he_folder + '145160_polar.txt'

    az = np.loadtxt(az_path)
    dis = np.loadtxt(dis_path)
    pol = np.loadtxt(pol_path)

    x = dis*np.sin(pol * np.pi/180)*np.cos(az * np.pi/180)
    y = dis*np.sin(az * np.pi/180)*np.sin(pol * np.pi/180)
    z = dis*np.cos(pol * np.pi/180)
    return x, y, z

def plot_dE_background(E_i, calibration, measurement_time, 
                       MG_norm, he_min, he_max, back_yes, tot_norm,
                       isPureAluminium = False, lim_ToF_vec = None):
    print('Lim ToF vec: ' + str(lim_ToF_vec))
    print('TOT NORM: ' + str(tot_norm))
    # Import background data
    dirname = os.path.dirname(__file__)
    clu_path = os.path.join(dirname, '../Clusters/Background.h5')
    df = pd.read_hdf(clu_path, 'coincident_events')
    df = df[df.d != -1]
    df = df[(df.wADC > 500) & (df.gADC > 400)]
    df = df[(df.wM == 1) & (df.gM <= 5)]
    df = df[df.Time < 1.5e12]
    print('Length of df before: ' + str(df.shape[0]))
    if lim_ToF_vec is not None:
        print('Hello')
        df = df[  (df.ToF * 62.5e-9 * 1e6 >= lim_ToF_vec[0])
                & (df.ToF * 62.5e-9 * 1e6 <= lim_ToF_vec[1])]
    print('Length of df after: ' + str(df.shape[0]))
    
    if isPureAluminium:
        df = df[(df.Bus <= 8) & (df.Bus >= 6)]
        df = df[  (df.gCh != 119) & (df.gCh != 80) 
                & (df.gCh != 99) & (df.gCh != 101)]
    # Calculate background duration
    start_time = df.head(1)['Time'].values[0]
    end_time = df.tail(1)['Time'].values[0]
    duration = (end_time - start_time) * 62.5e-9
    # Calculate background
    t_off = get_t_off(calibration) * np.ones(df.shape[0])
    T_0 = get_T0(calibration, E_i) * np.ones(df.shape[0])
    frame_shift = get_frame_shift(E_i) * np.ones(df.shape[0])
    E_i = E_i * np.ones(df.shape[0])
    ToF = df.ToF.values
    d = df.d.values
    dE, t_f = get_dE(E_i, ToF, d, T_0, t_off, frame_shift)
    df_temp = pd.DataFrame(data={'dE': dE, 't_f': t_f})
    dE = df_temp[df_temp['t_f'] > 0].dE
    # Calculate weights
    number_of_events = len(dE)
    events_per_s = number_of_events / duration
    events_s_norm = events_per_s / number_of_events
    weights = ((1/tot_norm) 
                * events_s_norm * measurement_time * np.ones(len(dE)))
    # Histogram background
    dE_bins = 390
    dE_range = [he_min, he_max]
    MG_dE_hist, MG_bins = np.histogram(dE, bins=dE_bins, range=dE_range, 
                                       weights=weights)
    MG_bin_centers = 0.5 * (MG_bins[1:] + MG_bins[:-1])
    if back_yes:
        plt.plot(MG_bin_centers, MG_dE_hist, color='green', label='MG background', 
                    zorder=5)
    
    return MG_dE_hist


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


def get_charge_norm(calibration):
    dir_name = os.path.dirname(__file__)
    path = os.path.join(dir_name, '../Tables/Charge_normalisation.xlsx')
    matrix = pd.read_excel(path).values
    charge_norm_table = {}
    for i, row in enumerate(matrix):
        charge_norm_table.update({row[0]: [row[2], row[5], row[7], row[8]]})
    
    no_glitch_time = charge_norm_table[calibration][0]
    total_time = charge_norm_table[calibration][1]
    MG_charge = charge_norm_table[calibration][2]
    He3_charge = charge_norm_table[calibration][3]
    charge_norm = ((MG_charge * (no_glitch_time/total_time)) / He3_charge)
    print(charge_norm)
    
    return charge_norm

def create_ess_channel_to_coordinate_map(theta, offset):
    dirname = os.path.dirname(__file__)
    file_path = os.path.join(dirname, 
                             '../Tables/Coordinates_MG_SEQ_ESS.xlsx')
    matrix = pd.read_excel(file_path).values
    coordinates = matrix[1:801]
    ess_ch_to_coord = np.empty((3,124,80),dtype='object')
    coordinate = {'x': -1, 'y': -1, 'z': -1}
    axises =  ['x','y','z']
    
    c_offset = [[-1, 1, -1], [-1, -1, 1], [-1, 1, 1]]
    c_count = 0
    
    for i, row in enumerate(coordinates):
        grid_ch = i // 20 + 80
        for j, col in enumerate(row):
            module = j // 12
            layer = (j // 3) % 4
            wire_ch = (19 - (i % 20)) + (layer * 20)
            coordinate_count = j % 3
            coordinate[axises[coordinate_count]] = col
            if coordinate_count == 2:
                x = coordinate['x']
                y = coordinate['y']
                z = coordinate['z']
                # Convert from [mm] to [m]
                x = x/1000
                y = y/1000
                z = z/1000
                # Insert corners of vessels
                if wire_ch == 0 and grid_ch == 80 and module == 0:
                    ess_ch_to_coord[0][120][0] = {'x': offset['x'], 'y': offset['y'], 'z': offset['z']}
                if (  (wire_ch == 0 and grid_ch == 119 and module == 0)
                    | (wire_ch == 60 and grid_ch == 80 and module == 2)
                    | (wire_ch == 60 and grid_ch == 119 and module == 2)
                    ):
                    x_temp = x + 46.514/1000 * c_offset[c_count][0] + np.finfo(float).eps
                    y_temp = y + 37.912/1000 * c_offset[c_count][1] + np.finfo(float).eps
                    z_temp = z + 37.95/1000 * c_offset[c_count][2] + np.finfo(float).eps
                    z_temp, x_temp, y_temp = x_temp, y_temp, z_temp
                    x_temp, z_temp = get_new_x(x_temp, z_temp, theta), get_new_y(x_temp, z_temp, theta)
                    # Apply translation
                    x_temp += offset['x']
                    y_temp += offset['y']
                    z_temp += offset['z']
                    ess_ch_to_coord[0][121+c_count][0] = {'x': x_temp, 
                                                          'y': y_temp,
                                                          'z': z_temp}
                    c_count += 1
                
                # Shift to match internal and external coordinate system
                z, x, y = x, y, z
                # Apply rotation
                x, z = get_new_x(x, z, theta), get_new_y(x, z, theta)
                # Apply translation
                x += offset['x']
                y += offset['y']
                z += offset['z']

                ess_ch_to_coord[module, grid_ch, wire_ch] = {'x': x, 'y': y,
                                                             'z': z}
                coordinate = {'x': -1, 'y': -1, 'z': -1}

    return ess_ch_to_coord
    
def create_ill_channel_to_coordinate_map(theta, offset):
        
    WireSpacing  = 10     #  [mm]
    LayerSpacing = 23.5   #  [mm]
    GridSpacing  = 23.5   #  [mm]
    
    x_offset = 46.514     #  [mm]
    y_offset = 37.912     #  [mm]
    z_offset = 37.95      #  [mm]
    
    corners =   [[0, 80], [0, 119], [60, 80], [60, 119]]
    corner_offset = [[-1, -1, -1], [-1, -1, 1], [-1, 1, -1], [-1, 1, 1]]
    
    # Make for longer to include the for corners of the vessel
    ill_ch_to_coord = np.empty((3,124,80),dtype='object')
    for Bus in range(0,3):
        for GridChannel in range(80,120):
            for WireChannel in range(0,80):
                    x = (WireChannel % 20)*WireSpacing + x_offset
                    y = ((WireChannel // 20)*LayerSpacing 
                         + (Bus*4*LayerSpacing) + y_offset)
                    z = ((GridChannel-80)*GridSpacing) + z_offset 
                    # Convert from [mm] to [m]
                    x = x/1000
                    y = y/1000
                    z = z/1000
                    # Shift to match internal and external coordinate system
                    z, x, y = x, y, z
                    # Apply rotation
                    x, z = get_new_x(x, z, theta), get_new_y(x, z, theta)
                    # Apply translation
                    x += offset['x']
                    y += offset['y']
                    z += offset['z']
                                        
                    ill_ch_to_coord[Bus,GridChannel,WireChannel] = {'x': x,
                                                                    'y': y,
                                                                    'z': z}
        if Bus == 0:
            for i, corner in enumerate(corners[1:2]):
                WireChannel = corner[0]
                GridChannel = corner[1]
                x = (WireChannel % 20)*WireSpacing + x_offset
                y = ((WireChannel // 20)*LayerSpacing + (Bus*4*LayerSpacing) + y_offset)
                z = ((GridChannel-80)*GridSpacing) + z_offset 
                x += corner_offset[i+1][0] * x_offset
                y += corner_offset[i+1][1] * y_offset
                z += corner_offset[i+1][2] * z_offset
                x = x/1000 + np.finfo(float).eps
                y = y/1000 + np.finfo(float).eps
                z = z/1000 + np.finfo(float).eps
                z, x, y = x, y, z

                x, z = get_new_x(x, z, theta), get_new_y(x, z, theta)
                x += offset['x']
                y += offset['y']
                z += offset['z']
                ill_ch_to_coord[0, 121+i, 0] = {'x': x, 'y': y, 'z': z}
        
            ill_ch_to_coord[Bus, 120, 0] = {'x': offset['x'], 'y': offset['y'], 'z': offset['z']}

            
        if Bus == 2:
            for i, corner in enumerate(corners[2:]):
                WireChannel = corner[0]
                GridChannel = corner[1]
                x = (WireChannel % 20)*WireSpacing + x_offset
                y = ((WireChannel // 20)*LayerSpacing + (Bus*4*LayerSpacing) + y_offset)
                z = ((GridChannel-80)*GridSpacing) + z_offset 
                x += corner_offset[i+2][0] * x_offset
                y += corner_offset[i+2][1] * y_offset
                z += corner_offset[i+2][2] * z_offset
                x = x/1000
                y = y/1000
                z = z/1000
                z, x, y = x, y, z
                x, z = get_new_x(x, z, theta), get_new_y(x, z, theta)
                x += offset['x']
                y += offset['y']
                z += offset['z']
                ill_ch_to_coord[0, 122+i, 0] = {'x': x, 'y': y, 'z': z}
            
    return ill_ch_to_coord


def get_new_x(x, y, theta):
    return np.cos(np.arctan(y/x)+theta)*np.sqrt(x ** 2 + y ** 2)
    

def get_new_y(x, y, theta):
    return np.sin(np.arctan(y/x)+theta)*np.sqrt(x ** 2 + y ** 2)

def import_He3_coordinates_NEW():
    dirname = os.path.dirname(__file__)
    he_folder = os.path.join(dirname, '../Tables/Helium3_coordinates/')
    az_path = he_folder + '145160_azimuthal.txt'
    dis_path = he_folder + '145160_distance.txt'
    pol_path = he_folder + '145160_polar.txt'

    az = np.loadtxt(az_path)
    dis = np.loadtxt(dis_path)
    pol = np.loadtxt(pol_path)
    distance = np.ones(len(dis) * 2)
    count = 0
    for d in dis:
        for i in range(2):
            distance[count] = d
            count += 1

    x = dis*np.sin(pol * np.pi/180)*np.cos(az * np.pi/180)
    y = dis*np.sin(az * np.pi/180)*np.sin(pol * np.pi/180)
    z = dis*np.cos(pol * np.pi/180)
    d = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    
    
    labels = []
    for i in range(0, len(x)):
        labels.append('Number: ' + str(i) + '<br>Distance: ' + str(round(d[i], 4)))
    return x, y, z, distance
    