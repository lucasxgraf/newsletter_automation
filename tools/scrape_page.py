#!/usr/bin/env python3
"""Scrape text content from URLs in .tmp/search_results.json. Saves to .tmp/scraped_content.json."""

import json
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

MAX_CHARS_PER_PAGE = 4000
REQUEST_TIMEOUT = 10


def scrape_url(url: str) -> str | None:
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()

        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 60]
        text = " ".join(paragraphs)
        return text[:MAX_CHARS_PER_PAGE] if text else None
    except Exception as e:
        print(f"  Skipping {url}: {e}", file=sys.stderr)
        return None


def main():
    tmp = Path(__file__).parent.parent / ".tmp"
    search_file = tmp / "search_results.json"

    if not search_file.exists():
        print("Error: .tmp/search_results.json not found. Run search_web.py first.", file=sys.stderr)
        sys.exit(1)

    results = json.loads(search_file.read_text())
    scraped = []

    for item in results:
        url = item["url"]
        print(f"Scraping: {url}", file=sys.stderr)
        text = scrape_url(url)

        if text:
            scraped.append({"url": url, "title": item.get("title", ""), "text": text})
            print(f"  OK — {len(text)} chars", file=sys.stderr)
        else:
            # Fall back to the DuckDuckGo snippet so we don't lose the source entirely
            snippet = item.get("snippet", "")
            if snippet:
                scraped.append({"url": url, "title": item.get("title", ""), "text": snippet})
                print(f"  Using snippet fallback — {len(snippet)} chars", file=sys.stderr)

        time.sleep(0.5)

    out_path = tmp / "scraped_content.json"
    out_path.write_text(json.dumps(scraped, indent=2, ensure_ascii=False))

    print(f"\nScraped {len(scraped)} pages → {out_path}", file=sys.stderr)
    print(json.dumps({"scraped": len(scraped), "path": str(out_path)}))


if __name__ == "__main__":
    main()
