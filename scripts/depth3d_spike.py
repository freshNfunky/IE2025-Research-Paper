"""Spike C demo: 2D vs 3D mode via monocular depth + flatness test.

For each YOLO detection we estimate depth and measure how flat the region is.
In "3D mode" a flat detection (a 2D depiction: billboard, poster, painted
surface, a thin/sky object) is flagged as a likely false positive, which the 2D
appearance path cannot do.

Usage: python scripts/depth3d_spike.py [n_images]
Outputs: figures/depth3d_*.png and a per-box summary.
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

from hpercept import datasets                          # noqa: E402
from hpercept.detector import get_detector             # noqa: E402
from hpercept.openworld.depth import MonoDepth, flatness  # noqa: E402
from hpercept.pipeline import get_pipeline             # noqa: E402

OUT = REPO / "figures"
OUT.mkdir(exist_ok=True)


def render(image, depth, boxes, flats, path):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 5.5))
    a1.imshow(image); a1.axis("off"); a1.set_title("3D mode: flat detections flagged")
    a2.imshow(depth, cmap="plasma"); a2.axis("off")
    a2.set_title("monocular depth (nearer = bright)")
    cmap = {"3d": "#2ecc71", "flat": "#e74c3c", "n/a": "#95a5a6"}
    for box, fl in zip(boxes, flats):
        x1, y1, x2, y2 = box.xyxy
        col = cmap[fl.verdict]
        for ax in (a1, a2):
            ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                                   edgecolor=col, linewidth=2.2))
        tag = f"{box.coco_name}  {fl.verdict.upper()}  relief={fl.relief:.2f}"
        a1.text(x1, max(0, y1 - 4), tag, fontsize=7.5, color="white", va="bottom",
                bbox=dict(boxstyle="round,pad=0.15", fc=col, ec="none"))
    fig.tight_layout(); fig.savefig(path, dpi=150, bbox_inches="tight"); plt.close(fig)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    pipe = get_pipeline()
    det = get_detector(pipe.weights, 0.20)
    md = MonoDepth()

    print(f">>> streaming {n} images; estimating depth (first call downloads the model)",
          flush=True)
    samples = datasets.get_source("road_anomaly").load(n)

    n_flat = n_box = 0
    for i, s in enumerate(samples):
        boxes = det.detect(s.image, conf=0.20)
        if not boxes:
            continue
        depth = md.depth(s.image)
        flats = [flatness(depth, b) for b in boxes]
        render(s.image, depth, boxes, flats, OUT / f"depth3d_{i:02d}.png")
        for b, fl in zip(boxes, flats):
            n_box += 1; n_flat += int(fl.is_flat)
            print(f"  img{i} {b.coco_name:<12} relief={fl.relief:.3f} step={fl.step:.3f} "
                  f"-> {fl.verdict.upper()}", flush=True)
    print(f"\n>>> {n_flat}/{n_box} assessable detections flagged flat "
          f"(possible 2D false positives); small boxes marked n/a", flush=True)


if __name__ == "__main__":
    main()
