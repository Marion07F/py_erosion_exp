# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 14:01:20 2021

@author: PaulLeroy
"""

import os, shutil

import numpy as np
import matplotlib.pyplot as plt
import matplotlib

import tools.cc as cc

# parameters
dir_ = 'C:/DATA/lgu/processing'
bin_ = 'SPA4040.bin'
m3c2_params = os.path.join(dir_, 'm3c2_outCore.txt') # M3C2 parameters
rasterSpacing = 0.0005 # spacing for the core points generation

vmin = -0.0005
vmax = 0.000
cmap_reversed = matplotlib.cm.get_cmap('Blues_r')

cloud = os.path.join(dir_, bin_)

#%% create the output directory (based on the .bin filename)

head, tail = os.path.split(cloud)
root, ext = os.path.splitext(tail)
odir = os.path.join(head, root)
print(f'output directory: {odir}')
os.makedirs(odir, exist_ok=True)
figDir = os.path.join(odir, root)
os.makedirs(figDir, exist_ok=True)
print(f'figures directory: {figDir}')

#%% transform BIN to SBF (this splits the bin file in singular files)

src = cloud
dst = os.path.join(odir, tail)
shutil.copy(src, dst)
cc.to_sbf(dst)
os.remove(dst)

# get the list of SBF files
list_ = os.listdir(odir)
list_sbf_data = [file for file in list_ if '.sbf.data' in file]
N = len(list_sbf_data) - 1
sbf = [os.path.join(odir, root + f'_{k}.sbf') for k in range(N)]
print(f'{N} .sbf files extracted from the original .bin file (!!! LAST CLOUD REMOVE !!!)')

#%% BUILD CORE POINTS FOR ALL CLOUDS (except the last one)

print('Build core points:')
print('   1. best fit plane')
print('   2. transform cloud')
print('   3. rasterize')
print('   4. inverse transformation')

corePtsList = []

for idx in range(N-1):
    filename = sbf[idx]
    print(f'Compute core points from: {filename}')
    
    # BEST FIT PLANE
    bestFitPlane, outputMatrix = cc.best_fit_plane(filename)
    # get the transformation from the txt file
    transformation = cc.get_orientation_matrix(outputMatrix)
    invTransformation = np.linalg.inv(transformation)
    transfile = os.path.join(odir, f'transformation_{idx}.txt')
    invTransfile = os.path.join(odir, f'inverseTransformation_{idx}.txt')
    np.savetxt(transfile, transformation, fmt='%.12f')
    np.savetxt(invTransfile, invTransformation, fmt='%.12f')
    os.remove(bestFitPlane) # remove temporary cloud
    os.remove(outputMatrix) # remove temporary txt file
    
    # APPLY TRANSFORMATION TO ORIGINAL CLOUD
    transformed = cc.apply_trans_alt(filename, transfile)
    
    # CREATE RASTER
    raster = cc.rasterize(transformed, rasterSpacing)
    os.remove(transformed) # remove temporary cloud
    
    # APPLY INVERSE TRANSFORMATION TO RASTER
    corePts = cc.apply_trans_alt(raster, invTransfile)
    os.remove(raster) # remove temporary cloud
    
    corePtsList.append(corePts)
    
#%% LAUNCH M3C2 FOR ALL CLOUDS (except the last one)

results = []
for idx in range(N-1):
    res = cc.m3c2(sbf[idx], sbf[idx+1], m3c2_params, corePtsList[idx], fmt='SBF')
    results.append(res)
    print(f'm3c2 {idx} / {idx+1} => {res}')

#%% OPEN ALL M3C2 DIST

XY = []
C = []
for idx in range(N-1):
    pc, sf, config = cc.read_sbf(results[idx])
    # x and y coordinates will be used to place the points on the scatter plot
    xy = pc[:, 0:2]
    xy[:, 0] = xy[:, 0] - np.mean(xy[:, 0])  # remove mean x
    xy[:, 1] = xy[:, 1] - np.mean(xy[:, 1])  # remove mean y
    # the M3C2 distance will be used for the color of the points on the scatter plot
    c = sf[:, 6]
    XY.append(xy)
    C.append(c)

#%% GENERATE IMAGES

for idx in range(N-1):
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
    figname = os.path.join(figDir, f'{title}.png')
    plt.savefig(figname)
    print(figname)
    plt.close(fig0)