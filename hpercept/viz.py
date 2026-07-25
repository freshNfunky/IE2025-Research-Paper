"""Rendering: annotated image + an HTML taxonomy tree showing the fallback path.

Colour code (consistent across image boxes and the tree):
    identified  -> green   (committed to a specific leaf)
    abstracted  -> orange  (fell back to a coarser but safe node)
    unknown     -> red     (below-floor: localized UNKNOWN obstacle)
    rejected    -> gray    (failed context/constraint validation)
"""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .abstraction import Outcome
from .pipeline import Prediction, SceneResult
from .taxonomy import Node, Taxonomy

COLORS = {
    Outcome.IDENTIFIED: (46, 204, 113),
    Outcome.ABSTRACTED: (243, 156, 18),
    Outcome.UNKNOWN: (231, 76, 60),
}
REJECTED_COLOR = (127, 140, 141)


def _font(size: int = 16):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def annotate(image_rgb: np.ndarray, scene: SceneResult) -> np.ndarray:
    """Draw all predictions onto a copy of the image."""
    img = Image.fromarray(image_rgb.copy())
    draw = ImageDraw.Draw(img)
    font = _font(16)

    for pred in scene.predictions:
        color = _color_for(pred)
        x1, y1, x2, y2 = pred.box.xyxy
        width = 2 if pred.rejected else 3
        draw.rectangle([x1, y1, x2, y2], outline=color, width=width)

        label = _label_for(pred)
        tw = draw.textlength(label, font=font)
        th = 18
        ly = max(0, y1 - th)
        draw.rectangle([x1, ly, x1 + tw + 8, ly + th], fill=color)
        draw.text((x1 + 4, ly + 1), label, fill=(0, 0, 0), font=font)

    return np.array(img)


def _color_for(pred: Prediction):
    if pred.rejected:
        return REJECTED_COLOR
    return COLORS.get(pred.classification.outcome, (52, 152, 219))


def _label_for(pred: Prediction) -> str:
    c = pred.classification
    tag = "REJECT " if pred.rejected else ""
    return f"{tag}{c.label} {c.confidence:.2f}"


# --------------------------------------------------------------------------- #
#  HTML taxonomy tree                                                          #
# --------------------------------------------------------------------------- #
def taxonomy_html(
    taxonomy: Taxonomy,
    highlight: Prediction | None = None,
) -> str:
    """Render the taxonomy as a nested tree; highlight one prediction's path."""
    path_names = set()
    reported = None
    outcome = None
    if highlight is not None:
        path_names = {n.name for n in highlight.classification.path}
        reported = highlight.classification.node.name
        outcome = highlight.classification.outcome

    rgb = COLORS.get(outcome, (52, 152, 219)) if outcome else (52, 152, 219)
    accent = f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"

    def render(node: Node) -> str:
        on_path = node.name in path_names
        is_reported = node.name == reported
        floor_badge = " 🛡" if node.floor else ""
        style = "padding:1px 6px;border-radius:5px;margin:1px 0;display:inline-block;"
        if is_reported:
            style += f"background:{accent};color:#000;font-weight:700;"
        elif on_path:
            style += "background:#2c3e50;color:#fff;"
        else:
            style += "color:#7f8c8d;"
        html = f'<div style="margin-left:14px;"><span style="{style}">{node.name}{floor_badge}</span>'
        if node.children:
            html += "".join(render(c) for c in node.children)
        html += "</div>"
        return html

    legend = (
        '<div style="font-size:12px;margin-bottom:6px;">'
        "🛡 = safety floor (abstraction never stops above it) &nbsp;|&nbsp; "
        f'<span style="color:{accent};font-weight:700;">■</span> reported level'
        "</div>"
    )
    return f'<div style="font-family:monospace;font-size:13px;">{legend}{render(taxonomy.root)}</div>'
