# Spike: physics-bounded digital-twin (voxel) simulation, feasibility and effort

Scoping note for a **simulation model that runs simultaneously with reality** as a
physics-bounded, semantically annotated **voxel** world. Goal: test the core thesis
that a physics-bounded running twin constrains degrees of freedom and makes behavior
predictable, unlike today's snapshot-machine driving functions. See the vision note
`docs/future_work_semantic_context.md`.

## 0. Theoretical basis (already abstract in the Goedel paper)

The abstract foundation is in the companion paper on decidability and the semantic
crisis (`schaller_patterns`, doi:10.5281/zenodo.20562409): a system cannot verify
itself (it cannot be its own *Selbstzweck*), but meaning and decidability resolve
**against a context**. The digital twin operationalizes that abstract "context": it
is a physics-bounded, semantically annotated running world model that supplies the
context against which perception and prediction become decidable. The same semantic
model is meant to span the pure-semantic reasoning OS (**XIXUM**) and this
physics-grounded twin (one identical model, not two fused). This note is the
engineering feasibility of that operationalization only; the formalism lives in the
paper.

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
