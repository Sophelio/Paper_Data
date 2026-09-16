# S7.8 — Utility and qualification rule operationalization

Freeze: **`D3D-SIR-S7.8-UTILITY-AND-QUALIFICATION-RULES-V1`**
Parent: `D3D-SIR-S7.7-ONE-SEED-PRIMARY-SEARCH-AND-EXPLORED-FRONTIER-V2`
Selection domain: `AHAT_REC_DENSITY_ONE_SEED_V2` — 162 845 supports, sizes 1–12

---

## What this stage did

Instantiated the exact operational meaning of the already-frozen `U_rec` and
`V_rec` policies, so that S7.9 can perform development-side selection with no
remaining discretion.

## What this stage did not do

- **did not select `C*`** — no candidate was chosen;
- **did not open the external cohort** — 0 external signal values, 0 external
  target values, cohort `SEALED`;
- **did not run the baseline ladder** — B0/B1/B1A/B2/B3/H0 all `NOT_RUN`;
- **did not compute any utility quantity over `Ahat_rec`**;
- did not modify `Ahat_rec`, `A_rec` or `G_rec`, rerun S7.7, or execute the
  two-seed sensitivity.

S7.7 answered *where did the frozen search look?* S7.8 answers *by what exact
scientific rule will we judge what it found?* It does **not** answer *which
representation wins* — that is S7.9.

## Start here

| Document | Purpose |
|---|---|
| `S7_8_UTILITY_AND_QUALIFICATION_RULES_FINAL.md` | manuscript-ready section |
| `S7_8_UTILITY_AND_QUALIFICATION_AUDIT_REPORT.md` | full internal audit, 23 sections |
| `DEVELOPMENT_SELECTION_PROTOCOL.md` | the exact rule S7.9 executes |
| `SUPPORT_STABILITY_PROTOCOL.md` | Rank-5 resampling procedure |
| `QUALIFICATION_GATE_PROTOCOL.md` | V1–V10 stage ownership |

## The rule in one page

```
estimator : DEVELOPMENT_RELATION_OLS_V1   (OLS, fitted intercept, cell-local coefficients)
metric    : NRMSE_{s,b} = RMSE(protected) / std(y_calibration_{s,b}, ddof=0)
equiv     : delta_equiv = max(SE_delta, 0.01)        # NRMSE units, floor immutable

E0 = Ahat_rec                                                        162 845
E1 = { C : |FIT(C) − FIT_best| <= max(SE_delta(C,best), 0.01) }      Rank 1  fit
E2 = min BLOCK_WORST (practical equivalence), then min SHOT_P90      Rank 2  stability
E3 = min |C|, then min ACTIVE_TERMS                                  Rank 3  parsimony
E4 = min COND_MEDIAN, then COND_P90, then COND_MAX                   Rank 4  conditioning
E5 = max BOOT_SELECTION_FREQ, then FOLD_SELECTION_FREQ               Rank 5  support stability
     final tie-break: canonical support id
```

Lexicographic. No weighted sum, no family penalty or bonus, no ECE penalty, no
C6/C7 pruning, no condition-number cutoff, no stability pass/fail threshold.

## Two findings S7.9 must not miss

**1. The canonical support id cannot be split on the pipe character.**
`PHASE(i|j)`, `LEVEL_RATE(i|j)`, `RATE_OVER_LEVEL(i|j)` and
`LEVEL_OVER_RATE(i|j)` embed a pipe inside their own parentheses. A naive
`split('|')` returns the wrong atom count for **116 608 of 162 845 rows
(71.6 %)**, and the damage concentrates on exactly the C6/C7 families the stage
protects. Split at **parenthesis depth 0 only**, and run the mandatory checksum
against registry `support_size` before computing anything.

**2. The Rank-2 paired standard error is implementable without discretion.**
With each candidate contributing its own worst block,
`mean_s d_s(A,B) = BLOCK_WORST(A) − BLOCK_WORST(B)` exactly (verified to
2.7 × 10⁻¹⁶). The permitted fallback to a 0.01-only floor is therefore
**`NOT_REQUIRED`** and was not invoked.

## Files

**Policies** — `U_REC_OPERATIONAL_V1.json`, `V_REC_OPERATIONAL_V1.json`,
`estimator_policy.json`, `practical_equivalence_policy.json`,
`stability_metric_policy.json`, `conditioning_policy.json`,
`support_stability_policy.json`, `development_selection_algorithm.json`,
`gate_stage_ownership.json`

**Manifests** — `PARENT_FREEZE_VERIFICATION.json`, `ACCESS_AUDIT.json`,
`ALGORITHM_DRY_RUN.json`, `S7_9_REUSE_PRECONDITIONS.json`,
`SEMANTIC_SEPARATION.json`, `CARRY_FORWARD_FINDINGS.json`,
`OUTCOME_BASED_REVISION_AUDIT.json`

**Freeze** — `S7_8_ACCEPTANCE_CHECKS.json`, `S7_8_FREEZE.json`

## Reproduce

```bash
python scripts/s7_8_a_verify_parents.py      # lineage + frontier integrity
python scripts/s7_8_b_build_policies.py      # emit the policy JSONs
python scripts/s7_8_d_algorithm_dryrun.py    # synthetic dry run (no frontier values)
python scripts/s7_8_c_freeze.py              # acceptance checks + freeze
```

Environment: Python 3.13.5, numpy 2.5.2, pandas 3.0.5, Windows-11-10.0.26200-SP0
— identical to S7.7R.

## Boundary

Selection happens **within the frozen explored frontier only**.
`global_optimality_claim = false`. Approximately 5.1 × 10³⁹ admissible support
combinations remain `ADMISSIBLE_UNSEARCHED` and carry no negative finding.

**Next stage: S7.9 — development selection and representation freeze. NOT
AUTHORISED.**
