# Information-flow and leakage audit

Adversarial audit of what information reached which stage. Conducted knowing
that the **previous** DIII-D reconstruction lineage was retired for exactly this
class of defect.

Two policies are kept apart throughout, following the current architecture:

- **`I_q`** — what information is *epistemically admissible* to the scientific
  task at all.
- **`V_q`** — what *evidentiary role* admissible information may play, and what
  qualification tests the resulting claim must satisfy.

Evidence roles are **variable- and transition-specific**. A discharge does not
carry one global "development" or "validation" status for every transition: its
predictor observations may be admissible for applicability assessment while its
held-out target values remain prohibited from support discovery. That is a `V_q`
statement, not an `I_q` one, and §3 is a table of exactly such
transition-specific roles.

Machine-readable: `INFORMATION_FLOW_AUDIT.json`.

---

## 1. Target ancestry

`q_rec` target: **`density`**, line-averaged electron density.

Of 95 quantities in the scientific object, **78 are admitted** and **17 are
excluded**:

| rule | n | signals |
|---|---|---|
| `R1_target_itself` | 1 | `density` |
| `PRIMARY_NUMERICAL_SUPPORT_FAIL` | 1 | `vsurf` |
| `R5_unresolved_ancestry` (fail-closed) | 15 | `aminor`, `area`, `betan`, `drsep`, `kappa`, `li`, `q95`, `rmaxis`, `rsurf`, `tribot`, `tritop`, `volume`, `zcur`, `zmaxis`, `zsurf` |

The 15 fail-closed exclusions are every EFIT-derived equilibrium quantity:
*"LINEAGE_PARTIAL: EFIT settings/inputs unresolved; independence from the target
cannot be certified (fail-closed)."*

**This is the decisive structural difference from the retired branch.** The
retired `I_p` branch admitted `q95`, `betan`, `li` and `kappa`, and died of it —
`q95` proved to be essentially `shape·a²B_t/I_p`, leaving only 7.3 % residual
scatter after algebraic removal of the target. Here the same class of quantity is
excluded *before* coordinate construction, on provenance grounds, without
inspecting any performance.

**Verified:** the target does not appear as its own predictor; no admitted
coordinate has target ancestry; every one of the 38 selected coordinates across
the six qualified supports and the descriptive support lies inside the qualified
basis.

## 2. The `prmtan_neped` question

`prmtan_neped` — pedestal electron density from a tanh fit — is in the same
`density` scientific family as the target, and it appears in **all six** fold
supports and in `C_E2_ALL_DESC`. It is the single highest-risk admission in the
branch, so it was tested with the same instrument that retired the `I_p` branch.

| | `q95` vs `I_p` (**retired**) | `prmtan_neped` vs `density` | `pcdiamag3` vs `density` |
|---|---|---|---|
| median &#124;corr&#124; | 0.945 | 0.892 | 0.897 |
| median R² (single signal) | 0.79 | 0.796 | 0.804 |
| **residual scatter after removing it** | **7.3 %** | **53.5 %** | **44.2 %** |

Correlation and single-signal R² look similar. **The decisive statistic does
not.** After removing the best per-shot affine function of `prmtan_neped` from
the target, **53.5 %** of the target's standard deviation remains, against
**7.3 %** for `q95`/`I_p`. `q95` *was* the target algebraically; `prmtan_neped`
is not.

This repository's own audit already established the governing principle, and
recorded correcting itself on it:

> "Ancestry is definitional/computational, not statistical … those three are
> direct diagnostics that co-evolve with `I_p` within a discharge. Corrected;
> correlation is now reported as context only."

The frozen, **predeclared** ablation settles it directly. `PRMTAN_NEPED_ONLY` —
that single coordinate, same estimator, same metric — scores mean NRMSE
**0.4632** with `Δ₁ = +0.2529`, and **fails** the V3-style criterion. A
coordinate that were algebraically circular with the target would not.

Two qualifications stand, and are carried in `S7_11_QUALIFICATIONS.json`:

> Provenance certification establishes no target-*signal* ancestry. It does
> **not** establish physical or statistical independence from line-averaged
> density.

Only 2 of 78 predictors reach median R² ≥ 0.75 against the target
(`pcdiamag3` 0.804, `prmtan_neped` 0.796), and both are direct diagnostics of
different instruments.

## 3. Stage-by-stage information flow

| Stage | Target values available | Held-out targets | Predictors | Verified by |
|---|---|---|---|---|
| S7.1 | none | — | all 95, provenance only | freeze: no target selected |
| S7.2/2C | none | — | none | `no_target_selected = true` |
| S7.3V2 | target identity only | — | 78 admitted | boundary CSV |
| S7.4V2–S7.7R | development only | sealed | 78 | `external_cohort_state = SEALED` |
| S7.9 | **development only** | sealed | 78 | `external_predictor_reads = 0`, `external_target_reads = 0`, `FIREWALL_INTACT` |
| S7.10 | development + external | **opened here, once** | 78 | freeze ordering: model frozen 20:32:08 UTC, first external access 22:48:51 UTC |
| S7.11 | as S7.10 | inspected | 78 | sensitivity plan hashed 100.6 s before first external access |
| S7.R1 | **none used** | — | 78, target-blind | explicit prohibition on using target values to define states |
| S7.K2 | **none used** | — | 78, target-blind | `target_blind = true`, `model_error_blind = true`, `epoch1_outcome_used_in_construction = false` |
| S7.E2.1 | per fold: training discharges only | **opened after the support was hashed** | all 62, non-target | access ledger + firewall vault |
| S7.E2.2 | all 62, declared | — | all 62 | `ALL_OBJECT_TARGET_ACCESS_PERMITTED_FOR_DESCRIPTION = true` |

## 4. The nine checks

**1. No target descendant in any explanatory support.** ✅ 17 exclusions applied
before coordinate construction; every selected coordinate is inside the qualified
basis, which is built from the 78 admitted predictors only.

**2. Range support uses no held-out target value.** ✅ The predicate
`E(c) = max(L − min c_app, 0, max c_app − U)/(U − L)` is a function of predictor
values alone. Independently re-implemented here from the policy equation and
reproduced exactly: 3,451 survivors at τ = 1, exact constructor counts, 263
degenerate cells of 2,004,708.

**3. Normalization does not leak protected statistics.** ✅ In the frozen
estimator, `mu` and `sd` are computed from the **calibration slice only**
(`xc`), with `sd ≤ 0 → divisor exactly 1.0`. NRMSE is normalized by
`std(y_calibration, ddof = 0)`. No protected-window statistic enters any fit.

**4. Baselines share the target-availability assumptions.** ✅ B0 (calibration
mean), B1 (last calibration value), B1A (AR(1) fitted on calibration), B2/H0
(ridge on calibration), B3 (gradient boosting on calibration) all read `y_cal`
only, through the same gated accessor as the relational estimator.

**5. Fold construction is target-blind.** ✅ Deterministic: sort by
(processing era, discharge id), assign `position mod 6`. No randomness, no seed,
exactly one partition generated, none scored or compared.
`target_blind = true`, `performance_blind = true`. **Independently reproduced
here** — every one of the 62 assignments.

**6. No support selection saw its own fold's held-out targets.** ✅ Enforced at
runtime by a vault that raises `FIREWALL` on any premature target read, with
every open timestamped. The support hash **precedes** held-out target access in
all six folds, and protected windows are opened last, for scoring only.

**7. No threshold was chosen from held-out performance.** ✅ τ = 1 comes from a
grid frozen with a recorded hash before any survivor count existed; the V3
threshold −0.01 and the `CLEAN_DEMO` threshold −0.05 were frozen before Epoch 2
ran, and `CLEAN_DEMO` was **missed and not moved**.

**8. Global predictor statistics are permitted by the claim actually made.** ✅
Range-support applicability is instantiated from the non-target observations of
the whole finite object. This is a deliberate, documented decision (E2.0A) whose
epistemic cost is carried in the claim: Epoch 2 tests target-relationship
transfer, not predictor-geometry survival on unseen discharges.

**9. Block semantics are consistent.** ✅ Three block-local prequential windows
per discharge — A cal [0, 0.4] prot [0.4, 0.5]; B cal [0, 0.6] prot [0.6, 0.7];
C cal [0, 0.8] prot [0.8, 0.9] — identical for the relational estimator and all
six baselines.

## 5. Residual risks, stated plainly

| Risk | Status |
|---|---|
| the protected-evidence rule was triggered | **Handled and recorded.** Spending the Epoch-1 evaluation evidence on diagnosis materially narrowed `V_rec`, which constituted descendant claim branch `QREC-B2`. See `REVISION_LEDGER.md`. |
| `prmtan_neped` is in the target's scientific family | **Disclosed and bounded.** Not algebraically circular (53.5 % residual scatter; alone it fails V3 at 0.4632). Physical and statistical independence from line-averaged density is **not** claimed. |
| `pcdiamag3` is an uncalibrated signal | **Disclosed.** `UNCALIBRATED_SIGNAL`; its fitted coefficient carries no certified physical-dimensional interpretation, in any support, however often selected. |
| Predictor-side applicability used the whole object | **Disclosed and load-bearing.** It is the principal limitation of the qualified claim and appears in `Q_REC_STAR.json`, not as a footnote. |
| Epoch-1 evaluation evidence informed the Epoch-2 contract | **Disclosed.** Handled by a cross-fitted design *and* an explicitly narrowed claim; Epoch 2 is never described as external validation. |
| The `prmtan_neped` ablation is Epoch-1 | **Noted.** `PRMTAN_NEPED_ONLY` is a property of the primitive and the estimator, not of the selected support, so it bounds the Epoch-2 concern too. No Epoch-2 ablation was run, because running one after seeing the Epoch-2 result would itself be post hoc. |
