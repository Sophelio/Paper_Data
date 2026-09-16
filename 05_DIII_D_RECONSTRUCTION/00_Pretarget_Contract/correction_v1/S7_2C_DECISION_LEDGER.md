# S7.2C — Correction decision ledger

Supplements, and does not replace, the V1 ledger
(`../CONTRACT_DECISION_LEDGER.md`, D-01 … D-20), which remains binding for every
decision not superseded here.

**Nothing in this ledger was informed by any signal value, any target, any
model, or any result. None was inspected in this run.**

---

## Part 1 — Human decisions now frozen

These were the six items left open at the end of V1. All are now closed.

### H-A · No EFIT-lineage recovery campaign

**Decision.** Do not undertake an EFIT-lineage recovery campaign for the primary
study.
**Reason.** The strict experiment may simply lose the 15 `LINEAGE_PARTIAL`
equilibrium quantities under fail-closed provenance. That cost was accepted
prospectively in V1 (ledger D-03) and keeps the primary study simpler and
cleaner.
**Consequence, accepted.** For a target whose relationship to the equilibrium
group cannot be resolved, all 15 leave the primary boundary and stay out.
**Reversible?** Not within this study.

### H-B · No `PROVENANCE_RELAXED` variant

**Decision.** Do not declare a `PROVENANCE_RELAXED` secondary variant.
**Reason.** The primary paper needs **one clean, target-independent
reconstruction study**. A secondary branch admitting partially resolved ancestry
would function as a rescue path — and a rescue path declared in advance is still
a rescue path.
**Consequence.** V1 offered this as escape 2 from fail-closed. That escape is now
closed. Fail-closed means what it says.
**Reversible?** No.

### H-C · No target-class override

**Decision.** Do not override the frozen primary target classes.
**Reason.** The V1 class policy stands: `DIRECT_MEASUREMENT` and
`DIAGNOSTIC_RECONSTRUCTION` with resolved unit are eligible; actuation,
equilibrium-derived, uncalibrated raw and event labels are not.
**Consequence.** `pcdiamag3` — one of the historical eight — remains excluded,
because S7.1 established it is uncalibrated with no physical unit. V1 recorded
this as an override candidate; the override is now refused.

### H-D · No second-order derivatives

**Decision.** Do not promote second or higher temporal derivatives.
**Reason.** Source cadence cannot support them; V1 presumed them inadmissible
and the presumption is now final.

### H-E · No support beyond 12

**Decision.** Do not widen the representation-size range beyond 1–12.
**Reason.** The bound derives from calibration-sample economy on the worst
admissible grid (75 samples at 20 ms). Widening it would not be justified by
anything available before results exist.

### H-F · Do not rewrite the S7.1 mixed-hash freeze

**Decision.** Leave the S7.1 historical freeze as it is; continue using the
uniform canonical raw-byte hashes established by S7.2.
**Reason.** The historical record stays as written. The workaround is in place
and verified (9/9), and rewriting a frozen artifact to tidy its bookkeeping
would be worse than documenting the defect.

---

## Part 2 — Specification corrections

### C-01 · Practical equivalence was logically inconsistent

**Question.** V1 required *both* within-1-SE **and** within-0.01. Is that the
intended rule?
**Finding.** No — it is self-defeating. The floor was introduced because a
one-SE rule degenerates when `SE` is tiny. Requiring both means the tiny `SE`
stays binding and the floor never does anything. The conjunction removes exactly
the protection it was added to provide.
**Corrected to.** `delta_equiv = max(SE_delta, 0.01)`; equivalent iff
`|RMSE_A − RMSE_B| <= delta_equiv`. Within one SE **OR** within the floor.
**Floor value.** Unchanged at 0.01.
**`SE_delta` now defined operationally** over the 20 development discharges,
which V1 had left implicit.
**Not consulted.** No SE, no RMSE, no difference of any kind — none exists.

### C-02 · Ordinary CV replaced

**Question.** Is `CV = sd/|mean|` a sound variation floor for an unknown target?
**Finding.** No. It is undefined at zero mean, explosive near zero, and
meaningless for a sign-changing trajectory. Several plausible candidates in this
object — `vsurf`, `zmaxis`, `drsep`, `zcur`, the CER rotation channels — cross or
sit near zero.
**Corrected to.** `RRV_s = 1.4826·MAD(y_s)/RMS(y_s)`, `RRV_dev = median_s(RRV_s)`,
floor 0.05. Zero-safe by construction (`RMS = 0 ⟹ RRV = 0`), and scale-relative
rather than mean-relative.
**Timing.** Corrected **prospectively** — no candidate value has been inspected,
so the change cannot have been motivated by any candidate's score.
**Not consulted.** No signal values.

### C-03 · Primary metric was undefined

**Question.** What exactly is "calibration-normalized RMSE"?
**Finding.** V1 named it but never specified the denominator, which meant the
0.01 floor had no defined scale and the V3 gate was not decidable.
**Corrected to.** `scale_{s,b} = std(y_calibration_{s,b}, ddof=0)`;
`NRMSE = RMSE(protected)/scale`. `ddof = 0` recorded explicitly everywhere.
**Zero-scale.** `INVALID_FOR_NORMALIZED_SCORING` — **no epsilon**. An epsilon
would have to be chosen, and any value chosen with outcomes in view is a tuned
parameter. Declaring the block invalid is the honest option.
**Effect.** The 0.01 floor is now exactly 1% of the calibration target
standard-deviation scale.

### C-04 · Rolling-origin protection was self-contradictory

**Question.** May block A's evaluation target values ever be used again?
**Finding.** V1's "protected" language read as permanent sealing, which directly
contradicts block B calibrating on `[0, 0.60)` — a window containing block A's
evaluation interval. As written, the protocol forbade its own geometry.
**Corrected to.** **BLOCK-LOCAL PROTECTION** with sequential/prequential
semantics: score A, freeze the score, and only then may those values serve as
ordinary calibration history for B and C.
**Invariant preserved.** A target value may never influence its own evaluation
block's fit, any earlier block, or any frozen choice.
**Unchanged.** The time fractions. `[0,0.4)/[0.4,0.5)`, `[0,0.6)/[0.6,0.7)`,
`[0,0.8)/[0.8,0.9)`.
**Scope.** Applies only within a discharge. The **external cohort remains
globally sealed** before S7.10.

### C-05 · Target selection left discretion open

**Question.** Who chooses among eligible candidates?
**Finding.** V1 deferred it to human review — after S7.3 makes relative
feasibility visible. That is the worst possible moment for discretion.
**Corrected to.** A deterministic 5-level lexicographic rule; the top-ranked
eligible candidate **is** the primary target. Level 5 (frozen inventory order)
guarantees uniqueness.
**Escape.** Only a genuine newly discovered defect, frozen in the ledger, with
the identical rule re-applied to the remaining set.
**Not consulted.** No candidate, no eligibility outcome, no ranking.

### C-06 · Gate V3 was not decidable

**Question.** What is "the predeclared aggregate sense"?
**Finding.** Never defined. The mandatory nontrivial-skill gate could not have
been evaluated as written.
**Corrected to.** `NRMSE_method,s` = mean over A,B,C; `Delta_j` = mean over
external discharges of the paired difference; **PASS iff `Delta_0 <= −0.01` AND
`Delta_1 <= −0.01`**. CIs reported but explicitly **not** thresholds for V3.
**Reason for using the floor as the margin.** It ties the gate to the same
practical-relevance scale as the equivalence rule, rather than to statistical
resolvability — with 42 discharges it is entirely possible to resolve a
difference that does not matter.

### C-07 · Gate V6 cited the wrong cohort

**Question.** Which counts does the external era gate use?
**Finding.** V1 said 35/27. Those are **parent-object** counts. The gate operates
on the external cohort, which is **24 earlier / 18 later**.
**Corrected to.** 24/18, with a three-valued outcome: `PASS` /
`PASS_WITH_QUALIFICATION` / `FAIL_FOR_FULL_DOMAIN`.
**Interpretation frozen.** `FAIL_FOR_FULL_DOMAIN` does not erase a result — it
requires the final `Omega_rec` claim to be **narrowed** rather than averaged
across the processing discontinuity.

### C-09 · Hash manifest was self-referential

**Question.** Two V1 artifacts appeared to have drifted. Real?
**Finding.** No. `S7_2_ACCEPTANCE_CHECKS.json` and `S7_2_FREEZE.json` are both
written *after* the manifest is built, so the hashes recorded for them are
necessarily stale — a file cannot contain its own hash. **All 35 substantive
artifacts verify with zero drift.**
**Corrected to.** V2 excludes self-referential files from the manifest
explicitly and lists them under `self_referential_excluded`.
**Note.** This is the same class of record-keeping defect found in the S7.1
freeze (mixed hash rules). Both are bookkeeping, neither affects data integrity,
and both are now documented rather than silently patched.

---

## What was deliberately not done

- No signal value was read. The archives were not opened in this run.
- No target was ranked or selected.
- No model was fitted; no coordinate was generated.
- No external value was accessed.
- The V1 freeze was not modified — it is preserved and verified intact.
- The S7.1 object and its freeze were not touched.
