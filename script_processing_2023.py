# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 15:58:01 2023

@author: Benjamin
"""

import os

import m3c2_tools

dirGlobal = "C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare"
dir_ = "C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare/DATA"

fileVminVmax = os.path.join(dirGlobal, 'VminVmax.txt')

m3c2_tools.execute_all(dir_, dirGlobal, fileVminVmax, 'DATA3')

#%%
idir = r'C:\Users\Benjamin\Desktop\Traitement_Cloud_Compare\DATA3\REF03\m3c2inc'
m3c2_tools.post_processing(idir, tag="inc")