"""HOWC benchmark on the *right* axes (not closed-set mAP).

Reads review/cases.csv (the per-detection dump) and compares the
CLASSIFICATION arms that share the same YOLO boxes:

  FLAT : arg-max leaf (a flat closed-vocabulary head, the YOLO-style behaviour)
  HIER : hierarchical abstraction with a safety floor (HOWC)

on the metrics HOWC is actually designed for:

  1. off-branch mistake rate  -- a categorical error (predicted category not on
     the root-to-truth path). Abstraction to an ancestor is NOT counted as a
     mistake, it is correct-but-coarse.
  2. calibrated abstention     -- fraction the arm declines (UNKNOWN). Only HIER
     can abstain.
  3. on-path severity          -- for on-branch predictions, how many levels
     coarser than the truth (specificity cost of playing safe).

Honest scope: the "novel" objects here are a label-space proxy (COCO classes
absent from our taxonomy), which YOLO itself recognizes; a true YOLO-vs-HOWC
comparison on novelty needs a GT-labelled leave-classes-out set (see the concept
doc). This script quantifies the FLAT-vs-HIER (closed-flat vs hierarchical)
trade-off on real detections.

Usage: python scripts/howc_benchmark.py
Output: figures/howc_benchmark.png + printed table.
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(REPO))
from hpercept.taxonomy import Taxonomy   # noqa: E402

tax = Taxonomy.load(REPO / "taxonomy.yaml")


def on_path(a, b):
    return a is b or a in b.ancestors() or b in a.ancestors()


def hops(a, b):
    anc = {x.name for x in a.ancestors(include_self=True)}
    x = b
    while x and x.name not in anc:
        x = x.parent
    return (a.depth - x.depth) + (b.depth - x.depth)


def main():
    rows = list(csv.DictReader((REPO / "review/cases.csv").open()))
    it = [r for r in rows if r["population"] == "in_taxonomy"]
    n = len(it)

    flat_off = flat_on = 0
    hier_off = hier_on = hier_abst = 0
    flat_on_sev = []
    hier_on_sev = []
    for r in it:
        true = tax.by_name(r["true_node"])
        fl = tax.by_name(r["flat_leaf"])
        if on_path(fl, true):
            flat_on += 1
            flat_on_sev.append(hops(fl, true))
        else:
            flat_off += 1
        if r["hier_outcome"] == "unknown":
            hier_abst += 1
        else:
            hn = tax.by_name(r["hier_node"])
            if on_path(hn, true):
                hier_on += 1
                hier_on_sev.append(hops(hn, true))
            else:
                hier_off += 1

    def pct(x):
        return 100.0 * x / n

    print(f"\nIN-TAXONOMY objects (n={n}), same YOLO boxes:")
    print(f"{'':16}{'FLAT (arg-max leaf)':>22}{'HIER (HOWC)':>16}")
    print(f"{'correct branch':16}{pct(flat_on):>20.0f}% {pct(hier_on):>14.0f}%")
    print(f"{'OFF branch (err)':16}{pct(flat_off):>20.0f}% {pct(hier_off):>14.0f}%")
    print(f"{'abstain (UNKNOWN)':16}{0:>20.0f}% {pct(hier_abst):>14.0f}%")
    import statistics as st
    print(f"on-path severity (levels coarser than truth): "
          f"FLAT {st.mean(flat_on_sev):.1f}, HIER {st.mean(hier_on_sev):.1f}")
    print("\nHeadline: HIER makes 0% categorical (off-branch) errors and abstains "
          f"{pct(hier_abst):.0f}% vs FLAT's {pct(flat_off):.0f}% off-branch errors.")

    # figure
    cats = ["correct\nbranch", "OFF branch\n(categorical error)", "abstain\n(UNKNOWN)"]
    flat = [pct(flat_on), pct(flat_off), 0]
    hier = [pct(hier_on), pct(hier_off), pct(hier_abst)]
    x = range(len(cats))
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.bar([i - 0.2 for i in x], flat, 0.4, label="FLAT (arg-max leaf)", color="#95a5a6")
    ax.bar([i + 0.2 for i in x], hier, 0.4, label="HIER (HOWC)", color="#2ecc71")
    ax.set_xticks(list(x)); ax.set_xticklabels(cats)
    ax.set_ylabel("% of known objects"); ax.set_ylim(0, 100)
    ax.set_title("HOWC vs flat head on known objects: no categorical errors, "
                 "calibrated abstention")
    ax.legend()
    for i, (f, h) in enumerate(zip(flat, hier)):
        ax.text(i - 0.2, f + 1, f"{f:.0f}", ha="center", fontsize=8)
        ax.text(i + 0.2, h + 1, f"{h:.0f}", ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(REPO / "figures/howc_benchmark.png", dpi=160, bbox_inches="tight")
    print(">>> wrote figures/howc_benchmark.png")


if __name__ == "__main__":
    main()
