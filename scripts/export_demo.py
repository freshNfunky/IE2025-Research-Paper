"""Export a static, self-contained interactive demo of the perception pipeline.

Runs the full two-path system (YOLO+CLIP hierarchical abstraction + CLIPSeg
cross-validation) on a handful of curated road scenes and writes, under
``demo/data/``:

  * scene_NN.jpg        -- the original frame (downscaled for the web),
  * scene_NN_seg.jpg    -- the dense segmentation overlay,
  * scenes.json         -- every detection with its taxonomy descent (per-node
                           probability mass), constraint result and segmentation
                           cross-check verdict, plus legends.

The companion ``demo/index.html`` reads only these static files, so the demo
drops onto any static/PHP web space (no Python at serve time) -- the same way a
krpano tour does.

Usage:
    python scripts/export_demo.py [source_id] [n_images] [max_scenes]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hpercept import datasets                                   # noqa: E402
from hpercept.abstraction import AbstractionConfig, flat_classify  # noqa: E402
from hpercept.pipeline import get_pipeline                     # noqa: E402
from hpercept.viz import COLORS, REJECTED_COLOR, segmentation_overlay  # noqa: E402

OUT = REPO / "demo" / "data"
MAX_W = 900          # downscale wide frames for the web


def _rgb(t):
    return "#%02x%02x%02x" % (int(t[0]), int(t[1]), int(t[2]))


OUTCOME_HEX = {k.value: _rgb(v) for k, v in COLORS.items()}
OUTCOME_HEX["rejected"] = _rgb(REJECTED_COLOR)


def _save_jpg(arr: np.ndarray, path: Path, scale: float) -> tuple[int, int]:
    im = Image.fromarray(arr)
    if scale != 1.0:
        im = im.resize((int(im.width * scale), int(im.height * scale)),
                       Image.LANCZOS)
    im.save(path, quality=88)
    return im.width, im.height


def tax_tree(node) -> dict:
    """Nested taxonomy structure for the demo's tree view (name/floor/children)."""
    return {"name": node.name, "floor": bool(node.floor),
            "children": [tax_tree(c) for c in node.children]}


def detection_dict(p, scale: float, pipe, cfg) -> dict:
    c = p.classification
    x1, y1, x2, y2 = p.box.xyxy
    path = [{"name": n.name, "mass": round(c.node_mass.get(n.name, 0.0), 3),
             "floor": bool(n.floor)} for n in c.path]
    # Per-node probability mass (non-zero only) so the tree view can show how the
    # descent distributed mass, like the paper's decision-path bars.
    node_mass = {k: round(v, 3) for k, v in c.node_mass.items() if v >= 0.005}

    return {
        "box": [round(x1 * scale), round(y1 * scale),
                round(x2 * scale), round(y2 * scale)],
        "label": c.label,
        "outcome": c.outcome.value,
        "confidence": round(c.confidence, 2),
        "importance": round(p.importance, 2),
        "yolo": p.box.coco_name,
        "yolo_conf": round(p.box.coco_conf, 2),
        "novel": pipe.taxonomy.by_coco(p.box.coco_name) is None,
        "rejected": bool(p.rejected),
        "constraints": p.constraints.summary,
        "seg_status": p.seg.status if p.seg else "off",
        "seg_note": p.seg.note if p.seg else "",
        "path": path,
        "node_mass": node_mass,
    }


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "road_anomaly"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    max_scenes = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    OUT.mkdir(parents=True, exist_ok=True)

    pipe = get_pipeline()
    cfg = AbstractionConfig()
    print(f">>> streaming {n} images from '{src}'", flush=True)
    samples = datasets.get_source(src).load(n)

    scenes = []
    for s in samples:
        if len(scenes) >= max_scenes:
            break
        scene = pipe.run(s.image, mode="clip", segment=True, cfg=cfg)
        if not scene.predictions:
            continue
        idx = len(scenes)
        sid = f"scene_{idx:02d}"
        h, w = s.image.shape[:2]
        scale = min(1.0, MAX_W / float(w))
        ow, oh = _save_jpg(s.image, OUT / f"{sid}.jpg", scale)
        if scene.seg_result is not None:
            overlay = segmentation_overlay(s.image, scene.seg_result, alpha=0.55)
            _save_jpg(overlay, OUT / f"{sid}_seg.jpg", scale)
        dets = []
        for p in scene.predictions:
            d = detection_dict(p, scale, pipe, cfg)
            # Flat baseline on the same CLIP features (arg-max leaf + reject option).
            feat = pipe.clip.image_features(p.box.crop(s.image))
            flat = flat_classify(feat, pipe.taxonomy, pipe.clip,
                                 temperature=cfg.temperature, reject_threshold=0.5)
            d["flat"] = {"leaf": flat.leaf.name, "prob": round(flat.prob, 2),
                         "accepted": bool(flat.accepted)}
            dets.append(d)
        scenes.append({
            "id": sid,
            "image": f"data/{sid}.jpg",
            "seg": f"data/{sid}_seg.jpg",
            "width": ow, "height": oh,
            "caption": s.caption or sid,
            "detections": dets,
        })
        c = scene.counts()
        print(f"    {sid}: {len(dets)} detections {c}", flush=True)

    seg_classes = pipe.segmenter.classes
    data = {
        "outcome_colors": OUTCOME_HEX,
        "seg_marks": {"confirm": "✓", "neutral": "∼",
                      "flag": "⚠", "conflict": "✗", "off": ""},
        "seg_legend": [{"name": c.name, "color": _rgb(c.color)} for c in seg_classes],
        "taxonomy": tax_tree(pipe.taxonomy.root),
        "scenes": scenes,
    }
    (OUT / "scenes.json").write_text(json.dumps(data, indent=1))
    print(f">>> wrote {OUT/'scenes.json'} with {len(scenes)} scenes", flush=True)


if __name__ == "__main__":
    main()
