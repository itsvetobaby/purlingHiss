import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_links(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        return [urljoin(url, link.get('href')) for link in soup.find_all('a') if link.get('href')]
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

def is_valid(url, base_url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and parsed.netloc == urlparse(base_url).netloc

def extract_base_path(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}" + "/".join(parsed.path.split('/')[:2])

def crawl(base_url, timeout=180, max_duplicate_ratio=0.95, max_workers=20, max_urls=75):
    visited = set()
    to_visit = [base_url]
    unique_urls = set()

    start_time = time.time()
    last_found_time = start_time
    total_urls_processed = 0
    duplicate_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while to_visit and len(visited) < max_urls:
            current_time = time.time()
            if current_time - last_found_time > timeout:
                print(f"Timeout reached. Ending crawl after {timeout} seconds of inactivity.")
                break

            futures = {executor.submit(get_links, url): url for url in to_visit[:max_workers]}
            to_visit = to_visit[max_workers:]

            for future in as_completed(futures):
                current_url = futures[future]
                total_urls_processed += 1

                if len(visited) >= max_urls:
                    print(f"Reached the maximum number of {max_urls} visited URLs. Ending crawl.")
                    break

                if current_url in visited:
                    duplicate_count += 1
                else:
                    visited.add(current_url)
                    if is_valid(current_url, base_url):
                        links = future.result()
                        base_path = extract_base_path(current_url)
                        unique_urls.add(base_path)
                        last_found_time = current_time  # Reset the timer when a valid URL is found
                        for link in links:
                            if link not in visited:
                                to_visit.append(link)

                if total_urls_processed > 0 and (duplicate_count / total_urls_processed) >= max_duplicate_ratio:
                    print(f"Duplicate URL ratio reached {max_duplicate_ratio * 100}%. Ending crawl.")
                    break

    return unique_urls

def initMapping(base_url):
    print(f"Starting crawl for {base_url}...")
    urls = crawl(base_url)
    return urls