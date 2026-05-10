#!/usr/bin/env python3
"""Generate a horizontal bar chart from stats in .tmp/newsletter_content.json. Saves to .tmp/chart.png."""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# GADS Brand Colors
BG_COLOR = "#2E1B0E"       # Espresso
BAR_COLOR = "#3D6B78"      # Slate
BAR_HOVER = "#9B7B50"      # Bronze
TEXT_COLOR = "#F5F0EB"     # Ivory
MUTED_COLOR = "#E8DDD0"    # Ivory Soft
GRID_COLOR = "#4A3020"     # Espresso Mid

WIDTH, HEIGHT = 6.5, 4


def draw_placeholder(out_path: Path, topic: str):
    fig, ax = plt.subplots(figsize=(WIDTH, HEIGHT), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.text(0.5, 0.5, f"No numerical data\nfound for this topic",
            ha="center", va="center", color=MUTED_COLOR,
            fontsize=13, fontfamily="sans-serif", transform=ax.transAxes)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, facecolor=BG_COLOR)
    plt.close(fig)


def draw_chart(stats: list[dict], topic: str, out_path: Path):
    labels = [s["label"] for s in stats]
    values = [float(s["value"]) for s in stats]
    max_val = max(values)

    fig, ax = plt.subplots(figsize=(WIDTH, HEIGHT), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    bars = ax.barh(labels, values, color=BAR_COLOR, height=0.45, zorder=2)

    for bar, val in zip(bars, values):
        ax.text(
            bar.get_width() + max_val * 0.015,
            bar.get_y() + bar.get_height() / 2,
            f"{val:g}",
            va="center", ha="left", color=TEXT_COLOR,
            fontsize=11, fontweight="bold", fontfamily="sans-serif",
        )

    ax.spines[:].set_visible(False)
    ax.xaxis.set_visible(False)
    ax.tick_params(colors=MUTED_COLOR, labelsize=10)
    for label in ax.get_yticklabels():
        label.set_color(MUTED_COLOR)
        label.set_fontfamily("sans-serif")

    ax.set_title(f"Key Numbers · {topic}", color=TEXT_COLOR,
                 fontsize=12, fontweight="bold", fontfamily="sans-serif", pad=14)

    ax.grid(axis="x", color=GRID_COLOR, zorder=1, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_xlim(0, max_val * 1.22)

    # GADS footer line
    fig.text(0.92, 0.02, "GADS", ha="right", fontsize=9,
             color="#9B7B50", fontfamily="sans-serif", fontstyle="normal")

    fig.tight_layout(rect=[0, 0.04, 1, 1])
    fig.savefig(out_path, dpi=150, facecolor=BG_COLOR, bbox_inches="tight")
    plt.close(fig)


def main():
    tmp = Path(__file__).parent.parent / ".tmp"
    content_path = tmp / "newsletter_content.json"

    if not content_path.exists():
        print("Error: .tmp/newsletter_content.json not found. Run write_newsletter.py first.", file=sys.stderr)
        sys.exit(1)

    content = json.loads(content_path.read_text())
    stats = content.get("stats", [])
    topic = content.get("topic", "Newsletter")
    out_path = tmp / "chart.png"

    if len(stats) < 2:
        print("Not enough stats — generating placeholder.", file=sys.stderr)
        draw_placeholder(out_path, topic)
    else:
        draw_chart(stats, topic, out_path)
        print(f"Chart with {len(stats)} bars generated.", file=sys.stderr)

    print(f"Saved → {out_path}", file=sys.stderr)
    print(json.dumps({"path": str(out_path)}))


if __name__ == "__main__":
    main()
