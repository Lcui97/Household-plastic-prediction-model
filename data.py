import requests
import pandas as pd
import time

# Configuration
TARGET_ROWS = 35000  # Fetch a bit more to allow for cleaning
PAGE_SIZE = 1000      # Max allowed by API usually around 100-1000
OUTPUT_FILE = "plastic_data.csv"

# The specific columns for our project
FIELDS = [
    "code",
    "product_name",
    "brands",
    "packaging_tags",      # KEY for your project (e.g., "en:plastic-bottle")
    "packaging_text",      # Raw text descriptions
    "ingredients_text",    # Useful for NLP context
    "ecoscore_grade",      # Good target variable for regression
    "countries_en"
]

def fetch_plastic_data():
    all_products = []
    page = 1
    
    print(f"Starting data mine for {TARGET_ROWS} products...")
    
    while len(all_products) < TARGET_ROWS:
        # Open Food Facts "Search" API Endpoint
        url = "https://world.openfoodfacts.org/cgi/search.pl"
        
        params = {
            "action": "process",
            "tagtype_0": "countries",   # Filter by country
            "tag_contains_0": "contains",
            "tag_0": "united states",   # Target US market
            "tagtype_1": "packaging",   # Ensure packaging data exists
            "tag_contains_1": "contains",
            "tag_1": "plastic",         # loose filter to prioritize plastic items
            "page_size": PAGE_SIZE,
            "page": page,
            "json": "1",
            "fields": ",".join(FIELDS)
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            products = data.get("products", [])
            if not products:
                break
                
            all_products.extend(products)
            print(f"   Collected {len(all_products)} / {TARGET_ROWS} rows... (Page {page})")
            
            page += 1
            time.sleep(1.0) # Be nice to their API
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break

    # Convert to DataFrame
    df = pd.DataFrame(all_products)
    
    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Success! Saved {len(df)} rows to '{OUTPUT_FILE}'")
    print(f"   Key Feature: Check the 'packaging_tags' column for your labels.")

if __name__ == "__main__":
    fetch_plastic_data()