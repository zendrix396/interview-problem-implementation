from curl_cffi import requests
from bs4 import BeautifulSoup
import time
import json

API_URL = "https://hoi4.paradoxwikis.com/api.php"
START_PAGE = "Hearts_of_Iron_4_Wiki"
OUTPUT_FILE = "hoi4_database.txt"

DELAY_BETWEEN_PAGES = 0.5 

MAX_PAGES_TO_SCRAPE = None 

visited_pages = set()
pages_queue = [START_PAGE]

queued_pages = {START_PAGE}

def get_page_content(title):
    params = {
        "action": "parse",
        "page": title,
        "format": "json",
        "prop": "text|links",  
        "redirects": 1        
    }
    
    try:
        response = requests.get(API_URL, params=params, impersonate="chrome120", timeout=10)
        data = response.json()
        
        if "error" in data:
            print(f"Skipped '{title}': {data['error'].get('info')}")
            return None
            
        return data['parse']
    except Exception as e:
        print(f"Connection failed for '{title}': {e}")
        return None

def clean_html_to_text(html_code):
    soup = BeautifulSoup(html_code, "html.parser")
    for script in soup(["script", "style"]):
        script.extract()
        
    text = soup.get_text(separator="\n")
    
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    return text

print(f"Starting Crawler on: {START_PAGE}")
print(f"Saving data to: {OUTPUT_FILE}")
print("Press Ctrl+C to stop the script at any time.\n")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    count = 0
    while pages_queue:
        if MAX_PAGES_TO_SCRAPE and count >= MAX_PAGES_TO_SCRAPE:
            print("Max page limit reached.")
            break
        
        current_title = pages_queue.pop(0)
        visited_pages.add(current_title)
        
        print(f"[{count+1}] Scraping: {current_title} ...", end="", flush=True)
        data = get_page_content(current_title)
        
        if data:
            raw_html = data['text']['*']
            readable_text = clean_html_to_text(raw_html)
            
            separator = "="*60
            f.write(f"\n\n{separator}\nPAGE TITLE: {current_title}\n{separator}\n")
            f.write(readable_text)
            f.write(f"\n{separator}\n")
            
            print(" Done. ", end="")
            
            new_links_count = 0
            if 'links' in data:
                for link_obj in data['links']:
                    link_title = link_obj['*']
                    namespace = link_obj.get('ns', 0)
                    
                    if namespace == 0:
                        if link_title not in visited_pages and link_title not in queued_pages:
                            pages_queue.append(link_title)
                            queued_pages.add(link_title)
                            new_links_count += 1
            
            print(f"(Found {new_links_count} new pages)")
            count += 1
        
        time.sleep(DELAY_BETWEEN_PAGES)

print(f"Crawler finished! Scraped {count} pages.")

