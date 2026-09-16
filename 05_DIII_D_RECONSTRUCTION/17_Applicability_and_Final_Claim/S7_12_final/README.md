# S7.12 — Final qualified reconstruction result

Freeze **`D3D-SIR-S7.12-QUALIFIED-RECONSTRUCTION-RESULT-V1`**
Status **`Q_REC_FINAL_QUALIFIED_POSITIVE_RESULT`** · 36/36 acceptance

```
Q_REC_STATUS      = QUALIFIED_POSITIVE_RECONSTRUCTION_FORMAL_PASS
CLEAN_DEMO_STATUS = CLEAN_DEMO_NOT_MET
Q_REC_BRANCH_CLOSED = true
```

**The `q_rec` branch is closed.** No Epoch 3, no S7.13, no further search.

---

## The claim

> Within the predictor-qualified frozen 62-discharge observational object,
> relational supports discovered **without a discharge's own target values**
> reconstruct that discharge **nontrivially relative to the frozen baselines**.

`PREDICTOR_QUALIFIED` · `TARGET_CROSS_FITTED` · `RECONSTRUCTION`.

Not external validation. Not a claim about unseen or future discharges. Not a
universal DIII-D relation. Not a unique equation.

## The result

| | | | |
|---|---|---|---|
| `Δ₀` vs calibration mean | **−0.764489** | REL mean | 0.1891 |
| `Δ₁` vs persistence | **−0.027308** | median | 0.1515 |
| **V3** | **PASS** | p90 | 0.2959 |
| **V6** | **PASS_WITH_QUALIFICATION** | max | **0.9199** |
| **V-RANGE** | **PASS** (2 232 / 0) | discharges > 1.0 | **0** |

vs raw ridge **−0.096** · vs raw gradient boosting **−0.157** · vs hardened raw
ablation **−0.095** · vs persistence **32–5–25**.

Earlier era (35): `Δ₁ = +0.0076`, practical tie. Later era (27):
`Δ₁ = −0.0726`, material improvement. **The pooled pass is carried by the later
era.**

## The arc

```
Epoch 1 discovery
   -> external qualification FAILED   (mean 0.74, max 11.95, 2 catastrophic)
   -> provenance: extrapolation of PROD(gasa,gasa)
   -> operational-state explanation PROPOSED
   -> R1 tested it target-blindly and REFUTED it
   -> defect localized to P_rec, not X_rec
   -> K2 added a generic range-support predicate, tau = 1, frozen first
   -> E2.0A clarified the transition-specific information boundary
   -> Epoch 2 searched afresh, cross-fitted
   -> FORMAL PASS, and the catastrophic tail disappeared
```

| | Epoch 1 | Epoch 2 |
|---|---|---|
| max NRMSE | **11.95** | **0.92** |
| discharges > 1.0 | 2 | **0** |
| 187019 / 187022 | 11.95 / 11.77 | **0.297 / 0.436** |

## `Q_rec*` is a family, not an equation

Six folds → six different supports, all size 12, none identical, mean Jaccard
0.285, 35 distinct coordinates. A seventh full-object search produced a seventh
distinct support.

> **Stable reconstruction utility with non-unique relational supports.**

`C_E2_ALL_DESC` (E2.2) is carried as a **representative** descriptive
realization — not unique, not held out, not externally validated, not canonical.

## Start here

| Document | Purpose |
|---|---|
| `S7_12_QUALIFIED_RESULT_FINAL.md` | the result in full, 11 sections |
| `S7_12_MANUSCRIPT_SUMMARY.md` | drop-in main-text and supplement text |
| `S7_12_CLAIM_BOUNDARY.md` | what may and may not be written |
| `S7_12_SUPPLEMENT_SUMMARY.md` | supplement structure and Figure-6 handoff |
| `S7_12_QUALIFIED_RESULT_AUDIT_REPORT.md` | internal audit, 11 sections |

Machine-readable: `Q_REC_STAR.json` · `Q_REC_PROVENANCE_CHAIN.json` ·
`Q_REC_GATE_TABLE.json` · `Q_REC_LIMITATIONS.json` ·
`Q_REC_BRANCH_CLOSURE.json` · `FIGURE_6_HANDOFF.json`.

## Reproduce

```bash
python scripts/s7_12_assemble.py   # verify 13 parents, assemble, freeze
```

Assembly only: no search, no fit, no gate evaluation, no new metric. Every number
is read from a frozen parent record and carried unchanged.
