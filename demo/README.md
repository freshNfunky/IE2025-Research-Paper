# Interactive perception demo (static)

A self-contained, **fully static** showcase of the hierarchical perception
pipeline (YOLO+CLIP hierarchical abstraction + CLIPSeg cross-validation). It
runs anywhere you can serve files over HTTP — a plain static or PHP web space,
the same as a krpano tour. **No Python or server logic at serve time.**

## Contents

```
demo/
  index.html          self-contained viewer (inline CSS + JS)
  data/
    scenes.json       all detections: taxonomy descent, constraints, seg verdict
    scene_NN.jpg      the frame
    scene_NN_seg.jpg  the dense segmentation overlay
```

## What it shows

- Pick a scene from the gallery.
- Boxes are drawn from the JSON, coloured by **outcome** (identified / abstracted
  / unknown / rejected) or by **segmentation verdict** (confirm / flag / conflict).
- Toggle the **segmentation overlay**.
- Click a detection to see:
  - its **Detail** (label, outcome, confidence, detector guess, constraints,
    segmentation cross-check verdict),
  - the full **taxonomy tree** with the descent **path highlighted** and per-node
    probability **mass** bars (as in the paper, Fig. 2; safety floors marked ◆),
  - a **flat list vs. hierarchical** comparison — a flat classifier forces a
    specific/wrong leaf or drops the object, while the hierarchy abstracts to a
    safe level.

> This static demo is a teaser; the convincing **live video** dashboard is
> tracked as a standalone app in issue #4.

## Deploy

Copy the whole `demo/` folder to your web space, e.g. under `…/project/perception/`,
and open `index.html`. Relative paths (`data/…`) keep it portable to any
subfolder. It must be served over `http(s)://` (not opened as a `file://` path),
because the viewer fetches `data/scenes.json`.

Local preview:

```bash
cd demo && python3 -m http.server 8777   # then open http://localhost:8777
```

## Regenerate the data

The assets are produced offline from the pipeline:

```bash
python scripts/export_demo.py road_anomaly 12 8   # source, images to stream, max scenes
```

This writes `demo/data/`. Downscaling and the JSON schema are defined in
`scripts/export_demo.py`.
