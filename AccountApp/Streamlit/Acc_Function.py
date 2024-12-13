import pandas as pd
import numpy as np
import os
from datetime import date


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

    def cat(df,cato):
        df = df.drop(columns=['Transaction Date','Debit Amount','Credit Amount'])

        return df

    # Required input: Newfile, Filelocation 

    def catmerge(catn, cato):
        catn= catn.drop(columns=['Transaction Date','Debit Amount','Credit Amount'])
        cat = pd.concat([catn,cato], ignore_index=True)
        return cat

    def dfmerge(df,cat):

        dfn = df
        catn= cato = cat

        # merge cat table with df 
        MergeTable = pd.merge(df,
                        cat,
                        on = 'Transaction Description',
                        how = 'left',
                        suffixes = ('','_DROP')).filter(regex='^(?!.*_DROP)')
        MergeTable.drop_duplicates(ignore_index=True, inplace=True)

        catn = MergeTable[MergeTable['Categories'].isna()]
        catn = catn.drop_duplicates(ignore_index=True)
        catn = catn.loc[:, ~catn.columns.str.contains('^Unnamed')]
        # catn.to_excel(catnpath,index=False)

        MergeTable = MergeTable.loc[:, ~MergeTable.columns.str.contains('^Unnamed')]

        # MergeTable.to_csv(dfopath, index=False)

        return dfn,catn,cato

    def Backup(df,path):

        backup_path = 'pages/Temp/Record/Backup/'+str(date.today())+'.csv'
        df = pd.DataFrame 
        # move and rename dfn to backup file 
        # os.rename(dfnpath,backup_path)
        df.to_csv(backup_path,index=False)



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