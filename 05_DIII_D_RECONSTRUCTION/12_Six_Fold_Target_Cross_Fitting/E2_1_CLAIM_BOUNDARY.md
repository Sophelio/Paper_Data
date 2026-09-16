# E2.1 — Claim boundary

Machine-readable: `E2_1_RESULT.json`, `E2_1_GATE_TABLE.json`.

---

## What Epoch 2 established

```
FORMAL_PASS
QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS
```

> Within the frozen 62-discharge object, relational supports discovered without
> a discharge's own target values reconstruct that discharge nontrivially
> relative to the frozen baselines.

`Δ₀ = −0.7645` and `Δ₁ = −0.0273`, both clearing the frozen `−0.01` threshold.
V-RANGE passed on all 2 232 held-out coordinate-block checks with zero failures.
No out-of-fold discharge exceeded NRMSE 1.0.

## What it does NOT establish

None of the following may be written, whatever the result:

- ✗ virgin external validation
- ✗ untouched external validation
- ✗ unknown-predictor-distribution transfer
- ✗ fully inductive predictor generalization
- ✗ future-discharge applicability
- ✗ zero-shot transfer
- ✗ universal DIII-D relation
- ✗ cross-device generalization

## The two limits that must travel with the claim

**1. Predictor-side applicability used the whole object.** Under E2.0A, the
range-support condition was instantiated from the non-target predictor
observations of all 62 discharges. Epoch 2 therefore tests whether the **target
relationship** transfers to held-out discharges — **not** whether the support's
**predictor geometry** would survive discharges never consulted. This is a real
reduction in what the positive result means and belongs in the text.

**2. The margin over persistence is thin, and era-asymmetric.**

| | `Δ₁` vs persistence | direction |
|---|---|---|
| pooled (62) | **−0.0273** | passes `−0.01` |
| earlier era (35) | **+0.0076** | `PRACTICAL_TIE` |
| later era (27) | **−0.0726** | `MATERIAL_IMPROVEMENT` |

Discharge-level record against persistence: **32 wins, 5 ties, 25 losses**. The
pooled pass is carried by the later era; in the earlier era the relational
representation and persistence are practically tied.

`CLEAN_DEMO_PASS` was **not met**, on two of its five criteria: `Δ₁` does not
reach `−0.05`, and the earlier era is not a material improvement.

## Where the result *is* strong

Against the raw-coordinate comparators the margin is substantial and not
marginal at all:

| comparator | paired mean `Δ` | W/T/L |
|---|---|---|
| B0 calibration mean | **−0.7645** | 62/0/0 |
| B2 raw ridge (78) | **−0.0960** | 39/7/16 |
| B3 raw HistGB (78) | **−0.1573** | 37/4/21 |
| H0 hardened ridge (70) | **−0.0951** | 37/7/18 |
| B1A AR(1) | −0.1671 | 55/2/5 |

The relational construction beats every raw-coordinate alternative by a wide
margin. It is only **persistence** that is close — and for a slowly varying
target like line-averaged density, persistence is the demanding baseline.

The defensible representational statement is therefore: *relational coordinates
add substantial reconstruction utility over raw-coordinate representations of
the same information, and modestly over persistence.*

## Support non-uniqueness

Six folds produced six different supports, mean pairwise Jaccard 0.285, no two
identical. This must be reported as **stable utility with non-unique supports**,
never as identification of a canonical relation. See `E2_1_SUPPORT_STABILITY.md`.

## Preferred wording

> Under the revised range-support-qualified contract, discharge-grouped
> target-cross-fitted discovery produced relational representations that
> reconstructed held-out DIII-D target observations nontrivially relative to
> persistence across the predictor-qualified 62-discharge observational object.

And immediately alongside it:

> Predictor-side applicability used the full finite object's non-target
> observations; the margin over persistence is modest and is carried by the
> later processing era, where the earlier era is practically tied.

Do **not** write "externally validated on unseen discharges."
