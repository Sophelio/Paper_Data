# S7.5H — Primitive-space and ontology hardening: internal audit

**Freeze:** `D3D-SIR-S7.5H-PRIMITIVE-SPACE-AND-ONTOLOGY-HARDENING-V1`
**Primary ontology:** `G_REC_DENSITY_HARDENED_V2` v2.0.0
**Status:** `FROZEN_WITH_QUALIFICATIONS` · acceptance **48/48** · 2026-09-04

---

## 1. Executive verdict

The hardened ontology is built and frozen: **70 primitives**, **nine
constructor families C0–C8**, depth 1, **23 861** symbolic coordinates. Zero
density values, zero external values, no model, no baseline, no target
statistic of any kind.

**Four qualifications, all recorded rather than repaired:**

1. **S7.6 already existed.** The stage premise that it had not started is
   incorrect. S7.6 V1 is preserved and marked superseded pending re-run.
2. **Instrumentation-density bias was not materially reduced** — the ECE share
   of the basis falls only 51.3% → 47.1%.
3. **The effective-rank audit disagrees strongly** with the number of
   representatives the frozen rule selected. Not acted on; thresholds not tuned.
4. **The hardened ontology is 1.75× larger**, not smaller, because four
   pairwise families were added while only 8 primitives were removed.

The stage did what its frozen policy said. Whether that policy achieves the
stated motivation is a separate question, answered honestly in §9 and §14.

## 2. Parent verification

`PARENTS_VERIFIED_WITH_STAGE_SEQUENCE_CONFLICT` — 0 hash drift across all eight
lineage freezes. Substantive checks pass: target `density`, canonical unit
`m^-3`, 78 predictors, `X_rec` instantiated, `G_REC_DENSITY_V1` present with 78
primitives and families C0–C4 totalling 13 604, external cohort 42 and sealed.

The single failing item is `no_s7_6_freeze_exists` — see §15.

## 3. Pre-value policy freeze

`HARDENING_POLICY_PREVALUE.json`, sha `d8c81421…`, hashed in stage A, which
**opens no archive at all**. Stage B verifies the hash before reading anything
and aborts on mismatch. The policy freezes all eight required components: group
rule, statistic, thresholds, representative algorithm, constructor catalogue,
typing and domain rules, deferred-channel treatment, and the ablation.

The ordering is structural, not a matter of discipline.

## 4. Firewall

```
development shots read        20  (exactly the frozen list)
predictor signals read        58  (eligible-group members only)
target values accessed         0
external values accessed       0
predictor-target correlation  not computed
mutual information / importance  not computed
model / baseline fitted        no
```

`FIREWALL_INTACT`. Only the 58 members of redundancy-eligible groups were
loaded — the minimum the audit requires.

## 5. Redundancy-eligible semantic groups

Decided on metadata alone, before values.

| Group | n | Eligible | Reason |
|---|---|---|---|
| `X_ECE` | 40 | **yes** | repeated radiometer channels, one quantity, one unit, one origin class |
| `X_CER_v` | 7 | **yes** | repeated rotation chords |
| `X_CER_Ti` | 7 | **yes** | repeated ion-temperature chords |
| `X_fs` | 4 | **yes** | filterscope channels, one quantity and unit |
| `X_NBI` | 10 | no | distinct beamlines, plus an aggregate and a torque — two dimensions |
| `X_mag` | 4 | no | four distinct quantities incl. two uncalibrated |
| `X_gas` | 4 | no | four distinct valves / manifolds |
| `X_density_aux` | 2 | no | density vs temperature, different dimensions |

Every ineligible group carries a recorded reason; none was silently compressed.
The 20 ineligible primitives were never correlation-tested and could not have
been deferred however strongly they happened to correlate.

## 6. Pairwise redundancy statistics

828 within-group pairs × up to 60 development discharge/block cells. Pearson
`r` on common finite calibration samples; a cell where either signal is constant
supports no redundancy claim and is not imputed.

**9 pairs qualified.** Eight are adjacent ECE channel pairs; one is
`fs04`/`fs04da`.

## 7. Representative selection

Greedy maximum-degree, tie-broken by lower frozen inventory index, with
**direct-witness-only** deferral. **8 deferred**, each with its own witness to
its own representative; no transitive removal.

### Provenance flag

`fs04` and `fs04da` correlate at **|r| = 1.000000 in all 60 cells**. That is not
the behaviour of two distinct viewing chords, and is consistent with one
measurement stored twice, possibly rescaled. Flagged for provenance follow-up;
not asserted as identity, and it changed nothing — the frozen rule defers
`fs04da` regardless of cause.

## 8. Primitive census

```
|P_full| = 78     |P_hard| = 70     |P_deferred| = 8
M = 70    Mt = 68 (typed)    Md = 63 (derivative-eligible)
```

`Md = 70 − 2 uncalibrated − 5 upstream-upsampled retained`.

## 9. Family composition — the bias audit

| Family | before | after | share before | share after |
|---|---|---|---|---|
| **ECE** | 40 | 33 | **0.513** | **0.471** |
| CER | 14 | 14 | 0.179 | 0.200 |
| beams | 10 | 10 | 0.128 | 0.143 |
| magnetics | 4 | 4 | 0.051 | 0.057 |
| gas | 4 | 4 | 0.051 | 0.057 |
| filterscope | 4 | 3 | 0.051 | 0.043 |
| density | 2 | 2 | 0.026 | 0.029 |

> **`materially_reduced: false`.** A 4.2-point shift in the dominant family's
> share does not meet any reasonable reading of "prevent one diagnostic family
> from dominating".

The primitive-space component of this hardening is close to a null result. The
grammar-broadening component is what changed substantially. Reported, not
adjusted.

## 10. Effective-rank audit — strong disagreement, not acted on

| Group | members | reps | median rank @95% | @99% |
|---|---|---|---|---|
| `X_ECE` | 40 | 33 | **3.0** | 7.0 |
| `X_CER_v` | 7 | 7 | 3.0 | 4.0 |
| `X_CER_Ti` | 7 | 7 | **2.0** | 3.5 |
| `X_fs` | 4 | 3 | 2.0 | 3.0 |

The reconciliation: the frozen criterion is **pairwise**, and `R_10 ≥ 0.97` is
what binds. **40 of 780 ECE pairs reach `R_med ≥ 0.99`, and 32 of those fail
`R_10 ≥ 0.97`** — near-redundant typically, not in the worst tenth of cells.
Low group rank does not imply any *pair* clears a direct-witness bar.

Per §28 the disagreement is recorded and did not change representative count,
thresholds or selections. A rank-based rule was forbidden as a selection
mechanism by §9, and rightly — SVD components are not scientifically legible
primitives.

## 11–13. Catalogue, typing, domains

Nine families, depth 1. C5 reciprocal, C6 level–rate, C7 rate-over-level, C8
level-over-rate, each with a frozen output dimension and, where applicable, a
symbolic domain predicate. C6 alone has **no** denominator predicate.

**C6–C8 are depth 1**, primitive-pair constructors with an internal rate
operator; they do not consume C1 objects. Recorded explicitly because the
notation invites a depth-2 reading.

`LEVEL_RATE(i|j) ≠ LEVEL_RATE(j|i)` — role-directional despite numerical
commutativity, since `x_i·ẋ_j ≠ x_j·ẋ_i`.

Preserved unchanged: `FD2_PHYSICAL_TIME_V1`; uncalibrated C0-only; upsampled
level-use allowed including as C6/C7/C8 level operands, derivative-use
sensitivity-only; aliasing propagation; component-level typing; no denominator
regularisation; numerical domain evaluation deferred to S7.6.

## 14. Symbolic combinatorial audit

| | C0 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | total |
|---|---|---|---|---|---|---|---|---|---|---|
| | 70 | 63 | 2 346 | 4 556 | 3 906 | 68 | 4 284 | 4 284 | 4 284 | **23 861** |

Original `G_REC_DENSITY_V1`: **13 604**. Ratio **1.75× — LARGER**.

C6/C7/C8 alone contribute 12 852. Removing 8 primitives reduced the original
five families from 13 604 to 10 941; adding four families more than doubled that
back up.

**No atomic enumeration was performed** — these are symbolic bounds. S7.6
instantiates.

## 15. Stage-sequence conflict

The instruction asserted "S7.6 HAS NOT STARTED". **It had.**
`D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-V1` exists, `FROZEN_READY_FOR_S7.7`, 40/40,
6 034 atoms, built on the full 78-primitive ontology.

**Contamination:** none possible. S7.6 V1 accessed 0 target values, 0 external
values, fitted nothing, computed no predictor-target statistic.

**Discretion:** every S7.5H decision is specified by the instruction —
thresholds, catalogue, representative rule. The only judgement is group
semantics, decided from metadata and independent of any S7.6 result. Residual
risk `LOW_AND_RECORDED`.

**Resolution `PROCEED_AND_SUPERSEDE`.** S7.6 V1 preserved unmodified and marked
`SUPERSEDED_FOR_PRIMARY_SEARCH_PENDING_RERUN_ON_HARDENED_ONTOLOGY`, exactly as
S7.3 V1 and S7.4 V1 were. The acceptance item `S7.6 not started` could not be
asserted truthfully and is recorded as reconciled, not passed.

## 16. Hardened raw ablation

`H0_RAW_HARDENED`: Ridge on the 70 hardened primitive levels only, no
constructed coordinates, same calibration geometry, preprocessing and
penalty-selection rule as B2, development-only tuning.

`DIAGNOSTIC_ABLATION` — **not** a mandatory gate baseline, **not** a replacement
for B2. **B2 is unchanged and was not shrunk.** Frozen, not run.

`B2 vs H0` isolates primitive-space hardening; `H0 vs relational SIR` isolates
relational construction on the same hardened information.

## 17. Things explicitly not used

Density values · predictor–target correlation · mutual information with the
target · target feature importance · any model or baseline · any SIR result ·
"probably does not matter for density" · PCA/autoencoder/learned components as
primitives · effective rank as a selection mechanism · any post-hoc threshold
adjustment.

## 18–19. Files and reproduction

6 Markdown, 8 CSV, 9 JSON, 3 scripts — all hashed in `S7_5H_FREEZE.json`.

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$S = "S7\05H_primitive_space_and_ontology_hardening\scripts"
& $P $S\s7_5h_a_policy.py      # metadata only; freezes the policy
& $P $S\s7_5h_b_redundancy.py  # development predictors only
& $P $S\s7_5h_c_ontology.py    # hardened ontology, audit, freeze
```

Deterministic; no seeds. Stage B aborts if the policy hash changed.

## 20. Recommendation for S7.6

**`READY_WITH_QUALIFICATIONS`.**

S7.6 must be **re-run** on `G_REC_DENSITY_HARDENED_V2` before S7.7. Its method is
unchanged; the denominator rule frozen at `6d4004eb…` applies unchanged and
extends to the three new partial maps C5, C7 and C8.

Two things for human review before that re-run:

**First**, the primitive-space hardening largely did not work as intended — 8 of
78 deferred, ECE share 51.3% → 47.1%. If materially stronger compression is
wanted, it requires a **new stage with new thresholds frozen prospectively**,
never a retroactive adjustment of these. That is a decision to take now, before
S7.6 consumes this ontology.

**Second**, C7 and C8 both place a **rate in a denominator**. In S7.6 V1 no C4
instance survived the denominator gate, because time derivatives change sign
within every calibration interval. The same mechanism will bear on C7 and C8. If
it eliminates them too, the four-family broadening will have added 68 usable
coordinates (C5) rather than 12 852 — worth anticipating, though only S7.6 can
determine it.
