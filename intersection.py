# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 13:33:50 2018

@author: lucas
"""

import matplotlib.pyplot as plt
import csv

x = []
y = []

x1 = [31]
y1 = [20]


with open('test.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    next(plots)
      
    for row in plots:
        x.append(int(row[0]))
        y.append(int(row[1]))
        
        '''x1.append(int(row[0]))
        y1.append(int(row[1]))'''



x = [0,x[0],x[0],x[0]+x[1],x[0]+x[1],x[0]+x[1]+x[2]]
y = [y[0],y[0],y[1],y[1],y[2],y[2],]

x1 = [0,x1[0],x1[0]]
y1 = [y1[0],y1[0],0]
     
   
    
if x1[0]> x[0] and x1[0] <= x[1]:
    y2 = (y[0])
    x2 = x1[0]
    
if x1[0]> x[1] and x1[0] <= x[2]:
    y2 = (y[1])
    x2 = x1[0]

if x1[0]> x[2] and x1[0] <= x[3]:
    y2 = (y[2])
    x2 = x1[0]

if x1[0]> x[3] and x1[0] <= x[4]:
    y2 = (y[3])
    x2 = x1[0]

if x1[0]> x[4] and x1[0] <= x[5]:
    y2 = (y[4])
    x2 = x1[0]


    
plt.plot(x2,y2,"yo")         
plt.plot(x,y, label='Loaded from file!') 
plt.plot(x1,y1)
  

plt.xlabel('Energy')    
plt.ylabel('Price')
plt.title('Cell A')
plt.show()

print ("traded amount: " + str(x2)+ ", market price:" + str(y2))


