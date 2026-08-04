---
license: cc-by-nc-4.0
tags:
  - autonomous-driving
  - object-detection
  - open-set-recognition
  - functional-safety
  - neuro-symbolic
pipeline_tag: object-detection
---

# HOWC : hierarchical taxonomic perception for novel road objects

A training-free layer that turns a flat object detector into a hierarchical,
open-set one. Each detection is classified by **taxonomic abstraction**: the most
specific level the evidence safely supports, or an explicit **UNKNOWN OBSTACLE**,
never a confident wrong leaf.

Paper (open access): *Hierarchical Taxonomic Abstraction for the Safe Handling of
Novel Objects in Autonomous Driving Perception*, F. Schaller,
[doi:10.5281/zenodo.21593472](https://doi.org/10.5281/zenodo.21593472).
Source & full history: <https://github.com/freshNfunky/IE2025-Research-Paper>.

## Why it is different

A flat detector returns one fixed class or nothing. On an untrained object (a
horse-drawn carriage, an overloaded truck) it must mislabel it or drop it, both
unsafe. HOWC abstracts up a taxonomy to a still-useful category
(… → Truck → Transport Vehicle → Vehicle), bounded by a per-branch **safety
floor** so it never collapses into a useless "Object"; below the floor it flags an
explicit **UNKNOWN OBSTACLE** with an inspectable decision path.

## Honest scope

- Not new weights, and not a closed-set-accuracy win: on COCO mAP a trained YOLO
  is more accurate. The contribution is the **taxonomic abstraction layer** over
  open-vocabulary (CLIP) features.
- Where it wins: on known objects, **0% categorical (off-branch) errors** with
  ~24% calibrated abstention, vs a flat head's ~53% off-branch errors.
- On **out-of-vocabulary** objects (v3, ground-truth leave-classes-out on COCO,
  n=235): a flat closed head gives a confident **wrong specific label 100%** of the
  time (37% in the wrong super-category); this layer gives **0%** confident wrong
  specific labels and **safely handles 94%** (a correct super-category, or an
  explicit UNKNOWN). Honest caveat: the win is **safety, not specificity**, it
  recovers the correct super-category only 26% of the time and conservatively flags
  the rest (69%) as UNKNOWN.
- Training-free (pretrained YOLO + CLIP zero-shot). First run downloads weights
  (~360 MB).

## Run it locally

This repository is self-contained (code + taxonomy + a Gradio app):

```bash
pip install -r requirements.txt
python app.py            # Gradio UI: upload an image, see the taxonomy decision
python app.py --share    # same, but also prints a temporary public URL (~72h)
```

## License

CC BY-NC 4.0, matching the paper.
