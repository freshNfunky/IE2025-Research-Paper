"""Gradio UI for hierarchical, context-constrained object perception.

Run:  python app.py    (first run downloads the YOLO + CLIP weights lazily)
"""
from __future__ import annotations

import numpy as np
import gradio as gr

from hpercept import datasets
from hpercept.abstraction import AbstractionConfig
from hpercept.pipeline import get_pipeline
from hpercept.viz import (
    annotate,
    segmentation_overlay,
    seg_legend_html,
    taxonomy_html,
)

PIPELINE = get_pipeline()
TAXONOMY = PIPELINE.taxonomy

MODE_LABELS = {
    "YOLO + CLIP (open-set, recommended)": "clip",
    "YOLO only (COCO confidence)": "yolo",
}


# --------------------------------------------------------------------------- #
#  Callbacks                                                                   #
# --------------------------------------------------------------------------- #
def load_samples(source_id: str, n: int):
    src = datasets.get_source(source_id)
    try:
        samples = src.load(int(n))
    except Exception as exc:  # streaming/gated/missing -> show a helpful note
        msg = f"⚠️ Could not load '{src.name}': {exc}\n\nHint: {src.note}"
        return gr.update(value=[]), msg
    if not samples:
        return gr.update(value=[]), (
            f"No samples found for '{src.name}'.\n{src.note}"
        )
    gallery = [(s.image, s.caption or f"#{i}") for i, s in enumerate(samples)]
    return gr.update(value=gallery), f"Loaded {len(samples)} sample(s) from {src.name}."


def pick_from_gallery(evt: gr.SelectData, source_id: str, n: int):
    # Re-fetch the selected sample deterministically by index.
    src = datasets.get_source(source_id)
    samples = src.load(int(n))
    idx = evt.index if isinstance(evt.index, int) else 0
    idx = min(idx, len(samples) - 1)
    return samples[idx].image


SEG_ICON = {"confirm": "✅", "flag": "⚠️", "conflict": "❌", "neutral": "➖", "off": "—"}


def analyze(image: np.ndarray, mode_label: str, det_conf: float,
            descend: float, min_sim: float, enforce_floor: bool,
            use_seg: bool):
    if image is None:
        return (None, "Please choose or upload an image first.", [], _tree(None),
                gr.update(choices=[], value=None), None, "")

    mode = MODE_LABELS[mode_label]
    cfg = AbstractionConfig(
        commit_mass=float(descend),
        min_abs_sim=float(min_sim),
        enforce_floor=bool(enforce_floor),
    )
    scene = PIPELINE.run(image, mode=mode, det_conf=float(det_conf), cfg=cfg,
                         segment=bool(use_seg))
    annotated = annotate(image, scene)

    def _seg_cell(p):
        if p.seg is None:
            return "—"
        return f"{SEG_ICON.get(p.seg.status, '')} {p.seg.note}"

    rows = [[
        i, p.classification.label, p.classification.outcome.value,
        f"{p.classification.confidence:.2f}", p.box.coco_name,
        f"{p.box.coco_conf:.2f}", p.constraints.summary, _seg_cell(p),
    ] for i, p in enumerate(scene.predictions)]

    c = scene.counts()
    summary = (
        f"**{len(scene.predictions)} detections** — "
        f"🟢 {c['identified']} identified · "
        f"🟠 {c['abstracted']} abstracted · "
        f"🔴 {c['unknown']} unknown · "
        f"⬜ {c['rejected']} rejected (constraint)"
    )
    if use_seg:
        s = scene.seg_counts()
        summary += (
            f"\n\n**Segmentation cross-check** — "
            f"✅ {s['confirm']} confirmed · "
            f"➖ {s['neutral']} neutral · "
            f"⚠️ {s['flag']} flagged (paths disagree) · "
            f"❌ {s['conflict']} conflict (rejected)"
        )

    # Segmentation overlay + legend (or clear them when segmentation is off).
    if use_seg and scene.seg_result is not None:
        seg_img = segmentation_overlay(image, scene.seg_result)
        seg_legend = seg_legend_html(scene.seg_result)
    else:
        seg_img, seg_legend = None, ""

    choices = [f"{i}: {p.classification.label}" for i, p in enumerate(scene.predictions)]
    first = choices[0] if choices else None
    tree = _tree(scene.predictions[0] if scene.predictions else None)

    analyze.last_scene = scene  # stash for the highlight callback
    return (annotated, summary, rows, tree,
            gr.update(choices=choices, value=first), seg_img, seg_legend)


def highlight(selection: str):
    scene = getattr(analyze, "last_scene", None)
    if scene is None or not selection:
        return _tree(None)
    idx = int(selection.split(":")[0])
    idx = min(idx, len(scene.predictions) - 1)
    return _tree(scene.predictions[idx])


def _tree(pred):
    return taxonomy_html(TAXONOMY, pred)


# --------------------------------------------------------------------------- #
#  Layout                                                                      #
# --------------------------------------------------------------------------- #
def build() -> gr.Blocks:
    with gr.Blocks(title="Hierarchical Perception") as demo:
        gr.Markdown(
            "# Hierarchical Object Perception for Autonomous Driving\n"
            "Novel objects are not dropped — the system **abstracts up the "
            "taxonomy** until it reaches a confident, *safety-useful* level "
            "(bounded by the 🛡 floor, so it never becomes paranoid), then "
            "**validates** each detection against physical/semantic context.\n\n"
            "Enabling **segmentation cross-validation 🖇** adds a second, "
            "independent perception path: a dense open-vocabulary segmenter "
            "labels every pixel and each box is checked against it — "
            "corroborating plausible detections (✅) and rejecting implausible "
            "ones like a *car sitting on sky pixels* (❌)."
        )
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 1 · Input")
                source = gr.Dropdown(
                    choices=[(s.name, s.id) for s in datasets.list_sources()],
                    value="road_anomaly", label="Dataset (lazy-streamed)",
                )
                n_samples = gr.Slider(1, 24, value=8, step=1, label="Samples to fetch")
                load_btn = gr.Button("Load samples", variant="secondary")
                status = gr.Markdown()
                gallery = gr.Gallery(label="Samples — click one", columns=4, height=220)
                image = gr.Image(label="Current image", type="numpy")

                gr.Markdown("### 2 · Settings")
                mode = gr.Radio(
                    choices=list(MODE_LABELS.keys()),
                    value=list(MODE_LABELS.keys())[0], label="Mode",
                )
                det_conf = gr.Slider(0.05, 0.9, value=0.25, step=0.05,
                                     label="YOLO detection confidence")
                descend = gr.Slider(
                    0.3, 0.9, value=0.40, step=0.05,
                    label="Commit mass (↑ = abstracts sooner / more cautious)",
                )
                min_sim = gr.Slider(0.15, 0.35, value=0.20, step=0.01,
                                    label="Min CLIP similarity (below = UNKNOWN)")
                floor = gr.Checkbox(value=True, label="Enforce abstraction floor 🛡 (anti-paranoia)")
                use_seg = gr.Checkbox(
                    value=False,
                    label="Segmentation cross-validation 🖇 (2nd perception path)",
                )
                run_btn = gr.Button("Analyze", variant="primary")

            with gr.Column(scale=2):
                gr.Markdown("### 3 · Result")
                out_img = gr.Image(label="Annotated", type="numpy")
                out_summary = gr.Markdown()
                out_table = gr.Dataframe(
                    headers=["#", "label", "outcome", "conf", "yolo", "yolo_conf",
                             "constraints", "segmentation"],
                    label="Detections", wrap=True,
                )
                with gr.Accordion("Segmentation overlay (2nd path)", open=False):
                    out_seg = gr.Image(label="Semantic segmentation", type="numpy")
                    out_seg_legend = gr.HTML()
                pick = gr.Dropdown(label="Highlight object in taxonomy", choices=[])
                out_tree = gr.HTML(_tree(None))

        # wiring
        load_btn.click(load_samples, [source, n_samples], [gallery, status])
        gallery.select(pick_from_gallery, [source, n_samples], image)
        run_btn.click(
            analyze,
            [image, mode, det_conf, descend, min_sim, floor, use_seg],
            [out_img, out_summary, out_table, out_tree, pick, out_seg, out_seg_legend],
        )
        pick.change(highlight, pick, out_tree)
    return demo


if __name__ == "__main__":
    build().launch()
