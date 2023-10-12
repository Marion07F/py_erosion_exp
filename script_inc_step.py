# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 10:22:28 2023

@author: Benjamin
"""
import glob
import os
import shutil
import tools.cc as cc

#def execute_all_inc_PdT(dir_, idir, fileVminVmax, o_name, inc)



dir_ = "C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare/DATA"
idir = r"C:\Users\Benjamin\Desktop\Traitement_Cloud_Compare\PROCESSINGerosion\DIP9067\m3c2inc"
A= glob.glob(idir + "\*_M3C2.sbf*")

# odir = r"C:\Users\Benjamin\Desktop\Traitement_Cloud_Compare\PROCESSINGerosion\DIP9067\m3c2inc\inc2"

# if os.path.isdir(odir):
#     [shutil.move(file, odir) for file in A]

#%%
inc = 2
odir = os.path.join(idir, f"inc{inc}")
os.makedirs(odir, exist_ok=True)

#%%
m3c2_params = os.path.join(dir_, 'm3c2_param.txt')
corePtsList = glob.glob(idir + "\*.bin")

sbf_list = glob.glob(idir + "\*.sbf")
results = []
N = len(sbf_list)

for idx in range(0, N-inc, inc):
    res = cc.m3c2(sbf_list[idx], sbf_list[idx+inc], m3c2_params, corePtsList[idx], fmt='SBF')
    if os.path.isdir(odir):
        shutil.move(res, odir)
        shutil.move(res + ".data", odir)
    results.append(res)
    print(f'm3c2 {idx} / {idx+1} => {res}')


