# S7.2C — Pre-target contract correction and hardening

**Freeze:** `D3D-SIR-S7.2-RECONSTRUCTION-CONTRACT-PRETARGET-V2`
**Supersedes:** `…-V1` (preserved unmodified) · **Date:** 2026-09-02
**Status:** `FROZEN_READY_FOR_S7.3`

---

## 1. Verdict

Nine clauses corrected, six human decisions frozen. V2 inherits V1 in full and
supersedes only the named clauses; every other V1 rule remains binding and is
not restated.

**Zero signal values were inspected. No target was ranked or selected. No model
was fitted. No coordinate was generated. No external value was accessed.** The
data archives were not opened in this run.

Three of the nine corrections fixed clauses that were **not merely imprecise but
self-defeating as written** — the equivalence conjunction, the rolling-origin
sealing language, and the undefined V3 aggregate. Catching them before S7.3 is
the difference between a contract that constrains the study and one that only
appears to.

## 2. V1 preservation

**35/35 substantive artifacts verified, zero drift.** V1 is unmodified and
remains reproducible.

Two entries in V1's manifest — `S7_2_ACCEPTANCE_CHECKS.json` and
`S7_2_FREEZE.json` — could not verify, and this is **not drift**. Both are
written *after* the manifest is built, so the hashes recorded for them are
necessarily stale: a file cannot contain its own hash. That is a construction
defect in the V1 manifest, corrected in V2 (clause C-09) by excluding
self-referential files explicitly.

It is the same class of bookkeeping defect found in the S7.1 freeze (mixed hash
rules). Both are documented rather than silently patched, and neither affects
data integrity.

## 3. The nine corrections

Machine-readable: `manifests/SUPERSEDED_CLAUSES.csv`. Full statements in
`S7_2C_CONTRACT_V2.md`.

### C-01 · Practical equivalence was logically inconsistent

V1 required **both** within-1-SE **and** within-0.01. The floor exists because a
one-SE rule degenerates when `SE` is tiny — but under a conjunction the tiny `SE`
stays binding and the floor never relaxes anything. The rule removed exactly the
protection it was added to provide.

```
delta_equiv = max(SE_delta, 0.01)
equivalent iff |RMSE_A - RMSE_B| <= delta_equiv
```

Within one SE **OR** within the floor. Floor value unchanged.
`SE_delta` is now defined operationally over the 20 development discharges.

### C-02 · Ordinary CV retired

`CV = sd/|mean|` is undefined at zero mean, explosive near it, and meaningless
for sign-changing trajectories — and this object contains several plausible
candidates that cross or sit near zero.

```
RRV_s   = 1.4826 * MAD(y_s) / RMS(y_s)      (0 if RMS = 0)
RRV_dev = median_s(RRV_s)                    over 20 development discharges
min_median_robust_relative_variation = 0.05
```

Corrected **prospectively** — no candidate value has been inspected, so the
change cannot have been motivated by any candidate's score.

### C-03 · Primary metric defined exactly

V1 named "calibration-normalized RMSE" without a denominator, leaving the 0.01
floor without a scale and gate V3 undecidable.

```
scale_{s,b} = std(y_calibration_{s,b}, ddof=0)
NRMSE_{s,b} = RMSE(protected) / scale_{s,b}
```

`ddof = 0` explicit. Calibration values only. `scale == 0 ⟹
INVALID_FOR_NORMALIZED_SCORING`, **no epsilon** — any epsilon would have to be
chosen, and a value chosen with outcomes in view is a tuned parameter.

The floor is now exactly **1% of the calibration target standard-deviation
scale**.

### C-04 · Rolling-origin protection was self-contradictory

V1's "protected" language read as permanently sealing block A's evaluation
values — while block B calibrates on `[0, 0.60)`, a window that contains them.
As written, the protocol forbade its own geometry.

**BLOCK-LOCAL PROTECTION**, sequential/prequential: score A → freeze the score →
only then may those values act as ordinary calibration history for B and C.

Invariant preserved: a target value may never influence its own evaluation
block's fit, any earlier block, or any frozen choice. **Time fractions
unchanged.** The external cohort remains **globally sealed** before S7.10.

### C-05 · Deterministic target selection

V1 deferred the choice among eligible candidates to human review — after S7.3
makes relative feasibility visible, which is the worst moment for discretion.

Five-level lexicographic rule: target-side major flags (fewer) → surviving
certified predictors (more) → surviving distinct families (more) → RRV margin
(larger) → frozen inventory index (lower). Level 5 guarantees a unique winner.
**The top-ranked eligible candidate IS the primary target.**

### C-06 · Gate V3 defined exactly

"The predeclared aggregate sense" was never defined, so the mandatory
nontrivial-skill gate could not have been evaluated.

```
NRMSE_method,s = mean over blocks A,B,C
Delta_j        = mean over external discharges of (NRMSE_REL,s - NRMSE_Bj,s)
PASS iff Delta_0 <= -0.01 AND Delta_1 <= -0.01
```

CIs reported but **not** thresholds — with 42 discharges it is entirely possible
to resolve a difference that does not matter.

### C-07 · Gate V6 cited the wrong cohort

V1 said 35/27; those are **parent-object** counts. The external gate operates on
**24 earlier / 18 later**. Three-valued outcome frozen: `PASS` /
`PASS_WITH_QUALIFICATION` / `FAIL_FOR_FULL_DOMAIN`, the last **narrowing**
`Omega_rec` rather than erasing the result.

### C-08 · Six human decisions frozen

See §4.

### C-09 · Hash manifest self-reference

Described in §2.

## 4. Human decisions frozen

| | Decision | Consequence |
|---|---|---|
| **H-A** | no EFIT-lineage recovery campaign | the 15 `LINEAGE_PARTIAL` equilibrium quantities may be lost under fail-closed, and stay lost |
| **H-B** | no `PROVENANCE_RELAXED` variant | V1's escape 2 from fail-closed is **closed**; fail-closed now means what it says |
| **H-C** | no target-class override | `pcdiamag3` stays excluded (uncalibrated, no physical unit) |
| **H-D** | no second-order derivatives | presumption is now final |
| **H-E** | no support beyond 12 | bound stands on calibration-sample economy |
| **H-F** | do not rewrite the S7.1 mixed-hash freeze | historical record preserved; canonical hashes continue in use |

H-A and H-B together are the substantive commitment: the primary study accepts
the full cost of fail-closed provenance and provides **no rescue path**. That is
a stronger position than V1 held, and it was taken before knowing what it costs.

## 5. Preserved from V1

20/42 partition · external firewall · continuous reconstruction · structural
transfer with local calibration · target-history exclusion · sibling-channel
primary exclusion · fail-closed provenance · canonical-unit conversion ·
no-super-resolution · first derivatives only · relational depth 1 · support 1–12
· B0/B1/B2/B3 · discharge-level inference · seeding firewall · claim-domain
limits · eight admissibility classes · ten gates · lexicographic utility.

Component status unchanged: `q` FROZEN · `I` PARTIAL · `P` PARTIAL ·
`B` PARTIAL · `H` FROZEN · `U` FROZEN · `V` PARTIAL · `Ω` PARTIAL.

## 6. Acceptance

**24/24 checks pass**, covering all 21 required items plus three added
(all six human decisions frozen; no model fitted; no coordinate generated).

**Markdown files created in this run: 4** — against a preferred ceiling of 8 and
a hard limit of 20. V1's 23 policy documents were **not** duplicated; V2
inherits them and names only the superseded clauses. Machine-readable detail
lives in JSON and CSV.

## 7. Files produced

```
correction_v1/
  S7_2C_CORRECTION_REPORT.md          S7_2C_CONTRACT_V2.md
  S7_2C_DECISION_LEDGER.md            TARGET_SELECTION_RULE.md
  K_REC_PRE_V2.json                   target_selection_schema.json
  metric_and_gate_definitions.json    S7_2C_ACCEPTANCE_CHECKS.json
  S7_2_FREEZE_V2.json
  manifests/  V1_FREEZE_VERIFICATION.json
              SUPERSEDED_CLAUSES.csv
  scripts/    build_s7_2c.py
```

Updated outside: `S7/STATUS.md`. Unchanged: all V1 artifacts, all S7.1
artifacts.

## 8. Reproduction

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
& $P S7\02_reconstruction_contract\correction_v1\scripts\build_s7_2c.py
```

Deterministic; no seeds. Exits non-zero if the V1 freeze fails verification.

## 9. Recommendation

**`READY_FOR_S7.3`.**

All six previously open human decisions are frozen, so S7.3 opens with no
discretionary latitude: eligibility criteria, the variation statistic, the
primary metric, the selection rule, and the two gates that will judge the result
are all fixed and hashed.

**S7.3 is not authorised by this document.**
