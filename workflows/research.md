# Research Sub-Workflow

## Objective
Find and extract relevant, recent web content about a given topic to use as source material for the newsletter.

## Required Inputs
- `topic`: the newsletter subject (string)

## Steps

### 1. Web Search
Run the search tool to find relevant pages:
```
python tools/search_web.py "<topic>" 6
```
Output: `.tmp/search_results.json` — list of `{title, url, snippet}` objects.

**If you get a `RatelimitException`:**
- The tool retries automatically with exponential backoff (up to 5 attempts)
- If all retries fail, wait 60 seconds and run again
- As a last resort, manually provide 3-5 URLs by editing `.tmp/search_results.json` directly:
  ```json
  [{"title": "Article Title", "url": "https://...", "snippet": ""}]
  ```

### 2. Scrape Pages
Extract text content from the found URLs:
```
python tools/scrape_page.py
```
Output: `.tmp/scraped_content.json` — list of `{url, title, text}` objects.

**Known limitations:**
- Pages behind JavaScript or paywalls will be skipped; their DuckDuckGo snippet is used instead
- If fewer than 3 pages scraped successfully, the research may be thin — consider adding more URLs manually to `.tmp/search_results.json` and re-running

### 3. Quality Check
Before proceeding to writing, verify the scraped content:
- Open `.tmp/scraped_content.json` and confirm at least 3 entries have `text` longer than 200 chars
- If the content looks off-topic or too sparse, re-run with a more specific topic string

## Output
`.tmp/scraped_content.json` — ready to pass to `write_newsletter.py`

## Edge Cases

| Situation | Action |
|---|---|
| DuckDuckGo rate-limited repeatedly | Wait 5 min, try again; or manually populate search results |
| All pages return 403/paywall | Use snippet-only mode (automatic); add niche/blog URLs manually |
| Topic too broad (vague results) | Narrow the topic string: "AI automation 2025" instead of "AI" |
| Topic too narrow (< 3 results) | Broaden slightly or add language variants |
