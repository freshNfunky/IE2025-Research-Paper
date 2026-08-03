"""Spike B: evaluate an out-of-ODD (OOD) reject via negative prompts.

For each detection we compute
    ood_margin = best_taxonomy_leaf_cosine - best_negative_prompt_cosine
and ask whether flagging UNKNOWN when ood_margin < t would convert the
implausible abstractions (airplane/kite/frisbee -> Living Being) into UNKNOWN
without breaking the good cases. Ground truth = the `plausible` logic from
dump_cases. No model or config is changed here; this only measures separation.

Usage: python scripts/ood_spike.py [n_images]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(Path(__file__).resolve().parent))  # import dump_cases

from hpercept import datasets                              # noqa: E402
from hpercept.abstraction import AbstractionConfig, classify_crop  # noqa: E402
from hpercept.detector import get_detector                 # noqa: E402
from hpercept.pipeline import get_pipeline                 # noqa: E402
import dump_cases                                          # noqa: E402


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    pipe = get_pipeline()
    tax, clip = pipe.taxonomy, pipe.clip
    cfg = AbstractionConfig()
    det = get_detector(pipe.weights, 0.20)

    print(f">>> streaming {n} images", flush=True)
    samples = datasets.get_source("road_anomaly").load(n)

    recs = []  # (population, plausible, outcome, ood_margin, yolo, neg_label)
    for s in samples:
        h, w = s.image.shape[:2]
        for box in det.detect(s.image, conf=0.20):
            crop = box.crop(s.image)
            feat = clip.image_features(crop)
            hier = classify_crop(crop, tax, clip, cfg, image_feat=feat)
            max_neg, neg_label = clip.negatives_max_sim(feat)
            true_node = tax.by_coco(box.coco_name)
            pop = "out_of_taxonomy" if true_node is None else "in_taxonomy"
            below = tax.is_below_floor(hier.node)
            plaus = dump_cases.is_plausible(pop, hier.outcome.value, hier.node,
                                            true_node, below, box.coco_name)
            recs.append((pop, plaus, hier.outcome.value,
                         round(hier.top_sim - max_neg, 4), box.coco_name, neg_label))

    # --- separation report ------------------------------------------------ #
    def margins(pred):
        return sorted(r[3] for r in recs if pred(r))

    oot_impl = margins(lambda r: r[0] == "out_of_taxonomy" and not r[1])
    oot_plaus = margins(lambda r: r[0] == "out_of_taxonomy" and r[1])
    known_good = margins(lambda r: r[0] == "in_taxonomy" and r[1]
                         and r[2] != "unknown")

    def stats(name, xs):
        if not xs:
            print(f"  {name:<28} n=0"); return
        a = np.array(xs)
        print(f"  {name:<28} n={len(xs):2d}  min={a.min():+.3f} "
              f"med={np.median(a):+.3f} max={a.max():+.3f}")

    print("\n=== ood_margin (leaf_cosine - best_negative) by group ===")
    stats("out_of_tax IMPLAUSIBLE", oot_impl)
    stats("out_of_tax plausible", oot_plaus)
    stats("in_tax good (committed)", known_good)

    print("\n=== threshold sweep: flag UNKNOWN if ood_margin < t ===")
    print("   t     implausible_caught   collateral(good_broken)")
    impl = [r for r in recs if r[0] == "out_of_taxonomy" and not r[1]]
    good = [r for r in recs if (r[0] == "in_taxonomy" and r[1] and r[2] != "unknown")
            or (r[0] == "out_of_taxonomy" and r[1] and r[2] != "unknown")]
    for t in [-0.02, 0.0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.12]:
        caught = sum(1 for r in impl if r[3] < t)
        broken = sum(1 for r in good if r[3] < t)
        print(f"  {t:+.2f}      {caught:2d}/{len(impl)}                {broken:2d}/{len(good)}")

    print("\n=== the implausible cases and their margins ===")
    for r in recs:
        if r[0] == "out_of_taxonomy" and not r[1]:
            print(f"  {r[4]:<12} outcome={r[2]:<10} margin={r[3]:+.3f} "
                  f"(best_neg='{r[5]}')")


if __name__ == "__main__":
    main()
