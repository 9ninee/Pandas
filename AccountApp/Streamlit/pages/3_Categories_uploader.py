import streamlit as st
import pandas as pd
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from utils.auto_categorizer import TransactionCategorizer

st.title("Categories uploader")

## --- path ---
catnpath = 'Temp/Excel/DiscriptionCategories.xlsx'
catopath = 'Temp/Record/DiscriptionCategories.xlsx'
cat_list_path = "Temp/Excel/Indcat.csv"

# Initialize categorizer
@st.cache_resource
def get_categorizer():
    # Check if API access is available
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
        use_api = True
    except Exception:
        use_api = False
        st.warning("API key not found, using offline mode only")
    
    return TransactionCategorizer(
        categories_file=cat_list_path,
        record_file=catopath,
        use_api=use_api
    )

# Load your data
catn = pd.read_excel(catnpath)
cato = pd.read_excel(catopath)
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
gd.configure_pagination(enabled=True)
gd.configure_default_column(editable=True, groupable=True)

st.sidebar.header("Please update new categories")

# Get categorizer instance
categorizer = get_categorizer()

# Create form
input_form = st.sidebar.form("Input_Form")
Transaction = input_form.selectbox("Transaction Description", tran_list)

# Get suggested category before showing the dropdown
suggested_category = None
if Transaction:
    category, method, confidence = categorizer.categorize(Transaction)
    if category:
        suggested_category = category

# Reorder categories list to put suggestion first if exists
if suggested_category and suggested_category in cat_list.values:
    # Convert to list for manipulation
    categories_list = cat_list.tolist()
    # Remove suggestion from current position
    categories_list.remove(suggested_category)
    # Add suggestion at the beginning
    categories_list.insert(0, suggested_category)
else:
    categories_list = cat_list.tolist()

# Show categories dropdown with reordered list
categories = input_form.selectbox("Categories", categories_list)
auto_apply = input_form.checkbox("Auto-apply to similar transactions?")
add_data = input_form.form_submit_button()

# Show similar transactions and suggested category
if Transaction:
    st.sidebar.subheader("Similar Transactions:")
    
    if suggested_category:
        source = "Historical Match" if method == "history" else (
            "AI Suggestion" if method in ['spacy_llm', 'gpt'] else 
            "Local Model" if method == 'local_spacy' else 
            "Fuzzy Match"
        )
        if method in ['history', 'fuzzy_fallback']:
            st.sidebar.success(f"Suggested Category ({source}): {category} ({confidence}% match)")
        else:
            st.sidebar.success(f"Suggested Category ({source}): {category}")
    
    # Show similar transactions
    similar_transactions = categorizer.get_similar_transactions(Transaction)
    for trans, cat, score in similar_transactions:
        st.sidebar.write(f"- {trans} ({score}%) → {cat}")

if add_data:
    Transaction = str(Transaction)
    categories = str(categories)
    
    # Update catn
    catn.loc[catn["Transaction Description"] == Transaction, "Categories"] = categories
    
    # Also update cato (record file)
    new_record = pd.DataFrame({
        'Transaction Description': [Transaction],
        'Categories': [categories]
    })
    cato = pd.concat([new_record, cato]).drop_duplicates(subset='Transaction Description')
    
    # Update business types based on new categorization
    transaction_upper = Transaction.upper()
    category_type = categories.split('.')[1].upper() if '.' in categories else categories.upper()
    
    # Check if business type exists, if not create it
    if category_type not in categorizer.business_types:
        categorizer.update_business_types(category_type, {
            "category": categories,
            "keywords": [transaction_upper],
            "chains": []
        })
    else:
        # Add transaction as keyword if it's not already there
        categorizer.add_business_keyword(category_type, transaction_upper)
        
        # If it looks like a chain store (no numbers, all caps), add to chains
        if transaction_upper.replace(' ', '').isalpha():
            categorizer.add_business_chain(category_type, transaction_upper)
    
    # Auto-apply to similar transactions if checked
    if auto_apply:
        similar_trans = categorizer.get_similar_transactions(Transaction)
        
        # Show which transactions will be updated
        updated_transactions = []
        for trans, cat, score in similar_trans:
            if score >= 78:  # You can adjust this threshold
                catn.loc[catn["Transaction Description"] == trans[0], "Categories"] = categories
                updated_transactions.append(f"- {trans[0]} ({score}%)")
                
                # Also update business types for similar transactions
                trans_upper = trans[0].upper()
                categorizer.add_business_keyword(category_type, trans_upper)
                if trans_upper.replace(' ', '').isalpha():
                    categorizer.add_business_chain(category_type, trans_upper)
        
        if updated_transactions:
            st.sidebar.write("Updated similar transactions:")
            for trans in updated_transactions:
                st.sidebar.write(trans)
    
    # Save all changes at once
    catn.to_excel(catnpath, index=False)
    cato.to_excel(catopath, index=False)
    
    # Force refresh of the cache
    st.cache_data.clear()
    st.rerun()

# Display grid
AgGrid(catn, width=7000,theme='streamlit')



