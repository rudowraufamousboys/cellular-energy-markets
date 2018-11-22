# -*- coding: utf-8 -*-
"""
Created on Mon Nov 19 14:57:35 2018

@author: lucas
"""

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
        
        self.dfload = pd.read_csv(self.name + '/' + 'load.csv')
        self.dfload.set_index('snapshot', inplace=True)
        self.dfload.sort_values('price', axis=1, ascending=False, inplace=True)
        
        self.dfsupply = pd.read_csv(self.name + '/' + 'supply.csv')
        self.dfsupply.set_index('snapshot', inplace=True)
        self.dfsupply.sort_values('price', axis=1, ascending=True, inplace=True)
        
      
        self.dfsupplycumsum=self.dfsupply.iloc[1:].cumsum(axis=1, skipna=True)
        self.dfsupplydropped=self.dfsupply.drop(self.dfsupply.index[1:])
        self.dfsupplyacc=self.dfsupplydropped.append(self.dfsupplycumsum)      # accumulated supply curve with price in last row!!!
        
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

class cellTypeB(cellTypeA):
    
    level=2
    
    def __init__(self, name):
        
        super().__init__(name)
        
class cellTypeC(cellTypeA):
    
    level=3
    
    def __init__(self,name):
        
        super().__init__(name)
    


cellA1=cellTypeA('A1')
cellB1=cellTypeB('B1')
cellB2=cellTypeB('B2')
cellC1=cellTypeC('C1')
cellC2=cellTypeC('C2')
cellC3=cellTypeC('C3')
cellC4=cellTypeC('C4')

'''
dfsumSupply = sum of supply for each row of the dfsupply data frame
dfsumLoad = sum of load for each row of the dfload data frame

dfsupplyacc= accumulated supply curve 
'''

'''
form local to global
'''

sumLoadA1=cellA1.dfsumLoad
sumSupplyA1=cellA1.dfsumSupply
supplyaccA1=cellA1.dfsupplyacc

sumLoadB1=cellB1.dfsumLoad
sumSupplyB1=cellB1.dfsumSupply
supplyaccB1=cellB1.dfsupplyacc

sumLoadB2=cellB2.dfsumLoad
sumSupplyB2=cellB2.dfsumSupply
supplyaccB2=cellB2.dfsupplyacc

sumLoadC1=cellC1.dfsumLoad
sumSupplyC1=cellC1.dfsumSupply
supplyaccC1=cellC1.dfsupplyacc

sumLoadC2=cellC2.dfsumLoad
sumSupplyC2=cellC2.dfsumSupply
supplyaccC2=cellC2.dfsupplyacc

sumLoadC3=cellC3.dfsumLoad
sumSupplyC3=cellC3.dfsumSupply
supplyaccC3=cellC3.dfsupplyacc

sumLoadC4=cellC4.dfsumLoad
sumSupplyC4=cellC4.dfsumSupply
supplyaccC4=cellC4.dfsupplyacc


#Plotten

#Cell C1
name='C1'
print(supplyaccC1)
print(sumLoadC1)
print(supplyaccC1['PV']-sumLoadC1['sumLoad_C1'])


x=supplyaccC1['Wind']
x1=supplyaccC1['PV']
#x2=supplyaccC4['Gasturbine']
#Difference=supplyaccC1['PV']-sumLoadC1['sumLoad_C1']

print(x)
print(x1)
#print(x2)

y=(x[0])                                                                        #Price Wind
print(y)

y1= (x1[0])                                                                     #Price PV
print(y1)

D=sumLoadC1['sumLoad_C1']                                                       #Demand of the cell


i = len(x)-1
print(i)


for z in range(1,i):                                                            #loop for plots
    xi=[0,0,x[z],x[z],x1[z]]
    yi=[0,y,y,y1,y1]
    Di=[D[z],D[z]]
    Yi=[0,y1*1.2]
    #Differencei=[Difference[i]]
    plt.plot(xi,yi)
    plt.plot(Di,Yi)
    plt.xlabel('Energy')    
    plt.ylabel('Price')
    plt.title(name)
    plt.axis([0,300, \
              0,y1*1.2])
    plt.show()
    print (xi)
    print (yi)

   #print (Differencei)
 
#Cell C2
#next 
name='C2'
print(supplyaccC2)
print(sumLoadC2)
print(supplyaccC2['PV']-sumLoadC2['sumLoad_C2'])


x=supplyaccC2['Wind']
x1=supplyaccC2['PV']
#x2=supplyaccC4['Gasturbine']
#Difference=supplyaccC1['PV']-sumLoadC1['sumLoad_C1']

print(x)
print(x1)
#print(x2)

y=(x[0])                                                                        #Price Wind
print(y)

y1= (x1[0])                                                                     #Price PV
print(y1)

D=sumLoadC2['sumLoad_C2']                                                       #Demand of the cell


i = len(x)-1

for z in range(1,i):                                                            #loop for plots
    xi=[0,0,x[z],x[z],x1[z]]
    yi=[0,y,y,y1,y1]
    Di=[D[z],D[z]]
    Yi=[0,y1*1.2]
    #Differencei=[Difference[i]]
    plt.plot(xi,yi)
    plt.plot(Di,Yi)
    plt.xlabel('Energy')    
    plt.ylabel('Price')
    plt.title(name)
    plt.axis([0,300, \
              0,y1*1.2])
    plt.show()
    print (xi)
    print (yi)
    #print (Differencei)
    
    
