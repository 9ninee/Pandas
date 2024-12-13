import streamlit as st
import pandas as pd 
from st_aggrid import AgGrid


st.set_page_config(
    page_title="Bookeeping Software",
    page_icon="",
)

st.sidebar.success("Select a page above.")

st.title("DashBoard")


st.header("Select Filter")

dfopath = 'Temp/Record/Data.csv'

df = pd.read_csv(dfopath,encoding='latin1',index_col=[0])
df = df.dropna(axis=1,how='all')

categores = df["Categories"].unique().tolist()
categories_selection= st.multiselect("Categories : ",
                                    categores,
                                    default=categores)

mask = df["Categories"].isin(categories_selection)

number_of_results = df[mask].shape[0]

st.markdown(f"*Avalible Results : {number_of_results}*")

AgGrid(df)

# df_grouped = df[mask].groupby(by=["Categories"])
# df_grouped = df_grouped.reset_index()


# st.dataframe(df[mask])

#pie chart 
#pie_chart = px.pie(df_grouped,
#                title="Pie Chart",
#                Values= "Debit Amount",
#                Names= "Categories")

#st.dataframe(pie_chart)



