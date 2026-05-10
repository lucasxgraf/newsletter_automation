#!/usr/bin/env python3
"""Use Groq LLM to write newsletter content and extract structured data. Saves to .tmp/newsletter_content.json."""

import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv(Path(__file__).parent.parent / ".env")

SYSTEM_PROMPT = """You are an expert newsletter writer. You write engaging, well-researched newsletters in a clear and informative style.
You always respond with valid JSON — nothing else outside the JSON block."""

USER_PROMPT_TEMPLATE = """Write a newsletter about the topic: "{topic}"

Use the following research as your source material:

---
{research}
---

Return a single JSON object with exactly these fields:

{{
  "subject_line": "Compelling email subject line (max 60 chars)",
  "intro": "Engaging opening paragraph (2-3 sentences)",
  "sections": [
    {{"heading": "Section 1 heading", "body": "2-3 paragraphs of content"}},
    {{"heading": "Section 2 heading", "body": "2-3 paragraphs of content"}},
    {{"heading": "Section 3 heading", "body": "2-3 paragraphs of content"}}
  ],
  "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3", "Takeaway 4", "Takeaway 5"],
  "stats": [
    {{"label": "Stat label", "value": 42}},
    {{"label": "Another stat", "value": 78}}
  ],
  "facts": [
    "Interesting fact 1 from the research",
    "Interesting fact 2 from the research",
    "Interesting fact 3 from the research",
    "Interesting fact 4 from the research",
    "Interesting fact 5 from the research"
  ]
}}

Rules:
- "stats" must contain 2-4 items where "value" is always a plain number (no units, no % sign — put units in the label instead). Only include stats if real numerical data appears in the research; otherwise use an empty array.
- "facts" must contain exactly 5 short, punchy facts drawn from the research.
- Return ONLY the JSON object. No markdown fences, no explanations."""


def build_research_text(scraped_path: Path) -> str:
    data = json.loads(scraped_path.read_text())
    parts = []
    for item in data:
        parts.append(f"Source: {item['url']}\n{item['text']}")
    return "\n\n---\n\n".join(parts)


def extract_json(raw: str) -> dict:
    raw = raw.strip()
    # Strip markdown code fences if the model added them anyway
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def main():
    if len(sys.argv) < 2:
        print("Usage: python write_newsletter.py \"<topic>\"", file=sys.stderr)
        sys.exit(1)

    topic = sys.argv[1]
    tmp = Path(__file__).parent.parent / ".tmp"
    scraped_path = tmp / "scraped_content.json"

    if not scraped_path.exists():
        print("Error: .tmp/scraped_content.json not found. Run scrape_page.py first.", file=sys.stderr)
        sys.exit(1)

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY not set in .env", file=sys.stderr)
        sys.exit(1)

    research = build_research_text(scraped_path)
    prompt = USER_PROMPT_TEMPLATE.format(topic=topic, research=research[:12000])

    print("Calling Groq API...", file=sys.stderr)
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=4096,
    )

    raw = response.choices[0].message.content
    content = extract_json(raw)
    content["topic"] = topic

    out_path = tmp / "newsletter_content.json"
    out_path.write_text(json.dumps(content, indent=2, ensure_ascii=False))

    print(f"Newsletter written → {out_path}", file=sys.stderr)
    print(f"Subject: {content.get('subject_line', '')}", file=sys.stderr)
    print(json.dumps({"subject_line": content.get("subject_line"), "path": str(out_path)}))


if __name__ == "__main__":
    main()
