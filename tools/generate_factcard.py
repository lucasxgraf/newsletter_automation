#!/usr/bin/env python3
"""Generate a visual fact card from facts in .tmp/newsletter_content.json. Saves to .tmp/factcard.png."""

import json
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

IMG_W, IMG_H = 1200, 675   # 16:9 widescreen

# GADS Brand Colors
BG_COLOR        = (46, 27, 14)      # Espresso #2E1B0E
HEADER_BG       = (74, 48, 32)      # Espresso Mid #4A3020
ACCENT_COLOR    = (61, 107, 120)    # Slate #3D6B78
BRONZE_COLOR    = (155, 123, 80)    # Bronze #9B7B50
TEXT_COLOR      = (245, 240, 235)   # Ivory #F5F0EB
MUTED_COLOR     = (232, 221, 208)   # Ivory Soft #E8DDD0
DIVIDER_COLOR   = (74, 48, 32)      # Espresso Mid

BRAND_ASSETS = Path(__file__).parent.parent / "brand_assets"


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def paste_logo(img: Image.Image, draw: ImageDraw.ImageDraw):
    logo_path = BRAND_ASSETS / "icon_GADS.png"
    if not logo_path.exists():
        return
    icon = Image.open(logo_path).convert("RGBA")
    # Resize icon to fit header area
    icon_h = 48
    ratio = icon_h / icon.size[1]
    icon_w = int(icon.size[0] * ratio)
    icon = icon.resize((icon_w, icon_h), Image.LANCZOS)

    # Place in top-right with padding
    x = IMG_W - icon_w - 40
    y = (90 - icon_h) // 2
    # Convert icon to RGB on Espresso-Mid background for anti-aliasing
    bg_patch = Image.new("RGB", (icon_w, icon_h), HEADER_BG)
    if icon.mode == "RGBA":
        bg_patch.paste(icon, (0, 0), mask=icon.split()[3])
    else:
        bg_patch.paste(icon, (0, 0))
    img.paste(bg_patch, (x, y))


def draw_factcard(facts: list[str], topic: str, out_path: Path):
    img = Image.new("RGB", (IMG_W, IMG_H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Header band
    draw.rectangle([(0, 0), (IMG_W, 90)], fill=HEADER_BG)
    draw.rectangle([(0, 88), (IMG_W, 93)], fill=ACCENT_COLOR)

    # Fonts
    font_headline = load_font(30, bold=True)
    font_label    = load_font(12)
    font_fact     = load_font(19)
    font_number   = load_font(28, bold=True)
    font_footer   = load_font(13)
    font_tag      = load_font(11)

    # Header: label + title
    draw.text((40, 16), "GADS NEWSLETTER", font=font_tag, fill=BRONZE_COLOR)
    draw.text((40, 36), f"5 Key Facts: {topic}", font=font_headline, fill=TEXT_COLOR)

    # Logo icon top-right
    paste_logo(img, draw)

    # Fact rows
    usable_h = IMG_H - 90 - 44  # minus header and footer
    row_h = usable_h // 5

    for i, fact in enumerate(facts[:5]):
        y = 93 + i * row_h

        # Subtle row alternation
        if i % 2 == 0:
            draw.rectangle([(0, y), (IMG_W, y + row_h)], fill=(52, 31, 16))

        # Row separator
        if i > 0:
            draw.line([(40, y), (IMG_W - 40, y)], fill=DIVIDER_COLOR, width=1)

        # Number badge
        badge_y = y + (row_h - 36) // 2
        draw.rounded_rectangle([(40, badge_y), (76, badge_y + 36)], radius=6, fill=ACCENT_COLOR)
        num_text = str(i + 1)
        bbox = draw.textbbox((0, 0), num_text, font=font_number)
        nw, nh = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((40 + (36 - nw) // 2, badge_y + (36 - nh) // 2 - 2), num_text, font=font_number, fill=TEXT_COLOR)

        # Fact text
        wrapped = textwrap.fill(fact, width=80)
        lines = wrapped.split("\n")
        text_y = y + (row_h - len(lines) * 24) // 2
        for j, line in enumerate(lines):
            draw.text((96, text_y + j * 24), line, font=font_fact, fill=MUTED_COLOR if j > 0 else TEXT_COLOR)

    # Footer bar
    draw.rectangle([(0, IMG_H - 44), (IMG_W, IMG_H)], fill=HEADER_BG)
    draw.text((40, IMG_H - 29),
              "Graf Automation & Development Studio · AI Automation · Web Dev · DACH",
              font=font_footer, fill=BRONZE_COLOR)

    img.save(out_path, "PNG")


def main():
    tmp = Path(__file__).parent.parent / ".tmp"
    content_path = tmp / "newsletter_content.json"

    if not content_path.exists():
        print("Error: .tmp/newsletter_content.json not found. Run write_newsletter.py first.", file=sys.stderr)
        sys.exit(1)

    content = json.loads(content_path.read_text())
    facts = content.get("facts", [])
    topic = content.get("topic", "Newsletter")
    out_path = tmp / "factcard.png"

    if not facts:
        print("Warning: no facts found — generating empty card.", file=sys.stderr)
        facts = ["No facts extracted from research."] * 5

    draw_factcard(facts, topic, out_path)
    print(f"Fact card saved → {out_path}", file=sys.stderr)
    print(json.dumps({"path": str(out_path)}))


if __name__ == "__main__":
    main()
