import os
import sys
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# CONFIG

if len(sys.argv) < 2:
    print("Usage: python downloader.py <URL>")
    sys.exit(1)

BASE_URL = sys.argv[1].rstrip("/")
DOWNLOAD_DIR = "website_copy"

VISITED_PAGES = set()
ASSET_QUEUE = set()

# ---------------- HELPERS ----------------

def safe_local_path(url):
    parsed = urlparse(url)

    path = parsed.path

    if path.endswith("/") or path == "":
        path += "index.html"

    if "." not in os.path.basename(path):
        path += ".html"

    return os.path.join(DOWNLOAD_DIR, path.lstrip("/"))


def ensure_directory(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def make_relative_path(target_url, current_page_url):
    target_local = safe_local_path(target_url)
    current_local = safe_local_path(current_page_url)

    current_dir = os.path.dirname(current_local)

    relative = os.path.relpath(target_local, current_dir)

    return relative.replace("\\", "/")


# ---------------- PAGE CRAWLER ----------------

def crawl_page(url):

    if url in VISITED_PAGES:
        return

    VISITED_PAGES.add(url)

    print(f"[PAGE] {url}")

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return

    except Exception as e:
        print(f"Failed page: {url} -> {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # -------- COLLECT ASSETS --------

    asset_tags = {
        "img": "src",
        "script": "src",
        "link": "href",
        "video": "src",
        "audio": "src",
        "source": "src",
    }

    for tag, attr in asset_tags.items():

        for element in soup.find_all(tag):

            if not element.has_attr(attr):
                continue

            asset_url = urljoin(url, element[attr])

            if asset_url.startswith("data:"):
                continue

            parsed = urlparse(asset_url)

            if parsed.scheme not in ["http", "https"]:
                continue

            ASSET_QUEUE.add(asset_url)

            # Rewrite to local path immediately
            relative = make_relative_path(asset_url, url)

            element[attr] = relative

    # -------- FIND NEW PAGES --------

    for link in soup.find_all("a", href=True):

        next_url = urljoin(url, link["href"])

        parsed = urlparse(next_url)

        clean_url = parsed._replace(fragment="").geturl()

        if clean_url.startswith(BASE_URL):

            relative = make_relative_path(clean_url, url)

            link["href"] = relative

            if clean_url not in VISITED_PAGES:
                crawl_page(clean_url)

    # -------- SAVE PAGE --------

    local_path = safe_local_path(url)

    ensure_directory(local_path)

    with open(local_path, "w", encoding="utf-8") as file:
        file.write(str(soup))


# ---------------- ASSET DOWNLOADER ----------------

def download_assets():

    print(f"\nDownloading {len(ASSET_QUEUE)} assets...\n")

    for asset_url in ASSET_QUEUE:

        try:
            response = requests.get(asset_url, timeout=15)

            if response.status_code != 200:
                continue

            local_path = safe_local_path(asset_url)

            ensure_directory(local_path)

            with open(local_path, "wb") as file:
                file.write(response.content)

            print(f"[ASSET] {asset_url}")

        except Exception as e:
            print(f"Failed asset: {asset_url} -> {e}")


# ---------------- MAIN ----------------

if __name__ == "__main__":

    print(f"Starting crawl: {BASE_URL}\n")

    crawl_page(BASE_URL)

    print(f"\nPages complete: {len(VISITED_PAGES)}")

    download_assets()

    print("\nDone.")