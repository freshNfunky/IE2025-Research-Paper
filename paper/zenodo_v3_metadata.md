# Zenodo deposit metadata, v3 (HOWC open-world paper)

Fallback publication after arXiv moderation declined the submission (scope
judgment, not peer review). Files to upload live in `build/zenodo_v3/`:
`paper_v3.pdf` (main) and `paper_v3_source.zip` (LaTeX source + figures).

## Form fields

**Resource type:** Publication → Preprint

**Title**
```
Open-World Hierarchical Perception: Taxonomic Abstraction over Class-Agnostic Proposals for the Safe Handling of Out-of-Vocabulary Road Objects
```

**Authors**
```
Schaller, Felix
```
ORCID: 0000-0002-3218-3214

**Description / Abstract** (plain text)
```
A closed-set detector for autonomous driving must assign every object one of a fixed set of labels. On an object outside that set (a horse-drawn carriage, road debris, livestock on a rural road) it can only force a confident but wrong specific label or drop the object. Prior work in this series replaced the flat label set with a hierarchical taxonomy and a runtime abstraction rule, but evaluated it only on the boxes a closed detector already produces. This paper takes the layer open-world: we place taxonomic abstraction on top of class-agnostic region proposals so objects the closed detector never boxes can still be classified or flagged; we report a feasibility study of three open-world signals (class-agnostic segmentation, appearance-based out-of-distribution scoring, monocular depth) that shows why no single 2D cue suffices and how they compose; and we run the evaluation the earlier papers could not, a ground-truth leave-classes-out benchmark on real annotated objects. Holding out seven COCO classes and classifying their 235 ground-truth crops, a flat closed head emits a confident wrong specific label 100% of the time (37% of them in the wrong super-category, e.g. an animal named as a vehicle), whereas the hierarchical layer emits zero confident wrong specific labels and safely handles 94% of the objects (a correct super-category, or an explicit UNKNOWN OBSTACLE). We are explicit that this is a safety result, not a specificity one: the correct super-category is recovered only 26% of the time and the remaining 69% are conservatively flagged unknown. The contribution is an open-world perception layer that never makes a confident categorical mistake on an out-of-vocabulary object, together with an honest account of its cost.
```

**License:** Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
— matches v1 and the HuggingFace model card. (Zenodo offers plain CC BY-NC, so
we use it here rather than the BY-NC-SA arXiv forced.)

**Keywords**
```
open-world perception; open-set recognition; hierarchical classification; autonomous driving; functional safety; novelty handling; taxonomic abstraction
```

**Related / alternate identifiers**
- `continues` → `10.5281/zenodo.21593472` (v1 of the series)
- `isSupplementedBy` → `https://github.com/freshNfunky/IE2025-Research-Paper` (code)

**Notes** (optional)
```
Third paper in a series. Code and full history at
https://github.com/freshNfunky/IE2025-Research-Paper . 6 pages, 4 figures, 1 table.
```
