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

## Known gap

The **identified** tier (a normal car/person committed to a specific leaf) is
not shown here because it needs a known-object driving set (Cityscapes), whose
large parquet shards did not stream reliably on the current connection. To be
added once a stable connection (or a few cached Cityscapes frames in
`data/samples/`) is available.
