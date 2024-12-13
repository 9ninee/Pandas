import sys
import os
import pandas as pd
import streamlit as st
from pathlib import Path

# Add project root to path to import utils
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.auto_categorizer import TransactionCategorizer

def test_categorizer():
    # Test data paths
    categories_file = "Temp/Excel/Indcat.csv"
    record_file = "Temp/Record/DiscriptionCategories.xlsx"
    
    # Initialize categorizer
    categorizer = TransactionCategorizer(categories_file, record_file)
    
    # Test transactions
    test_cases = [
        # Known transactions (should match via fuzzy)
        "TESCO STORE 2960",
        "COSTA COFFEE",
        # New transactions (should trigger Spacy/GPT)
        "WALMART GROCERIES",
        "STARBUCKS COFFEE",
        "UBER RIDE",
        "NETFLIX SUBSCRIPTION",
    ]
    
    print("\n=== Testing Categorization System ===\n")
    
    # Test each transaction
    for transaction in test_cases:
        print(f"\nTesting transaction: {transaction}")
        
        # Get category and method
        category, method, confidence = categorizer.categorize(transaction)
        
        print(f"Result:")
        print(f"- Category: {category}")
        print(f"- Method: {method}")
        print(f"- Confidence: {confidence:.2f}")
        
        # Get similar transactions
        print("\nSimilar transactions:")
        similar = categorizer.get_similar_transactions(transaction)
        for trans, cat, score in similar:
            print(f"- {trans} ({score}%) → {cat}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_categorizer() 