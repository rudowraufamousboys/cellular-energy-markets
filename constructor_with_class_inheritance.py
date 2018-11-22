'''
constructor with class inheritance
'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from itertools import islice


class grid:
    
    level=0
    
    def __init__(self, energyPrice):
        
        self.energyPrice=energyPrice
        

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

       
        self.dfload = pd.read_csv(self.name + '/' + 'load.csv')
        self.dfload.set_index('snapshot', inplace=True)
        self.dfload.sort_values('price', axis=1, ascending=False, inplace=True)
        
        self.dfsupply = pd.read_csv(self.name + '/' + 'supply.csv')
        self.dfsupply.set_index('snapshot', inplace=True)
        self.dfsupply.sort_values('price', axis=1, ascending=True, inplace=True)

# ACCUMULATED SUPPLY CURVE:
        
# following code accumulates the supply values in ascending order by the method
# .cumsum .iloc[1:] makes sure that the price (which is in row 0) is skipped
# self.dfsupplydropped drops every row except the price row for appending to
# dfsupplycumsum which in return gives the self.dfsupplyacc, the accumulated 
# supply curve with the price in the first row.
      
        self.dfsupplycumsum=self.dfsupply.iloc[1:].cumsum(axis=1, skipna=True)
        self.dfsupplydropped=self.dfsupply.drop(self.dfsupply.index[1:])
        self.dfsupplyacc=self.dfsupplydropped.append(self.dfsupplycumsum)      

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
        self.dropPriceofLoad=self.dfload.drop('price', axis=0)
        
        
        for index, row in self.dropPriceofLoad.iterrows():
            
            self.sumL=self.dropPriceofLoad.sum(axis=1)
            self.sumLoad.append(self.sumL)
            
            break
               
        self.k=pd.Series(self.sumLoad)
        self.r=self.k.to_dict()
        
        self.dfsumLoad=pd.DataFrame.from_dict(self.r, orient='columns')
        #self.dfsumLoad.rename(columns={0:'sumLoad'+'_'+self.name}, inplace=True)

# SUM OF SUPPLY:

# see: SUM OF LOAD
        
        self.sumSupply=[]
        self.dropPriceofSupply=self.dfsupply.drop('price', axis=0)


        for index, row in self.dropPriceofSupply.iterrows():
            
            self.sumS=self.dropPriceofSupply.sum(axis=1)
            self.sumSupply.append(self.sumS)
            
            break
                
        self.j=pd.Series(self.sumSupply)
        self.s=self.j.to_dict()
        
        self.dfsumSupply=pd.DataFrame.from_dict(self.s, orient='columns')
        #self.dfsumSupply.rename(columns={0:'sumSupply'+'_'+self.name}, inplace=True)
        
# ENERGY BALANCE:

# self.dfenergyBalance is a DataFrame that consits the supply values which are
# subtracted by the load values of the cell
        
        self.dfenergyBalance=self.dfsumSupply - self.dfsumLoad.values
        
# EXCESS SUPPLY:

# self.indexS is getting the index of one of the DataFrames which has 
# the date and time as index. The so generated list has the price at first 
# position and will be dropped by self.indexL.pop(0).
# To seperate the positive of the negative values in the self.dfenergyBalance
# there will be a for loop for the items in self.tempL, which is a temporary
# list containing the energyBalance values in column [0].
        
        self.indexS=self.dfload.index.tolist()
        
        self.indexS.pop(0)
        
        self.tempS=self.dfenergyBalance[0].tolist()
        
        for item in self.tempS:
            
            if item < 0:
                
                item=0
            
            self.excessSupply.append(item)
            
        self.dfexcessSupply=pd.DataFrame({'excess_Supply':self.excessSupply}).set_index([self.indexS])

        
            
# EXCESS LOAD:
        
# self.indexL is getting the index of one of the DataFrames which have 
# the date and time as index. The so generated list has the price at first 
# position and will be dropped by self.indexL.pop(0).
# To seperate the positive of the negative values in the self.dfenergyBalance
# there will be a for loop for the items in self.tempL, which is a temporary
# list containing the energyBalance values in column [0].

        
        self.indexL=self.dfsupply.index.tolist()
        
        self.indexL.pop(0)
            
        self.tempL=self.dfenergyBalance[0].tolist()
            
        for item in self.tempL:
                
            if item < 0:
                    
                item=item
                    
            else:
                    
                item=0
                    
            self.excessLoad.append(item)
            
        self.dfexcessLoad=pd.DataFrame({'excess_Load':self.excessLoad}).set_index([self.indexL])
                        
                
class cellTypeB(cellTypeA):
    
    level=2
    
    def __init__(self, name):
        
        super().__init__(name)
        
class cellTypeC(cellTypeA):
    
    level=3
    
    def __init__(self,name):
        
        super().__init__(name)
    
# CREATING OBJECTS:

cellA1=cellTypeA('A1')
cellB1=cellTypeB('B1')
cellB2=cellTypeB('B2')
cellC1=cellTypeC('C1')
cellC2=cellTypeC('C2')
cellC3=cellTypeC('C3')
cellC4=cellTypeC('C4')


# CREATING GLOBAL VARIABLES:

# sumLoad

sumLoadA1=cellA1.dfsumLoad
sumLoadB1=cellB1.dfsumLoad
sumLoadB2=cellB2.dfsumLoad
sumLoadC1=cellC1.dfsumLoad
sumLoadC2=cellC2.dfsumLoad
sumLoadC3=cellC3.dfsumLoad
sumLoadC4=cellC4.dfsumLoad

# excessLoad

excessLoadA1=cellA1.dfexcessLoad
excessLoadB1=cellB1.dfexcessLoad
excessLoadB2=cellB2.dfexcessLoad
excessLoadC1=cellC1.dfexcessLoad
excessLoadC2=cellC2.dfexcessLoad
excessLoadC3=cellC3.dfexcessLoad
excessLoadC4=cellC4.dfexcessLoad

# sumSupply

sumSupplyA1=cellA1.dfsumSupply
sumSupplyB1=cellB1.dfsumSupply
sumSupplyB2=cellB2.dfsumSupply
sumSupplyC1=cellC1.dfsumSupply
sumSupplyC2=cellC2.dfsumSupply
sumSupplyC3=cellC3.dfsumSupply
sumSupplyC4=cellC4.dfsumSupply

# excessSupply

excessSupplyA1=cellA1.dfexcessSupply
excessSupplyB1=cellB1.dfexcessSupply
excessSupplyB2=cellB2.dfexcessSupply
excessSupplyC1=cellC1.dfexcessSupply
excessSupplyC2=cellC2.dfexcessSupply
excessSupplyC3=cellC3.dfexcessSupply
excessSupplyC4=cellC4.dfexcessSupply

# supplyacc

supplyaccA1=cellA1.dfsupplyacc.drop(cellA1.dfsupplyacc.index[0])
supplyaccB1=cellB1.dfsupplyacc.drop(cellB1.dfsupplyacc.index[0])
supplyaccB2=cellB2.dfsupplyacc.drop(cellB2.dfsupplyacc.index[0])
supplyaccC1=cellC1.dfsupplyacc.drop(cellC1.dfsupplyacc.index[0])
supplyaccC2=cellC2.dfsupplyacc.drop(cellC2.dfsupplyacc.index[0])
supplyaccC3=cellC3.dfsupplyacc.drop(cellC3.dfsupplyacc.index[0])
supplyaccC4=cellC4.dfsupplyacc.drop(cellC4.dfsupplyacc.index[0])

# prices sorted

pricesA1=cellA1.dfsupplyacc.drop(cellA1.dfsupplyacc.index[1:])
pricesA1=cellB1.dfsupplyacc.drop(cellB1.dfsupplyacc.index[1:])
pricesA1=cellB2.dfsupplyacc.drop(cellB2.dfsupplyacc.index[1:])
pricesA1=cellC1.dfsupplyacc.drop(cellC1.dfsupplyacc.index[1:])
pricesA1=cellC2.dfsupplyacc.drop(cellC2.dfsupplyacc.index[1:])
pricesA1=cellC3.dfsupplyacc.drop(cellC3.dfsupplyacc.index[1:])
pricesA1=cellC4.dfsupplyacc.drop(cellC4.dfsupplyacc.index[1:])



   
