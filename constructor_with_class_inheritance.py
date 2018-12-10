'''
constructor with class inheritance
'''
# TO_DO --> Funktionen für Standardprozesse
# Wieviel wird abgeregelt und bei welcher Zelle
# Autarkiegrad
# Preis von excessSupply darf nicht höher sein als der von der höheren Zellebene

# Was passiert zwischen A1 und Netz ??
# Netzpreis variieren
# Preis vom Netz muss zurückgegeben werden

# action items:

# erstmal Programm bis zum grid zuende schreiben
# dann muss die Information des Netzpreises an die untergeordneten Zellen 
# gegeben werden. Wer muss wann wieviel abregeln wenn der Netzpreis unter dem letzten
# Preis liegt.
# Danach müssen die Schnittpunkte der Preisfindung dargestellt werden.
# def für Funktion wie z. B. merit order in CellA und dann vererben.
# Programm entrümpeln durch Funktionen.

# Flexibilitäten

# abhängige Preisprofile. z. B. Preisvelrauf abhängig vom State of Charge
# wenn voll dann gibt sie gerne Energie ab, nimmt aber nicht gerne auf
# bei halben SOC nimmt sie gerne soviel auf, wie sie abgeben würde.

# neue Klasse "flexibility" oder "storage" mit mitlaufendem State of charge (SOC)
# Biogasanlage: Preisabhängigkeit von Biogasspeicherstand. Fester Leistungswert?
# Wie soll die Biogasanlage geregelt werden?

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
        self.dfsumSupply.rename(columns={0:'sumSupply'+'_'+self.name}, inplace=True)
        
# ENERGY BALANCE:

# self.dfenergyBalance is a DataFrame that consits the supply values which are
# subtracted by the load values of the cell
        
        self.dfenergyBalance=self.dfsumSupply - self.dfsumLoad.values        

# EXCESS LOAD:

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
            
            if item < 0:
                
                item=0
            
            self.excessSupply.append(item)
            
        self.dfexcessSupply=pd.DataFrame({'excessSupply'+self.name:self.excessSupply}).set_index([self.indexS])
        

        
            
# EXCESS SUPPLY:
        
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
                    
                item=item
                    
            else:
                    
                item=0
                    
            self.excessLoad.append(item)
            
        self.dfexcessLoad=pd.DataFrame({'excessLoad'+self.name:self.excessLoad}).set_index([self.indexL])
                        
                
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

LineC1B1=powerLine('C1B1',0,0,0)
LineC2B1=powerLine('C2B1',0,0,0)
LineC3B2=powerLine('C3B2',0,0,0)
LineC4B2=powerLine('C4B2',0,0,0)
LineB1A1=powerLine('B1A1',0,0,0)
LineB2A1=powerLine('B2A1',0,0,0)
LineA1G=powerLine('A1G',0,0,0)

# grid

grid=grid(30)

# CREATING GLOBAL VARIABLES:

# grid price

gridPrice=grid.energyPrice

# load

loadA1=cellA1.dfload.drop(cellA1.dfload.index[0])
loadB1=cellB1.dfload.drop(cellB1.dfload.index[0])
loadB2=cellB2.dfload.drop(cellB2.dfload.index[0])
loadC1=cellC1.dfload.drop(cellC1.dfload.index[0])
loadC2=cellC2.dfload.drop(cellC2.dfload.index[0])
loadC3=cellC3.dfload.drop(cellC3.dfload.index[0])
loadC4=cellC4.dfload.drop(cellC4.dfload.index[0])

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
pricesB1=cellB1.dfsupplyacc.drop(cellB1.dfsupplyacc.index[1:])
pricesB2=cellB2.dfsupplyacc.drop(cellB2.dfsupplyacc.index[1:])
pricesC1=cellC1.dfsupplyacc.drop(cellC1.dfsupplyacc.index[1:])
pricesC2=cellC2.dfsupplyacc.drop(cellC2.dfsupplyacc.index[1:])
pricesC3=cellC3.dfsupplyacc.drop(cellC3.dfsupplyacc.index[1:])
pricesC4=cellC4.dfsupplyacc.drop(cellC4.dfsupplyacc.index[1:])

# supply cell level B

supplyB1=cellB1.dfsupply
supplyB2=cellB2.dfsupply

# last prices cell level C

lastPriceC1=cellC1.dfsupply.iloc[0][-1] 
lastPriceC2=cellC2.dfsupply.iloc[0][-1]
lastPriceC3=cellC3.dfsupply.iloc[0][-1]
lastPriceC4=cellC4.dfsupply.iloc[0][-1]

# PRICE DETERMINATION:


# supplyC1C2B1

supplyC1C2B1=pd.concat([supplyB1, excessSupplyC1, excessSupplyC2], axis=1)
supplyC1C2B1.iloc[-1,supplyC1C2B1.columns.get_loc('excessSupplyC2')]=lastPriceC2
supplyC1C2B1.iloc[-1,supplyC1C2B1.columns.get_loc('excessSupplyC1')]=lastPriceC1
supplyC1C2B1.sort_values('price', axis=1, ascending=True, inplace=True)

# supplyC3C4B2

supplyC3C4B2=pd.concat([supplyB2, excessSupplyC3, excessSupplyC4], axis=1)
supplyC3C4B2.iloc[-1,supplyC3C4B2.columns.get_loc('excessSupplyC4')]=lastPriceC4
supplyC3C4B2.iloc[-1,supplyC3C4B2.columns.get_loc('excessSupplyC3')]=lastPriceC3
supplyC3C4B2.sort_values('price', axis=1, ascending=True, inplace=True)

# supplyaccC1C2B1

supplyC1C2B1droppedPrice=supplyC1C2B1.drop(supplyC1C2B1.index[-1])
supplyC1C2B1acc=supplyC1C2B1droppedPrice.iloc[0:].cumsum(axis=1, skipna=True)

supplyC1C2B1droppedValues=supplyC1C2B1.drop(supplyC1C2B1.index[:-1])
supplyC1C2B1acc=pd.concat([supplyC1C2B1acc,supplyC1C2B1droppedValues])

# supplyaccC3C4B2

supplyC3C4B2droppedPrice=supplyC3C4B2.drop(supplyC3C4B2.index[-1])
supplyC3C4B2acc=supplyC3C4B2droppedPrice.iloc[0:].cumsum(axis=1, skipna=True)

supplyC3C4B2droppedValues=supplyC3C4B2.drop(supplyC3C4B2.index[:-1])
supplyC3C4B2acc=pd.concat([supplyC3C4B2acc,supplyC3C4B2droppedValues])

# set value of supply in each column by value of line capacity
# excessSupplyC1 is limited by line capacity LineC1B1
# excessSupplyC2 is limited by line capacity LineC2B2
# excessSupplyC3 is limited by line capacity LineC3B2
# excessSupplyC4 is limited by line capacity LineC4B2
# excessSupplyB1 is limited by line capacity LineB1A1
# excessSupplyB2 is limited by line capacity LineB2A1
# excessSupplyA1 is limited by line capacity LineA1grid

# concatenation loadC1, loadC2, loadB1 and sum of laod

sumLoadB1l=[]

loadC1C2B1=pd.concat([excessLoadC1, excessLoadC2, loadB1], axis=1)

for index, row in loadC1C2B1.iterrows():
    
    sumLB1=loadC1C2B1.sum(axis=1)
    sumLoadB1l.append(sumLB1)
            
    break
               
    kB1=pd.Series(sumLoadB1)
    rB1=kB1.to_dict()
        
    sumLoadB1=pd.DataFrame.from_dict(rB1, orient='columns')
    sumLoadB1.rename(columns={0:'sumLoadB1'}, inplace=True)

# concatenation loadC3, loadC4, loadB2

sumLoadB2l=[]

loadC3C4B2=pd.concat([excessLoadC3, excessLoadC4, loadB2], axis=1)

for index, row in loadC3C4B2.iterrows():
    
    sumLB2=loadC3C4B2.sum(axis=1)
    sumLoadB2l.append(sumLB2)
            
    break
               
    kB2=pd.Series(sumLoadB2)
    rB2=kB2.to_dict()
        
    sumLoadB2=pd.DataFrame.from_dict(rB2, orient='columns')
    sumLoadB2.rename(columns={0:'sumLoadB2'}, inplace=True)
    
# sum supply cell level B

sumSupplyB1l=[]

for index, row in supplyC1C2B1.iterrows():
    
    sumSB1=supplyC1C2B1.sum(axis=1)
    sumSupplyB1l.append(sumSB1)
    
    break

    jB1=pd.Series(sumSupplyB1l)
    sB1=jB1.to_dict()
    
    sumSupplyB1=pd.DataFrame.from_dict(sB1, orient='columns')
    sumSupplyB1.rename(columns={0:'sumSupplyB1'}, inplace=True)


sumSupplyB2l=[]

for index, row in supplyC3C4B2.iterrows():
    
    sumSB2=supplyC3C4B2.sum(axis=1)
    sumSupplyB2l.append(sumSB2)
    
    break

    jB2=pd.Series(sumSupplyB2l)
    sB2=jB2.to_dict()
    
    sumSupplyB2=pd.DataFrame.from_dict(sB2, orient='columns')
    sumSupplyB2.rename(columns={0:'sumSupplyB2'}, inplace=True)
    
# energy balance cell level B
    
energyBalanceB1=sumSupplyB1 - sumLoadB1.values
energyBalanceB2=sumSupplyB2 - sumLoadB2.values

# excessLoadB1

excessLoadB1l=[]

indexYB1=loadC1C2B1.index.tolist()

tempLB1=energyBalanceB1['sumSupply_B1'].tolist()

for item in tempLB1:
    
    if item < 0:
        
        item=item
        
    else:
        
        item=0
            
    excessLoadB1l.append(item)
    
excessLoadB1=pd.DataFrame({'excessLoadB1':excessLoadB1l}).set_index([indexYB1])

# excessSupplyB1

excessSupplyB1l=[]

indexZB1=loadC1C2B1.index.tolist()

tempSB1=energyBalanceB1['sumSupply_B1'].tolist()

for item in tempSB1:
    
    if item > 0:
        
        item=item
        
    else:
        
        item=0
        
    excessSupplyB1l.append(item)
    
excessSupplyB1=pd.DataFrame({'excessSupplyB1':excessSupplyB1l}).set_index([indexZB1])

# excessLoadB2

excessLoadB2l=[]

indexYB2=loadC3C4B2.index.tolist()

tempLB2=energyBalanceB2['sumSupply_B2'].tolist()

for item in tempLB2:
    
    if item < 0:
        
        item=item
        
    else:
        
        item=0
            
    excessLoadB2l.append(item)
    
excessLoadB2=pd.DataFrame({'excessLoadB2':excessLoadB2l}).set_index([indexYB2])

# excessSupplyB2

excessSupplyB2l=[]

indexZB2=loadC3C4B2.index.tolist()

tempSB2=energyBalanceB2['sumSupply_B2'].tolist()

for item in tempSB2:
    
    if item > 0:
        
        item=item
        
    else:
        
        item=0
        
    excessSupplyB2l.append(item)
    
excessSupplyB2=pd.DataFrame({'excessSupplyB2':excessSupplyB2l}).set_index([indexZB2])


        


  
    

   
