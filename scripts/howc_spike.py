"""Spike A2 / "HOWC": open-world region proposals + hierarchical classification.

For each image: YOLO gives closed-set boxes; MobileSAM proposes class-agnostic
regions; the regions YOLO missed are classified by the hierarchical abstraction.
This measures how many extra objects a class-agnostic proposer surfaces and how
they label -- the open-world detection front-end for "HOWC".

Usage: python scripts/howc_spike.py [n_images]
Outputs: figures/howc_*.png and a summary.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hpercept import datasets                              # noqa: E402
from hpercept.abstraction import AbstractionConfig, Outcome, classify_crop  # noqa: E402
from hpercept.detector import get_detector                 # noqa: E402
from hpercept.openworld.segment import SamProposer         # noqa: E402
from hpercept.pipeline import get_pipeline                 # noqa: E402

OUT = REPO / "figures"
OUT.mkdir(exist_ok=True)
OC = {Outcome.IDENTIFIED: "#2ecc71", Outcome.ABSTRACTED: "#f39c12",
      Outcome.UNKNOWN: "#e74c3c"}


def render(image, yolo, novel, cls, path):
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.imshow(image); ax.axis("off")
    for y in yolo:                              # closed-set YOLO (blue, dashed)
        x1, y1, x2, y2 = y.xyxy
        ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                               edgecolor="#3498db", linewidth=1.6, linestyle="--"))
    for r, c in zip(novel, cls):                # SAM-only regions, by outcome
        x1, y1, x2, y2 = r.xyxy
        col = OC[c.outcome]
        ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                               edgecolor=col, linewidth=2.4))
        ax.text(x1, max(0, y1 - 3), c.label, fontsize=7.5, color="white",
                va="bottom", bbox=dict(boxstyle="round,pad=0.15", fc=col, ec="none"))
    ax.set_title(f"HOWC : {len(yolo)} YOLO (blue dashed) + "
                 f"{len(novel)} class-agnostic regions YOLO missed (solid)")
    fig.tight_layout(); fig.savefig(path, dpi=150, bbox_inches="tight"); plt.close(fig)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    pipe = get_pipeline()
    tax, clip = pipe.taxonomy, pipe.clip
    cfg = AbstractionConfig()
    det = get_detector(pipe.weights, 0.20)
    sam = SamProposer()

    print(f">>> streaming {n} images (first call downloads MobileSAM ~40 MB)", flush=True)
    samples = datasets.get_source("road_anomaly").load(n)

    tot_yolo = tot_novel = tot_labeled = tot_unknown = 0
    for i, s in enumerate(samples):
        yolo = det.detect(s.image, conf=0.20)
        novel = sam.novel_regions(s.image, yolo)
        cls = [classify_crop(r.crop(s.image), tax, clip, cfg) for r in novel]
        labeled = sum(1 for c in cls if c.outcome is not Outcome.UNKNOWN)
        tot_yolo += len(yolo); tot_novel += len(novel)
        tot_labeled += labeled; tot_unknown += len(novel) - labeled
        if novel:
            render(s.image, yolo, novel, cls, OUT / f"howc_{i:02d}.png")
        print(f"  img{i}: YOLO={len(yolo):2d}  SAM-only={len(novel):2d} "
              f"(labeled {labeled}, unknown {len(novel) - labeled})", flush=True)

    print(f"\n>>> totals: YOLO={tot_yolo}  extra class-agnostic regions={tot_novel} "
          f"(got a taxonomic category: {tot_labeled}, flagged UNKNOWN: {tot_unknown})",
          flush=True)


if __name__ == "__main__":
    main()
