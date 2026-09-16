# `Q_rec*` — the final qualified reconstruction result

Freeze **`D3D-SIR-S7.12-QUALIFIED-RECONSTRUCTION-RESULT-V1`**
Status **`Q_REC_FINAL_QUALIFIED_POSITIVE_RESULT`** · 36/36 acceptance

```
Q_REC_STATUS      = QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS
CLEAN_DEMO_STATUS = CLEAN_DEMO_NOT_MET
                    NON_UNIQUE_RELATIONAL_SUPPORTS
                    Q_REC_BRANCH_CLOSED
```

These two statuses are **distinct and must not be blurred**. The formal
scientific result is positive. The more demanding prospective editorial tier was
not reached.

---

## 1. The qualified claim

> Within the predictor-qualified frozen 62-discharge observational object,
> relational supports discovered **without a discharge's own target values**
> reconstruct that discharge **nontrivially relative to the frozen baselines**.

Operationally: `PREDICTOR_QUALIFIED`, `TARGET_CROSS_FITTED`, `RECONSTRUCTION`.

## 2. What it does not support

virgin external validation · untouched external validation ·
unknown-predictor-distribution transfer · fully inductive predictor
generalization · future-discharge applicability · zero-shot transfer · universal
DIII-D relation · universal DIII-D generalization · cross-device generalization ·
unique physical equation · universal coefficient vector.

**These limitations are part of `Q_rec*`, not footnotes outside it.**

The exact qualification that must survive every restatement:
*predictor-side applicability was instantiated from the non-target observations
of the entire finite 62-discharge object.* Epoch 2 therefore tests transfer of
the **target relationship** to withheld targets — not transfer of predictor
geometry to genuinely unseen discharges.

## 3. The numbers

62 out-of-fold discharges, one result each, from the support of the fold in which
that discharge was held out.

| method | mean | median | paired `Δ` | W/T/L |
|---|---|---|---|---|
| **relational** | **0.1891** | **0.1515** | — | — |
| B0 calibration mean | 0.9536 | 0.9365 | **−0.764489** | 62/0/0 |
| **B1 persistence** | 0.2164 | 0.1744 | **−0.027308** | **32/5/25** |
| B1A AR(1) | 0.3563 | 0.3329 | −0.1671 | 55/2/5 |
| B2 raw ridge (78) | 0.2851 | 0.1972 | **−0.0960** | 39/7/16 |
| B3 raw HistGB (78) | 0.3464 | 0.1960 | **−0.1573** | 37/4/21 |
| H0 hardened raw ridge (70) | 0.2842 | 0.1914 | **−0.0951** | 37/7/18 |

REL p90 **0.2959** · max **0.9199** · discharges above 1.0: **0**.

## 4. Gates

| gate | result |
|---|---|
| V1 information boundary | INHERITED_PASS |
| V2 discovery discipline | PASS (target cross-fitting) |
| **V3 nontrivial skill** | **PASS** — both `Δ` clear −0.01 |
| V4 fair raw comparison | PASS |
| V5 freeze discipline | PASS |
| **V6 processing-era robustness** | **PASS_WITH_QUALIFICATION** |
| V7 common support | PASS |
| V8 discharge-level inference | PASS |
| **V-RANGE applicability** | **PASS** — 2 232 checks, 0 failures |
| V10 numerical provenance | INHERITED_PASS |

No mandatory gate failed. No gate was created here, and no threshold moved.

### Era result — reported in full, not averaged away

| era | n | `Δ₁` vs persistence | direction |
|---|---|---|---|
| earlier | 35 | **+0.0076** | `PRACTICAL_TIE` |
| later | 27 | **−0.0726** | `MATERIAL_IMPROVEMENT` |

The pooled pass is **carried by the later era**. It is not true that both eras
improve materially, and this document does not say so.

### `V-RANGE` — an applicability property

`tau = 1`: *application may extend beyond the calibration hull by no more than
one complete calibration-range width.* All 2 232 held-out coordinate-block checks
passed, 0 failed. This passed **by construction**: the 3 451-coordinate
predictor-qualified basis is closed under the support predicate. It is an
applicability property, **not** a performance result.

## 5. Why `CLEAN_DEMO_PASS` was not met

| criterion | |
|---|---|
| FORMAL_PASS | ✓ |
| `Δ₁ ≤ −0.05` | ✗ (−0.027308) |
| full cross-fitted range support | ✓ |
| no discharge above NRMSE 1.0 | ✓ |
| material improvement in **both** eras | ✗ |

The threshold was frozen before the run, was **not adjusted**, and the tier was
**not** promoted to a gate. A formal pass that misses a reporting tier remains a
formal pass.

## 6. `Q_rec*` does not name one representation

The qualification evidence comes from **six** fold-specific representations,
conceptually a family

```
F_rec* = {(C_k*, R_k*)}_{k=1..6}
```

*(conceptual notation only — do not import it into the manuscript without first
deciding whether prose suffices).*

`Q_rec*` therefore carries: the qualified discovery procedure and contract; the
six target-cross-fitted representations and their hashes; their aggregate
out-of-fold evidence; the explicit statement of support non-uniqueness; and,
optionally, `C_E2_ALL_DESC` as a representative full-object descriptive
realization.

| | |
|---|---|
| supports | 6, all size 12 |
| any two identical | **no** |
| mean pairwise Jaccard | **0.285** |
| distinct coordinates | 35 |
| in all six | `ID(pcdiamag3)`, `RATIO(ece21,cerqtit10)` |

A seventh, independent full-object search (E2.2) produced a **seventh distinct
support**, sharing 3–8 of 12 coordinates with the folds and identical to none.

> **Stable reconstruction utility with non-unique relational supports.**
> Observational adequacy does not imply unique mathematical representation.

No fold support is canonical. `C_E2_ALL_DESC` is **representative** — not
unique, not held out, not externally validated.

## 7. The iterative arc

| | |
|---|---|
| 1 | Epoch 1 selected a promising development representation |
| 2 | frozen external qualification **failed**: mean 0.7424, max **11.95**, two catastrophic discharges |
| 3 | provenance localized the failure to extreme extrapolation of `PROD(gasa,gasa)` |
| 4 | an operational-state explanation was proposed |
| 5 | S7.R1 tested it **target-blindly and refuted it** — development already represented stronger gas actuation; no clean actuator state separated the failures |
| 6 | the defect was therefore localized to `P_rec`, **not** to `X_rec` |
| 7 | K2 introduced a generic observational range-support predicate: constructor-generic, dimensionless, `tau = 1`, target-blind |
| 8 | E2.0A clarified the transition-specific information boundary |
| 9 | Epoch 2 searched afresh under `K_REC_V2` |
| 10 | cross-fitted qualification formally **passed** |
| 11 | the catastrophic tail **disappeared** |

| | Epoch 1 | Epoch 2 |
|---|---|---|
| mean | 0.7424 | **0.1891** |
| max | **11.95** | **0.92** |
| discharges > 1.0 | 2 | **0** |
| 187019 | 11.95 | **0.297** |
| 187022 | 11.77 | **0.436** |

**On causal language.** Too many things differ between the epochs — the
contract, the basis, the validation geometry and the supports all changed. The
defensible statements are: *the revised range-support-qualified discovery
procedure eliminated the catastrophic extrapolation tail observed in Epoch 1*,
and *the disappearance of the failure mode is consistent with the reconciliation
having localized the relevant contract defect.* Anything stronger is not
warranted, and "K2 proved the range-support rule caused the improvement" is
explicitly forbidden.

## 8. Representation-level claim

The strongest representation-level result is **not** the persistence comparison.
It is that relational coordinates substantially outperform the tested
raw-coordinate representations of the same admissible information:

**−0.096** vs raw ridge · **−0.157** vs raw gradient boosting ·
**−0.095** vs the hardened raw ablation.

Permitted: *relational coordinate construction adds substantial reconstruction
utility over the tested raw-coordinate representations.* Not permitted:
*universally better than raw features.*

Against persistence, be precise: *the relational representation clears the
prospectively frozen nontrivial skill threshold relative to persistence*, and
*the pooled margin over persistence is modest.* Persistence is a demanding
baseline for a slowly varying target, and Epoch 1's sensitivity analysis found
**no** support in the development-equivalent family beating it by more than
0.0287 — evidence that the ceiling is a property of the object and task, not of
any one representation.

## 9. Information boundary

> The information boundary is **transition-specific**: observations admissible
> for coordinate construction or applicability need not be admissible for
> relation selection. In the reconstruction example, non-target observations
> across the finite scientific object determine range-support applicability,
> while held-out target values remain unavailable to support discovery.

This is a **clarification**, not a new definition of `I_q`. No canonical
notation change is required, and none was made.

## 10. Coefficient and provenance qualifications

- Coefficients are **locally calibrated** per discharge and per block. Support
  transfer does **not** imply coefficient transfer. There is **no universal
  coefficient vector**.
- **`pcdiamag3` remains `UNCALIBRATED_SIGNAL`.** It appears in all six fold
  supports, in `C_E2_ALL_DESC`, and in 100 % of Epoch 1's 217 bootstrap winners.
  Its fitted coefficient has **no certified physical-dimensional
  interpretation**, however often it is selected.
- **`prmtan_neped`** is provenance-certified independent of the target *signal*
  under the frozen information boundary — not physically or statistically
  independent of line-averaged density.
- **`gasa`…`gasd` are actuator command voltages**, not fueling rates.

## 11. Branch closure

```
Q_REC_BRANCH_CLOSED               = true
NO_FURTHER_DISCOVERY_EPOCH_AUTHORIZED = true
EPOCH2_IS_FINAL_QREC_ATTEMPT      = true
```

S7.12 performed no search, no fit, no gate evaluation and no new metric. Nothing
was tuned, no threshold moved, no support rescued, no budget increased, no seed
added, no fold changed, no discharge or block deleted, no baseline or utility
altered. There is no Epoch 3 and no S7.13. `q_desc` is untouched.
