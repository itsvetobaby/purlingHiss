from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import time

def setup_driver():
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

def find_element_by_text_from_url(url, target_text, match_ratio=80):
    driver = setup_driver()
    
    try:
        driver.get(url)
        
        # Wait for the page to fully load by waiting for a specific element to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))  # Wait for the body to be present
        )
        
        # Give additional time for any dynamic content to fully render
        time.sleep(5)
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Convert the target text to lowercase and strip any surrounding whitespace
        target_text_lower = target_text.strip().lower()
        
        print('Searching for:', target_text_lower)

        # Find all elements and filter by fuzzy matching with the target text
        elements = soup.find_all(True)  # Finds all tags
        target_element = None
        for element in elements:
            if element.string:
                element_text = element.string.strip().lower()  # Convert to lowercase
                print('Checking element text:', element_text)
                # Use fuzzy matching to compare the text
                similarity = fuzz.partial_ratio(element_text, target_text_lower)  # Use partial ratio for partial matching
                if similarity >= match_ratio:
                    target_element = element
                    break
        
        # If the element is found, traverse 3 parents up (adjust this if needed)
        if target_element:
            parent_element = target_element
            for _ in range(2):  # Adjust this number to traverse the correct number of levels up
                if parent_element.parent:
                    parent_element = parent_element.parent
                else:
                    break
            
            # Return the outer HTML of the parent element 3 levels up
            return str(parent_element)
        else:
            return None
    
    finally:
        driver.quit()

def getDiv(url, target_text):
    outer_html = find_element_by_text_from_url(url, target_text)
    if outer_html:
        print("Found parent element 3 levels up:\n" + outer_html)
        return outer_html
    else:
        print("No element found with the specified text.")
        return None
