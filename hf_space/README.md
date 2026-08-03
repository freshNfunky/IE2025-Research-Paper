---
title: HOWC Hierarchical Perception
emoji: 🚗
colorFrom: indigo
colorTo: green
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: cc-by-nc-4.0
tags:
  - autonomous-driving
  - object-detection
  - open-set-recognition
  - functional-safety
  - neuro-symbolic
---

# HOWC : hierarchical perception for novel road objects

Upload a road image. A detector proposes boxes, and each is classified by
**hierarchical taxonomic abstraction**: the most specific level the evidence
safely supports, or an explicit **UNKNOWN OBSTACLE** if it cannot commit. Novel
or ambiguous objects are never dropped and never given a confident wrong label.

Based on *Hierarchical Taxonomic Abstraction for the Safe Handling of Novel
Objects in Autonomous Driving Perception* (F. Schaller,
[doi:10.5281/zenodo.21593472](https://doi.org/10.5281/zenodo.21593472)).

## What is different from a normal detector

A flat detector returns **one fixed class or nothing**. On an object it was not
trained on (a horse-drawn carriage, an overloaded truck) it must mislabel it or
drop it, both unsafe. HOWC instead **abstracts up a taxonomy** to a category
that is still confident and *safety-useful* (… → Truck → Transport Vehicle →
Vehicle), bounded by a per-branch **safety floor** so it never collapses into a
useless "Object"; below the floor it emits an explicit **UNKNOWN OBSTACLE** with
a decision path you can inspect.

## Honest scope (what this is and is not)

- **Not** a new set of weights and **not** a closed-set-accuracy win: on standard
  COCO mAP a trained YOLO is more accurate. The novelty is the **taxonomic
  abstraction layer** over open-vocabulary (CLIP) features.
- Where it wins: on known objects it makes **0% categorical (off-branch) errors**
  and abstains ~24% of the time, versus a flat head's ~53% off-branch errors; on
  novel objects it produces a safe coarse label or a flagged UNKNOWN instead of a
  confident wrong leaf.
- Training-free (pretrained YOLO + CLIP zero-shot). First run downloads the
  weights (~360 MB). CPU works but is slow.

## Deploying this Space

This folder (`app.py`, `requirements.txt`, this `README.md`) plus the `hpercept/`
package and `taxonomy.yaml` from the source repo must sit at the Space root. Copy
them in (or add the repo as a dependency). Source + full paper:
<https://github.com/freshNfunky/IE2025-Research-Paper>.

## License

CC BY-NC 4.0, matching the paper.
