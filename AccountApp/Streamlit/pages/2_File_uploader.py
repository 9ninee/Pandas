import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

def main():
    st.title("File Uploader")
    with st.form("form", clear_on_submit=True):
        col1, col2 = st.columns([5,2])

    with col1:
        uploaded_file = st.file_uploader("Choose a CSV file",type=["csv"],accept_multiple_files=True)
        global df
        dfn = pd.DataFrame()
    
    if uploaded_file is not None:
        try:
            for i in range(len(uploaded_file)):
                df = pd.read_csv(uploaded_file[i])
                df.dropna(axis=1,how="all",inplace=True) 
                st.caption(uploaded_file[i].name)
                AgGrid(df)
                path = 'pages/Temp/Record/Banknote/'+str(uploaded_file[i].name)
                df.to_csv(path,index=False)
        except:
            df  = pd.read_excel(uploaded_file)

    with col2:
        button = st.form_submit_button("Submit")
        if button and uploaded_file is not None:
            st.success('File submitted')
    
main()
# Done