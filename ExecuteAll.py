# -*- coding: utf-8 -*-
# """
# Created on Mon Jun  7 14:01:20 2021

# @author: PaulLeroy
# @modified by: Marion Fournereau
# """


import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path
import os, shutil
import tools.cc as cc
import json

# Parameters
dirGlobal = "C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare"#"C:/Users/phili/OneDrive/Desktop/Marion/M2/Traitement_Cloud_Compare"
dir_ = "C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare/DATA"#'C:/Users/phili/OneDrive/Desktop/Marion/M2/Traitement_Cloud_Compare/DATAtmp'
#dir_ = 'C:/Users/Utilisateur/Desktop/Traitement_Cloud_Compare/DATA'
dir_2 = "C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare/DATA2"
if not os.path.exists(os.path.join(dirGlobal, 'DATA2')):
    os.makedirs(os.path.join(dirGlobal, 'DATA2'))
ManipList = []

fileVminVmax = os.path.join(dirGlobal, 'VminVmax.txt')
with open(fileVminVmax) as f:
    datasVminVmaxString = f.read()
    
datasVminVmax = json.loads(datasVminVmaxString)

## Mise en place de la boucle pour faire tourner le code pour chaque manip 
pathlist = Path(dir_).glob('./*.bin')

for path in pathlist:
    ManipList.append(path)
    
for Manip in ManipList:
    bin_ = os.path.basename(Manip)
    
    m3c2_params = os.path.join(dir_, 'm3c2_param.txt') # M3C2 parameters
    rasterSpacing = 1 # spacing for the core points generation
    
    vmin = datasVminVmax[Manip.stem]["vmin"]
    vmax = datasVminVmax[Manip.stem]["vmax"]
    cmap_reversed = matplotlib.cm.get_cmap('Blues_r')
        
    cloud = os.path.join(dir_, bin_)
        
        #%% create the output directory (based on the .bin filename)
        
    head, tail = os.path.split(cloud)
    root, ext = os.path.splitext(tail)
    odir = os.path.join(dir_2, root)
    print(f'output directory: {odir}')
    os.makedirs(odir, exist_ok=True)
    
    m3c2incDir = os.path.join(odir, "m3c2inc")
    os.makedirs(m3c2incDir, exist_ok=True)
    print(f'm3c2inc directory: {m3c2incDir}')
    m3c2incFigDir = os.path.join(odir, "m3c2incFig")
    os.makedirs(m3c2incFigDir, exist_ok=True)
    print(f'm3c2incFig directory: {m3c2incFigDir}')
        #%% transform BIN to SBF (this splits the bin file in singular files)
        
    src = cloud
    dst = os.path.join(m3c2incDir, tail)
    shutil.copy(src, dst)
    cc.to_sbf(dst)
    os.remove(dst)
        
    # get the list of SBF files
    list_ = os.listdir(m3c2incDir)
    list_sbf_data = [file for file in list_ if '.sbf.data' in file]
    N = len(list_sbf_data) 
    sbf = [os.path.join(m3c2incDir, root + f'_{k}.sbf') for k in range(N)]
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
            transfile = os.path.join(m3c2incDir, f'transformation_{idx}.txt')
            invTransfile = os.path.join(m3c2incDir, f'inverseTransformation_{idx}.txt')
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
            scat = ax0.scatter(XY[idx][:, 0], XY[idx][:, 1], s=2, c=C[idx], cmap=cmap_reversed, vmin=vmin, vmax=vmax)
            cb = fig0.colorbar(scat)
            cb.set_label('M3C2 [mm]')
            ax0.set_aspect('equal')
            ax0.grid()
            plt.xlim(-85, 85)
            plt.ylim(-85, 85)
            fhead, ftail = os.path.split(sbf[idx])
            froot, fext = os.path.splitext(ftail)
            title = froot.split('_output_scale')[0]
            ax0.set_title(title)
            ax0.set_xlabel('[mm]')
            ax0.set_ylabel('[mm]')
            figname = os.path.join(m3c2incFigDir, f'{title}.png')
            plt.savefig(figname, dpi=300, bbox_inches='tight')
            print(figname)
            plt.close(fig0)