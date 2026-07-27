"""Standalone live-video perception dashboard — local server (Issue #4).

Runs the two-path pipeline (YOLO+CLIP hierarchical abstraction + CLIPSeg
cross-validation) frame-by-frame over a video and streams the annotated frame
plus per-frame KPIs and the taxonomy descent to a browser dashboard.

Transport is Server-Sent Events (SSE) — built into FastAPI, no websockets/PyAV
needed. One stream carries everything, perfectly frame-synced:

    data: {"frame": "<base64 jpeg>", "w":…, "h":…,
           "detections":[…], "kpis":{…}, "focus":{…taxonomy path…}, "fps":…}

Video is decoded with OpenCV (ffmpeg under the hood). Because YOLO+CLIP+CLIPSeg
per frame is heavy, we process 1 of every ``stride`` frames and can run
segmentation on an interval; the dashboard plays results as they arrive.

Run:  python app_live/run.py     (launcher opens the dashboard)
      or: uvicorn app_live.server:app --port 8800
"""
from __future__ import annotations

import base64
import json
import time
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import sys
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hpercept.pipeline import get_pipeline                       # noqa: E402
from hpercept.abstraction import flat_classify                   # noqa: E402
from hpercept.viz import COLORS, REJECTED_COLOR, segmentation_overlay  # noqa: E402

HERE = Path(__file__).resolve().parent
STATIC = HERE / "static"
UPLOADS = HERE / "_uploads"
UPLOADS.mkdir(exist_ok=True)
MAX_W = 900

app = FastAPI(title="Live Hierarchical Perception")


def _hex(t):
    return "#%02x%02x%02x" % (int(t[0]), int(t[1]), int(t[2]))


OUTCOME_HEX = {k.value: _hex(v) for k, v in COLORS.items()}
OUTCOME_HEX["rejected"] = _hex(REJECTED_COLOR)

# The current video source + processing options (single-session app).
STATE: dict = {"video": None, "stride": 3, "seg_every": 3, "segment": True}


def taxonomy_tree(node) -> dict:
    return {"name": node.name, "floor": bool(node.floor),
            "children": [taxonomy_tree(c) for c in node.children]}


def _detection(p, scale: float) -> dict:
    c = p.classification
    x1, y1, x2, y2 = p.box.xyxy
    return {
        "box": [round(x1 * scale), round(y1 * scale),
                round(x2 * scale), round(y2 * scale)],
        "label": c.label,
        "outcome": c.outcome.value,
        "is_leaf": bool(c.node.is_leaf),
        "confidence": round(c.confidence, 2),
        "importance": round(p.importance, 2),
        "rejected": bool(p.rejected),
        "seg_status": p.seg.status if p.seg else "off",
        "path": [{"name": n.name, "mass": round(c.node_mass.get(n.name, 0.0), 3),
                  "floor": bool(n.floor)} for n in c.path],
        "node_mass": {k: round(v, 3) for k, v in c.node_mass.items() if v >= 0.005},
    }


@app.get("/", response_class=HTMLResponse)
def index():
    return (STATIC / "index.html").read_text(encoding="utf-8")


@app.get("/meta")
def meta():
    pipe = get_pipeline()
    return JSONResponse({
        "outcome_colors": OUTCOME_HEX,
        "seg_marks": {"confirm": "✓", "neutral": "~", "flag": "⚠",
                      "conflict": "✗", "off": ""},
        "taxonomy": taxonomy_tree(pipe.taxonomy.root),
    })


def _load_demos() -> list[dict]:
    f = HERE / "demos.json"
    if not f.exists():
        return []
    return json.loads(f.read_text(encoding="utf-8")).get("demos", [])


@app.get("/demos")
def demos():
    """Curated public warm-up clips the user can try before uploading their own."""
    out = []
    for d in _load_demos():
        cached = (UPLOADS / f"demo_{d['id']}{d.get('ext', '.mp4')}").exists()
        out.append({k: d[k] for k in ("id", "name", "credit", "license")
                    if k in d} | {"cached": cached})
    return {"demos": out}


def _fetch_demo(demo_id: str) -> Optional[str]:
    """Download a demo clip to the local cache (once) and return its path."""
    import urllib.request
    d = next((x for x in _load_demos() if x["id"] == demo_id), None)
    if d is None:
        return None
    dst = UPLOADS / f"demo_{demo_id}{d.get('ext', '.mp4')}"
    if not dst.exists():
        req = urllib.request.Request(d["url"], headers={"User-Agent": "hpercept-demo"})
        with urllib.request.urlopen(req, timeout=60) as r, open(dst, "wb") as f:
            f.write(r.read())
    return str(dst)


@app.post("/load")
async def load(file: Optional[UploadFile] = File(default=None),
               path: str = Form(default=""), demo: str = Form(default="")):
    """Set the video source: an uploaded file, a local path, or a demo id."""
    if demo:
        p = _fetch_demo(demo)
        if p is None:
            return JSONResponse({"error": f"unknown demo: {demo}"}, status_code=400)
        STATE["video"] = p
    elif file is not None:
        dst = UPLOADS / file.filename
        dst.write_bytes(await file.read())
        STATE["video"] = str(dst)
    elif path:
        if not Path(path).is_file():
            return JSONResponse({"error": f"not a file: {path}"}, status_code=400)
        STATE["video"] = path
    else:
        return JSONResponse({"error": "provide a file, path or demo"}, status_code=400)
    cap = cv2.VideoCapture(STATE["video"])
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return {"video": STATE["video"], "frames": frames, "fps": round(fps, 1)}


def _sse(payload: dict) -> str:
    return "data: " + json.dumps(payload) + "\n\n"


def _stream_gen(stride: int, segment: bool, seg_every: int):
    """Blocking generator (runs in a threadpool via StreamingResponse)."""
    video = STATE["video"]
    if not video:
        yield "event: error\ndata: {\"error\":\"no video loaded\"}\n\n"
        return
    pipe = get_pipeline()
    cap = cv2.VideoCapture(video)
    seg_cache = None
    i = 0
    try:
        while True:
            ok, bgr = cap.read()
            if not ok:
                break
            i += 1
            if stride > 1 and (i % stride) != 0:
                continue
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            h0, w0 = rgb.shape[:2]
            scale = min(1.0, MAX_W / float(w0))
            if scale < 1.0:
                rgb = cv2.resize(rgb, (int(w0 * scale), int(h0 * scale)),
                                 interpolation=cv2.INTER_AREA)
            t0 = time.time()
            do_seg = segment and (i // max(1, stride)) % max(1, seg_every) == 0
            scene = pipe.run(rgb, mode="clip", segment=do_seg)

            # Raw frame (boxes/labels are drawn client-side so they can be toggled).
            def _jpg(arr):
                _, b = cv2.imencode(".jpg", cv2.cvtColor(arr, cv2.COLOR_RGB2BGR),
                                    [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                return base64.b64encode(b).decode("ascii")

            frame_b64 = _jpg(rgb)
            seg_b64 = None
            if do_seg and scene.seg_result is not None:
                seg_b64 = _jpg(segmentation_overlay(rgb, scene.seg_result, alpha=0.55))

            dets = []
            for p in scene.predictions:
                d = _detection(p, 1.0)
                # Flat baseline on the same CLIP features (arg-max leaf + reject).
                feat = pipe.clip.image_features(p.box.crop(rgb))
                fl = flat_classify(feat, pipe.taxonomy, pipe.clip,
                                   reject_threshold=0.5)
                d["flat"] = {"leaf": fl.leaf.name, "prob": round(fl.prob, 2),
                             "accepted": bool(fl.accepted)}
                d["novel"] = pipe.taxonomy.by_coco(p.box.coco_name) is None
                dets.append(d)

            focus_idx = max(range(len(scene.predictions)),
                            key=lambda k: scene.predictions[k].importance,
                            default=-1) if scene.predictions else -1
            counts = scene.counts()
            dt = time.time() - t0
            yield _sse({
                "frame_idx": i,
                "frame": frame_b64,
                "seg_frame": seg_b64,
                "w": rgb.shape[1], "h": rgb.shape[0],
                "detections": dets,
                "focus_idx": focus_idx,
                "kpis": {**counts, "seg": scene.seg_counts() if do_seg else {},
                         "seg_on": do_seg},
                "fps": round(1.0 / dt, 2) if dt > 0 else 0,
            })
    finally:
        cap.release()
    yield "event: end\ndata: {}\n\n"


@app.get("/stream")
def stream(stride: int = 3, segment: int = 1, seg_every: int = 3):
    gen = _stream_gen(stride=max(1, stride), segment=bool(segment),
                      seg_every=max(1, seg_every))
    return StreamingResponse(gen, media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache",
                                      "X-Accel-Buffering": "no"})


# Serve any other static assets (css/js) if we split them out later.
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
