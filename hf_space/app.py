"""HOWC hierarchical perception - HuggingFace Space (Gradio).

Upload a road image; a detector proposes boxes and each is classified by
hierarchical taxonomic abstraction: the most specific safe level, or an explicit
UNKNOWN, never a confident wrong leaf. Models download lazily on first run.

To deploy: this file plus requirements.txt and README.md, together with the
`hpercept/` package and `taxonomy.yaml` at the Space root (copy them in, or
`pip install` the package). See README.md.
"""
from __future__ import annotations

import numpy as np
import gradio as gr

from hpercept.abstraction import AbstractionConfig
from hpercept.pipeline import get_pipeline
from hpercept.viz import annotate, taxonomy_html

PIPE = get_pipeline()
TAX = PIPE.taxonomy


def analyze(image: np.ndarray, det_conf: float, commit_mass: float, floor: bool):
    if image is None:
        return None, "Upload an image first.", [], taxonomy_html(TAX, None), gr.update(choices=[])
    cfg = AbstractionConfig(commit_mass=float(commit_mass), enforce_floor=bool(floor))
    scene = PIPE.run(image, mode="clip", det_conf=float(det_conf), cfg=cfg)
    annotated = annotate(image, scene)
    rows = [[i, p.classification.label, p.classification.outcome.value,
             f"{p.classification.confidence:.2f}", p.box.coco_name]
            for i, p in enumerate(scene.predictions)]
    c = scene.counts()
    summary = (f"**{len(scene.predictions)} detections** - "
               f"🟢 {c['identified']} identified · 🟠 {c['abstracted']} abstracted · "
               f"🔴 {c['unknown']} unknown · ⬜ {c['rejected']} rejected")
    choices = [f"{i}: {p.classification.label}" for i, p in enumerate(scene.predictions)]
    first = scene.predictions[0] if scene.predictions else None
    analyze.scene = scene
    return annotated, summary, rows, taxonomy_html(TAX, first), gr.update(
        choices=choices, value=(choices[0] if choices else None))


def highlight(sel: str):
    scene = getattr(analyze, "scene", None)
    if not scene or not sel:
        return taxonomy_html(TAX, None)
    i = min(int(sel.split(":")[0]), len(scene.predictions) - 1)
    return taxonomy_html(TAX, scene.predictions[i])


with gr.Blocks(title="HOWC Hierarchical Perception") as demo:
    gr.Markdown(
        "# HOWC : hierarchical perception for novel road objects\n"
        "Objects that fit no flat class are **abstracted up a taxonomy** to the "
        "most specific *safe* level (bounded by a 🛡 floor), or flagged as an "
        "explicit **UNKNOWN OBSTACLE** - never dropped, never a confident wrong "
        "label. Paper: doi:10.5281/zenodo.21593472")
    with gr.Row():
        with gr.Column():
            img = gr.Image(label="Road image", type="numpy")
            det = gr.Slider(0.05, 0.9, value=0.25, step=0.05, label="Detection confidence")
            cm = gr.Slider(0.3, 0.9, value=0.40, step=0.05,
                           label="Commit mass (↑ = abstracts sooner)")
            fl = gr.Checkbox(value=True, label="Safety floor 🛡 (anti-paranoia)")
            btn = gr.Button("Analyze", variant="primary")
        with gr.Column():
            out = gr.Image(label="Annotated", type="numpy")
            summ = gr.Markdown()
            tbl = gr.Dataframe(headers=["#", "label", "outcome", "conf", "yolo"],
                               label="Detections")
            pick = gr.Dropdown(label="Highlight in taxonomy", choices=[])
            tree = gr.HTML(taxonomy_html(TAX, None))
    btn.click(analyze, [img, det, cm, fl], [out, summ, tbl, tree, pick])
    pick.change(highlight, pick, tree)

if __name__ == "__main__":
    import sys
    # `python app.py --share` -> a temporary public URL (~72h), for launch-day
    # demand tests without hosting a Space.
    demo.launch(share="--share" in sys.argv)
