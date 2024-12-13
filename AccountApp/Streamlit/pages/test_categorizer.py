import streamlit as st
from utils.auto_categorizer import TransactionCategorizer
import time

st.title("Categorizer Testing Tool")

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
        categories_file="Temp/Excel/Indcat.csv",
        record_file="Temp/Record/DiscriptionCategories.xlsx",
        use_api=use_api
    )

categorizer = get_categorizer()

# Add rate limit tracking
if 'last_request_time' not in st.session_state:
    st.session_state.last_request_time = 0

def check_rate_limit():
    """Ensure at least 1 second between requests"""
    current_time = time.time()
    if current_time - st.session_state.last_request_time < 1:
        time.sleep(1)
    st.session_state.last_request_time = current_time

# Input section
st.subheader("Test Transaction")
test_transaction = st.text_input("Enter a transaction to test:", "TESCO STORE 2960")

if test_transaction:
    st.write("---")
    st.subheader("Results")
    
    # Test categorization
    with st.spinner("Categorizing transaction..."):
        try:
            check_rate_limit()
            category, method, confidence = categorizer.categorize(test_transaction)
        except Exception as e:
            st.error(f"Categorization failed: {str(e)}")
            st.stop()
    
    # Display results
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Category", category or "None")
    with col2:
        st.metric("Method", method)
    with col3:
        st.metric("Confidence", f"{confidence:.2f}%")
    
    # Show similar transactions
    st.subheader("Similar Transactions")
    similar = categorizer.get_similar_transactions(test_transaction)
    
    if similar:
        for trans, cat, score in similar:
            st.write(f"- {trans} ({score}%) → {cat}")
    else:
        st.write("No similar transactions found")
    
    # Debug information
    with st.expander("Debug Information"):
        st.json({
            "input": test_transaction,
            "category": category,
            "method": method,
            "confidence": confidence,
            "similar_count": len(similar),
            "categories_loaded": len(categorizer.categories),
            "history_entries": len(categorizer.history)
        }) 