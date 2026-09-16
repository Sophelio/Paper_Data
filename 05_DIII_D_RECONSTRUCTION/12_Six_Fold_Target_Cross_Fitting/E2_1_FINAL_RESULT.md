# S7.E2.1 — Cross-fitted discovery and qualification: result

Freeze **`D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1`**
Status **`QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS`** · 38/38 acceptance

```
FORMAL_PASS          — the frozen scientific gates pass
CLEAN_DEMO_NOT_MET   — the prospective reporting tier is not reached
```

---

## The gates

| | | |
|---|---|---|
| `Δ₀` vs calibration mean | **−0.764489** | clears −0.01 |
| `Δ₁` vs persistence | **−0.027308** | clears −0.01 |
| **V3** | | **PASS** |
| **V6** | earlier `+0.0076` tie · later `−0.0726` improvement | **PASS_WITH_QUALIFICATION** |
| **V-RANGE** | 2 232 checks, **0 failures** | **PASS** (by construction, as predicted) |
| discharges with NRMSE > 1 | **0** | |

## Cross-fitted performance, 62 out-of-fold discharges

| method | mean | median | p90 | max |
|---|---|---|---|---|
| **REL** | **0.1891** | **0.1515** | 0.2959 | **0.9199** |
| B0 calibration mean | 0.9536 | 0.9365 | | |
| **B1 persistence** | 0.2164 | 0.1744 | | |
| B1A AR(1) | 0.3563 | 0.3329 | | |
| B2 raw ridge (78) | 0.2851 | 0.1972 | | |
| B3 raw HistGB (78) | 0.3464 | 0.1960 | | |
| H0 hardened ridge (70) | 0.2842 | 0.1914 | | |

| paired vs | mean `Δ` | median `Δ` | W/T/L |
|---|---|---|---|
| B0 | −0.7645 | | 62/0/0 |
| **B1** | **−0.0273** | | **32/5/25** |
| B1A | −0.1671 | | 55/2/5 |
| B2 | −0.0960 | | 39/7/16 |
| B3 | −0.1573 | | 37/4/21 |
| H0 | −0.0951 | | 37/7/18 |

## The contract hardening worked

| | Epoch 1 | **Epoch 2** |
|---|---|---|
| mean NRMSE | 0.7424 | **0.1891** |
| median NRMSE | 0.1699 | **0.1515** |
| **max NRMSE** | **11.95** | **0.92** |
| discharges > 1.0 | 2 | **0** |
| 187019 | 11.95 | **0.297** |
| 187022 | 11.77 | **0.436** |

The range-support condition eliminated the catastrophic extrapolation tail
entirely. That was its purpose, and it is the clearest single piece of evidence
that the reconciliation chain — failure, refuted state hypothesis, `P_rec`
localization, generic hardening — identified the right defect.

## Execution

Six folds, one frozen policy, non-interactive. Per fold: 108 strata, 461-coordinate
shortlist, ~127 600 proposals (budget 300 000), ~100 000–105 500 unique supports
explored, ~65 s search. **765 758 proposals total** against a 1 800 000 budget.

| fold | frontier | E1 | E2→E5 | dev FIT | `COND_MEDIAN` | boot freq | support sha |
|---|---|---|---|---|---|---|---|
| 0 | 105 548 | 2 639 | 1 | 0.1756 | 2.151 | 0.121 | `4654cd92…` |
| 1 | 105 112 | 3 065 | 1 | 0.1772 | 1.708 | 0.007 | `c3206098…` |
| 2 | 101 183 | 2 933 | 1 | 0.1786 | 1.766 | 0.009 | `08fd3481…` |
| 3 | 99 632 | 8 502 | 1 | 0.1748 | 1.443 | 0.001 | `e69c6efc…` |
| 4 | 105 365 | 6 907 | 1 | 0.1625 | 1.660 | 0.023 | `688791d4…` |
| 5 | 103 940 | 1 898 | 1 | 0.1654 | 1.566 | 0.072 | `358854514…` |

Rank 2 was decisive in every fold, as in Epoch 1: `E2` collapsed to a singleton
each time, so parsimony, conditioning and support stability were non-binding.

## Why `CLEAN_DEMO_PASS` was not met

Two of its five criteria fail:

| criterion | |
|---|---|
| FORMAL_PASS | ✔ |
| `Δ₁ ≤ −0.05` | ✗ — achieved −0.0273 |
| full cross-fitted range support | ✔ |
| no discharge above NRMSE 1.0 | ✔ |
| both eras material improvement vs B1 | ✗ — earlier era is a practical tie |

The threshold was frozen before the run and is **not** adjusted. A formal pass
that misses the reporting tier remains a formal pass.

## Honest reading

The pooled pass over persistence is **carried by the later era**. In the earlier
era (35 discharges) the relational representation and persistence are practically
tied at `+0.0076`; in the later era (27) the improvement is `−0.0726`. At the
discharge level the record against persistence is 32–5–25.

Against every **raw-coordinate** comparator the margin is wide and unambiguous:
−0.096 against ridge on all 78 predictors, −0.157 against gradient boosting on
the same basis, −0.095 against the hardened-basis ablation. Persistence is simply
a demanding baseline for a slowly varying target.

Notably, the pooled `Δ₁ = −0.0273` sits almost exactly at the ceiling S7.11
identified in Epoch 1, where no member of the 217-support family beat persistence
by more than 0.0287. Two epochs, two contracts and nine independent searches
arrive at the same margin — which suggests it is a property of the object and the
task, not of any particular support.

## Support non-uniqueness

Six folds, six different supports, all size 12, mean pairwise Jaccard **0.285**,
none identical, 35 distinct coordinates in total. Only `ID(pcdiamag3)` and
`RATIO(ece21,cerqtit10)` appear in all six. Level–level ratios dominate (34 of 72
slots). See `E2_1_SUPPORT_STABILITY.md`.

**Stable utility, non-unique supports** — the Epoch-1 lesson, reproduced under a
different contract.

## Stop rule

`EPOCH2_IS_FINAL_QREC_ATTEMPT = true`, and it is respected: Epoch 2 passed, so no
further epoch arises. Nothing was tuned, no threshold moved, no discharge or block
removed, no support repaired, no two-seed rescue, no budget extension, and the
optional all-data descriptive search was **not** run.
