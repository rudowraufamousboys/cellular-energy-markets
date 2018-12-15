#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 10 15:00:32 2018
@author: Dennis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from itertools import islice


class grid:
    
    level=0
    
    def __init__(self, Energyprice):
        
        self.Energyprice=Energyprice
        

class powerLine:
    
    def __init__(self, name, bonus, tax, capacity):
        
        self.name=name
        self.bonus=bonus
        self.tax=tax
        self.capacity=capacity

        

class cellTypeA:
    
    level=1
    
    def __init__(self, name):
        
        self.name=name
        self.excessLoad=[]
        self.excessSupply=[]
        
# LOADING CSVs:
        
# self.dfload is a pandas DataFrame which contains the load profiles 
# for every single consumer in the cell
# each consumer has an associated price
# the index consists of date and time (YYYY:MM:DD hh:mm:ss)
        
# self.dfsupply is a pandas DataFrame which contains the supply profiles for
# every single producer in the cell
# each producer has an associated price
# the index consists of date and time (YYY:MM:DD hh:mm:ss)
        
# self.load.sort_values sorts the columns by the value of the price index
        
# self.supply.sort_values sorts the columns by the value of the price index

       
        self.Loaddf = pd.read_csv(self.name + '/' + 'load.csv')
        self.Loaddf.set_index('snapshot', inplace=True)
        self.Loaddf.sort_values('price', axis=1, ascending=False, inplace=True)
        
        self.Supplydf = pd.read_csv(self.name + '/' + 'supply.csv')
        self.Supplydf.set_index('snapshot', inplace=True)
        self.Supplydf.sort_values('price', axis=1, ascending=True, inplace=True)
        
# ACCUMULATED SUPPLY CURVE:
        
# following code accumulates the supply values in ascending order by the method
# .cumsum .iloc[1:] makes sure that the price (which is in row 0) is skipped
# self.dfsupplydropped drops every row except the price row for appending to
# dfsupplycumsum which in return gives the self.dfsupplyacc, the accumulated 
# supply curve with the price in the first row.
      
        self.Supplycumsumdf=self.Supplydf.iloc[1:].cumsum(axis=1, skipna=True)
        self.Supplydroppeddf=self.Supplydf.drop(self.Supplydf.index[1:])
        self.Supplyaccdf=self.Supplydroppeddf.append(self.Supplycumsumdf)

# ACCUMULATED LOAD CURVE:
        
# following code accumulates the load values in descending order by the method
# .cumsum .iloc[1:] makes sure that the price (which is in row 0) is skipped
# self.dfsupplydropped drops every row except the price row for appending to
# dfsupplycumsum which in return gives the self.dfsupplyacc, the accumulated 
# supply curve with the price in the first row.
      
        self.Loadcumsumdf=self.Loaddf.iloc[1:].cumsum(axis=1, skipna=True)
        self.Loaddroppeddf=self.Loaddf.drop(self.Loaddf.index[1:])
        self.Loadaccdf=self.Loaddroppeddf.append(self.Loadcumsumdf)

# SUM OF LOAD:

# here we're creating the sum of load for each cell in order to intersect the 
# resulting curve with the supply curve of a higher level cell.
# First of all we're creating the empty list self.sumLoad=[].
# This list will be filled with the sum of values for the rows or indexes
# in the self.dfload DataFrame. The price row will be dropped by
# self.dropPriceofLoad=self.dfload.drop('price', axis=0).
# self.sumL is a helping variable and the sum of each row
# in the self.dfdroppedPriceofLoad DataFrame, which subsequently will be 
# appended to self.sumLoad=[] list.

# iterrows(): generates index value pairs (e. g. 2011-06-21 00:00:00 136)
# that is in fact a nested list self.k which will be changed to a dictionary
# self.r=self.k.to_dict() just to get a new DateFrame with self.dfsumLoad
# =pd.DataFrame.from_dict(self.r, orient='columns')

        self.sumLoad=[]
        self.dropPriceofLoad=self.Loaddf.drop('price', axis=0)
        
        
        for index, row in self.dropPriceofLoad.iterrows():
            
            self.sumL=self.dropPriceofLoad.sum(axis=1)
            self.sumLoad.append(self.sumL)
            
            break
               
        self.k=pd.Series(self.sumLoad)
        self.r=self.k.to_dict()
        
        self.Sumloaddf=pd.DataFrame.from_dict(self.r, orient='columns')
        self.Sumloaddf.rename(columns={0:'sumLoad'+'_'+self.name}, inplace=True)

# SUM OF SUPPLY & LOAD:

# see: SUM OF LOAD
        
        self.sumSupply=[]
        self.dropPriceofSupply=self.Supplydf.drop('price', axis=0)


        for index, row in self.dropPriceofSupply.iterrows():
            
            self.sumS=self.dropPriceofSupply.sum(axis=1)
            self.sumSupply.append(self.sumS)
            
            break
                
        self.j=pd.Series(self.sumSupply)
        self.s=self.j.to_dict()
        
        self.SumSupplydf=pd.DataFrame.from_dict(self.s, orient='columns')
        self.SumSupplydf.rename(columns={0:'sumSupply'+'_'+self.name}, inplace=True)
        
# ENERGY BALANCE:

# self.dfenergyBalance is a DataFrame that consits the supply values which are
# subtracted by the load values of the cell
        
        self.Energybalance=self.Supplyaccdf.iloc[1:,-1]-self.Loadaccdf.iloc[1:,-1].values
        self.Energybalancedf=self.Energybalance.to_frame()
        self.Energybalancedf.rename(columns={self.Energybalancedf.columns[-1]:'EnergyBalance'+self.name}, inplace=True)
        
        
        
# EXCESS SUPPLY / EXCESS DEMAND:
        
# EXCESS SUPPLY:

# self.indexS is getting the index of one of the DataFrames which have 
# the date and time as index. The so generated list has the price at first 
# position and will be dropped by self.indexL.pop(0).
# To seperate the positive of the negative values in the self.dfenergyBalance
# there will be a for loop for the items in self.tempL, which is a temporary
# list containing the energyBalance values in column [0].
        
        self.indexS=self.Supplydf.index.tolist()
        
        self.indexS.pop(0)
        
        self.tempS=self.Energybalancedf[self.Energybalancedf.columns[-1]].tolist()
        
        for item in self.tempS:
            
            if item > 0:
                
                item=item
                
            else:
                
                item=0
            
            self.excessSupply.append(item)
            
        self.Excesssupplydf=pd.DataFrame({'Excesssupply'+self.name:self.excessSupply}).set_index([self.indexS])
        


# EXCESS LOAD:
        
# self.indexL is getting the index of one of the DataFrames which has 
# the date and time as index. The so generated list has the price at first 
# position and will be dropped by self.indexL.pop(0).
# To seperate the positive of the negative values in the self.dfenergyBalance
# there will be a for loop for the items in self.tempL, which is a temporary
# list containing the energyBalance values in column [0].

        
        self.indexL=self.Loaddf.index.tolist()
        
        self.indexL.pop(0)
            
        self.tempL=self.Energybalancedf[self.Energybalancedf.columns[-1]].tolist()
            
        for item in self.tempL:
                
            if item < 0:
                    
                item=item*-1
                    
            else:
                    
                item=0
                    
            self.excessLoad.append(item)
            
        self.Excessloaddf=pd.DataFrame({'Excessload'+self.name:self.excessLoad}).set_index([self.indexL])

# LAST PRICE SUPPLY / FIRST PRICE LOAD

# to value
        
        self.LastpriceSupplyv=self.Supplyaccdf.iloc[0][-1]
        self.FirstpriceLoadv=self.Loadaccdf.iloc[0][0]

# to dict
        
        self.LastpriceSupplyd={'price':self.LastpriceSupplyv}
        self.FirstpriceLoadd={'price':self.FirstpriceLoadv}

# to df
        
        self.LastpriceSupplydf=pd.DataFrame.from_dict(self.LastpriceSupplyd ,orient='index')
        self.FirstpriceLoaddf=pd.DataFrame.from_dict(self.FirstpriceLoadd, orient='index')
        
# rename column '0' to Excessload and Excesssupply
        
        self.LastpriceSupplydf.rename(columns={0:'Excesssupply'+self.name}, inplace=True)
        self.FirstpriceLoaddf.rename(columns={0:'Excessload'+self.name}, inplace=True)
        
 # append Excessloaddf / Excesssupplydf to FirstpriceLoaddf / LastpriceSupplydf

        self.Excesssupplydf=self.LastpriceSupplydf.append(self.Excesssupplydf)
        self.Excessloaddf=self.FirstpriceLoaddf.append(self.Excessloaddf)


class cellTypeB(cellTypeA):
    
    level=2
    
    def __init__(self, name):
        
        super().__init__(name)
        
class cellTypeC(cellTypeA):
    
    level=3
    
    def __init__(self, name):
        
        super().__init__(name)



# CREATING OBJECTS:
        
# cells

cellA1=cellTypeA('A1')
cellB1=cellTypeB('B1')
cellB2=cellTypeB('B2')
cellC1=cellTypeC('C1')
cellC2=cellTypeC('C2')
cellC3=cellTypeC('C3')
cellC4=cellTypeC('C4')

# lines

LineC1B1=powerLine('C1B1',0,0,1000)
LineC2B1=powerLine('C2B1',0,0,1000)
LineC3B2=powerLine('C3B2',0,0,1000)
LineC4B2=powerLine('C4B2',0,0,1000)
LineB1A1=powerLine('B1A1',0,0,1000)
LineB2A1=powerLine('B2A1',0,0,1000)
LineA1G=powerLine('A1G',0,0,1000) 


# CELL LEVEL B

# LOADDF / SUPPLY DF


# LOADACCDF / SUPPLYACCDF



# SUMOFLOAD

# ENERGYBALANCEDF

# EXCESSSUPPLY / EXCESS DEMAND

# LASTPRICESUPPLY / LASTPRICELOAD

# APPEND EXCESSLOAD / EXCESSSUPPLY TO FIRSTPRICELOAD / LASTPRICESUPPLY

# CELL LEVEL A

# LOADDF / SUPPLY DF

# LOADACCDF / SUPPLYACCDF

# SUMOFLOAD

# ENERGYBALANCEDF

# EXCESSSUPPLY / EXCESS DEMAND

# LASTPRICESUPPLY / LASTPRICELOAD

# APPEND EXCESSLOAD / EXCESSSUPPLY TO FIRSTPRICELOAD / LASTPRICESUPPLY

