from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-gpu")  # Disable GPU usage
    chrome_options.add_argument("--remote-debugging-port=9222")  # Use a different port
    chrome_options.binary_location = "/usr/bin/chromium-browser"  # Path to Chromium

    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def find_div_by_text_from_url(url, target_text):
    driver = setup_driver()
    
    try:
        driver.get(url)
        time.sleep(3)  # Allow the page to load fully
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Convert the target text to lowercase and strip any surrounding whitespace
        target_text_lower = target_text.lower().strip()
        print('searching for ' + target_text_lower)
        # Find the div element that contains the target text in a case-insensitive manner, ignoring surrounding whitespace
        target_div = soup.find('div', string=lambda text: text and target_text_lower in text.lower().strip())
        
        # If the div is found, traverse 7 parents up
        if target_div:
            parent_div = target_div
            for _ in range(3):  # Adjust this number to traverse the correct number of levels up
                if parent_div.parent:
                    parent_div = parent_div.parent
                else:
                    break
            
            # Return the outer HTML of the parent div 7 levels up
            return str(parent_div)
        else:
            return None
    
    finally:
        driver.quit()

def getDiv(url, target_text):
    outer_html = find_div_by_text_from_url(url, target_text)
    if outer_html:
        print("Found parent div 7 levels up:\n" + outer_html)
        return outer_html
    else:
        print("No div found with the specified text.")
        return None

