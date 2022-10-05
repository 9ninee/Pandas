import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
import numpy
import function 

def main():
    st.title("File Uploader")

    uploaded_file = st.file_uploader("Choose a CSV or Excel file",type=["csv",'xlsx'])
    
    global df
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except:
            df  = pd.read_excel(uploaded_file)
        else:
            st.write("Plz input a CSV/Excel File")

    df = df.dropna(axis='columns', how ='all')
    
    AgGrid(df)

    button = st.sidebar.button("Submit")
    
    if button:
        
        df.to_csv()
main()
