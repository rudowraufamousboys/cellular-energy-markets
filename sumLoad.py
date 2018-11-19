        self.sumLoad=[]
        self.dropPriceofLoad=self.dfload.drop('price', axis=0)
        
        
        for index, row in self.dropPriceofLoad.iterrows():
            
            self.sum=self.dropPriceofLoad.sum(axis=1)
            self.sumLoad.append(self.sum)
            
            break
                
        self.k=pd.Series(self.sumLoad)
        self.r=self.k.to_dict()
        
        self.sumLoaddf=pd.DataFrame.from_dict(self.r, orient='columns')
        self.sumLoaddf.rename(columns={0:'sumLoad'+'_'+self.name}, inplace=True) 

  
