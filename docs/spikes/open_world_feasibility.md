# Spike: open-world classifier, feasibility and effort

Branch: `spike/open-world-classifier`. Goal: estimate the effort to move from the
current **label-space-gap** system to a genuine **open-world** one, and to use
**LiDAR / 3D** so that 2D ambiguities resolve over space.

## 1. Where the current system is closed

| Stage | Today | Limit |
|------|-------|-------|
| Detection | YOLO (closed set) | only proposes boxes for COCO-like classes. A truly unknown object may never be boxed. **This is the real bottleneck.** |
| Classification | CLIP over taxonomy leaves | "unknown" is a cosine threshold, not distribution-aware OOD. |
| Geometry | none (2D only) | billboard-vs-car, elevated-vs-on-ground, occlusion, metric size stay ambiguous. |

Open-world means solving three separable sub-problems. Each can be added
independently, which is good for effort control.

## 2. Building blocks, options, effort

### A. Open-world detection (get a box for *anything*)
- **A1 Open-vocabulary detector** (YOLO-World, GroundingDINO): prompt with the
  taxonomy plus a generic "object". Effort **medium** (swap the front-end).
  Footprint **large** (GroundingDINO ~700 MB+; YOLO-World mid). Risk: prompt
  sensitivity, license/deps.
- **A2 Class-agnostic segmentation** (SAM / MobileSAM / FastSAM) -> mask
  everything, classify each region with CLIP. Effort **medium-high**.
  Footprint: SAM ViT-H ~2.4 GB, **MobileSAM ~40 MB** (viable).
- **A3 Geometric proposals from LiDAR**: ground removal + Euclidean clustering of
  the point cloud -> 3D object proposals **independent of appearance**. Effort
  **medium**, footprint **tiny** (numpy / open3d), data: needs LiDAR. This is the
  differentiator and the cheapest compute, and it directly serves the
  "3D resolves 2D ambiguity" thesis.

**Recommendation:** A3 (LiDAR geometric proposals) as the primary open-world
source, optionally A1/A2 as an appearance-based second source, fused later.

### B. OOD-aware classification (a principled "unknown")
- Today: `min_abs_sim` cosine gate (crude).
- Upgrade: max-logit / energy / Mahalanobis on the CLIP embedding, or a
  "background / none-of-these" prompt in the open-vocab set, with a calibrated
  reject. Effort **low-medium**, post-hoc on embeddings we already compute.
  **Cheapest high-value win, do first.**

### C. 3D / LiDAR foreground isolation
- Project LiDAR into the image (calibration), build a sparse depth map, segment
  foreground by **z-depth discontinuity**: objects "pop out" from the background
  plane. Effort **medium**. Pays off three ways:
  - fixes the 2D-segmentation elevation limit (issue #1): elevated objects
    separate from the surface behind them;
  - rejects flat fakes (a billboard car is flat in depth): the redundancy story;
  - gives **metric size** for the physical-constraint gates (measured, not prior).
- Data: **KITTI** (synchronized stereo + Velodyne + calibration; `pykitti`).

## 3. Effort summary (rough, focused work)

| Task | Effort | New deps / data |
|------|--------|-----------------|
| B. OOD scoring on existing CLIP | ~1-2 d | none |
| C. KITTI loader + LiDAR->image projection + depth foreground | ~3-5 d | pykitti, KITTI (GBs) |
| A3. LiDAR geometric object proposals (cluster) | ~3-5 d | open3d |
| A1. Open-vocab detector integration | ~2-4 d | large model download |
| A2. MobileSAM + CLIP region classify | ~3-5 d | mobile-sam |
| Fusion + KITTI eval harness | ~5+ d | - |

- **Minimal geometry-assisted open-world MVP** (B + C + A3 on KITTI): **~1.5-2 weeks**.
- **Credible full prototype** (add A1/A2 + fusion + eval): **~3-4 weeks**.

## 4. Recommended minimal spike (this branch)
1. **B** OOD scoring upgrade on CLIP (post-hoc, no new deps).
2. **C** KITTI loader + LiDAR-to-image projection + depth-based foreground mask.
3. **A3** cluster the depth foreground into geometric proposals; show that a
   LiDAR-proposed region YOLO misses can still be classified or flagged.

Defer: open-vocab detector, SAM, sensor fusion, temporal (issue #8).

## 5. Proposed integration surface (how invasive)
Small and additive. The pipeline already separates propose -> classify ->
validate, so open-world slots in as new *proposers* and a new *validator*:

```
hpercept/openworld/
  ood.py        # OODScorer(image_feat) -> score; wraps existing CLIP embedding
  lidar.py      # LidarFrame: load, project to image, sparse depth, foreground mask
  proposals.py  # geometric object proposals from the depth foreground
datasets.py     # add a KITTI source (camera + velodyne + calib)
pipeline.py     # accept extra proposers; feed metric size to constraints.py
```
No change to the taxonomy or the abstraction core. Risk of regressing v1: low.

## 6. Data and risks
- **Data:** KITTI (free, standard). Alternatives with LiDAR: nuScenes (larger),
  Waymo Open. Note: KITTI is ordinary urban/highway, **not** the anomaly regime,
  so corner-case + LiDAR data is scarce and may need our own captures later.
- **Risks:** model/download footprint (disk-limited machine), LiDAR-camera
  calibration/sync correctness, KITTI domain vs. our anomaly focus.

## 6b. Spike B result (appearance-only OOD): negative, and informative

Implemented an ODD gate via negative / background prompts
(`hpercept/classifier.py: NEGATIVE_PROMPTS`, `negatives_max_sim`) and evaluated
`ood_margin = best_leaf_cosine - best_negative_cosine` on the Road Anomaly set
(`scripts/ood_spike.py`). Ground truth = the `plausible` label.

It does **not** separate. The margins overlap almost entirely:
- implausible (n=5): min -0.018, median -0.014, max +0.008
- plausible out-of-tax (n=15): min -0.067, median -0.008, max +0.033
- in-tax good (n=26): min -0.014, median +0.028, max +0.050

The best threshold that catches all 5 implausible cases (t=+0.02) also breaks
11 of 30 good cases: a net loss. Tellingly, the implausible cases match
"a plain textureless background" rather than "an aircraft" or "sky" -- even the
full-frame airplane. CLIP on the 2D crop cannot reliably tell that it is an
aircraft in the first place.

**Conclusion:** the ambiguity is not lexical or appearance-based; it is the
undersampling / scale-dependent regime (the shampoo-bottle paradox). A 2D
appearance score cannot resolve it, which is exactly the empirical case for C
(geometry / LiDAR). We therefore do **not** wire the OOD gate in; we keep it as a
documented negative result. (min-abs-sim tuning was also checked and overlaps
similarly.)

## 6c. Spike C result (monocular depth flatness): promising, not finished

Implemented depth + a per-box flatness/foreground test
(`hpercept/openworld/depth.py`, `scripts/depth3d_spike.py`), depth source =
monocular (Depth-Anything) as a LiDAR stand-in that runs on our images.

Positive: the depth map cleanly separates foreground from background
(`figures/depth3d_04.png`), and with an **assessability gate** large upright
objects read `3d` (giraffe 0.235, truck 0.231, airplane 0.197) while small /
distant ones are held `n/a` instead of falsely flagged (16 detections: 4 `3d`,
1 `flat`, the rest `n/a`).

Limits: relief is **shape-sensitive** (a compact sheep read `flat`, a false
positive), monocular depth is **relative** not metric, and the dataset has no
billboard for a true `flat` demonstration. So the flatness-as-billboard test is
not yet reliable. Consistent with B, the recurring confound is **scale**:
structure is only measurable above a size, which is exactly where **metric
LiDAR** would help. Verdict: real capability (depth/foreground signal per
detection), promising for the billboard case, but needs metric depth to be
dependable.

## 6d. Spike A2 result ("YOLO+" via MobileSAM): recall up, precision down

Class-agnostic proposals (`hpercept/openworld/segment.py`, MobileSAM via
ultralytics) feeding the hierarchical classifier (`scripts/yoloplus_spike.py`),
8 Road Anomaly images:

- YOLO (closed set): **19** detections total.
- MobileSAM regions YOLO missed: **148**. The hierarchical UNKNOWN gate filters
  **112** as UNKNOWN (its value as a filter), leaving **36** with a category.
- But the 36 are mostly **background** (trees/bushes labelled "Living Being",
  see `figures/yoloplus_01.png`): huge recall, poor precision.

MobileSAM segments *everything* (sky, grass, walls, object parts), so as an
open-world detector it needs an objectness / foreground filter to be usable. The
hierarchy removes the gross background (UNKNOWN) but not vegetation. This is the
DETECTION-side confirmation of the same lesson.

## 7. Verdict (synthesis across A2, B, C)

The three spikes converge on one conclusion: **no single 2D signal is enough**,
and the pieces are complementary rather than competing.

- **A2 (MobileSAM):** open-world *recall* -- boxes for untrained objects -- but
  massively over-proposes (precision collapses).
- **C (depth/geometry):** the natural *precision filter* for A2 -- foreground vs
  background, flat vs solid -- but monocular relative depth is scale-limited;
  needs metric LiDAR.
- **B (appearance OOD):** does not separate on its own; the ambiguity is
  scale/undersampling, not lexical.

So a real **"YOLO+"** (the product idea: YOLO extended with hierarchical
taxonomic classification for unknown objects) is: class-agnostic proposals
(recall) + a geometry/depth filter (precision) + the hierarchical abstraction
(semantics + the UNKNOWN safety net). The hierarchy is the differentiator and
already works; the open-world front-end is feasible but only with the geometry
filter. Effort estimate unchanged (section 3): MVP ~1.5-2 weeks once metric depth
is available.

## 8. HuggingFace publishing path

The whole thing is HF-publishable with no exotic dependencies: CLIP (open_clip),
Depth-Anything (transformers), and MobileSAM/YOLO (ultralytics) are all
HF/ultralytics-hosted and fetched lazily. Plan:

1. Package the pipeline (`hpercept/`) as a small library with a `pipeline()` entry.
2. A **HF Space** (Gradio, reuse `app_live/`) demoing "YOLO+": upload an image,
   get YOLO + class-agnostic proposals, each with a hierarchical taxonomic label
   or UNKNOWN, plus the decision path. Models pulled from the Hub at runtime.
3. A **model card** framing the novelty: not new weights, but a *taxonomic
   abstraction head* over open-vocabulary features that stays safe on untrained
   objects (abstract to a floor, or flag UNKNOWN). Link the paper + this spike.
4. Optionally publish the taxonomy + prompts as a small dataset/config artifact.

Novelty for the Hub is the **hierarchical taxonomic classification layer** ("YOLO+"),
not the base detectors.

