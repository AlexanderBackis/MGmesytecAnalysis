#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 13:18:00 2018

@author: alexanderbackis
"""

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

    event_number = np.arange(1, df.shape[0]+1,1)
    trigger_number = np.arange(1,len(triggers)+1,1)
    
    plt.subplot(1,2,1)
    plt.title('Timestamp vs. Event number', x=0.5, y=1.04)
    plt.xlabel('Event number')
    plt.ylabel('Timestamp')
    plt.plot(event_number, df.Time, color='blue')
    
    plt.subplot(1,2,2)
    plt.title('Trigger-time vs. Trigger number', x=0.5, y=1.04)
    plt.xlabel('Trigger number')
    plt.ylabel('Trigger time')
    plt.plot(trigger_number, triggers, color='blue')
    
    plt.tight_layout()
    
    plot_path = get_plot_path(data_set) + name + '.pdf'
        
    return fig, plot_path

# =============================================================================
# 12. Delta E histogram (separate detectors)
# =============================================================================
    
def dE_histogram(fig, name, df, data_set, E_i):
        df = df[df.d != -1]
        bus_ranges = [[0,2], [3,5], [6,8]]
        
        name = ('12. Histogram of $E_i$ - $E_f$, Vanadium, ' + str(E_i) + 'meV')
        
        fig.suptitle(name, x=0.5, y=1.05)
        
        detectors = ['ILL', 'ESS_1', 'ESS_2']
    
        fig.set_figheight(4)
        fig.set_figwidth(12)
        
        color_vec = ['darkorange', 'magenta', 'blue']
        
        dE_bins = 400
        dE_range = [-E_i, E_i]
        
        for i, bus_range in enumerate(bus_ranges):
            title = detectors[i]
            bus_min = bus_range[0]
            bus_max = bus_range[1]
            df_temp = df[(df.Bus >= bus_min) & (df.Bus <= bus_max)]
            plt.subplot(1, 3, i+1)
            plt.grid(True, which='major', zorder=0)
            plt.grid(True, which='minor', linestyle='--',zorder=0)
            plt.hist(df_temp.dE, bins=dE_bins, range=dE_range, log=LogNorm(), 
                     color=color_vec[i], histtype='step', label=title, 
                     zorder=3)
            plt.hist(df.dE, bins=dE_bins, range=dE_range, log=LogNorm(), 
                     color='black', histtype='step', label='All detectors', 
                     zorder=2)
#            plt.ylim(1, 5e4)
            plt.legend()
            plt.xlabel('$E_i$ - $E_f$ [meV]')
            plt.ylabel('Counts')
            plt.title(title)
        
        plt.tight_layout()
        plot_path = get_plot_path(data_set) + name + '.pdf'
        
        return fig, plot_path

# =============================================================================
# 13. Delta E
# =============================================================================
    
def dE_single(fig, name, df, data_set, E_i):
        df = df[df.d != -1]
        df = df[(df.wADC > 400) & (df.gADC > 400)]
        df = df[(df.wM == 1) & (df.gM < 5)]
        bus_min = 6
        bus_max = 8
        df = df[(df.Bus >= bus_min) & (df.Bus <= bus_max)]
        
        
        bus_ranges = [[0,2], [3,5], [6,8]]
        color_vec = ['darkorange', 'magenta', 'blue']
        detectors = ['ILL', 'ESS_1', 'ESS_2']
        dE_bins = 400
        dE_range = [-E_i, E_i]
        
        name = ('13. Vanadium, ' + str(E_i) + 'meV')
        plt.grid(True, which='major', zorder=0)
        plt.grid(True, which='minor', linestyle='--',zorder=0)
        
#        for i, bus_range in enumerate(bus_ranges):
#            bus_min = bus_range[0]
#            bus_max = bus_range[1]
#            df_temp = df[(df.Bus >= bus_min) & (df.Bus <= bus_max)]
#
#            plt.hist(df_temp.dE, bins=dE_bins, range=dE_range, log=LogNorm(), 
#                     color=color_vec[i], histtype='step', label=detectors[i], 
#                     zorder=3)
        
        hist, bins, patches = plt.hist(df.dE, bins=dE_bins, range=dE_range, log=LogNorm(), 
                     color='black', histtype='step',  
                     zorder=2)
        #plt.legend(loc='upper left')
        plt.xlabel('$\Delta E$ [meV]')
        plt.ylabel('Counts')
        plt.title(name + ', Histogram of $E_i$ - $E_f$')
        
        folder = get_output_path(data_set)
        hist_path = folder + name + ', histogram.dat'
        bins_path = folder + name + ', bins.dat'
        np.savetxt(hist_path, hist, delimiter=",")
        np.savetxt(bins_path, bins, delimiter=",")
            
        
        plot_path = get_plot_path(data_set) + name + '.pdf'

        
        return fig, plot_path
    
    
# =============================================================================
# 14. ToF vs d + dE
# =============================================================================
        
    
def ToF_vs_d_and_dE(fig, name, df, data_set, E_i):
        df = df[df.d != -1]
        df = df[df.tf > 0]
        bus_ranges = [[0,2], [3,5], [6,8]]
        
        name = ('14. Histogram of $E_i$ - $E_f$, Vanadium, ' + str(E_i) + 'meV')
        
        fig.suptitle(name, x=0.5, y=1.05)
        
        detectors = ['ILL', 'ESS_1', 'ESS_2']
    
        fig.set_figheight(9)
        fig.set_figwidth(12)
        
        color_vec = ['darkorange', 'magenta', 'blue']
        
        dE_bins = 400
        dE_range = [-E_i, E_i]
        
        ToF_bins = 200
        ToF_range = [0, 20e3]
        
        d_bins = 100
        d_range = [5.9, 6.5]
        
        tf_bins = 200
        tf_range = [0, 20e3]
        
        for i, bus_range in enumerate(bus_ranges):
#            # Plot ToF vs d
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
    
def compare_MG_and_He3(fig, name, df, data_set, E_i):
    
    name = ('16. Vanadium, ' + str(E_i) + 'meV\n Comparrison between He3 and'
            + ' Multi-Grid')
    
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
    
    dE_bins = 400
    dE_range = [-E_i, E_i]
    df = filter_clusters(df)
    hist, bins, patches = plt.hist(df.dE, bins=dE_bins, range=dE_range)
    plt.clf()
    plt.title(name)
    plt.grid(True, which='major', zorder=0)
    plt.grid(True, which='minor', linestyle='--',zorder=0)
    
    binCenters = 0.5 * (bins[1:] + bins[:-1])
    norm_MG = 1 / sum(hist)
    plt.plot(binCenters+1.1, hist * norm_MG, color='crimson', zorder=3, 
             label='Multi-Grid')
    
    
    data = energy_dict[E_i]
    norm_he3 = 1 / sum(data['histogram'])
    plt.plot(data['bins']-1, data['histogram'] * norm_he3, color='teal',
             label='He3', zorder=2)
    
    plt.xlabel('$E_i$ - $E_f$ [meV]')
    plt.ylabel('Normalized counts')
    plt.yscale('log')
    
    plt.legend(loc='upper left')
    
    plot_path = get_plot_path(data_set) + name + '.pdf'
    
    return fig, plot_path

# =============================================================================
# 17. Plotly interactive ToF
# =============================================================================
    
def plotly_interactive_ToF(df, data_set, E_i):
    df = filter_clusters(df)
    data = [go.Histogram(visible = False,
                         name = str(thres),
                         x = df[df.wADC >= thres].ToF,
                         nbinsx = 1000)
            for thres in np.arange(0, 4100, 100)]
    
    data[10]['visible'] = True
    
    steps = []
    for i in range(len(data)):
        step = dict(
                method = 'restyle',  
                args = ['visible', [False] * len(data)],
                label = str(i*4100//len(data))
        )
        step['args'][1][i] = True # Toggle i'th trace to "visible"
        steps.append(step)

    sliders = [dict(
        active = 10,
        currentvalue = {"prefix": "Wire threshold [ADC channels]: "},
        pad = {"t": 50},
        steps = steps,
    )]
    
    layout = go.Layout(
            xaxis=dict(
                range=[0, 3e5],
                title='ToF [TDC channels]'
                ),
            yaxis=dict(
                type='log',
                autorange=True,
                title='Counts'
                ),
            sliders=sliders,
            title='ToF Histogram')
    
    fig = dict(data=data, layout=layout)
    py.offline.plot(fig, filename='Sine Wave Slider.html')
    
    

    

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
#    df = df[(df.wADC > 400) & (df.gADC > 400)]
    df = df[(df.wM == 1) & (df.gM < 5)]
    return df



    
    
    
    