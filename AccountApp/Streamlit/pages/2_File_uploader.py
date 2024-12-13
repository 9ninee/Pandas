import streamlit as st
import pandas as pd
from st_aggrid import AgGrid


def main():
    st.title("File Uploader")

    uploaded_file = st.file_uploader("Choose a CSV file",type=["csv"],accept_multiple_files=True)

    if uploaded_file is not None:
        global df

        try:
            # df = pd.read_csv(uploaded_file)
            for i in range(len(uploaded_file)):
                df = pd.read_csv(uploaded_file[i])
                df.dropna(axis=1,how="all") 
                AgGrid(df)

        except:
            df  = pd.read_excel(uploaded_file)

    # choice = st.selectbox()
    # AgGrid(df)
main()
