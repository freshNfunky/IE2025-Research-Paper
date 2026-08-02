# Outreach copy (arXiv + Show HN + Reddit)

Fill the placeholder `<HF_SPACE_URL>` once the Space is deployed. Honest
positioning throughout: the novelty is the taxonomic abstraction layer and the
safety behaviour, not closed-set accuracy.

---

## 1. arXiv

**Title:** Hierarchical Taxonomic Abstraction for the Safe Handling of Novel
Objects in Autonomous Driving Perception

**Categories:** cs.CV (primary), cs.RO, cs.AI

**Abstract.**
Object detectors for autonomous driving classify against a flat list of
categories. When a scene contains an object that fits none of them, an overloaded
rural truck, a horse trailer, a horse-drawn carriage, a flat classifier must
either force a confident but wrong label or drop the object entirely, and both are
unsafe. We replace the flat list with a hierarchical taxonomy and add a runtime
abstraction mechanism: each detection descends the taxonomy only as far as the
visual evidence justifies and otherwise falls back to a coarser, still
safety-relevant category. A per-branch safety floor bounds this fallback so the
system never collapses into a useless generic label; below the floor it emits an
explicit, localized UNKNOWN OBSTACLE with an inspectable decision path. Using a
pretrained detector and CLIP zero-shot scoring over the taxonomy leaves
(training-free), we run a fair head-to-head against a flat baseline on a
real-world corner-case set. On out-of-taxonomy objects the hierarchy is handled
safely in 100% of cases (abstracted or flagged) versus 0% for the flat baseline;
on known objects it makes zero categorical (off-branch) errors with calibrated
abstention, where a flat head is off-branch 53% of the time. We frame the method
as a semantic safety argument for perception in the SOTIF regime, state its
limitations honestly (novelty is a label-space proxy, no box-level ground truth,
monocular/appearance signals are scale-limited), and outline extensions via
semantic segmentation, LiDAR geometry, and Doppler/motion cues.

---

## 2. Show HN

**Title:** Show HN: YOLO+, perception that abstracts up a taxonomy instead of
guessing on unknown road objects

**Body.**
Self-driving perception classifies against a flat list of classes. When something
appears that fits no class (an overloaded truck, a horse-drawn carriage), a flat
classifier either forces a wrong label or drops the object. Both are unsafe, and
real incidents trace back to exactly this.

We built a small, training-free layer on top of a detector. Instead of a flat
list, categories form a taxonomy, and each detection is abstracted up to the most
specific level the evidence supports (... Truck, Transport Vehicle, Vehicle), or
flagged UNKNOWN if it cannot commit. A per-branch "safety floor" stops it from
over-abstracting into a useless "it is an object".

Honest results: we do not beat YOLO on COCO accuracy (CLIP zero-shot is weaker,
and slower). The point is the tail. On known objects it makes 0% categorical
errors and abstains about 24% of the time, versus a flat head's 53% off-branch
errors; on out-of-taxonomy objects it stays safe 100% of the time (abstract or
flag) versus 0% for flat.

Demo: <HF_SPACE_URL> . Paper (open access): https://doi.org/10.5281/zenodo.21593472 .
Code: https://github.com/freshNfunky/IE2025-Research-Paper .

Feedback welcome, especially on the open-world detection front-end: class-agnostic
proposals (SAM) massively over-propose, and we think geometry/LiDAR is the missing
precision filter.

---

## 3. Reddit

### r/MachineLearning

**Title:** [P] YOLO+: hierarchical taxonomic abstraction for safe handling of
novel objects (training-free, with an honest benchmark)

**Body.**
A flat classifier on an out-of-distribution object either forces a confident wrong
class or drops it. We put a hierarchical taxonomy over pretrained detection + CLIP
zero-shot: each box is scored against the taxonomy leaves, the leaf probabilities
are aggregated up the tree, and the system commits only as deep as one branch
holds enough mass; otherwise it stops at a coarser node. A per-branch safety floor
turns over-abstraction into an explicit UNKNOWN rather than a useless "object".

We benchmark on the axes that matter for this, not COCO mAP (where a trained YOLO
wins): off-branch categorical-error rate and calibrated abstention. On known
objects: 0% off-branch errors and ~24% abstention for the hierarchy, vs 53%
off-branch for a flat arg-max head. On out-of-taxonomy objects: 100% safe-handled
(abstract or flag) vs 0% flat. Honest limits are in the writeup (novelty is a
label-space proxy; no box GT).

Demo <HF_SPACE_URL> · paper https://doi.org/10.5281/zenodo.21593472 · code
https://github.com/freshNfunky/IE2025-Research-Paper

### r/SelfDrivingCars

**Title:** Perception that says "some kind of vehicle" instead of mislabeling or
dropping an unknown road object

**Body.**
Detectors know a fixed class list. Meet something off-list (an overloaded rural
bus, a horse-drawn cart) and they either guess a wrong class or ignore it. We
built a layer that abstracts up a taxonomy instead: if it cannot tell the exact
type, it falls back to the most specific safe category (down to just "vehicle" or
"living being"), or flags an explicit unknown obstacle, with a safety floor so it
never degrades into a meaningless "object". Think trapeze safety net, with
multiple levels. It is a SOTIF-oriented, semantic safety argument for statistical
perception, with measured results and an interactive demo.

Demo <HF_SPACE_URL> · paper https://doi.org/10.5281/zenodo.21593472
