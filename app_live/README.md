# Live video perception dashboard (standalone)

Runs the two-path pipeline (YOLO+CLIP hierarchical abstraction + CLIPSeg
cross-validation) **frame by frame over video** and shows it live:

- **left** — the annotated video (boxes coloured by outcome);
- **right, top** — live KPIs (identified / abstracted / unknown / rejected,
  segmentation verdicts, throughput);
- **right, bottom** — the taxonomy tree with the descent path of the most
  important object in the current frame highlighted. **Click any box** in the
  video to focus a specific object instead (its path is tracked across frames);
  click empty space to return to the automatic (most-important) focus.

Start with a public warm-up clip, then load your own footage. It is a local app:
a small FastAPI server does the inference and streams annotated frames + data to
the browser over Server-Sent Events (no websockets/PyAV needed); OpenCV/ffmpeg
decodes the video.

## Run

```bash
pip install -r requirements.txt            # repo root: the pipeline (torch, ultralytics, open_clip, transformers)
pip install -r app_live/requirements-app.txt
python app_live/run.py                      # opens http://127.0.0.1:8800/
```

The first processed frame is slow (models load lazily; CLIPSeg adds a one-time
compile). Turn **segmentation off** for a fast warm-up (~a few fps); turn it on
to see the cross-check verdicts (slower).

## Warm-up clips

Three public, freely-licensed clips (Wikimedia Commons) are offered in-app and
downloaded on demand to `app_live/_uploads/` (cached, git-ignored). Credits and
licenses are shown per clip and defined in `demos.json` — add your own there.

## Own video

“own video” in the toolbar uploads any local video file; or POST a server-side
path to `/load` (`path=/abs/path.mp4`).

## Performance

Per-frame YOLO+CLIP(+CLIPSeg) is heavy. Two knobs keep it fluid:

- **stride** — process 1 of every N frames (toolbar);
- **segmentation interval** — CLIPSeg runs every few processed frames.

On Apple Silicon (MPS), segmentation-off runs at a handful of fps; with
segmentation on it is a slideshow-paced demonstration, not real-time.

## Specificity (why green is rare)

The **specificity** selector maps to the abstraction operating point:

- **Safe (paper)** — the calibrated default (`temperature=0.06`,
  `commit_mass=0.40`). When leaf probability mass is split across similar
  categories (Sedan / SUV / Bus …) it abstracts to the common ancestor
  (orange "Vehicle") rather than guess, so a concrete green *identified*
  leaf is deliberately rare on real footage. This is the paper's result.
- **Balanced / Specific (demo)** — sharpen the softmax and lower the commit
  bar so more objects descend to a leaf (green). This trades a little safety
  for specificity and exists to *show* that trade-off live; it does not
  change the pipeline defaults (the presets are passed as `/stream` args).

## Packaging for a GitHub Release (TODO)

The intended distribution is a downloadable standalone build. Sketch:

```bash
pip install pyinstaller
pyinstaller --name hpercept-live --add-data "app_live/static:static" \
  --add-data "app_live/demos.json:." --collect-all ultralytics \
  --collect-all open_clip --collect-all transformers app_live/run.py
```

Torch/transformers make the bundle large; a per-OS build in CI is the practical
path. Tracked in issue #4.
