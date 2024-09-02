import os
from urllib.parse import urlparse
from supabase import create_client, Client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import warnings
from fuzzywuzzy import fuzz
import json
import time
from concurrent.futures import ThreadPoolExecutor

warnings.filterwarnings("ignore", message="Using slow pure-python SequenceMatcher.")

# Get Supabase URL and Key from environment variables
SUPABASE_URL = ('https://mfraljoybtduzwhprbcp.supabase.co')
SUPABASE_KEY = ('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mcmFsam95YnRkdXp3aHByYmNwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyMjQxMDQzOSwiZXhwIjoyMDM3OTg2NDM5fQ.dziHliVn419S4COaWU4oiM0uGnS6oDcH4oLEGaSl4vg')

def get_currency_code(symbol):
    currency_mapping = {
        "$": "USD",
        "£": "GBP",
        "€": "EUR",
        "₹": "INR",
        "¥": "JPY",
        "₩": "KRW",
        "₽": "RUB",
        "฿": "THB",
        "₫": "VND",
        "₺": "TRY",
        "₪": "ILS",
        "₱": "PHP",
        "₦": "NGN",
        "CHF": "CHF"
    }
    return currency_mapping.get(symbol, "Unknown")

def initialize_supabase() -> Client:
    # Create Supabase client
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-gpu")  # Disable GPU usage
    chrome_options.add_argument("--remote-debugging-port=9230")  # Use a different port
    chrome_options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"  # Path to Brave on macOS

    # Make sure to specify the ChromeDriver path explicitly in the Service object
    service = Service(executable_path="/opt/homebrew/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_data(driver, url, selectors):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(url)

    # Handle cookies if the selector is provided (not included here for brevity)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selectors['parent']))
        )
    except TimeoutException:
        print("Timeout: Parent elements not found.")
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return []

    time.sleep(10)
    parents = driver.find_elements(By.CSS_SELECTOR, selectors['parent'])

    data = []
    for parent in parents:
        item = {}
        try:
            if selectors.get('product_name'):
                try:
                    item['product_name'] = parent.find_element(By.CSS_SELECTOR, selectors['product_name']).text
                except NoSuchElementException:
                    item['product_name'] = None

            if selectors.get('brand'):
                try:
                    item['brand'] = parent.find_element(By.CSS_SELECTOR, selectors['brand']).text
                except NoSuchElementException:
                    item['brand'] = None

            if selectors.get('seller'):
                item['seller'] = selectors['seller']  # Assuming seller is a static value, not extracted from the page

            if selectors.get('price'):
                try:
                    price_text = parent.find_element(By.CSS_SELECTOR, selectors['price']).text
                    item['price'], item['currency'] = extract_price_and_currency(price_text)
                except NoSuchElementException:
                    item['price'] = None
                    item['currency'] = None

            if selectors.get('wasPrice'):
                try:
                    was_price_text = parent.find_element(By.CSS_SELECTOR, selectors['wasPrice']).text
                    item['wasPrice'], currency = extract_price_and_currency(was_price_text)
                    # If the currency is not already set, set it now
                    if not item.get('currency'):
                        item['currency'] = currency
                except NoSuchElementException:
                    item['wasPrice'] = None

            if selectors.get('href'):
                try:
                    item['href'] = parent.find_element(By.CSS_SELECTOR, selectors['href']).get_attribute('href')
                except NoSuchElementException:
                    item['href'] = None

        except Exception as e:
            print(f"An error occurred while extracting data: {e}")
            continue

        # Add the extracted item to the data list
        data.append(item)

    driver.close()  # Close the tab
    driver.switch_to.window(driver.window_handles[0])  # Switch back to the original tab
    print(data)
    return data

def extract_price_and_currency(price_text):
    if not price_text:
        return None, None

    # Extract the currency symbol (assuming it is the first character)
    symbol = price_text[0]
    currency = get_currency_code(symbol)

    # Remove the currency symbol from the price string
    price = price_text.replace(symbol, "").strip()

    return price, currency

def process_page(driver, page_url, row, is_first_page):
    try:
        if not is_first_page:
            time.sleep(5)  # Introduce a delay before opening the second page

        extracted_data = scrape_data(driver, page_url, row)
        return extracted_data
    except Exception as e:
        print(f"An error occurred while processing {page_url}: {e}")
        return []

def extract_data():
    # Initialize the Supabase client
    supabase = initialize_supabase()

    try:
        # Query data from the extractors table where file_rule is 'combo'
        response = supabase.table("extractors").select("*").eq("file_rule", "combo").execute()
        bundle = []
        # Check if the response contains data
        if response.data:
            # Initialize the driver once
            driver = initialize_driver()

            # Print the extracted data
            for row in response.data:
                print(row)

                # Use a ThreadPoolExecutor to process pages in parallel
                with ThreadPoolExecutor(max_workers=2) as executor:
                    results = executor.map(lambda page_url: process_page(driver, page_url, row, page_url == row['pages'][0]), row['pages'])

                    # Collect the results from the parallel tasks
                    extracted_data = [result for result in results if result]
                    bundle.extend(extracted_data)
                    time.sleep(8)

            # Close the driver after all pages are processed
            driver.quit()

            return bundle
        else:
            print("No data found for file_rule = 'combo'")

    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    # Extract and print data for rows with file_rule = 'combo'
    data = extract_data()
    if data:
        print(data)
        data_str = json.dumps(data, indent=4)
        print(data_str)