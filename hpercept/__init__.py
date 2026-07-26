"""Hierarchical, context-constrained perception for autonomous driving.

Implements the runtime taxonomy-abstraction idea from F. Schaller,
"The Role of Semantic Models in Constraining Pattern Recognition",
Intelligent Environments 2025.
"""
from .abstraction import AbstractionConfig, Classification, Outcome
from .constraints import SegAgreement, segmentation_agreement
from .pipeline import Pipeline, Prediction, SceneResult, get_pipeline
from .segmenter import SegClass, SegResult, Segmenter, get_segmenter, load_seg_taxonomy
from .taxonomy import Node, Taxonomy

__all__ = [
    "AbstractionConfig",
    "Classification",
    "Outcome",
    "Pipeline",
    "Prediction",
    "SceneResult",
    "get_pipeline",
    "Node",
    "Taxonomy",
    "SegAgreement",
    "segmentation_agreement",
    "SegClass",
    "SegResult",
    "Segmenter",
    "get_segmenter",
    "load_seg_taxonomy",
]

__version__ = "0.1.0"
