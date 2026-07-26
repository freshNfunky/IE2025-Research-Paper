"""Minimal offline smoke test -- verifies taxonomy + abstraction logic (and the
segmentation cross-validation gate) without downloading any model.
Run: python smoke_test.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from hpercept.abstraction import Outcome, classify_by_coco
from hpercept.constraints import segmentation_agreement, validate
from hpercept.detector import Box
from hpercept.segmenter import SegResult, load_seg_taxonomy
from hpercept.taxonomy import Taxonomy

TAX = Taxonomy.load(Path(__file__).parent / "taxonomy.yaml")
SEG_CLASSES = load_seg_taxonomy()


def _check(name: str, cond: bool) -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    assert cond, name


def _seg_of(dominant: str, size: int = 100) -> SegResult:
    """A synthetic uniform segmentation labelling every pixel ``dominant``."""
    idx = next(i for i, c in enumerate(SEG_CLASSES) if c.name == dominant)
    label_map = np.full((size, size), idx, dtype=np.int32)
    return SegResult(label_map=label_map, classes=SEG_CLASSES)


def check_segmentation() -> None:
    print("\n-- segmentation cross-validation (synthetic, no model) --")

    # Seg taxonomy is well-formed: every "thing" maps onto a real safety floor.
    for c in SEG_CLASSES:
        if c.thing:
            node = TAX.by_name(c.maps_to)
            _check(f"seg class '{c.name}' maps to a floor node",
                   node is not None and node.floor)

    box = Box(x1=10, y1=10, x2=90, y2=90, coco_name="car", coco_conf=0.9)
    car = TAX.by_name("Passenger Car")   # a Vehicle-branch, ground, non-sky node

    # Data-driven flying car: a car whose pixels are sky -> conflict -> reject.
    fly = segmentation_agreement(box, car, _seg_of("sky"))
    _check("car-on-sky -> seg conflict", fly.status == "conflict")
    _check("car-on-sky -> validate rejects",
           not validate(box, car, 100, 100, seg=fly).ok)

    # Corroboration: a car whose pixels are 'vehicle' -> confirm -> not rejected.
    ok = segmentation_agreement(box, car, _seg_of("vehicle"))
    _check("car-on-vehicle -> seg confirm", ok.status == "confirm")
    _check("car-on-vehicle -> validate passes",
           validate(box, car, 100, 100, seg=ok).ok)

    # Cross-branch disagreement: a 'car' box over 'person' pixels -> FLAG, not a
    # rejection (there is still an obstacle; only the label is disputed).
    xb = segmentation_agreement(box, car, _seg_of("person"))
    _check("car-on-person -> seg flag", xb.status == "flag")
    _check("car-on-person -> NOT rejected (obstacle kept)",
           validate(box, car, 100, 100, seg=xb).ok)

    # Safety-first: an UNKNOWN obstacle (above every floor) is never rejected by
    # segmentation, even sitting on sky pixels.
    root = TAX.root
    unk = segmentation_agreement(box, root, _seg_of("sky"))
    _check("unknown obstacle -> seg never conflicts", unk.status != "conflict")


def main() -> None:
    # Tree loaded and indexed
    _check("root is Object", TAX.root.name == "Object")
    _check("max depth > 5", TAX.max_depth > 5)

    # COCO mapping
    truck = TAX.by_coco("truck")
    _check("truck maps into taxonomy", truck is not None)
    _check("truck is below a floor", TAX.is_below_floor(truck))

    # Floors exist and nodes above them are flagged not-below-floor
    moving = TAX.by_name("Moving Object")
    _check("Moving Object is above all floors", not TAX.is_below_floor(moving))

    # Abstraction by confidence (YOLO-only path)
    high = classify_by_coco("truck", 0.92, TAX)
    _check("high-conf truck -> identified", high.outcome is Outcome.IDENTIFIED)

    mid = classify_by_coco("truck", 0.45, TAX)
    _check("mid-conf truck -> abstracted", mid.outcome is Outcome.ABSTRACTED)
    _check("abstracted target is a floor (Vehicle)", mid.node.name == "Vehicle")

    low = classify_by_coco("truck", 0.20, TAX)
    _check("low-conf -> unknown", low.outcome is Outcome.UNKNOWN)

    unmapped = classify_by_coco("banana", 0.9, TAX)
    _check("unmapped class -> unknown", unmapped.outcome is Outcome.UNKNOWN)

    check_segmentation()

    print("\nAll smoke checks passed ✅")


if __name__ == "__main__":
    main()
