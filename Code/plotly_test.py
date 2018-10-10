#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 15:33:23 2018

@author: alexanderbackis
"""

import cluster as clu
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cmx
import matplotlib.patheffects as path_effects
import plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.io as pio

py.offline.init_notebook_mode(connected=True)


from plotly.tools import make_subplots

fig = make_subplots(1, 2)

fig.add_scatter(y=[1, 3, 2], row=1, col=1, visible=True)
fig.add_scatter(y=[3, 1, 1.5], row=1, col=1, visible='legendonly')
fig.add_scatter(y=[2, 2, 1], row=1, col=1, visible='legendonly')
fig.add_scatter(y=[1, 3, 2], row=1, col=2, visible=True)
fig.add_scatter(y=[1.5, 2, 2.5], row=1, col=2, visible='legendonly')
fig.add_scatter(y=[2.5, 1.2, 2.9], row=1, col=2, visible='legendonly')

steps = []
for i in range(3):
    step = dict(
        method = 'restyle',  
        args = ['visible', ['legendonly'] * len(fig.data)],
    )
    step['args'][1][i] = True
    step['args'][1][i+3] = True
    steps.append(step)

sliders = [dict(
    steps = steps,
)]

fig.layout.sliders = sliders

go.FigureWidget(fig)