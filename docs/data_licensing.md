# Data licensing and use boundaries

Which datasets may appear in public artifacts (repo, papers, arXiv/Zenodo/HF,
issues, figures) and which may not. When in doubt, treat data as all-rights-reserved
and keep it out of anything public.

## Public / OK to publish results from

| Dataset | License | Use |
|---|---|---|
| COCO (val) | CC BY 4.0 (images vary) | v3 leave-classes-out benchmark. Public. |
| nuScenes-mini | free, **non-commercial** research | planned twin MVP (#13). Public results OK, non-commercial only. |
| KITTI (tracking/raw subset) | CC BY-NC-SA 4.0 | alternative for the twin MVP. Public results OK, non-commercial only. |

These match the project's non-commercial line (CC BY-NC-SA / CC BY-NC). Keep the raw
data in a gitignored `data/` dir; never commit it, stream/load lazily.

## RESTRICTED: internal use only, never public

**AVL GmbH / SafeWahr recordings.** Public-release rights are **unknown** (provided
under a project/consortium context; not clarified in writing as of this note).

- **Internal / local experimentation:** OK (per the author's understanding of the
  internal-use basis).
- **Public in any form:** NOT OK until written clearance exists. This includes:
  - the raw recordings themselves,
  - **anything derived from them** (figures, cropped frames, annotated examples,
    per-frame result tables, test fixtures, model cards, paper content, issue
    attachments).
- Storage: `data/avl_safewahr/` (gitignored; explicit rules in `.gitignore`).
- Any AVL-based result stays in **internal validation only**. Public claims must be
  reproducible from the public datasets above, not from AVL data.

To lift the restriction: obtain written permission from the SafeWahr coordinator /
AVL data-governance for the specific public use intended, then update this file.
