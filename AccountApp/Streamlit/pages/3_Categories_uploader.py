import streamlit as st
import pandas as pd 
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

st.title("Categries uploader")

## --- path ---
catnpath = 'pages/Temp/Excel/DiscriptionCategories.csv'
catopath = 'pages/Temp/Record/DiscriptionCategories.csv'
cat_list_path = "pages/Temp/Excel/Indcat.csv"

catn = pd.read_csv(catnpath,parse_dates=['Transaction Date'],dayfirst=True)
cato = pd.read_csv(catopath)
cato.sort_index(ascending=False)

cat_list = pd.read_csv(cat_list_path)
cat_list = cat_list['cat_name']
cat_list = cat_list.dropna(how="all")

tran_list = catn["Transaction Description"]
tran_list = tran_list.drop_duplicates()
tran_list.sort_values(inplace=True)

st.subheader("Waiting list")
st.empty()
gd = GridOptionsBuilder.from_dataframe(catn)
gd.configure_pagination(enabled = True)
gd.configure_default_column(editable = True, groupable = True)

st.sidebar.header("Please update new categories")

input_form = st.sidebar.form("Input_Form")
    
Transaction = input_form.multiselect("Transaction Description",tran_list)
categories = input_form.selectbox("Categories",cat_list)
add_data = input_form.form_submit_button()

# add_data not yet done 

st.cache(allow_output_mutation= True)
    
if add_data:
    for f in Transaction:
        Tran = f
        categories = str(categories)
        catn.loc[catn[ "Transaction Description"] == Tran,"Categories"] = categories
        catn.to_csv(catnpath,index=False)

AgGrid(catn,width=7000)
