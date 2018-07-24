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

# =============================================================================
# Plot 2D Histogram of collected charge, individual channel
# =============================================================================

def charge_scatter(df, bus, Channel, maxWM, maxGM):
    if Channel < 80:
        df_red = df[(df.wCh == Channel) & (df.Bus == bus) &
                    (df.wM <= maxWM) & (df.gM <= maxGM)]
    else:
        df_red = df[(df.gCh == Channel) & (df.Bus == bus) &
                    (df.wM <= maxWM) & (df.gM <= maxGM)]
    
    fig = plt.figure()
    name = ('Scatter map collected charge, Channel ' + str(Channel) 
            + ', Bus ' + str(bus) + '\n' 
            + '(Max wire multiplicity: ' + str(maxWM) + 
            ', max grid multiplicity: ' + str(maxGM) + ')') 
    
    plt.title(name)
    plt.hist2d(df_red.wADC, df_red.gADC, bins=[200, 200], 
               norm=LogNorm(),range=[[0, 5000], [0, 5000]], vmin=1, vmax=10000,
               cmap='jet')
    plt.xlabel("wADC [ADC channels]")
    plt.ylabel("gADC [ADC channels]")
    plt.colorbar()
    plt.show()
    plot_path = get_plot_path() + name  + '.pdf'
    fig.savefig(plot_path, bbox_inches='tight')
    
    
        


# =============================================================================
# Plot 2D Histogram of Hit Position with a specific side
# =============================================================================
    
def plot_2D_side_1(bus_vec, df, fig):
    name = 'Front view'
    df_tot = pd.DataFrame()
    
    for i, bus in enumerate(bus_vec):
        df_clu = df[df.Bus == bus]
        df_clu = df_clu[(df_clu.wCh != -1) & (df_clu.gCh != -1)]
        df_clu['wCh'] += (80 * i)
        df_tot = pd.concat([df_tot, df_clu])        
    
    plt.hist2d(df_tot.wCh, df_tot.gCh, bins=[12, 40], 
               range=[[0,240],[80,120]], norm=LogNorm(), vmin=100, vmax=30000,
               cmap = 'jet')
    
    loc = np.arange(0, 260, step=40)
    ticks = np.arange(0, 14, step = 2)
    plt.xticks(loc, ticks)
    
    loc = np.arange(80, 130, step=10)
    ticks = np.arange(0, 50, step=10)
    plt.yticks(loc, ticks)
    
    plt.xlabel("Layer")
    plt.ylabel("Grid")
    plt.colorbar()
    plt.title(name)
    
def plot_2D_side_2(bus_vec, df, fig):
    name = 'Top view'
    df_tot = pd.DataFrame()
    
    for i, bus in enumerate(bus_vec):
        df_clu = df[df.Bus == bus]
        df_clu = df_clu[(df_clu.wCh != -1) & (df_clu.gCh != -1)]
        df_clu['wCh'] += (80 * i)
        df_tot = pd.concat([df_tot, df_clu])  
        
    plt.hist2d(np.floor(df_tot['wCh'] / 20).astype(int), df_tot['wCh'] % 20, 
               bins=[12, 20], range=[[0,12],[0,20]], norm=LogNorm(), vmin=100, 
               vmax=30000, cmap = 'jet')
    
    loc = np.arange(0, 25, step=5)
    plt.yticks(loc, loc)
    
    plt.xlabel("Layer")
    plt.ylabel("Wire")
    plt.colorbar()
    plt.title(name)
    
def plot_2D_side_3(bus_vec, df, fig):
    name = 'Side view'
    df_tot = pd.DataFrame()
    
    for i, bus in enumerate(bus_vec):
        df_clu = df[df.Bus == bus]
        df_clu = df_clu[(df_clu.wCh != -1) & (df_clu.gCh != -1)]
        df_tot = pd.concat([df_tot, df_clu])
    
        
    plt.hist2d(df_tot['wCh'] % 20, df_tot['gCh'],
               bins=[20, 40], range=[[0,20],[80,120]], norm=LogNorm(), 
               vmin=100, vmax=30000, cmap = 'jet')
    
    
    loc = np.arange(80, 130, step=10)
    ticks = np.arange(0, 50, step=10)
    plt.yticks(loc, ticks)
    
    plt.xlabel("Wire")
    plt.ylabel("Grid")
    plt.colorbar()
    plt.title(name)
    
def plot_all_sides(bus_vec, df):
    fig = plt.figure()
    
    fig.set_figheight(4)
    fig.set_figwidth(14)
    
    plt.subplot(1,3,1)
    plot_2D_side_1(bus_vec, df, fig)
    plt.subplot(1,3,2)
    plot_2D_side_2(bus_vec, df, fig)
    plt.subplot(1,3,3)
    plot_2D_side_3(bus_vec, df, fig)
    
    name = ('2D Histogram of hit position, different perspectives')
    fig.suptitle(name, x=0.5, y=1.05, fontweight="bold")
    plt.tight_layout()
    plt.show()
    plot_path = get_plot_path() + name  + '.pdf'
    fig.savefig(plot_path, bbox_inches='tight')


#def plot_perspectives(bus_order, df):
#    fig = plt.figure()
#    fig.set_figheight(4)
#    fig.set_figwidth(14)
#    df = df[(df.wCh != -1) & (df.gCh != -1)]
#    df_front_tot 
#    df_top_tot
#    df
#    for i, bus in enumerate(bus_order):
#        df_front = df[df.Bus == bus]
#        df_front['wCh'] += (80 * i)
#        df_front = 
    
    
# =============================================================================
# Plot 2D Pulse Height Spectrum, Channel VS Charge
# =============================================================================

def plot_PHS(df, bus, fig):
    df_red = df[df.Bus == bus]
    plt.subplot(1,3,bus+1)
    plt.hist2d(df_red.Channel, df_red.ADC, bins=[120, 120], norm=LogNorm(), 
               range=[[0, 120], [0, 4400]], vmin=1, vmax=3000, cmap='viridis')
    plt.ylabel("Charge [ADC channels]")
    plt.xlabel("Channel [a.u.]")
    plt.colorbar()
    name = 'Bus ' + str(bus)
    plt.title(name)
    
def plot_PHS_buses(df, bus_vec):
    fig = plt.figure()
    fig.suptitle('2D-Histogram of Channel vs Charge',x=0.5,
                 y=1)
    fig.set_figheight(4)
    fig.set_figwidth(14)
    for bus in bus_vec:
        plot_PHS(df, bus, fig)
    name = '2D-Histogram of Channel vs Charge all buses'
    plt.tight_layout()
    plt.show()
    plot_path = get_plot_path() + name  + '.pdf'
    fig.savefig(plot_path)
    

# =============================================================================
# Helper Functions
# ============================================================================= 
    
def get_plot_path():
    dirname = os.path.dirname(__file__)
    folder = os.path.join(dirname, '../Plot/')
    return folder