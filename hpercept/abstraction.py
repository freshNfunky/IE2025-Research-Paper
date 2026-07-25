"""The core contribution: hierarchical classification with an abstraction floor.

Two knobs govern behaviour, mirroring the paper:

* ``descend_threshold`` -- how decisive the evidence for a child must be before
  we commit one level deeper. Low  -> the system dives to specific leaves
  eagerly (risk: over-confident wrong leaves). High -> the system abstracts
  readily (safer, but more "paranoid").

* the **floor** (encoded in the taxonomy, not a scalar) -- how shallow we are
  allowed to fall back before we give up on a semantic label and declare
  UNKNOWN_OBSTACLE. This is the anti-paranoia limit: without it, an uncertain
  detector would happily label everything the useless-but-technically-true
  "Object", and a planner fed that would brake for the whole world.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np

from .classifier import ClipClassifier
from .taxonomy import Node, Taxonomy


class Outcome(str, Enum):
    IDENTIFIED = "identified"        # committed to a specific leaf
    ABSTRACTED = "abstracted"        # fell back to a coarser (but useful) node
    UNKNOWN = "unknown"              # even the floor was not confident


@dataclass
class Step:
    """One descent decision, kept for explainability in the UI."""

    parent: str
    chosen: str
    prob: float          # softmax prob of the chosen child among its siblings
    abs_sim: float       # raw CLIP cosine similarity to the chosen child
    committed: bool      # did we actually descend into `chosen`?


@dataclass
class Classification:
    node: Node                       # the node we report (deepest reached if unknown)
    outcome: Outcome
    confidence: float                # confidence of the *reported* level
    path: list[Node] = field(default_factory=list)
    steps: list[Step] = field(default_factory=list)

    @property
    def label(self) -> str:
        if self.outcome is Outcome.UNKNOWN:
            return f"UNKNOWN OBSTACLE (~{self.node.name})"
        return self.node.name

    @property
    def is_novelty(self) -> bool:
        return self.outcome in (Outcome.ABSTRACTED, Outcome.UNKNOWN)


@dataclass
class AbstractionConfig:
    descend_threshold: float = 0.55   # min sibling-softmax prob to go deeper
    min_abs_sim: float = 0.20         # min raw CLIP similarity to commit
    temperature: float = 0.01         # softmax temperature over siblings
    enforce_floor: bool = True        # apply the anti-paranoia limit


def classify_crop(
    crop_rgb: np.ndarray,
    taxonomy: Taxonomy,
    clip: ClipClassifier,
    cfg: AbstractionConfig,
) -> Classification:
    """Top-down hierarchical descent with confidence gating and floor fallback."""
    image_feat = clip.image_features(crop_rgb)

    node = taxonomy.root
    path: list[Node] = [node]
    steps: list[Step] = []
    committed_conf = 1.0

    while node.children:
        probs = clip.child_probs(image_feat, node.children, cfg.temperature)
        best_child = max(node.children, key=lambda c: probs[c.name])
        best_p = probs[best_child.name]
        abs_sim = float(np.dot(image_feat, clip._text_feats[best_child.name]))

        confident = best_p >= cfg.descend_threshold and abs_sim >= cfg.min_abs_sim
        steps.append(
            Step(node.name, best_child.name, best_p, abs_sim, committed=confident)
        )
        if not confident:
            break  # ambiguous among children -> stop and abstract here
        node = best_child
        path.append(node)
        committed_conf = min(committed_conf, best_p)

    outcome = _resolve_outcome(node, taxonomy, cfg)
    return Classification(
        node=node,
        outcome=outcome,
        confidence=round(committed_conf, 3),
        path=path,
        steps=steps,
    )


def _resolve_outcome(node: Node, taxonomy: Taxonomy, cfg: AbstractionConfig) -> Outcome:
    if node.is_leaf and not (cfg.enforce_floor and not taxonomy.is_below_floor(node)):
        return Outcome.IDENTIFIED
    if cfg.enforce_floor and not taxonomy.is_below_floor(node):
        # We stopped ABOVE every safety floor -> too abstract to be useful.
        return Outcome.UNKNOWN
    if node.is_leaf:
        return Outcome.IDENTIFIED
    return Outcome.ABSTRACTED


# --------------------------------------------------------------------------- #
#  YOLO-only fallback mode (no CLIP): abstract using YOLO's own confidence.    #
# --------------------------------------------------------------------------- #
def classify_by_coco(
    coco_name: str,
    coco_conf: float,
    taxonomy: Taxonomy,
    leaf_threshold: float = 0.55,
    unknown_threshold: float = 0.30,
) -> Classification:
    """Map a YOLO COCO detection onto the taxonomy and abstract by confidence.

    Without CLIP we cannot score arbitrary abstraction levels, so we use a
    coarse heuristic: high confidence -> keep the specific COCO leaf; medium ->
    abstract one level toward the floor; below ``unknown_threshold`` or an
    unmapped class -> UNKNOWN.
    """
    leaf = taxonomy.by_coco(coco_name)
    if leaf is None or coco_conf < unknown_threshold:
        floor = _fallback_floor(taxonomy)
        return Classification(
            node=floor, outcome=Outcome.UNKNOWN, confidence=round(coco_conf, 3),
            path=floor.path_from_root(),
        )
    if coco_conf >= leaf_threshold:
        return Classification(
            node=leaf, outcome=Outcome.IDENTIFIED, confidence=round(coco_conf, 3),
            path=leaf.path_from_root(),
        )
    # Medium confidence: abstract up toward (but not above) the floor.
    target = leaf.nearest_floor() or leaf.parent or leaf
    return Classification(
        node=target, outcome=Outcome.ABSTRACTED, confidence=round(coco_conf, 3),
        path=target.path_from_root(),
    )


def _fallback_floor(taxonomy: Taxonomy) -> Node:
    """A generic floor node to attribute unknowns to (deepest reached: root)."""
    return taxonomy.root
