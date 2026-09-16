# S7.2 — The reconstruction task class `q_rec`

## The task

> **Reconstruct one observed scalar plasma or state quantity from the other
> task-admissible contemporaneous observations, on the frozen 62-discharge
> DIII-D observational object.**

The target is deliberately **not yet chosen**. This document fixes what the task
*is* before we know which target makes it easy.

## The scientific question

> Can SIR identify a **target-independent relational representation** on
> development discharges whose **support** remains useful on previously unseen
> DIII-D discharges, when coefficients are calibrated only from an allowed
> calibration interval?

The object of study is the **support** — which scientific coordinates enter the
relation — not a particular set of fitted numbers.

## What the task is

**CONTINUOUS RECONSTRUCTION.** At each scored time sample the predictors are
observed *contemporaneously* with the target. The task asks whether a relational
representation carries the target's information, not whether the future can be
anticipated.

## What the task is not

| Not this | Why it matters |
|---|---|
| ELM detection | no event taxonomy is required or used; the archive carries **no** ELM annotations at all |
| Event classification | there is no label-generation pipeline in scope |
| Forecasting | predictors are contemporaneous, never lagged-only |
| Causal inference | provenance closure establishes *ancestry*, not causation |
| Control | no actuation decision is proposed |
| Zero-shot coefficient transfer | coefficients may be re-estimated per discharge |
| Discovery of a universal plasma equation | the claim domain is 62 discharges |

Choosing a boring, continuous target is deliberate. The novelty belongs in task
conditioning, provenance closure, typed ontology generation, representation
discovery, frozen structural transfer and qualification — not in the target.
Reviewers should not have to adjudicate plasma-event taxonomy to assess the
method.

---

## STRUCTURAL TRANSFER WITH LOCAL CALIBRATION

This is the transfer claim, and it is the single most important thing to state
precisely.

**What transfers:** the *scientific coordinate support* — which coordinates, and
in what relational form.

**What does not transfer:** the *numerical coefficients*, which may be
re-estimated on each new discharge from permitted calibration data.

### Operationally

1. The representation (coordinate support and relation form) is selected using
   **development discharges only**.
2. That support is **frozen** — hashed and recorded — **before any external
   discharge is evaluated**.
3. On a new external discharge, relation coefficients **may** be estimated using
   target values inside the declared **calibration interval** of that discharge.
4. Target values inside **protected intervals** are never used for fitting, for
   hyperparameter choice, or for anything except final scoring.
5. The frozen support is then scored on the protected intervals.

### Why this is the honest claim

A zero-shot fixed-coefficient claim would be stronger, and this study does not
make it. Tokamak discharges differ in configuration, and a single coefficient
vector would be expected to fail for reasons unrelated to whether the
*representation* is right.

Conversely, a claim that merely refits everything per discharge would be
vacuous. The discipline is that **the support is frozen across discharges** —
only the coefficients are local. If the support is wrong, local calibration will
not rescue it, and the baselines in `BASELINE_PROTOCOL.md` are there to show
whether it did.

### The comparison that makes it meaningful

Local calibration is granted to **every** comparator on identical geometry:
the constant baseline, persistence, the raw linear baseline and the raw
nonlinear baseline all receive the same calibration intervals and are scored on
the same protected samples. The question is therefore never "does calibration
help?" but "**does the relational support contribute anything beyond trivial and
raw-coordinate alternatives given the same calibration?**"

---

## Why reconstruction and not forecasting

Because predictors are observed during the protected block, this is a statement
about **information content**, not about temporal anticipation. Saying otherwise
would overclaim.

The rolling-origin geometry in `VALIDATION_PROTOCOL.md` looks like a forecasting
design and is not one: expanding calibration windows are used because they
distribute protected blocks through the trajectory in a target-blind way, not
because anything is being predicted forward in time.

## Failure is an acceptable outcome

A negative result under this contract is a publishable, informative outcome and
is preferable to a positive result obtained by changing the rules after seeing
them. The previous q_rec attempt was retired because a constant predictor beat
it; that is exactly the failure mode `BASELINE_PROTOCOL.md` exists to catch
before, not after, the fact.
