# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 15:34:16 2018

@author: lucas
"""
import matplotlib.pyplot as plt
import pylab as pyl
import csv

x = []
y = []

x1 = [40,40]
y1 = [20,0]

with open('test.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
      
    for row in plots:
        x.append(int(row[0]))
        y.append(int(row[1]))
        
        '''x1.append(int(row[0]))
        y1.append(int(row[1]))'''



x = [0,x[0],x[0],x[0]+x[1],x[0]+x[1],x[0]+x[1]+x[2]]
y = [y[0],y[0],y[1],y[1],y[2],y[2],]




print (x)
print (y)

print (x1)
print (y1)
        
plt.plot(x,y, label='Loaded from file!') 
'''plt.plot(x1,y1 label='Loaded from file!')'''
plt.plot(x1,y1)
   

plt.xlabel('Energy')    
plt.ylabel('Price')
plt.title('Cell A')
plt.show()


