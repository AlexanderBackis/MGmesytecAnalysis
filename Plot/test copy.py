#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 09:21:08 2018

@author: alexanderbackis
"""

import matplotlib.pyplot as plt
import numpy as np

X = np.arange(0,201,1)
Y_1 = np.arange(0,402,2)
Y_2 = np.arange(0,804,4)

plt.figure()

plt.plot(X,Y_1)
plt.xlabel('x')
plt.ylabel('y')
plt.ylim([0,800])

input('Type Enter when done')
input('Type Enter when done')
print('hajahja')
input('Type Enter when done')

plt.figure()
plt.plot(X,Y_2)
plt.xlabel('x')
plt.ylabel('y')
plt.ylim([0,800])

input('Type Enter when done')