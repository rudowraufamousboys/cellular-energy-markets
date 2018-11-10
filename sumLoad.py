sumLoad=[] #empty list to store series (index, sum)

load=cellC4.dfload #getting cellC4.dfload global

dropPriceofLoad=load.drop('price', axis=0) #.drop('price', axis=0) deletes the row with the index 'price'

for index, row in dropPriceofLoad.iterrows(): # iterration
    
    sum=dropPriceofLoad.sum(axis=1)
    sumLoad.append(sum)

print(sumLoad)

  
