#!/usr/bin/env python3
"""Generate a GADS-branded data chart. Saves to .tmp/chart.png."""

import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).parent.parent

# GADS Brand Palette — official guidelines
ESPRESSO    = "#1A1210"
BRONZE      = "#8B7056"
IVORY_SOFT  = "#DEC9AF"
IVORY       = "#FAF6EF"
SILVER      = "#9A9490"
BAR_TRACK   = "#2C1C18"


def parse_value(raw) -> float:
    s = str(raw).replace(",", "").replace(" ", "").replace(" ", "")
    m = re.search(r"\d+\.?\d*", s)
    return float(m.group()) if m else 0.0


def main():
    tmp = BASE / ".tmp"
    content_path = tmp / "newsletter_content.json"

    if not content_path.exists():
        print("Error: newsletter_content.json not found.", file=sys.stderr)
        sys.exit(1)

    content  = json.loads(content_path.read_text())
    stats    = content.get("stats", [])
    out_path = tmp / "chart.png"

    if len(stats) < 2:
        fig, ax = plt.subplots(figsize=(12, 4.5), facecolor=ESPRESSO)
        ax.set_facecolor(ESPRESSO)
        ax.text(0.5, 0.5, "No statistical data available",
                ha="center", va="center", color=SILVER, fontsize=16,
                transform=ax.transAxes, fontfamily="sans-serif")
        ax.axis("off")
        fig.savefig(out_path, dpi=150, bbox_inches="tight",
                    facecolor=ESPRESSO, pad_inches=0.25)
        plt.close(fig)
        print(json.dumps({"path": str(out_path)}))
        return

    labels   = [s["label"]              for s in stats]
    raw_strs = [str(s["value"])          for s in stats]
    values   = [parse_value(s["value"])  for s in stats]

    n      = len(labels)
    fig_h  = 3.6 + n * 1.05
    fig, ax = plt.subplots(figsize=(12, fig_h), facecolor=ESPRESSO)
    ax.set_facecolor(ESPRESSO)

    max_val = max(values) if max(values) > 0 else 1.0
    x_max   = max_val * 1.32

    # Dark track behind each bar
    for i in range(n):
        ax.barh(i, x_max * 0.97, height=0.50,
                color=BAR_TRACK, zorder=1, align="center")

    # Bronze bars
    bars = ax.barh(range(n), values, height=0.50,
                   color=BRONZE, zorder=2, align="center")

    # Bright leading-edge accent
    accent_w = max_val * 0.006
    for i in range(n):
        ax.barh(i, accent_w, height=0.50,
                color="#B09070", zorder=3, align="center")

    # Value labels right of each bar
    for i, (bar, raw) in enumerate(zip(bars, raw_strs)):
        w = bar.get_width()
        ax.text(w + x_max * 0.022, i, raw,
                va="center", ha="left",
                color=IVORY, fontsize=13, fontweight="bold",
                fontfamily="sans-serif")

    # Y-axis category labels
    ax.set_yticks(range(n))
    ax.set_yticklabels(labels, color=IVORY_SOFT, fontsize=12,
                       fontfamily="sans-serif")
    ax.tick_params(axis="y", length=0, pad=14)

    ax.set_xlim(0, x_max)
    ax.xaxis.set_visible(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_ylim(-0.65, n - 0.35)

    # Header: eyebrow + title + accent rule
    fig.text(0.055, 0.97, "BY THE NUMBERS",
             color=BRONZE, fontsize=9, fontweight="bold",
             va="top", transform=fig.transFigure,
             fontfamily="sans-serif")
    fig.text(0.055, 0.90, "Key Statistics",
             color=IVORY, fontsize=20, fontweight="bold",
             va="top", transform=fig.transFigure,
             fontfamily="sans-serif")
    fig.add_artist(plt.Line2D(
        [0.055, 0.30], [0.83, 0.83],
        transform=fig.transFigure, color=BRONZE, linewidth=1.5,
    ))

    # "GADS" brand mark — top-right, large Ivory text
    fig.text(0.945, 0.96, "GADS",
             color=IVORY, fontsize=26, fontweight="bold",
             ha="right", va="top", transform=fig.transFigure,
             fontfamily="sans-serif")

    plt.subplots_adjust(left=0.30, right=0.84, top=0.80, bottom=0.05)
    fig.savefig(out_path, dpi=150, bbox_inches="tight",
                facecolor=ESPRESSO, pad_inches=0.28)
    plt.close(fig)

    print(f"Chart saved → {out_path}", file=sys.stderr)
    print(json.dumps({"path": str(out_path)}))


if __name__ == "__main__":
    main()
