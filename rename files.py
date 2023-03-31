# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 09:26:55 2023

@author: Utilisateur
"""
import re
import os


def rename(dir_path):
    dir = os.scandir(dir_path)
    
    for file in dir :
        if re.match("[A-z0-9]*_[0-9][_.]",file.name):
            idx = re.search("_[0-9]",file.name).start() + 1
            
            file_name = file.name[:idx] + str(0) + file.name[idx:]
            new_file_path = os.path.join(dir_path, file_name)

            os.rename(file.path,new_file_path)
        
        if file.is_dir():
            rename(file.path)
            
rename("C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare/DATA2")
rename("C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare/PROCESSINGerosion+")
#rename("C:/Users/Benjamin/Desktop/Tests_CANUPO/BIN/")