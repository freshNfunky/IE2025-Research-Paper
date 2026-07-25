"""Hierarchical, context-constrained perception for autonomous driving.

Implements the runtime taxonomy-abstraction idea from F. Schaller,
"The Role of Semantic Models in Constraining Pattern Recognition",
Intelligent Environments 2025.
"""
from .abstraction import AbstractionConfig, Classification, Outcome
from .pipeline import Pipeline, Prediction, SceneResult, get_pipeline
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
]

__version__ = "0.1.0"
