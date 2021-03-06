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

gridPricesdf=grid.Energyprices
Linecapacitydf=grid.Linecapacity

gridpricesl=gridPricesdf.iloc[:,0].tolist()

# list of market equilibrium price:
priceMarketequilibriumA1l=[]
# list of market equilibrium energy:
energyOfferA1l=[0]

listname = ['C1','C2','B1','C3','C4','B2','A1']
name= listname[6]
pricecurve=[]

#for z in range (SupplyB1B2A1df.index.size)--> 0;95
for z in range(SupplyB1B2A1df.index.size-1):
        
        
        # first value of line capacity is a dyanmic price that will be replaced
        # each time step in order to add the grid to the supplyacc of cell level:
        Linecapacitydf.iloc[0,0]=gridpricesl[z]
        # the lince capacity plus dynamic price is added to the supply of cell level A:        
        SupplyB1B2A1dfi=pd.concat((SupplyB1B2A1df, Linecapacitydf), axis=1)
        # sorting the columns by price:
        SupplyB1B2A1dfi.sort_values('price', axis=1, ascending=True, inplace=True)
        # creating price df by dropping the supply values:
        SupplypricesB1B2A1i=SupplyB1B2A1dfi.drop(SupplyB1B2A1dfi.index[1])
        # accumulate supply including line capacity between cell level A and grid:
        SupplyB1B2A1accdfi=SupplyB1B2A1dfi.iloc[z+1:].cumsum(axis=1, skipna=True)
        #SupplyB1B2A1accdfi=SupplypricesB1B2A1i.append(SupplyB1B2A1accdfi)
        
        #Supply graph
        #x values for plot 
        x_values=SupplyB1B2A1accdfi.iloc[0].values.tolist()
        
        #double x values for steps
        x_supplyacc=x_values*2
        x_supplyacc.sort()
        #insert (0,0) for start point of the supply graph
        x_supplyacc.insert(0,0)
        x_supplyacc.insert(1,0)
        del x_supplyacc[-1]
        
        #y values for plot
        y_values=SupplypricesB1B2A1i.iloc[0].values.tolist()
        
        #double y values for plot
        y_supplyacc=y_values*2
        y_supplyacc.sort()
        #insert (0,0) for start point of the supply graph
        y_supplyacc.insert(0,0)
        
        #Demand graph
        x_load=SumloadB1B2A1df.iloc[z].tolist()
        y_load=[0,40]*len(x_load)
        #double x values for demand plot
        x_load=x_load*2
        
        for Z in range (1,len(x_supplyacc)):
                
                #condition for intersection between supply and demand curve
            if x_load[0]> x_supplyacc[-Z]:
                priceMarketequilibrium=y_supplyacc[-Z]
                energyMarketequilibrium=x_load[0]
                energy_offerA1=x_supplyacc[-Z+1]-x_load[0]
                #if a condition is met, the loop stops
                break
        
        supplyplot1, =plt.plot(x_supplyacc[0:3],y_supplyacc[0:3])
        supplyplot2, =plt.plot(x_supplyacc[2:5],y_supplyacc[2:5])
        supplyplot3, =plt.plot(x_supplyacc[4:7],y_supplyacc[4:7])
        supplyplot4, =plt.plot(x_supplyacc[6:9],y_supplyacc[6:9])
        supplyplot5, =plt.plot(x_supplyacc[8:11],y_supplyacc[8:11])
            
            
        #supplyplot, =plt.plot(x_supplyacc,y_supplyacc)
        demandplot, =plt.plot(x_load,y_load)
        meplot, =plt.plot(energyMarketequilibrium,priceMarketequilibrium,'yo')
        #flexplot, =plt.plot(Fxi,Fyi,"--")
       
        
        #legend for the plots
        plt.legend([supplyplot1,supplyplot2,supplyplot3,supplyplot4,supplyplot5, demandplot,(meplot)],[SupplyB1B2A1accdfi.columns[0],SupplyB1B2A1accdfi.columns[1],SupplyB1B2A1accdfi.columns[2],SupplyB1B2A1accdfi.columns[3],SupplyB1B2A1accdfi.columns[4],'Demand','Market Equilibrium'],loc='center left', bbox_to_anchor=(1, 0.5))
        
        #label for the axes
        plt.xlabel('Energy')    
        plt.ylabel('Price')
        
        #name of the graphs with name of the cell and time
        plt.title(name+' '+ SupplyB1B2A1accdf.index[z+1])
                        # plt.axis([0,300, \
                        #       0,y1[0]*1.2])
        plt.show()
        
        # appending market equilibrium price to a list:
        priceMarketequilibriumA1l.append(priceMarketequilibrium)
        # appending market equilibrium energy to a list:
        energyOfferA1l.append(energy_offerA1)
        
        pricecurve.append(priceMarketequilibrium)
        #print(pricecurve)
        
        SupplyB1B2A1dfi=SupplyB1B2A1df
        

        
#plt.plot(pricecurve)
#plt.xlabel('Timesteps')    
#plt.ylabel('Price')
#plt.show()

#next

        
        #name=listname[+1]
        #print(SupplyB1B2A1accdf.index[z+1])
        
        #plt.savefig('plot'+str(z)+'.pdf')   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        #plt.pause(2.5)
        
energyofferCelllevelA1=pd.DataFrame(index=ExcesssupplyC1C2B1df.index)
energyofferCelllevelA1['energyofferCelllevelA1']=energyOfferA1l
        
#besser wäre es nicht erst due liste zu füllen sondern für jeden zeitschritt einzuordnen !!!!!

        
listname = ['C1','C2','B1','C3','C4','B2','A1']
pricecurve=[]            
        
        
        
              





for z in range (SupplyB1B2A1df.index.size-1):
    
    name= listname[2]
        

    SupplyC1C2B1dfi=pd.concat((SupplyC1C2B1df, energyofferCelllevelA1), axis=1)
    SupplyC3C4B2dfi=pd.concat((SupplyC3C4B2df, energyofferCelllevelA1), axis=1)
    

    if LastpriceSupplyC1C2B1df.iloc[0,0] and LastpriceSupplyC3C4B2df.iloc[0,0] \
    > priceMarketequilibrium and ExcesssupplyC1C2B1l[z] > 0 and \
    ExcesssupplyC3C4B2l[z] > 0:
        
        SupplyC1C2B1dfi.iloc[z,-1]=(SupplyC1C2B1dfi.iloc[z,-1]/2)
        SupplyC3C4B2dfi.iloc[z,-1]=(SupplyC3C4B2dfi.iloc[z,-1]/2)
        print('1') 
        
     
                                        
    elif LastpriceSupplyC1C2B1df.iloc[0,0] > priceMarketequilibrium and \
    ExcesssupplyC1C2B1l[z] > 0:
        
        SupplyC1C2B1dfi.iloc[z,-1]=(SupplyC1C2B1dfi.iloc[z,-1])
        SupplyC3C4B2dfi.iloc[z,-1]=(SupplyC3C4B2dfi.iloc[z,-1]*0)
        print('2')
       
    
    elif LastpriceSupplyC3C4B2df.iloc[0,0] > priceMarketequilibrium and \
    ExcesssupplyC3C4B2l[z] > 0:
        
        SupplyC3C4B2dfi.iloc[z,-1]=(SupplyC3C4B2dfi.iloc[z,-1])
        SupplyC1C2B1dfi.iloc[z,-1]=(SupplyC1C2B1dfi.iloc[z,-1]*0)       
        print('3')

    else:
        print('Keine Iteration notwendig!') 
        
    
  

    
    SupplyC1C2B1dfi.iloc[0,-1]=priceMarketequilibriumA1l[z] #In die letzte Spalte und erste Zeile wird der ME drangehangen
    SupplyC3C4B2dfi.iloc[0,-1]=priceMarketequilibriumA1l[z]
    
    SupplyC1C2B1dfi.sort_values('price', axis=1, ascending=True, inplace=True)
    SupplyC3C4B2dfi.sort_values('price', axis=1, ascending=True, inplace=True)
    
    SupplypricesC1C2B1i=SupplyC1C2B1dfi.drop(SupplyC1C2B1dfi.index[1:])
    SupplypricesC3C4B2i=SupplyC3C4B2dfi.drop(SupplyC3C4B2dfi.index[1:])
    
    SupplyC1C2B1accdfi=SupplyC1C2B1dfi.iloc[z+1:].cumsum(axis=1, skipna=True)
    SupplyC3C4B2accdfi=SupplyC3C4B2dfi.iloc[z+1:].cumsum(axis=1, skipna=True)
    
    
    x_values=SupplyC1C2B1accdfi.iloc[0].values.tolist()
        
        #double x values for steps
    x_supplyacc=x_values*2
    x_supplyacc.sort()
    #insert (0,0) for start point of the supply graph
    x_supplyacc.insert(0,0)
    x_supplyacc.insert(1,0)
    del x_supplyacc[-1]
        
    #y values for plot
    y_values=SupplypricesC1C2B1i.iloc[0].values.tolist()
        
    #double y values for plot
    y_supplyacc=y_values*2
    y_supplyacc.sort()
    #insert (0,0) for start point of the supply graph
    y_supplyacc.insert(0,0)
        
    #Demand graph
    x_load=SumloadC1C2B1df.iloc[z].tolist()
    y_load=[0,40]*len(x_load)
    #double x values for demand plot
    x_load=x_load*2
    
    for Z in range (1,len(x_supplyacc)):
                
        #condition for intersection between supply and demand curve
        if x_load[0]> x_supplyacc[-Z]:
            priceMarketequilibrium=y_supplyacc[-Z]
            energyMarketequilibrium=x_load[0]
            energy_offerB1=x_supplyacc[-Z+1]-x_load[0]
            #if a condition is met, the loop stops
            break
        
    supplyplot1, =plt.plot(x_supplyacc[0:3],y_supplyacc[0:3])
    supplyplot2, =plt.plot(x_supplyacc[2:5],y_supplyacc[2:5])
    supplyplot3, =plt.plot(x_supplyacc[4:7],y_supplyacc[4:7])
    supplyplot4, =plt.plot(x_supplyacc[6:9],y_supplyacc[6:9])
    supplyplot5, =plt.plot(x_supplyacc[8:11],y_supplyacc[8:11])
            
            
    #supplyplot, =plt.plot(x_supplyacc,y_supplyacc)
    demandplot, =plt.plot(x_load,y_load)
    meplot, =plt.plot(energyMarketequilibrium,priceMarketequilibrium,'yo')
    #flexplot, =plt.plot(Fxi,Fyi,"--")
       
        
    #legend for the plots
    plt.legend([supplyplot1,supplyplot2,supplyplot3,supplyplot4,supplyplot5, demandplot,(meplot)],[SupplyC1C2B1accdfi.columns[0],SupplyC1C2B1accdfi.columns[1],SupplyC1C2B1accdfi.columns[2],SupplyC1C2B1accdfi.columns[3],SupplyC1C2B1accdfi.columns[4],'Demand','Market Equilibrium'],loc='center left', bbox_to_anchor=(1, 0.5))
        
    #label for the axes
    plt.xlabel('Energy')    
    plt.ylabel('Price')
        
    #name of the graphs with name of the cell and time
    plt.title(name+' '+ SupplyC1C2B1accdf.index[z+1])
                        # plt.axis([0,300, \
                        #       0,y1[0]*1.2])
    plt.show()
        
    # appending market equilibrium price to a list:
    
    #priceMarketequilibriumA1l.append(priceMarketequilibrium)
    
    # appending market equilibrium energy to a list:
    
    #energyOfferA1l.append(energy_offerA1)
        
    #pricecurve.append(priceMarketequilibrium)
    
    #print(pricecurve)
        
#plt.plot(pricecurve)
        
        #name=listname[+1]
        #print(SupplyB1B2A1accdf.index[z+1])
        
        #plt.savefig('plot'+str(z)+'.pdf')   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        #plt.pause(2.5)
    name= listname[5]
    
    x_values=SupplyC3C4B2accdfi.iloc[0].values.tolist()
        
        #double x values for steps
    x_supplyacc=x_values*2
    x_supplyacc.sort()
    #insert (0,0) for start point of the supply graph
    x_supplyacc.insert(0,0)
    x_supplyacc.insert(1,0)
    del x_supplyacc[-1]
        
    #y values for plot
    y_values=SupplypricesC3C4B2i.iloc[0].values.tolist()
        
    #double y values for plot
    y_supplyacc=y_values*2
    y_supplyacc.sort()
    #insert (0,0) for start point of the supply graph
    y_supplyacc.insert(0,0)
        
    #Demand graph
    x_load=SumloadC3C4B2df.iloc[z].tolist()
    y_load=[0,40]*len(x_load)
    #double x values for demand plot
    x_load=x_load*2
    
    for Z in range (1,len(x_supplyacc)):
                
        #condition for intersection between supply and demand curve
        if x_load[0]> x_supplyacc[-Z]:
            priceMarketequilibrium=y_supplyacc[-Z]
            energyMarketequilibrium=x_load[0]
            energy_offerB2=x_supplyacc[-Z+1]-x_load[0]
            #if a condition is met, the loop stops
            break
        
    supplyplot1, =plt.plot(x_supplyacc[0:3],y_supplyacc[0:3])
    supplyplot2, =plt.plot(x_supplyacc[2:5],y_supplyacc[2:5])
    supplyplot3, =plt.plot(x_supplyacc[4:7],y_supplyacc[4:7])
    supplyplot4, =plt.plot(x_supplyacc[6:9],y_supplyacc[6:9])
    supplyplot5, =plt.plot(x_supplyacc[8:11],y_supplyacc[8:11])
            
            
    #supplyplot, =plt.plot(x_supplyacc,y_supplyacc)
    demandplot, =plt.plot(x_load,y_load)
    meplot, =plt.plot(energyMarketequilibrium,priceMarketequilibrium,'yo')
    #flexplot, =plt.plot(Fxi,Fyi,"--")
       
        
    #legend for the plots
    plt.legend([supplyplot1,supplyplot2,supplyplot3,supplyplot4,supplyplot5, demandplot,(meplot)],[SupplyC3C4B2accdfi.columns[0],SupplyC3C4B2accdfi.columns[1],SupplyC3C4B2accdfi.columns[2],SupplyC3C4B2accdfi.columns[3],SupplyC3C4B2accdfi.columns[4],'Demand','Market Equilibrium'],loc='center left', bbox_to_anchor=(1, 0.5))
        
    #label for the axes
    plt.xlabel('Energy')    
    plt.ylabel('Price')
        
    #name of the graphs with name of the cell and time
    plt.title(name+' '+ SupplyC3C4B2accdf.index[z+1])
                        # plt.axis([0,300, \
                        #       0,y1[0]*1.2])
    plt.show()
        
    # appending market equilibrium price to a list:
    
    #priceMarketequilibriumA1l.append(priceMarketequilibrium)
    
    # appending market equilibrium energy to a list:
    
    #energyOfferA1l.append(energy_offerA1)
        
    #pricecurve.append(priceMarketequilibrium)
    
    #print(pricecurve)
        
#plt.plot(pricecurve)
        
        #name=listname[+1]
        #print(SupplyB1B2A1accdf.index[z+1])
        
        #plt.savefig('plot'+str(z)+'.pdf')   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        #plt.pause(2.5)
    

    

