#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mon Dec 10 15:00:32 2018
@author: Dennis
"""


from __future__ import print_function
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#from shapely.geometry import LineString

from matplotlib.pyplot import figure



class grid:
    
    level=0
    
    def __init__(self, name):
        
        self.name=name
        self.Energyprices=pd.read_csv(self.name + '/' + 'gridprice.csv')
        self.Energyprices.set_index('snapshot', inplace=True)
        
        self.Linecapacity=pd.read_csv(self.name+'/'+'gridsupply.csv')
        self.Linecapacity.set_index('snapshot', inplace=True)
        

class powerLine:
    
    def __init__(self, name, bonus, tax, capacity):
        
        self.name=name
#       self.tax=tax
        self.capacity=capacity

        

class cellTypeA:
    
    level=1
    
    def __init__(self, name, bonus):
        
        self.name=name
        self.bonus=bonus
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
        self.Sumloaddf.rename(columns={0:'Sumload'+'_'+self.name}, inplace=True)

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
        self.SumSupplydf.rename(columns={0:'Sumsupply'+'_'+self.name}, inplace=True)
        
# ENERGY BALANCE:

# self.dfenergyBalance is a DataFrame that consits the supply values which are
# subtracted by the load values of the cell
        
        self.Energybalance=self.Supplyaccdf.iloc[1:,-1]-self.Loadaccdf.iloc[1:,-1].values
        self.Energybalancedf=self.Energybalance.to_frame()
        self.Energybalancedf.rename(columns={self.Energybalancedf.columns[-1]:'Energybalance'+self.name}, inplace=True)
        
        
        
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
        self.LastpriceSupplyv= self.LastpriceSupplyv*self.bonus
        
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
    
    def __init__(self, name, bonus) :
        
        super().__init__(name, bonus)
        
class cellTypeC(cellTypeA):
    
    level=3
    
    def __init__(self, name, bonus):
        
        super().__init__(name, bonus)



# CREATING OBJECTS:
        
# cells

cellA1=cellTypeA('A1',0.5)
cellB1=cellTypeB('B1',0.5)
cellB2=cellTypeB('B2',0.5)
cellC1=cellTypeC('C1',0.5)
cellC2=cellTypeC('C2',0.5)
cellC3=cellTypeC('C3',0.5)
cellC4=cellTypeC('C4',0.5)

#  for grid and bonus for decentral energy production

tax=1

# grid

grid=grid('grid') 


# CELL LEVEL B

# LOADDF / SUPPLY DF

LoadC1C2B1df=pd.concat([cellC1.Excessloaddf,cellC2.Excessloaddf,cellB1.Loaddf], axis=1)
LoadC1C2B1df.sort_values('price', axis=1, ascending=False, inplace=True)

LoadC3C4B2df=pd.concat([cellC3.Excessloaddf, cellC4.Excessloaddf, cellB2.Loaddf], axis=1)
LoadC3C4B2df.sort_values('price', axis=1, ascending=False, inplace=True)

SupplyC1C2B1df=pd.concat([cellC1.Excesssupplydf, cellC2.Excesssupplydf, cellB1.Supplydf], axis=1)
SupplyC1C2B1df.sort_values('price', axis=1, ascending=True, inplace=True)

SupplyC3C4B2df=pd.concat([cellC3.Excesssupplydf, cellC4.Excesssupplydf, cellB2.Supplydf], axis=1)
SupplyC3C4B2df.sort_values('price', axis=1, ascending=True, inplace=True)

# PRICES FOR CUMSUM

LoadC1C2B1Pricesdf=LoadC1C2B1df.drop(LoadC1C2B1df.index[1:])
SupplyC1C2B1Pricesdf=SupplyC1C2B1df.drop(SupplyC1C2B1df.index[1:])

LoadC3C4B2Pricesdf=LoadC3C4B2df.drop(LoadC3C4B2df.index[1:])
SupplyC3C4B2Pricesdf=SupplyC3C4B2df.drop(SupplyC3C4B2df.index[1:])

# LOADACCDF / SUPPLYACCDF

LoadC1C2B1accdf=LoadC1C2B1df.iloc[1:].cumsum(axis=1)
LoadC3C4B2accdf=LoadC3C4B2df.iloc[1:].cumsum(axis=1)

SupplyC1C2B1accdf=SupplyC1C2B1df.iloc[1:].cumsum(axis=1)
SupplyC3C4B2accdf=SupplyC3C4B2df.iloc[1:].cumsum(axis=1)

LoadC1C2B1accdf=LoadC1C2B1Pricesdf.append(LoadC1C2B1accdf)
LoadC3C4B2accdf=LoadC3C4B2Pricesdf.append(LoadC3C4B2accdf)

SupplyC1C2B1accdf=SupplyC1C2B1Pricesdf.append(SupplyC1C2B1accdf)
SupplyC3C4B2accdf=SupplyC3C4B2Pricesdf.append(SupplyC3C4B2accdf)

# SUMOFLOAD

sumLoadC1C2B1l=[]
dropPriceofLoadC1C2B1df=LoadC1C2B1df.drop('price', axis=0)


for index, row in dropPriceofLoadC1C2B1df.iterrows():
            
    sumS=dropPriceofLoadC1C2B1df.sum(axis=1)
    sumLoadC1C2B1l.append(sumS)
            
    break
                
j=pd.Series(sumLoadC1C2B1l)
s=j.to_dict()
        
SumloadC1C2B1df=pd.DataFrame.from_dict(s, orient='columns')
SumloadC1C2B1df.rename(columns={0:'SumofLoad'}, inplace=True)

###############################################################################

sumLoadC3C4B2l=[]
dropPriceofLoadC3C4B2df=LoadC3C4B2df.drop('price', axis=0)


for index, row in dropPriceofLoadC3C4B2df.iterrows():
            
    sumT=dropPriceofLoadC3C4B2df.sum(axis=1)
    sumLoadC3C4B2l.append(sumT)
            
    break
                
k=pd.Series(sumLoadC3C4B2l)
t=k.to_dict()
        
SumloadC3C4B2df=pd.DataFrame.from_dict(t, orient='columns')
SumloadC3C4B2df.rename(columns={0:'SumofLoad'}, inplace=True)

# ENERGYBALANCEDF

EnergybalanceC1C2B1=SupplyC1C2B1accdf.iloc[1:,-1]-LoadC1C2B1accdf.iloc[1:,-1].values
EnergybalanceC1C2B1df=EnergybalanceC1C2B1.to_frame()
EnergybalanceC1C2B1df.rename(columns={EnergybalanceC1C2B1df.columns[-1]:'EnergybalanceC1C2B1'}, inplace=True)

EnergybalanceC3C4B2=SupplyC3C4B2accdf.iloc[1:,-1]-LoadC3C4B2accdf.iloc[1:,-1].values
EnergybalanceC3C4B2df=EnergybalanceC3C4B2.to_frame()
EnergybalanceC3C4B2df.rename(columns={EnergybalanceC3C4B2df.columns[-1]:'EnergybalanceC3C4B2'}, inplace=True)

# EXCESSSUPPLY

ExcesssupplyC1C2B1l=[]

indexS=SupplyC1C2B1df.index.tolist()
        
indexS.pop(0)
        
tempS=EnergybalanceC1C2B1df[EnergybalanceC1C2B1df.columns[-1]].tolist()
        
for item in tempS:
            
    if item > 0:
                
        item=item
                
    else:
        
        item=0
            
    ExcesssupplyC1C2B1l.append(item)
            
ExcesssupplyC1C2B1df=pd.DataFrame({'ExcesssupplyC1C2B1':ExcesssupplyC1C2B1l}).set_index([indexS])

###############################################################################

ExcesssupplyC3C4B2l=[]

indexS=SupplyC3C4B2df.index.tolist()
        
indexS.pop(0)
        
tempS=EnergybalanceC3C4B2df[EnergybalanceC3C4B2df.columns[-1]].tolist()
        
for item in tempS:
            
    if item > 0:
                
        item=item
                
    else:
        
        item=0
            
    ExcesssupplyC3C4B2l.append(item)
            
ExcesssupplyC3C4B2df=pd.DataFrame({'ExcesssupplyC3C4B2':ExcesssupplyC3C4B2l}).set_index([indexS])

# EXCESS LOAD

ExcessloadC1C2B1l=[]

indexS=LoadC1C2B1df.index.tolist()
        
indexS.pop(0)
        
tempS=EnergybalanceC1C2B1df[EnergybalanceC1C2B1df.columns[-1]].tolist()
        
for item in tempS:
            
    if item < 0:
                
        item=item*-1
                
    else:
        
        item=0
            
    ExcessloadC1C2B1l.append(item)
            
ExcessloadC1C2B1df=pd.DataFrame({'ExcessloadC1C2B1':ExcessloadC1C2B1l}).set_index([indexS])

###############################################################################

ExcessloadC3C4B2l=[]

indexS=LoadC3C4B2df.index.tolist()
        
indexS.pop(0)
        
tempS=EnergybalanceC3C4B2df[EnergybalanceC3C4B2df.columns[-1]].tolist()
        
for item in tempS:
            
    if item < 0:
                
        item=item*-1
                
    else:
        
        item=0
            
    ExcessloadC3C4B2l.append(item)
            
ExcessloadC3C4B2df=pd.DataFrame({'ExcessloadC3C4B2':ExcessloadC3C4B2l}).set_index([indexS])

# LASTPRICESUPPLY / LASTPRICELOAD

# to value
        
LastpriceSupplyC1C2B1v=SupplyC1C2B1accdf.iloc[0][-1]
#LastpriceSupplyC1C2B1v=LastpriceSupplyC1C2B1v

LastpriceSupplyC3C4B2v=SupplyC3C4B2accdf.iloc[0][-1]
#LastpriceSupplyC3C4B2v=LastpriceSupplyC3C4B2v

FirstpriceLoadC1C2B1v=LoadC1C2B1accdf.iloc[0][0]
FirstpriceLoadC3C4B2v=LoadC3C4B2accdf.iloc[0][0]

# to dict
        
LastpriceSupplyC1C2B1d={'price':LastpriceSupplyC1C2B1v}
LastpriceSupplyC3C4B2d={'price':LastpriceSupplyC3C4B2v}

FirstpriceLoadC1C2B1d={'price':FirstpriceLoadC1C2B1v}
FirstpriceLoadC3C4B2d={'price':FirstpriceLoadC3C4B2v}

# to df
        
LastpriceSupplyC1C2B1df=pd.DataFrame.from_dict(LastpriceSupplyC1C2B1d ,orient='index')
LastpriceSupplyC3C4B2df=pd.DataFrame.from_dict(LastpriceSupplyC3C4B2d ,orient='index')

FirstpriceLoadC1C2B1df=pd.DataFrame.from_dict(FirstpriceLoadC1C2B1d, orient='index')
FirstpriceLoadC3C4B2df=pd.DataFrame.from_dict(FirstpriceLoadC3C4B2d, orient='index')

        
# rename column '0' to Excessload and Excesssupply
        
LastpriceSupplyC1C2B1df.rename(columns={0:'ExcesssupplyC1C2B1'}, inplace=True)
LastpriceSupplyC3C4B2df.rename(columns={0:'ExcesssupplyC3C4B2'}, inplace=True)

FirstpriceLoadC1C2B1df.rename(columns={0:'ExcessloadC1C2B1'}, inplace=True)
FirstpriceLoadC3C4B2df.rename(columns={0:'ExcessloadC3C4B2'}, inplace=True)
        
# append Excessloaddf / Excesssupplydf to FirstpriceLoaddf / LastpriceSupplydf

ExcesssupplyC1C2B1df=LastpriceSupplyC1C2B1df.append(ExcesssupplyC1C2B1df)
ExcesssupplyC3C4B2df=LastpriceSupplyC3C4B2df.append(ExcesssupplyC3C4B2df)

ExcessloadC1C2B1df=FirstpriceLoadC1C2B1df.append(ExcessloadC1C2B1df)
ExcessloadC3C4B2df=FirstpriceLoadC3C4B2df.append(ExcessloadC3C4B2df)


# CELL LEVEL A

# LOADDF / SUPPLY DF

LoadB1B2A1df=pd.concat([ExcessloadC1C2B1df,ExcessloadC3C4B2df,cellA1.Loaddf], axis=1)
LoadB1B2A1df.sort_values('price', axis=1, ascending=False, inplace=True)

SupplyB1B2A1df=pd.concat([ExcesssupplyC1C2B1df, ExcesssupplyC3C4B2df, cellA1.Supplydf], axis=1)
SupplyB1B2A1df.sort_values('price', axis=1, ascending=True, inplace=True)

# PRICES FOR CUMSUM

LoadB1B2A1Pricesdf=LoadB1B2A1df.drop(LoadC1C2B1df.index[1:])
SupplyB1B2A1Pricesdf=SupplyB1B2A1df.drop(SupplyC1C2B1df.index[1:])

# LOADACCDF / SUPPLYACCDF

LoadB1B2A1accdf=LoadB1B2A1df.iloc[1:].cumsum(axis=1)
LoadB1B2A1accdf=LoadB1B2A1Pricesdf.append(LoadB1B2A1accdf)

SupplyB1B2A1accdf=SupplyB1B2A1df.iloc[1:].cumsum(axis=1)
SupplyB1B2A1accdf=SupplyB1B2A1Pricesdf.append(SupplyB1B2A1accdf)

# SUMOFLOAD

sumLoadB1B2A1l=[]
dropPriceofLoadB1B2A1df=LoadB1B2A1df.drop('price', axis=0)


for index, row in dropPriceofLoadB1B2A1df.iterrows():
            
    sumS=dropPriceofLoadB1B2A1df.sum(axis=1)
    sumLoadB1B2A1l.append(sumS)
            
    break
                
j=pd.Series(sumLoadB1B2A1l)
s=j.to_dict()
        
SumloadB1B2A1df=pd.DataFrame.from_dict(s, orient='columns')
SumloadB1B2A1df.rename(columns={0:'SumofLoad'}, inplace=True)


# ALTERNATING GRID PRICE

#gridPricesdf=grid.Energyprices

gridPrices=grid.Energyprices.iloc[:,0].tolist()

gridPrices = [i * tax for i in gridPrices]

lineCapacities=grid.Linecapacity['gridsupply'].tolist()

# delete first value in list for it is the price

del lineCapacities[0]

for item in lineCapacities:
    
    float(item)

###############################################################################

# data frames cell level C:

SupplyC1df=cellC1.Supplydf
SupplyC2df=cellC2.Supplydf
SupplyC3df=cellC3.Supplydf
SupplyC4df=cellC4.Supplydf

sumLoadC1df=cellC1.Sumloaddf
sumLoadC2df=cellC2.Sumloaddf
sumLoadC3df=cellC3.Sumloaddf
sumLoadC4df=cellC4.Sumloaddf

sumSupplyC1df=cellC1.SumSupplydf
sumSupplyC2df=cellC2.SumSupplydf
sumSupplyC3df=cellC3.SumSupplydf
sumSupplyC4df=cellC4.SumSupplydf


ExcesssupplyC1df=cellC1.Excesssupplydf
ExcesssupplyC1df.drop(ExcesssupplyC1df.index[0], inplace=True)

ExcesssupplyC2df=cellC2.Excesssupplydf
ExcesssupplyC2df.drop(ExcesssupplyC2df.index[0], inplace=True)

ExcesssupplyC3df=cellC3.Excesssupplydf
ExcesssupplyC3df.drop(ExcesssupplyC3df.index[0], inplace=True)

ExcesssupplyC4df=cellC4.Excesssupplydf
ExcesssupplyC4df.drop(ExcesssupplyC4df.index[0], inplace=True)

LastpriceSupplyC1=cellC1.LastpriceSupplydf.iloc[0,0]
#LastpriceSupplyC1=LastpriceSupplyC1*bonus

LastpriceSupplyC2=cellC2.LastpriceSupplydf.iloc[0,0]
#LastpriceSupplyC2=LastpriceSupplyC2*bonus

LastpriceSupplyC3=cellC3.LastpriceSupplydf.iloc[0,0]
#LastpriceSupplyC3=LastpriceSupplyC3*bonus

LastpriceSupplyC4=cellC4.LastpriceSupplydf.iloc[0,0]
#LastpriceSupplyC4=LastpriceSupplyC4*bonus

###############################################################################

# line capacities:

layoutFactor=2.5

LineCapacityC1B1=cellC1.Sumloaddf['Sumload_C1'].tolist() 
LineCapacityC1B1=max(LineCapacityC1B1)*layoutFactor

LineCapacityC2B1=cellC2.Sumloaddf['Sumload_C2'].tolist() 
LineCapacityC2B1=max(LineCapacityC2B1)*layoutFactor

LineCapacityC3B2=cellC3.Sumloaddf['Sumload_C3'].tolist() 
LineCapacityC3B2=max(LineCapacityC3B2)*layoutFactor

LineCapacityC4B2=cellC4.Sumloaddf['Sumload_C4'].tolist() 
LineCapacityC4B2=max(LineCapacityC4B2)*layoutFactor

LineCapacityB1A1=SumloadC1C2B1df['SumofLoad'].tolist() 
LineCapacityB1A1=max(LineCapacityB1A1)*layoutFactor

LineCapacityB2A1=SumloadC3C4B2df['SumofLoad'].tolist() 
LineCapacityB2A1=max(LineCapacityB2A1)*layoutFactor

LineCapacityA1G=SumloadB1B2A1df['SumofLoad'].tolist()
LineCapacityA1G=max(LineCapacityA1G)*layoutFactor 

###############################################################################                           
  
# energy offer start values:

energy_offerA1=float(0)

energy_offerB1=float(0)
energy_offerB2=float(0)

energy_offerC1=float(0)
energy_offerC2=float(0)
energy_offerC3=float(0)
energy_offerC4=float(0)

# price energy offer start values:

price_offerA1=float(0)

price_offerB1=float(0)
price_offerB2=float(0)

price_offerC1=float(0)
price_offerC2=float(0)
price_offerC3=float(0)
price_offerC4=float(0)

###############################################################################

# list for while loop:

marketPrice=[0,1]

marketPricequilibrium=[]
energyMarketequilibriuml=[]

# lists for energy cut:

energy_cutA1l=[]
energy_cutnameA1l=[]
grid_supplyl=[]
grid_cutl=[]
last_xValuel=[]
lineCutl=[]

energy_cutB1l=[]
energy_cutB2l=[]

energy_cutC1l=[]
energy_cutC2l=[]
energy_cutC3l=[]
energy_cutC4l=[]


# counter for market price:
 
q=0

# counter for time steps

z=0
    
while marketPrice[q+1] != marketPrice[q]:
    
    ###########################################################################
    ################### L O O P ###############################################
    ###########################################################################
    ##################################### D O W N #############################
    ###########################################################################
    ###########################################################################
        
    ###########################LEVEL GRID to A#################################  
        
            x_values=SupplyB1B2A1df.iloc[z+1].values.tolist()
            
            # adding grid capacity, energyoffer_B1 and energyoffer_B2 to supply:
            
            if lineCapacities[z] > LineCapacityA1G:
                
                lineCapacities[z]=LineCapacityA1G
            
            x_values.append(lineCapacities[z])
                                   
            y_values=SupplyB1B2A1df.iloc[0].values.tolist()
            
            # adding grid price, price_offerB1 and price_offerB2 to supply:
            
            y_values.append(gridPrices[z])
            
    #        if price_offerB1 > 0:
    #            
    #            y_values.append(price_offerB1)
    #            
    #        else:
    #            
    #            pass
    #        
    #        if price_offerB2 > 0:
    #            
    #            y_values.append(price_offerB2)
    #            
    #        else:
    #            
    #            pass
            
            x_values = [x for _,x in sorted(zip(y_values,x_values))]
            
            x_values=[sum(x_values[:y]) for y in range(1, len(x_values) + 1)]
            
            y_values.sort()
            
            # supply curve:
            
            x_supplyacc=x_values*2
            x_supplyacc.sort()
    
            x_supplyacc.insert(0,0)
            x_supplyacc.insert(1,0)
            del x_supplyacc[-1]
                
            
            y_supplyacc=y_values*2
            y_supplyacc.sort()
    
            y_supplyacc.insert(0,0)
           
            # load curve:
    
            x_load=SumloadC1C2B1df.iloc[z].tolist()
            y_load=[0,40]*len(x_load)
    
            x_load=x_load*2
            
    
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            for Z in range (1,len(x_supplyacc)):
                        
            #condition for intersection between supply and demand curve
            
                if x_load[0]> x_supplyacc[-Z]:
                    price_offerA1=y_supplyacc[-Z]
                    energyMarketequilibrium=x_load[0]
                    energy_offerA1=x_supplyacc[-Z+1]-x_load[0]
                    #if a condition is met, the loop stops
                    break        
    
            if energy_offerA1 < 0:
                
                energy_offerA1=float(0)
                price_offerA1=y_supplyacc[-1]
                #price_offerA1=float(0)
                
            else:
                
                pass
            
    ###############################flexible demand#############################
             
            i=0
            
            Fxi=[x_load[0],x_load[0]+50-i,x_load[0]+50-i]
            Fyi=[20-0.1*i,20-0.1*i,0]
    
            for Z in range (1,len(x_supplyacc)):
                    
                    if Fxi[1]>x_supplyacc[-Z] and Fyi[1]>=y_supplyacc[-Z+1]:
                       
                        y_me1=y_supplyacc[-Z+1]
                        x_me1=Fxi[1]
                        energy_offerA1=x_supplyacc[-Z+1]-Fxi[1]
                        
                        
                        
                        #if a condition is met, the loop stops
                        
                    
                        if y_me1==price_offerA1:
                            y_me1=price_offerA1
                            x_me1=energyMarketequilibrium=Fxi[1]
                            x_offer1=energy_offerA1=x_supplyacc[-Z+1]-Fxi[1]
                            i=i+1
                        
                        if i>=50:
                            i=50                        
                            
                            
                        #if x_supplyacc[-Z] > x_me:
                         #   print(x_supplyacc[-Z])
                
                        break
                    
                
            energy_offerA1reset=energy_offerA1
            price_offerA1reset=price_offerA1
#            
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!       
            
#            plot, =plt.plot(x_supplyacc,y_supplyacc)
#            plot, =plt.plot(x_load,y_load)
#            plot, =plt.plot(energyMarketequilibrium,price_offerA1,'yo')
#            plot, =plt.plot(Fxi,Fyi,"--")
#            
#            plt.xlabel('Energy A1')    
#            plt.ylabel('Price A1')
#                    
#            plt.show()
                  
    ################################LEVEL A to B1##############################

            if energy_offerA1 > LineCapacityB1A1:
                
                lineCutB1A1=energy_offerA1-LineCapacityB1A1
                
                energy_offerA1=LineCapacityB1A1
                
            else:
                
                lineCutB1A1=0.0
                                
    ###########################################################################
            
            x_values=SupplyC1C2B1df.iloc[z+1].values.tolist()
                
        # adding energyoffer_A1 to supply /
        # manipulating energy_offerA1 depending on last price and excesssupply:
                
            ExcesssupplyC1C2B1=ExcesssupplyC1C2B1df['ExcesssupplyC1C2B1'].tolist()
            ExcesssupplyC3C4B2=ExcesssupplyC3C4B2df['ExcesssupplyC3C4B2'].tolist()
                
            if ExcesssupplyC1C2B1[z+1] > 0 and LastpriceSupplyC1C2B1v >  \
                price_offerA1 and ExcesssupplyC3C4B2[z+1] > 0:
                    
                energy_offerA1= energy_offerA1/2
                    
            else:
                    
                energy_offerA1= 0
                    
            x_values.append(energy_offerA1)
                
    #        if energy_offerC1 > 0:
    #                
    #            x_values.append(energy_offerC1)
    #                
    #        else:
    #                
    #            pass
    #            
    #        if energy_offerC2 > 0:
    #                
    #            x_values.append(energy_offerC2)
    #                
    #        else:
    #                
    #            pass
            
            y_values=SupplyC1C2B1df.iloc[0].values.tolist()
            
            if ExcesssupplyC1C2B1[z+1] == 0:
                    
                price_offerA1= 0
                   
            else:
                    
                pass
                
            y_values.append(price_offerA1)        
                
            x_values = [x for _,x in sorted(zip(y_values,x_values))]
                
            x_values=[sum(x_values[:y]) for y in range(1, len(x_values) + 1)]
                                    
            y_values.sort()
                
            # supply curve:
                
            x_supplyacc=x_values*2
            x_supplyacc.sort()
        
            x_supplyacc.insert(0,0)
            x_supplyacc.insert(1,0)
            del x_supplyacc[-1]
                    
                
            y_supplyacc=y_values*2
            y_supplyacc.sort()
        
            y_supplyacc.insert(0,0)
               
            # load curve:
        
            x_load=SumloadC1C2B1df.iloc[z].tolist()
            y_load=[0,40]*len(x_load)
        
            x_load=x_load*2
                
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            for Z in range (1,len(x_supplyacc)):
                            
                #condition for intersection between supply and demand curve
                if x_load[0]> x_supplyacc[-Z]:
                    price_offerB1=y_supplyacc[-Z]
                    energyMarketequilibrium=x_load[0]
                    energy_offerB1=x_supplyacc[-Z+1]-x_load[0]
                    #if a condition is met, the loop stops
                    break
                
            if energy_offerB1 < 0:
                    
                energy_offerB1=float(0)
                price_offerB1=y_supplyacc[-1]
                #price_offerB1=float(0)
                    
            else:
                    
                pass
    
    ###############################flexible demand#############################
             
            i=0
            
            Fxi=[x_load[0],x_load[0]+50-i,x_load[0]+50-i]
            Fyi=[20-0.1*i,20-0.1*i,0]
    
            for Z in range (1,len(x_supplyacc)):
                    
                    if Fxi[1]>x_supplyacc[-Z] and Fyi[1]>=y_supplyacc[-Z+1]:
                       
                        y_me1=y_supplyacc[-Z+1]
                        x_me1=Fxi[1]
                        energy_offerB1=x_supplyacc[-Z+1]-Fxi[1]
                        
                        
                        
                        #if a condition is met, the loop stops
                        
                    
                        if y_me1==price_offerB1:
                            y_me1=price_offerB1
                            x_me1=energyMarketequilibrium=Fxi[1]
                            x_offer1=energy_offerB1=x_supplyacc[-Z+1]-Fxi[1]
                            i=i+1
                        
                        if i>=50:
                            i=50                        
                            
                            
                        #if x_supplyacc[-Z] > x_me:
                         #   print(x_supplyacc[-Z])
                
                        break
    
                
            energy_offerB1reset=energy_offerB1
            price_offerB1reset=price_offerB1
                
            energy_offerA1=energy_offerA1reset
            price_offerA1=price_offerA1reset
            
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
                
#            plot, =plt.plot(x_supplyacc,y_supplyacc)
#            plot, =plt.plot(x_load,y_load)
#            plot, =plt.plot(energyMarketequilibrium,price_offerB1,'yo')
#            plot, =plt.plot(Fxi,Fyi,"--")
#                
#            plt.xlabel('Energy B1')    
#            plt.ylabel('Price B1')
#                        
#            plt.show()
                
    ################################LEVEL A to B2##############################

            if energy_offerA1 > LineCapacityB2A1:
                
                lineCutB2A1=energy_offerA1-LineCapacityB2A1                
            
                energy_offerA1=LineCapacityB2A1
                
            else:
                
                lineCutB2A1=0.0
                
    ###########################################################################
                                    
            x_values=SupplyC3C4B2df.iloc[z+1].values.tolist()
                
        # adding energyoffer_A1 to supply /
        # manipulating energy_offerA1 depending on last price and excesssupply:
                
            ExcesssupplyC1C2B1=ExcesssupplyC1C2B1df['ExcesssupplyC1C2B1'].tolist()
            ExcesssupplyC3C4B2=ExcesssupplyC3C4B2df['ExcesssupplyC3C4B2'].tolist()
                
            if ExcesssupplyC3C4B2[z+1] > 0 and LastpriceSupplyC3C4B2v >  \
                price_offerA1 and ExcesssupplyC1C2B1[z+1] > 0:
                    
                energy_offerA1= energy_offerA1/2
                    
            else:
                    
                energy_offerA1= 0
                    
            x_values.append(energy_offerA1)
                
    #        if energy_offerC1 > 0:
    #                
    #            x_values.append(energy_offerC1)
    #                
    #        else:
    #                
    #            pass
    #            
    #        if energy_offerC2 > 0:
    #                
    #            x_values.append(energy_offerC2)
    #                
    #        else:
    #                
    #            pass
            
            y_values=SupplyC3C4B2df.iloc[0].values.tolist()
            
            if ExcesssupplyC3C4B2[z+1] == 0:
                    
                price_offerA1= 0
                   
            else:
                    
                pass
                
            y_values.append(price_offerA1)        
                
            x_values = [x for _,x in sorted(zip(y_values,x_values))]
                
            x_values=[sum(x_values[:y]) for y in range(1, len(x_values) + 1)]
                                    
            y_values.sort()
                
            # supply curve:
                
            x_supplyacc=x_values*2
            x_supplyacc.sort()
        
            x_supplyacc.insert(0,0)
            x_supplyacc.insert(1,0)
            del x_supplyacc[-1]
                    
                
            y_supplyacc=y_values*2
            y_supplyacc.sort()
        
            y_supplyacc.insert(0,0)
               
            # load curve:
        
            x_load=SumloadC3C4B2df.iloc[z].tolist()
            y_load=[0,40]*len(x_load)
        
            x_load=x_load*2
                
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            for Z in range (1,len(x_supplyacc)):
                            
                #condition for intersection between supply and demand curve
                if x_load[0]> x_supplyacc[-Z]:
                    price_offerB2=y_supplyacc[-Z]
                    energyMarketequilibrium=x_load[0]
                    energy_offerB2=x_supplyacc[-Z+1]-x_load[0]
                    #if a condition is met, the loop stops
                    break
                
            if energy_offerB2 < 0:
                    
                energy_offerB2=float(0)
                price_offerB2=y_supplyacc[-1]
                #price_offerB2=float(0)
                    
            else:
                    
                pass
                
    ###############################flexible demand#############################
             
            i=0
            
            Fxi=[x_load[0],x_load[0]+50-i,x_load[0]+50-i]
            Fyi=[20-0.1*i,20-0.1*i,0]
    
            for Z in range (1,len(x_supplyacc)):
                    
                    if Fxi[1]>x_supplyacc[-Z] and Fyi[1]>=y_supplyacc[-Z+1]:
                       
                        y_me1=y_supplyacc[-Z+1]
                        x_me1=Fxi[1]
                        energy_offerB2=x_supplyacc[-Z+1]-Fxi[1]
                        
                        
                        
                        #if a condition is met, the loop stops
                        
                    
                        if y_me1==price_offerB2:
                            y_me1=price_offerB2
                            x_me1=energyMarketequilibrium=Fxi[1]
                            x_offer1=energy_offerB2=x_supplyacc[-Z+1]-Fxi[1]
                            i=i+1
                        
                        if i>=50:
                            i=50                        
                            
                            
                        #if x_supplyacc[-Z] > x_me:
                         #   print(x_supplyacc[-Z])
                
                        break            
                
            energy_offerB2reset=energy_offerB2
            price_offerB2reset=price_offerB2
                
            energy_offerA1=energy_offerA1reset
            price_offerA1=price_offerA1reset
            
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!       
                
#            plot, =plt.plot(x_supplyacc,y_supplyacc)
#            plot, =plt.plot(x_load,y_load)
#            plot, =plt.plot(energyMarketequilibrium,price_offerB2,'yo')
#            plot, =plt.plot(Fxi,Fyi,"--")
#                
#            plt.xlabel('Energy B2')    
#            plt.ylabel('Price B2')
#                        
#            plt.show()
                  
    ################################LEVEL B1 to C1#############################
           
            if energy_offerB1 > LineCapacityC1B1:

                lineCutB1C1=energy_offerB1-LineCapacityC1B1
                
                energy_offerB1=LineCapacityC1B1
                
            else:
                
                lineCutB1C1=0.0
                
    ###########################################################################
                    
            x_values=SupplyC1df.iloc[z+1].values.tolist()
            
        # adding energyoffer_B1 to supply /
        # manipulating energy_offerB1 depending on last price and excesssupply:
            
            ExcesssupplyC1=ExcesssupplyC1df['ExcesssupplyC1'].tolist()
            ExcesssupplyC2=ExcesssupplyC2df['ExcesssupplyC2'].tolist()
            
            if ExcesssupplyC1[z] > 0 and LastpriceSupplyC1 >  \
            price_offerB1 and ExcesssupplyC2[z] > 0:
                
                energy_offerB1= float(energy_offerB1/2)
                
            else:
                
                energy_offerB1= float(0)
           
            #adding energyoffer_B1 to supply:
            
            x_values.append(energy_offerB1)
                                
            y_values=SupplyC1df.iloc[0].values.tolist()
            
            # adding price_offerB1 to supply prices:
            
            if ExcesssupplyC1[z] == 0:
                
                price_offerB1=float(0)
            
            y_values.append(price_offerB1)
                    
            x_values = [x for _,x in sorted(zip(y_values,x_values))]
            
            x_values=[sum(x_values[:y]) for y in range(1, len(x_values) + 1)]
            
            y_values.sort()
            
            # supply curve:
            
            x_supplyacc=x_values*2
            x_supplyacc.sort()
    
            x_supplyacc.insert(0,0)
            x_supplyacc.insert(1,0)
            del x_supplyacc[-1]
                
            
            y_supplyacc=y_values*2
            y_supplyacc.sort()
    
            y_supplyacc.insert(0,0)
           
            # load curve:
    
            x_load=sumLoadC1df.iloc[z].tolist()
            y_load=[0,40]*len(x_load)
    
            x_load=x_load*2
            
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            for Z in range (1,len(x_supplyacc)):
                        
            #condition for intersection between supply and demand curve
                if x_load[0]> x_supplyacc[-Z]:
                    price_offerC1=y_supplyacc[-Z]
                    energyMarketequilibrium=x_load[0]
                    energy_offerC1=x_supplyacc[-Z+1]-x_load[0]
                    #if a condition is met, the loop stops
                    break            
    
            if energy_offerB2 < 0:
                
                energy_offerC1=float(0)
                price_offerC1=y_supplyacc[-1]
                #price_offerC1=float(0)
                
            else:
                
                pass
                
    ###############################flexible demand#############################
             
            i=0
            
            Fxi=[x_load[0],x_load[0]+50-i,x_load[0]+50-i]
            Fyi=[20-0.1*i,20-0.1*i,0]
    
            for Z in range (1,len(x_supplyacc)):
                    
                    if Fxi[1]>x_supplyacc[-Z] and Fyi[1]>=y_supplyacc[-Z+1]:
                       
                        y_me1=y_supplyacc[-Z+1]
                        x_me1=Fxi[1]
                        energy_offerC1=x_supplyacc[-Z+1]-Fxi[1]
                        
                        
                        
                        #if a condition is met, the loop stops
                        
                    
                        if y_me1==price_offerC1:
                            y_me1=price_offerC1
                            x_me1=energyMarketequilibrium=Fxi[1]
                            x_offer1=energy_offerC1=x_supplyacc[-Z+1]-Fxi[1]
                            i=i+1
                        
                        if i>=50:
                            i=50                        
                            
                            
                        #if x_supplyacc[-Z] > x_me:
                         #   print(x_supplyacc[-Z])
                
                        break
                    
    ###############################energy cut##################################

            for Z in range (1,len(x_values)):
                
                if x_values[-1]> energyMarketequilibrium:
                    
                    energy_cutC1=x_values[-1]- energyMarketequilibrium
                    
                else:
                    
                    energy_cutC1=float(0)        
            
            energy_offerB1=energy_offerB1reset
            price_offerB1=price_offerB1reset
            
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
            
#            plot, =plt.plot(x_supplyacc,y_supplyacc)
#            plot, =plt.plot(x_load,y_load)
#            plot, =plt.plot(energyMarketequilibrium,price_offerC1,'yo')
#            plot, =plt.plot(Fxi,Fyi,"--")
#            
#            
#            plt.xlabel('Energy C1')    
#            plt.ylabel('Price C1')
#                    
#            plt.show()
           
    ################################LEVEL B1 to C2#############################

            if energy_offerB1 > LineCapacityC2B1:

                lineCutC2B1=energy_offerB1-LineCapacityC2B1                
                
                energy_offerB1=LineCapacityC2B1
                
            else:
                
                lineCutC2B1=0.0
                
    ###########################################################################
            
            x_values=SupplyC2df.iloc[z+1].values.tolist()
            
        # adding energyoffer_B1 to supply /
        # manipulating energy_offerB1 depending on last price and excesssupply:
            
            ExcesssupplyC1=ExcesssupplyC1df['ExcesssupplyC1'].tolist()
            ExcesssupplyC2=ExcesssupplyC2df['ExcesssupplyC2'].tolist()
            
            if ExcesssupplyC2[z] > 0 and LastpriceSupplyC2 >  \
            price_offerB1 and ExcesssupplyC1[z] > 0:
                
                energy_offerB1= energy_offerB1/2
                
            else:
                
                energy_offerB1= 0
           
            #adding energyoffer_B1 to supply:
            
            x_values.append(energy_offerB1)
                                
            y_values=SupplyC2df.iloc[0].values.tolist()
            
            # adding price_offerB1 to supply prices:
            
            if ExcesssupplyC2[z] == 0:
                
                price_offerB1= 0
            
            y_values.append(price_offerB1)
                    
            x_values = [x for _,x in sorted(zip(y_values,x_values))]
            
            x_values=[sum(x_values[:y]) for y in range(1, len(x_values) + 1)]
            
            y_values.sort()
            
            # supply curve:
            
            x_supplyacc=x_values*2
            x_supplyacc.sort()
    
            x_supplyacc.insert(0,0)
            x_supplyacc.insert(1,0)
            del x_supplyacc[-1]
                
            
            y_supplyacc=y_values*2
            y_supplyacc.sort()
    
            y_supplyacc.insert(0,0)
           
            # load curve:
    
            x_load=sumLoadC2df.iloc[z].tolist()
            y_load=[0,40]*len(x_load)
    
            x_load=x_load*2
            
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            for Z in range (1,len(x_supplyacc)):
                        
            #condition for intersection between supply and demand curve
                if x_load[0]> x_supplyacc[-Z]:
                    price_offerC2=y_supplyacc[-Z]
                    energyMarketequilibrium=x_load[0]
                    energy_offerC2=x_supplyacc[-Z+1]-x_load[0]
                    #if a condition is met, the loop stops
                    break            
    
            if energy_offerB2 < 0:
                
                energy_offerC2=float(0)
                price_offerC2=y_supplyacc[-1]
                #price_offerB2=float(0)
                
            else:
                
                pass
    
    ###############################flexible demand#############################
             
            i=0
            
            Fxi=[x_load[0],x_load[0]+50-i,x_load[0]+50-i]
            Fyi=[20-0.1*i,20-0.1*i,0]
    
            for Z in range (1,len(x_supplyacc)):
                    
                    if Fxi[1]>x_supplyacc[-Z] and Fyi[1]>=y_supplyacc[-Z+1]:
                       
                        y_me1=y_supplyacc[-Z+1]
                        x_me1=Fxi[1]
                        energy_offerC2=x_supplyacc[-Z+1]-Fxi[1]
                        
                        
                        
                        #if a condition is met, the loop stops
                        
                    
                        if y_me1==price_offerC2:
                            y_me1=price_offerC2
                            x_me1=energyMarketequilibrium=Fxi[1]
                            x_offer1=energy_offerC2=x_supplyacc[-Z+1]-Fxi[1]
                            i=i+1
                        
                        if i>=50:
                            i=50                        
                            
                            
                        #if x_supplyacc[-Z] > x_me:
                         #   print(x_supplyacc[-Z])
                
                        break

    ###############################energy cut##################################

            for Z in range (1,len(x_values)):
                
                if x_values[-1]> energyMarketequilibrium:
                    
                    energy_cutC2=x_values[-1]- energyMarketequilibrium
                    
                else:
                    
                    energy_cutC2=float(0)                            
            
            energy_offerB1=energy_offerB1reset
            price_offerB1=price_offerB1reset
            
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!       
            
#            plot, =plt.plot(x_supplyacc,y_supplyacc)
#            plot, =plt.plot(x_load,y_load)
#            plot, =plt.plot(energyMarketequilibrium,price_offerC2,'yo')
#            plot, =plt.plot(Fxi,Fyi,"--")
#            
#            plt.xlabel('Energy C2')    
#            plt.ylabel('Price C2')
#                    
#            plt.show()
    
    ################################LEVEL B2 to C3#############################
 
            if energy_offerB2 > LineCapacityC3B2:

                lineCutC3B2=energy_offerB2-LineCapacityC3B2                
                
                energy_offerB2=LineCapacityC3B2
                
            else:
                
                lineCutC3B2=0.0

    ###########################################################################
           
            x_values=SupplyC3df.iloc[z+1].values.tolist()
            
            ExcesssupplyC3=ExcesssupplyC3df['ExcesssupplyC3'].tolist()
            ExcesssupplyC4=ExcesssupplyC4df['ExcesssupplyC4'].tolist()
            
            if ExcesssupplyC3[z] > 0 and LastpriceSupplyC3 >  \
            price_offerB2 and ExcesssupplyC4[z] > 0:
                
                energy_offerB2= energy_offerB2/2
                
            else:
                
                energy_offerB2= 0
            
            # adding energyoffer_B2 to supply:
            
            x_values.append(energy_offerB2)
                                
            y_values=SupplyC3df.iloc[0].values.tolist()
            
            # adding price_offerB2 to supply prices:
            
            if ExcesssupplyC3[z] == 0:
                
                price_offerB2= 0        
            
            y_values.append(price_offerB2)
                    
            x_values = [x for _,x in sorted(zip(y_values,x_values))]
            
            x_values=[sum(x_values[:y]) for y in range(1, len(x_values) + 1)]
            
            y_values.sort()
            
            # supply curve:
            
            x_supplyacc=x_values*2
            x_supplyacc.sort()
    
            x_supplyacc.insert(0,0)
            x_supplyacc.insert(1,0)
            del x_supplyacc[-1]
                
            
            y_supplyacc=y_values*2
            y_supplyacc.sort()
    
            y_supplyacc.insert(0,0)
           
            # load curve:
    
            x_load=sumLoadC3df.iloc[z].tolist()
            y_load=[0,40]*len(x_load)
    
            x_load=x_load*2
            
    
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            for Z in range (1,len(x_supplyacc)):
                        
            #condition for intersection between supply and demand curve
                if x_load[0]> x_supplyacc[-Z]:
                    price_offerC3=y_supplyacc[-Z]
                    energyMarketequilibrium=x_load[0]
                    energy_offerC3=x_supplyacc[-Z+1]-x_load[0]
                    #if a condition is met, the loop stops
                    break            
    
            if energy_offerB2 < 0:
                
                energy_offerC3=float(0)
                price_offerC3=y_supplyacc[-1]
                #price_offerB2=float(0)
                
            else:
                
                pass
    
    ###############################flexible demand#############################
             
            i=0
            
            Fxi=[x_load[0],x_load[0]+50-i,x_load[0]+50-i]
            Fyi=[20-0.1*i,20-0.1*i,0]
    
            for Z in range (1,len(x_supplyacc)):
                    
                    if Fxi[1]>x_supplyacc[-Z] and Fyi[1]>=y_supplyacc[-Z+1]:
                       
                        y_me1=y_supplyacc[-Z+1]
                        x_me1=Fxi[1]
                        energy_offerC3=x_supplyacc[-Z+1]-Fxi[1]
                        
                        
                        
                        #if a condition is met, the loop stops
                        
                    
                        if y_me1==price_offerC3:
                            y_me1=price_offerC3
                            x_me1=energyMarketequilibrium=Fxi[1]
                            x_offer1=energy_offerC3=x_supplyacc[-Z+1]-Fxi[1]
                            i=i+1
                        
                        if i>=50:
                            i=50                        
                            
                            
                        #if x_supplyacc[-Z] > x_me:
                         #   print(x_supplyacc[-Z])
                
                        break 

    ###############################energy cut##################################

            for Z in range (1,len(x_values)):
                
                if x_values[-1]> energyMarketequilibrium:
                    
                    energy_cutC3=x_values[-1]- energyMarketequilibrium
                    
                else:
                    
                    energy_cutC3=float(0)                                        
            
            energy_offerB2=energy_offerB2reset
            price_offerB2=price_offerB2reset
            
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
            
#            plot, =plt.plot(x_supplyacc,y_supplyacc)
#            plot, =plt.plot(x_load,y_load)
#            plot, =plt.plot(energyMarketequilibrium,price_offerC3,'yo')
#            plot, =plt.plot(Fxi,Fyi,"--")
#                    
#            plt.xlabel('Energy C3')    
#            plt.ylabel('Price C3')
#            
#            plt.show()
            
    ################################LEVEL B2 to C4#############################
  
            if energy_offerB2 > LineCapacityC4B2:

                lineCutC4B2=energy_offerB2-LineCapacityC4B2                
                
                energy_offerB2=LineCapacityC4B2
                
            else:
                
                lineCutC4B2=0.0
                
    ###########################################################################
          
            x_values=SupplyC4df.iloc[z+1].values.tolist()
            
            ExcesssupplyC3=ExcesssupplyC3df['ExcesssupplyC3'].tolist()
            ExcesssupplyC4=ExcesssupplyC4df['ExcesssupplyC4'].tolist()
            
            if ExcesssupplyC4[z] > 0 and LastpriceSupplyC4 >  \
            price_offerB2 and ExcesssupplyC3[z] > 0:
                
                energy_offerB2= energy_offerB2/2
                
            else:
                
                energy_offerB2= 0
            
            # adding energyoffer_B2 to supply:
            
            x_values.append(energy_offerB2)
                                
            y_values=SupplyC4df.iloc[0].values.tolist()
            
            # adding price_offerB2 to supply prices:
            
            if ExcesssupplyC4[z] == 0:
                
                price_offerB2= 0        
            
            y_values.append(price_offerB2)
                    
            x_values = [x for _,x in sorted(zip(y_values,x_values))]
            
            x_values=[sum(x_values[:y]) for y in range(1, len(x_values) + 1)]
            
            y_values.sort()
            
            # supply curve:
            
            x_supplyacc=x_values*2
            x_supplyacc.sort()
    
            x_supplyacc.insert(0,0)
            x_supplyacc.insert(1,0)
            del x_supplyacc[-1]
                
            
            y_supplyacc=y_values*2
            y_supplyacc.sort()
    
            y_supplyacc.insert(0,0)
           
            # load curve:
    
            x_load=sumLoadC4df.iloc[z].tolist()
            y_load=[0,40]*len(x_load)
    
            x_load=x_load*2
            
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        
            for Z in range (1,len(x_supplyacc)):
                        
            #condition for intersection between supply and demand curve
                if x_load[0]> x_supplyacc[-Z]:
                    price_offerC4=y_supplyacc[-Z]
                    energyMarketequilibrium=x_load[0]
                    energy_offerC4=x_supplyacc[-Z+1]-x_load[0]
                    #if a condition is met, the loop stops
                    break            
    
            if energy_offerB2 < 0:
                
                energy_offerC4=float(0)
                price_offerC4=y_supplyacc[-1]
                #price_offerB2=float(0)
                
            else:
                
                pass
    
    ###############################flexible demand#############################
             
            i=0
            
            Fxi=[x_load[0],x_load[0]+50-i,x_load[0]+50-i]
            Fyi=[20-0.1*i,20-0.1*i,0]
    
            for Z in range (1,len(x_supplyacc)):
                    
                    if Fxi[1]>x_supplyacc[-Z] and Fyi[1]>=y_supplyacc[-Z+1]:
                       
                        y_me1=y_supplyacc[-Z+1]
                        x_me1=Fxi[1]
                        energy_offerC4=x_supplyacc[-Z+1]-Fxi[1]
                        
                        
                        
                        #if a condition is met, the loop stops
                        
                    
                        if y_me1==price_offerC4:
                            y_me1=price_offerC4
                            x_me1=energyMarketequilibrium=Fxi[1]
                            x_offer1=energy_offerC4=x_supplyacc[-Z+1]-Fxi[1]
                            i=i+1
                        
                        if i>=50:
                            i=50                        
                            
                        break

    ###############################energy cut##################################

            for Z in range (1,len(x_values)):
                
                if x_values[-1]> energyMarketequilibrium:
                    
                    energy_cutC4=x_values[-1]- energyMarketequilibrium
                    
                else:
                    
                    energy_cutC4=float(0)                                 
            
            energy_offerB2=energy_offerB2reset
            price_offerB2=price_offerB2reset
            
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
            
#            plot, =plt.plot(x_supplyacc,y_supplyacc)
#            plot, =plt.plot(x_load,y_load)
#            plot, =plt.plot(energyMarketequilibrium,price_offerC4,'yo')
#            plot, =plt.plot(Fxi,Fyi,"--")
#                    
#            plt.xlabel('Energy C4')     
#            plt.ylabel('Price C4')
#            
#            plt.show()
    
    ###########################################################################
    ################## L O O P ################################################
    ###########################################################################
    #################################### U P ##################################
    ###########################################################################
    ###########################################################################
    
    ##########################LEVEL C1 / C2 to B1##############################

            if energy_offerC1 > LineCapacityC1B1:

                lineCutC1B1=energy_offerC1-LineCapacityC1B1  
                
                energy_offerC1=LineCapacityC1B1
                
            else:
                
                lineCutC1B1=0.0
                                
    ###########################################################################
                
            if energy_offerC2 > LineCapacityC2B1:

                lineCutC2B1=energy_offerC2-LineCapacityC2B1  
                
                energy_offerC2=LineCapacityC2B1
                
            else:
                
                lineCutC2B1=0.0

    ###########################################################################
        
            ExcesssupplyC1C2B1=ExcesssupplyC1C2B1df['ExcesssupplyC1C2B1']\
            .tolist()
            ExcesssupplyC3C4B2=ExcesssupplyC3C4B2df['ExcesssupplyC3C4B2']\
            .tolist()
            
            x_values=SupplyC1C2B1df.iloc[z+1].values.tolist()
            
            if energy_offerC1 > 0:
                
                x_values.append(energy_offerC1)
                
            else:
                
                pass
            
            if energy_offerC2 > 0:
                
                x_values.append(energy_offerC2)
                
            else:
                
                pass
            
            if ExcesssupplyC1C2B1[z+1] > 0 and LastpriceSupplyC1C2B1v >  \
            price_offerA1 and ExcesssupplyC3C4B2[z+1] > 0:
                    
                energy_offerA1= energy_offerA1/2
                    
            else:
                    
                energy_offerA1= float(0)
                    
            x_values.append(energy_offerA1)
            
            y_values=SupplyC1C2B1df.iloc[0].values.tolist()
            
            if energy_offerC1 > 0:
                
                y_values.append(price_offerC1)
                
            else:
                
                pass
            
            if energy_offerC2 > 0:
                
                y_values.append(price_offerC2)
                
            else:
                
                pass
            
            if energy_offerA1 > 0:
                
                y_values.append(price_offerA1)
                
            else:
                
                y_values.append(float(0))
                
            x_values = [x for _,x in sorted(zip(y_values,x_values))]
            
            x_values=[sum(x_values[:y]) for y in range(1, len(x_values) + 1)]
            
            y_values.sort()
            
            # supply curve:
                
            x_supplyacc=x_values*2
            x_supplyacc.sort()
        
            x_supplyacc.insert(0,0)
            x_supplyacc.insert(1,0)
            del x_supplyacc[-1]
                    
                
            y_supplyacc=y_values*2
            y_supplyacc.sort()
        
            y_supplyacc.insert(0,0)
               
            # load curve:
        
            x_load=SumloadC1C2B1df.iloc[z].tolist()
            y_load=[0,40]*len(x_load)
        
            x_load=x_load*2
                
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                
            for Z in range (1,len(x_supplyacc)):
                            
                #condition for intersection between supply and demand curve
                if x_load[0]> x_supplyacc[-Z]:
                    price_offerB1=y_supplyacc[-Z]
                    energyMarketequilibrium=x_load[0]
                    energy_offerB1=x_supplyacc[-Z+1]-x_load[0]
                    #if a condition is met, the loop stops
                    break
                
            if energy_offerB1 < 0:
                    
                energy_offerB1=float(0)
                price_offerB1=y_supplyacc[-1]
                #price_offerB1=float(0)
                    
            else:
                    
                pass
    
    ###############################flexible demand#############################
             
            i=0
            
            Fxi=[x_load[0],x_load[0]+50-i,x_load[0]+50-i]
            Fyi=[20-0.1*i,20-0.1*i,0]
    
            for Z in range (1,len(x_supplyacc)):
                    
                    if Fxi[1]>x_supplyacc[-Z] and Fyi[1]>=y_supplyacc[-Z+1]:
                       
                        y_me1=y_supplyacc[-Z+1]
                        x_me1=Fxi[1]
                        energy_offerB1=x_supplyacc[-Z+1]-Fxi[1]
                        
                        
                        
                        #if a condition is met, the loop stops
                        
                    
                        if y_me1==price_offerB1:
                            y_me1=price_offerB1
                            x_me1=energyMarketequilibrium=Fxi[1]
                            x_offer1=energy_offerB1=x_supplyacc[-Z+1]-Fxi[1]
                            i=i+1
                        
                        if i>=50:
                            i=50                        
                            
                            
                        #if x_supplyacc[-Z] > x_me:
                         #   print(x_supplyacc[-Z])
                
                        break
                    
    ###############################energy cut##################################

            for Z in range (1,len(x_values)):
                
                if x_values[-1]> energyMarketequilibrium:
                    
                    energy_cutB1=x_values[-1]- energyMarketequilibrium
                    
                else:
                    
                    energy_cutB1=float(0)
    
                
#            energy_offerB1reset=energy_offerB1
#            price_offerB1reset=price_offerB1
#                
#            energy_offerA1=energy_offerA1reset
#            price_offerA1=price_offerA1reset
            
                                
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
                
#            plot, =plt.plot(x_supplyacc,y_supplyacc)
#            plot, =plt.plot(x_load,y_load)
#            plot, =plt.plot(energyMarketequilibrium,price_offerB1,'yo')
#            plot, =plt.plot(Fxi,Fyi,"--")
#                
#            plt.xlabel('Energy B1')    
#            plt.ylabel('Price B1')
#                        
#            plt.show()
            
    ###########################LEVEL C3 / C4 to B2#############################

            if energy_offerC3 > LineCapacityC3B2:

                lineCutC3B2=energy_offerC3-LineCapacityC3B2
            
                energy_offerC3=LineCapacityC3B2
                
            else:
                
                lineCutC3B2=0.0
                                
    ###########################################################################
                
            if energy_offerC4 > LineCapacityC4B2:

                lineCutC4B2=energy_offerC4-LineCapacityC4B2
                
                energy_offerC4=LineCapacityC4B2
                
            else:
                
                lineCutC4B2=0.0
              
    ###########################################################################
                
            ExcesssupplyC1C2B1=ExcesssupplyC1C2B1df['ExcesssupplyC1C2B1']\
            .tolist()
            ExcesssupplyC3C4B2=ExcesssupplyC3C4B2df['ExcesssupplyC3C4B2']\
            .tolist()
            
            x_values=SupplyC3C4B2df.iloc[z+1].values.tolist()
            
            if energy_offerC3 > 0:
                
                x_values.append(energy_offerC3)
                
            else:
                
                pass
            
            if energy_offerC4 > 0:
                
                x_values.append(energy_offerC4)
                
            else:
                
                pass
            
            if ExcesssupplyC3C4B2[z+1] > 0 and LastpriceSupplyC3C4B2v >  \
            price_offerA1 and ExcesssupplyC1C2B1[z+1] > 0:
                    
                energy_offerA1= energy_offerA1/2
                    
            else:
                    
                energy_offerA1= float(0)
                    
            x_values.append(energy_offerA1)
            
            y_values=SupplyC3C4B2df.iloc[0].values.tolist()
            
            if energy_offerC3 > 0:
                
                y_values.append(price_offerC3)
                
            else:
                
                pass
            
            if energy_offerC4 > 0:
                
                y_values.append(price_offerC4)
                
            else:
                
                pass
            
            if energy_offerA1 > 0:
                
                y_values.append(price_offerA1)
                
            else:
                
                y_values.append(float(0))
    
            x_values = [x for _,x in sorted(zip(y_values,x_values))]
            
            x_values=[sum(x_values[:y]) for y in range(1, len(x_values) + 1)]
            
            y_values.sort()
            
            # supply curve:
                
            x_supplyacc=x_values*2
            x_supplyacc.sort()
        
            x_supplyacc.insert(0,0)
            x_supplyacc.insert(1,0)
            del x_supplyacc[-1]
                    
                
            y_supplyacc=y_values*2
            y_supplyacc.sort()
        
            y_supplyacc.insert(0,0)
               
            # load curve:
        
            x_load=SumloadC3C4B2df.iloc[z].tolist()
            y_load=[0,40]*len(x_load)
        
            x_load=x_load*2
                
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            
                #energy_offerB1=energy_offerB1+1
                #price_offerB1=price_offerB1+1
                
            for Z in range (1,len(x_supplyacc)):
                            
                #condition for intersection between supply and demand curve
                if x_load[0]> x_supplyacc[-Z]:
                    price_offerB2=y_supplyacc[-Z]
                    energyMarketequilibrium=x_load[0]
                    energy_offerB2=x_supplyacc[-Z+1]-x_load[0]
                    #if a condition is met, the loop stops
                    break
                
            if energy_offerB2 < 0:
                    
                energy_offerB2=float(0)
                price_offerB2=y_supplyacc[-1]
                #price_offerB1=float(0)
                    
            else:
                    
                pass
    
    ###############################flexible demand#############################
             
            i=0
            
            Fxi=[x_load[0],x_load[0]+50-i,x_load[0]+50-i]
            Fyi=[20-0.1*i,20-0.1*i,0]
    
            for Z in range (1,len(x_supplyacc)):
                    
                    if Fxi[1]>x_supplyacc[-Z] and Fyi[1]>=y_supplyacc[-Z+1]:
                       
                        y_me1=y_supplyacc[-Z+1]
                        x_me1=Fxi[1]
                        energy_offerB2=x_supplyacc[-Z+1]-Fxi[1]
                        
                        
                        
                        #if a condition is met, the loop stops
                        
                    
                        if y_me1==price_offerB2:
                            y_me1=price_offerB2
                            x_me1=energyMarketequilibrium=Fxi[1]
                            x_offer1=energy_offerB2=x_supplyacc[-Z+1]-Fxi[1]
                            i=i+1
                        
                        if i>=50:
                            i=50                        
                            
                            
                        #if x_supplyacc[-Z] > x_me:
                         #   print(x_supplyacc[-Z])
                
                        break
                
    ###############################energy cut##################################

            for Z in range (1,len(x_values)):
                
                if x_values[-1]> energyMarketequilibrium:
                    
                    energy_cutB2=x_values[-1]- energyMarketequilibrium
                    
                else:
                    
                    energy_cutB2=float(0)
                    
            #energy_offerB2reset=energy_offerB2
            #price_offerB2reset=price_offerB2
                
            #energy_offerA1=energy_offerA1reset
            #price_offerA1=price_offerA1reset
            
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
                
#            plot, =plt.plot(x_supplyacc,y_supplyacc)
#            plot, =plt.plot(x_load,y_load)
#            plot, =plt.plot(energyMarketequilibrium,price_offerB2,'yo')
#            plot, =plt.plot(Fxi,Fyi,"--")
#                
#            plt.xlabel('Energy B2')    
#            plt.ylabel('Price B2')
#                        
#            plt.show()
            
            
    ###########################LEVEL B1 / B2 to A1#############################

            if energy_offerB1 > LineCapacityB1A1:
                
                lineCutB1A1=energy_offerB1-LineCapacityB1A1
            
                energy_offerB1=LineCapacityB1A1
                
            else:
                
                lineCutB1A1=0.0
                
    ###########################################################################
                
            if energy_offerB2 > LineCapacityB2A1:
                
                lineCutB2A1=energy_offerB2-LineCapacityB2A1
                
                energy_offerB2=LineCapacityB2A1
                
            else:
                
                lineCutB2A1=0.0
                
    ###########################################################################
            
            x_values=SupplyB1B2A1df.iloc[z+1].values.tolist()
            
            offer_names=list(SupplyB1B2A1df.columns.values)
                                    
            x_values.append(lineCapacities[z])
            offer_names.append('grid')
            
            if energy_offerB1 > 0:
                
                x_values.append(energy_offerB1)
                offer_names.append('energy_offerB1')
                
            else:
                
                pass
            
            if energy_offerB2 > 0:
                
                x_values.append(energy_offerB2)
                offer_names.append('energy_offerB2')
                
            else:
                
                pass
                               
            y_values=SupplyB1B2A1df.iloc[0].values.tolist()
            
            # adding grid price, price_offerB1 and price_offerB2 to supply:
            
            y_values.append(gridPrices[z])
            
            if energy_offerB1 > 0:
                
                y_values.append(price_offerB1)
                
            else:
                
                pass
            
            if energy_offerB2 > 0:
                
                y_values.append(price_offerB2)
                
            else:
                
                pass
    
            x_values= [x for _,x in sorted(zip(y_values,x_values))]
            
            x_energycut=x_values
            
            offer_names= [x for _,x in sorted(zip(y_values,offer_names))]
            
            x_values=[sum(x_values[:y]) for y in range(1, len(x_values) + 1)]
            
            y_values.sort()
        
            # supply curve:
            
            x_supplyacc=x_values*2
            x_supplyacc.sort()
    
            x_supplyacc.insert(0,0)
            x_supplyacc.insert(1,0)
            del x_supplyacc[-1]
                
            
            y_supplyacc=y_values*2
            y_supplyacc.sort()
    
            y_supplyacc.insert(0,0)
           
            # load curve:
    
            x_load=SumloadC1C2B1df.iloc[z].tolist()
            y_load=[0,40]*len(x_load)
    
            x_load=x_load*2
            
    
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
            
            #energy_offerA1=energy_offerA1+1
            #price_offerA1=price_offerA1+1
            
            for Z in range (1,len(x_supplyacc)):
                        
            #condition for intersection between supply and demand curve
            
                if x_load[0]> x_supplyacc[-Z]:
                    price_offerA1=y_supplyacc[-Z]
                    energyMarketequilibrium=x_load[0]
                    energy_offerA1=x_supplyacc[-Z+1]-x_load[0]
                    #if a condition is met, the loop stops
                    break        
    
            if energy_offerA1 < 0:
                
                energy_offerA1=float(0)
                price_offerA1=y_supplyacc[-1]
                #price_offerA1=float(0)
                
            else:
                
                pass
            
    ###############################flexible demand#############################
             
            i=0
            
            Fxi=[x_load[0],x_load[0]+50-i,x_load[0]+50-i]
            Fyi=[20-0.1*i,20-0.1*i,0]
    
            for Z in range (1,len(x_supplyacc)):
                    
                    if Fxi[1]>x_supplyacc[-Z] and Fyi[1]>=y_supplyacc[-Z+1]:
                       
                        y_me1=y_supplyacc[-Z+1]
                        x_me1=Fxi[1]
                        energy_offerA1=x_supplyacc[-Z+1]-Fxi[1]
                        
                        
                        
                        #if a condition is met, the loop stops
                        
                    
                        if y_me1==price_offerA1:
                            y_me1=price_offerA1
                            x_me1=energyMarketequilibrium=Fxi[1]
                            x_offer1=energy_offerA1=x_supplyacc[-Z+1]-Fxi[1]
                            i=i+1
                        
                        if i>=50:
                            i=50                        
                            
                            
                        #if x_supplyacc[-Z] > x_me:
                         #   print(x_supplyacc[-Z])
                
                        break
    
    
#            energy_offerA1reset=energy_offerA1
#            price_offerA1reset=price_offerA1
            
     ###############################energy cut#################################
     #grid cut and supply:
     
            i_delete= offer_names.index('grid')
            
            if gridPrices[z]== price_offerA1:
                
                grid_cut=x_values[i_delete]- energyMarketequilibrium
                
            if grid_cut > lineCapacities[z]:
                
                grid_cut= lineCapacities[z]
            
            grid_supply= lineCapacities[z] - grid_cut
            
#            grid_supply=x_values[i_delete]- grid_cut
            
            if gridPrices[z] > price_offerA1:
                
                grid_cut= x_energycut[i_delete]
                grid_supply= 0.0
                
            else:
                
                pass
            
            if gridPrices[z] < price_offerA1:
                
                grid_cut= 0.0
                grid_supply= x_energycut[i_delete]
 
                
      #########################################################################
      # energy cut:
      
            if energyMarketequilibrium > x_values[-1]:
                
                energy_cutA1=0.0
                energy_cutnameA1='NaN'
                
            else:
                
                pass
                
            if energyMarketequilibrium == x_values[-1]:
                
                energy_cutA1=0.0
                energy_cutnameA1='NaN'
                
            else:
                
                pass
            
            if energyMarketequilibrium < x_values[-1]:
                    
                energy_cutA1= x_values[-1]- energyMarketequilibrium - grid_cut\
                +lineCutC1B1+lineCutC2B1+lineCutC3B2+lineCutC4B2+lineCutB1A1+\
                lineCutB2A1                                               
                
#            for Z in range (1, len(x_values)):
#                
#                if energyMarketequilibrium == x_values[-Z]:
#                    
#                    energy_cutA1= x_values[-1]- x_values[-Z]- grid_cut
#                    #energy_cutnameA1= offer_names[-Z:-1]
#                                        
#                else:
#                    
#                    pass
                
#                if energyMarketequilibrium < x_values[-1]:
#                    
#                    energy_cutA1= x_values[-1]- energyMarketequilibrium- grid_cut
                
#                if energyMarketequilibrium < x_values[-Z] and \
#                energyMarketequilibrium > x_values[-Z-1]:
#                    
#                    energy_cutA1 = x_values[-Z] - energyMarketequilibrium - grid_cut
#                    energy_cutnameA1=offer_names[-Z-1:-1]
#                    
#                else:
#                    
#                    pass
                
                    
#            for Z in range (1,len(x_values)):
#                
#                if x_values[-Z]> energyMarketequilibrium:
#                    
#                    energy_cutnameA1= offer_names[-Z:len(x_values)]
#                
#                    if (x_values[-Z]-x_values[-Z-1])< (x_values[-Z]-\
#                       energyMarketequilibrium):
#                        
#                        energy_cutA1=x_values[-Z]- energyMarketequilibrium - grid_cut
#                        
#                    else:
#                        
#                        energy_cutA1=x_values[-Z]- energyMarketequilibrium - grid_cut
#                        
#
#                                
#            if x_values[0]> energyMarketequilibrium:
#                
#                energy_cutnameA1= offer_names[0]  
#                    
#                energy_cutA1= x_values[0]-energyMarketequilibrium - grid_cut
#            
#            if energy_cutnameA1 == 'grid':
#
#                grid_supply=energy_cutA1                
#                energy_cutA1=0
#                
#            else:
#                
#                grid_supply=0
                                            
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
            
#            plot, =plt.plot(x_supplyacc,y_supplyacc)
#            plot, =plt.plot(x_load,y_load)
#            plot, =plt.plot(energyMarketequilibrium,price_offerA1,'yo')
#            plot, =plt.plot(Fxi,Fyi,"--")
#            
#            plt.xlabel('Energy A1')    
#            plt.ylabel('Price A1')
#                    
#            plt.show()  
            
            marketPrice.append(price_offerA1)
            
            q=q+1
            
            plot, =plt.plot(x_supplyacc,y_supplyacc)
            plot, =plt.plot(x_load,y_load)
            plot, =plt.plot(energyMarketequilibrium,price_offerA1,'yo')
            plot, =plt.plot(Fxi,Fyi,"--")
            
            plt.xlabel('Energy A1')    
            plt.ylabel('Price A1')
                    
            plt.show()   
            print(cellC1.Excesssupplydf.index[z])
            
            if marketPrice[q+1] == marketPrice[q]:
                
                q= 0
                
                z+=1
                
                energy_cutA1l.append(energy_cutA1)                
                #energy_cutnameA1l.append(energy_cutnameA1)
                grid_supplyl.append(grid_supply)
                
                grid_cutl.append(grid_cut)
                last_xValuel.append(x_values[-1])
                energyMarketequilibriuml.append(energyMarketequilibrium)
                
                marketPricequilibrium.append(marketPrice[-1])
                
                marketPrice=[0,1]
                
            if z == len(gridPrices):

                for item in energy_cutA1l:
                    
                    if item < 0:
                        
                        item = 0
                        
                    else:
                        
                        pass
                
                # market equilibrium price to df:
                
                marketPricequilibriumdf=pd.DataFrame\
                (index=ExcesssupplyC1C2B1df.index)
                
                marketPricequilibriumdf.drop(marketPricequilibriumdf.index[0]\
                                             , inplace=True)
                
                marketPricequilibriumdf['market_price']=marketPricequilibrium
                
                marketPricequilibriumdf.to_csv\
                ('Results/marketPricequilibriumdf.csv', \
                 sep=',', encoding='utf-8')
                
                # energy cut to df:
                
                ###############################################################
                
                energy_cutA1df=pd.DataFrame\
                (index=ExcesssupplyC1C2B1df.index)
                
                energy_cutA1df.drop(energy_cutA1df.index[0]\
                                             , inplace=True)
                
                energy_cutA1df['energy_cutA1']=energy_cutA1l
                #energy_cutA1df['names']=energy_cutnameA1l
                
                energy_cutA1df.to_csv('Results/energy cut.csv',\
                                           sep=',', encoding='utf-8')
                 
                ###############################################################
                                
                grid_supplydf=pd.DataFrame\
                (index=ExcesssupplyC1C2B1df.index)
                
                grid_supplydf.drop(grid_supplydf.index[0]\
                                             , inplace=True)
                
                grid_supplydf['grid_supply']=grid_supplyl
                
                grid_supplydf.to_csv('Results/grid_supply.csv',\
                                           sep=',', encoding='utf-8')
                
                ###############################################################
                                
                grid_cutdf=pd.DataFrame\
                (index=ExcesssupplyC1C2B1df.index)
                
                grid_cutdf.drop(grid_supplydf.index[0]\
                                             , inplace=True)
                
                grid_cutdf['grid_cut']=grid_cutl
                
                grid_cutdf.to_csv('Results/grid_cut.csv',\
                                           sep=',', encoding='utf-8')
                
                ###############################################################                
#                
#                energy_cutB1df=pd.DataFrame\
#                (index=ExcesssupplyC1C2B1df.index)
#                
#                energy_cutB1df.drop(energy_cutB1df.index[0]\
#                                             , inplace=True)
#                
#                energy_cutB1df['energy_cutB1']=energy_cutB1l
#                
#               ###############################################################
#                
#                energy_cutB2df=pd.DataFrame\
#                (index=ExcesssupplyC1C2B1df.index)
#                
#                energy_cutB2df.drop(energy_cutB2df.index[0]\
#                                             , inplace=True)
#                
#                energy_cutB2df['energy_cutB2']=energy_cutB2l
#                
#                ###############################################################
#                
#                energy_cutC1df=pd.DataFrame\
#                (index=ExcesssupplyC1C2B1df.index)
#                
#                energy_cutC1df.drop(energy_cutC1df.index[0]\
#                                             , inplace=True)
#                
#                energy_cutC1df['energy_cutC1']=energy_cutC1l
#                
#                ###############################################################
#                
#                energy_cutC2df=pd.DataFrame\
#                (index=ExcesssupplyC1C2B1df.index)
#                
#                energy_cutC2df.drop(energy_cutC2df.index[0]\
#                                             , inplace=True)
#                
#                energy_cutC2df['energy_cutC1']=energy_cutC2l
#                
#                ###############################################################
#                
#                energy_cutC3df=pd.DataFrame\
#                (index=ExcesssupplyC1C2B1df.index)
#                
#                energy_cutC3df.drop(energy_cutC3df.index[0]\
#                                             , inplace=True)
#                
#                energy_cutC3df['energy_cutC1']=energy_cutC3l
#                
#                ###############################################################
#                
#                energy_cutC4df=pd.DataFrame\
#                (index=ExcesssupplyC1C2B1df.index)
#                
#                energy_cutC4df.drop(energy_cutC4df.index[0]\
#                                             , inplace=True)
#                
#                energy_cutC4df['energy_cutC1']=energy_cutC4l
                
    ################ R E S U L T  P R E S E N T A T I O N #####################
    # market and grid price
                
                y_marketPrice=marketPricequilibriumdf['market_price'].tolist()
    
                y_gridPrice=gridPrices
                
#                y_gridPrice=[i * tax for i in y_gridPrice]
                
                x_time=[15]
                x_time=x_time*len(gridPrices)
                x_time=[sum(x_time[:y]) for y in range(1, len(x_time) + 1)]
                
                x_time = [i * (1/60) for i in x_time]
                               
                plt.plot(x_time, y_marketPrice, x_time, y_gridPrice)
                plt.legend(['Market_Price','Grid_Price'])
                plt.grid(True)
                
                plt.xlabel('Time [h]', fontsize=14)
                plt.ylabel('Price [€Cent/ kWh]', fontsize=14)
                
                plt.savefig('plots/market_price_grid_price', dpi=None, \
                facecolor='w', edgecolor='w',\
                orientation='portrait', papertype=None, format=None,\
                transparent=False, bbox_inches=None, pad_inches=0.1,\
                frameon=None, metadata=None)
                
                plt.show()
                
     ##########################################################################
     # energy cut
          
                y_energycut=energy_cutA1df['energy_cutA1'].tolist()
                                
                x_time=[15]
                x_time=x_time*len(gridPrices)
                x_time=[sum(x_time[:y]) for y in range(1, len(x_time) + 1)]
                
                x_time = [i * (1/60) for i in x_time]
                               
                plt.plot(x_time, y_energycut)
                plt.legend(['energy cut'])
                plt.grid(True)
                
                plt.xlabel('Time [h]', fontsize=14)
                plt.ylabel('Energy [kWh]', fontsize=14)
                
                plt.savefig('plots/energy cut', dpi=None, \
                facecolor='w', edgecolor='w',\
                orientation='portrait', papertype=None, format=None,\
                transparent=False, bbox_inches=None, pad_inches=0.1,\
                frameon=None, metadata=None)
                
                plt.show()
                                                
     ##########################################################################
     # grid supply
           
                y_grid_supply=grid_supplydf['grid_supply'].tolist()
                    
                x_time=[15]
                x_time=x_time*len(gridPrices)
                x_time=[sum(x_time[:y]) for y in range(1, len(x_time) + 1)]
                
                x_time = [i * (1/60) for i in x_time]
                               
                plt.plot(x_time, y_grid_supply)
                plt.legend(['grid_supply'])
                plt.grid(True)
                
                plt.xlabel('Time [h]', fontsize=14)
                plt.ylabel('Energy [kWh]', fontsize=14)
                
                plt.savefig('plots/grid_supply', dpi=None, \
                facecolor='w', edgecolor='w',\
                orientation='portrait', papertype=None, format=None,\
                transparent=False, bbox_inches=None, pad_inches=0.1,\
                frameon=None, metadata=None)
                
                plt.show()

     ##########################################################################
     # grid cut
           
                y_gridcut=grid_cutdf['grid_cut'].tolist()
                    
                x_time=[15]
                x_time=x_time*len(gridPrices)
                x_time=[sum(x_time[:y]) for y in range(1, len(x_time) + 1)]
                
                x_time = [i * (1/60) for i in x_time]
                               
                plt.plot(x_time, y_gridcut)
                plt.legend(['grid_cut'])
                plt.grid(True)
                
                plt.xlabel('Time [h]', fontsize=14)
                plt.ylabel('Energy [kWh]', fontsize=14)
                
                plt.savefig('plots/grid_cut', dpi=None, \
                facecolor='w', edgecolor='w',\
                orientation='portrait', papertype=None, format=None,\
                transparent=False, bbox_inches=None, pad_inches=0.1,\
                frameon=None, metadata=None)
                
                plt.show()
                
     ##########################################################################
     # self_sufficiency
     
     # C1
     
                sumLoadC1l=sumLoadC1df['Sumload_C1'].tolist()
                sumSupplyC1l=sumSupplyC1df['Sumsupply_C1'].tolist()
                
                self_sufficiencyC1 = [a / b * 100 for a, b in \
                                      zip(sumSupplyC1l, sumLoadC1l)]
     # C2

                sumLoadC2l=sumLoadC2df['Sumload_C2'].tolist()
                sumSupplyC2l=sumSupplyC2df['Sumsupply_C2'].tolist()
                
                self_sufficiencyC2 = [a / b * 100 for a, b in \
                                      zip(sumSupplyC2l, sumLoadC2l)]
                
     # C3

                sumLoadC3l=sumLoadC3df['Sumload_C3'].tolist()
                sumSupplyC3l=sumSupplyC3df['Sumsupply_C3'].tolist()
                
                self_sufficiencyC3 = [a / b * 100 for a, b in \
                                      zip(sumSupplyC3l, sumLoadC3l)]
                
     # C4

                sumLoadC4l=sumLoadC4df['Sumload_C4'].tolist()
                sumSupplyC4l=sumSupplyC4df['Sumsupply_C4'].tolist()
                
                self_sufficiencyC4 = [a / b * 100 for a, b in \
                                      zip(sumSupplyC4l, sumLoadC4l)]

    # B1

                sumLoadB1l=cellB1.Sumloaddf['Sumload_B1'].tolist()
                sumSupplyB1l=cellB1.SumSupplydf['Sumsupply_B1'].tolist()
                
                self_sufficiencyB1 = [a / b * 100 for a, b in \
                                      zip(sumSupplyB1l, sumLoadB1l)]
                
    # B2

                sumLoadB2l=cellB2.Sumloaddf['Sumload_B2'].tolist()
                sumSupplyB2l=cellB2.SumSupplydf['Sumsupply_B2'].tolist()
                
                self_sufficiencyB2 = [a / b * 100 for a, b in \
                                      zip(sumSupplyB2l, sumLoadB2l)]

    # A1

                sumLoadA1l=cellA1.Sumloaddf['Sumload_A1'].tolist()
                sumSupplyA1l=cellA1.SumSupplydf['Sumsupply_A1'].tolist()
                
                self_sufficiencyA1 = [a / b * 100 for a, b in \
                                      zip(sumSupplyA1l, sumLoadA1l)]
                                
    # plot C1                                                    
                
                y_selfSufficiencyC1=self_sufficiencyC1
                    
                x_time=[15]
                x_time=x_time*len(gridPrices)
                x_time=[sum(x_time[:y]) for y in range(1, len(x_time) + 1)]
                
                x_time = [i * (1/60) for i in x_time]
                               
                plt.plot(x_time, y_selfSufficiencyC1)
                plt.legend(['self sufficiency C1'])
                plt.grid(True)
                
                plt.xlabel('Time [h]', fontsize=14)
                plt.ylabel('self sufficiency [%]', fontsize=14)
                
                plt.savefig('plots/selfSufficiencyC1', dpi=None, \
                facecolor='w', edgecolor='w',\
                orientation='portrait', papertype=None, format=None,\
                transparent=False, bbox_inches=None, pad_inches=0.1,\
                frameon=None, metadata=None)
                
                plt.show()

    # plot C2                                                    
                
                y_selfSufficiencyC2=self_sufficiencyC2
                    
                x_time=[15]
                x_time=x_time*len(gridPrices)
                x_time=[sum(x_time[:y]) for y in range(1, len(x_time) + 1)]
                
                x_time = [i * (1/60) for i in x_time]
                               
                plt.plot(x_time, y_selfSufficiencyC2)
                plt.legend(['self sufficiency C2'])
                plt.grid(True)
                
                plt.xlabel('Time [h]', fontsize=14)
                plt.ylabel('self sufficiency [%]', fontsize=14)
                
                plt.savefig('plots/selfSufficiencyC2', dpi=None, \
                facecolor='w', edgecolor='w',\
                orientation='portrait', papertype=None, format=None,\
                transparent=False, bbox_inches=None, pad_inches=0.1,\
                frameon=None, metadata=None)                
                
                plt.show()

    # plot C3                                                    
                
                y_selfSufficiencyC3=self_sufficiencyC3
                    
                x_time=[15]
                x_time=x_time*len(gridPrices)
                x_time=[sum(x_time[:y]) for y in range(1, len(x_time) + 1)]
                
                x_time = [i * (1/60) for i in x_time]
                               
                plt.plot(x_time, y_selfSufficiencyC3)
                plt.legend(['self sufficiency C3'])
                plt.grid(True)
                
                plt.xlabel('Time [h]', fontsize=14)
                plt.ylabel('self sufficiency [%]', fontsize=14)
                
                plt.savefig('plots/selfSufficiencyC3', dpi=None, \
                facecolor='w', edgecolor='w',\
                orientation='portrait', papertype=None, format=None,\
                transparent=False, bbox_inches=None, pad_inches=0.1,\
                frameon=None, metadata=None)

                plt.show()
                
    # plot C4                                                    
                
                y_selfSufficiencyC4=self_sufficiencyC4
                    
                x_time=[15]
                x_time=x_time*len(gridPrices)
                x_time=[sum(x_time[:y]) for y in range(1, len(x_time) + 1)]
                
                x_time = [i * (1/60) for i in x_time]
                               
                plt.plot(x_time, y_selfSufficiencyC4)
                plt.legend(['self sufficiency C4'])
                plt.grid(True)
                
                plt.xlabel('Time [h]', fontsize=14)
                plt.ylabel('self sufficiency [%]', fontsize=14)
                
                plt.savefig('plots/selfSufficiencyC4', dpi=None, \
                facecolor='w', edgecolor='w',\
                orientation='portrait', papertype=None, format=None,\
                transparent=False, bbox_inches=None, pad_inches=0.1,\
                frameon=None, metadata=None)
                
                plt.show()
                
    # plot B1                                                    
                
                y_selfSufficiencyB1=self_sufficiencyB1
                    
                x_time=[15]
                x_time=x_time*len(gridPrices)
                x_time=[sum(x_time[:y]) for y in range(1, len(x_time) + 1)]
                
                x_time = [i * (1/60) for i in x_time]
                               
                plt.plot(x_time, y_selfSufficiencyB1)
                plt.legend(['self sufficiency B1'])
                plt.grid(True)
                
                plt.xlabel('Time [h]', fontsize=14)
                plt.ylabel('self sufficiency [%]', fontsize=14)
                
                plt.savefig('plots/selfSufficiencyB1', dpi=None, \
                facecolor='w', edgecolor='w',\
                orientation='portrait', papertype=None, format=None,\
                transparent=False, bbox_inches=None, pad_inches=0.1,\
                frameon=None, metadata=None)
                
                plt.show()
                
    # plot B2                                                    
                
                y_selfSufficiencyB2=self_sufficiencyB2
                    
                x_time=[15]
                x_time=x_time*len(gridPrices)
                x_time=[sum(x_time[:y]) for y in range(1, len(x_time) + 1)]
                
                x_time = [i * (1/60) for i in x_time]
                               
                plt.plot(x_time, y_selfSufficiencyB2)
                plt.legend(['self sufficiency B2'])
                plt.grid(True)
                
                plt.xlabel('Time [h]', fontsize=14)
                plt.ylabel('self sufficiency [%]', fontsize=14)
                
                plt.savefig('plots/selfSufficiencyB2', dpi=None, \
                facecolor='w', edgecolor='w',\
                orientation='portrait', papertype=None, format=None,\
                transparent=False, bbox_inches=None, pad_inches=0.1,\
                frameon=None, metadata=None)
                
                plt.show()
                
    # plot A1                                                    
                
                y_selfSufficiencyA1=self_sufficiencyA1
                    
                x_time=[15]
                x_time=x_time*len(gridPrices)
                x_time=[sum(x_time[:y]) for y in range(1, len(x_time) + 1)]
                
                x_time = [i * (1/60) for i in x_time]
                               
                plt.plot(x_time, y_selfSufficiencyA1)
                plt.legend(['self sufficiency A1'])
                plt.grid(True)
                
                plt.xlabel('Time [h]', fontsize=14)
                plt.ylabel('self sufficiency [%]', fontsize=14)
                
                plt.savefig('plots/selfSufficiencyA1', dpi=None, \
                facecolor='w', edgecolor='w',\
                orientation='portrait', papertype=None, format=None,\
                transparent=False, bbox_inches=None, pad_inches=0.1,\
                frameon=None, metadata=None)
                
                plt.show()
                
    # self sufficiency list to data frame
    
    # C1:
    
                selfSufficiencyC1df=pd.DataFrame\
                (index=energy_cutA1df.index)
                selfSufficiencyC1df['selfSufficiencyC1']=self_sufficiencyC1
                
                selfSufficiencyC1df.to_csv('Results/SufficiencyC1.csv',\
                                           sep=',', encoding='utf-8')
                
    # C2:
    
                selfSufficiencyC2df=pd.DataFrame\
                (index=energy_cutA1df.index)
                selfSufficiencyC2df['selfSufficiencyC2']=self_sufficiencyC2
                
                selfSufficiencyC2df.to_csv('Results/SufficiencyC2.csv',\
                                           sep=',', encoding='utf-8')
                
    # C3:
    
                selfSufficiencyC3df=pd.DataFrame\
                (index=energy_cutA1df.index)
                selfSufficiencyC3df['selfSufficiencyC3']=self_sufficiencyC3
                
                selfSufficiencyC3df.to_csv('Results/SufficiencyC3.csv',\
                                           sep=',', encoding='utf-8')
                
    # C4:
    
                selfSufficiencyC4df=pd.DataFrame\
                (index=energy_cutA1df.index)
                selfSufficiencyC4df['selfSufficiencyC4']=self_sufficiencyC4
                
                selfSufficiencyC4df.to_csv('Results/SufficiencyC4.csv',\
                                           sep=',', encoding='utf-8')
                
    # B1:
    
                selfSufficiencyB1df=pd.DataFrame\
                (index=energy_cutA1df.index)
                selfSufficiencyB1df['selfSufficiencyB1']=self_sufficiencyB1
                
                selfSufficiencyB1df.to_csv('Results/SufficiencyB1.csv',\
                                           sep=',', encoding='utf-8')
                
    # B2:
    
                selfSufficiencyB2df=pd.DataFrame\
                (index=energy_cutA1df.index)
                selfSufficiencyB2df['selfSufficiencyB2']=self_sufficiencyB2
                
                selfSufficiencyB2df.to_csv('Results/SufficiencyB2.csv',\
                                           sep=',', encoding='utf-8')

    # A1:
    
                selfSufficiencyA1df=pd.DataFrame\
                (index=energy_cutA1df.index)
                selfSufficiencyA1df['selfSufficiencyA1']=self_sufficiencyA1
                
                selfSufficiencyA1df.to_csv('Results/SufficiencyA1.csv',\
                                           sep=',', encoding='utf-8')
                
    ###########################################################################
                
#                plot, =plt.plot(x_supplyacc,y_supplyacc)
#                plot, =plt.plot(x_load,y_load)
#                plot, =plt.plot(energyMarketequilibrium,price_offerA1,'yo')
#                plot, =plt.plot(Fxi,Fyi,"--")
#                
#                plt.xlabel('Energy A1')    
#                plt.ylabel('Price A1')
#                        
#                plt.show()  
            
     ##########################################################################
            
#                y_priceDifference=\
#                [a - b for a, b in zip(y_gridPrice, y_marketPrice)]
#                
#                plt.plot(x_time, y_priceDifference)
#                plt.legend(['Market_Price' + ' - ' + 'Grid_Price'])
#                plt.grid(True)
#                
#                plt.xlabel('Time [h]', fontsize=14)
#                plt.ylabel('Price [€Cent/ kWh]', fontsize=14)
#                
#                plt.show()
#                
                break
                
    ########################################################################### 
    ################## T H E ##################################################
    ###########################################################################
    #################################### E N D ################################
    ###########################################################################
    ###########################################################################    
        
        
        
        
