import os
from supabase import create_client, Client
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import time
import re
import random
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait


# Instantiate Supabase
SUPABASE_URL = "https://mfraljoybtduzwhprbcp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1mcmFsam95YnRkdXp3aHByYmNwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyMjQxMDQzOSwiZXhwIjoyMDM3OTg2NDM5fQ.dziHliVn419S4COaWU4oiM0uGnS6oDcH4oLEGaSl4vg"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def take_screenshot(url, save_path):
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-gpu")  # Disable GPU usage
    chrome_options.add_argument("--remote-debugging-port=9222")  # Use a different port
    chrome_options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"  # Path to Brave on macOS

    # Make sure to specify the ChromeDriver path explicitly in the Service object
    service = Service(executable_path="/opt/homebrew/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Open the provided URL
    driver.get(url)
    driver.set_window_size(1500, 1500)
    
    # Optional: wait for a few seconds to allow the page to load fully
    time.sleep(3)
    #scroll down 100 px
    driver.execute_script("window.scrollTo(0, 1800)")
    time.sleep(10)  # Wait to see the effect


    
    # Save the screenshot
    driver.save_screenshot(save_path)
    
    # Close the browser session
    driver.quit()

    # Resize the image to lower its resolution
    image = Image.open(save_path)
    new_width = 900  # You can adjust this value as needed
    new_height = int(new_width * image.height / image.width)
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    resized_image.save(save_path)  # Overwrite the original image with the resized one

def bypass(url):
    save_path = "screenshot.png"  # Replace with your desired save path
    
    # Take the screenshot of the provided URL
    take_screenshot(url, save_path)
    print(f"Screenshot saved to {save_path}")
    
    # Extract the site name from the URL for the file path
    site_name = extract_site_name(url)
    print(f"Extracted site name: {site_name}")
    
    # Define the file path
    file_path = f"{site_name}.png"
    print(f"Constructed file path: {file_path}")

    try:
        # Perform the upload operation
        with open(save_path, 'rb') as f:
            print("Uploading file...")
            supabase.storage.from_("TE").upload(file=f, path=file_path, file_options={"content-type": "image/png"})
            print(f"File uploaded to {file_path}")

        return file_path

    except Exception as error:
        print(f"Error uploading file or saving URL: {error}")
        return file_path

def extract_site_name(url):
    parsed_url = urlparse(url)
    # Split the netloc by dots and remove the 'www' or similar subdomains
    domain_parts = parsed_url.netloc.split('.')
    # Check if the second last element is the main domain
    if len(domain_parts) > 2 and domain_parts[-2] != 'co':
        main_domain = domain_parts[-2]
    else:
        main_domain = domain_parts[-3]
    return main_domain

