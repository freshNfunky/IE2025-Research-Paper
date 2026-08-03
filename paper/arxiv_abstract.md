# arXiv submission metadata

Paste-ready fields for the arXiv submission of the evaluation paper.

**Title**
Hierarchical Taxonomic Abstraction for the Safe Handling of Novel Objects in
Autonomous Driving Perception

**Authors**
Felix Schaller (Independent Researcher, Dubai / Munich; ORCID 0000-0002-3218-3214)

**Primary category:** cs.AI  (endorsed)
**Cross-list:** cs.CV, cs.RO

**Comments (optional):** Evaluation paper; interactive code and model card at
https://huggingface.co/freshNfunky/yolo-plus-perception ; source at
https://github.com/freshNfunky/IE2025-Research-Paper ; companion paper
doi:10.5281/zenodo.21593472.

**License:** CC BY-NC 4.0

---

## Abstract

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
monocular and appearance signals are scale-limited), and outline extensions via
semantic segmentation, LiDAR geometry, and Doppler/motion cues.
