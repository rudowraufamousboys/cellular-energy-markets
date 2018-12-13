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
        self.dfsumLoad.rename(columns={0:'sumLoad'+'_'+self.name}, inplace=True)
        
# SUM OF SUPPLY & LOAD:

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
        self.dfsumSupply.rename(columns={0:'sumSupply'+'_'+self.name}, inplace=True)

# ENERGY BALANCE:

# self.dfenergyBalance is a DataFrame that consits the supply values which are
# subtracted by the load values of the cell
        
        self.dfenergyBalance=self.dfsumSupply - self.dfsumLoad.values        

# EXCESS SUPPLY:

# self.indexS is getting the index of one of the DataFrames which have 
# the date and time as index. The so generated list has the price at first 
# position and will be dropped by self.indexL.pop(0).
# To seperate the positive of the negative values in the self.dfenergyBalance
# there will be a for loop for the items in self.tempL, which is a temporary
# list containing the energyBalance values in column [0].
        
        self.indexS=self.dfload.index.tolist()
        
        self.indexS.pop(0)
        
        self.tempS=self.dfenergyBalance['sumSupply'+'_'+self.name].tolist()
        
        for item in self.tempS:
            
            if item > 0:
                
                item=item
                
            else:
                
                item=0
            
            self.excessSupply.append(item)
            
        self.dfexcessSupply=pd.DataFrame({'excessSupply'+'_'+self.name:self.excessSupply}).set_index([self.indexS])
        


# EXCESS LOAD:
        
# self.indexL is getting the index of one of the DataFrames which has 
# the date and time as index. The so generated list has the price at first 
# position and will be dropped by self.indexL.pop(0).
# To seperate the positive of the negative values in the self.dfenergyBalance
# there will be a for loop for the items in self.tempL, which is a temporary
# list containing the energyBalance values in column [0].

        
        self.indexL=self.dfsupply.index.tolist()
        
        self.indexL.pop(0)
            
        self.tempL=self.dfenergyBalance['sumSupply'+'_'+self.name].tolist()
            
        for item in self.tempL:
                
            if item < 0:
                    
                item=item*-1
                    
            else:
                    
                item=0
                    
            self.excessLoad.append(item)
            
        self.dfexcessLoad=pd.DataFrame({'excessLoad'+'_'+self.name:self.excessLoad}).set_index([self.indexL])
                        
                
class cellTypeB(cellTypeA):
    
    level=2
    
    def __init__(self, name):
        
        super().__init__(name)
        
class cellTypeC(cellTypeA):
    
    level=3
    
    def __init__(self,name):
        
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

# EXCESS SUPPLY CELL LEVEL C

# assumption: excessSupplyC1(C2) has the highest price of energy generation in C1(C2)

# taking the last price [-1] in the first row [0]:

lastPricesupplyC1=cellC1.dfsupplyacc.iloc[0][-1] 
lastPricesupplyC2=cellC2.dfsupplyacc.iloc[0][-1]

# making excessSupplyC1(C2) global

excessSupplyC1=cellC1.dfexcessSupply
excessSupplyC2=cellC2.dfexcessSupply

# creating a dict out of the last price C1(C2). The index is 'price':

lastPricesupplyC1d={'price':lastPricesupplyC1}
lastPricesupplyC2d={'price':lastPricesupplyC2}

# creating a df out of the dictionaries lastPriceC1(C2)d:

lastPricesupplyC1df=pd.DataFrame.from_dict(lastPricesupplyC1d, orient='index')
lastPricesupplyC2df=pd.DataFrame.from_dict(lastPricesupplyC2d, orient='index')

# rename colum '0' to 'excessSupply_C1' in order to append excessSupplyC1(C2)
# to lastPriceC1(C2)df

lastPricesupplyC1df.rename(columns={0:'excessSupply_C1'}, inplace=True)
excessSupplyC1=lastPricesupplyC1df.append(excessSupplyC1)

lastPricesupplyC2df.rename(columns={0:'excessSupply_C2'}, inplace=True)
excessSupplyC2=lastPricesupplyC2df.append(excessSupplyC2)

# assumption: excessSupplyC3(C4) has the highest price of energy generation in C3(C4)

# taking the last price [-1] in the first row [0]:

lastPricesupplyC3=cellC3.dfsupplyacc.iloc[0][-1] 
lastPricesupplyC4=cellC4.dfsupplyacc.iloc[0][-1]

# making excessSupplyC3(C4) global

excessSupplyC3=cellC3.dfexcessSupply
excessSupplyC4=cellC4.dfexcessSupply

# creating a dict out of the last price C3(C4). The index is 'price':

lastPricesupplyC3d={'price':lastPricesupplyC3}
lastPricesupplyC4d={'price':lastPricesupplyC4}

# creating df out of the dictionaries lastPriceC3(C4)d:

lastPricesupplyC3df=pd.DataFrame.from_dict(lastPricesupplyC3d, orient='index')
lastPricesupplyC4df=pd.DataFrame.from_dict(lastPricesupplyC4d, orient='index')

# rename colum '0' to 'excessSupply_C3(C4)' in order to append excessSupplyC3(C4)
# tp lastPriceC1(C2)df

lastPricesupplyC3df.rename(columns={0:'excessSupply_C3'}, inplace=True)
excessSupplyC3=lastPricesupplyC3df.append(excessSupplyC3)

lastPricesupplyC4df.rename(columns={0:'excessSupply_C4'}, inplace=True)
excessSupplyC4=lastPricesupplyC4df.append(excessSupplyC4)

# ADDING EXCESS SUPPLY C1 & C2 (C3 & C4) TO SUPPLY B1 (B2) AND SORT BY 'PRICE':

supplyC1C2B1=pd.concat([cellB1.dfsupply,excessSupplyC1,excessSupplyC2],axis=1)
supplyC1C2B1.sort_values('price', axis=1, ascending=True, inplace=True)

supplyC3C4B2=pd.concat([cellB2.dfsupply,excessSupplyC3,excessSupplyC4],axis=1)
supplyC3C4B2.sort_values('price', axis=1, ascending=True, inplace=True)

# ACCUMULATE SUPPLY VALUES:

supplyC1C2B1acc=supplyC1C2B1.iloc[1:].cumsum(axis=1, skipna=True)
supplyC3C4B2acc=supplyC3C4B2.iloc[1:].cumsum(axis=1, skipna=True)

# since the price is getting lost it has to be added seperatly
# dropping values in supplyC1C2B1 and supplyC3C4B2:

supplyPricesC1C2B1=supplyC1C2B1.drop(supplyC1C2B1.index[1:])
supplyPricesC3C4B2=supplyC3C4B2.drop(supplyC3C4B2.index[1:])

# append supplyPricesC1C2B1(C3C4B2) to supplyC1C2B1(C4C4B2)acc:

supplyC1C2B1acc=supplyPricesC1C2B1.append(supplyC1C2B1acc)
supplyC3C4B2acc=supplyPricesC3C4B2.append(supplyC3C4B2acc)

# ADDING LOADS OF C1(C3), C2(C4) and B1(B2):

# just in case that a load price is needed:

lastPriceloadC1=cellC1.dfload.iloc[0][0]
lastPriceloadC2=cellC2.dfload.iloc[0][0]

lastPriceloadC3=cellC3.dfload.iloc[0][0]
lastPriceloadC4=cellC4.dfload.iloc[0][0]

# creating dict out of lastPriceloadC1 - C4:

lastPriceloadC1d={'price':lastPriceloadC1}
lastPriceloadC2d={'price':lastPriceloadC2}

lastPriceloadC3d={'price':lastPriceloadC3}
lastPriceloadC4d={'price':lastPriceloadC4}

# creating df out of lastPriceloadC1-C4d

lastPriceloadC1df=pd.DataFrame.from_dict(lastPriceloadC1d, orient='index')
lastPriceloadC1df.rename(columns={0:'excessLoad_C1'},inplace=True)

lastPriceloadC2df=pd.DataFrame.from_dict(lastPriceloadC2d, orient='index')
lastPriceloadC2df.rename(columns={0:'excessLoad_C2'},inplace=True)

lastPriceloadC3df=pd.DataFrame.from_dict(lastPriceloadC3d, orient='index')
lastPriceloadC3df.rename(columns={0:'excessLoad_C3'},inplace=True)

lastPriceloadC4df=pd.DataFrame.from_dict(lastPriceloadC4d, orient='index')
lastPriceloadC4df.rename(columns={0:'excessLoad_C4'},inplace=True)

# append excessLoadC1 - C4 to lastPriceloadC1 - C4:

excessLoadC1=lastPriceloadC1df.append(cellC1.dfexcessLoad)
excessLoadC2=lastPriceloadC2df.append(cellC2.dfexcessLoad)
excessLoadC3=lastPriceloadC3df.append(cellC3.dfexcessLoad)
excessLoadC4=lastPriceloadC4df.append(cellC4.dfexcessLoad)

# loadC1C2B1 and loadC3B2:

loadC1C2B1=pd.concat([excessLoadC1,excessLoadC2,cellB1.dfload],axis=1)
loadC1C2B1.sort_values('price', axis=1, ascending=False, inplace=True)

loadC3C4B2=pd.concat([excessLoadC3,excessLoadC4,cellB2.dfload],axis=1)
loadC3C4B2.sort_values('price', axis=1, ascending=False, inplace=True)


# energyBalanceC1C2B1 / energyBalanceC3C4B2

energyBalanceC1C2B1=supplyC1C2B1.iloc[1:] - loadC1C2B1.iloc[1:].values
energyBalanceC3C4B2=supplyC3C4B2.iloc[1:] - loadC3C4B2.iloc[1:].values

# sumSupplyC1C2B1(C3C4B2) out of energyBlanaceC1C2B1(C3C4B2)

sumSupplyC1C2B1=energyBalanceC1C2B1.sum(axis=1)
sumSupplyC1C2B1=sumSupplyC1C2B1.to_frame()
sumSupplyC1C2B1.rename(columns={0:'sumSupply_C1C2B1'},inplace=True)

sumSupplyC1C2B1l=sumSupplyC1C2B1['sumSupply_C1C2B1'].tolist()

sumSupplyC3C4B2=energyBalanceC3C4B2.sum(axis=1)
sumSupplyC3C4B2=sumSupplyC3C4B2.to_frame()
sumSupplyC3C4B2.rename(columns={0:'sumSupply_C3C4B2'},inplace=True)

sumSupplyC3C4B2l=sumSupplyC3C4B2['sumSupply_C3C4B2'].tolist()

# excessSupply and excessLoad for cell level B:

excessLoadC1C2B1l=[]
excessLoadC3C4B2l=[]

for item in sumSupplyC1C2B1l:
    
    if item < 0:
        item=item*-1
    else:
        item=0
    excessLoadC1C2B1l.append(item)
    
for item in sumSupplyC3C4B2l:
    
    if item < 0:
        item=item*-1
    else:
        item=0
    excessLoadC3C4B2l.append(item)
     
excessSupplyC1C2B1l=[]
excessSupplyC3C4B2l=[]

for item in sumSupplyC1C2B1l:
    
    if item > 0:
        item=item
    else:
        item=0
    excessSupplyC1C2B1l.append(item)
    
for item in sumSupplyC3C4B2l:
    
    if item > 0:
        item=item
    else:
        item=0
    excessSupplyC3C4B2l.append(item)
    
# drop first column of sumSupplyC1C2B1(C3C4B2) to get Index
    
excessLoadC1C2B1=sumSupplyC1C2B1.drop(['sumSupply_C1C2B1'], axis=1)
excessLoadC3C4B2=sumSupplyC3C4B2.drop(['sumSupply_C3C4B2'], axis=1)

excessSupplyC1C2B1=sumSupplyC1C2B1.drop(['sumSupply_C1C2B1'], axis=1)
excessSupplyC3C4B2=sumSupplyC3C4B2.drop(['sumSupply_C3C4B2'], axis=1)

excessLoadC1C2B1['excessLoad_C1C2B1']=excessLoadC1C2B1l
excessLoadC3C4B2['excessLoad_C3C4B2']=excessLoadC3C4B2l

excessSupplyC1C2B1['excessSupply_C1C2B1']=excessSupplyC1C2B1l
excessSupplyC3C4B2['excessSupply_C3C4B2']=excessSupplyC3C4B2l

# last prices supply cell level B

# value:

lastPricesupplyC1C2B1=supplyC1C2B1acc.iloc[0][-1]
lastPricesupplyC3C4B2=supplyC3C4B2acc.iloc[0][-1]

# value to dict:

lastPricesupplyC1C2B1d={'price':lastPricesupplyC1C2B1}
lastPricesupplyC3C4B2d={'price':lastPricesupplyC3C4B2}

# dict to df:

lastPricesupplyC1C2B1df=pd.DataFrame.from_dict(lastPricesupplyC1C2B1d, orient='index')
lastPricesupplyC1C2B1df.rename(columns={0:'excessSupply_C1C2B1'}, inplace=True)

lastPricesupplyC3C4B2df=pd.DataFrame.from_dict(lastPricesupplyC3C4B2d, orient='index')
lastPricesupplyC3C4B2df.rename(columns={0:'excessSupply_C3C4B2'}, inplace=True)

# prices for excess load cell level B:

firstPriceloadC1C2B1=loadC1C2B1.iloc[0][0]
firstPriceloadC3C4B2=loadC3C4B2.iloc[0][0]

# value to dict:

firstPriceloadC1C2B1d={'price':firstPriceloadC1C2B1}
firstPriceloadC1C2B1d={'price':firstPriceloadC3C4B2}

# dict to df:

firstPriceloadC1C2B1df=pd.DataFrame.from_dict(firstPriceloadC1C2B1d, orient='index')
firstPriceloadC1C2B1df.rename(columns={0:'excessLoad_C1C2B1'}, inplace=True)

firstPriceloadC3C4B2df=pd.DataFrame.from_dict(firstPriceloadC1C2B1d, orient='index')
firstPriceloadC3C4B2df.rename(columns={0:'excessLoad_C3C4B2'}, inplace=True)

# append prices to supply and load on cell level B:

excessSupplyC1C2B1=lastPricesupplyC1C2B1df.append(excessSupplyC1C2B1)
excessSupplyC3C4B2=lastPricesupplyC3C4B2df.append(excessSupplyC3C4B2)

excessLoadC1C2B1=firstPriceloadC1C2B1df.append(excessLoadC1C2B1)
excessLoadC3C4B2=firstPriceloadC3C4B2df.append(excessLoadC3C4B2)

# CELL LEVEL A

# ADDING EXCESS SUPPLY C1C2B1 & C3C4B2 TO SUPPLY A1 AND SORT BY 'PRICE':

supplyC1C2C3C4B1B2A1=pd.concat([cellA1.dfsupply,excessSupplyC1C2B1,excessSupplyC3C4B2], axis=1)
supplyC1C2C3C4B1B2A1.sort_values('price', axis=1, ascending=True, inplace=True)

# ACCUMULATE SUPPLY VALUES:

supplyC1C2C3C4B1B2A1acc=supplyC1C2C3C4B1B2A1.iloc[1:].cumsum(axis=1, skipna=True)

# since the price is getting lost it has to be added seperatly
# dropping values in supplyC1C2C3C4B1B2:

supplyPricesC1C2C3C4B1B2A1=supplyC1C2C3C4B1B2A1.drop(supplyC1C2C3C4B1B2A1.index[1:])

# append supplyPricesC1C2C3C4B1B2A1 to supplyC1C2C3C4B1B2A1acc:

supplyC1C2C3C4B1B2A1acc=supplyPricesC1C2C3C4B1B2A1.append(supplyC1C2C3C4B1B2A1acc)

# ADDING EXCESS LOAD C1C2B1 & C3C4B2 TO LOAD A1 AND SORT BY 'PRICE':

loadC1C2C3C4B1B2A1=pd.concat([cellA1.dfload,excessLoadC1C2B1,excessLoadC3C4B2], axis=1)
loadC1C2C3C4B1B2A1.sort_values('price', axis=1, ascending=False, inplace=True)








    
    








