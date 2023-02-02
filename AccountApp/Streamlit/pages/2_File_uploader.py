import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
import numpy
import os
from datetime import datetime

def main():
    st.title("File Uploader")
    with st.form("my-form", clear_on_submit=True):
        col1, col2 = st.columns([5,2])

    with col1:
        uploaded_file = st.file_uploader("Choose a CSV file",type=["csv"],accept_multiple_files=True)
        global df, dfn
        dfn = pd.DataFrame()
    
    if uploaded_file is not None:
        try:
            for i in range(len(uploaded_file)):
                df = pd.read_csv(uploaded_file[i])
                df.dropna(axis=1,how="all",inplace=True) 
                AgGrid(df)
                if not dfn.empty:
                    dfn = pd.concat([dfn,df], ignore_index=True)
                else:
                    dfn = df
        except:
            df  = pd.read_excel(uploaded_file)

    with col2:
        button = st.form_submit_button("Submit")
        if button:
            path = 'pages/Temp/Record/Banknote/'+str(datetime.now().strftime('%Y%m%d_%H%M%S'))+'.csv'
            dfn.to_csv(path,index=False)
            st.success('File submitted')
    
main()
