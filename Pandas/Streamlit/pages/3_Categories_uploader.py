import streamlit as st
import pandas as pd 
import numpy as np
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import os

st.title("Categries uploader")

## --- path ---
catnpath = '/Users/nigel/Library/Mobile Documents/com~apple~CloudDocs/Programme/Temp/Excel/DiscriptionCategories.xlsx'
catopath = '/Users/nigel/Library/Mobile Documents/com~apple~CloudDocs/Programme/Temp/Record/DiscriptionCategories.xlsx'
cat_list_path = "/Users/nigel/Library/Mobile Documents/com~apple~CloudDocs/Programme/Temp/Excel/Indcat.csv"

catn = pd.read_excel(catnpath)
cato = pd.read_excel(catopath)
cato.sort_index(ascending=False)

cat_list = pd.read_csv(cat_list_path)
cat_list = cat_list['cat_name']
cat_list = cat_list.dropna(how="all")

tran_list = catn['Transaction Description']
tran_list = tran_list.drop_duplicates()
tran_list = tran_list.sort_values(axis=['Transaction Description'])

st.subheader("Uncated transaction")

gd = GridOptionsBuilder.from_dataframe(catn)
gd.configure_pagination(enabled = True)
gd.configure_default_column(editable = True, groupable = True)

AgGrid(catn,width=7000)

st.sidebar.header("Please update new categories")

input_form = st.sidebar.form("Input_Form")
    
Transaction = input_form.selectbox("Transaction Description",tran_list)
categories = input_form.selectbox("Categories",cat_list)
add_data = input_form.form_submit_button()

##add_data not yet done 

if add_data:
    new_data = {"Transaction Description": Transaction, "Categories": categories}
    catn.loc[str(Transaction), "Categories"]= str(categories)
    catn.to_excel(catopath,index="false")

# st.write(cat_list)


