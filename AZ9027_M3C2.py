# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 09:16:04 2021

@author: PaulLeroy
"""

import os, shutil

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import tools.cc as cc

# parameters
dir_ = 'C:\DATA\lgu\processing\AZ9027_M3C2'
m3c2_params = 'C:/DATA/lgu/processing/m3c2_outCore.txt' # M3C2 parameters
head, tail = os.path.split(dir_)
odir = os.path.join(dir_, tail)
os.makedirs(odir, exist_ok=True)

vmin = -0.006
vmax = 0.000
cmap_reversed = matplotlib.cm.get_cmap('Blues_r')

#%% list the data files, replace spaces by '_'
results = os.listdir(dir_)
ply = [file for file in os.listdir(dir_) if '.ply' in file]
N = len(ply)
for idx in range(N):
    name = ply[idx]
    newName = name.replace(' ', '_')
    src = os.path.join(dir_, name)
    dst = os.path.join(dir_, newName)
    shutil.move(src, dst)

#%% convert files to sbf
for idx in range(N):
    filename = os.path.join(dir_, ply[idx])
    print(filename)
    cc.to_sbf(filename)

#%% OPEN ALL M3C2 DIST

sbf = os.listdir(dir_)
sbf = [file for file in sbf if '.sbf' in file]
sbf = [file for file in sbf if '.sbf.data' not in file]

XY = []
C = []
dict_ = {}
for idx in range(N):
    pc, sf, config = cc.read_sbf(os.path.join(dir_, sbf[idx]))
    # x and y coordinates will be used to place the points on the scatter plot
    xy = pc[:, 0:2]
    xy[:, 0] = xy[:, 0] - np.mean(xy[:, 0])  # remove mean x
    xy[:, 1] = xy[:, 1] - np.mean(xy[:, 1])  # remove mean y
    # the M3C2 distance will be used for the color of the points on the scatter plot
    c = sf[:, 2]
    XY.append(xy)
    C.append(c)

#%% GENERATE IMAGES

for idx in range(N):
    fig0, ax0 = plt.subplots(figsize=(10, 10))
    scat = ax0.scatter(XY[idx][:, 0], XY[idx][:, 1], c=C[idx], cmap=cmap_reversed, vmin=vmin, vmax=vmax)
    cb = fig0.colorbar(scat)
    cb.set_label('M3C2 [m]')
    ax0.set_aspect('equal')
    ax0.grid()
    fhead, ftail = os.path.split(sbf[idx])
    froot, fext = os.path.splitext(ftail)
    title = froot.split('_output_scale')[0]
    ax0.set_title(title)
    ax0.set_xlabel('[m]')
    ax0.set_ylabel('[m]')
    figname = os.path.join(odir, f'{title}.png')
    plt.savefig(figname)
    print(figname)
    plt.close(fig0)

