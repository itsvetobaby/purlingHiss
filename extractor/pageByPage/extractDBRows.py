import os
from urllib.parse import urlparse
from supabase import create_client, Client
from scrape import scrape_data
import json
import concurrent.futures

# Get Supabase URL and Key from environment variables
SUPABASE_URL = ('https://mfraljoybtduzwhprbcp.supabase.co')
SUPABASE_KEY = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mcmFsam95YnRkdXp3aHByYmNwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyMjQxMDQzOSwiZXhwIjoyMDM3OTg2NDM5fQ.dziHliVn419S4COaWU4oiM0uGnS6oDcH4oLEGaSl4vg')

def initialize_supabase() -> Client:
    # Create Supabase client
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def process_page(page_url, row):
    try:
        extracted_data = scrape_data(page_url, row)
        return extracted_data
    except Exception as e:
        print(f"An error occurred while processing {page_url}: {e}")
        return []

def extract_data(domain: str):
    # Initialize the Supabase client
    supabase = initialize_supabase()

    try:
        # Query data from the extractors table where domain matches
        response = supabase.table("extractors").select("product_name, cookies, brand, seller, price, wasPrice, href, parent, pages").eq("domain", domain).execute()
        bundle = []
        # Check if the response contains data
        if response.data:
            # Print the extracted data
            for row in response.data:
                print(row)
                for page_url in row['pages']:
                    extracted_data = scrape_data(page_url, row)
                    if extracted_data:
                        bundle.extend(extracted_data)
      

            return bundle
        else:
            print("No data found for the domain:", domain)

    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    # Example domain
    domain = "www.sportsdirect.com"
    
    # Extract and print data for the given domain
    data = extract_data(domain)
    if data:
        data_str = json.dumps(data, indent=4)
        # Write to data.json
        print(data_str)
        with open('data.json', 'w') as f:
            f.write(data_str)
    else:
        print("No data to write.")
