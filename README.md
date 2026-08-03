# Hierarchical Object Perception for Autonomous Driving

Object detection for driving scenes (YOLO-style), but with a twist: instead of a
**flat class list**, objects live in a **hierarchical taxonomy**. When a novel
or ambiguous object appears — a horse-drawn carriage, an unknown work vehicle —
the system does **not** drop it or force a wrong leaf label. It **abstracts up
the taxonomy** until it reaches a category that is still confident *and*
safety-useful, then **validates** the detection against physical/semantic
context.

This is a reference implementation of the runtime idea in:

> F. Schaller, *The Role of Semantic Models in Constraining Pattern Recognition
> in Modern AI Systems*, Intelligent Environments 2025 (IOS Press),
> doi:10.3233/AISE250023.

## The two key ideas

1. **Abstraction fallback (don't fall into the void).**
   A detection descends the taxonomy top-down. At each level it only commits one
   step deeper if the evidence is decisive. If it becomes ambiguous, it *stops* —
   reporting the last confident, coarser category (e.g. `Truck` → `Transport
   Vehicle`) rather than a made-up leaf.

2. **Abstraction floor (don't become paranoid).**
   The more abstract a category, the more trivially true it is — labelling
   everything `Object` would make a planner brake for the whole world. So every
   safety-actionable node carries a `floor` flag (🛡: `Vehicle`, `Living Being`,
   `Static Object`). Abstraction may never stop *above* the nearest floor. If
   even the floor is not confident, the detection becomes an explicit,
   **localized `UNKNOWN OBSTACLE`** handed to a conservative policy — not a
   useless generic bucket.

Plus a **context-validation layer** that rejects physically implausible
detections (the paper's "car flying above the clouds" example): size and
position plausibility per category, inherited down the taxonomy.

3. **Segmentation cross-validation (a second, independent perception path).**
   Alongside the box path, an **open-vocabulary semantic segmenter** (CLIPSeg)
   densely labels every pixel into its own stuff/things taxonomy
   (`segmentation.yaml`: road, sidewalk, vehicle, person, vegetation, sky, …).
   Each box is then cross-checked against it: a detection is **corroborated**
   when the pixels under it agree with its taxonomy branch, and **rejected** when
   they contradict it — the *data-driven* version of the position gate (a
   `Vehicle` box sitting on `sky` pixels is the classic flying-car false
   positive). Because the two paths come from different model families
   (YOLO+CLIP vs. CLIPSeg), their agreement is genuine evidence. Safety-first:
   an `UNKNOWN OBSTACLE` is never vetoed by segmentation.

## Architecture

```
image
  ├─ YOLO (ultralytics)            → boxes ("there is an object here")
  │    └─ per box:
  │         clip mode : CLIP zero-shot top-down descent over taxonomy nodes
  │         yolo mode : COCO→taxonomy + confidence-based abstraction
  │    └─ constraint validation    → reject implausible detections
  └─ CLIPSeg (optional 2nd path)   → dense pixel labels (stuff/things)
       └─ per box: cross-check region vs. taxonomy branch (confirm / conflict)
  └─ annotated image + segmentation overlay + taxonomy tree
```

| File | Role |
|------|------|
| `taxonomy.yaml` | The semantic model: the tree + floors + constraints |
| `segmentation.yaml` | Segmentation stuff/things taxonomy (2nd path) |
| `hpercept/taxonomy.py` | Tree loading, traversal, floor logic |
| `hpercept/detector.py` | YOLO wrapper (lazy model load) |
| `hpercept/classifier.py` | CLIP zero-shot over all taxonomy nodes |
| `hpercept/segmenter.py` | CLIPSeg open-vocab segmenter (lazy model load) |
| `hpercept/abstraction.py` | **Core**: hierarchical descent + floor fallback |
| `hpercept/constraints.py` | Physical/semantic + segmentation validation |
| `hpercept/datasets.py` | Lazy, streaming dataset registry |
| `hpercept/pipeline.py` | Wires it all together |
| `hpercept/viz.py` | Annotated image + overlay + HTML taxonomy tree |
| `app.py` | Gradio UI |

## Datasets (lazy, low-disk)

Nothing is downloaded up front. Pick a set in the dropdown and fetch N samples —
only those images are streamed (Hugging Face streaming mode).

| Set | Purpose |
|-----|---------|
| **CODA** | Real-world **corner cases** / unknowns — the primary novelty set |
| **BDD100K** | Large **known** baseline for contrast |
| **Road Anomaly** | Unknown objects on the road (animals, odd vehicles) |
| **Local folder** | Your own images / extracted video frames (`data/samples/`) |

> Because the classification is **training-free** (pretrained YOLO + CLIP
> zero-shot), these sets are used for *evaluation/demo*, not training.

## Setup

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Heaviest dependency is PyTorch (~2 GB). Models download lazily on first use
> (YOLOv8n ~6 MB, CLIP ViT-B-32 ~350 MB, CLIPSeg ~150 MB). The **YOLO-only** mode
> works without CLIP if disk is tight, and segmentation is off by default (its
> weights are only fetched when you enable the cross-check).

## Run

```bash
python app.py            # Gradio UI at http://127.0.0.1:7860
python smoke_test.py     # offline logic check, no model download
```

## Tuning the behaviour (live in the UI)

- **Descend threshold** — how decisive evidence must be to go one level deeper.
  ↑ = abstracts sooner (more cautious / "paranoid"), ↓ = dives to leaves eagerly.
- **Enforce abstraction floor 🛡** — toggle the anti-paranoia limit on/off to see
  the difference between a bounded `UNKNOWN OBSTACLE` and collapse to `Object`.
- **Min CLIP similarity** — refuse to commit on weak visual evidence.
- **Segmentation cross-validation 🖇** — turn on the second perception path; each
  detection gets a ✅ confirm / ➖ neutral / ❌ conflict verdict (conflicts are
  rejected), plus a segmentation overlay.

## 3D mode (open-world spike)

> Experimental, on branch `spike/open-world-classifier`. See
> [docs/spikes/open_world_feasibility.md](docs/spikes/open_world_feasibility.md).

The 2D pipeline cannot tell a real object from a flat 2D depiction (a car on a
billboard, a poster, painted livery). A **3D mode** adds a depth signal and, per
detection, a **flatness / foreground test**: a flat panel has near-planar depth
(low internal relief once a plane is removed), a real object has relief.

- **Depth source.** Spike uses **monocular** depth (Depth-Anything), so it runs
  on the existing images with no LiDAR dataset. Production would feed the *same*
  test from **LiDAR** projected into the image (metric depth); see
  `hpercept/openworld/lidar.py` (stub).
- **Verdicts per detection:** `3d` (assessable, has relief) · `flat` (assessable,
  near-planar → likely a 2D false positive) · `n/a` (too small / distant to
  judge — the scale limit; metric LiDAR would extend the assessable range).

Run:

```bash
python scripts/depth3d_spike.py 6     # writes figures/depth3d_*.png
```

**Findings (honest).** The depth map cleanly separates foreground from
background, and large upright objects read as `3d` while small/distant ones are
correctly held `n/a` (see `figures/depth3d_04.png`: a foreground truck+trailer is
`3d`, distant cars are `n/a`). Limits: monocular depth is *relative*, and the
relief metric is shape-sensitive (a compact animal can read low-relief); the
dataset has no billboard to demonstrate a true `flat` rejection. A reliable
billboard/flatness test needs **metric** depth (LiDAR) and better geometry. This
is a promising capability, not a finished one.

### YOLO+ : open-world proposals + hierarchical classification

The product idea is **YOLO+**: extend a detector with the hierarchical taxonomic
classifier so untrained objects still get a safe coarse label or an explicit
UNKNOWN. A class-agnostic proposer (MobileSAM via ultralytics) supplies boxes for
things the closed set misses:

```bash
python scripts/yoloplus_spike.py 8    # YOLO vs MobileSAM + hierarchical labels
```

**Findings (honest).** MobileSAM hugely increases recall (19 YOLO detections vs
148 extra regions on 8 images) but over-proposes background (sky, grass, walls).
The UNKNOWN gate filters ~76% as UNKNOWN; the rest is still noisy (vegetation
labelled `Living Being`). Class-agnostic proposals therefore need an objectness /
**geometry filter** (the depth mode above) to be usable. Synthesis of the three
open-world spikes: recall (SAM) + precision (depth/geometry) + semantics
(hierarchy) are complementary; the hierarchy is the differentiator and already
works. See [docs/spikes/open_world_feasibility.md](docs/spikes/open_world_feasibility.md).

**HuggingFace.** The stack is HF-publishable as-is (CLIP, Depth-Anything,
MobileSAM/YOLO are all Hub/ultralytics-hosted, fetched lazily). Intended: a HF
Space demoing YOLO+ and a model card whose novelty is the *taxonomic abstraction
layer* over open-vocabulary features, not new detector weights.

## Status

Early rough rig — end-to-end pipeline, taxonomy, abstraction floor, constraints,
lazy datasets and UI are in place. Next: real dataset-id verification for every
source, video/webcam input, and quantitative evaluation on CODA.
