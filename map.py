from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from urllib.parse import urljoin

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    service = Service(executable_path="/opt/homebrew/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def get_links(driver, url):
    try:
        driver.get(url)
        # Wait for the page to load
        driver.implicitly_wait(5)

        # Find all anchor tags and extract their href attributes
        links = [urljoin(url, elem.get_attribute('href')) for elem in driver.find_elements(By.TAG_NAME, 'a') if elem.get_attribute('href')]
        return links
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

def crawl_single_page(base_url, max_links=150):
    driver = setup_driver()

    try:
        links = get_links(driver, base_url)
        # Limit the number of URLs to max_links
        if len(links) > max_links:
            print(f"More than {max_links} URLs found. Returning first {max_links} URLs.")
            links = links[:max_links]
        else:
            print(f"Found {len(links)} URLs.")
    finally:
        driver.quit()

    return links

def initMapping(base_url):
    print(f"Starting crawl for {base_url}...")
    urls = crawl_single_page(base_url)
    # Write to map.txt
    with open("map.txt", "w") as f:
        for url in urls:
            f.write(url + "\n")
    return urls

