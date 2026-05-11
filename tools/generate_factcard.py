#!/usr/bin/env python3
"""Generate a GADS-branded visual fact card. Saves to .tmp/factcard.png."""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

IMG_W, IMG_H = 1200, 675
HEADER_H     = 104
FOOTER_H     = 50

# GADS Brand Palette — official guidelines
ESPRESSO    = (26, 18, 16)       # #1A1210
PANEL_BG    = (33, 22, 20)       # #211614 — lifted Espresso for panels
BRONZE      = (139, 112, 86)     # #8B7056
IVORY_SOFT  = (222, 201, 175)    # #DEC9AF
IVORY       = (250, 246, 239)    # #FAF6EF
DIVIDER     = (44, 28, 24)       # Dark bronze-tinted row separator


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


def wrap_text(text: str, font, draw: ImageDraw.ImageDraw, max_width: int) -> list[str]:
    words   = text.split()
    lines   = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        w    = draw.textbbox((0, 0), test, font=font)[2]
        if w > max_width and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def draw_factcard(facts: list[str], topic: str, out_path: Path):
    img  = Image.new("RGB", (IMG_W, IMG_H), ESPRESSO)
    draw = ImageDraw.Draw(img)

    # ── Fonts ─────────────────────────────────────────────────────────────────
    f_eyebrow  = load_font(11)
    f_header   = load_font(26, bold=True)
    f_gads_hdr = load_font(34, bold=True)   # "GADS" top-right brand mark
    f_number   = load_font(46, bold=True)
    f_fact     = load_font(19)
    f_fact_sm  = load_font(17)
    f_footer   = load_font(16, bold=True)   # "GADS" footer brand mark

    # ── Header panel ──────────────────────────────────────────────────────────
    draw.rectangle([(0, 0), (IMG_W, HEADER_H)], fill=PANEL_BG)
    draw.rectangle([(0, HEADER_H - 3), (IMG_W, HEADER_H)], fill=BRONZE)

    draw.text((48, 20), "GADS NEWSLETTER", font=f_eyebrow, fill=BRONZE)
    topic_display = topic if len(topic) <= 52 else topic[:50] + "…"
    draw.text((48, 42), f"Quick Facts: {topic_display}", font=f_header, fill=IVORY)

    # "GADS" brand mark — top-right, large Ivory
    gads_hdr = "GADS"
    ghbbox = draw.textbbox((0, 0), gads_hdr, font=f_gads_hdr)
    ghw    = ghbbox[2] - ghbbox[0]
    ghh    = ghbbox[3] - ghbbox[1]
    draw.text((IMG_W - ghw - 40, (HEADER_H - ghh) // 2),
              gads_hdr, font=f_gads_hdr, fill=IVORY)

    # ── Fact rows ─────────────────────────────────────────────────────────────
    content_top    = HEADER_H
    content_bottom = IMG_H - FOOTER_H
    row_h          = (content_bottom - content_top) // 5

    PAD_X    = 48
    NUM_W    = 78
    SEP_GAP  = 22
    text_x   = PAD_X + NUM_W + SEP_GAP * 2
    text_max = IMG_W - text_x - PAD_X

    for i, fact in enumerate(facts[:5]):
        y = content_top + i * row_h

        if i > 0:
            draw.line([(PAD_X, y), (IMG_W - PAD_X, y)], fill=DIVIDER, width=1)

        # Large Bronze number
        num_str = f"{i + 1:02d}"
        nbbox   = draw.textbbox((0, 0), num_str, font=f_number)
        nw, nh  = nbbox[2] - nbbox[0], nbbox[3] - nbbox[1]
        num_x   = PAD_X + (NUM_W - nw) // 2
        num_y   = y + (row_h - nh) // 2 - 3
        draw.text((num_x, num_y), num_str, font=f_number, fill=BRONZE)

        # Thin vertical separator
        sep_x = PAD_X + NUM_W + SEP_GAP
        draw.line([(sep_x, y + 18), (sep_x, y + row_h - 18)],
                  fill=DIVIDER, width=1)

        # Fact text
        lines   = wrap_text(fact, f_fact, draw, text_max)
        line_h  = 27
        total_h = len(lines) * line_h
        base_y  = y + (row_h - total_h) // 2

        for j, line in enumerate(lines):
            font  = f_fact    if j == 0 else f_fact_sm
            color = IVORY     if j == 0 else IVORY_SOFT
            draw.text((text_x, base_y + j * line_h), line, font=font, fill=color)

    # ── Footer panel — "GADS" only ─────────────────────────────────────────────
    draw.rectangle([(0, IMG_H - FOOTER_H), (IMG_W, IMG_H)], fill=PANEL_BG)
    gads_ftr  = "GADS"
    gfbbox = draw.textbbox((0, 0), gads_ftr, font=f_footer)
    gfw    = gfbbox[2] - gfbbox[0]
    gfh    = gfbbox[3] - gfbbox[1]
    draw.text(((IMG_W - gfw) // 2, IMG_H - FOOTER_H + (FOOTER_H - gfh) // 2),
              gads_ftr, font=f_footer, fill=BRONZE)

    img.save(out_path, "PNG")


def main():
    tmp          = Path(__file__).parent.parent / ".tmp"
    content_path = tmp / "newsletter_content.json"

    if not content_path.exists():
        print("Error: .tmp/newsletter_content.json not found. Run write_newsletter.py first.",
              file=sys.stderr)
        sys.exit(1)

    content  = json.loads(content_path.read_text())
    facts    = content.get("facts", [])
    topic    = content.get("topic", "Newsletter")
    out_path = tmp / "factcard.png"

    if not facts:
        facts = ["No facts extracted from research."] * 5

    draw_factcard(facts, topic, out_path)
    print(f"Fact card saved → {out_path}", file=sys.stderr)
    print(json.dumps({"path": str(out_path)}))


if __name__ == "__main__":
    main()
