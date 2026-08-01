# Reviewer response and v2 revision plan

Informal but rigorous review by **Dr. Ho Wa Ku** (LinkedIn exchange, execution
governance / safety assurance background). This log captures each point, our
position, and the concrete change for the next revision (**paper v2 / v2.1**).
Paper v1 is published (DOI 10.5281/zenodo.21593472) and is **not** edited; these
changes land in v2.

Legend: **Accept** = we agree and will change; **Accept+deepen** = we agree and
the point opens a stronger reformulation; **Clarify** = keep but state more
precisely.

---

## R1. Claim wording: "20 of 20" not "100% novelty-detection accuracy"
**Accept.** The defensible statement is "20 of 20 out-of-taxonomy proxy
detections met the predefined safe-handling criterion", with the denominator
explicit. "100% novelty-detection accuracy" overreaches.
**v2 action:** restate every headline with its denominator; rename the metric to
*safe-handling rate on out-of-taxonomy detections*; move the proxy caveat from
the limitations paragraph into the results statement itself.

## R2. Our "novelty" is not real novelty (the key point)
**Accept + deepen.** Two layers:
1. It is a *proxy*: novel := the detector's COCO class has no node in our
   taxonomy (giraffe, airplane). The detector already **recognizes** these
   objects; they are a **label-space gap** in our taxonomy, not open-world
   novelty. Classification happens entirely inside YOLO's known category space.
2. **Real novelty** is the *scale-dependent undecidability* of the companion
   paper (the shampoo-bottle paradox): at low resolution an undersampled pattern
   is confidently classifiable as one thing (a horse's head) while the truth (a
   collage of hair and oil) is hidden behind the undersampling. The pattern
   itself is undecidable, independent of any label list.

These are two different regimes:
- **(a) label-space gap** — the object is clear, our vocabulary lacks a leaf.
  Abstraction solves this (our current result).
- **(b) pattern-level undecidability** — the evidence itself does not determine
  the class at the available resolution. Abstraction is *necessary* here too,
  but the trigger is epistemic (insufficient information), not lexical.

**v2 action:**
- Rename "novel" to "out-of-taxonomy (label-space gap)" throughout; reserve
  "novelty" for regime (b).
- Add a **genuine-novelty evaluation**: a resolution / undersampling stress test
  where the true class is undecidable from the crop (downsampled or distant
  objects, the shampoo-bottle regime), measuring whether the system abstracts or
  flags UNKNOWN instead of committing a confident leaf. This is the honest
  open-world test and the bridge between the two papers.
- Frame the safety floor as the response to **both** regimes: a lexical gap
  bottoms out at a floor; an epistemic gap (low resolution) should trigger the
  same abstraction, and ideally a resolution-aware confidence.

## R3. No box-level ground truth -> false negatives out of scope
**Accept.** Object-level false negatives and missed objects are unmeasured;
detection recall has no denominator in v1. The KPI scores only detected objects.
**v2 action:** evaluate on a box-annotated corner-case set (CODA / BDD100K);
report recall, precision, mAP, importance-weighted; state detection-stage false
negatives explicitly and separately from the classification-stage result.

## R4. Flat baseline's 0% is definitional, not empirical
**Accept.** The flat 0% follows from the comparison rule (arg-max can only emit a
leaf; the reject variant drops), not from a fully equivalent empirical baseline.
**v2 action:** add a real flat **open-set** baseline (e.g. max-softmax-probability
or energy/OOD score with a calibrated reject), so the flat number is earned, not
defined. Keep the definitional version only as an upper-bound illustration.

## R5. Execution Governance does not follow "as a consequence"
**Accept.** The taxonomy supplies **bounded semantic evidence**. EG **separately**
determines whether a manoeuvre is authorized under mandate, constraints, live
context, accountability and sufficient proof. A bounded claim ("Vehicle") may
justify restricted deceleration, increased separation or Safe-Hold while
remaining insufficient for a specific manoeuvre.
**v2 action:** rewrite the EG paragraph so EG owns authorization; present our
evidence-to-envelope mapping strictly as **design intent**, not a result, and
not automatic.

## R6. Independence and uncertainty must be explicit
**Accept.** Segmentation shares the visual source, so it is **corroborative, not
independent**. Doppler and LiDAR add genuine independence, but any decidability
claim must be bounded by sensor geometry, calibration, synchronization,
ego-motion, occlusion, multipath and measurement uncertainty.
**v2 action:** add an *independence and uncertainty budget* subsection; classify
each channel by how independent it truly is; replace "formal decidability" with
**bounded decidability** with a stated uncertainty budget.

## R7. Adopt the bridge
**Accept.** Use his formulation as the interface to EG:
bounded semantic evidence -> cross-channel coherence and residual uncertainty ->
action-specific authorization envelope -> permitted manoeuvre / restricted
operation / Safe-Hold -> reviewable execution evidence.

---

## What does not change
The core contribution stands: abstraction to a per-branch safety floor turns
"drop or mislabel" into a **bounded, reviewable semantic claim**, which (per the
reviewer) is materially interpretable. The revisions are about **precision**
(denominators, wording), **baseline rigor** (empirical open-set flat baseline),
**scope honesty** (detection-stage false negatives, degradation, domain shift),
and, most importantly, **separating a label-space gap from genuine pattern-level
novelty** and testing the latter directly.

## Deliverables for the exchange
- `paper/supplement/cases.csv` — per-detection breakdown of all detections.
- `paper/supplement/supplement.pdf` — one-page summary table with denominators
  and thresholds.
