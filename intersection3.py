# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 13:33:50 2018

@author: lucas
"""

import matplotlib.pyplot as plt
import csv

x = []
y = []

x1 = []
y1 = []

with open('supply.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    next(plots)
      
    for row in plots:
        x.append(int(row[0]))
        y.append(int(row[1]))
        
with open('demand.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    next(plots)

    for row in plots:
        x1.append(int(row[0]))
        y1.append(int(row[1]))
        
        
x = [0,x[0],x[0],x[0]+x[1],x[0]+x[1],x[0]+x[1]+x[2]]
y = [y[0],y[0],y[1],y[1],y[2],y[2]]

x1 = [x1[0],x1[0]]
y1 = [y1[0],0]


i = len(x)-1
z = 0 

for z in range(i):
    
    if x1[0]> x[z] and x1[0] <= x[z+1]:
        y2 = y[z]
        x2 = x1[0]
        
        
plt.plot(x2,y2,"yo")    
plt.plot(x,y, label='Loaded from file!') 
plt.plot(x1,y1)
  

plt.xlabel('Energy')    
plt.ylabel('Price')
plt.title('Cell A')
plt.show()

print ("traded amount: " + str(x2)+ ", market price:" + str(y2))


