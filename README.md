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

## Architecture

```
image
  └─ YOLO (ultralytics)            → boxes ("there is an object here")
       └─ per box:
            clip mode : CLIP zero-shot top-down descent over taxonomy nodes
            yolo mode : COCO→taxonomy + confidence-based abstraction
       └─ constraint validation    → reject implausible detections
  └─ annotated image + taxonomy tree showing the abstraction path
```

| File | Role |
|------|------|
| `taxonomy.yaml` | The semantic model: the tree + floors + constraints |
| `hpercept/taxonomy.py` | Tree loading, traversal, floor logic |
| `hpercept/detector.py` | YOLO wrapper (lazy model load) |
| `hpercept/classifier.py` | CLIP zero-shot over all taxonomy nodes |
| `hpercept/abstraction.py` | **Core**: hierarchical descent + floor fallback |
| `hpercept/constraints.py` | Physical/semantic context validation |
| `hpercept/datasets.py` | Lazy, streaming dataset registry |
| `hpercept/pipeline.py` | Wires it all together |
| `hpercept/viz.py` | Annotated image + HTML taxonomy tree |
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
> (YOLOv8n ~6 MB, CLIP ViT-B-32 ~350 MB). The **YOLO-only** mode works without
> CLIP if disk is tight.

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

## Status

Early rough rig — end-to-end pipeline, taxonomy, abstraction floor, constraints,
lazy datasets and UI are in place. Next: real dataset-id verification for every
source, video/webcam input, and quantitative evaluation on CODA.
