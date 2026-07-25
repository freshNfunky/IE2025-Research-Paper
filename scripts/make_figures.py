"""Generate paper-ready figures for the intermediate status report.

For each detection we render a two-panel figure:
  left  : the frame with the selected bounding box highlighted
  right : the taxonomy decision path, expanded only along the descent, with the
          per-node probability mass (the "confidence values") and the safety
          floor marked -- so one can see exactly where the system abstracted and
          why an object became UNKNOWN.

Plus summary charts across the sampled images.

Usage:
    python scripts/make_figures.py [source_id] [n_images]
Outputs into figures/ (created if missing).
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hpercept import datasets                       # noqa: E402
from hpercept.abstraction import Outcome            # noqa: E402
from hpercept.pipeline import get_pipeline          # noqa: E402
from hpercept.taxonomy import Node                  # noqa: E402

OUT = REPO / "figures"
OUT.mkdir(exist_ok=True)

OUTCOME_COLOR = {
    Outcome.IDENTIFIED: "#2ecc71",
    Outcome.ABSTRACTED: "#f39c12",
    Outcome.UNKNOWN: "#e74c3c",
}
REJECT_COLOR = "#7f8c8d"


def color_for(pred) -> str:
    if pred.rejected:
        return REJECT_COLOR
    return OUTCOME_COLOR[pred.classification.outcome]


# --------------------------------------------------------------------------- #
#  Taxonomy decision-path panel                                               #
# --------------------------------------------------------------------------- #
def _display_nodes(root: Node, path_names: set[str]):
    """DFS order, expanding a node's children only if it lies on the path."""
    rows: list[tuple[Node, int]] = []

    def rec(node: Node, depth: int):
        rows.append((node, depth))
        if node.name in path_names:
            for c in node.children:
                rec(c, depth + 1)

    rec(root, 0)
    return rows


def draw_tree_panel(ax, taxonomy, pred):
    cls = pred.classification
    path_names = {n.name for n in cls.path}
    reported = cls.node.name
    accent = color_for(pred)
    rows = _display_nodes(taxonomy.root, path_names)

    n = len(rows)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, n + 1)
    ax.axis("off")

    for i, (node, depth) in enumerate(rows):
        y = n - i
        x = 0.3 + depth * 0.85
        mass = cls.node_mass.get(node.name, 0.0)
        on_path = node.name in path_names
        is_reported = node.name == reported

        # connector to parent row (visual guide)
        if depth > 0:
            ax.plot([x - 0.4, x - 0.05], [y, y], color="#cccccc", lw=0.8, zorder=1)

        # node chip
        face = accent if is_reported else ("#2c3e50" if on_path else "#ecf0f1")
        txtcol = "white" if (is_reported or on_path) else "#7f8c8d"
        weight = "bold" if (is_reported or on_path) else "normal"
        label = node.name + ("  ◆" if node.floor else "")  # black diamond
        ax.add_patch(FancyBboxPatch(
            (x, y - 0.32), 3.1, 0.64, boxstyle="round,pad=0.02,rounding_size=0.1",
            facecolor=face, edgecolor="none", zorder=2))
        ax.text(x + 0.12, y, label, va="center", ha="left", fontsize=8.5,
                color=txtcol, fontweight=weight, zorder=3)

        # mass bar + value
        bx = x + 3.35
        ax.add_patch(Rectangle((bx, y - 0.18), 2.4, 0.36, facecolor="#f0f0f0",
                               edgecolor="none", zorder=2))
        ax.add_patch(Rectangle((bx, y - 0.18), 2.4 * max(0.0, min(1.0, mass)), 0.36,
                               facecolor=accent if on_path else "#bdc3c7", zorder=3))
        ax.text(bx + 2.5, y, f"{mass:.2f}", va="center", ha="left", fontsize=8,
                color="#333", zorder=3)

    # header + verdict annotation
    o = cls.outcome
    verdict = {
        Outcome.IDENTIFIED: "committed to a specific leaf",
        Outcome.ABSTRACTED: "ambiguous below here -> abstracted to safety floor",
        Outcome.UNKNOWN: "mass split above the floor -> UNKNOWN OBSTACLE",
    }[o]
    ax.set_title("Taxonomy decision path  (node = probability mass)",
                 fontsize=10, loc="left")
    ax.text(0.3, n + 0.6, "◆ = safety floor (abstraction never stops above it)",
            fontsize=8, color="#555")
    ax.text(0.3, 0.2, f"→ {verdict}", fontsize=8.5, style="italic",
            color=accent, transform=ax.transData)


def draw_image_panel(ax, image, scene, sel_idx, zoom=True):
    # Draw ONLY the detection this figure explains, and (optionally) zoom to it
    # with context, so the box, the label and the taxonomy path on the right
    # unambiguously refer to the same object -- even when the box is small.
    ax.imshow(image)
    ax.axis("off")
    p = scene.predictions[sel_idx]
    x1, y1, x2, y2 = p.box.xyxy
    c = color_for(p)
    ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, fill=False,
                           edgecolor=c, linewidth=3,
                           linestyle="-" if not p.rejected else "--"))
    cls = p.classification
    tag = (f"{cls.label}  (conf {cls.confidence:.2f}, "
           f"sim {cls.top_sim:.2f}, imp {p.importance:.2f})")
    ax.text(x1, max(0, y1 - 8), tag, fontsize=8.5, color="white",
            va="bottom", ha="left",
            bbox=dict(boxstyle="round,pad=0.25", fc=c, ec="none"))
    ax.set_title(f"YOLO: {p.box.coco_name} ({p.box.coco_conf:.2f})  →  "
                 f"{cls.outcome.value.upper()}",
                 fontsize=10, loc="left")
    if zoom:
        H, W = image.shape[:2]
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        rx = max((x2 - x1) * 1.7, 170)   # context around the box; min for tiny boxes
        ry = max((y2 - y1) * 1.7, 170)
        r = max(rx, ry)                  # keep it square-ish so nothing squashes
        ax.set_xlim(max(0, cx - r), min(W, cx + r))
        ax.set_ylim(min(H, cy + r), max(0, cy - r))  # inverted for image coords


def make_example(taxonomy, image, scene, sel_idx, out_path):
    # Stacked (portrait) layout: image on top, decision graph below. Reads well
    # at single-column width, unlike the very wide side-by-side variant.
    fig, (axi, axt) = plt.subplots(2, 1, figsize=(7.2, 8.8),
                                   gridspec_kw={"height_ratios": [1.0, 1.15]})
    draw_image_panel(axi, image, scene, sel_idx, zoom=True)
    draw_tree_panel(axt, taxonomy, scene.predictions[sel_idx])
    fig.tight_layout()
    fig.savefig(out_path, dpi=170, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- #
#  Summary charts                                                             #
# --------------------------------------------------------------------------- #
def make_summary(all_preds, out_path):
    counts = {"identified": 0, "abstracted": 0, "unknown": 0}
    rejected = 0
    confs = {"identified": [], "abstracted": [], "unknown": []}
    for p in all_preds:
        o = p.classification.outcome.value
        counts[o] += 1
        confs[o].append(p.classification.confidence)
        if p.rejected:
            rejected += 1

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    labels = ["identified", "abstracted", "unknown"]
    cols = [OUTCOME_COLOR[Outcome(l)] for l in labels]
    ax1.bar(labels, [counts[l] for l in labels], color=cols)
    ax1.bar(["rejected\n(constraint)"], [rejected], color=REJECT_COLOR)
    ax1.set_title("Detection outcomes across sampled frames")
    ax1.set_ylabel("count")
    for i, l in enumerate(labels):
        ax1.text(i, counts[l], str(counts[l]), ha="center", va="bottom")

    for l in labels:
        if confs[l]:
            ax2.scatter([l] * len(confs[l]), confs[l],
                        color=OUTCOME_COLOR[Outcome(l)], alpha=0.6, s=30)
    ax2.set_ylim(0, 1)
    ax2.set_title("Reported-level confidence (subtree mass) by outcome")
    ax2.set_ylabel("confidence")
    fig.tight_layout()
    fig.savefig(out_path, dpi=170, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- #
def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "road_anomaly"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    print(f">>> streaming {n} images from '{src}'", flush=True)
    samples = datasets.get_source(src).load(n)
    print(f">>> got {len(samples)} images; running pipeline", flush=True)

    pipe = get_pipeline()
    tax = pipe.taxonomy
    all_preds = []
    made = 0
    for si, s in enumerate(samples):
        scene = pipe.run(s.image, mode="clip")
        all_preds.extend(scene.predictions)
        for di, p in enumerate(scene.predictions):
            o = p.classification.outcome.value
            name = f"ex_{src}_{si:02d}_{di}_{o}.png"
            make_example(tax, s.image, scene, di, OUT / name)
            made += 1
            print(f"    wrote {name}  [{p.classification.label}]", flush=True)

    if all_preds:
        make_summary(all_preds, OUT / f"summary_{src}.png")
        print(f">>> wrote summary_{src}.png", flush=True)
    print(f">>> DONE: {made} example figures for {len(all_preds)} detections", flush=True)


if __name__ == "__main__":
    main()
