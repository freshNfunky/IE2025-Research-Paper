"""Dump the per-detection breakdown behind the benchmark, for the record.

Mirrors scripts/benchmark.py exactly (same detector, boxes, CLIP, thresholds)
but writes one CSV row per detection instead of only the aggregates. Used as the
supplementary evidence table requested in the review exchange.

Note on terminology: what the benchmark calls "novel" is a PROXY, namely a
detection whose YOLO/COCO class has no node in our taxonomy (giraffe, airplane).
The detector already recognizes those objects; they are out-of-taxonomy for our
label set, not open-world novelties. The column is named `population` with values
`out_of_taxonomy` / `in_taxonomy` to avoid overclaiming.

Usage: python scripts/dump_cases.py [n_images] [reject_tau]
Output: review/cases.csv
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hpercept import datasets                                    # noqa: E402
from hpercept.abstraction import (                               # noqa: E402
    AbstractionConfig, Outcome, classify_crop, flat_classify)
from hpercept.detector import get_detector                       # noqa: E402
from hpercept.pipeline import get_pipeline, importance_of        # noqa: E402
from hpercept.taxonomy import Node                               # noqa: E402

OUT = REPO / "review"
OUT.mkdir(parents=True, exist_ok=True)


def on_same_path(a: Node, b: Node) -> bool:
    return a is b or a in b.ancestors() or b in a.ancestors()


# Expected coarse category (safety floor) for out-of-taxonomy COCO classes, used
# only for a semantic-plausibility check. None = no clean coarse category exists
# in our taxonomy (an out-of-ODD object such as a kite or a tie), so abstracting
# it to a specific branch is a semantic overreach; only an UNKNOWN flag is
# plausible there.
EXPECTED_FLOOR = {
    "giraffe": "Living Being", "zebra": "Living Being", "elephant": "Living Being",
    "bear": "Living Being",
    "airplane": "Vehicle", "boat": "Vehicle",
    # umbrella, kite, snowboard, tie, frisbee, sports ball, ... -> None (no fit)
}


def is_plausible(population, outcome, node, true_node, below_floor, coco):
    """Is the reported category semantically plausible (not just 'not-a-leaf')?"""
    if outcome == "unknown":
        return True                       # an honest flag is never a wrong claim
    if population == "in_taxonomy":
        return bool(below_floor and on_same_path(node, true_node))
    exp = EXPECTED_FLOOR.get(coco)         # out-of-taxonomy, abstracted / identified
    if exp is None:
        return False                       # no correct coarse branch -> overreach
    return exp in {a.name for a in node.ancestors(include_self=True)}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    tau = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5

    pipe = get_pipeline()
    tax, clip = pipe.taxonomy, pipe.clip
    cfg = AbstractionConfig()
    detector = get_detector(pipe.weights, 0.20)

    print(f">>> streaming {n} Road Anomaly images", flush=True)
    samples = datasets.get_source("road_anomaly").load(n)

    rows = []
    n_out = n_in = 0
    for si, s in enumerate(samples):
        h, w = s.image.shape[:2]
        for di, box in enumerate(detector.detect(s.image, conf=0.20)):
            crop = box.crop(s.image)
            feat = clip.image_features(crop)
            imp = importance_of(box, w, h)
            flat = flat_classify(feat, tax, clip, temperature=cfg.temperature,
                                 reject_threshold=tau)
            hier = classify_crop(crop, tax, clip, cfg, image_feat=feat)
            true_node = tax.by_coco(box.coco_name)

            floor = hier.node.nearest_floor()
            below_floor = tax.is_below_floor(hier.node)
            if true_node is None:            # out-of-taxonomy (proxy novelty)
                population = "out_of_taxonomy"
                verdict = ("safe" if hier.outcome in (Outcome.ABSTRACTED, Outcome.UNKNOWN)
                           else "UNSAFE_wrong_leaf")
                n_out += 1
            else:                            # in-taxonomy (known)
                population = "in_taxonomy"
                if hier.outcome is Outcome.UNKNOWN:
                    verdict = "unknown"
                elif below_floor and on_same_path(hier.node, true_node):
                    verdict = "useful"
                else:
                    verdict = "wrong_branch"
                n_in += 1

            x1, y1, x2, y2 = box.xyxy
            rows.append({
                "image": si, "det": di,
                "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                "area_frac": round(box.area_frac(w, h), 4),
                "importance": round(imp, 3),
                "yolo_class": box.coco_name, "yolo_conf": round(box.coco_conf, 3),
                "population": population,
                "true_node": true_node.name if true_node else "",
                "hier_outcome": hier.outcome.value,
                "hier_node": hier.node.name,
                "hier_confidence": hier.confidence,
                "top_leaf_cosine": hier.top_sim,
                "nearest_floor": floor.name if floor else "",
                "below_floor": below_floor,
                "flat_leaf": flat.leaf.name,
                "flat_prob": flat.prob,
                "flat_leaf_cosine": flat.sim,
                "flat_accepted": flat.accepted,
                "kpi_verdict": verdict,
                "plausible": is_plausible(population, hier.outcome.value, hier.node,
                                          true_node, below_floor, box.coco_name),
            })
        print(f"    [{si+1}/{len(samples)}] out_of_taxonomy={n_out} in_taxonomy={n_in}",
              flush=True)

    path = OUT / "cases.csv"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # sanity aggregate
    safe = sum(1 for r in rows if r["population"] == "out_of_taxonomy"
               and r["kpi_verdict"] == "safe")
    useful = sum(1 for r in rows if r["population"] == "in_taxonomy"
                 and r["kpi_verdict"] == "useful")
    oot_plaus = sum(1 for r in rows if r["population"] == "out_of_taxonomy" and r["plausible"])
    print(f"\n>>> wrote {path} ({len(rows)} rows)", flush=True)
    print(f">>> out_of_taxonomy safe-handled: {safe}/{n_out} "
          f"(of which plausibly abstracted/flagged: {oot_plaus}/{n_out})", flush=True)
    print(f">>> in_taxonomy useful: {useful}/{n_in}", flush=True)


if __name__ == "__main__":
    main()
