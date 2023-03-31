# -*- coding: utf-8 -*-
"""
Created on Wed Mar 30 15:45:38 2022

@author: Marion Fournereau
"""
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import pandas as pd
import mpl_axes_aligner as al

# Paramètres 
#Definir la police et la taille des textes des figures
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams["font.size"] = 18

dirPROCESSING = "C:/Users/Benjamin/Desktop/Traitement_Cloud_Compare/PROCESSINGerosion+"
dirBALANCE = "C:/Users/Benjamin/Desktop/Poids_manips/SR" #######"C:/Users/phili/OneDrive/Desktop/Marion/M2/Graphs"

nomManip=os.listdir(dirPROCESSING)
DOSSIER_M3C2 = 'tot' # ou tot si M3C2 disque à disque initial

EM3C2 = 0.4
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
       
# Calcul des taux d'érosion par differentiel  
    #Poids=[x * (-1) for x in Poids]  
    #Valeurstot=[x * (-1) for x in Valeurstot]   
    DM3C2 = np.diff(Valeurstot)
    DPoids = np.diff(Poids)
    DTempsM3C2 = np.diff(TempsM3C2)
    DTemps = np.diff(Temps)
   
    VitesseM3C2 = DM3C2/DTempsM3C2      
    VitessePoids = DPoids/DTemps
    
    TauxErosionM = VitesseM3C2/NptsF[1:]
    VErosionMoyenneM3C2 = sum(TauxErosionM)/len(TauxErosionM)
    VErosionMoyennePds = sum(VitessePoids)/len(VitessePoids)
    print(nomManip[idx],'Taux_M3C2_moyen', VErosionMoyenneM3C2,'Taux_Poids_moyen', VErosionMoyennePds)
    
    
    
# Variables pour la création du graphique
    xValues = TempsM3C2[20:50]
    yValues = ValeurstotNorm[20:50]
    xErrorValues = ([1/60]*(len(Valeurstot))) # Incertitude sur TempsM3C2
    yErrorValues = IncertVNorm                # Incertitude sur la valeurs des données M3C2
    
    x2Values = Temps[20:50] 
    y2Values = PoidsNorm[20:50]
    x2ErrorValues = ([1/60]*(len(Temps)))     # Incertitude sur Temps
    y2ErrorValues = IncertPNorm               # Incertitude sur la valeurs des données de poids de la balance
    
    x3Values = TempsM3C2[21:50]#[1:]
    y3Values = TauxErosionM[20:50]
    x3ErrorValues = 0                         # Incertitude sur Temps
    y3ErrorValues = np.divide(IncertResultV[1:],NptsF[1:])       # Incertitude sur les taux d'érosion M3C2
    
    x4Values = Temps[21:50]#[1:]
    y4Values = VitessePoids[20:50]
    x4ErrorValues = 0                         # Incertitude sur Temps
    y4ErrorValues = Epoids                    # Incertitude sur les taux d'érosion obtenus par la balance
    
    
    plt.rcParams["figure.figsize"] = [7.00, 4.50]
    plt.rcParams["figure.autolayout"] = True

    ax0 = plt.subplot(211)
    ax1 = ax0.twinx()
    plt.setp(ax0.get_xticklabels(), visible=False)
    plt.title(f'{nomManip[idx]}', loc = "center", fontsize=16) # Create a twin of Axes with a shared x-axis but independent y-axis.
    ax2 = plt.subplot(212,sharex=ax0)
    ax3 = ax2.twinx() # Create a twin of Axes with a shared x-axis but independent y-axis.

    ax1.get_shared_x_axes().join(ax1, ax3)
    
    ax0.plot(xValues, yValues, 'mediumblue')
    ax0.errorbar(xValues, yValues, xerr = xErrorValues, yerr = yErrorValues, fmt = 'none',elinewidth = 1, capsize = 3, ecolor = 'mediumblue', zorder = 1)
    
    ax1.plot(x2Values, y2Values, 'crimson')
    ax1.errorbar(x2Values, y2Values, xerr = x2ErrorValues, yerr = y2ErrorValues, fmt = 'none',elinewidth = 1, capsize = 3, ecolor = 'crimson', zorder = 1)

    al.align.yaxes(ax0, 1, ax1, 1, 0.85)
    al.align.yaxes(ax0, 0, ax1, 0, 0.15)    
    
    ax2.plot(x3Values, y3Values, 'mediumblue')
    ax2.errorbar(x3Values, y3Values, xerr = x3ErrorValues, yerr = y3ErrorValues, fmt = 'none',elinewidth = 1, capsize = 3, ecolor = 'mediumblue', zorder = 1)
    ax3.plot(x4Values, y4Values, 'crimson')
    ax3.errorbar(x4Values, y4Values, xerr = x4ErrorValues, yerr = y4ErrorValues, fmt = 'none',elinewidth = 1, capsize = 3, ecolor = 'crimson', zorder = 1)
    ax0.set_ylabel('Diff topo \n [-]', color='mediumblue')    
    ax1.set_ylabel('Poids \n [-]', color='crimson')
    ax2.set_xlabel('Temps [min]')
    ax2.set_ylabel("Vitesse d'érosion \n [mm/min]", color='mediumblue')
    ax3.set_ylabel("Vitesse d'érosion \n [g/min]", color='crimson')
    
    head, tail = os.path.split(' '.join(filenamestot))
    root, ext = os.path.splitext(tail)
    save =  f"{SaveFich[idx]}/plotsubplot_{root}"
    #plt.savefig(f"{save}.pdf",
                    #dpi=300, 
                   # format='pdf',
                    #bbox_inches='tight')
    plt.show()