"""Open-vocabulary semantic segmenter -- the second, independent perception path.

Where ``detector.py`` answers "there is an object, here is its box", this module
answers "what stuff is at every pixel?". It is deliberately a *different* model
family (CLIPSeg, not YOLO) so its output is genuine corroborating evidence for
the box path rather than a correlated echo of it. The segmentation taxonomy
lives in ``segmentation.yaml`` and, like the box taxonomy, is expressed as
open-vocabulary text prompts -- no fixed-class training required.

Loaded lazily, exactly like the detector and the CLIP classifier: importing this
module is cheap; the ~150 MB CLIPSeg weights are only pulled the first time
``segment`` is called.

Backend note: CLIPSeg is the default because it keeps the whole system
open-vocabulary and needs no dataset-specific fine-tuning. A Cityscapes-trained
closed-set model (e.g. ``nvidia/segformer-b0-finetuned-cityscapes-1024-1024``)
would give crisper masks; it could be dropped in behind the same ``SegResult``
interface without touching the rest of the pipeline.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import yaml

from .detector import Box

_SEG_TAXONOMY_PATH = Path(__file__).resolve().parent.parent / "segmentation.yaml"


@dataclass
class SegClass:
    """One entry of the segmentation taxonomy (see segmentation.yaml)."""

    name: str
    prompt: str
    role: str                       # cityscapes-style super-category
    thing: bool                     # discrete object (True) vs. background stuff
    maps_to: str                    # hpercept taxonomy node name, or "" for stuff
    color: tuple[int, int, int]

    @property
    def is_sky(self) -> bool:
        return self.role == "sky"


@dataclass
class SegResult:
    """A dense semantic segmentation of one image.

    ``label_map`` holds, per pixel, an index into ``classes``. Kept intentionally
    simple (a single argmax label per pixel) so the cross-validation logic is a
    handful of transparent array operations, matching the paper's "simple,
    inspectable rules" stance for the validation layer.
    """

    label_map: np.ndarray           # (H, W) int; index into ``classes``
    classes: list[SegClass]

    @property
    def shape(self) -> tuple[int, int]:
        return self.label_map.shape  # type: ignore[return-value]

    def class_of(self, idx: int) -> SegClass:
        return self.classes[idx]

    def _region(self, box: Box) -> np.ndarray:
        """The label sub-array under a box, clipped to the image bounds."""
        h, w = self.label_map.shape
        x1, y1, x2, y2 = box.xyxy
        x1 = max(0, min(x1, w))
        x2 = max(0, min(x2, w))
        y1 = max(0, min(y1, h))
        y2 = max(0, min(y2, h))
        return self.label_map[y1:y2, x1:x2]

    def histogram_in(self, box: Box) -> dict[str, float]:
        """Fraction of the box's pixels assigned to each seg class (name -> frac)."""
        region = self._region(box)
        if region.size == 0:
            return {}
        counts = np.bincount(region.ravel(), minlength=len(self.classes))
        total = float(region.size)
        return {c.name: counts[i] / total for i, c in enumerate(self.classes)}

    def dominant_in(self, box: Box) -> tuple[Optional[SegClass], float]:
        """The most common seg class under a box and its pixel fraction."""
        region = self._region(box)
        if region.size == 0:
            return None, 0.0
        counts = np.bincount(region.ravel(), minlength=len(self.classes))
        idx = int(counts.argmax())
        return self.classes[idx], float(counts[idx]) / float(region.size)

    def fraction_in(self, box: Box, predicate: Callable[[SegClass], bool]) -> float:
        """Fraction of the box's pixels whose class satisfies ``predicate``."""
        region = self._region(box)
        if region.size == 0:
            return 0.0
        keep = np.array([predicate(c) for c in self.classes], dtype=bool)
        return float(keep[region].sum()) / float(region.size)

    def color_map(self) -> np.ndarray:
        """Render the label map to an (H, W, 3) uint8 RGB image."""
        palette = np.array([c.color for c in self.classes], dtype=np.uint8)
        return palette[self.label_map]


def load_seg_taxonomy(path: str | Path = _SEG_TAXONOMY_PATH) -> list[SegClass]:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    classes: list[SegClass] = []
    for spec in data["classes"]:
        classes.append(
            SegClass(
                name=spec["name"],
                prompt=spec.get("prompt", spec["name"]),
                role=spec.get("role", "object"),
                thing=bool(spec.get("thing", False)),
                maps_to=str(spec.get("maps_to", "") or ""),
                color=tuple(spec.get("color", [128, 128, 128])),  # type: ignore[arg-type]
            )
        )
    return classes


class Segmenter:
    """Thin wrapper around CLIPSeg with lazy model loading.

    One forward pass scores every taxonomy prompt against the image and we take
    a per-pixel argmax. CLIPSeg has no explicit background class, so the prompt
    set in ``segmentation.yaml`` is kept broad enough (road, building, sky, ...)
    that "nothing here" is rare -- the argmax then just picks the closest stuff
    class, which is the intended behaviour for a dense labelling.
    """

    def __init__(
        self,
        model_name: str = "CIDAS/clipseg-rd64-refined",
        classes: Optional[list[SegClass]] = None,
        device: Optional[str] = None,
    ) -> None:
        self.model_name = model_name
        self.classes = classes or load_seg_taxonomy()
        self._device = device
        self._model = None
        self._processor = None

    # ---- lazy model ---------------------------------------------------- #
    def _ensure_model(self) -> None:
        if self._model is not None:
            return
        # Imported lazily so the app (and the box-only pipeline) can start
        # without paying the transformers import until segmentation is asked for.
        import torch
        from transformers import CLIPSegForImageSegmentation, CLIPSegProcessor

        if self._device is None:
            if torch.cuda.is_available():
                self._device = "cuda"
            elif torch.backends.mps.is_available():
                self._device = "mps"
            else:
                self._device = "cpu"

        self._processor = CLIPSegProcessor.from_pretrained(self.model_name)
        model = CLIPSegForImageSegmentation.from_pretrained(self.model_name)
        self._model = model.to(self._device).eval()

    def segment(self, image_rgb: np.ndarray) -> SegResult:
        """Densely label an RGB image into the segmentation taxonomy."""
        self._ensure_model()
        import torch
        import torch.nn.functional as F
        from PIL import Image

        h, w = image_rgb.shape[:2]
        pil = Image.fromarray(image_rgb)
        prompts = [c.prompt for c in self.classes]

        inputs = self._processor(
            text=prompts,
            images=[pil] * len(prompts),
            padding=True,
            return_tensors="pt",
        ).to(self._device)

        with torch.no_grad():
            logits = self._model(**inputs).logits  # (C, h', w') or (h', w') if C==1
        if logits.dim() == 2:
            logits = logits.unsqueeze(0)

        # Upsample every class heatmap back to the original resolution, then take
        # the per-pixel argmax to get a single dense label map.
        up = F.interpolate(
            logits.unsqueeze(0), size=(h, w), mode="bilinear", align_corners=False
        )[0]
        label_map = up.argmax(dim=0).to("cpu").numpy().astype(np.int32)
        return SegResult(label_map=label_map, classes=self.classes)


@lru_cache(maxsize=1)
def get_segmenter(model_name: str = "CIDAS/clipseg-rd64-refined") -> Segmenter:
    """Process-wide singleton so the segmentation model is loaded at most once."""
    return Segmenter(model_name=model_name)
