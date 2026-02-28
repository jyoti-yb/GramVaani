import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import time

BASE_URL = "https://www.apnikheti.com"
START_URL = "https://www.apnikheti.com/en/pn/agriculture/"
OUTPUT_DIR = "rag/knowledge_base"

HEADERS = {
    "User-Agent": "AgroGuide-Educational-Project/1.0 (Academic Research Use)"
}

MAX_PAGES = 50
visited = set()


def is_valid_crop_page(url):
    return (
        "/en/pn/agriculture/crops/" in url
        or "/en/pn/agriculture/horticulture/" in url
    )


def extract_links(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    links = set()
    for a in soup.find_all("a", href=True):
        full_url = urljoin(BASE_URL, a["href"])
        if full_url.startswith(BASE_URL):
            links.add(full_url)

    return links


def extract_main_content(soup):
    main_content = soup.find("div", class_="col-md-9")

    if not main_content:
        print("Main content not found.")
        return None

    for tag in main_content(["script", "style", "nav", "footer"]):
        tag.extract()

    text = main_content.get_text(separator="\n")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return "\n".join(lines)


def scrape_crop_page(url):
    print(f"Scraping: {url}")

    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("h1")
    crop_name = title_tag.get_text(strip=True) if title_tag else "unknown_crop"

    text = extract_main_content(soup)

    if not text:
        return

    filename = crop_name.lower().replace(" ", "_").replace("/", "_") + ".txt"

    with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Saved: {filename}")


def run_crawler():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Extracting category links...")
    level1_links = extract_links(START_URL)

    category_links = [
        link for link in level1_links
        if "/en/pn/agriculture/" in link
    ]

    print(f"Found {len(category_links)} category links.")

    count = 0

    for category in category_links:
        print(f"\nScanning category: {category}")
        level2_links = extract_links(category)

        for link in level2_links:
            if is_valid_crop_page(link) and link not in visited:
                visited.add(link)

                scrape_crop_page(link)
                time.sleep(1)  # polite delay

                count += 1
                if count >= MAX_PAGES:
                    print("Reached crawl limit.")
                    return


if __name__ == "__main__":
    run_crawler()