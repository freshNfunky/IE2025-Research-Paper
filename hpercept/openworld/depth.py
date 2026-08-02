"""Spike C: a depth source and a flatness / foreground test.

The value we want to show: with a depth signal, a *flat* detection (a car on a
billboard, a poster, painted livery) can be told apart from a genuine 3D object,
which pure 2D appearance cannot do. This is the "3D mode" over the "2D mode".

Depth source for the spike is **monocular** estimation (Depth-Anything), because
it runs on our existing images (including the billboard-style scene) with no
LiDAR dataset. In production the same interface is fed by **LiDAR** projected
into the image (metric depth); see `lidar.py` for that stub. Monocular depth is
relative, not metric, which is enough for the flatness / relief test used here.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..detector import Box


class MonoDepth:
    """Lazy monocular depth estimator (relative inverse-depth)."""

    def __init__(self, model: str = "depth-anything/Depth-Anything-V2-Small-hf") -> None:
        self.model = model
        self._pipe = None

    def _ensure(self):
        if self._pipe is None:
            from transformers import pipeline
            self._pipe = pipeline("depth-estimation", model=self.model)
        return self._pipe

    def depth(self, image_rgb: np.ndarray) -> np.ndarray:
        """Return a float32 HxW relative-depth map (larger = nearer)."""
        from PIL import Image
        out = self._ensure()(Image.fromarray(image_rgb))
        d = np.asarray(out["predicted_depth"], dtype=np.float32)
        if d.ndim == 3:
            d = d[0]
        h, w = image_rgb.shape[:2]
        if d.shape != (h, w):                       # resize to image resolution
            from PIL import Image as I
            d = np.asarray(I.fromarray(d).resize((w, h), I.BILINEAR), dtype=np.float32)
        return d


@dataclass
class FlatnessResult:
    relief: float          # planar-residual spread inside the box (0..1), low = flat
    step: float            # depth step object-vs-border (0..1), low = no foreground
    assessable: bool       # box large enough for relief to be meaningful
    is_flat: bool          # assessable AND relief below threshold -> likely 2D

    @property
    def verdict(self) -> str:
        if not self.assessable:
            return "n/a"          # too small / distant to judge 3D structure
        return "flat" if self.is_flat else "3d"


def flatness(depth: np.ndarray, box: Box, relief_thresh: float = 0.12,
             min_side: int = 64, min_area_frac: float = 0.02) -> FlatnessResult:
    """Is the region inside ``box`` flat (a 2D depiction) or a 3D object?

    A flat panel has near-planar depth (low residual once a plane is removed); a
    real object has internal relief. This is only meaningful when the box is large
    enough to resolve structure: small / distant boxes are marked *not assessable*
    rather than falsely flagged flat (the recurring scale / undersampling limit;
    metric LiDAR depth would raise the assessable range).
    """
    h, w = depth.shape
    x1, y1, x2, y2 = box.xyxy
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    bw, bh = x2 - x1, y2 - y1
    assessable = (min(bw, bh) >= min_side
                  and (bw * bh) / float(w * h) >= min_area_frac)
    if bw < 4 or bh < 4:
        return FlatnessResult(1.0, 0.0, False, False)

    patch = depth[y1:y2, x1:x2].astype(np.float32)
    scale = float(depth.max() - depth.min()) or 1.0

    # remove a best-fit plane, measure residual spread (internal relief)
    ph, pw = patch.shape
    ys, xs = np.mgrid[0:ph, 0:pw]
    A = np.stack([xs.ravel(), ys.ravel(), np.ones(ph * pw)], axis=1).astype(np.float32)
    coef, *_ = np.linalg.lstsq(A, patch.ravel(), rcond=None)
    resid = patch.ravel() - A @ coef
    relief = float(np.std(resid) / scale)

    # foreground step: object interior vs a border ring around the box
    bx1, by1 = max(0, x1 - 6), max(0, y1 - 6)
    bx2, by2 = min(w, x2 + 6), min(h, y2 + 6)
    ring = depth[by1:by2, bx1:bx2]
    step = float(abs(np.median(patch) - np.median(ring)) / scale)

    return FlatnessResult(round(relief, 4), round(step, 4), assessable,
                          assessable and relief < relief_thresh)
