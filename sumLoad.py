sumLoad=[]

load=cellC4.dfload

dropPriceofLoad=load.drop('price', axis=0)

i=len(dropPriceofLoad)

for index, row in dropPriceofLoad.iterrows():
    
    sum=dropPriceofLoad.sum(axis=1)
    sumLoad.append(sum)
    
    if i == len(dropPriceofLoad):
        break
    
k=pd.Series(sumLoad)
 
r=k.to_dict() 

sumLoaddf=pd.DataFrame.from_dict(r, orient='columns')
sumLoaddf=sumLoaddf.rename()

  
