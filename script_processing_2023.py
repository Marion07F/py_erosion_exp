# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 15:58:01 2023

@author: Marion
"""

import os
import glob
import m3c2_tools

dirGlobal = "C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare"
dir_ = "C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare/DATA"
D = "PROCESSINGerosion+"

fileVminVmax = os.path.join(dirGlobal, 'VminVmax.txt')

#Traitement des données brutes par M3C2 en incrémental (inc) et en total (tot)
#%%
m3c2_tools.execute_all_inc(dir_, dirGlobal, fileVminVmax, f'{D}')
#%%
m3c2_tools.execute_all_tot(dir_, dirGlobal, fileVminVmax, f'{D}')

#%% Renomer les fichiers sortants

#♥m3c2_tools.rename(f'C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare/{D}')

#%% Sortir les données
dir_list = glob.glob(fr'C:\Users\Benjamin\Desktop\Traitement_Cloud_Compare\{D}\*')
for root_dir in dir_list: 
    if os.path.isdir(root_dir):
        idir = os.path.join(root_dir, 'm3c2inc')
        m3c2_tools.post_processing(idir, tag="inc")
        
        idir = os.path.join(root_dir, 'm3c2tot')
        m3c2_tools.post_processing(idir, tag="tot")
