"""Spike A2: class-agnostic region proposals (MobileSAM) for "YOLO+".

The closed-set detector only proposes boxes for classes it was trained on, so a
genuinely untrained object may never be boxed. MobileSAM segments *everything*,
appearance- and class-agnostic, giving candidate regions regardless of class.
Feeding those regions into the hierarchical taxonomic classifier is the "YOLO+"
idea: propose open-world, then label by abstraction, so unknown / untrained
objects still receive a safe, coarse category or an explicit UNKNOWN.

MobileSAM is loaded via ultralytics (already a dependency; weights ~40 MB, fetched
from the ultralytics/HF assets on first use), which keeps the whole thing
HuggingFace-publishable with no extra heavy install.
"""
from __future__ import annotations

import numpy as np

from ..detector import Box


def iou(a: Box, b: Box) -> float:
    ax1, ay1, ax2, ay2 = a.xyxy
    bx1, by1, bx2, by2 = b.xyxy
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
    inter = iw * ih
    ua = (ax2 - ax1) * (ay2 - ay1) + (bx2 - bx1) * (by2 - by1) - inter
    return inter / ua if ua > 0 else 0.0


class SamProposer:
    """Lazy MobileSAM everything-mode proposer -> class-agnostic candidate boxes."""

    def __init__(self, weights: str = "mobile_sam.pt") -> None:
        self.weights = weights
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from ultralytics import SAM
            self._model = SAM(self.weights)
        return self._model

    def proposals(self, image_rgb: np.ndarray, min_area_frac: float = 0.004,
                  max_area_frac: float = 0.5, min_side: int = 24) -> list[Box]:
        """Return plausible object-sized regions (background stuff filtered out)."""
        h, w = image_rgb.shape[:2]
        res = self.model.predict(image_rgb, verbose=False)[0]
        if res.masks is None:
            return []
        boxes: list[Box] = []
        for m in res.masks.data.cpu().numpy():
            ys, xs = np.where(m > 0.5)
            if xs.size == 0:
                continue
            x1, y1, x2, y2 = int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())
            bw, bh = x2 - x1, y2 - y1
            frac = (bw * bh) / float(w * h)
            if not (min_area_frac <= frac <= max_area_frac):
                continue          # drop tiny specks and whole-scene stuff (sky/road)
            if min(bw, bh) < min_side:
                continue
            boxes.append(Box(x1, y1, x2, y2, "region", float(m.mean())))
        return boxes

    def novel_regions(self, image_rgb: np.ndarray, yolo_boxes: list[Box],
                      iou_thresh: float = 0.5) -> list[Box]:
        """SAM proposals not already covered by a YOLO detection (deduped)."""
        out: list[Box] = []
        for p in self.proposals(image_rgb):
            if any(iou(p, y) >= iou_thresh for y in yolo_boxes):
                continue
            if any(iou(p, o) >= 0.7 for o in out):
                continue
            out.append(p)
        return out
