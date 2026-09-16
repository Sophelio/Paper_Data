# S7.8 — Support stability protocol (Rank 5)

The inherited `U_rec` requires support stability "under development-shot
resampling and fold perturbation". This document freezes that procedure. It is
executed in **S7.9**, not here.

Machine-readable form: `support_stability_policy.json`.

---

## What this procedure is, and is not

It is an **analyst-defined qualification procedure** and must be labelled as
one. `E` is not instantiated in this study, so:

- **no** measurement-error weights;
- **no** description of these numerical perturbations as observational
  uncertainty;
- what is measured is **selection stability**, never measurement error.

It **does not modify `Ahat_rec`** and **does not rerun the S7.7 search**. It
tests stability *within* the frozen explored frontier: would the frozen utility
rule have landed on the same representation had the 20 development discharges,
or the three temporal blocks, come out slightly differently?

## 1. Discharge bootstrap

| | |
|---|---|
| replicates | **1000** |
| unit | development discharge |
| draw | 20 discharges **with replacement** |
| seed | **2026090501** |
| generator | `numpy.random.default_rng(2026090501)` |
| draw order | replicates drawn in sequence from a single stream; replicate *r* is the *r*-th draw |
| resampled | discharge indices **only** — the three blocks are never resampled |

A resampled multiset enters every discharge-level aggregation as **integer
multiplicities**: `FIT`, `BLOCK_WORST`, `SHOT_P90` and the 60-cell conditioning
summaries are all recomputed with those weights. With all multiplicities equal
to 1 the weighted computation reproduces the plain one exactly (verified in the
dry run).

For each replicate:

1. retain the same candidate frontier `Ahat_rec`;
2. recompute utility **Ranks 1–4** using the resampled discharge indices;
3. identify the **Rank-4 winner** under the frozen algorithm.

> The replicate count is fixed at 1000 **before** any stability outcome exists
> and **may not be reduced after inspecting outcomes**.

### Not the same bootstrap as the inference plan

`STATISTICAL_INFERENCE_PLAN.md` requires **≥ 10 000** replicates for the paired
discharge bootstrap that produces confidence intervals on **gate comparisons**
at S7.10. That is a different procedure at a different stage for a different
purpose. Both stand; neither replaces the other, and the parent count is not
modified.

## 2. Fold perturbation

Exactly three perturbations — **omit block A**, **omit block B**, **omit block
C**. For each:

- recompute utility Ranks 1–4 over the remaining two blocks (40 cells);
- `NRMSE_s` becomes the mean over the two remaining blocks;
- `BLOCK_WORST` becomes the max over the two remaining blocks;
- the search is not altered and support identities are not altered.

## 3. Candidate stability scores

Evaluated over the candidates surviving the **original, unresampled** Ranks 1–4
— that is, over `E4`.

```
BOOT_SELECTION_FREQ(C) = fraction of the 1000 bootstrap replicates
                         in which C is the Rank-4 winner
FOLD_SELECTION_FREQ(C) = fraction of the 3 block-omission perturbations
                         in which C is the Rank-4 winner
```

**Rank-4 winner** means the canonical-first element of `E4` under that replicate
or perturbation — the unique candidate that Ranks 1–4 plus the canonical
support-id tie-break resolve to.

There is no circularity: the winner is defined by Ranks 1–4 only, and Rank 5
consumes it.

## 4. Rank-5 ordering

1. maximize `BOOT_SELECTION_FREQ`;
2. maximize `FOLD_SELECTION_FREQ`;
3. canonical support ID tie-break.

> **No pass/fail threshold is introduced.** Support stability is a
> ranking/qualification quantity, **not a gate**. A low selection frequency is a
> finding to report, not a disqualification.

## 5. Computation

Ranks 1–3 are pure functions of the 162 845 × 60 NRMSE matrix and the registry
`support_size`, so all 1000 replicates are evaluated by weighted matrix
reductions rather than per-candidate loops.

Per-cell `kappa` does **not** depend on the discharge resample, so conditioning
may be computed lazily and memoized for the candidates that reach Rank 4 in any
replicate. This is an efficiency measure and changes no defined quantity.

Requirement: identical inputs must yield an identical `E5` across runs and
machines.

## 6. What may not happen

- reducing the replicate count after seeing stability;
- changing the stability quantiles after seeing candidate behaviour;
- converting `BOOT_SELECTION_FREQ` into a pass/fail gate;
- resampling blocks instead of discharges;
- rerunning the search inside a replicate.
