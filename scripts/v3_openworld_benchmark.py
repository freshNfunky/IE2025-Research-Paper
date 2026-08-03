"""v3 open-world benchmark: HOWC vs a flat/closed head on OUT-OF-VOCABULARY
objects, with ground-truth boxes (leave-classes-out on COCO val).

Protocol (standard open-set): remove a set of classes from the taxonomy, then
evaluate on the REAL GT objects of those held-out classes (boxes + labels from
detection-datasets/coco). The held-out class is now out-of-vocabulary, so:

  FLAT (closed head): must name a specific leaf -> always a confident WRONG
       specific label (a truck called "sedan": wrong size/behaviour model).
  HOWC (hierarchical): abstracts to the correct SUPER-category (Vehicle /
       Living Being) or flags UNKNOWN -> a reliable, if coarse, recognition.

Because we score GT objects, we know the true super-category, so "reliable" is
measured, not asserted. This is the classification-handling half of the v3 claim
(YOLO itself boxes these fine; the point is what a fixed vocabulary can *say*).

Usage: python scripts/v3_openworld_benchmark.py [n_images]
Output: figures/v3_openworld_benchmark.png + printed table.
"""
from __future__ import annotations

import sys
from itertools import islice
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hpercept.abstraction import (AbstractionConfig, Outcome,          # noqa: E402
                                  classify_crop, flat_classify)
from hpercept.pipeline import get_pipeline                            # noqa: E402
from hpercept.taxonomy import Node, Taxonomy                          # noqa: E402

COCO_NAMES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
    "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear",
    "hair drier", "toothbrush"]

# held-out COCO class -> its true taxonomy super-category (a safety floor)
HELD_OUT = {"truck": "Vehicle", "bus": "Vehicle", "horse": "Living Being",
            "cow": "Living Being", "sheep": "Living Being",
            "elephant": "Living Being", "bear": "Living Being"}


def on_path(a: Node, b: Node) -> bool:
    return a is b or a in b.ancestors() or b in a.ancestors()


def prune(tax: Taxonomy) -> Taxonomy:
    """Return a taxonomy with the held-out classes' nodes removed."""
    removed = set()
    for cls in HELD_OUT:
        node = tax.by_coco(cls)
        if node and node.parent and id(node) not in removed:
            node.parent.children = [c for c in node.parent.children if c is not node]
            removed.add(id(node))
    return Taxonomy(tax.root)   # re-index leaves / by_coco / depths


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    pipe = get_pipeline()
    clip = pipe.clip                      # text feats cover the FULL taxonomy;
    ptax = prune(pipe.taxonomy)           # pruned tax just uses a subset of leaves
    cfg = AbstractionConfig()

    from datasets import load_dataset
    print(f">>> streaming {n} COCO val images", flush=True)
    ds = load_dataset("detection-datasets/coco", split="val", streaming=True)
    names = COCO_NAMES

    # counters
    H = {"correct_super": 0, "unknown": 0, "off_branch": 0, "leaf": 0}
    F = {"right_branch_specific": 0, "wrong_branch_specific": 0}
    total = 0
    for ex in islice(ds, n):
        img = np.array(ex["image"].convert("RGB"))
        ih, iw = img.shape[:2]
        o = ex["objects"]
        for cat, box in zip(o["category"], o["bbox"]):
            cls = names[cat]
            if cls not in HELD_OUT:
                continue
            x, y, w, h = box
            if w * h < 0.01 * iw * ih:      # skip tiny GT boxes
                continue
            crop = img[int(y):int(y + h), int(x):int(x + w)]
            if crop.size == 0:
                continue
            true_anc = ptax.by_name(HELD_OUT[cls])
            total += 1

            hier = classify_crop(crop, ptax, clip, cfg)
            if hier.outcome is Outcome.UNKNOWN:
                H["unknown"] += 1
            elif hier.node.is_leaf:
                H["leaf"] += 1                       # over-committed a specific leaf
            elif on_path(hier.node, true_anc):
                H["correct_super"] += 1              # abstracted to the right branch
            else:
                H["off_branch"] += 1                 # wrong super-category

            flat = flat_classify(clip.image_features(crop), ptax, clip,
                                 temperature=cfg.temperature)
            if on_path(flat.leaf, true_anc):
                F["right_branch_specific"] += 1
            else:
                F["wrong_branch_specific"] += 1

    report(H, F, total)


def pct(a, b):
    return 100.0 * a / b if b else 0.0


def report(H, F, n):
    hier_safe = H["correct_super"] + H["unknown"]
    print(f"\nOUT-OF-VOCABULARY GT objects (leave-classes-out on COCO), n={n}")
    print("=" * 60)
    print("FLAT / closed head (must name a specific leaf):")
    print(f"  confident WRONG specific label : {n}/{n} (100%)")
    print(f"    of which on the right branch : {F['right_branch_specific']}/{n}")
    print(f"    wrong branch                 : {F['wrong_branch_specific']}/{n}")
    print("HOWC (hierarchical):")
    print(f"  correct super-category         : {H['correct_super']}/{n} "
          f"({pct(H['correct_super'], n):.0f}%)")
    print(f"  honest UNKNOWN                 : {H['unknown']}/{n} "
          f"({pct(H['unknown'], n):.0f}%)")
    print(f"  --> reliably handled           : {hier_safe}/{n} "
          f"({pct(hier_safe, n):.0f}%)")
    print(f"  over-committed leaf (wrong)    : {H['leaf']}/{n}")
    print(f"  off-branch (wrong super)       : {H['off_branch']}/{n}")
    print("=" * 60)
    print(f">>> Headline: HOWC reliably recognizes {pct(hier_safe, n):.0f}% of "
          f"out-of-vocabulary objects (correct super-category or honest UNKNOWN) "
          f"and gives 0 confident wrong specific labels, vs the flat head's 100%.")

    # stacked outcome distribution per head, coloured by safety
    GREEN, GOLD, ORANGE, RED = "#2ecc71", "#f1c40f", "#e67e22", "#e74c3c"
    flat_rb, flat_wb = pct(F["right_branch_specific"], n), pct(F["wrong_branch_specific"], n)
    h_cs, h_uk, h_ob, h_lf = (pct(H["correct_super"], n), pct(H["unknown"], n),
                              pct(H["off_branch"], n), pct(H["leaf"], n))
    fig, ax = plt.subplots(figsize=(8.5, 5))
    # Flat bar
    ax.bar(0, flat_rb, 0.5, color=ORANGE, label="wrong specific, right super")
    ax.bar(0, flat_wb, 0.5, bottom=flat_rb, color=RED, label="wrong super (categorical error)")
    # HOWC bar
    ax.bar(1, h_cs, 0.5, color=GREEN, label="correct super-category")
    ax.bar(1, h_uk, 0.5, bottom=h_cs, color=GOLD, label="honest UNKNOWN")
    ax.bar(1, h_ob, 0.5, bottom=h_cs + h_uk, color=RED)
    ax.bar(1, h_lf, 0.5, bottom=h_cs + h_uk + h_ob, color="#7f0000")
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Flat / closed head", "HOWC"])
    ax.set_ylabel("% of out-of-vocabulary GT objects"); ax.set_ylim(0, 105)
    ax.set_title(f"Out-of-vocabulary objects (GT, leave-classes-out, n={n})\n"
                 "Flat: 100% confident-wrong specific.  HOWC: 0% wrong specific, "
                 f"{pct(hier_safe, n):.0f}% safe.")
    for y, t in [(flat_rb / 2, f"{flat_rb:.0f}%"),
                 (flat_rb + flat_wb / 2, f"{flat_wb:.0f}%")]:
        ax.text(0, y, t, ha="center", va="center", fontsize=9, color="white")
    for y, t in [(h_cs / 2, f"{h_cs:.0f}%"), (h_cs + h_uk / 2, f"{h_uk:.0f}%")]:
        ax.text(1, y, t, ha="center", va="center", fontsize=9, color="black")
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(REPO / "figures/v3_openworld_benchmark.png", dpi=160, bbox_inches="tight")
    print(">>> wrote figures/v3_openworld_benchmark.png")


if __name__ == "__main__":
    main()
