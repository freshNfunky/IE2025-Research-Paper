"""Taxonomy tree: loading, traversal, and the abstraction-floor logic.

The taxonomy is the semantic model that constrains pattern recognition. Every
detection is placed on a *path* from the root to some node; how deep we commit
depends on confidence, and how shallow we are *allowed* to fall back is bounded
by the nearest ``floor`` node (the anti-paranoia limit).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional

import yaml


@dataclass
class Node:
    """A single taxonomy category."""

    name: str
    prompt: str
    parent: Optional["Node"] = None
    children: list["Node"] = field(default_factory=list)

    # Semantic / safety metadata (see taxonomy.yaml for meaning).
    floor: bool = False
    coco: list[str] = field(default_factory=list)
    size: Optional[tuple[float, float]] = None
    sky_ok: bool = False

    # Filled in by Taxonomy after the tree is built.
    depth: int = 0

    # ---- convenience -------------------------------------------------- #
    @property
    def is_leaf(self) -> bool:
        return not self.children

    @property
    def is_root(self) -> bool:
        return self.parent is None

    def ancestors(self, include_self: bool = False) -> list["Node"]:
        """Return [self?, parent, ..., root] closest-first."""
        chain: list[Node] = [self] if include_self else []
        node = self.parent
        while node is not None:
            chain.append(node)
            node = node.parent
        return chain

    def path_from_root(self) -> list["Node"]:
        """Return [root, ..., self]."""
        return list(reversed(self.ancestors(include_self=True)))

    def nearest_floor(self) -> Optional["Node"]:
        """Closest floor node on the path from this node up to the root."""
        for anc in self.ancestors(include_self=True):
            if anc.floor:
                return anc
        return None

    def __repr__(self) -> str:  # pragma: no cover - debug aid
        return f"<Node {self.name!r} depth={self.depth}>"


class Taxonomy:
    """Loaded taxonomy with helpers used across the pipeline."""

    def __init__(self, root: Node) -> None:
        self.root = root
        self._by_name: dict[str, Node] = {}
        self._by_coco: dict[str, Node] = {}
        self._index(root, depth=0)

    # ---- construction ------------------------------------------------- #
    @classmethod
    def load(cls, path: str | Path) -> "Taxonomy":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        root = cls._build(data["root"], parent=None)
        return cls(root)

    @staticmethod
    def _build(spec: dict, parent: Optional[Node]) -> Node:
        size = spec.get("size")
        node = Node(
            name=spec["name"],
            prompt=spec.get("prompt", spec["name"]),
            parent=parent,
            floor=bool(spec.get("floor", False)),
            coco=list(spec.get("coco", []) or []),
            size=(tuple(size) if size else None),
            sky_ok=bool(spec.get("sky_ok", False)),
        )
        for child_spec in spec.get("children", []) or []:
            node.children.append(Taxonomy._build(child_spec, parent=node))
        return node

    def _index(self, node: Node, depth: int) -> None:
        node.depth = depth
        self._by_name[node.name.lower()] = node
        for coco_name in node.coco:
            self._by_coco[coco_name.lower()] = node
        for child in node.children:
            self._index(child, depth + 1)

    # ---- lookup ------------------------------------------------------- #
    def by_name(self, name: str) -> Optional[Node]:
        return self._by_name.get(name.lower())

    def by_coco(self, coco_name: str) -> Optional[Node]:
        """Map a COCO class name onto its taxonomy node (deepest known leaf)."""
        return self._by_coco.get(coco_name.lower())

    def iter_nodes(self) -> Iterator[Node]:
        yield from self._walk(self.root)

    def _walk(self, node: Node) -> Iterator[Node]:
        yield node
        for child in node.children:
            yield from self._walk(child)

    @property
    def max_depth(self) -> int:
        return max(n.depth for n in self.iter_nodes())

    # ---- abstraction-floor logic -------------------------------------- #
    def is_below_floor(self, node: Node) -> bool:
        """True if ``node`` is a safe/useful label (at or below a floor).

        A node satisfies the floor if it *is* a floor node or has a floor node
        among its ancestors. Nodes strictly above every floor (e.g. the root
        "Object" or "Moving Object") are considered too abstract -> the caller
        should emit UNKNOWN_OBSTACLE instead of reporting them.
        """
        return node.nearest_floor() is not None
