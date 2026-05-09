# LIBRARIES

import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# CONFIG

import sys


if len(sys.argv) < 2:
    print("Usage: python script.py <URL>")
    sys.exit(1)

URL = sys.argv[1]
print(f"Starting download from: {URL}")
DOWNLOAD_DIR = "website_copy"
VISITED = set()

# FUNC

def save_page(url):
    response = requests.get(url)
    if response.status_code != 200:
        return
    
    parsed_url = urlparse(url)
    path = parsed_url.path.lstrip("/")
    if path.endswith("/"):
        path += "index.html"
    elif not path.endswith(".html"):
        path += ".html"
    
    local_path = os.path.join(DOWNLOAD_DIR, path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    with open(local_path, "w", encoding="utf-8") as file:
        file.write(response.text)
    
    print(f"Saved {url} -> {local_path}")

    soup = BeautifulSoup(response.text, "html.parser")

    for link in soup.find_all("a", href=True):
        next_url = urljoin(url, link["href"])
        if URL in next_url and next_url not in VISITED:
            VISITED.add(next_url)
            save_page(next_url)

if __name__ == "__main__":
    VISITED.add(URL)
    save_page(URL)