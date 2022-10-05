# %%
import pandas as pd
import numpy as np
import os
from datetime import date

class Calcualtion():

    # Required input: Newfile, Filelocation 

    def Lloyrd(self,dfn, path): # path
        dfopath = 'pages/Temp/Record/Data.csv'
        catnpath = 'pages/Temp/Excel/DiscriptionCategories.xlsx'
        catopath = 'pages/Temp/Record/DiscriptionCategories.xlsx'
        backup_path = 'pages/Temp/Record/Backup/'+str(date.today())+'.csv'

        dfn = df = pd.read_csv(dfn,encoding='latin1',index_col=[0])

        df = df.dropna(axis=1,how='all')
        catn = pd.read_excel(catnpath)
        cato = pd.read_excel(catopath)
        dfo = pd.read_csv(dfopath,encoding='latin1',index_col=[0])
        dfo.dropna(axis=1,how='all',inplace=True)

        df = df.drop(columns=['Account Number','Balance','Transaction Type','Sort Code'])
        catn = catn.drop(columns=['Transaction Date','Debit Amount','Credit Amount'])
        cat = pd.concat([catn,cato], ignore_index=True)
        df = pd.concat([df,dfo], ignore_index=True)
        df['Transaction Description'] = df['Transaction Description'].astype(str)

        return dfn, cat

    def merge(self,df, cat):

        dfn = dfo= df
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

        # move and rename dfn to backup file 
        # os.rename(dfnpath,backup_path)

        dfo.to_csv(backup_path, index=False)

        return dfn,dfo,catn,cato






# dfnpath = 'pages/Temp/Excel/15101160_20220519_0443.xlsx'
# dfopath = 'pages/Temp/Record/Data.csv'
# catnpath = 'pages/Temp/Excel/DiscriptionCategories.xlsx'
# catopath = 'pages/Temp/Record/DiscriptionCategories.xlsx'
# backup_path = 'AccountApp/Streamlit/pages/Temp/Record/Backup/'+str(date.today())+'.csv'