#!/usr/bin/env python3
"""Combine newsletter content + images into a formatted HTML email. Saves to .tmp/newsletter.html."""

import base64
import json
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

BASE = Path(__file__).parent.parent


def encode_image(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("utf-8")


def prepare_logo_b64() -> str:
    """Load the GADS logo, resize to email width, and return as base64."""
    logo_path = BASE / "brand_assets" / "logo_GADS.png"
    if not logo_path.exists():
        return ""
    from PIL import Image
    import io
    img = Image.open(logo_path).convert("RGBA")
    # Resize to a reasonable email display height (keep aspect ratio)
    target_h = 64
    ratio = target_h / img.height
    target_w = int(img.width * ratio)
    img = img.resize((target_w, target_h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def main():
    tmp = BASE / ".tmp"
    content_path = tmp / "newsletter_content.json"
    chart_path = tmp / "chart.png"
    factcard_path = tmp / "factcard.png"

    for p in [content_path, chart_path, factcard_path]:
        if not p.exists():
            print(f"Error: {p} not found. Run previous pipeline steps first.", file=sys.stderr)
            sys.exit(1)

    content = json.loads(content_path.read_text())

    env = Environment(loader=FileSystemLoader(str(BASE / "templates")))
    template = env.get_template("newsletter.html.j2")

    html = template.render(
        subject_line=content.get("subject_line", "Newsletter"),
        topic=content.get("topic", ""),
        intro=content.get("intro", ""),
        sections=content.get("sections", []),
        key_takeaways=content.get("key_takeaways", []),
        chart_b64=encode_image(chart_path),
        factcard_b64=encode_image(factcard_path),
        logo_b64=prepare_logo_b64(),
    )

    out_path = tmp / "newsletter.html"
    out_path.write_text(html, encoding="utf-8")

    print(f"HTML formatted → {out_path}", file=sys.stderr)
    print(json.dumps({"path": str(out_path), "subject_line": content.get("subject_line")}))


if __name__ == "__main__":
    main()
