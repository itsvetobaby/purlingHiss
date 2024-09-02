from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import warnings
from fuzzywuzzy import fuzz
import time

warnings.filterwarnings("ignore", message="Using slow pure-python SequenceMatcher.")

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

def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-gpu")  # Disable GPU usage
    chrome_options.add_argument("--remote-debugging-port=9222")  # Use a different port
    chrome_options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"  # Path to Brave on macOS

    # Make sure to specify the ChromeDriver path explicitly in the Service object
    service = Service(executable_path="/opt/homebrew/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_data(url, selectors):
    driver = initialize_driver()
    
    # Open the given URL
    driver.get(url)

    # Handle cookies if the selector is provided
    # Handle cookies if the selector is provided
    time.sleep(5)

    try:
        # Wait until the parent elements are present (this simulates waiting for network idle)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selectors['parent']))
        )
    except TimeoutException:
        print("Timeout: Parent elements not found.")
        driver.quit()
        return []

    time.sleep(5)
    # Find all parent elements
    parents = driver.find_elements(By.CSS_SELECTOR, selectors['parent'])
    



    time.sleep(25)

    # Initialize a list to store extracted data
    data = []

    # Iterate over all parent elements and extract data
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

    # Close the browser
    driver.quit()

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