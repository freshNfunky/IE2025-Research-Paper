"""Lazy dataset registry.

Designed for a machine with little free disk: nothing is downloaded up front.
When the user picks a dataset and asks for N samples, we open it in Hugging
Face *streaming* mode and pull only those N images (range requests, no full
shard download). A local-folder source and single-image upload/URL are always
available as zero-dependency fallbacks.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from typing import Callable, Iterator, Optional

import numpy as np

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass
class Sample:
    image: np.ndarray            # RGB uint8
    caption: str = ""


@dataclass
class DatasetSource:
    id: str
    name: str
    description: str
    kind: str                    # "hf" | "local"
    repo_id: str = ""
    split: str = "train"
    config: Optional[str] = None
    note: str = ""

    def load(self, n: int) -> list[Sample]:
        if self.kind == "hf":
            return list(islice(_stream_hf(self.repo_id, self.split, self.config), n))
        if self.kind == "local":
            return list(islice(_load_local(self.repo_id), n))
        raise ValueError(f"unknown source kind: {self.kind}")


# --------------------------------------------------------------------------- #
#  Registry -- edit / extend here.                                            #
# --------------------------------------------------------------------------- #
REGISTRY: dict[str, DatasetSource] = {
    # Primary "unknowns" set -- verified streaming. Thematically ideal: real
    # street scenes with anomalous objects (animals, unknown vehicles) that
    # have no proper flat class, exactly the paper's scenario.
    "road_anomaly": DatasetSource(
        id="road_anomaly",
        name="Road Anomaly (unknowns) ⭐",
        description="Internet street scenes with anomalous objects on the "
        "road (animals, unknown vehicles). Strong novelty triggers.",
        kind="hf",
        repo_id="kumuji/roadanomaly21_roadobstacle21",
        split="validation",
        note="SegmentMeIfYouCan mirror. Only the 'validation' split exists.",
    ),
    # Known-baseline set -- verified streaming. Mostly in-taxonomy objects, a
    # good contrast to the corner cases.
    "cityscapes": DatasetSource(
        id="cityscapes",
        name="Cityscapes (known baseline)",
        description="Dense urban driving scenes with common, in-taxonomy "
        "objects. Contrast set for the novelty triggers.",
        kind="hf",
        repo_id="Chris1/cityscapes",
        split="train",
        note="Streams cleanly (image + semantic_segmentation).",
    ),
    # Kept because the user asked for CODA, but the only HF mirror is the
    # LM-annotation build whose nested text schema breaks streaming casts.
    "coda": DatasetSource(
        id="coda",
        name="CODA (corner cases) ⚠ may fail",
        description="Real-world road corner cases. The only HF mirror is the "
        "CODA-LM (VQA) build; streaming often fails on its nested schema.",
        kind="hf",
        repo_id="KaiChen1998/coda-lm",
        split="validation",
        note="If this errors, use Road Anomaly, or download original CODA "
        "images from coda-dataset.github.io into data/samples/.",
    ),
    "local": DatasetSource(
        id="local",
        name="Local folder (data/samples)",
        description="Your own images / extracted video frames. Drop files "
        "into data/samples/ -- always works offline.",
        kind="local",
        repo_id=str(_DATA_DIR / "samples"),
    ),
}


def list_sources() -> list[DatasetSource]:
    return list(REGISTRY.values())


def get_source(source_id: str) -> DatasetSource:
    return REGISTRY[source_id]


# --------------------------------------------------------------------------- #
#  Loaders                                                                     #
# --------------------------------------------------------------------------- #
def _stream_hf(repo_id: str, split: str, config: Optional[str]) -> Iterator[Sample]:
    from datasets import get_dataset_config_names, load_dataset

    def _open(cfg: Optional[str]):
        return load_dataset(repo_id, name=cfg, split=split, streaming=True)

    try:
        ds = _open(config)
    except ValueError:
        # Most commonly: "Config name is missing" for multi-subset datasets.
        if config is not None:
            raise
        configs = get_dataset_config_names(repo_id)
        if not configs:
            raise
        ds = _open(configs[0])
    for example in ds:
        img = _extract_image(example)
        if img is None:
            continue
        yield Sample(image=img, caption=_extract_caption(example))


def _load_local(folder: str) -> Iterator[Sample]:
    from PIL import Image

    root = Path(folder)
    if not root.exists():
        root.mkdir(parents=True, exist_ok=True)
        return
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    for path in sorted(root.iterdir()):
        if path.suffix.lower() in exts:
            with Image.open(path) as im:
                yield Sample(image=np.array(im.convert("RGB")), caption=path.name)


def _extract_image(example: dict) -> Optional[np.ndarray]:
    """Find the first PIL image in an HF example and return it as RGB ndarray."""
    from PIL import Image

    for value in example.values():
        if isinstance(value, Image.Image):
            return np.array(value.convert("RGB"))
    # Some datasets nest the image or expose a path/bytes dict.
    for value in example.values():
        if isinstance(value, dict) and "bytes" in value and value["bytes"]:
            import io

            return np.array(Image.open(io.BytesIO(value["bytes"])).convert("RGB"))
    return None


def _extract_caption(example: dict) -> str:
    for key in ("caption", "text", "question", "label", "image_id", "id"):
        if key in example and isinstance(example[key], (str, int)):
            return str(example[key])[:120]
    return ""
