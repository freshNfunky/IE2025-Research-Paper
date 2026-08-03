# Version lineage

Scope grows from "classify a detector's boxes" to "open-world perception".

## v1 — Hierarchical taxonomic abstraction (evaluation paper)
Flat vs. hierarchical classification with a per-branch safety floor; safe handling
of novel objects (abstract up the taxonomy or flag UNKNOWN, never a confident
wrong leaf). **Published:** Zenodo doi:10.5281/zenodo.21593472. arXiv source
package: `scripts/build_arxiv.sh`; metadata: `paper/arxiv_abstract.md`.

## v2 / v2.1 — Semantic segmentation cross-validation
A second, independent perception path (CLIPSeg) that confirms / flags / conflicts
the box detections, adding pixel-context corroboration and an importance signal.
v2.1 folds in the reviewer response (`paper/reviews/response_ku.md`): precise
denominators, the novelty-is-a-proxy caveat, and the honest limits. Issue #1.

## v3 — Open-world hierarchical classifier  (working name: "HOWC")
The scope broadens from labelling a closed detector's boxes to **open-world
perception**: class-agnostic region proposals (MobileSAM) for objects the closed
set misses, a **geometry / depth** precision filter (flat vs. 3D, foreground
isolation), and **multi-modal motion** cues (stereo, Doppler, LiDAR), all feeding
the hierarchical abstraction and its UNKNOWN safety net.

- Concept + honest benchmark: `docs/howc_concept.md`
- Open-world feasibility spikes (A2 / B / C, with negative results kept honest):
  `docs/spikes/open_world_feasibility.md`
- Tracking: #8 (multi-modal fusion + temporal), #10 (motion-mask indicator),
  #11 (YOLO-vs-HOWC leave-classes-out benchmark + publishing)

**Naming (open decision).** "HOWC" is an internal working name only. YOLO is a
trademark (Ultralytics); a public name must be distinct to avoid confusion and
trademark issues. The HF model repo, model card, and outreach copy currently use
the working name and will be renamed once a public name is chosen.
