import pandas as pd
import os

class bank():

    def Lloyrd (dfn): # done
        dfn = dfn.dropna(axis=1,how='all')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        dfn.drop(columns=['Account Number','Balance','Transaction Type','Sort Code'],errors='ignore',inplace=True) 
        dfn['Transaction Description'] = dfn['Transaction Description'].astype(str)
        return dfn
    
    def HSBC(dfn):
        dfn = dfn.dropna(axis=1,how='all')
        pass

    def Chase(dfn):
        dfn = dfn.dropna(axis=1,how='all')
        pass

class func():
    # Required input: Newfile, Filelocation 
    

    def catconcat(): #done
        cato = 'pages/Temp/Record/DiscriptionCategories.csv'
        cato = pd.read_csv(cato)
        catn = "pages/Temp/Excel/DiscriptionCategories.xlsx"
        catn = pd.read_excel(catn)
        catn= catn.drop(columns=['Debit Amount','Credit Amount'])
        catn = catn.dropna(how="any")
        cat = pd.concat([catn,cato], ignore_index=True)
        return cat

    def dfmerge(df,cat): #done

        MergeTable = pd.merge(df,
                        cat,
                        on = 'Transaction Description',
                        how = 'left',
                        suffixes = ('','_DROP')).filter(regex='^(?!.*_DROP)')

        MergeTable.drop_duplicates(ignore_index=True, inplace=True)
        catn = MergeTable[MergeTable['Categories'].isna()]
        catn = catn.drop_duplicates(ignore_index=True)
        catn = catn.loc[:, ~catn.columns.str.contains('^Unnamed')]
        MergeTable = MergeTable.loc[:, ~MergeTable.columns.str.contains('^Unnamed')]
        
        return catn,cat,MergeTable

    def Backup(file_path): #done
        file_name = os.path.basename(file_path)
        backup_path = 'pages/Temp/Record/Backup/'+str(file_name)
        os.rename(file_path,backup_path)
        return None

    def load_data():
        pass

    # def read_dfo(self):
    #     return dfo


# dfn = df = pd.read_csv(dfn,encoding='latin1',index_col=[0])
# dfnpath = 'pages/Temp/Excel/15101160_20220519_0443.xlsx'
# dfopath = 'pages/Temp/Record/Data.csv'
# catnpath = 'pages/Temp/Excel/DiscriptionCategories.xlsx'
# catopath = 'pages/Temp/Record/DiscriptionCategories.xlsx'
# backup_path = 'AccountApp/Streamlit/pages/Temp/Record/Backup/'+str(date.today())+'.csv'
        # dfo = pd.read_csv(dfopath,encoding='latin1',index_col=[0])
        # dfo.dropna(axis=1,how='all',inplace=True)
        # df = pd.concat([df,dfo], ignore_index=True)
        # dfopath = str(path) +'/Record/Data.csv'
        # catnpath = str(path) +'/Excel/DiscriptionCategories.xlsx'
        # catopath = str(path) +'/Record/DiscriptionCategories.xlsx'
        # catn = pd.read_excel(catnpath)
        # cato = pd.read_excel(catopath)