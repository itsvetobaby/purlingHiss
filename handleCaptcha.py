import os
from supabase import create_client, Client
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import random
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
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.binary_location = "/usr/bin/chromium-browser"  # Path to Chromium

    # Make sure to specify the ChromeDriver path explicitly in the Service object
    service = Service(executable_path="/usr/bin/chromedriver")
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Open the provided URL
    driver.get(url)
    driver.set_window_size(1500, 1500)
    
    # Optional: wait for a few seconds to allow the page to load fully
    time.sleep(3)
    #scroll down 100 px
    driver.execute_script("window.scrollTo(0, 200)")
    time.sleep(10)  # Wait to see the effect
    
    # Save the screenshot
    driver.save_screenshot(save_path)
    
    # Close the browser session
    driver.quit()

def bypass(url):
    save_path = "screenshot.png"  # Replace with your desired save path
    
    take_screenshot(url, save_path)
    print(f"Screenshot saved to {save_path}")
    # Generate a unique file name based on the current timestamp
    random_number = random.randint(1, 999999)
    file_name = f"testURL{random_number}.png"
    file_path = f"{file_name}"

    try:

        # Construct the file URL if upload is successful
        file_url = f"Images/{file_path}"

        with open(save_path, 'rb') as f:
            supabase.storage.from_("Images").upload(file=f,path=file_url, file_options={"content-type": "image/png"})

        

        return file_url

    except Exception as error:
        print(f"Error uploading file or saving URL: {error}")
