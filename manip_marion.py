# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 14:01:20 2021

@author: PaulLeroy
"""

import os, shutil

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import tools.cc as cc

# parameters
dir_ = 'C:/DATA/lgu/processing'
bin_ = 'Manip_Marion.bin'
m3c2_params = os.path.join(dir_, 'm3c2_outCore.txt') # M3C2 parameters
rasterSpacing = 0.0005 # spacing for the core points generation
vmin = -0.003
vmax = 0.003

cloud = os.path.join(dir_, bin_)

#%% create the output directory (based on the .bin filename)

head, tail = os.path.split(cloud)
root, ext = os.path.splitext(tail)
odir = os.path.join(head, root)
print(f'output directory: {odir}')
os.makedirs(odir, exist_ok=True)

#%% transform BIN to SBF (this splits the bin file in singular files)

src = cloud
dst = os.path.join(odir, tail)
shutil.copy(src, dst)
cc.to_sbf(dst)
os.remove(dst)

# get the list of SBF files
list_ = os.listdir(odir)
list_sbf_data = [file for file in list_ if '.sbf.data' in file]
N = len(list_sbf_data)
sbf = [os.path.join(odir, root + f'_{k}.sbf') for k in range(N)]
print(f'{N} .sbf files extracted from the original .bin file')

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
    # the M3C2 distance will be used for the color of the points on the scatter plot
    c = sf[:, 6]
    XY.append(xy)
    C.append(c)

#%% ANIMATE

fig, ax = plt.subplots(figsize=(10, 10))

scat = ax.scatter(XY[0][:, 0], XY[0][:, 1], c=C[0], cmap='bwr', vmin=vmin, vmax=vmax)
cb = fig.colorbar(scat)
cb.set_label('M3C2 [m]')
ax.set_aspect('equal')
ax.grid()
ax.set_title(0)
ax.set_xlabel('[m]')
ax.set_ylabel('[m]')

def update(idx):
    scat.set_offsets(XY[idx])
    scat.set_array(C[idx])
    ax.set_title(str(idx))
    return scat, ax

anim = animation.FuncAnimation(fig, update, frames=N-1, interval=1000)

# Set up formatting for the movie files
if False:
    mp4 = os.path.join(odir, f'{root}.mp4')
    anim.save(mp4)
    print(f'movie {mp4} saved')
    
plt.show()

#%% GENERATE IMAGES

for idx in range(N-1):
    fig0, ax0 = plt.subplots(figsize=(10, 10))
    scat = ax0.scatter(XY[idx][:, 0], XY[idx][:, 1], c=C[idx], cmap='bwr', vmin=vmin, vmax=vmax)
    cb = fig0.colorbar(scat)
    cb.set_label('M3C2 [m]')
    ax0.set_aspect('equal')
    ax0.grid()
    ax0.set_title(idx)
    ax0.set_xlabel('[m]')
    ax0.set_ylabel('[m]')
    figname = os.path.join(odir, f'{root}_{idx}.png')
    plt.savefig(figname)
    print(figname)
    plt.close(fig0)
