"""Render the full taxonomy as a clean left-to-right architecture diagram.

This is the paper's "Figure 2" (taxonomic hierarchy), generated from the actual
taxonomy.yaml so the figure can never drift from the running system. Safety
floors (the anti-paranoia limit) are highlighted.

Usage: python scripts/make_taxonomy_figure.py
Output: figures/taxonomy_architecture.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hpercept.taxonomy import Node, Taxonomy   # noqa: E402

OUT = REPO / "figures"
OUT.mkdir(exist_ok=True)

COL_W = 3.05        # horizontal distance between levels
BOX_W = 2.75        # node box width
BOX_H = 0.66        # node box height
ROOT_C = "#2c3e50"
FLOOR_C = "#f39c12"
LEAF_C = "#eef1f4"
INNER_C = "#d6dde3"


def layout(node: Node, depth: int, counter: list[int], pos: dict):
    x = depth * COL_W
    if node.is_leaf:
        y = counter[0]
        counter[0] += 1
    else:
        ys = [layout(c, depth + 1, counter, pos) for c in node.children]
        y = sum(ys) / len(ys)
    pos[node.name] = (x, y)
    return y


def draw(tax: Taxonomy):
    pos: dict[str, tuple[float, float]] = {}
    layout(tax.root, 0, [0], pos)

    n_leaves = sum(1 for _ in (n for n in tax.iter_nodes() if n.is_leaf))
    max_depth = tax.max_depth
    fig_w = (max_depth + 1) * 1.55
    fig_h = max(6, n_leaves * 0.52)
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))

    # connectors first (behind boxes)
    for node in tax.iter_nodes():
        x, y = pos[node.name]
        for c in node.children:
            cx, cy = pos[c.name]
            midx = x + BOX_W + (cx - x - BOX_W) * 0.5
            ax.plot([x + BOX_W, midx, midx, cx], [y, y, cy, cy],
                    color="#b0b8bf", lw=0.9, zorder=1)

    # boxes
    for node in tax.iter_nodes():
        x, y = pos[node.name]
        if node.is_root:
            face, txt, weight = ROOT_C, "white", "bold"
        elif node.floor:
            face, txt, weight = FLOOR_C, "black", "bold"
        elif node.is_leaf:
            face, txt, weight = LEAF_C, "#2c3e50", "normal"
        else:
            face, txt, weight = INNER_C, "#2c3e50", "normal"
        ax.add_patch(FancyBboxPatch(
            (x, y - BOX_H / 2), BOX_W, BOX_H,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor=face, edgecolor="#8a949c", linewidth=0.6, zorder=2))
        label = node.name + ("  ◆" if node.floor else "")
        ax.text(x + BOX_W / 2, y, label, ha="center", va="center",
                fontsize=8.2, color=txt, fontweight=weight, zorder=3)
        # tiny COCO hint under leaves that map to a detector class
        if node.coco:
            ax.text(x + BOX_W / 2, y - BOX_H / 2 - 0.16,
                    "coco: " + ", ".join(node.coco), ha="center", va="top",
                    fontsize=5.4, color="#7f8c8d", style="italic", zorder=3)

    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    ax.set_xlim(min(xs) - 0.4, max(xs) + BOX_W + 0.4)
    ax.set_ylim(min(ys) - 0.9, max(ys) + 0.9)
    ax.invert_yaxis()
    ax.axis("off")
    ax.set_title(
        "Object taxonomy for constrained perception\n"
        "◆ = safety floor: abstraction never falls back above this level "
        "(else → UNKNOWN OBSTACLE)",
        fontsize=11, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT / "taxonomy_architecture.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f">>> wrote figures/taxonomy_architecture.png "
          f"({sum(1 for _ in tax.iter_nodes())} nodes, {n_leaves} leaves, "
          f"depth {max_depth})")


if __name__ == "__main__":
    draw(Taxonomy.load(REPO / "taxonomy.yaml"))
