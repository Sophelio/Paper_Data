# S7.2 — Baseline protocol

## Why baselines are frozen before the target exists

The previous q_rec attempt was retired partly because **a constant persistence
predictor beat it** — 0.0685 against 0.1137 for the relational model and 0.1821
for raw coordinates. That was discovered *after* the fact.

Freezing the ladder now means the comparison cannot be arranged, or quietly
dropped, once results exist.

---

## The mandatory ladder — FROZEN

Every baseline receives **identical geometry**: same calibration intervals, same
protected samples, same target-admissible predictor information, same
calibration-fitted preprocessing.

### B0 — calibration mean

Predict the calibration-set mean of the target throughout the protected block.

*Catches:* a target with little variation in the protected interval. This is the
baseline that defeated the retired q_rec.

### B1 — persistence

Predict the last available target value immediately before the protected block,
held constant throughout it.

*Catches:* a slowly-varying target where the previous value is nearly sufficient.
The rolling geometry gives this a clean definition — the last calibration sample
of each block.

### B2 — raw linear baseline

Ridge (or equivalently transparent regularized linear regression) on the **same
target-admissible primitive predictors**, no constructed coordinates.

*Isolates:* the contribution of the **relational construction**. B2 has the same
information; only the representation differs. This is the comparison the
scientific claim actually rests on.

Penalty selected on development discharges only, by the same procedure granted
to the relational model, and frozen before external evaluation.

### B3 — raw nonlinear baseline

**`sklearn.ensemble.HistGradientBoostingRegressor`**, on the same
target-admissible primitive predictors.

Fixed by name now, before any target exists, so it cannot be chosen by running
comparisons. It is a mature, standard, well-understood learner already present
in the environment.

*Isolates:* whether the relational representation contributes anything beyond
what a competent off-the-shelf nonlinear learner extracts from the same raw
information.

**Hyperparameters:** library defaults, except any needed for determinism
(`random_state` fixed and recorded). Any departure from defaults must be
selected on **development discharges only** and frozen before external
evaluation. No hyperparameter may be tuned against external outcomes.

---

## What the ladder is for

> The purpose is **not** to beat machine learning.

It is to establish whether **relational representation contributes utility
beyond trivial and raw-coordinate alternatives**.

A clean reading of the possible outcomes, agreed in advance:

| Outcome | Reading |
|---|---|
| relational ≤ B0 or B1 | the task is trivial or degenerate; **no claim** |
| relational ≈ B2 | the construction adds nothing over raw linear; **no representational claim** |
| relational > B2, ≈ B3 | representation matches a nonlinear learner while staying interpretable — a **meaningful, modest** claim |
| relational > B2 and > B3 | the strongest available outcome |
| relational < B3 | reported plainly; interpretability may still be argued, but **not as accuracy** |

All five will be reported. The third and fourth rows are the interesting ones;
the first two are honest negative results and are publishable as such.

## Reporting

For every baseline: paired per-discharge differences against the relational
representation, paired discharge bootstrap CIs, win/tie/loss counts, and results
split by processing era. Identical scored samples throughout (gate V7).

## Deferred

- **S7.9:** instantiated baseline configurations, hashed.
- **S7.10:** executed comparison on external protected blocks.
