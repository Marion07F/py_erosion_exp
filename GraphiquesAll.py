# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 15:45:38 2022

@author: Marion Fournereau
"""
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import mpl_axes_aligner as al

# Paramètres 
#Definir la police et la taille des textes des figures
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 18
plt.rcParams["font.weight"]= "light"
dirPROCESSING = "C:/Users/phili/OneDrive/Desktop/Marion/M2/Traitement_Cloud_Compare/PROCESSINGerosion+"
dirBALANCE = "C:/Users/phili/OneDrive/Desktop/Marion/M2/Graphs"

nomManip=os.listdir(dirPROCESSING)
DOSSIER_M3C2 = 'inc' # ou tot si M3C2 disque à disque initial

EM3C2 = 0.1
Epoids = 4

ManipList = []
SaveFich = []

# Mise en place des boucles pour faire tourner le code pour chaque manip
for idx in range(len(nomManip)):
    ManipList.append(os.path.join(dirPROCESSING + '/' + nomManip[idx]))
    
    SaveFich.append(os.path.join(dirPROCESSING + '/' + nomManip[idx] + '/Figures'))
    if not os.path.exists(os.path.join(dirPROCESSING + '/' + nomManip[idx] + '/Figures')):
        os.makedirs(os.path.join(dirPROCESSING + '/' + nomManip[idx] + '/Figures'))
        
for idx in range(len(ManipList)): #len(ManipList)
    filenames = glob.glob(os.path.join(ManipList[idx], f'*M3C2{DOSSIER_M3C2}.txt'))
    filenamestot = glob.glob(os.path.join(ManipList[idx], '*M3C2tot_all.txt'))
    
# Crée les histogrammes
    for idx2 in range(len(filenames)):  
        print(filenames[idx2])
         
        Fichier = open(filenames[idx2], "r")
        Fichier.readline()
        Valeurs = list(map(float,Fichier.readlines()))
        Fichier.close()
        plt.figure(0)
        num_bins = 40
        n, bins, patches = plt.hist(Valeurs, num_bins,edgecolor = "black", facecolor='mediumslateblue', alpha=0.5)

        plt.xlabel('Diff topo [mm]')
        plt.ylabel('N')
        
        head, tail = os.path.split(filenames[idx2])
        root, ext = os.path.splitext(tail)
        save =  f"{SaveFich[idx]}/Hist_{root}"
        plt.savefig(f"{save}.pdf",
                      dpi=300, 
                      format='pdf',
                      bbox_inches='tight')
        plt.show()
#%%
## Crée les graphiques Balances/M3C2        
    Fichiertot = open(' '.join(filenamestot), "r")
    Fichiertot.readline()
    Fichiertot.readline()
    Fichiertot.readline()
    NptsF = list(map(float,Fichiertot.readline().strip().split('\t')))
    Fichiertot.readline()
        
    Valeurstot = list(map(float,Fichiertot.readline().strip().split('\t')))
    Fichiertot.close()
    
    Fichierpds = open(dirBALANCE+f"/{nomManip[idx]}.txt")
    Temps = list(map(int, Fichierpds.readline().split(",")))
    Poids = list(map(int, Fichierpds.readline().split(",")))
    Fichierpds.close()
    
    IncertResultV = [x * EM3C2 for x in NptsF]    
    IncertResultP = [x * Epoids for x in Poids]

# Créée la liste de valeurs de temps pour les valeurs M3C2
    TempsM3C2 = []
    TempsAll = []
    TempsAll.append(Temps[0]-2)
    if len(Valeurstot)==len(Poids) :
        TempsM3C2 = Temps
    else :
        TempsM3C2 = (TempsAll + Temps)

    
# Créee les valeurs normalisées pour M3C2 et Balance ainsi que pour leurs incertitudes
    Valeurstottmp = [(i - min(Valeurstot)) for i in Valeurstot] 
    #Valeurstot=[x * (-1) for x in Valeurstot]    
    ValeurstotNorm = [(i/max(Valeurstottmp)) for i in Valeurstottmp]
    Poids=[x * (-1) for x in Poids]
    PoidsNorm = [(i - min(Poids))/(max(Poids)-min(Poids)) for i in Poids]
    
    IncertVNorm =  [(i/max(Valeurstot)) for i in IncertResultV]    
    IncertPNorm = Epoids/(max([(i - min(Poids)) for i in Poids]))
    
# Variables pour la création du graphique        
    xValues = TempsM3C2
    yValues = ValeurstotNorm
    xErrorValues = ([1/60]*(len(Valeurstot))) # Incertitude sur TempsM3C2
    yErrorValues = IncertVNorm                # Incertitude sur la valeurs des données M3C2

    x2Values = Temps 
    y2Values = PoidsNorm
    x2ErrorValues = ([1/60]*(len(Temps)))     # Incertitude sur Temps
    y2ErrorValues = IncertPNorm               # Incertitude sur la valeurs des données de poids de la balance

# Création du graphique
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax2 = ax1.twinx()
    ax1.plot(xValues, yValues, 'blue')
    ax1.errorbar(xValues, yValues, xerr = xErrorValues, yerr = yErrorValues, fmt = 'none',elinewidth = 1, capsize = 3, ecolor = 'blue', zorder = 1)
    ax2.plot(x2Values, y2Values, 'red')
    ax2.errorbar(x2Values, y2Values, xerr = x2ErrorValues, yerr = y2ErrorValues, fmt = 'none',elinewidth = 1, capsize = 3, ecolor = 'red', zorder = 1)
    ax1.set_xlabel('Temps (min)')
    ax1.set_ylabel('M3C2 (-)', fontsize=13, color='b')
    ax2.set_ylabel('Poids pesé (-)', fontsize=13, color='r')
    plt.title(f'{nomManip[idx]}', fontsize=14)
    al.align.yaxes(ax1, 0, ax2, 0, 0.15)
    al.align.yaxes(ax1, 1, ax2, 1, 0.85)
    
# Enregistrement des graphiques dans le dossier Figure de chaque manip   
    head, tail = os.path.split(' '.join(filenamestot))
    root, ext = os.path.splitext(tail)
    save =  f"{SaveFich[idx]}/plot_{root}"
    # plt.savefig(f"{save}.png",
    #             dpi=300, 
    #             format='png',
    #             bbox_inches='tight')  
    plt.show()
    
# Calcul des taux d'érosion par differentiel   
    Poids=[x * (-1) for x in Poids] 
    Valeurstot=[x * (-1) for x in Valeurstot] 
    #ValeurstotS = np.divide(Valeurstot,NptsF)
    DM3C2 = np.diff(Valeurstot)
    DPoids = np.diff(Poids)
    DTempsM3C2 = np.diff(TempsM3C2)
    DTemps = np.diff(Temps)
   
    VitesseM3C2 = DM3C2/DTempsM3C2      
    VitessePoids = DPoids/DTemps
        
# Variables pour la création du graphique
    xValues = TempsM3C2[1:]
    xErrorValues = 0
    yValues = VitesseM3C2
    yErrorValues = IncertResultV[1:]
    x2Values = Temps[1:]
    x2ErrorValues = 0
    y2Values = VitessePoids
    y2ErrorValues = Epoids/DTemps
    
# Création du graphique
    fig, ax1 = plt.subplots(figsize=(8, 5))
    ax2 = ax1.twinx()
    ax1.plot(xValues, yValues, 'blue')
    ax1.errorbar(xValues, yValues, xerr = xErrorValues, yerr = yErrorValues, fmt = 'none',elinewidth = 1, capsize = 3, ecolor = 'blue', zorder = 1)
    ax2.plot(x2Values, y2Values, 'red')
    ax2.errorbar(x2Values, y2Values, xerr = x2ErrorValues, yerr = y2ErrorValues, fmt = 'none',elinewidth = 1, capsize = 3, ecolor = 'red', zorder = 1)
    ax1.set_xlabel('Temps (min)', fontsize=13)
    ax1.set_ylabel("Taux d'érosion M3C2 (mm/min)", fontsize=13, color='b')
    ax2.set_ylabel("Taux d'érosion Balance (g/min)", fontsize=13, color='r')
    plt.title(f'{nomManip[idx]}', fontsize=14)
    #al.align.yaxes(ax1, 0, ax2, 0, 0.1)
    #al.align.yaxes(ax1, 1, ax2, 1, 0.9)
    
# Enregistrement des graphiques dans le dossier Figure de chaque manip  
    head, tail = os.path.split(' '.join(filenamestot))
    root, ext = os.path.splitext(tail)
    save =  f"{SaveFich[idx]}/plotdiff_{root}tmp"
    # plt.savefig(f"{save}.png",
    #             dpi=300, 
    #             format='png',
    #             bbox_inches='tight')
    plt.show()
    
    #Moyenne = [sum(i) for i in VitesseM3C2]
    #Moyenne= Moyenne/len(VitesseM3C2)
    print(f'Erosion moyenne {root} = ' , VitesseM3C2)