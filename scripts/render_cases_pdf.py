"""Render paper/supplement/cases.csv as a print-friendly one-page PDF table.

Keeps a readable subset of the columns (the full data stays in cases.csv) so the
per-detection breakdown can be attached as a PDF alongside the CSV.

Usage: python scripts/render_cases_pdf.py
Output: paper/supplement/cases.pdf
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parent.parent
SUP = REPO / "paper" / "supplement"

# (csv column, header shown)
COLS = [
    ("image", "img"), ("det", "det"), ("yolo_class", "yolo"),
    ("yolo_conf", "conf"), ("population", "population"),
    ("hier_outcome", "outcome"), ("hier_node", "reported"),
    ("top_leaf_cosine", "cos"), ("importance", "imp"),
    ("nearest_floor", "floor"), ("flat_leaf", "flat_leaf"),
    ("kpi_verdict", "verdict"), ("plausible", "plausible"),
]

ROW_C = {"safe": "#eafaf1", "useful": "#eafaf1", "unknown": "#fef9e7",
         "wrong_branch": "#fdedec", "UNSAFE_wrong_leaf": "#fdedec"}


def main():
    rows = list(csv.DictReader((SUP / "cases.csv").open()))
    table = [[r[c] for c, _ in COLS] for r in rows]
    headers = [h for _, h in COLS]

    fig, ax = plt.subplots(figsize=(13, 0.22 * len(rows) + 1.2))
    ax.axis("off")
    ax.set_title("Per-detection breakdown (paper/supplement/cases.csv)",
                 fontsize=10, loc="left")
    tbl = ax.table(cellText=table, colLabels=headers, loc="upper center",
                   cellLoc="left")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(6)
    tbl.scale(1, 1.05)
    # header style + per-row tint by verdict; mark implausible in bold red
    plaus_i = [c for c, _ in COLS].index("plausible")
    for (r, c), cell in tbl.get_celld().items():
        cell.set_linewidth(0.2)
        if r == 0:
            cell.set_facecolor("#2c3e50"); cell.set_text_props(color="w", weight="bold")
        else:
            verdict = rows[r - 1]["kpi_verdict"]
            cell.set_facecolor(ROW_C.get(verdict, "#ffffff"))
            if c == plaus_i and rows[r - 1]["plausible"] == "False":
                cell.set_text_props(color="#c0392b", weight="bold")

    fig.savefig(SUP / "cases.pdf", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f">>> wrote {SUP / 'cases.pdf'} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
