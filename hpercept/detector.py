"""YOLO detector wrapper.

Produces class-agnostic-ish bounding boxes plus the raw COCO class YOLO thinks
each box is. Downstream, the taxonomy/CLIP stage decides the *hierarchical*
label; YOLO here is only responsible for "there is an object, here is its box".
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

import numpy as np


@dataclass
class Box:
    """Axis-aligned box in pixel coordinates plus YOLO's own guess."""

    x1: float
    y1: float
    x2: float
    y2: float
    coco_name: str          # YOLO's COCO label (e.g. "car")
    coco_conf: float        # YOLO's confidence for that label

    @property
    def xyxy(self) -> tuple[int, int, int, int]:
        return int(self.x1), int(self.y1), int(self.x2), int(self.y2)

    def area_frac(self, img_w: int, img_h: int) -> float:
        w = max(0.0, self.x2 - self.x1)
        h = max(0.0, self.y2 - self.y1)
        return (w * h) / float(max(1, img_w * img_h))

    def crop(self, image: np.ndarray, pad: float = 0.06) -> np.ndarray:
        """Return the (slightly padded) image region for this box."""
        h, w = image.shape[:2]
        pw, ph = (self.x2 - self.x1) * pad, (self.y2 - self.y1) * pad
        x1 = int(max(0, self.x1 - pw))
        y1 = int(max(0, self.y1 - ph))
        x2 = int(min(w, self.x2 + pw))
        y2 = int(min(h, self.y2 + ph))
        return image[y1:y2, x1:x2]


class Detector:
    """Thin wrapper around Ultralytics YOLO with lazy model loading."""

    def __init__(self, weights: str = "yolov8n.pt", conf: float = 0.25) -> None:
        self.weights = weights
        self.conf = conf
        self._model = None

    @property
    def model(self):
        if self._model is None:
            # Imported lazily so the app can start (and YOLO-only-less modes can
            # run) without paying the import cost until detection is needed.
            from ultralytics import YOLO

            self._model = YOLO(self.weights)
        return self._model

    def detect(self, image: np.ndarray, conf: Optional[float] = None) -> list[Box]:
        """Run detection on an RGB image and return boxes.

        We use class-agnostic NMS so that a novel object which weakly activates
        several COCO heads still yields a single box (recall matters more than
        the COCO label here -- the taxonomy decides the real category). A low
        confidence keeps recall on out-of-distribution objects that no COCO
        class fits well; the safety floor and constraints filter the noise."""
        results = self.model.predict(
            image, conf=conf if conf is not None else self.conf,
            iou=0.5, agnostic_nms=True, verbose=False,
        )
        names = self.model.names
        boxes: list[Box] = []
        for res in results:
            for b in res.boxes:
                x1, y1, x2, y2 = b.xyxy[0].tolist()
                cls_id = int(b.cls[0].item())
                boxes.append(
                    Box(
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2,
                        coco_name=names.get(cls_id, str(cls_id)),
                        coco_conf=float(b.conf[0].item()),
                    )
                )
        return boxes


@lru_cache(maxsize=2)
def get_detector(weights: str = "yolov8s.pt", conf: float = 0.20) -> Detector:
    """Cached detector so the model is loaded at most once per weights file.

    Default is YOLOv8s (not the nano model): its higher recall is what lets the
    prominent, safety-critical novel objects (an atypical tractor, an overloaded
    truck) get a box at all. Missing a large object is the worst failure."""
    return Detector(weights=weights, conf=conf)
