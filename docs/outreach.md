# Outreach copy (arXiv + Show HN + Reddit)

NOTE: the HF link below is the free **model repo** (card + runnable code, run
locally). An interactive Gradio Space needs HF PRO; swap in the Space URL once live.
Positioning throughout: the novelty is the taxonomic abstraction layer and the
safety behaviour, not closed-set accuracy.

UPDATE (v3, open-world): the v1/v2 "100% safe on novel objects" numbers came from
a **label-space proxy** (COCO classes left out of the taxonomy, which YOLO itself
recognizes). v3 closes that with a **ground-truth leave-classes-out** benchmark on
real annotated objects (n=235): the flat head is confidently wrong 100% of the
time (37% in the wrong super-category); HOWC is confidently wrong 0% of the time
and safely handles 94% (26% correct super-category, 69% honest UNKNOWN). The win
is safety, not specificity, and we say so.

---

## 1. arXiv

**Title (v3):** Open-World Hierarchical Perception: Taxonomic Abstraction over
Class-Agnostic Proposals for the Safe Handling of Out-of-Vocabulary Road Objects

**Categories:** cs.AI (primary), cs.CV, cs.RO

**Abstract.**
A closed-set detector for autonomous driving must assign every object one of a
fixed set of labels. On an object outside that set (a horse-drawn carriage, road
debris, livestock on a rural road) it can only force a confident but wrong specific
label or drop the object. Prior work in this series replaced the flat label set
with a hierarchical taxonomy and a runtime abstraction rule, but evaluated it only
on the boxes a closed detector already produces. This paper takes the layer
open-world: we place taxonomic abstraction on top of class-agnostic region
proposals so objects the closed detector never boxes can still be classified or
flagged; we report a feasibility study of three open-world signals (class-agnostic
segmentation, appearance-based out-of-distribution scoring, monocular depth) that
shows why no single 2D cue suffices and how they compose; and we run the evaluation
the earlier papers could not, a ground-truth leave-classes-out benchmark on real
annotated objects. Holding out seven COCO classes and classifying their 235
ground-truth crops, a flat closed head emits a confident wrong specific label 100%
of the time (37% of them in the wrong super-category, e.g. an animal named as a
vehicle), whereas the hierarchical layer emits zero confident wrong specific labels
and safely handles 94% of the objects (a correct super-category, or an explicit
UNKNOWN OBSTACLE). We are explicit that this is a safety result, not a specificity
one: the correct super-category is recovered only 26% of the time and the remaining
69% are conservatively flagged unknown. The contribution is an open-world
perception layer that never makes a confident categorical mistake on an
out-of-vocabulary object, together with an honest account of its cost.

(v1 abstract, the closed-box evaluation, remains archived at
doi:10.5281/zenodo.21593472.)

---

## 2. Show HN

**Title:** Show HN: HOWC, perception that abstracts up a taxonomy instead of
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
and slower). The point is the tail. The clean test is a ground-truth
leave-classes-out benchmark: remove classes from the taxonomy, then classify their
real annotated crops. On 235 such out-of-vocabulary objects the flat head is
confidently wrong 100% of the time (37% in the wrong super-category, e.g. an animal
called a vehicle); ours is confidently wrong 0% of the time and stays safe on 94%.
The catch, which we state plainly: most of that safety is abstention (69% flagged
UNKNOWN), and it only recovers the correct super-category 26% of the time. The win
is not making a confident categorical mistake, not superior accuracy. On known
in-taxonomy objects it makes 0% off-branch errors with ~24% abstention, versus a
flat head's 53% off-branch.

Code + run it yourself: https://huggingface.co/freshNfunky/howc . Paper (open access): https://doi.org/10.5281/zenodo.21593472 .
Code: https://github.com/freshNfunky/IE2025-Research-Paper .

Feedback welcome, especially on the open-world detection front-end: class-agnostic
proposals (SAM) massively over-propose, and we think geometry/LiDAR is the missing
precision filter.

---

## 3. Reddit

### r/MachineLearning

**Title:** [P] HOWC: hierarchical taxonomic abstraction for safe handling of
novel objects (training-free, with an honest benchmark)

**Body.**
A flat classifier on an out-of-distribution object either forces a confident wrong
class or drops it. We put a hierarchical taxonomy over pretrained detection + CLIP
zero-shot: each box is scored against the taxonomy leaves, the leaf probabilities
are aggregated up the tree, and the system commits only as deep as one branch
holds enough mass; otherwise it stops at a coarser node. A per-branch safety floor
turns over-abstraction into an explicit UNKNOWN rather than a useless "object".

We benchmark on the axes that matter for this, not COCO mAP (where a trained YOLO
wins): off-branch categorical-error rate, calibrated abstention, and out-of-
vocabulary handling. The headline test is ground-truth leave-classes-out: hold
classes out of the taxonomy, classify their real annotated crops. On 235 such
objects the flat head is confidently wrong 100% of the time (37% in the wrong
super-branch); the hierarchy is 0% confidently-wrong and safe on 94%. We are
explicit that this is a safety result, not a specificity one: 69% of that is
honest UNKNOWN and only 26% is a recovered correct super-category. On in-taxonomy
objects: 0% off-branch and ~24% abstention, vs 53% off-branch for a flat arg-max
head. (This closes the earlier label-space-proxy caveat; remaining limits, the 69%
abstention and the 2D-only proposal front-end, are in the writeup.)

Code + card: https://huggingface.co/freshNfunky/howc · paper https://doi.org/10.5281/zenodo.21593472 · code
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
perception, with measured results and runnable code.

Code + card: https://huggingface.co/freshNfunky/howc · paper https://doi.org/10.5281/zenodo.21593472
