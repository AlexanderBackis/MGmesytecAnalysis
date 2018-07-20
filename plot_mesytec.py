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
# Helper Functions
# ============================================================================= 
    
def get_plot_path():
    dirname = os.path.dirname(__file__)
    folder = os.path.join(dirname, '../Plot/')
    return folder