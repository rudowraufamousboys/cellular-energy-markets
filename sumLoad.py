'''
zum Testen mit Liste / für Programm values in einen data frame einfügen mit Zeitstempel
'''
sumLoad=[]

for i in dfLoad[1]:

  sum=dfload.sum(axis=0, level=1)
  sumLoad.append(sum)

print(sumLoad)

'''
iterrows() allows you to efficiently loop over your DataFrame rows as (index, Series) pairs. 
In other words, it gives you (index, row) tuples as a result:
'''

for index, row in dfload.iterrows():
  
  sum=dfload.sum(axis=0, level=1)
  sumLoad.append(sum)

  
