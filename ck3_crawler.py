from curl_cffi import requests
from bs4 import BeautifulSoup
from queue import Queue, Empty
from threading import Thread, Lock
import time
import json

API_URL = "https://ck3.paradoxwikis.com/api.php"
START_PAGE = "Crusader_Kings_III_Wiki"
OUTPUT_FILE = "ck3_database.txt"

NUM_WORKERS = 8
REQUEST_DELAY = 0.15
MAX_PAGES_TO_SCRAPE = None
IMPERSONATE = "chrome120"

visited_pages = set()
queued_pages = {START_PAGE}

visit_lock = Lock()
queue_lock = Lock()
count_lock = Lock()

pages_scraped = 0
stop_crawl = False

pages_queue = Queue()
write_queue = Queue()

pages_queue.put(START_PAGE)


def make_session():
    return requests.Session(
        impersonate=IMPERSONATE,
        timeout=15,
    )


def get_page_content(session, title):
    params = {
        "action": "parse",
        "page": title,
        "format": "json",
        "prop": "text|links",
        "redirects": 1,
    }

    try:
        response = session.get(API_URL, params=params)
        data = response.json()

        if "error" in data:
            print(f"Skipped '{title}': {data['error'].get('info')}")
            return None

        return data["parse"]
    except Exception as e:
        print(f"Connection failed for '{title}': {e}")
        return None


def clean_html_to_text(html_code):
    soup = BeautifulSoup(html_code, "html.parser")

    for tag in soup(["script", "style"]):
        tag.extract()

    text = soup.get_text(separator="\n")
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = "\n".join(chunk for chunk in chunks if chunk)

    return text


def enqueue_link(link_title):
    global stop_crawl

    with queue_lock:
        if stop_crawl:
            return False

        if link_title in visited_pages or link_title in queued_pages:
            return False

        if MAX_PAGES_TO_SCRAPE is not None:
            total_known = len(visited_pages) + len(queued_pages)
            if total_known >= MAX_PAGES_TO_SCRAPE:
                return False

        queued_pages.add(link_title)
        pages_queue.put(link_title)
        return True


def worker(worker_id):
    global pages_scraped, stop_crawl

    session = make_session()

    while True:
        if stop_crawl and pages_queue.empty():
            return

        try:
            current_title = pages_queue.get(timeout=1)
        except Empty:
            if stop_crawl:
                return
            continue

        with visit_lock:
            if current_title in visited_pages:
                pages_queue.task_done()
                continue
            visited_pages.add(current_title)

        with count_lock:
            if MAX_PAGES_TO_SCRAPE is not None and pages_scraped >= MAX_PAGES_TO_SCRAPE:
                stop_crawl = True
                pages_queue.task_done()
                continue

        print(f"[Worker {worker_id}] Scraping: {current_title} ...", end="", flush=True)

        data = get_page_content(session, current_title)

        if data:
            raw_html = data["text"]["*"]
            readable_text = clean_html_to_text(raw_html)

            write_queue.put({
                "title": current_title,
                "text": readable_text,
            })

            new_links_count = 0
            if "links" in data:
                for link_obj in data["links"]:
                    link_title = link_obj["*"]
                    namespace = link_obj.get("ns", 0)

                    if namespace == 0:
                        if enqueue_link(link_title):
                            new_links_count += 1

            with count_lock:
                pages_scraped += 1
                scraped_so_far = pages_scraped
                if MAX_PAGES_TO_SCRAPE is not None and pages_scraped >= MAX_PAGES_TO_SCRAPE:
                    stop_crawl = True

            print(f" Done. (Found {new_links_count} new pages, total scraped: {scraped_so_far})")
        else:
            print(" Failed.")

        pages_queue.task_done()
        time.sleep(REQUEST_DELAY)


def writer():
    separator = "=" * 60

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        while True:
            item = write_queue.get()
            if item is None:
                write_queue.task_done()
                return

            f.write(f"\n\n{separator}\nPAGE TITLE: {item['title']}\n{separator}\n")
            f.write(item["text"])
            f.write(f"\n{separator}\n")
            f.flush()

            write_queue.task_done()


print(f"Starting concurrent crawler on: {START_PAGE}")
print(f"Saving data to: {OUTPUT_FILE}")
print(f"Workers: {NUM_WORKERS}")

writer_thread = Thread(target=writer, daemon=True)
writer_thread.start()

workers = []
for i in range(NUM_WORKERS):
    t = Thread(target=worker, args=(i + 1,), daemon=True)
    t.start()
    workers.append(t)

pages_queue.join()
stop_crawl = True

for t in workers:
    t.join(timeout=2)

write_queue.put(None)
write_queue.join()
writer_thread.join(timeout=2)

print(f"Crawler finished! Scraped {pages_scraped} pages.")

