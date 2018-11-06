#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

"""
Created on Thu Aug  9 13:59:13 2018

@author: Dennis

TO - DO:
    I.  Summe residullasten (data frame)
    II. Gesamtsumme der Erzeugung --> ist ein Handel mit höherer Ebene notwendig?
    III. Algorithmus für die Eigenversorgung der Zellen --> Lastkurve:
        
        WENN value Energiebilanz > 0 dann setze alle negativen values zu 0
        AUßERDEM WENN Energiebilanz >= Energie teuerstes Kraftwerk DANN bleibt Energiemenge
        teuerstes Kraftgleich unverändert. Die Differenz zwischen Energiebilanz und
        Energie des teursten Kraftwerks wird absteigend mit den nächst teuereren Kraftwerken verrechnet
        
        WENN value Energiebeilanz < 0 dann summiere alle positven Werte und verosrge teurste Verbraucher
        
        SCHLEIFEN!!!!!!
        
        
        
    IV. Assoziierung der Lasten zu den Preisen und Preisreihenfolge
    V. Iteration mit nächst höherer Ebene und einem Startpreis

CONNECT A VALUE OF A DATAFRAME TO THE COLMUNS OF ANOTHER DATAFRAME --> Zuordnung Preise an Erzeuger oder Verbraucher
Danach nach Preis ordnen. Y-Wert: Preis, X-Wert: Energiemenge
    
"""


class cell():

    # constructor for the class 'cell'
    def __init__(self, name, level):

        self.name = name
        self.level = level

        # creating data frame (df) loads
        self.dfload = pd.read_csv(self.name + '/' + 'load.csv')
        self.dfload.set_index('snapshot', inplace=True)

        # creating data frame supply
        self.dfsupply = pd.read_csv(self.name + '/' + 'supply.csv')
        self.dfsupply.set_index('snapshot', inplace=True)

        #self.dfpriceBuy = pd.read_csv(self.name + '/' + 'priceBuy.csv')
        # creating data frame for energy consumption price

        # creating data frame for energy selling price
        #self.dfpriceSell = pd.read_csv(self.name + '/' + 'priceSell.csv')

        # creating data frame for simulation period (snapshot or time stamp)
        #self.dfsnapshot = pd.read_csv(self.name + '/' + 'snapshot.csv')

        #self.dfresidualLoad = pd.read_csv(self.name + '/' + 'residualLoad.csv')

        #self.dfresidualLoad.set_index('snapshot', inplace=True)

        # calculation of residual load of each unit in each corresponding cell
        #self.dfresidualLoadc = self.dfsupply - self.dfload.values

        # sorting the energy amounts by the price which is assocciated to the load
        self.dfloadsorted = self.dfload.sort_values('price', axis=1)

        # sorting the energy supply by the price which is assocciated to the supply
        self.dfsupplysorted = self.dfsupply.sort_values('price', axis=1)


    # Getters 

    def getDfSupplyValuesByDate(self, date):
        return self.dfsupplysorted.loc[date]

    def getDfSupplyValuesByLoad(self, load):
        return self.dfsupplysorted[load]

    def getDfLoadValuesByDate(self, date):
        return self.dfloadsorted.loc[date]

    def getDfLoadValuesByLoad(self, load):
        return self.dfloadsorted[load]

    def getStartDate(self):
        return self.dfloadsorted.iloc[1].name

    def getEndDate(self):
        return self.dfloadsorted.iloc[-1].name

    # Visualisation functions 

    def createHistogram(self, prices, loads):
        return -1
