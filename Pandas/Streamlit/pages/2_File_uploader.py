import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

def main():
    st.title("File Uploader")

    uploaded_file = st.file_uploader("Choose a CSV or Excel file",type=["csv",'xlsx'])
    
    global df
    if uploaded_file is not None:
        global df

        try:
            df = pd.read_csv(uploaded_file)

        except:
            df  = pd.read_excel(uploaded_file)
    
    df.dropna
    AgGrid(df)
main()
