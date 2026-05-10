#!/usr/bin/env python3
"""Search the web for a topic using DuckDuckGo. Saves results to .tmp/search_results.json."""

import json
import random
import sys
import time
from pathlib import Path

from ddgs import DDGS
from ddgs.exceptions import RatelimitException


def search(topic: str, num_results: int = 6) -> list[dict]:
    results = []
    max_attempts = 5

    for attempt in range(max_attempts):
        try:
            with DDGS() as ddgs:
                raw = list(ddgs.text(topic, max_results=num_results))
            results = [
                {"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")}
                for r in raw
            ]
            break
        except RatelimitException:
            if attempt == max_attempts - 1:
                raise
            wait = (2 ** attempt) + random.uniform(0, 1)
            print(f"Rate limited — retrying in {wait:.1f}s (attempt {attempt + 1}/{max_attempts})", file=sys.stderr)
            time.sleep(wait)

    return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python search_web.py \"<topic>\" [num_results]", file=sys.stderr)
        sys.exit(1)

    topic = sys.argv[1]
    num_results = int(sys.argv[2]) if len(sys.argv) > 2 else 6

    print(f"Searching for: {topic}", file=sys.stderr)
    results = search(topic, num_results)

    out_path = Path(__file__).parent.parent / ".tmp" / "search_results.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))

    print(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nSaved {len(results)} results to {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
