# S7.4 — Mathematical interpretation: internal audit report

**Freeze:** `D3D-SIR-S7.4-MATHEMATICAL-INTERPRETATION-V1`
**Status:** **`TARGET_TEMPORAL_RESOLUTION_RECONCILIATION_REQUIRED`**
**Date:** 2026-09-02 · acceptance **24/24** (gate checks; `X_rec` items N/A)

---

## 1. Executive verdict

**S7.4 stopped at its own mandatory precondition. `X_rec` was not
instantiated.**

Section 4 required the target's temporal provenance to be reconciled before any
mathematical interpretation could be defined. It does not reconcile: the frozen
20 ms analysis grid is **finer than `vsurf`'s source-supported cadence in 20 of
62 discharges**, including **7 of the 20 development discharges**. That is a
direct conflict with the frozen no-super-resolution rule, on the target itself.

Per §4 the correct action is to stop and return
`TARGET_TEMPORAL_RESOLUTION_RECONCILIATION_REQUIRED`, not to redefine `X_rec`
around the problem.

A second, independent finding is recorded but **not acted on**: `vsurf` shares
the equilibrium group's time base exactly in all 62 discharges.

Parent freezes verified clean. No archive was opened. No target was reranked, no
boundary changed, no coordinate generated.

## 2. Parent verification — `PARENTS_VERIFIED`

| Parent | Artifacts verified | Drift |
|---|---|---|
| `D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1` | 9 | 0 |
| `D3D-SIR-S7.2-…-PRETARGET-V1` | 35 | 0 |
| `D3D-SIR-S7.2-…-PRETARGET-V2` (authoritative) | 10 | 0 |
| `D3D-SIR-S7.3-TARGET-AND-INFORMATION-BOUNDARY-V1` | 33 | 0 |

Substantive checks, all pass: `y* == vsurf`; 79 predictors; 7 families; external
cohort 42; development 20; `selected_target_boundary.csv`, `I_REC_SELECTED.json`
and `O_REC_SELECTED.json` all byte-unchanged.

## 3. Target temporal-provenance reconciliation — **FAILED**

Full treatment in `TARGET_TEMPORAL_PROVENANCE_AUDIT.md`.

| Cadence | Value |
|---|---|
| `SOURCE_SUPPORTED_CADENCE` | **19.93 – 82.91 ms**, median 20.24, varies by discharge |
| `ARCHIVED_CADENCE` | 20.0 ms, uniform |
| `ANALYSIS_CADENCE` | 20.0 ms |

**Verdict `C_SOURCE_CADENCE_VARIES_BY_DISCHARGE`.**

`vsurf` was cubic-spline resampled in all 62 discharges and **upsampled in 36**.
In 20 discharges the source cadence is coarser than the analysis grid — 7
development, 13 external. Worst case `165027`: 56 source samples → 229 archived,
source Δt ≈ 82.9 ms.

`UPSTREAM_UPSAMPLED` is therefore **not** a bookkeeping artefact. It records
genuine interpolation-created samples in the quantity the reconstruction will be
scored against.

The source-supported estimate is a **lower bound on coarseness**: `original_length`
is what the pipeline received, and the pipeline generator is absent (U001), so
the true source can only be coarser. Better information about U001 cannot rescue
the finding.

## 4–12. Not reached

`X_rec` was not defined. The following were consequently **not** produced, and no
claim is made about any of them: the formal `X_rec` definition; time
parameterization; realization/ensemble structure; typed predictor blocks; target
space; sampled-trajectory regularity; numerical representation; predictor
dependency metadata; resolution/aliasing metadata carried into `X_rec`.

The design work for these is straightforward once the cadence is settled — the
typed 8-block decomposition, the `t` versus `tau` split, the
sampled-vs-interpolant-vs-latent distinction — but every one of them depends on
the analysis cadence, which is exactly what is unresolved. Producing them now
would bake in a grid the contract forbids.

## 13. Development / external access audit

**Zero archives opened.** The gate was resolved entirely from frozen S7.1
metadata (`signal_quality_summary.csv`) and the per-shot metadata sidecars
(component `A`: `method`, `category`, `original_length`, `resampled_length`).
No signal value was read — development or external. The external cohort remains
sealed.

## 14. Assumptions explicitly not made

None were needed, because no interpretation was defined. For the record, and to
be inherited by the reconciliation: no differentiability, no Markov property, no
latent state, no causal ordering, no dynamical closure, no claim that the 79
predictors span a physical state, no cross-discharge concatenation.

## 15. Second finding — `vsurf` on the equilibrium time base

In **62 of 62** discharges, `vsurf` has identical `original_length`,
`resampled_length`, `t_start`, `t_end` and `n_samples` to all 15 equilibrium
quantities. No exceptions.

This suggests `vsurf` is carried on the EFIT time base — the same reconstruction
whose 15 outputs S7.3 excluded from `vsurf`'s own boundary as `LINEAGE_PARTIAL`
under fail-closed.

It is not proof. The registry describes it as "Surface loop voltage" with no EFIT
attribution, unlike `aminor` and `area`; its origin class is
`DIRECT_MEASUREMENT` at `STRONGLY_INFERRED`, which is inferred rather than
documented; and its resampling method differs from the equilibrium group's within
a given shot.

But it opens a question S7.3 had no reason to ask: **is the target's own ancestry
relative to the equilibrium reconstruction resolved?** For the 15 the fail-closed
answer was no.

**Not acted on.** S7.4 may not rerank targets or alter `I_rec`. Recorded for the
reconciliation as an independent item — resolving the cadence does not resolve
this, and vice versa.

## 16. Files produced

```
04_mathematical_interpretation/
  README.md
  TARGET_TEMPORAL_PROVENANCE_AUDIT.md
  S7_4_MATHEMATICAL_INTERPRETATION_AUDIT_REPORT.md
  target_temporal_provenance.json
  vsurf_temporal_provenance.csv          62 rows, per discharge
  S7_4_ACCEPTANCE_CHECKS.json
  S7_4_FREEZE.json
  manifests/PARENT_FREEZE_VERIFICATION.json
  scripts/s7_4_temporal_gate.py
```

**3 Markdown files** (limit 20, preferred ≤6). Not produced, because the stage
stopped: `X_REC.json`, `typed_signal_blocks.csv`, `trajectory_index.csv`,
`temporal_semantics.json`, `interpretation_constraints.json`,
`predictor_dependency_edges.csv`, `X_REC_DEFINITION.md`, `TEMPORAL_SEMANTICS.md`,
`S7_4_MATHEMATICAL_INTERPRETATION_FINAL.md`.

## 17. Reproduction

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
& $P S7\04_mathematical_interpretation\scripts\s7_4_temporal_gate.py
```

Deterministic; no seeds; opens no archive. Exits non-zero on parent drift.

## 18. Recommendation

**`TEMPORAL_RECONCILIATION_REQUIRED`.** S7.5 is not authorised.

A narrowly scoped reconciliation is needed before S7.4 can be re-attempted. The
options the finding leaves open are enumerated in
`TARGET_TEMPORAL_PROVENANCE_AUDIT.md` §"What reconciliation would need to
decide"; the choice among them is a human decision.

Two things are worth stating for that decision. First, the ranking that selected
`vsurf` was resolved at Level 4 by a margin of 0.081 over `density`, which has a
1 ms archived cadence and was not upsampled — so a corrected cadence definition
could plausibly change the winner, and re-opening selection is a live option
rather than a formality. Second, the second finding points the same way, which
makes a combined reconciliation more efficient than two separate ones.

The contract held. This is what a target-blind, fail-closed contract is supposed
to do when a defect surfaces after selection: stop, rather than accommodate.
