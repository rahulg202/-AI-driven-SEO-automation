import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
from collections import deque

def crawl_website(main_url, delay=0.5):
    queue = deque([main_url])
    visited = set([main_url])
    ordered_links = [main_url]
    base_domain = urlparse(main_url).netloc
    
    print(f"Starting to crawl {main_url}")
    
    while queue:
        current_url = queue.popleft()
        print(f"Crawling: {current_url}")
        
        try:
            time.sleep(delay)
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', '')
            if 'text/html' not in content_type.lower():
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                full_url = urljoin(current_url, href)
                parsed_url = urlparse(full_url)
                
                clean_url = parsed_url._replace(fragment='').geturl()
                
                if (parsed_url.netloc == base_domain and 
                    clean_url not in visited and
                    not any(ext in parsed_url.path.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.zip'])):
                    
                    queue.append(clean_url)
                    visited.add(clean_url)
                    ordered_links.append(clean_url)
                    print(f"  Found: {clean_url}")
                    
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching {current_url}: {e}")
        except Exception as e:
            print(f"  Error processing {current_url}: {e}")
    
    print(f"\nCrawling completed. Found {len(ordered_links)} pages.")
    return ordered_links