import streamlit as st
import pandas as pd 
from st_aggrid import AgGrid
import os
import glob
import Acc_Function

st.set_page_config(
    page_title="Bookeeping Software",
    page_icon="",
)

st.title('Expenses Dash Borad')

st.sidebar.title("Select Filter")

dfopath = 'pages/Temp/Record/Data.csv'
df = pd.read_csv(dfopath,encoding='latin1',parse_dates=['Transaction Date'],dayfirst=True)
df = df.dropna(axis=1,how='all')

categories_selection= st.sidebar.multiselect("Categories : ",
                                    options = df["Categories"].unique(),
                                    default = df["Categories"].unique())

mask = df["Categories"].isin(categories_selection)

Update = st.sidebar.button("Update")

if Update:
    path = "pages/Temp/Record/Banknote/"
    csv_files = glob.glob(os.path.join(path, "*.csv"))
    cat = Acc_Function.func.catconcat()
    table = []

    for f in csv_files:
        dfnew = pd.read_csv(f,parse_dates=['Transaction Date'],dayfirst=True)
        catn,cat,MergeTable = Acc_Function.func.dfmerge(dfnew,cat)
        Acc_Function.func.Backup(f)
        table.append(MergeTable)

    try:
        dfn = pd.concat(table,ignore_index=True)
        dfnew = pd.concat([dfn,df]).drop_duplicates().reset_index(drop=True)
        dfnew = dfnew.sort_values(by='Transaction Date',ascending = False)
        dfnew.to_csv('pages/Temp/Record/Data.csv',index=False)
        catn.to_csv('pages/Temp/Excel/DiscriptionCategories.csv',index=False)
        cat.to_csv('pages/Temp/Record/DiscriptionCategories.csv',index=False)
        st.success("Update Complete")
        
    except ValueError:
        st.error('Not Banknote is imported, please import statement with File Uplodaer')
    
df_selection = df.query(
    'Categories==@categories_selection'
)

number_of_results = df[mask].shape[0]
st.markdown(f"*Avalible Results : {number_of_results}*")
AgGrid(df_selection)  

total_expenses = int(df_selection["Debit Amount"].sum())
total_income = int(df_selection["Credit Amount"].sum())
# expensesbycategories = int(df["Debit Amount"].groupby('Categories').sum())
expensesbymonth = int(df_selection["Debit Amount"].sum())


# left_column, middle_column, right_column = st.columns(3)

# with left_column:
    