"""Minimal offline smoke test -- verifies taxonomy + abstraction logic without
downloading any model. Run: python smoke_test.py
"""
from __future__ import annotations

from pathlib import Path

from hpercept.abstraction import Outcome, classify_by_coco
from hpercept.taxonomy import Taxonomy

TAX = Taxonomy.load(Path(__file__).parent / "taxonomy.yaml")


def _check(name: str, cond: bool) -> None:
    print(f"[{'PASS' if cond else 'FAIL'}] {name}")
    assert cond, name


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

    print("\nAll smoke checks passed ✅")


if __name__ == "__main__":
    main()
