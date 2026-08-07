# Spike: physics-bounded digital-twin (voxel) simulation, feasibility and effort

Scoping note for a **simulation model that runs simultaneously with reality** as a
physics-bounded, semantically annotated **voxel** world. Goal: test the core thesis
that a physics-bounded running twin constrains degrees of freedom and makes behavior
predictable, unlike today's snapshot-machine driving functions. See the vision note
`docs/future_work_semantic_context.md`.

## 0. Theoretical basis (from the Goedel/Context paper)

The foundation is the author's paper *Goedel's Incompleteness Theorem and the Power
of Context* (v1, 2026; the theoretical closure of `schaller_patterns`,
doi:10.5281/zenodo.20562409). It is a non-peer-reviewed preprint and its physical
synthesis is the author's position, so it is cited here as a **framework**, not as
established fact. The load-bearing claims for the twin:

- **Contextlessness** is a single failure mode: a context-free system has no
  internal access to its own semantics (Goedel, Rice, Tarski, Loewenheim-Skolem as
  four projections). The resolving move is to supply an external **validation space
  M** / bounded context; the cognition chain is
  **Context -> Meaning -> Function -> Cognition**.
- **Reality does not hallucinate because it is physically sub-complex.** Feedback
  requires latency (an imaginary restoring term); state diffusion and the event
  horizon (c) truncate and blur the variance. So prediction does not collapse to
  "anything goes": it degrades gradually, and the future is "the low-resolution
  projection of a present already underway". An event **announces itself: abstractly
  at a distance, sharply up close.**
- **Safety = manufacturing sub-complexity artificially** by bounding context (ODD,
  interlocks, monitors, redundancy) so that within the boundary the output is
  trustworthy. Safety is produced by bounding context, not by perfecting the
  algorithm (paper Sec. VII-F).

**Why the twin is the concrete instrument, not a side quest:**

1. The physics-bounded, semantically annotated running twin **is a constructed
   validation space M / bounded context** for the driving ODD. It manufactures the
   sub-complexity the paper says safety requires, explicitly and in software.
2. The paper's **footnote 1 (Sec. V) defers exactly this**: it flags that classical
   control theory under-uses the imaginary mapping space, that this recurs "including
   simulation", and that "a full treatment of the simulation case lies beyond this
   paper and warrants separate work". This spike **is** that deferred simulation
   case: a simulation that runs with latency (a real forward model), not a
   feed-forward snapshot y(t)=f(x(t)) but a feedback system y'(t)=g(y,x) with a
   state of its own.
3. **HOWC already realizes the semantic-resolution half.** The taxonomy resolution
   gradient (coarse/uncertain far, specific/certain near) instantiates "an event
   announces itself abstractly at a distance, sharply up close"; the safety floor /
   UNKNOWN is the bounded-context reject. The twin adds the *physical*-boundedness
   half (the running, conserved, horizon-capped world model).

One identical semantic model is meant to span the pure-semantic reasoning OS
(**XIXUM**) and this physics-grounded twin (one model, not two fused). This note
scopes the engineering feasibility of that operationalization only; the formalism
lives in the paper.

## 1. What the voxel twin actually requires (decomposition)

| Block | What | Tooling | Effort (focused, solo) |
|------|------|---------|------|
| A. Voxel world | semantic occupancy grid (a taxonomy label per voxel/object), sparse | Open3D / OctoMap (octree, not dense arrays) | ~3-5 d |
| B. Physics stepper | propagate state forward, physically bounded | minimal: constant-velocity + constraints (~2-4 d); real engine: PyBullet / MuJoCo / Genesis (~1 wk) | 2 d - 1 wk |
| C. Semantic coupling | place HOWC detections as labelled objects in the voxel world | reuse `hpercept/` | ~1 wk |
| D. "Simultaneous with reality" loop | predict next state, compare to next observation, divergence metric | custom loop | ~1 wk |
| E. *optional* rendering | synthetic sensor data / visualization / HMI | Unity **or** CARLA / Omniverse | 2-4 wk+ |

## 2. Tooling options and honest trade-offs

- **Python-light (Open3D + simple physics):** cheapest path to the thesis; no game
  engine. Best first step.
- **CARLA** (Unreal-based, AV-native): sensors (LiDAR/camera/radar), maps, traffic
  out of the box. The standard when synthetic sensor data is needed.
- **NVIDIA Omniverse / Isaac Sim:** the industrial digital-twin option (photoreal,
  USD, physics), heavy; relevant given the reasoning-model direction (Alpamayo).
- **Unity3D:** great for interactive visualization and **HMI** (fits the passenger-
  experience angle), but its PhysX is game-grade not AV-fidelity, and rendering is
  not needed to prove the prediction thesis. Not the first step.

## 3. Effort tiers

- **Minimal thesis-proving MVP (no game engine), ~2-3 weeks:** Python + Open3D voxel
  occupancy + simple physics stepper, run on **real sequences** (KITTI / nuScenes,
  which give metric 3D), plus a predicted-vs-observed **divergence metric**. Shows
  concretely that a physics-bounded prediction narrows the state space vs a snapshot
  re-perceiver. This is the scientific core.
- **Credible prototype, +3-4 weeks:** real physics engine, richer semantics, more
  scenes, proper occupancy evaluation.
- **Full twin with synthetic sensors + HMI, multi-month:** CARLA/Omniverse (sensors)
  and/or Unity (HMI). Mostly integration/tooling, not research.

## 4. Key synergy and dependencies

- The twin needs **metric 3D**, exactly the gap the open-world feasibility spike
  already identified (`docs/spikes/open_world_feasibility.md`): LiDAR / stereo. So
  the twin and the 3D-perception extension are the **same dependency**, not double
  work.
- Reuses the existing taxonomy and `hpercept/` for the semantic labels per voxel.

## 5. Risks
- Voxel resolution vs memory (use octree / sparse, not dense grids).
- Physics fidelity vs game-engine physics; sim-to-real gap.
- LiDAR-camera calibration / temporal sync correctness (same risk as the 3D spike).
- Scope creep into a rendering/tooling project instead of a prediction experiment.

## 6. Recommended minimal spike
Python-light MVP (section 3, tier 1) on a real metric-3D sequence: build the sparse
semantic voxel occupancy, step it with simple physics, and report the
predicted-vs-observed divergence over a short horizon. Defer CARLA/Unity/Omniverse
until synthetic sensors or HMI are actually needed.
