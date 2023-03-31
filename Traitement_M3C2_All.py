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

#Definir la police et la taille des textes des figures
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 22

## Paramètres
# Définir l'index 
idx_Npoints_cloud1 = 0
idx_Npoints_cloud2 = 1
idx_STD_cloud1 = 2
idx_STD_cloud2 = 3
idx_significant_change = 4
idx_distance_uncertainty = 5
idx_M3C2_distance = 6

cmap_reversed = matplotlib.cm.get_cmap('Blues')
    
DOSSIER_M3C2 = 'inc' # ou tot si M3C2 disque à disque initial

dirGlobal = "C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare"#"C:/Users/phili/OneDrive/Desktop/Marion/M2/Traitement_Cloud_Compare"
dirDATA = "C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare/DATA2"#"C:/Users/phili/OneDrive/Desktop/Marion/M2/Traitement_Cloud_Compare/DATA"
dirPROCESSING = "C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare/PROCESSINGerosion+"#"C:/Users/phili/OneDrive/Desktop/Marion/M2/Traitement_Cloud_Compare/PROCESSINGerosion+tmp"
if not os.path.exists(os.path.join(dirGlobal, 'PROCESSINGerosion+')):
    os.makedirs(os.path.join(dirGlobal, 'PROCESSINGerosion+'))
    
nomManip=os.listdir(dirDATA)

ManipList = []
SaveList = []
SaveFich = []
SaveFig = []

fileVminVmax = os.path.join(dirGlobal, 'VminVmax.txt')
with open(fileVminVmax) as f:
    datasVminVmaxString = f.read()
datasVminVmax = json.loads(datasVminVmaxString)

for idx in range(len(nomManip)):#len(nomManip)
    ManipList.append(os.path.join(dirDATA, nomManip[idx], f'm3c2{DOSSIER_M3C2}'))
    
    SaveList.append(os.path.join(dirPROCESSING + '/' + nomManip[idx]) + '/' + f'm3c2{DOSSIER_M3C2}')
    if not os.path.exists(os.path.join(dirPROCESSING + '/' + nomManip[idx]) + '/' + f'm3c2{DOSSIER_M3C2}'):
        os.makedirs(os.path.join(dirPROCESSING + '/' + nomManip[idx]) + '/' + f'm3c2{DOSSIER_M3C2}')
        
    SaveFich.append(os.path.join(dirPROCESSING + '/' + nomManip[idx]))
    if not os.path.exists(os.path.join(dirPROCESSING + '/' + nomManip[idx])):
        os.makedirs(os.path.join(dirPROCESSING + '/' + nomManip[idx]))
        
    SaveFig.append(os.path.join(dirPROCESSING + '/' + nomManip[idx]) + '/' + f'm3c2{DOSSIER_M3C2}_FIG')
    if not os.path.exists(os.path.join(dirPROCESSING + '/' + nomManip[idx]) + '/' + f'm3c2{DOSSIER_M3C2}_FIG'):
        os.makedirs(os.path.join(dirPROCESSING + '/' + nomManip[idx]) + '/' + f'm3c2{DOSSIER_M3C2}_FIG')
        
# Mise en place des boucles pour faire tourner le code pour chaque manip        
for idx in range(len(ManipList)):
    filename = glob.glob(os.path.join(ManipList[idx], '*M3C2.sbf'))
    NptsI = []
    NptsF = []
    M3C2tot = []
    vmin = datasVminVmax[nomManip[idx]]["vmin"]
    vmax = datasVminVmax[nomManip[idx]]["vmax"]
    for idx2 in range(len(filename)):
        sbf1 = os.path.join(filename[idx2])
        
        head, tail = os.path.split(sbf1)
        root, ext = os.path.splitext(tail)
        destFile = os.path.join(SaveList[idx], root)
        
        pc, sf, config = cc.read_sbf(sbf1, verbose=False)
        M3C2I = sf[:,6]
        NptsI.append(len(M3C2I)) # Récupère le nombre de points initiaux dans chaque manip 
 
        # Lance la commande depuis cloud compare pour faire une selection des points du nuage en gardant uniquement les points significatifs 
        cmd = f"CloudCompare.exe -SILENT -o {sbf1} -AUTO_SAVE OFF -SET_ACTIVE_SF {idx_M3C2_distance} -FILTER_SF MIN MAX -SAVE_CLOUDS FILE {destFile}"
        # Permet d'afficher les details du process cloud compare dans la console de façon propre
        ple.exe(cmd, debug=True) 
        out = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
        
        cc.to_sbf(destFile +'.bin') # Converti le fichier .bin obtenu en fichier .sbf
        
        sbf2 = os.path.join(destFile + '.sbf')
        pc2, sf2, config2 = cc.read_sbf(sbf2, verbose=False)
        M3C2F = -sf2[:,6] #Erosion positive
        NptsF.append(len(M3C2F))
        
        df = pd.DataFrame(M3C2F)
        sums = df.sum()
        M3C2tot.append(int(round(sums))) # Récupère le nombre de points finaux dans chaque manip 
        
        # Ecrit dans un fichier texte les valeurs de M3C2 pour chaque manip
        with open(str(SaveFich[idx]) + '//' +  f"{root}{DOSSIER_M3C2}.txt", "w") as f:
            f.write('#M3C2' + '\n')
            for item in M3C2F:
                    f.write(f'{item}\n')
        f.close()
        
        # x and y coordinates will be used to place the points on the scatter plot
        xy = pc[:, 0:2]
        xy2 = pc2[:, 0:2]
        xy2[:, 0] = xy2[:, 0] - np.mean(xy[:, 0])  # remove mean x
        xy2[:, 1] = xy2[:, 1] - np.mean(xy[:, 1])  # remove mean y
        # the M3C2 distance will be used for the color of the points on the scatter plot
        c = -sf2[:, 6] #Erosion positive

        # Créee la figure pour chaque manip du disque M3C2 filtré
        fig0, ax0 = plt.subplots(figsize=(7, 7))
        scat = ax0.scatter(xy2[:, 0], xy2[:, 1], s=1.5, c=c, cmap=cmap_reversed, vmin=vmax, vmax=-vmin)
        cb = fig0.colorbar(scat,fraction=0.046, pad=0.04)
        cb.set_label('Diff topo [mm]')

        ax0.set_aspect('equal')
        ax0.grid()
        plt.xlim(-85, 85)
        plt.ylim(-85, 85)
        ax0.set_title(f'{root}',fontsize=17)
        ax0.set_xlabel('[mm]')
        ax0.set_ylabel('[mm]')
        #plt.xticks(fontsize=18,family='Times New Roman')
       # plt.yticks(fontsize=18,family='Times New Roman')
        figname = os.path.join(SaveFig[idx]+ '/'+ f'{root}.png')
        plt.savefig(figname, dpi=300, bbox_inches='tight')
        print(figname)
        plt.close(fig0)
        
        
        
     #%%
    # Crée un fichier texte pour rentrer le nombre de points initial, final et la valeur de la somme des M3C2 (totale ou incrémentale) 
    with open(str(SaveFich[idx]) +  '//' +f"{nomManip[idx]}_M3C2{DOSSIER_M3C2}_all.txt", "w") as f:
        f.write("#Nombre de points initial" + '\n')
        for item in NptsI:
                f.write(f'{item}' + '\t')
        f.write('\n') 
        f.write("#Nombre de points final" + '\n') 
        for item in NptsF:
                f.write(f'{item}' + '\t')
        f.write('\n') 
        f.write('#Somme M3C2' + '\n')
        for item in M3C2tot:
                f.write(f'{item}' + '\t')
        f.close()   

   
        