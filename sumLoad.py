'''
zum Testen mit Liste / für Programm values in einen data frame einfügen mit Zeitstempel
'''
sumLoad=[]

for i in dfLoad[1]:

  sum=dfload.sum(axis=0, level=1)
  sumLoad.append(sum)

print(sumLoad)
