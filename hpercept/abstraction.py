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
    mass: float          # probability mass of the chosen child's subtree (0..1)
    committed: bool      # did we actually descend into `chosen`?


@dataclass
class Classification:
    node: Node                       # the node we report (deepest reached if unknown)
    outcome: Outcome
    confidence: float                # confidence of the *reported* level
    path: list[Node] = field(default_factory=list)
    steps: list[Step] = field(default_factory=list)
    node_mass: dict[str, float] = field(default_factory=dict)  # per-node prob mass
    top_sim: float = 0.0             # best-leaf CLIP cosine similarity

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
    # CLIP is scored ONLY on the concrete leaf prompts (where it is reliable);
    # abstract-node scores are derived by summing leaf probability mass up the
    # tree. We then descend as long as a single child subtree holds enough mass
    # -- when mass splits across children (the crop is ambiguous between, say,
    # "horse" and "bicycle"), we stop and report their common ancestor.
    min_abs_sim: float = 0.22   # min best-leaf cosine; below this nothing matches
    commit_mass: float = 0.55   # min child subtree mass to descend one level
    temperature: float = 0.06   # softmax temperature over leaf similarities
    enforce_floor: bool = True  # apply the anti-paranoia (floor) limit


def classify_crop(
    crop_rgb: np.ndarray,
    taxonomy: Taxonomy,
    clip: ClipClassifier,
    cfg: AbstractionConfig,
) -> Classification:
    """Leaf-scored, mass-aggregated hierarchical classification with floor."""
    image_feat = clip.image_features(crop_rgb)

    leaves = [n for n in taxonomy.iter_nodes() if n.is_leaf]
    sims = np.array(
        [float(np.dot(image_feat, clip._text_feats[l.name])) for l in leaves]
    )
    top_sim = float(sims.max())

    # Softmax over leaves -> a probability per concrete category.
    z = sims / max(cfg.temperature, 1e-6)
    z = z - z.max()
    probs = np.exp(z)
    probs /= probs.sum()

    # Precompute each leaf's ancestor-name set so subtree mass is a fast sum.
    leaf_anc = [{a.name for a in l.ancestors(include_self=True)} for l in leaves]

    def mass(node: Node) -> float:
        return float(sum(p for p, anc in zip(probs, leaf_anc) if node.name in anc))

    node = taxonomy.root
    path: list[Node] = [node]
    steps: list[Step] = []

    # If nothing matches even the best leaf, don't descend at all -> UNKNOWN.
    if top_sim >= cfg.min_abs_sim:
        while node.children:
            best = max(node.children, key=mass)
            bm = mass(best)
            committed = bm >= cfg.commit_mass
            steps.append(Step(node.name, best.name, round(bm, 3), committed))
            if not committed:
                break  # mass split across children -> ambiguous -> abstract here
            node = best
            path.append(node)

    confidence = round(mass(node), 3) if top_sim >= cfg.min_abs_sim else 0.0
    outcome = _resolve_outcome(node, taxonomy, cfg)
    node_mass = {n.name: round(mass(n), 4) for n in taxonomy.iter_nodes()}
    return Classification(
        node=node,
        outcome=outcome,
        confidence=confidence,
        path=path,
        steps=steps,
        node_mass=node_mass,
        top_sim=round(top_sim, 4),
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
