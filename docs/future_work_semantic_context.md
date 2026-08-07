# Future work: a semantic, context-grounded reasoning layer

This note records the long-term research direction that HOWC (the open-world
perception layer, v3) is a first, concrete building block of. It is a **research
program, not a claimed result**: the paper delivers the perception substrate; the
program below is the intended trajectory. It is kept abstract where it touches
confidential source material (see issue #2).

## Motivation: explainable planning needs honest perception

Reasoning models for autonomous driving are moving toward inspectable decisions:
e.g. NVIDIA's Alpamayo emits a "chain-of-causation", a language reasoning trace
that explains why the vehicle yielded, slowed, or chose a path, linked to parts of
the scene. This validates the direction of this series (inspectable,
safety-relevant decisions over black-box output), but it also exposes a dependency:

> A chain-of-causation is only as trustworthy as the perception it references. If
> perception confidently mislabels an out-of-vocabulary object, the reasoning trace
> will confidently rationalize a wrong action, with a clean-looking justification.
> Explainability at the planning layer needs calibrated humility at the perception
> layer.

HOWC is exactly that calibrated-humility substrate: on out-of-vocabulary objects it
never emits a confident wrong specific label (0% vs a flat head's 100%), abstracting
to a correct super-category or an explicit UNKNOWN. The perception-level decision
path (the taxonomy descent) is the analog, one layer upstream, of the planning-level
chain-of-causation.

## Direction 1: a non-probabilistic semantic model of the ODD

The central component is a **semantic model that annotates the operational design
domain (ODD), the driving context, semantically** rather than statistically. It is
intended to grow into a **reasoning model that is formally non-probabilistic**:
conclusions follow from logical inference rules over semantic structure, not from a
learned likelihood. HOWC's taxonomy and safety floors are an early, narrow instance
of such structure (what an object *can safely be said to be* given the evidence).

## Direction 2: 3D perception and digital twins

The perception substrate is to be extended with **3D perception** (the feasibility
study in the paper shows why 2D cues alone are scale-limited and why metric geometry
is the missing piece) and with **digital twins** of the driving world. The intended
end state is a convergence: the **digital twin of the autonomous-driving world** and
a **purely semantic world model** (working name: *xixum*) merge, one supplying
grounded geometry and dynamics, the other supplying meaning. (3D/motion model
tracked abstractly in issue #2; its source is confidential.)

## Direction 3: context as the resolving principle

The unifying thesis, carried over from the companion work on decidability and the
semantic crisis in autonomous systems (`schaller_patterns`), is that **everything
resolves through a context**. Meaning is not intrinsic to a pattern; it is fixed by
the context the pattern is read in (the shampoo-bottle paradox: the same appearance
means different things at different scales/contexts).

The formal backbone is a reading of Goedel's incompleteness: **a system cannot
verify itself**, because a system cannot be its own purpose (*Selbstzweck*), that is
consistent and logical. But **against a context**, sense emerges, and with it, at the
end, cognition. Self-reference fails; context-reference succeeds. This is why the
reasoning layer above is defined relative to an annotated context (the semantic ODD),
not as a self-contained prover.

## Long-term: a formal-semantic, context-grounded cognitive AI

These strands are intended to flow into a **formal-semantic AGI**: a cognitive AI
that, given a context, produces a **logical closure** within that context by logical
inference rules, i.e. reasons to a grounded conclusion rather than sampling a likely
one. This is the north star, stated as such. Nothing in the current papers claims to
have built it; HOWC is one honest, measurable step (safe open-world perception) on
that path.

## Relation to this paper

- HOWC (v3) = the perception substrate: safe, inspectable, uncertainty-aware object
  handling that never commits a confident categorical mistake.
- The reasoning layer, the 3D/digital-twin grounding, and the context-resolution
  formalism are future work, tracked at a conceptual level here and in issues #1,
  #2, #8, #10.
