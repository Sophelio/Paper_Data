# S7.K2 — Observational range support

Machine-readable: `RANGE_SUPPORT_POLICY_V1.json`,
`manifests/RANGE_SUPPORT_CONCEPT.json`, `manifests/RANGE_SUPPORT_DESIDERATA.json`.

---

## The concept, before any number

> For a coordinate `c`, a local calibration interval and an application
> interval, let `S_cal(c)` be the empirical support of `c` on calibration — the
> values actually observed. The coordinate remains **mathematically** defined
> outside `S_cal(c)`, but its use inside a calibration-fitted relation is
> **empirically unsupported** when its application values move sufficiently far
> beyond `S_cal(c)`.

Observational range support is a property of the **triple** (coordinate,
calibration interval, application interval) — never of the constructor type
alone.

### Three admissibility notions, kept distinct

| | asks |
|---|---|
| **symbolic admissibility** | is the coordinate well formed in `G_rec`? |
| **mathematical domain admissibility** | is the coordinate map *defined* on the observed inputs? (`DENOMINATOR_ADMISSIBILITY_PRIMARY_V1`, unchanged) |
| **observational range applicability** | is the *fitted relation* empirically supported where it is applied? (**new**) |

These must not be collapsed. Denominator stability asks whether the map is
defined; range support asks whether the relation is supported. `x²` is defined
everywhere and can still be unsupported. Conversely a denominator can be
perfectly admissible on calibration while the ratio still leaves its calibration
range.

**Empirical confirmation that they are distinct:** across all 10,778 atoms × 186
blocks there are **zero** non-finite coordinate-cells. The denominator condition
is not the binding constraint anywhere in the atomic universe, so range support
is not a restatement of it.

## The frozen desiderata

Fourteen criteria were hashed **before** any candidate was computed
(`ef5054345f1a2cbc`): target-blind · model-error-blind · dimensionless ·
unit-scale invariant · sign-symmetric · constructor-generic · local ·
application-aware · monotone · auditable · no epsilon · degenerate-safe · not
special-cased · partial-application semantics.

Selection was permitted on mathematics, stability, breadth, interpretability and
constructor neutrality — and **forbidden** on whether any Epoch-1 block is
flagged, whether `C_dev_star` would pass, or the S7.11 70/143 partition.

## The frozen metric

```
L = min(c_cal)          U = max(c_cal)

E(c,s,b) = max( L − min(c_app),  0,  max(c_app) − U ) / (U − L)
```

> **How far beyond the calibration hull the application values reach, measured
> in units of the calibration range itself.**

Only four numbers are needed per block — the calibration and application
extrema. Dimensionless, invariant under `c → k·c`, symmetric in both
directions, monotone, and identical for every constructor family.

### Why this, and not hull-excess over calibration RMS

Both candidates satisfy every desideratum except one, and they separate sharply
on **D6, constructor genericity**:

| | p90 spread across the 7 families | ratio |
|---|---|---|
| **selected** — excess / calibration **range** | 0.032 … 0.139 | **4.3** |
| rejected — excess / calibration **RMS** | 0.029 … 1.029 | **35.1** |

RMS-normalisation systematically inflates rate-bearing families (C1, C6, C7),
because dividing by calibration RMS penalises coordinates whose calibration mean
sits near zero — a property of the constructor, not of range support. Dividing
by the calibration **range** uses the natural scale of the empirical support
itself, and is constructor-neutral by construction.

A third robust candidate (IQR/MAD) was **not needed**: only 263 of 2,004,708
coordinate-cells (0.013 %) are degenerate under either candidate, so neither is
ill-defined over any meaningful part of the universe.

## Degenerate calibration — explicit, never epsilon

If `U − L = 0` the coordinate is constant on calibration:

- if every application value equals that constant → `E = 0`, supported;
- otherwise → **`RANGE_SUPPORT_DEGENERATE_CALIBRATION`**, an explicit status,
  **not** a pass.

No epsilon is substituted anywhere. Observed rate: 263 / 2,004,708 cells.

## The threshold

```
τ = 1
```

**Application values may extend no farther beyond the calibration hull than one
full calibration range.**

The grid `{0, 0.25, 0.5, 1, 2, 5, 10}` was written and hashed
(`98951146f6ff13a5`) **before any applicability count was inspected**.

| τ | cell applicability | full-domain atoms | fraction |
|---|---|---|---|
| 0 | 0.802 | **9** | 0.001 |
| 0.25 | 0.946 | 1 026 | 0.095 |
| 0.5 | 0.971 | 2 099 | 0.195 |
| **1** | **0.986** | **3 451** | **0.320** |
| 2 | 0.994 | 5 957 | 0.553 |
| 5 | 0.998 | 8 722 | 0.809 |
| 10 | 0.999 | 9 559 | 0.887 |

`τ = 0` is strict interpolation and is destructive — nine atoms survive. Larger
values permit progressively more extrapolation with progressively weaker
interpretation. `τ = 1` is the one grid value with a one-sentence reading, it
sits inside a broad monotone stability region, and every constructor family
survives it.

One significant figure. No six-decimal thresholds.

## Local coordinate rule

```
RANGE_SUPPORT_PASS(c,s,b)   iff   E(c,s,b) ≤ τ   and not degenerate
failure status              →     RANGE_SUPPORT_NOT_APPLICABLE
```

This is **local**. It never means the coordinate is globally inadmissible —
`PROD(x,x)` stays in `G_rec` and `A_rec`; only the fitted relation is
unsupported on that particular block.

## Support rule — conservative, all-coordinate

```
RANGE_SUPPORT_PASS(C,s,b)   iff   every coordinate c_j ∈ C passes on that block
support score               =     max_j E(c_j,s,b)
```

No averaging. No support-level cancellation. The failing coordinate must remain
identifiable — the audit trail is the point.

## The closure property that makes Epoch 2 viable

Because the support predicate is the **conjunction** of coordinate predicates
over the *same* cells:

> If every coordinate of a support is individually full-domain, the support is
> automatically full-domain.

So a search restricted to the 3 451 full-domain coordinates yields full-domain
supports **by construction** — roughly 10³³ of size 12 — with no need to erase
anything from `A_rec`.
