"""Context-validation gates (paper section 3.2 / 4.3).

After a pattern is detected and hierarchically classified, we validate that it
is *plausible* in its context. These are deliberately simple, transparent rules
-- the point is to demonstrate the validation layer that rejects physically
impossible detections (the "car flying above the clouds" example), not to be an
exhaustive physics engine.

Two families of gate live here:

* *Geometric* gates (``validate``) use only the box and the taxonomy metadata --
  size and image-position priors. They are cheap and always on.
* A *data-driven* gate (``segmentation_agreement``) cross-checks each box
  against the independent semantic-segmentation path (see ``segmenter.py``). It
  is the empirical counterpart to the hard-coded position rule: instead of
  assuming "the top 35% of the frame is sky", it asks the segmenter what is
  actually there and rejects a ground vehicle whose pixels are labelled sky.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .detector import Box
from .segmenter import SegResult
from .taxonomy import Node

# Tunables for the segmentation cross-validation gate. Kept as module-level
# constants (not magic numbers) so the operating point is inspectable, mirroring
# the AbstractionConfig knobs on the box path.
#
# The support metric is measured over the *object* pixels under a box (the ones
# the segmenter labels as some discrete "thing"), NOT over the whole box. A road
# detection box legitimately contains a lot of road/terrain around the object;
# counting that as "non-support" would unfairly dilute every verdict. So we ask:
# of the pixels the segmenter thinks are objects, how many agree with the box's
# taxonomy branch?
SEG_CONFIRM_SUPPORT = 0.50   # >= this share of OBJECT pixels on-branch -> confirm
SEG_CONFLICT_FRAC = 0.55     # a competing class this dominant -> implausible
SEG_MIN_SUPPORT = 0.15       # on-branch object share below this is "unsupported"
SEG_OBJECT_FLOOR = 0.04      # need at least this share of the box to be objects


@dataclass
class ConstraintResult:
    ok: bool
    violations: list[str]

    @property
    def summary(self) -> str:
        return "OK" if self.ok else "; ".join(self.violations)


@dataclass
class SegAgreement:
    """How the segmentation path judges one box-based detection.

    ``status`` is one of, in increasing severity:
      "confirm"  -- the segmentation independently supports the detection's
                    taxonomy branch (real corroborating evidence).
      "neutral"  -- no strong signal either way (segmentation off, an UNKNOWN
                    obstacle with no branch to check, or the object pixels are
                    too few / too mixed to judge).
      "flag"     -- the two paths DISAGREE about the label: the object pixels
                    belong to a different taxonomy branch (box says Vehicle, the
                    segmenter says Living Being). This is surfaced but is NOT a
                    rejection -- there is still clearly an object there, so
                    dropping it would violate the "never lose an obstacle"
                    principle. A flag marks a detection for cautious handling /
                    relabelling, not deletion.
      "conflict" -- physically implausible: the object sits on sky pixels (the
                    data-driven "flying car"). Only this hard case is promoted to
                    a constraint violation that rejects the detection.
    """

    status: str
    support: float           # fraction of box pixels backing the box's branch
    dominant: str            # dominant seg class name under the box
    dominant_frac: float     # its pixel fraction
    note: str

    @property
    def is_conflict(self) -> bool:
        """Only a hard (physically-impossible) conflict rejects the detection."""
        return self.status == "conflict"

    @property
    def is_flag(self) -> bool:
        return self.status == "flag"


def validate(
    box: Box,
    node: Node,
    img_w: int,
    img_h: int,
    seg: Optional[SegAgreement] = None,
) -> ConstraintResult:
    """Run all context-validation gates for one classified detection.

    ``seg`` is the optional segmentation cross-check; when it reports a conflict
    the detection is rejected just like a geometric violation."""
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

    # --- Data-driven: segmentation cross-validation ------------------- #
    if seg is not None and seg.is_conflict:
        violations.append(f"segmentation: {seg.note}")

    return ConstraintResult(ok=not violations, violations=violations)


def segmentation_agreement(
    box: Box, node: Node, seg_result: SegResult
) -> SegAgreement:
    """Cross-check one detection against the dense segmentation.

    We resolve the detection's *branch* to its nearest safety-floor node (the
    same Living Being / Vehicle / Static Object level the segmentation taxonomy
    maps its "thing" classes onto), then compare:

      * support  -- how much of the box the segmenter assigns to that branch;
      * dominant -- the single most common class under the box.

    An UNKNOWN obstacle has no branch to confirm, so it is never *rejected* here
    -- safety-first: the segmentation may add a hint but must not veto an
    unexplained hazard.
    """
    branch = node.nearest_floor()
    dom, dom_frac = seg_result.dominant_in(box)

    if dom is None:  # degenerate/empty box region
        return SegAgreement("neutral", 0.0, "-", 0.0, "no segmentation coverage")

    # Aggregate the box's pixels by the taxonomy branch each seg class maps onto.
    # Only "thing" classes carry a branch; "stuff" (road, sky, ...) is context.
    hist = seg_result.histogram_in(box)          # class name -> fraction of box
    by_name = {c.name: c for c in seg_result.classes}
    thing_frac = sum(f for n, f in hist.items() if by_name[n].thing)
    branch_frac: dict[str, float] = {}
    for n, f in hist.items():
        c = by_name[n]
        if c.thing and c.maps_to:
            branch_frac[c.maps_to] = branch_frac.get(c.maps_to, 0.0) + f

    if branch is None:
        # Above every floor (UNKNOWN obstacle): report context, never reject.
        return SegAgreement(
            "neutral", 0.0, dom.name, dom_frac,
            f"unverifiable (dominant context: {dom.name})",
        )

    on_branch = branch_frac.get(branch.name, 0.0)
    # Corroboration is measured over object pixels only (see constants above).
    object_support = on_branch / thing_frac if thing_frac > 1e-6 else 0.0

    # --- Conflict 1: data-driven flying object ------------------------ #
    # The empirical version of the position gate: the pixels under a ground
    # object are actually sky.
    if dom.is_sky and not _inherited_sky_ok(node) and dom_frac >= SEG_CONFLICT_FRAC:
        return SegAgreement(
            "conflict", on_branch, dom.name, dom_frac,
            f"{node.name} sits on sky pixels ({dom_frac:.0%})",
        )

    # --- Flag: the object pixels belong to a DIFFERENT branch --------- #
    # e.g. a box classified Vehicle whose object pixels the segmenter labels
    # overwhelmingly "person"/"animal" (Living Being) and barely any vehicle.
    # The two paths disagree about *what* it is -- but there is clearly still an
    # object, so we flag for review rather than reject (dropping a mislabelled
    # obstacle is exactly the failure the hierarchy is designed to avoid).
    other = [(b, f) for b, f in branch_frac.items() if b != branch.name]
    if other and thing_frac > 1e-6:
        ob_branch, ob_frac = max(other, key=lambda kv: kv[1])
        if ob_frac / thing_frac >= SEG_CONFLICT_FRAC and object_support < SEG_MIN_SUPPORT:
            return SegAgreement(
                "flag", on_branch, dom.name, dom_frac,
                f"paths disagree: box says {branch.name}, segmentation says "
                f"'{ob_branch}' ({ob_frac / thing_frac:.0%} of object pixels)",
            )

    # --- Corroboration ------------------------------------------------ #
    if on_branch >= SEG_OBJECT_FLOOR and object_support >= SEG_CONFIRM_SUPPORT:
        return SegAgreement(
            "confirm", on_branch, dom.name, dom_frac,
            f"segmentation supports {branch.name} "
            f"({object_support:.0%} of object pixels)",
        )

    return SegAgreement(
        "neutral", on_branch, dom.name, dom_frac,
        f"weak support for {branch.name} "
        f"({on_branch:.0%} of box; dominant {dom.name})",
    )


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
