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

def is_focused_url(url, focused_url):
    return url.startswith(focused_url)

def crawl(base_url, focused_url, max_to_return, timeout=180, max_duplicate_ratio=0.95, max_workers=20, max_urls=75):
    visited = set()
    to_visit = [base_url]
    focused_urls = []

    start_time = time.time()
    last_found_time = start_time
    total_urls_processed = 0
    duplicate_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while to_visit and len(visited) < max_urls and len(focused_urls) < max_to_return:
            current_time = time.time()
            if current_time - last_found_time > timeout:
                print(f"Timeout reached. Ending crawl after {timeout} seconds of inactivity.")
                break

            futures = {executor.submit(get_links, url): url for url in to_visit[:max_workers]}
            to_visit = to_visit[max_workers:]

            for future in as_completed(futures):
                current_url = futures[future]
                total_urls_processed += 1

                if len(visited) >= max_urls or len(focused_urls) >= max_to_return:
                    print(f"Reached the limit. Ending crawl.")
                    break

                if current_url in visited:
                    duplicate_count += 1
                else:
                    visited.add(current_url)
                    if is_valid(current_url, base_url):
                        links = future.result()
                        last_found_time = current_time  # Reset the timer when a valid URL is found
                        for link in links:
                            if link not in visited:
                                if is_focused_url(link, focused_url):
                                    focused_urls.append(link)
                                    if len(focused_urls) >= max_to_return:
                                        break
                                to_visit.append(link)

                if total_urls_processed > 0 and (duplicate_count / total_urls_processed) >= max_duplicate_ratio:
                    print(f"Duplicate URL ratio reached {max_duplicate_ratio * 100}%. Ending crawl.")
                    break

    return focused_urls

def initFocusMapping(base_url, focused_url, max_to_return):
    print(f"Starting crawl for {base_url} focused on {focused_url}...")
    urls = crawl(base_url, focused_url, max_to_return)
    return urls


