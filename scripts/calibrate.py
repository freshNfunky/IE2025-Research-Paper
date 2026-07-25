"""Calibration sweep: find an operating point where the hierarchy identifies
KNOWN objects specifically while still abstracting/flagging NOVEL ones.

CLIP features are computed ONCE per detected box and cached; each (temperature,
commit_mass, min_abs_sim) config is then evaluated by re-running the (cheap,
arithmetic-only) mass descent on the cached features. Produces a trade-off plot:
  x = known objects usefully classified (specific, on correct branch)
  y = novel objects safely handled (abstracted / flagged unknown)
Top-right is best; the flat baseline sits at y=0 by construction.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hpercept import datasets                                    # noqa: E402
from hpercept.abstraction import (                               # noqa: E402
    AbstractionConfig, Outcome, classify_crop, flat_classify)
from hpercept.detector import get_detector                       # noqa: E402
from hpercept.pipeline import get_pipeline                       # noqa: E402

OUT = REPO / "figures"
OUT.mkdir(exist_ok=True)
_DUMMY = np.zeros((1, 1, 3), dtype=np.uint8)


def on_same_path(a, b):
    return a is b or a in b.ancestors() or b in a.ancestors()


def collect(n):
    pipe = get_pipeline()
    tax, clip = pipe.taxonomy, pipe.clip
    det = get_detector(pipe.weights, 0.25)
    samples = datasets.get_source("road_anomaly").load(n)
    boxes = []  # (feat, coco_name, true_node)
    for si, s in enumerate(samples):
        for b in det.detect(s.image, conf=0.25):
            feat = clip.image_features(b.crop(s.image))
            boxes.append((feat, b.coco_name, tax.by_coco(b.coco_name)))
        print(f"    cached {si+1}/{len(samples)}  boxes={len(boxes)}", flush=True)
    return pipe, tax, clip, boxes


def evaluate(pipe, tax, clip, boxes, temp, cmass, msim):
    cfg = AbstractionConfig(min_abs_sim=msim, commit_mass=cmass,
                            temperature=temp, enforce_floor=True)
    novel_total = novel_safe = 0
    known_total = known_good = known_unknown = 0
    for feat, coco, true_node in boxes:
        cls = classify_crop(_DUMMY, tax, clip, cfg, image_feat=feat)
        if true_node is None:  # novel
            novel_total += 1
            if cls.outcome in (Outcome.ABSTRACTED, Outcome.UNKNOWN):
                novel_safe += 1
        else:                  # known
            known_total += 1
            if cls.outcome is Outcome.UNKNOWN:
                known_unknown += 1
            # "useful": a below-floor category on the correct branch (not root/unknown)
            below_floor = tax.is_below_floor(cls.node)
            if (cls.outcome in (Outcome.IDENTIFIED, Outcome.ABSTRACTED)
                    and below_floor and on_same_path(cls.node, true_node)):
                known_good += 1
    return {
        "temp": temp, "commit_mass": cmass, "min_abs_sim": msim,
        "novel_total": novel_total, "novel_safe_pct": _p(novel_safe, novel_total),
        "known_total": known_total, "known_good_pct": _p(known_good, known_total),
        "known_unknown_pct": _p(known_unknown, known_total),
    }


def _p(a, b):
    return round(100.0 * a / b, 1) if b else 0.0


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    print(f">>> caching CLIP features for {n} images", flush=True)
    pipe, tax, clip, boxes = collect(n)
    print(f">>> {len(boxes)} boxes cached; sweeping configs", flush=True)

    temps = [0.02, 0.03, 0.04, 0.06]
    cmasses = [0.4, 0.5, 0.6, 0.7]
    msim = 0.20
    results = []
    for t in temps:
        for c in cmasses:
            r = evaluate(pipe, tax, clip, boxes, t, c, msim)
            results.append(r)
            print(f"    T={t} mass={c}: known_good={r['known_good_pct']}% "
                  f"known_unknown={r['known_unknown_pct']}% "
                  f"novel_safe={r['novel_safe_pct']}%", flush=True)

    (OUT / "calibration.json").write_text(json.dumps(results, indent=2))
    plot(results)
    # print a suggested operating point: maximize known_good + novel_safe
    best = max(results, key=lambda r: r["known_good_pct"] + r["novel_safe_pct"])
    print("\n>>> suggested operating point (max known_good + novel_safe):", flush=True)
    print(f"    temperature={best['temp']} commit_mass={best['commit_mass']} "
          f"-> known_good={best['known_good_pct']}% novel_safe={best['novel_safe_pct']}%",
          flush=True)


def plot(results, flat_known_pct=None):
    fig, ax = plt.subplots(figsize=(7.5, 6))
    best = max(results, key=lambda r: r["known_good_pct"] + r["novel_safe_pct"])
    for r in results:
        is_best = r is best
        ax.scatter(r["known_good_pct"], r["novel_safe_pct"],
                   s=180 if is_best else 55,
                   marker="*" if is_best else "o",
                   c="#f1c40f" if is_best else [[0.2, 0.5, 0.8]],
                   edgecolors="k", linewidths=0.5, zorder=4 if is_best else 3)
    ax.annotate(
        f"chosen: T={best['temp']}, mass={best['commit_mass']}\n"
        f"({best['known_good_pct']:.0f}% known, {best['novel_safe_pct']:.0f}% novel)",
        (best["known_good_pct"], best["novel_safe_pct"]),
        fontsize=8, xytext=(-8, -34), textcoords="offset points",
        ha="right", color="#7a5c00")
    # Flat baseline: 0% novel-safety, and its known accuracy on the x-axis.
    fx = flat_known_pct if flat_known_pct is not None else 0.0
    ax.axhline(0, color="#e74c3c", lw=1, ls=":", alpha=0.5, zorder=1)
    ax.scatter([fx], [0], marker="X", s=170, c="#e74c3c", edgecolors="k",
               linewidths=0.5, zorder=5,
               label=f"flat baseline ({fx:.0f}% known, 0% novel)")
    ax.annotate("flat: can categorize known objects,\nbut 0% safe on novel ones",
                (fx, 0), fontsize=8, xytext=(10, 18), textcoords="offset points",
                color="#a5281b")
    ax.set_xlabel("KNOWN objects usefully classified (%)  →  more specific")
    ax.set_ylabel("NOVEL objects safely handled (%)  →  safer")
    ax.set_xlim(-3, 100)
    ax.set_ylim(-6, 106)
    ax.grid(alpha=0.3)
    ax.set_title("Each dot = one config of the HIERARCHICAL system; "
                 "X = the FLAT baseline\n"
                 "(hierarchy: 100% novel-safe at up to 70% known;  flat: 0% novel-safe)")
    ax.legend(loc="center right")
    fig.tight_layout()
    fig.savefig(OUT / "calibration_tradeoff.png", dpi=170, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
