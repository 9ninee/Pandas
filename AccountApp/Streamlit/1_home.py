from requests import options
import streamlit as st
import pandas as pd 
from st_aggrid import AgGrid
import matplotlib as plt


st.set_page_config(
    page_title="Bookeeping Software",
    page_icon="",
)

st.title('Expenses Dash Borad')

st.sidebar.title("Select Filter")

#

dfopath = '/Users/nigel/Library/Mobile Documents/com~apple~CloudDocs/Programme/Temp/Record/Data.csv'

df = pd.read_csv(dfopath,encoding='latin1',index_col=[0])
df = df.dropna(axis=1,how='all')

categories_selection= st.sidebar.multiselect("Categories : ",
                                    options = df["Categories"].unique(),
                                    default = df["Categories"].unique()
                                )

mask = df["Categories"].isin(categories_selection)

df_selection = df.query(
    'Categories == @categories_selection'
)

number_of_results = df[mask].shape[0]
st.markdown(f"*Avalible Results : {number_of_results}*")
AgGrid(df_selection)  

total_expenses = int(df_selection["Debit Amount"].sum())
total_income = int(df_selection["Credit Amount"].sum())
expensesbycategories = int(df_selection["Debit Amount"].groupby('Categories').sum())
expensesbymonth = int(df_selection["Debit Amount"].sum())


# left_column, middle_column, right_column = st.columns(3)

# with left_column:
    