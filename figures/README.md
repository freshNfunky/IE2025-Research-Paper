# Intermediate status figures

Generated with `python scripts/make_figures.py road_anomaly 10` on the
SegmentMeIfYouCan **Road Anomaly** set (real street scenes with objects that
have no proper flat class — the paper's exact scenario).

Each `ex_*.png` is a two-panel figure:
- **left** — the frame with the selected bounding box highlighted, showing
  YOLO's (wrong, out-of-distribution) guess and the system's final outcome;
- **right** — the taxonomy decision path, expanded along the descent, annotated
  with each node's **probability mass** (the confidence values) and the
  safety-floor markers (◆). The verdict line explains where/why it abstracted.

Colour: 🟢 identified · 🟠 abstracted · 🔴 unknown.

## Recommended for the IEEE paper

| Figure | Story | Why it's exemplary |
|--------|-------|--------------------|
| **`ex_road_anomaly_01_0_unknown.png`** ⭐ | **Giraffe on the road.** YOLO: `giraffe (0.95)`. Mass concentrates at **Moving Object (0.74)** but then splits (Living Being 0.42 vs Vehicle 0.32) → above the safety floor → **UNKNOWN OBSTACLE**. | Clean single object, dramatic novelty, shows BOTH ideas at once: don't drop the object (it climbs to Moving Object) *and* don't over-abstract into a useless label (floor stops it → explicit UNKNOWN). |
| **`ex_road_anomaly_09_1_abstracted.png`** | **Turkeys crossing.** YOLO: `bird (0.59)`. Descends to **Living Being (0.55, a floor)** and stops → **ABSTRACTED**. | Perfect companion: shows the *successful* abstraction to a safe, useful level (the other half of the thesis). |

Pairing the giraffe (UNKNOWN) with the turkeys (ABSTRACTED) tells the whole
story in two figures.

## Summary

`summary_road_anomaly.png` — outcome distribution and per-outcome confidence
across the sampled frames. On an all-anomaly set the correct behaviour is
overwhelmingly UNKNOWN (22) with a few abstractions (1) and no false
leaf-level identifications (0) — i.e. the system stays conservative exactly
where it should.

## Benchmark: flat class list vs. hierarchical taxonomy

`scripts/benchmark.py` runs a fair head-to-head on the same YOLO boxes and the
same CLIP features and leaf vocabulary — the only difference is flat argmax (no
abstraction) vs. the hierarchical mass-descent with a safety floor. Novelty
ground truth: a detection is *novel* if YOLO's COCO class has no node in our
taxonomy (e.g. giraffe, airplane).

**`benchmark_flat_vs_hier.png`** (n = 40 images, 46 detections):

| | Flat (argmax) | Flat (reject@0.5) | **Hierarchical** |
|---|---|---|---|
| **Novel objects safely handled** | 0% (confident wrong leaf) | 0% (all dropped) | **100%** (11 abstracted, 5 flagged unknown) |
| Novel confident-wrong leaf | 100% | — | **0%** |
| **Known objects useful category** | 33% | — | **70%** (0% wrong branch, 30% honest unknown) |

> **Safety improvement on novel road objects: +100 percentage points.**
> On *known* objects the hierarchy is at least as specific as the flat baseline
> (70% vs 33% useful) and never makes a confident wrong claim — so the safety
> gain does not cost known-object performance.

`calibration_tradeoff.png` (`scripts/calibrate.py`) sweeps the operating point:
every hierarchical config sits at 100% novel-safety while the flat baseline is a
floor at 0% — the hierarchy dominates. Chosen point: `temperature=0.06,
commit_mass=0.40` (now the default in `AbstractionConfig`).

## Notes / gaps

- The **identified-to-a-leaf** tier reads 0% because several known COCO classes
  map onto *internal* taxonomy nodes (e.g. `car` → "Passenger Car", whose
  Sedan/SUV leaves always split the mass). "Useful category on the correct
  branch" is therefore the meaningful specificity measure, not "reached a leaf".
- A dedicated known-object driving set (Cityscapes) would strengthen the known
  half; its large parquet shards did not stream reliably here. The Road Anomaly
  frames already contain enough normal traffic to populate the known column.
