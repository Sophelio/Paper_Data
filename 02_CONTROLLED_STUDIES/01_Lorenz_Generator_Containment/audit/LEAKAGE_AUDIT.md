# Leakage audit

**Date:** 2026-08-27 · **Verdict: PASS**

| # | Check | Result |
|---|---|---|
| 1 | No z / dz / d2z anywhere in the feature DAG | **PASS** — 38 coordinates, 0 violations; the module never indexes a z column |
| 2 | Train / validation / test mutually disjoint | **PASS** — 32 / 8 / 8, pairwise-empty intersections, union = all 48 |
| 3 | Test contributes to no selection step | **PASS** — detail below |
| 4 | Fit-dependent quantities fitted on development data and applied unchanged | **PASS** |
| 5 | Same raw information boundary for the matched baseline | **PASS** — C0 is exactly the x,y stencil the derived coordinates are built from |
| 6 | Masks applied identically across learners | **PASS** — one shared support array per trajectory |
| 7 | Same sample support when comparing methods | **PASS** — identical rows for every method |
| 8 | Retained fraction reported | **PASS** — train 87.98%, validation 88.06%, test 88.52% |
| 9 | Near-perfect performance audited | **PASS** — see "exactness" below |
| 10 | Frozen re-run reproduces metrics | **PASS** — frozen artifact hash verifies; pipeline is deterministic |

## Check 3 — what the protected split touches

Nothing except final scoring. Specifically:

| Quantity | Fitted on |
|---|---|
| operand scales, clearances s_0, mean gains g_bar | train |
| quotient masking floors (5th percentile) | train |
| C* selection | train + validation |
| STLSQ threshold | validation |
| MLP early stopping | internal split of train |
| MLP input scaler | train |

The freeze is load-bearing, not decorative. Refitting the coordinate parameters
on train+test yields materially different constants —

    s_eff(ẏ|x)  3.377100 → 3.378517
    s_eff(ẋ|ẏ)  5.232317 → 5.266778

— and the pipeline uses the train-only values.

## Check 9 — the exactness is structural, not leakage

STLSQ on C* reaches test RMSE 3.3×10⁻⁵ (R² ≈ 1). Rule 9 requires this be
audited before acceptance. The fitted relation is

    z = 28.0000048 − 0.9999995·Q[ẏ|x] − 1.0000067·Q[y|x]

against the analytic identity `z = ρ − (ẏ + y)/x` with ρ = 28 — coefficient
errors ~10⁻⁶.

A leak would not reproduce ρ = 28 and coefficients of exactly −1 from z-free
inputs. Supporting evidence: raw stencil features correlate with z at
|r| ≈ 0.004, while Q[ẏ|x] correlates at 0.996. The exactness is a property of
the Lorenz structure made visible by the representation — it is the finding,
not an artefact.

**Consequence, stated plainly:** because the relation is *exactly* linear in
C*, the noiseless primary benchmark is degenerate at the top end. The predeclared
noise ablation, not the noiseless number, carries the informative comparison.
