# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 14:09:18 2022

@author: Marion Fournereau
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import glob
import os
import subprocess
import tools.cc as cc
import tools.common_ple as ple
import json

## Paramètres
# Définir l'index 
idx_Npoints_cloud1 = 0
idx_Npoints_cloud2 = 1
idx_STD_cloud1 = 2
idx_STD_cloud2 = 3
idx_significant_change = 4
idx_distance_uncertainty = 5
idx_M3C2_distance = 6
  
DOSSIER_M3C2 = 'inc' # ou tot si M3C2 disque à disque initial

dirGlobal = "C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare"#"C:/Users/phili/OneDrive/Desktop/Marion/M2/Traitement_Cloud_Compare"
dirPROCESSING = "C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare/PROCESSINGerosion+"

    
nomManip=os.listdir(dirPROCESSING)

ManipList = []
SaveList = []
SaveFich = []
SaveFig = []

for idx in range(len(nomManip)):#len(nomManip)
      ManipList.append(os.path.join(dirPROCESSING + '/' + nomManip[idx]) + '/' + f'm3c2{DOSSIER_M3C2}')
      if not os.path.exists(os.path.join(dirGlobal +  '/XY') + '/' + f'{nomManip[idx]}TXT{DOSSIER_M3C2}'):
          os.makedirs(os.path.join(dirGlobal + '/XY') + '/' + f'{nomManip[idx]}TXT{DOSSIER_M3C2}/')
      SaveFich.append(os.path.join(dirGlobal + '/XY')+ '/' + f'{nomManip[idx]}TXT{DOSSIER_M3C2}/')
      SaveList.append(os.path.join(dirPROCESSING + '/' + nomManip[idx]) + '/' + f'm3c2{DOSSIER_M3C2}')      
# Mise en place des boucles pour faire tourner le code pour chaque manip        
for idx in range(len(ManipList)):
    filename = glob.glob(os.path.join(ManipList[idx], '*M3C2.sbf'))
    NptsI = []
    NptsF = []
    M3C2tot = []

    for idx2 in range(len(filename)):#len(filename)
        sbf1 = os.path.join(filename[idx2])
        
        head, tail = os.path.split(sbf1)
        root, ext = os.path.splitext(tail)
        destFile = os.path.join(SaveList[idx], root)
        
        pc, sf, config = cc.read_sbf(sbf1, verbose=False)
        M3C2I = sf[:,6]
        NptsI.append(len(M3C2I)) # Récupère le nombre de points initiaux dans chaque manip 
 
        # x and y coordinates will be used to place the points on the scatter plot
        xy = pc[:, 0:2]

        xy[:, 0] = xy[:, 0] - np.mean(xy[:, 0])  # remove mean x
        xy[:, 1] = xy[:, 1] - np.mean(xy[:, 1])  # remove mean y
        # the M3C2 distance will be used for the color of the points on the scatter plot

        np.savetxt(f'{SaveFich[idx]}{root}{DOSSIER_M3C2}XY.txt',xy,fmt='%1.6f')

        
        
   
        