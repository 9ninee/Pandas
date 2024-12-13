import pandas as pd
from fuzzywuzzy import fuzz, process
import spacy
from typing import Optional, Tuple, List
import os
import streamlit as st
from openai import OpenAI
import time
from tenacity import retry, stop_after_attempt, wait_exponential
import json
from pathlib import Path

class TransactionCategorizer:
    def __init__(self, categories_file: str, record_file: str, use_api: bool = True):
        """
        Initialize the categorizer with paths to necessary files
        
        Args:
            categories_file: Path to file containing valid categories
            record_file: Path to historical categorization records
            use_api: Whether to use API-based models (default: True)
        """
        self.categories_file = categories_file
        self.record_file = record_file
        self.use_api = use_api
        self.spacy_nlp = None
        self.gpt_client = None
        self.local_nlp = None  # For local Spacy model
        self.categories = self._load_categories()
        self.history = self._load_history()
        self.business_types = self._load_business_types()
        self.business_keywords = self._create_business_keywords()
        
    def _load_categories(self) -> List[str]:
        """Load valid categories from file"""
        cat_df = pd.read_csv(self.categories_file)
        return cat_df['cat_name'].dropna(how="all").tolist()
    
    def _load_history(self) -> pd.DataFrame:
        """Load historical categorization records"""
        try:
            return pd.read_excel(self.record_file)
        except FileNotFoundError:
            return pd.DataFrame(columns=['Transaction Description', 'Categories'])
    
    def _initialize_local_model(self):
        """Initialize local Spacy model for offline categorization"""
        if self.local_nlp is None:
            try:
                # Load a small English model
                self.local_nlp = spacy.load("en_core_web_lg")
            except Exception:
                try:
                    # If model not found, download and load it
                    os.system("python -m spacy download en_core_web_lg")
                    self.local_nlp = spacy.load("en_core_web_lg")
                except Exception as e:
                    st.warning(f"Local model initialization failed: {str(e)}")
                    self.local_nlp = False
    
    def _get_local_category(self, transaction: str) -> Optional[str]:
        """Get category suggestion using local Spacy model"""
        self._initialize_local_model()
        if self.local_nlp and self.local_nlp is not False:
            try:
                # Process the transaction text
                doc = self.local_nlp(transaction)
                
                # Extract key entities and their labels
                entities = [ent.label_ for ent in doc.ents]
                
                # Simple rule-based categorization
                keywords = {
                    "4.1.Groceries": ["STORE", "SUPERMARKET", "GROCERY", "FOOD"],
                    "4.2.Restaurant": ["RESTAURANT", "CAFE", "COFFEE", "DINING"],
                    "4.3.Transport": ["TRANSPORT", "UBER", "TAXI", "TRAIN", "BUS"],
                    "4.4.Shopping": ["SHOP", "RETAIL", "MALL", "MARKET"],
                    "4.5.Entertainment": ["CINEMA", "MOVIE", "ENTERTAINMENT", "GAME"],
                    "4.6.Utilities": ["UTILITY", "ELECTRIC", "GAS", "WATER"],
                    # Add more categories and keywords as needed
                }
                
                # Check transaction text against keywords
                transaction_upper = transaction.upper()
                for category, words in keywords.items():
                    if any(word in transaction_upper for word in words):
                        if category in self.categories:
                            return category
                
                # Fallback to entity-based categorization
                entity_category_map = {
                    "ORG": "4.4.Shopping",  # Organizations often are shops
                    "GPE": "4.3.Transport",  # Locations might indicate transport
                    "MONEY": "4.4.Shopping",  # Money mentions often indicate purchases
                }
                
                for ent in doc.ents:
                    if ent.label_ in entity_category_map:
                        category = entity_category_map[ent.label_]
                        if category in self.categories:
                            return category
                
            except Exception as e:
                st.warning(f"Local categorization failed: {str(e)}")
        return None
    
    def _initialize_spacy(self):
        """Initialize local Spacy model"""
        if self.spacy_nlp is None:
            try:
                self.spacy_nlp = spacy.load('en_core_web_lg')
            except OSError:
                # If model isn't installed, download it
                st.info("Downloading required language model...")
                os.system("python -m spacy download en_core_web_lg")
                self.spacy_nlp = spacy.load('en_core_web_lg')
    
    def _initialize_gpt(self):
        """Lazy initialization of OpenAI GPT client"""
        if self.gpt_client is None:
            try:
                api_key = st.secrets["OPENAI_API_KEY"]
                self.gpt_client = OpenAI(api_key=api_key)
            except Exception as e:
                st.warning(f"GPT initialization failed: {str(e)}")
                self.gpt_client = False  # Mark as failed
    
    def _get_spacy_category(self, transaction: str) -> Optional[str]:
        """Get category suggestion using Spacy word vectors"""
        self._initialize_spacy()
        if not self.spacy_nlp:
            return None
            
        try:
            # Prepare transaction text
            transaction_doc = self.spacy_nlp(transaction.upper())
            
            # First try exact matches from business types
            for keyword, category in self.business_keywords.items():
                if keyword in transaction.upper():
                    return category
            
            # If no exact match, try similarity matching
            best_similarity = 0
            best_category = None
            
            # Compare with each business type's keywords
            for business_type, data in self.business_types.items():
                category = data['category']
                keywords = data['keywords'] + data['chains']
                
                # Calculate similarity with each keyword
                for keyword in keywords:
                    keyword_doc = self.spacy_nlp(keyword)
                    
                    # Calculate similarity between transaction and keyword
                    try:
                        similarity = transaction_doc.similarity(keyword_doc)
                        
                        # Update if this is the best match so far
                        if similarity > best_similarity and similarity > 0.6:  # Threshold
                            best_similarity = similarity
                            best_category = category
                            
                    except Exception:
                        # Skip if vectors aren't available for these words
                        continue
            
            return best_category
            
        except Exception as e:
            st.warning(f"Spacy categorization failed: {str(e)}")
            return None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        reraise=True
    )
    def _get_gpt_category(self, transaction: str) -> Optional[str]:
        """Get category suggestion from GPT with retry logic"""
        self._initialize_gpt()
        if self.gpt_client and self.gpt_client is not False:
            try:
                # Add delay to respect rate limits
                time.sleep(1)  # 1 second delay between requests
                
                prompt = f"""
                Categorize this transaction into one of these categories:
                {', '.join(self.categories)}
                
                Transaction: {transaction}
                
                Return only the category name, nothing else.
                """
                
                response = self.gpt_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a financial transaction categorizer. Respond only with the category name."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0,
                    max_tokens=50
                )
                
                suggested_category = response.choices[0].message.content.strip()
                if suggested_category in self.categories:
                    return suggested_category
            except Exception as e:
                st.warning(f"GPT categorization failed: {str(e)}")
                raise  # Re-raise for retry
        return None
    
    def _get_fuzzy_match(self, transaction: str, min_score: int = 78) -> Optional[Tuple[str, int]]:
        """Find closest match in historical data using fuzzy matching"""
        if self.history.empty:
            return None
            
        matches = process.extract(
            transaction,
            self.history['Transaction Description'].tolist(),
            scorer=fuzz.token_sort_ratio,
            limit=1
        )
        
        if matches and matches[0][1] >= min_score:
            match_desc = matches[0][0]
            match_cat = self.history[
                self.history['Transaction Description'] == match_desc
            ]['Categories'].iloc[0]
            
            if pd.notna(match_cat):
                return match_cat, matches[0][1]
        return None
    
    def _get_business_type_match(self, transaction: str) -> Optional[Tuple[str, float]]:
        """Match transaction to business type using keywords and chain names"""
        transaction_upper = transaction.upper()
        
        # First try exact chain matching
        for business_type, data in self.business_types.items():
            for chain in data["chains"]:
                if chain.upper() in transaction_upper:
                    return data["category"], 0.95  # High confidence for chain matches
        
        # Then try keyword matching
        best_match = None
        highest_score = 0
        
        for business_type, data in self.business_types.items():
            score = 0
            matched_keywords = 0
            
            for keyword in data["keywords"]:
                if keyword.upper() in transaction_upper:
                    matched_keywords += 1
                    score += 1
            
            if matched_keywords > 0:
                # Calculate confidence score (0-1)
                confidence = score / len(data["keywords"])
                if confidence > highest_score:
                    highest_score = confidence
                    best_match = (data["category"], min(0.90, confidence))
        
        return best_match
    
    def categorize(self, transaction: str) -> Tuple[str, str, float]:
        """
        Categorize a transaction using multiple methods in sequence:
        1. Try fuzzy matching first (fastest)
        2. Try business type matching
        3. Try Spacy similarity matching
        """
        # Try fuzzy matching first
        fuzzy_result = self._get_fuzzy_match(transaction)
        if fuzzy_result:
            category, score = fuzzy_result
            return category, 'history', score
        
        # Try business type matching
        business_match = self._get_business_type_match(transaction)
        if business_match:
            category, confidence = business_match
            return category, 'business_type', confidence * 100
        
        # Try Spacy similarity matching
        spacy_category = self._get_spacy_category(transaction)
        if spacy_category:
            return spacy_category, 'spacy', 80.0  # Fixed confidence for Spacy matches
        
        # If all else fails, use fuzzy matching with a lower threshold
        fuzzy_result = self._get_fuzzy_match(transaction, min_score=60)
        if fuzzy_result:
            category, score = fuzzy_result
            return category, 'fuzzy_fallback', score
        
        return None, 'none', 0.0
    
    def get_similar_transactions(self, transaction: str, limit: int = 5) -> List[Tuple[str, str, int]]:
        """Get similar transactions from history"""
        if self.history.empty:
            return []
            
        matches = process.extract(
            transaction,
            self.history['Transaction Description'].tolist(),
            scorer=fuzz.token_sort_ratio,
            limit=limit
        )
        
        results = []
        for match_desc, score in matches:
            category = self.history[
                self.history['Transaction Description'] == match_desc
            ]['Categories'].iloc[0]
            results.append((match_desc, category if pd.notna(category) else 'uncategorized', score))
            
        return results 
    
    def _load_business_types(self) -> dict:
        """Load business types from JSON file"""
        try:
            business_types_path = Path("data/business_types.json")
            with open(business_types_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            st.warning("Business types file not found. Creating default file.")
            # Create directory if it doesn't exist
            business_types_path.parent.mkdir(parents=True, exist_ok=True)
            # Create default file
            default_types = {}  # Empty dict as default
            with open(business_types_path, 'w') as f:
                json.dump(default_types, f, indent=4)
            return default_types
    
    def update_business_types(self, business_type: str, data: dict) -> None:
        """
        Update or add a business type
        
        Args:
            business_type: Name of the business type (e.g., "GROCERIES")
            data: Dictionary containing category, keywords, and chains
        """
        self.business_types[business_type] = data
        # Save to file
        business_types_path = Path("data/business_types.json")
        with open(business_types_path, 'w') as f:
            json.dump(self.business_types, f, indent=4)
    
    def add_business_keyword(self, business_type: str, keyword: str) -> None:
        """Add a new keyword to a business type"""
        if business_type in self.business_types:
            keyword = keyword.upper()
            if keyword not in self.business_types[business_type]["keywords"]:
                self.business_types[business_type]["keywords"].append(keyword)
                # Save to file
                business_types_path = Path("data/business_types.json")
                with open(business_types_path, 'w') as f:
                    json.dump(self.business_types, f, indent=4)
    
    def add_business_chain(self, business_type: str, chain: str) -> None:
        """Add a new chain to a business type"""
        if business_type in self.business_types:
            chain = chain.upper()
            if chain not in self.business_types[business_type]["chains"]:
                self.business_types[business_type]["chains"].append(chain)
                # Save to file
                business_types_path = Path("data/business_types.json")
                with open(business_types_path, 'w') as f:
                    json.dump(self.business_types, f, indent=4) 
    
    def _create_business_keywords(self) -> dict:
        """Create a mapping of keywords to categories from business types"""
        keyword_map = {}
        for business_type, data in self.business_types.items():
            category = data['category']
            # Add all keywords and chains to the mapping
            for keyword in data['keywords'] + data['chains']:
                keyword_map[keyword] = category
        return keyword_map
  