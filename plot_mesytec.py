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


# =============================================================================
# Plot 2D Histogram of hit location (channels)
# =============================================================================

def plot_2D_hit(df_clu, bus, number_of_detectors, loc, fig):
    df_clu_red = df_clu[(df_clu.wCh != -1) & (df_clu.gCh != -1)]
    
    plt.subplot(number_of_detectors,3,loc+1)
    plt.hist2d(df_clu_red.wCh, df_clu_red.gCh, bins=[80, 40], 
               range=[[-0.5,79.5],[79.5,119.5]], norm=LogNorm(), vmin=1, vmax=10000,
               cmap='jet')
    plt.xlabel("Wire [Channel number]")
    plt.ylabel("Grid [Channel number]")
    
    plt.colorbar()
    name = 'Bus ' + str(bus) + '\n(' + str(df_clu_red.shape[0]) + ' events)'
    plt.title(name)
    
def plot_2D_hit_buses(name, clusters, bus_vec, number_of_detectors, data_set, 
                      thresADC = 0):
    fig = plt.figure()
    name = (name + ' (Threshold: '  + str(thresADC) + ' ADC channels)')
    fig.suptitle(name + '\n(Threshold: ' 
                 + str(thresADC) + ' ADC channels)', x=0.5, y=1.05, 
                 fontweight="bold")
    fig.set_figheight(4 * number_of_detectors)
    fig.set_figwidth(14)
    for loc, bus in enumerate(bus_vec):
        df_clu = clusters[clusters.Bus == bus]
        plot_2D_hit(df_clu, bus, number_of_detectors, loc, fig)
    plt.tight_layout()
    plt.show()
    plot_path = get_plot_path(data_set) + name  + '.pdf'
    fig.savefig(plot_path, bbox_inches='tight')

# =============================================================================
# Plot 2D Histogram of collected charge
# =============================================================================

def charge_scatter(df, bus, number_of_detectors, loc, fig, minWM = 0, 
                   maxWM = 100, minGM = 0, maxGM = 100, 
                   exclude_channels = [-1] ):

    df_red = df[(df.Bus == bus) & (df.gM >= minWM) &
                (df.wM <= maxWM) & (df.gM >= minGM) & (df.gM <= maxGM)]
    
    for Channel in exclude_channels:
        if Channel < 80:
            df_red = df_red[df_red.wCh != Channel]
        else:
            df_red = df_red[df_red.gCh != Channel]
    
    plt.subplot(number_of_detectors,3,loc+1)

    plt.hist2d(df_red.wADC, df_red.gADC, bins=[200, 200], 
               norm=LogNorm(),range=[[0, 5000], [0, 5000]], vmin=1, vmax=10000,
               cmap='jet')
    plt.xlabel("wADC [ADC channels]")
    plt.ylabel("gADC [ADC channels]")
    plt.colorbar()
    name = 'Bus ' + str(bus) + '\n(' + str(df_red.shape[0]) + ' events)'
    plt.title(name)
    
def plot_charge_scatter_buses(name, df, bus_order, number_of_detectors, data_set, 
                              minWM = 0, maxWM = 100, minGM = 0, maxGM = 100,
                              exclude_channels = [-1]):
    fig = plt.figure()
    name = (name + '\n' 
            + '(wm_min: ' + str(minWM) + 
            ', wm_max: ' + str(maxWM) +
            ', gm_min: ' + str(minGM) +
            ', gm_max: ' + str(maxGM) +
            ', excluded channels: ' + str(exclude_channels) +
            ')')
    fig.suptitle(name, x=0.5, y=1.05, 
                 fontweight="bold")
    fig.set_figheight(4 * number_of_detectors)
    fig.set_figwidth(14)
    for loc, bus in enumerate(bus_order):
        df_clu = df[df.Bus == bus]
        charge_scatter(df_clu, bus, number_of_detectors, loc, fig, minWM, maxWM, 
                       minGM, maxGM, exclude_channels)

    plt.tight_layout()
    plt.show()
    plot_path = get_plot_path(data_set) + name  + '.pdf'
    fig.savefig(plot_path, bbox_inches='tight')
    
    
# =============================================================================
# Plot 2D Histogram of Hit Position with a specific side
# =============================================================================
    
def plot_2D_side_1(bus_vec, df, fig, number_of_detectors, count_range):
    name = 'Front view'
    df_tot = pd.DataFrame()
    
    for i, bus in enumerate(bus_vec):
        df_clu = df[df.Bus == bus]
        df_clu = df_clu[(df_clu.wCh != -1) & (df_clu.gCh != -1)]
        df_clu['wCh'] += (80 * i)
        df_clu['gCh'] += (-80 + 1)
        df_tot = pd.concat([df_tot, df_clu])        
    
    plt.hist2d(np.floor(df_tot['wCh'] / 20).astype(int) + 1, df_tot.gCh, bins=[12*number_of_detectors, 40], 
               range=[[0.5,12*number_of_detectors + 0.5],[0.5,40.5]], norm=LogNorm(), vmin=count_range[0], vmax=count_range[1],
               cmap = 'jet')
    
    plt.xlabel("Layer")
    plt.ylabel("Grid")
    plt.colorbar()
    plt.title(name)
    
def plot_2D_side_2(bus_vec, df, fig, number_of_detectors, count_range):
    name = 'Top view'
    df_tot = pd.DataFrame()
    
    for i, bus in enumerate(bus_vec):
        df_clu = df[df.Bus == bus]
        df_clu = df_clu[(df_clu.wCh != -1) & (df_clu.gCh != -1)]
        df_clu['wCh'] += (80 * i)
        df_tot = pd.concat([df_tot, df_clu])  
        
    plt.hist2d(np.floor(df_tot['wCh'] / 20).astype(int) + 1, df_tot['wCh'] % 20 + 1, 
               bins=[12*number_of_detectors, 20], range=[[0.5,12*number_of_detectors + 0.5],[0.5,20.5]], norm=LogNorm(), vmin=count_range[0], 
               vmax=count_range[1], cmap = 'jet')
    
    plt.xlabel("Layer")
    plt.ylabel("Wire")
    plt.colorbar()
    plt.title(name)
    
def plot_2D_side_3(bus_vec, df, fig, number_of_detectors, count_range):
    name = 'Side view'
    df_tot = pd.DataFrame()
    
    for i, bus in enumerate(bus_vec):
        df_clu = df[df.Bus == bus]
        df_clu = df_clu[(df_clu.wCh != -1) & (df_clu.gCh != -1)]
        df_clu['gCh'] += (-80 + 1)
        df_tot = pd.concat([df_tot, df_clu])
    
        
    plt.hist2d(df_tot['wCh'] % 20 + 1, df_tot['gCh'],
               bins=[20, 40], range=[[0.5,20.5],[0.5,40.5]], norm=LogNorm(), 
               vmin=count_range[0], vmax=count_range[1], cmap = 'jet')
    
    plt.xlabel("Wire")
    plt.ylabel("Grid")
    plt.colorbar()
    plt.title(name)
    
def plot_all_sides(name, bus_vec, df, data_set, number_of_detectors, count_range = [1e2, 3e4], 
                   ADCthreshold = 0):
    fig = plt.figure()
    
    fig.set_figheight(4)
    fig.set_figwidth(14)
    
    plt.subplot(1,3,1)
    plot_2D_side_1(bus_vec, df, fig, number_of_detectors, count_range)
    plt.subplot(1,3,2)
    plot_2D_side_2(bus_vec, df, fig, number_of_detectors, count_range)
    plt.subplot(1,3,3)
    plot_2D_side_3(bus_vec, df, fig, number_of_detectors, count_range)
    
    name = (name)
    fig.suptitle(name, x=0.5, y=1.05, fontweight="bold")
    plt.tight_layout()
    plt.show()
    plot_path = get_plot_path(data_set) + name  + '.pdf'
    fig.savefig(plot_path, bbox_inches='tight')

    
# =============================================================================
# Plot 1D Pulse Height Spectrum, Channel VS Charge
# =============================================================================
    
def plot_PHS_bus_channel(df, bus, Channel):
    df_red = df[df.Channel == Channel]
    plt.hist(df_red.ADC, bins=50, range=[0,4400])  
    
def plot_PHS_several_channels(name, df, bus, ChVec, data_set):
    fig = plt.figure()
    df_red = df[df.Bus == bus]
    
    for Channel in ChVec:
        df_ch = df_red[df_red.Channel == Channel]
        plt.hist(df_ch.ADC, bins=100, range=[0,4400], log=False, alpha = 1, 
                 label = 'Channel ' + str(Channel), histtype='step')
    
    plt.legend(loc='upper right')
    plt.xlabel("Charge  [ADC channels]")
    plt.ylabel("Counts")
    name = name + '\nBus ' + str(bus) + ', Channels: ' + str(ChVec)
    plt.title(name)
    plt.show()
    plot_path = get_plot_path(data_set) + name  + '.pdf'
    fig.savefig(plot_path, bbox_inches='tight')
    
    
# =============================================================================
# Plot 2D Pulse Height Spectrum, Channel VS Charge
# =============================================================================

def plot_PHS(df, bus, loc, number_of_detectors, fig, count_limit = 3000):
    df_red = df[df.Bus == bus]
    plt.subplot(1*number_of_detectors,3,loc+1)
    plt.hist2d(df_red.Channel, df_red.ADC, bins=[120, 120], norm=LogNorm(), 
               range=[[-0.5, 119.5], [0, 4400]], vmin=1, vmax=count_limit, cmap='jet')
    plt.ylabel("Charge [ADC channels]")
    plt.xlabel("Channel [a.u.]")
    plt.colorbar()
    name = ('Bus ' + str(bus) + ', ' + str(df_red.shape[0]) + ' events\n' + 
            'Wire events = ' + str(df_red[df_red.Channel < 80].shape[0]) + 
            ', Grid events = ' + str(df_red[df_red.Channel >= 80].shape[0]))
    
    #plt.grid(axis='x')
    plt.title(name)
    
def plot_PHS_buses(name, df, bus_vec, data_set, count_limit = 3000):
    fig = plt.figure()
    number_of_detectors = len(bus_vec) // 3
    fig.suptitle(name + '\n\n', x=0.5, y=1.05)
    fig.set_figheight(4 * number_of_detectors)
    fig.set_figwidth(14)
    for loc, bus in enumerate(bus_vec):
        plot_PHS(df, bus, loc, number_of_detectors, fig , count_limit)
    plt.tight_layout()
    plt.show()
    plot_path = get_plot_path(data_set) + name  + '.pdf'
    fig.savefig(plot_path)
    
# =============================================================================
# Plot 2D Histogram of Multiplicity
# =============================================================================       
    
def plot_2D_multiplicity(coincident_events, number_of_detectors, bus, loc, 
                         fig, m_range=8, count_range =  [1, 1e6], thresADC=0):
    df_clu = coincident_events[coincident_events.Bus == bus]
    df_clu = df_clu[df_clu.wADC > thresADC]
    plt.subplot(number_of_detectors,3,loc+1)
    hist, xbins, ybins, im = plt.hist2d(df_clu.wM, df_clu.gM, bins=[m_range+1, m_range+1], 
                                        range=[[0,m_range+1],[0,m_range+1]],
                                        norm=LogNorm(), vmin=count_range[0], vmax=count_range[1], 
                                        cmap = 'jet')
    tot = df_clu.shape[0]
    font_size = 50 / m_range
    for i in range(len(ybins)-1):
        for j in range(len(xbins)-1):
            if hist[j,i] > 0:
                text = plt.text(xbins[j]+0.5,ybins[i]+0.5, 
                         str(format(100*(round((hist[j,i]/tot),3)),'.1f')) + 
                         "%", color="w", ha="center", va="center", 
                         fontweight="bold", fontsize=font_size)
                text.set_path_effects([path_effects.Stroke(linewidth=1, foreground='black'),
                       path_effects.Normal()])
        
    ticks = np.arange(0,m_range+1,1)
    locs = np.arange(0.5, m_range+1.5,1)
    
    plt.xticks(locs,ticks)
    plt.yticks(locs,ticks)
    plt.xlabel("Wire Multiplicity")
    plt.ylabel("Grid Multiplicity")
    plt.colorbar()
    plt.tight_layout()
    name = 'Bus ' + str(bus) + '\n(' + str(df_clu.shape[0]) + ' events)'
    plt.title(name)

def plot_2D_multiplicity_buses(name, coincident_events, module_order, 
                               number_of_detectors, data_set, m_range = 8, 
                               count_limit = [1,1e6], thresADC=0):
    fig = plt.figure()
    name = (name + ' (Threshold: ' 
            + str(thresADC) + ' ADC channels)')
    fig.suptitle(name, x=0.5, y=1.05, fontweight="bold")
    fig.set_figheight(4*number_of_detectors)
    fig.set_figwidth(14)
    for loc, bus in enumerate(module_order):
        plot_2D_multiplicity(coincident_events, number_of_detectors, bus, loc, 
                             fig, m_range, count_limit, thresADC)

    plt.tight_layout()
    plt.show()
    plot_path = get_plot_path(data_set) + name  + '.pdf'
    fig.savefig(plot_path, bbox_inches='tight')
    

# =============================================================================
# Plot 3D Histogram of hit location
# =============================================================================  
    
def plot_all_sides_3D(name, coincident_events, bus_order, countThres, alpha, 
                      data_set, number_of_detectors):
    
    df_tot = pd.DataFrame()
    
    for i, bus in enumerate(bus_order):
        df_clu = coincident_events[coincident_events.Bus == bus]
        df_clu = df_clu[(df_clu.wCh != -1) & (df_clu.gCh != -1)]
        df_clu['wCh'] += (80 * i)
        df_tot = pd.concat([df_tot, df_clu])
    
    x = np.floor(df_tot['wCh'] / 20).astype(int)
    y = df_tot['gCh'] - 80
    z = df_tot['wCh'] % 20
    
    df_3d = pd.DataFrame()
    df_3d['x'] = x
    df_3d['y'] = y
    df_3d['z'] = z
        
    H, edges = np.histogramdd(df_3d.values, bins=(12*number_of_detectors, 40, 20), range=((0,12*number_of_detectors), 
                                             (0,40), (0,20)))

    hist = np.empty([4, H.shape[0]*H.shape[1]*H.shape[2]], dtype='int')
    loc = 0
    for i in range(0,12*number_of_detectors):
        for j in range(0,40):
            for k in range(0,20):
                if H[i,j,k] > countThres:
                    hist[0][loc] = i + 1
                    hist[1][loc] = j + 1
                    hist[2][loc] = k + 1
                    hist[3][loc] = H[i,j,k]
                    loc = loc + 1
                        
    scatter3d(hist[0][0:loc], hist[2][0:loc], hist[1][0:loc], hist[3][0:loc], countThres, data_set, alpha, 
              name, number_of_detectors)

    
def scatter3d(x,y,z, cs, countThres, data_set, alpha, name, 
              number_of_detectors, colorsMap='jet'):
    cm = plt.get_cmap(colorsMap)
   # cNorm = Normalize(vmin=min(cs), vmax=max(cs))
    scalarMap = cmx.ScalarMappable(norm=LogNorm(), cmap=cm)
    fig = plt.figure()
    #fig.set_size_inches(4.5, 5)
    name = (name + '\nLower threshold: ' 
            + str(countThres) + ' counts')
    fig.suptitle(name ,x=0.5, y=1.03, fontweight="bold")
    ax = Axes3D(fig)
    ax.scatter(x, y, z, c=scalarMap.to_rgba(cs), marker= "o", s=50, 
               alpha = alpha)
   
    ax.set_xlabel('Layer')
    ax.set_ylabel('Wire')
    ax.set_zlabel('Grid')
    
    ax.set_xticks(np.arange(0, 12*number_of_detectors + 2, step=2))
    ax.set_xticklabels(np.arange(0, 12*number_of_detectors + 2, step=2))
    ax.set_xlim([0,12*number_of_detectors])
#    
    ax.set_yticks(np.arange(0, 25, step=5))
    ax.set_yticklabels(np.arange(0, 25, step=5))
    ax.set_ylim([0,20])
#    
    ax.set_zticks(np.arange(0, 50, step=10))
    ax.set_zticklabels(np.arange(0, 50, step=10))
    ax.set_zlim([0,40])
    
    
    scalarMap.set_array(cs)
    fig.colorbar(scalarMap)
    
    plt.show()
    
    plot_path = get_plot_path(data_set) + name  + '.pdf'
    fig.savefig(plot_path, bbox_inches='tight')

# =============================================================================
# Plot 3D surface PHS
# =============================================================================  

    
def plot_3D_new(name, df, bus, data_set):    
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
  #  zlimVec =   [[0,500], [0,3000]]
    
    plt.close()
    
    fig = plt.figure()
    fig.set_size_inches(15, 6)
#    fig = plt.figure('position', [0, 0, 200, 500])

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
      #  ax.set_zlim(zlimVec[i])
    
#        ax.set_ylim([0,5000])
#        ticks = np.arange(0, 6000, step=1000)
#        ax.set_yticks(ticks)
#        ax.set_yticklabels(ticks[::-1])
        #fig.colorbar(m)
    
        plt.title(nameVec[i], x=0.5, y=1.02)
        
    plt.show()
    plot_path = get_plot_path(data_set) + name  + '.pdf'
    fig.savefig(plot_path, bbox_inches='tight')
    

# =============================================================================
# Plot ToF histogram
# =============================================================================
    
def plot_ToF_histogram(name, df, data_set, number_bins = None, rnge=None):
    fig = plt.figure()
    plt.hist(df.ToF, bins=number_bins, range=rnge)
    plt.title(name)
    plt.xlabel('ToF [TDC channels]')
    plt.ylabel('Counts  [a.u.]')
    plt.show()
    plot_path = get_plot_path(data_set) + name  + '.pdf'
    fig.savefig(plot_path, bbox_inches='tight')
    
    
    

    

# =============================================================================
# Helper Functions
# ============================================================================= 
    
def get_plot_path(data_set):
    dirname = os.path.dirname(__file__)
    folder = os.path.join(dirname, '../Plot/' + data_set + '/')
    return folder