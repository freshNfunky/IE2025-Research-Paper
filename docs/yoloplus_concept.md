# YOLO+ : concept and the honest benchmark

> **v3** of the project (see `docs/versions.md`). "YOLO+" is an internal working
> name; a distinct public name is needed (YOLO is a trademark). Naming is an open
> decision.

## What it is

Not a new detector. A **taxonomic abstraction layer** over open-vocabulary
features, on top of any proposer (closed-set YOLO boxes and/or class-agnostic
MobileSAM regions):

```
proposer -> crop -> CLIP embedding -> mass-aggregated hierarchical descent with a
safety floor -> most specific justifiable level, else UNKNOWN, + decision path
-> (downstream) geometry/segmentation as a precision and importance filter
```

Difference from YOLO in one line: YOLO returns **one fixed flat class or nothing**;
YOLO+ returns **as specific as safely justifiable, else a safe coarse category or
an explicit UNKNOWN**, with a traceable path. It degrades gracefully on untrained
objects.

## Benchmarking against YOLO: the honest part

**On closed-set mAP (COCO), YOLO+ loses.** CLIP zero-shot classification is weaker
and slower than a trained head. We do not compete there. YOLO+ is designed to win
on the axes a safety audience cares about:

1. **Novelty / open-set handling** (corner-case sets): safe-handling / abstraction
   vs. drop-or-mislabel.
2. **Off-branch mistake rate**: a categorical error (predicted category not on the
   root-to-truth path). Abstraction to an ancestor is *correct-but-coarse*, not a
   mistake.
3. **Calibrated abstention**: does the arm decline (UNKNOWN) when unsure?

### Result we have (FLAT vs HIER, `scripts/yoloplus_benchmark.py`)

Same YOLO boxes, in-taxonomy objects (n=34):

| | FLAT (arg-max leaf) | HIER (YOLO+) |
|---|---|---|
| correct branch | 47% | 76% |
| **off-branch (categorical error)** | **53%** | **0%** |
| abstain (UNKNOWN) | 0% | 24% |

Headline: **YOLO+ makes zero categorical errors and abstains 24% of the time,
where a flat head is off-branch 53% of the time.** It trades specificity (on-path
predictions are coarser) for never landing in the wrong category and for honest
abstention. Figure: `figures/yoloplus_benchmark.png`.

## The honest limitation (and the proper benchmark)

Our current "novel" split is a **label-space proxy** (COCO classes absent from our
taxonomy, e.g. giraffe), which **YOLO itself recognizes**. So on this data we
*cannot* fairly claim "YOLO+ beats YOLO on novelty" -- YOLO nails the giraffe;
YOLO+ only abstracts it. A valid YOLO-vs-YOLO+ comparison needs **ground-truth
labelled detection data with a leave-classes-out protocol**:

- pick a labelled set (CODA / BDD100K / a COCO subset) with GT boxes + classes;
- designate some classes **known** (in the taxonomy) and hold others out as
  **novel** (removed from the taxonomy);
- match detections to GT; on known classes measure accuracy/severity, on held-out
  classes measure whether each arm abstracts / abstracts to the correct ancestor
  (YOLO+) vs commits a wrong known class (YOLO/flat).

Only that design earns a "we beat YOLO on unknowns" claim. Tracked as a backlog
issue.

## Data-engine angle

YOLO+ is a **hierarchical auto-labeling / active-learning engine**: over unlabeled
video it emits fine labels where confident, coarse labels where only abstraction
is justified, and explicit UNKNOWN for human review. That yields a
hierarchically-labelled dataset with honest abstention -- input for the bigger bet
(train a detector on the taxonomy). "Better data -> better model" is a hypothesis
until that downstream training experiment is run.

## HuggingFace publishing

The stack is HF-publishable as-is (CLIP/open_clip, Depth-Anything/transformers,
MobileSAM+YOLO/ultralytics are all Hub-hosted, fetched lazily):

1. Package `hpercept/` as a small library with a `pipeline()` entry.
2. A **HF Space** (reuse `app_live/`) demoing YOLO+: image in -> boxes + class-
   agnostic proposals, each with a hierarchical label or UNKNOWN + decision path.
3. A **model card**: novelty is the *taxonomic abstraction layer*, not new weights.
4. Optionally a small **dataset artifact**: the hierarchically-labelled corner-case
   sample set.
