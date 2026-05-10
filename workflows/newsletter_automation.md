# Newsletter Automation — Main SOP

## Objective
Given a topic, produce a fully formatted HTML newsletter and send it via Gmail — entirely for free.

## Pipeline Overview
```
Topic → Search → Scrape → Write (Groq) → Chart → Fact Card → HTML → Send (Gmail)
```

---

## One-Time Setup

### A. Groq API Key (Free)
1. Go to https://console.groq.com and create a free account
2. Navigate to **API Keys** → **Create API Key**
3. Copy the key and paste it into `.env`:
   ```
   GROQ_API_KEY=gsk_...
   ```

### B. Gmail API via Google Cloud (Free)
1. Go to https://console.cloud.google.com and create a **New Project** (e.g. "newsletter-automation")
2. In the left menu: **APIs & Services → Library** → search "Gmail API" → **Enable**
3. Go to **APIs & Services → OAuth consent screen**:
   - User type: **External**
   - Fill in App name (e.g. "Newsletter Bot"), your email as support email and developer contact
   - Scopes: add `https://www.googleapis.com/auth/gmail.send`
   - Test users: add your Gmail address
   - Save
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
   - Application type: **Desktop app**
   - Name it anything (e.g. "newsletter-desktop")
   - Click **Create** → **Download JSON**
5. Rename the downloaded file to `credentials.json` and place it in the project root (`newsletter/credentials.json`)
6. First time you run `send_gmail.py`, a browser window opens asking you to approve access — do so. This creates `token.json` which is reused for all future runs.

### C. Python Dependencies
```bash
pip install -r requirements.txt
```

---

## Running the Full Pipeline

Replace `"<topic>"` with your actual topic each time.

```bash
# Step 1: Research
python tools/search_web.py "<topic>"
python tools/scrape_page.py

# Step 2: Write
python tools/write_newsletter.py "<topic>"

# Step 3: Visuals
python tools/generate_chart.py
python tools/generate_factcard.py

# Step 4: Format
python tools/format_html.py

# Step 5: Send
python tools/send_gmail.py --to lucasgraf01@gmail.com
```

All intermediate files are saved to `.tmp/`. You can inspect them at any stage before proceeding.

---

## What Each Tool Outputs

| Tool | Output File | Contains |
|---|---|---|
| `search_web.py` | `.tmp/search_results.json` | URLs + snippets from DuckDuckGo |
| `scrape_page.py` | `.tmp/scraped_content.json` | Extracted page text |
| `write_newsletter.py` | `.tmp/newsletter_content.json` | Prose, stats, facts, subject line |
| `generate_chart.py` | `.tmp/chart.png` | Horizontal bar chart (600×400) |
| `generate_factcard.py` | `.tmp/factcard.png` | Visual fact card (900×600) |
| `format_html.py` | `.tmp/newsletter.html` | Full HTML email (images inline) |

---

## Edge Cases

| Situation | Action |
|---|---|
| No stats in research | Chart shows "No data" placeholder — newsletter still sends fine |
| Groq returns malformed JSON | Re-run `write_newsletter.py` — temperature randomness is the usual cause |
| Gmail OAuth browser doesn't open | Run with `--no-browser` not supported; ensure desktop access |
| `credentials.json` not found | Re-download from Google Cloud Console (see Setup B above) |
| `token.json` expired | Delete it and run `send_gmail.py` again to re-authenticate |
| Scrape returns < 3 results | See `workflows/research.md` for manual fallback |

---

## Customising the Newsletter

- **Template**: Edit `templates/newsletter.html.j2` to change layout, colors, or sections
- **Tone/style**: Edit the `SYSTEM_PROMPT` in `tools/write_newsletter.py`
- **Number of search results**: Pass a second argument: `python tools/search_web.py "<topic>" 10`
- **Chart style**: Edit colors/dimensions in `tools/generate_chart.py` (BG_COLOR, BAR_COLOR, etc.)
- **Fact card style**: Edit colors/fonts in `tools/generate_factcard.py`

---

## Cost Summary
Everything is free:
- Groq: 14,400 req/day on Llama 3.1 8B; 1,000/day on Llama 3.3 70B
- Gmail API: free, no quota concerns for personal use
- DuckDuckGo: free, rate-limited but sufficient
- All Python libraries: open source
