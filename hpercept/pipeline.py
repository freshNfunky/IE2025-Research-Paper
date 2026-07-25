"""End-to-end perception pipeline.

    image --> [YOLO boxes] --> for each box:
                 mode == "clip"  : hierarchical CLIP descent (open-vocabulary)
                 mode == "yolo"  : COCO->taxonomy + confidence abstraction
              --> context-constraint validation
              --> annotated result + structured records
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

import numpy as np

from .abstraction import (
    AbstractionConfig,
    Classification,
    Outcome,
    classify_by_coco,
    classify_crop,
)
from .classifier import ClipClassifier
from .constraints import ConstraintResult, validate
from .detector import Box, get_detector
from .taxonomy import Taxonomy

Mode = Literal["clip", "yolo"]

_TAXONOMY_PATH = Path(__file__).resolve().parent.parent / "taxonomy.yaml"


@dataclass
class Prediction:
    box: Box
    classification: Classification
    constraints: ConstraintResult

    @property
    def rejected(self) -> bool:
        return not self.constraints.ok

    def to_dict(self) -> dict:
        c = self.classification
        return {
            "label": c.label,
            "outcome": c.outcome.value,
            "confidence": c.confidence,
            "yolo_class": self.box.coco_name,
            "yolo_conf": round(self.box.coco_conf, 3),
            "path": " > ".join(n.name for n in c.path),
            "box": list(self.box.xyxy),
            "constraints": self.constraints.summary,
            "rejected": self.rejected,
        }


@dataclass
class SceneResult:
    predictions: list[Prediction] = field(default_factory=list)
    image_shape: tuple[int, int] = (0, 0)  # (h, w)

    def counts(self) -> dict[str, int]:
        c = {"identified": 0, "abstracted": 0, "unknown": 0, "rejected": 0}
        for p in self.predictions:
            c[p.classification.outcome.value] += 1
            if p.rejected:
                c["rejected"] += 1
        return c


class Pipeline:
    def __init__(
        self,
        taxonomy: Optional[Taxonomy] = None,
        weights: str = "yolov8n.pt",
        clip_model: str = "ViT-B-32",
        clip_pretrained: str = "openai",
    ) -> None:
        self.taxonomy = taxonomy or Taxonomy.load(_TAXONOMY_PATH)
        self.weights = weights
        self._clip: Optional[ClipClassifier] = None
        self._clip_cfg = (clip_model, clip_pretrained)

    @property
    def clip(self) -> ClipClassifier:
        if self._clip is None:
            model, pretrained = self._clip_cfg
            self._clip = ClipClassifier(self.taxonomy, model, pretrained)
        return self._clip

    def run(
        self,
        image_rgb: np.ndarray,
        mode: Mode = "clip",
        det_conf: float = 0.25,
        cfg: Optional[AbstractionConfig] = None,
    ) -> SceneResult:
        cfg = cfg or AbstractionConfig()
        h, w = image_rgb.shape[:2]
        detector = get_detector(self.weights, det_conf)
        boxes = detector.detect(image_rgb, conf=det_conf)

        preds: list[Prediction] = []
        for box in boxes:
            if mode == "clip":
                crop = box.crop(image_rgb)
                cls = classify_crop(crop, self.taxonomy, self.clip, cfg)
            else:
                cls = classify_by_coco(
                    box.coco_name, box.coco_conf, self.taxonomy,
                    leaf_threshold=cfg.descend_threshold,
                )
            cons = validate(box, cls.node, w, h)
            preds.append(Prediction(box=box, classification=cls, constraints=cons))

        return SceneResult(predictions=preds, image_shape=(h, w))


@lru_cache(maxsize=1)
def get_pipeline(weights: str = "yolov8n.pt") -> Pipeline:
    """Process-wide singleton so models load once."""
    return Pipeline(weights=weights)
