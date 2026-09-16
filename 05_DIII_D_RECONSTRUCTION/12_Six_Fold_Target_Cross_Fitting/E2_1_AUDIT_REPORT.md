# S7.E2.1 — Cross-fitted discovery and qualification: internal audit report

Stage **S7.E2.1** · Freeze `D3D-SIR-S7.E2.1-CROSSFITTED-DISCOVERY-AND-QUALIFICATION-V1`
Execution protocol `E2_0A_PROTOCOL` · Contract `K_REC_V2`

---

## 1. Executive verdict

**`QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS`** · 38/38 acceptance.

`FORMAL_PASS` — V3, V6 and V-RANGE all pass. `CLEAN_DEMO_NOT_MET` — the
prospective reporting tier is missed on two of five criteria. The two are
reported separately and not collapsed.

## 2. Parent integrity

**S7.9 45/45 · S7.10 31/31 · S7.11 26/26 · S7.R1 21/21 · S7.K2 29/29 ·
S7.E2.0 22/22 · S7.E2.0A 14/14** reproduce byte-for-byte. E2.0A authoritative,
E2.0 preserved, `K_REC_V2` unchanged, `tau = 1`, `tau_train` RETIRED, V3/V6,
budget, seed policy, shortlist cap, support bound and stop rule all as frozen.

## 3. Basis verification — before any target opened

Recomputed independently from the frozen coordinate universe, frozen predictors
and `P-RANGE` at `tau = 1`:

**3 451 / 10 778** · C0 51 · C1 18 · C2 1 488 · C3 382 · C5 8 · C6 965 · C7 539 ·
**id-set hash matches `E2_0A_CANDIDATE_BASIS.json`**. `target_reads = 0` through
completion of the pre-search stage.

## 4. Search execution

Six fresh searches over the common basis under `SIGMA_REC_ONE_SEED_PRIMARY_V2`,
adapted mechanically. 108 strata, 461-coordinate shortlist, one seed per stratum,
support bound 1–12, MAIN and RAW_ONLY lanes.

| fold | proposals | unique supports | budget | within |
|---|---|---|---|---|
| 0 | 127 657 | 105 548 | 300 000 | yes |
| 1 | 127 665 | 105 112 | 300 000 | yes |
| 2 | 127 643 | 101 183 | 300 000 | yes |
| 3 | 127 440 | 99 632 | 300 000 | yes |
| 4 | 127 764 | 105 365 | 300 000 | yes |
| 5 | 127 589 | 103 940 | 300 000 | yes |

**Total 765 758 of 1 800 000.** No budget issue; no outcome-triggered expansion;
no two-seed; the Epoch-1 frontier was neither reused nor re-ranked.

**One implementation defect was found and fixed before any scientific run.** An
initial pass re-parsed support ids by splitting on the pipe character — exactly
the hazard K2 documented for C4/C6/C7/C8 signatures. It raised a `KeyError`
immediately, was fixed by carrying index tuples so no naive split exists anywhere
in the pipeline, and **no result was produced under the defective code**.

## 5. Non-interactive execution

All six folds ran in a single background process under one frozen policy. No fold
was inspected to decide how to run another; no fold was re-run; the run was not
stopped or altered mid-execution.

## 6. Selection

`U_rec` loaded from the authoritative frozen artifact, not rewritten. In **every
fold** `E1` reduced to `E2 = 1`, so Ranks 3–5 were non-binding — the same
structure as Epoch 1, where Rank 2 was decisive.

| fold | E1 | E2/E3/E4/E5 | dev FIT | `COND_MEDIAN` | boot freq | unique boot winners |
|---|---|---|---|---|---|---|
| 0 | 2 639 | 1 | 0.1756 | 2.151 | 0.121 | 320 |
| 1 | 3 065 | 1 | 0.1772 | 1.708 | 0.007 | 336 |
| 2 | 2 933 | 1 | 0.1786 | 1.766 | 0.009 | 379 |
| 3 | 8 502 | 1 | 0.1748 | 1.443 | 0.001 | 443 |
| 4 | 6 907 | 1 | 0.1625 | 1.660 | 0.023 | 386 |
| 5 | 1 898 | 1 | 0.1654 | 1.566 | 0.072 | 303 |

Bootstrap selection frequencies are again low (0.001–0.121, 303–443 distinct
winners per fold), reproducing the Epoch-1 finding that development selection does
not identify a unique support.

## 7. Ordering discipline

Per fold: identities hashed, `D_train` targets opened, search, `U_rec`, support
written and **hashed**, estimator and baselines frozen, V-RANGE recomputed,
held-out **calibration** targets opened, local coefficients, baselines, held-out
**protected** targets opened **last**, scored, fold frozen.

Target access is gated by a vault that raises `FIREWALL` on any read of a
discharge's targets before they are opened, and every open is timestamped in
`E2_1_ACCESS_AUDIT.json`. **The support hash precedes held-out target access in
all six folds**, verified programmatically.

## 8. V-RANGE integrity

**2 232 held-out coordinate-block checks, 0 failures, all six folds PASS** —
exactly the pass-by-construction the K2 closure property predicts. No
inconsistency arose, so the audit-stop path was not triggered.

## 9. Cross-fitted result

62 out-of-fold discharge results, one per discharge, from the support of the fold
in which it was held out. In-fold development scores contribute nothing.

`Delta_0 = -0.764489` · `Delta_1 = -0.027308` · **V3 PASS**.

REL mean 0.1891, median 0.1515, p90 0.2959, **max 0.9199**. Against B0 62/0/0;
against B1 32/5/25; against B2 39/7/16; against B3 37/4/21; against H0 37/7/18;
against B1A 55/2/5.

## 10. V6

| era | n | `Delta_0` | `Delta_1` | direction vs B1 |
|---|---|---|---|---|
| earlier | 35 | −0.7017 | **+0.0076** | `PRACTICAL_TIE` |
| later | 27 | −0.8459 | **−0.0726** | `MATERIAL_IMPROVEMENT` |

Pooled V3 passes, no era is `MATERIAL_ADVERSE`, at least one is a practical tie →
**`PASS_WITH_QUALIFICATION`**, applied exactly as frozen in E2.0. No era rescued
another; both are reported.

## 11. The hardening worked

| | Epoch 1 | Epoch 2 |
|---|---|---|
| mean / median NRMSE | 0.7424 / 0.1699 | 0.1891 / 0.1515 |
| max NRMSE | **11.95** | **0.92** |
| discharges above 1.0 | 2 | **0** |
| 187019 / 187022 | 11.95 / 11.77 | **0.297 / 0.436** |

The catastrophic extrapolation tail is gone, and the two discharges that destroyed
Epoch 1 now reconstruct unremarkably. This is the strongest evidence that the
R1 to K2 reconciliation localized the right defect.

## 12. Worst held-out discharges

| shot | era | fold | REL | B1 | B2 |
|---|---|---|---|---|---|
| 187024 | earlier | 4 | 0.9199 | 0.5485 | 0.5025 |
| 161136 | earlier | 1 | 0.4383 | 0.6092 | 0.3157 |
| 187022 | earlier | 3 | 0.4356 | 0.2345 | 0.6637 |
| 189646 | later | 5 | 0.3480 | 0.2538 | 0.7609 |

No pathology: the worst is 0.92, comfortably below 1.0, and on two of the four the
relational representation beats persistence or raw ridge.

## 13. CLEAN_DEMO_PASS

| criterion | |
|---|---|
| FORMAL_PASS | yes |
| `Delta_1 <= -0.05` | **no** (−0.0273) |
| full cross-fitted range support | yes |
| no discharge above NRMSE 1.0 | yes |
| both eras material improvement vs B1 | **no** |

**`CLEAN_DEMO_NOT_MET`.** The threshold was frozen before the run and was not
adjusted; the tier was not promoted to a gate; the formal pass stands.

## 14. Support stability

Six supports, all size 12, **none identical**, mean pairwise Jaccard 0.285, 35
distinct coordinates. In all six: `ID(pcdiamag3)`, `RATIO(ece21,cerqtit10)`.
Constructor recurrence C3 34 · C2 16 · C5 11 · C0 7 · C6 2 · C7 2. Descriptive
only; no gate created. See `E2_1_SUPPORT_STABILITY.md`.

## 15. Gate table

| gate | result |
|---|---|
| V1 information boundary | INHERITED_PASS |
| V2 development-only discovery | PASS (target cross-fitting) |
| **V3 nontrivial skill** | **PASS** |
| V4 fair raw comparison | PASS |
| V5 structural transfer / freeze discipline | PASS |
| **V6 processing-era robustness** | **PASS_WITH_QUALIFICATION** |
| V7 common support | PASS |
| V8 discharge-level inference | PASS |
| **V-RANGE applicability** | **PASS** |
| V10 numerical provenance | INHERITED_PASS |

No mandatory gate failed.

## 16. Stop rule

`EPOCH2_IS_FINAL_QREC_ATTEMPT = true`, respected. Epoch 2 passed, so no further
epoch arises. Nothing tuned, no threshold moved, no discharge or block removed, no
support repaired, no two-seed rescue, no budget extension. The optional all-data
descriptive representation was **not** run and awaits separate authorisation.

## 17. Files

6 Markdown (limit 20) · 8 CSV · 7 JSON · 12 fold artifacts · 4 manifests ·
4 scripts.

## 18. Recommendation

`q_rec` now has a **formal positive result** and, more importantly, a complete and
auditable iterative-discovery arc. The methodological story belongs in the main
text. The accuracy claim should be stated with its two limits attached: the margin
over persistence is modest and era-asymmetric, and predictor-side applicability
used the whole finite object.

`PAPER_UTILITY = MEDIUM_HIGH` — high for the method demonstration, moderate for
the reconstruction claim itself.
