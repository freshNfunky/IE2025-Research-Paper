"""Figures for the second perception path: semantic-segmentation cross-validation.

Produces, over a sample of road scenes run with ``segment=True``:

  * figures/segmentation_qualitative.png -- per scene, three panels:
        [ annotated boxes (+ ✓/✗ seg marker) | dense segmentation overlay |
          agreement notes ]
    so the reader can see the two independent perception paths side by side and
    how they (dis)agree per detection.

  * figures/segmentation_agreement.png -- summary charts across all detections:
        (a) how often the segmentation path independently CORROBORATES a box
            detection (confirm / neutral / conflict),
        (b) the corroboration rate broken down by box-path outcome
            (identified / abstracted / unknown), i.e. does the second path also
            back up the *novel* objects the hierarchy abstracted?

  * figures/segmentation.json -- the raw numbers.

Usage:
    python scripts/segmentation_demo.py [source_id] [n_images]
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch, Rectangle

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hpercept import datasets                                   # noqa: E402
from hpercept.abstraction import Outcome                        # noqa: E402
from hpercept.pipeline import get_pipeline                      # noqa: E402
from hpercept.viz import segmentation_overlay                   # noqa: E402

OUT = REPO / "figures"
OUT.mkdir(exist_ok=True)

SEG_COLOR = {"confirm": "#2ecc71", "neutral": "#95a5a6", "flag": "#f39c12",
             "conflict": "#e74c3c"}
SEG_MARK = {"confirm": "✓", "neutral": "~", "flag": "⚠", "conflict": "✗"}
SEG_STATES = ("confirm", "neutral", "flag", "conflict")
OUTCOME_COLOR = {
    Outcome.IDENTIFIED: "#2ecc71",
    Outcome.ABSTRACTED: "#f39c12",
    Outcome.UNKNOWN: "#e74c3c",
}


def _box_color(pred) -> str:
    if pred.seg is not None:
        return SEG_COLOR[pred.seg.status]
    return "#3498db"


# --------------------------------------------------------------------------- #
#  Qualitative: boxes | segmentation overlay | notes                          #
# --------------------------------------------------------------------------- #
def draw_scene(fig, gs_row, image, scene):
    axb = fig.add_subplot(gs_row[0])
    axs = fig.add_subplot(gs_row[1])

    # Panel 1: image + boxes coloured by segmentation verdict. The verdict mark
    # (✓/~/⚠/✗) and the branch note ride on the box itself, so we need no third
    # text column -- keeping the figure compact enough to sit inline with text.
    axb.imshow(image)
    axb.axis("off")
    axb.set_title("Box path (colour = seg verdict)", fontsize=9, loc="left")
    for i, p in enumerate(scene.predictions):
        x1, y1, x2, y2 = p.box.xyxy
        c = _box_color(p)
        axb.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                                edgecolor=c, linewidth=2.4))
        mark = SEG_MARK.get(p.seg.status, "") if p.seg else ""
        axb.text(x1, max(0, y1 - 4), f"{p.classification.label} {mark}",
                 fontsize=7.5, color="white", va="bottom", ha="left",
                 bbox=dict(boxstyle="round,pad=0.2", fc=c, ec="none"))

    # Panel 2: the dense segmentation overlay (the 2nd, independent path).
    if scene.seg_result is not None:
        axs.imshow(segmentation_overlay(image, scene.seg_result, alpha=0.55))
    else:
        axs.imshow(image)
    axs.axis("off")
    axs.set_title("Segmentation path (dense pixel labels)", fontsize=9, loc="left")


def make_qualitative(scenes, out_path):
    n = len(scenes)
    # Two columns (boxes | segmentation), one row per scene. Height per row is
    # driven by each image's own aspect ratio via constrained_layout so there is
    # no wasted vertical whitespace.
    fig = plt.figure(figsize=(11, 3.0 * n), constrained_layout=True)
    gs = fig.add_gridspec(n, 2, width_ratios=[1.0, 1.0])
    for r, (image, scene) in enumerate(scenes):
        draw_scene(fig, [gs[r, 0], gs[r, 1]], image, scene)
    fig.suptitle("Two independent perception paths: YOLO+CLIP boxes vs. dense "
                 "segmentation cross-validation", fontsize=13, fontweight="bold")
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- #
#  Summary charts                                                             #
# --------------------------------------------------------------------------- #
def make_summary(stats, out_path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.6))

    # (a) overall confirm / neutral / flag / conflict.
    labels = list(SEG_STATES)
    vals = [stats["overall"][l] for l in labels]
    total = max(1, sum(vals))
    bars = ax1.bar(labels, vals, color=[SEG_COLOR[l] for l in labels])
    ax1.set_title("Segmentation cross-check verdict\n(box detections, "
                  f"n={total})", fontsize=11)
    ax1.set_ylabel("count")
    for b, v in zip(bars, vals):
        ax1.text(b.get_x() + b.get_width() / 2, v, f"{v}\n{100*v/total:.0f}%",
                 ha="center", va="bottom", fontsize=9)

    # (b) verdict mix by box-path outcome (stacked).
    outs = ["identified", "abstracted", "unknown"]
    x = np.arange(len(outs))
    bottom = np.zeros(len(outs))
    for st in SEG_STATES:
        rates = []
        for o in outs:
            d = stats["by_outcome"][o]
            t = max(1, sum(d[s] for s in SEG_STATES))
            rates.append(100 * d[st] / t)
        ax2.bar(x, rates, bottom=bottom, color=SEG_COLOR[st], label=st)
        bottom += np.array(rates)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{o}\n(n={sum(stats['by_outcome'][o][s] for s in SEG_STATES)})"
                         for o in outs])
    ax2.set_ylim(0, 100)
    ax2.set_ylabel("% of detections")
    ax2.set_title("Cross-check verdict by box-path outcome", fontsize=11)
    ax2.legend(fontsize=8, loc="lower right", ncol=2)

    fig.suptitle("Does the segmentation path back up the box path?",
                 fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(out_path, dpi=170, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- #
def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "road_anomaly"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    print(f">>> streaming {n} images from '{src}'", flush=True)
    samples = datasets.get_source(src).load(n)
    print(f">>> got {len(samples)} images; running pipeline WITH segmentation",
          flush=True)

    pipe = get_pipeline()

    overall = defaultdict(int)
    by_outcome = {o: defaultdict(int) for o in ("identified", "abstracted", "unknown")}
    seg_rejections = 0
    candidates = []   # (image, scene, verdict_set) for the qualitative grid

    for si, s in enumerate(samples):
        scene = pipe.run(s.image, mode="clip", segment=True)
        for p in scene.predictions:
            if p.seg is None:
                continue
            overall[p.seg.status] += 1
            by_outcome[p.classification.outcome.value][p.seg.status] += 1
            if p.seg.is_conflict:
                seg_rejections += 1
        if scene.predictions:
            verdicts = {p.seg.status for p in scene.predictions if p.seg}
            candidates.append((s.image, scene, verdicts))
        print(f"    [{si+1}/{len(samples)}] dets={len(scene.predictions)} "
              f"overall={dict(overall)}", flush=True)

    # Pick 3 illustrative scenes, preferring diversity: at least one that carries
    # a "flag" (paths disagree) and one pure "confirm", then fill in order.
    chosen: list[int] = []
    for want in ("flag", "confirm"):
        for idx, (_, _, v) in enumerate(candidates):
            if want in v and idx not in chosen:
                chosen.append(idx)
                break
    for idx in range(len(candidates)):
        if len(chosen) >= 3:
            break
        if idx not in chosen:
            chosen.append(idx)
    qualitative = [(candidates[i][0], candidates[i][1]) for i in chosen[:3]]

    stats = {
        "n_images": len(samples),
        "overall": {k: overall[k] for k in SEG_STATES},
        "by_outcome": {o: {k: by_outcome[o][k] for k in SEG_STATES}
                       for o in by_outcome},
        "seg_rejections": seg_rejections,
    }
    tot = max(1, sum(stats["overall"].values()))
    stats["corroboration_rate_pct"] = round(100 * stats["overall"]["confirm"] / tot, 1)

    (OUT / "segmentation.json").write_text(json.dumps(stats, indent=2))
    if qualitative:
        make_qualitative(qualitative, OUT / "segmentation_qualitative.png")
        print(">>> wrote segmentation_qualitative.png", flush=True)
    make_summary(stats, OUT / "segmentation_agreement.png")
    print(">>> wrote segmentation_agreement.png, segmentation.json", flush=True)
    print(json.dumps(stats, indent=2), flush=True)


if __name__ == "__main__":
    main()
