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
LastpriceSupplyC3C4B2v=SupplyC3C4B2accdf.iloc[0][-1]

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
lineCapacities=grid.Linecapacity['gridsupply'].tolist()

# delete first value in list for it is the price

del lineCapacities[0]

for item in lineCapacities:
    
    float(item)

# data frames cell level C:

SupplyC1df=cellC1.Supplydf
SupplyC2df=cellC2.Supplydf
SupplyC3df=cellC3.Supplydf
SupplyC4df=cellC4.Supplydf

sumLoadC1df=cellC1.Sumloaddf
sumLoadC2df=cellC2.Sumloaddf
sumLoadC3df=cellC3.Sumloaddf
sumLoadC4df=cellC4.Sumloaddf

ExcesssupplyC1df=cellC1.Excesssupplydf
ExcesssupplyC1df.drop(ExcesssupplyC1df.index[0], inplace=True)

ExcesssupplyC2df=cellC2.Excesssupplydf
ExcesssupplyC2df.drop(ExcesssupplyC2df.index[0], inplace=True)

ExcesssupplyC3df=cellC3.Excesssupplydf
ExcesssupplyC3df.drop(ExcesssupplyC3df.index[0], inplace=True)

ExcesssupplyC4df=cellC4.Excesssupplydf
ExcesssupplyC4df.drop(ExcesssupplyC4df.index[0], inplace=True)

LastpriceSupplyC1=cellC1.LastpriceSupplydf.iloc[0,0]
LastpriceSupplyC2=cellC2.LastpriceSupplydf.iloc[0,0]
LastpriceSupplyC3=cellC3.LastpriceSupplydf.iloc[0,0]
LastpriceSupplyC4=cellC4.LastpriceSupplydf.iloc[0,0]


# list of market equilibrium price:
priceMarketequilibriumA1l=[]

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


 
for z in range (len(gridPrices)):
    
############################################################################### 
###################L O O P ####################################################
###############################################################################
#####################################D O W N###################################
###############################################################################
###############################################################################
    
###########################LEVEL GRID to A#####################################    
    
        x_values=SupplyB1B2A1df.iloc[z+1].values.tolist()
        
        # adding grid capacity, energyoffer_B1 and energyoffer_B2 to supply:
        
        x_values.append(lineCapacities[z])
       
#        if energy_offerB1 > 0:
#            
#            x_values.append(energy_offerB1)
#            
#        else:
#            
#            pass
#        
#        if energy_offerB2 > 0:
#        
#            x_values.append(energy_offerB2)
#            
#        else:
#            
#            pass
                    
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
        

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
        
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
        
###############################flexible demand#################################
         
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


        #energy_offerA1reset=energy_offerA1
        #price_offerA1reset=price_offerA1
        
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
        
        plot, =plt.plot(x_supplyacc,y_supplyacc)
        plot, =plt.plot(x_load,y_load)
        plot, =plt.plot(energyMarketequilibrium,price_offerA1,'yo')
        plot, =plt.plot(Fxi,Fyi,"--")
        
        plt.xlabel('Energy A1')    
        plt.ylabel('Price A1')
                
        plt.show()
              
################################LEVEL A to B1##################################
                                
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
            
        x_values = [x for _,x in sorted(zip(y_values,x_values))]
            
        x_values=[sum(x_values[:y]) for y in range(1, len(x_values) + 1)]
                                
        y_values=SupplyC1C2B1df.iloc[0].values.tolist()

                        
        if ExcesssupplyC1C2B1[z+1] == 0:
                
            price_offerA1= 0
               
        else:
                
            pass
            
        y_values.append(price_offerA1)
            
#        if energy_offerC1 > 0:
#                
#            y_values.append(price_offerC1)
#                
#        else:
#                
#            pass
#            
#        if energy_offerC2 > 0:
#                
#            y_values.append(price_offerC2)
#                
#        else:
#                
#            pass
                    
            
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
            
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
            #energy_offerB1=energy_offerB1+1
            #price_offerB1=price_offerB1+1
            
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

###############################flexible demand#################################
         
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

            
        #energy_offerB1reset=energy_offerB1
        #price_offerB1reset=price_offerB1
            
        #energy_offerA1=energy_offerA1reset
        #price_offerA1=price_offerA1reset
        
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
            
        plot, =plt.plot(x_supplyacc,y_supplyacc)
        plot, =plt.plot(x_load,y_load)
        plot, =plt.plot(energyMarketequilibrium,price_offerB1,'yo')
        plot, =plt.plot(Fxi,Fyi,"--")
            
        plt.xlabel('Energy B1')    
        plt.ylabel('Price B1')
                    
        plt.show()
            
################################LEVEL A to B2##################################
                                
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
            
        x_values = [x for _,x in sorted(zip(y_values,x_values))]
            
        x_values=[sum(x_values[:y]) for y in range(1, len(x_values) + 1)]
                                
        y_values=SupplyC3C4B2df.iloc[0].values.tolist()
            
        # adding grid price, price_offerB1 and price_offerB2 to supply:
            
        if ExcesssupplyC3C4B2[z+1] == 0:
                
            price_offerA1= 0
               
        else:
                
            pass
            
        y_values.append(price_offerA1)
            
#        if energy_offerC1 > 0:
#                
#            y_values.append(price_offerC1)
#                
#        else:
#                
#            pass
#            
#        if energy_offerC2 > 0:
#                
#            y_values.append(price_offerC2)
#                
#        else:
#                
#            pass
                    
            
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
            
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
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
            #price_offerB2=float(0)
                
        else:
                
            pass
            
###############################flexible demand#################################
         
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
            
        #energy_offerB2reset=energy_offerB2
        #price_offerB2reset=price_offerB2
            
        #energy_offerA1=energy_offerA1reset
        #price_offerA1=price_offerA1reset
        
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
            
        plot, =plt.plot(x_supplyacc,y_supplyacc)
        plot, =plt.plot(x_load,y_load)
        plot, =plt.plot(energyMarketequilibrium,price_offerB2,'yo')
        plot, =plt.plot(Fxi,Fyi,"--")
            
        plt.xlabel('Energy B2')    
        plt.ylabel('Price B2')
                    
        plt.show()
              
################################LEVEL B1 to C1#################################
        
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
        
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        #energy_offerC1=energy_offerC1+1
        #price_offerC1=price_offerC1+1
        
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
            
###############################flexible demand#################################
         
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
        
        #energy_offerB1=energy_offerB1reset
        #price_offerB1=price_offerB1reset
        
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
        
        plot, =plt.plot(x_supplyacc,y_supplyacc)
        plot, =plt.plot(x_load,y_load)
        plot, =plt.plot(energyMarketequilibrium,price_offerC1,'yo')
        plot, =plt.plot(Fxi,Fyi,"--")
        
        
        plt.xlabel('Energy C1')    
        plt.ylabel('Price C1')
                
        plt.show()
       
################################LEVEL B1 to C2#################################
        
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
        
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        #energy_offerC2=energy_offerC2+1
        #price_offerC2=price_offerC2+1
        
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

###############################flexible demand#################################
         
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
        
        #energy_offerB1=energy_offerB1reset
        #price_offerB1=price_offerB1reset
        
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
        
        plot, =plt.plot(x_supplyacc,y_supplyacc)
        plot, =plt.plot(x_load,y_load)
        plot, =plt.plot(energyMarketequilibrium,price_offerC2,'yo')
        plot, =plt.plot(Fxi,Fyi,"--")
        
        plt.xlabel('Energy C2')    
        plt.ylabel('Price C2')
                
        plt.show()

################################LEVEL B2 to C3#################################
        
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
        

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        #energy_offerC3=energy_offerC3+1
        #price_offerC3=price_offerC3+1
        
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

###############################flexible demand#################################
         
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
        
        #energy_offerB2=energy_offerB2reset
        #price_offerB2=price_offerB2reset
        
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
        
        plot, =plt.plot(x_supplyacc,y_supplyacc)
        plot, =plt.plot(x_load,y_load)
        plot, =plt.plot(energyMarketequilibrium,price_offerC3,'yo')
        plot, =plt.plot(Fxi,Fyi,"--")
                
        plt.xlabel('Energy C3')    
        plt.ylabel('Price C3')
        
        plt.show()
        
################################LEVEL B2 to C4#################################
        
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
        
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        
        #energy_offerC3=energy_offerC3+1
        #price_offerC3=price_offerC3+1
        
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

###############################flexible demand#################################
         
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
                        
                        
                    #if x_supplyacc[-Z] > x_me:
                     #   print(x_supplyacc[-Z])
            
                    break                                 
        
        #energy_offerB2=energy_offerB2reset
        #price_offerB2=price_offerB2reset
        
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!        
        
        plot, =plt.plot(x_supplyacc,y_supplyacc)
        plot, =plt.plot(x_load,y_load)
        plot, =plt.plot(energyMarketequilibrium,price_offerC4,'yo')
        plot, =plt.plot(Fxi,Fyi,"--")
                
        plt.xlabel('Energy C4')     
        plt.ylabel('Price C4')
        
        plt.show()

############################################################################### 
###################L O O P ####################################################
###############################################################################
#####################################U P#######################################
###############################################################################
############################################################################### 

###########################LEVEL C1 / C2 to B1#################################

# x_values=SupplyC1C2B1df.iloc[z+1].values.tolist()
# SupplyC1C2B1 + energy_offerC1 + energy_offcerC2 + energy_offerA1

###########################LEVEL B1 / B2 to A1#################################

# x_values=SupplyB1B2A1df.iloc[z+1].values.tolist()
# energy_offerB1 + energy_offcerB2 + linecapacity + gridPrice
