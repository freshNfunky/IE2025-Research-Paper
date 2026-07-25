"""Context-validation gates (paper section 3.2 / 4.3).

After a pattern is detected and hierarchically classified, we validate that it
is *plausible* in its context. These are deliberately simple, transparent rules
-- the point is to demonstrate the validation layer that rejects physically
impossible detections (the "car flying above the clouds" example), not to be an
exhaustive physics engine.
"""
from __future__ import annotations

from dataclasses import dataclass

from .detector import Box
from .taxonomy import Node


@dataclass
class ConstraintResult:
    ok: bool
    violations: list[str]

    @property
    def summary(self) -> str:
        return "OK" if self.ok else "; ".join(self.violations)


def validate(box: Box, node: Node, img_w: int, img_h: int) -> ConstraintResult:
    """Run all context-validation gates for one classified detection."""
    violations: list[str] = []

    # --- Physical: size plausibility ---------------------------------- #
    size_spec = _inherited_size(node)
    if size_spec is not None:
        frac = box.area_frac(img_w, img_h)
        lo, hi = size_spec
        if frac < lo:
            violations.append(f"too small for {node.name} ({frac:.4f}<{lo})")
        elif frac > hi:
            violations.append(f"too large for {node.name} ({frac:.3f}>{hi})")

    # --- Physical: position plausibility ------------------------------ #
    # A ground object whose box sits entirely in the top of the frame (sky)
    # is physically implausible -> the classic "flying car" false positive.
    if not _inherited_sky_ok(node):
        horizon = 0.35 * img_h  # everything above this is treated as "sky"
        if box.y2 < horizon:
            violations.append(f"{node.name} floating in sky region")

    return ConstraintResult(ok=not violations, violations=violations)


def _inherited_size(node: Node) -> tuple[float, float] | None:
    """Nearest size spec walking up the taxonomy (constraints inherit)."""
    for anc in node.ancestors(include_self=True):
        if anc.size is not None:
            return anc.size
    return None


def _inherited_sky_ok(node: Node) -> bool:
    for anc in node.ancestors(include_self=True):
        if anc.sky_ok:
            return True
    return False
