# Review evidence

Supplementary evidence for the paper *Hierarchical Taxonomic Abstraction for the
Safe Handling of Novel Objects in Autonomous Driving Perception*
(v1, doi:10.5281/zenodo.21593472), assembled during the review exchange with
Dr. Ho Wa Ku. These files are the authoritative record; they are versioned here
rather than sent as attachments.

## Files

| File | What it is |
|------|-----------|
| `cases.csv` | Machine-readable per-detection breakdown of all 54 detections (population, YOLO class, hierarchical outcome, node, floor, top-leaf cosine, flat baseline, KPI verdict, and a per-row `plausible` flag). |
| `supplement.pdf` | One-page summary: evaluation set, selection rule / manifest, thresholds, KPI table with denominators, fallback breakdown, and a preliminary evidence-to-envelope mapping. |
| `supplement.tex` | LaTeX source of the supplement. |
| `cases.pdf` | Print-friendly rendering of a readable subset of `cases.csv`. |
| `response_ku.md` | Point-by-point response and the planned v2 revisions (reviewer log). |

## Headline, stated precisely

Across 40 images, YOLOv8s produced 54 detections; 20 were **out-of-taxonomy**
(the predicted COCO class has no taxonomy node). All 20 satisfied the predefined
fallback rule (9 abstracted, 11 UNKNOWN): **20/20 fallback-rule coverage for
detected label-space-gap proxies**. This is *not* novelty-detection accuracy and
*not* demonstrated driving safety. Semantic-branch plausibility is **15/20** (5
cross-branch overreaches: airplane, kite, frisbee to *Living Being*), which is
exactly the gap a genuine open-world novelty test must target.

## Reproduce

```bash
python scripts/dump_cases.py 40 0.5      # -> review/cases.csv
python scripts/render_cases_pdf.py       # -> review/cases.pdf
# then build the supplement:
latexmk -cd -pdf review/supplement.tex   # -> review/supplement.pdf
```

Selection rule: SegmentMeIfYouCan Road Anomaly, validation split, the first 40
samples in Hugging Face streaming order (deterministic, no shuffle). The `image`
column in `cases.csv` (0..39) is the stream position.
