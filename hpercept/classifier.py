"""CLIP zero-shot classifier over taxonomy nodes.

This is what makes the system *open-vocabulary*: every taxonomy node (not just
the leaves) has a text prompt, and we can score how well any image crop matches
each node. That lets the abstraction logic ask "is this confidently a Truck? no?
then is it confidently a Transport Vehicle? ..." all the way up the tree, even
for objects the underlying detector was never trained on.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

import numpy as np

from .taxonomy import Node, Taxonomy


class ClipClassifier:
    """Wraps open_clip and pre-computes text features for every taxonomy node."""

    def __init__(
        self,
        taxonomy: Taxonomy,
        # NOTE: OpenAI CLIP weights were trained with the QuickGELU activation.
        # The plain "ViT-B-32" config uses nn.GELU and silently degrades
        # accuracy, so we must pair the "-quickgelu" model with the openai tag.
        model_name: str = "ViT-B-32-quickgelu",
        pretrained: str = "openai",
        device: Optional[str] = None,
    ) -> None:
        self.taxonomy = taxonomy
        self.model_name = model_name
        self.pretrained = pretrained
        self._device = device
        self._model = None
        self._preprocess = None
        self._tokenizer = None
        self._text_feats: dict[str, np.ndarray] = {}

    # ---- lazy model ---------------------------------------------------- #
    def _ensure_model(self) -> None:
        if self._model is not None:
            return
        import open_clip
        import torch

        if self._device is None:
            if torch.cuda.is_available():
                self._device = "cuda"
            elif torch.backends.mps.is_available():
                self._device = "mps"
            else:
                self._device = "cpu"

        model, _, preprocess = open_clip.create_model_and_transforms(
            self.model_name, pretrained=self.pretrained
        )
        model = model.to(self._device).eval()
        self._model = model
        self._preprocess = preprocess
        self._tokenizer = open_clip.get_tokenizer(self.model_name)
        self._encode_taxonomy_text()

    def _encode_taxonomy_text(self) -> None:
        import torch

        nodes = [n for n in self.taxonomy.iter_nodes()]
        prompts = [self._templated(n) for n in nodes]
        tokens = self._tokenizer(prompts).to(self._device)
        with torch.no_grad():
            feats = self._model.encode_text(tokens)
            feats = feats / feats.norm(dim=-1, keepdim=True)
        feats_np = feats.cpu().numpy()
        for node, f in zip(nodes, feats_np):
            self._text_feats[node.name] = f

    @staticmethod
    def _templated(node: Node) -> str:
        # A light prompt template improves CLIP zero-shot separability.
        return f"a photo of {node.prompt}"

    # ---- inference ----------------------------------------------------- #
    def image_features(self, crop_rgb: np.ndarray) -> np.ndarray:
        """Return an L2-normalized CLIP embedding for one RGB crop."""
        self._ensure_model()
        import torch
        from PIL import Image

        if crop_rgb.size == 0:
            # Degenerate crop -> return a zero vector (matches nothing well).
            dim = next(iter(self._text_feats.values())).shape[0]
            return np.zeros(dim, dtype=np.float32)

        pil = Image.fromarray(crop_rgb)
        tensor = self._preprocess(pil).unsqueeze(0).to(self._device)
        with torch.no_grad():
            feat = self._model.encode_image(tensor)
            feat = feat / feat.norm(dim=-1, keepdim=True)
        return feat.cpu().numpy()[0]

    def similarities(self, crop_rgb: np.ndarray, nodes: list[Node]) -> dict[str, float]:
        """Cosine similarity of the crop against each of ``nodes``."""
        self._ensure_model()
        img = self.image_features(crop_rgb)
        return {n.name: float(np.dot(img, self._text_feats[n.name])) for n in nodes}

    def child_probs(
        self, image_feat: np.ndarray, children: list[Node], temperature: float = 0.01
    ) -> dict[str, float]:
        """Softmax distribution over a node's children given a precomputed crop
        embedding. Used by the top-down hierarchical descent."""
        sims = np.array(
            [float(np.dot(image_feat, self._text_feats[c.name])) for c in children]
        )
        scaled = sims / max(temperature, 1e-6)
        scaled -= scaled.max()
        exp = np.exp(scaled)
        probs = exp / exp.sum()
        return {c.name: float(p) for c, p in zip(children, probs)}


@lru_cache(maxsize=1)
def get_classifier(taxonomy_id: int) -> "ClipClassifier":  # pragma: no cover
    # Not used directly (taxonomy isn't hashable); see pipeline for wiring.
    raise NotImplementedError
