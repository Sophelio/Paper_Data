# S7.3 — Target feasibility and information boundary: internal audit

**Freeze:** `D3D-SIR-S7.3-TARGET-AND-INFORMATION-BOUNDARY-V1`
**Status:** `FROZEN_READY_FOR_S7.4` · acceptance **35/35** · **Date:** 2026-09-02

---

## 1. Executive verdict

The primary reconstruction target is **`vsurf`** (surface loop voltage), selected
automatically by the frozen deterministic rule from 62 eligible candidates. The
primary information boundary admits **79** provenance-certified primitive
explanatory quantities across **7** scientific families, at a **20.0 ms** analysis
cadence.

**20 development discharges opened; 0 external.** No model, no baseline, no
correlation, no coordinate.

Two things are worth stating up front. First, the fail-closed rule cost exactly
what S7.2 predicted and no more: the 15 equilibrium quantities left the boundary
and nothing else did. Second, the lexicographic ordering demonstrably bound — the
candidate with the largest variation margin (`fs05da`, 0.414 against `vsurf`'s
0.130) ranks **third**, because Level 2 outranks Level 4. A weighted score would
have chosen differently, which is why the contract forbids one.

## 2. Parent-freeze verification

All three parents verified before any value was opened, under the S7.2 canonical
raw-byte convention with self-referential files excluded per clause C-09.

| Parent | Verified | Drift |
|---|---|---|
| `D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1` | 9 artifacts | 0 |
| `D3D-SIR-S7.2-…-PRETARGET-V1` | 35 artifacts | 0 |
| `D3D-SIR-S7.2-…-PRETARGET-V2` (authoritative) | 10 artifacts | 0 |

Cohort partition, development list, external list, `K_REC_PRE_V2`, target-selection
schema and metric/gate definitions all unchanged.
`manifests/PARENT_FREEZE_VERIFICATION.json`.

### Contract sanity check (§4) — `PASS_WITH_NOTATIONAL_NOTE`

The V2 field `practical_equivalence.rule` reads `|RMSE_A − RMSE_B| ≤ delta_equiv`
— a bare `RMSE` token, ambiguous in isolation. It does **not** explicitly encode
raw RMSE, so the STOP condition does not apply. Four independent fields fix the
unit as NRMSE: `primary_metric.symbol` is `NRMSE_{s,b}`;
`floor_interpretation` states the 0.01 is 1% of the calibration sd-scale, true
only in normalized units; gate V3 applies the same 0.01 to NRMSE differences;
and raw RMSE appears **only** under `also_reported`.

Recorded rather than silently reinterpreted, with a recommended purely notational
fix at the next revision. Immaterial to S7.3 — no model is fitted here, so the
rule is not exercised. `manifests/CONTRACT_NOTATION_AUDIT.json`.

## 3. External-firewall verification

```
value-bearing shots read      = 20  (exactly the frozen development list)
external value-bearing reads  =  0
external identifiers known    = 42
```

The development list was read from the frozen partition and verified against the
expected list; it was never used hard-coded as the primary source. Stage A opens
no archive at all, structurally. `manifests/DATA_ACCESS_LOG.csv`,
`manifests/EXTERNAL_FIREWALL_AUDIT.json`.

## 4. Metadata-only major-flag freeze

Frozen and hashed **before any value was opened**, from the S7.1 MAJOR register
only.

| Issue | Scope | Attaches to |
|---|---|---|
| U001 upstream generator absent | GLOBAL | all 95 — does not discriminate |
| U004 no uncertainty metadata | GLOBAL | all 95 — does not discriminate |
| U003 EFIT unresolved | signal-specific | 15 equilibrium (already class-excluded) |
| U009 era-varying resampling method | signal-specific | 4: `bt`, `ip`, `prmtan_neped`, `prmtan_teped` |
| U010 downsample without anti-alias | signal-specific | 18: 14 CER + the same 4 |

The ranking key counts **signal-specific** flags only; the two global flags add a
constant that cannot change a lexicographic ordering, and are recorded per signal
regardless.

**One deviation worth recording.** The S7.1R interim CSV that first listed the
U009/U010 attachments is no longer present on disk. The attachment was therefore
recomputed from its own primary source — the per-shot `shot_*_metadata.json`
sidecars, which hold only `method`, `category` and lengths. These are component
`A` metadata, explicitly permitted for all discharges by the firewall, and **no
data array was read**. The recomputation reproduces the documented counts exactly
(U009 = 4, U010 = 18). No new flag class was invented; no MODERATE or MINOR issue
was promoted; no flag derives from statistical behaviour; U003 was not used to
alter the candidate set.

## 5. Candidate census — 64

| Excluded | n |
|---|---|
| `EQUILIBRIUM_DERIVED` | 15 |
| `CONTROL_COMMAND_OR_ACTUATION` | 14 |
| uncalibrated raw (`pcbcoil`, `pcdiamag3`) | 2 |
| **candidates** | **64** |

Computed from the frozen inventory, not assumed. No override (H-C).

## 6. Per-candidate `I_rec` instantiation

Instantiated independently for all 64 **before** any ranking. Surviving predictor
counts range 40–79: ECE targets lose 39 siblings, filterscopes lose 3, and every
candidate loses the same 15 equilibrium quantities under fail-closed.

Statistical correlation was never used as ancestry evidence, for admission or
exclusion.

## 7–9. Development-only feasibility, RRV, NRMSE scale

Target values were canonicalised before any statistic
(`target_unit_canonicalization.csv`) and represented on each candidate's own
primary grid.

| | |
|---|---|
| RRV formula | `1.4826 · MAD(y_s) / RMS(y_s)`, `0` if `RMS = 0`; `RRV_dev = median_s` |
| RRV range across candidates | 0.0037 – 0.4640 |
| Failing `RRV_dev ≥ 0.05` | **2** — `bt` (0.0037), `ip` (0.0042) |
| Failing distinct ≥ 0.10 | 0 |
| Identically-zero discharges > 0 | 0 |
| Invalid NRMSE blocks > 0 | **0 of 64 candidates** |
| Both eras present | 64 |

`scale_{s,b} = std(y_calibration_{s,b}, ddof=0)` on the block-local geometry.
Zero-scale blocks would be `INVALID_FOR_NORMALIZED_SCORING`; **no epsilon was
introduced**, and none was needed. Per-shot RRV for all 20 discharges is in
`development_rrv_per_shot.csv`; all 3840 block scales in
`development_nrmse_scale_audit.csv`.

## 10. Algebraic-duplicate audit

Definitional and provenance only. S7.1 records one-to-one identity with no
aliases; the sole documented deterministic relation is `pinj = Σ pinj_*`, removed
by R3 where applicable; same-quantity series are removed by the sibling rule. No
surviving deterministic restatement for any candidate. **No correlation,
regression, inversion or performance used.**

## 11–12. Eligibility and deterministic ranking

**62 of 64 eligible.** Ranking applied lexicographically with no weighting.

| Rank | Candidate | L1 | L2 | L3 | L4 margin | L5 | Resolved |
|---|---|---|---|---|---|---|---|
| **1** | **`vsurf`** | 0 | 79 | 7 | 0.1297 | 5 | — |
| 2 | `density` | 0 | 79 | 7 | 0.0483 | 21 | **L4** |
| 3 | `fs05da` | 0 | 76 | 6 | 0.4140 | 27 | L2 |
| 4–6 | `fs04`, `fs04da`, `fs03da` | 0 | 76 | 6 | 0.28–0.19 | — | L2 |
| 7+ | 40 ECE channels | 0 | 40 | 6 | — | — | L2 |

46 candidates tied at Level 1 with zero flags; Level 2 reduced that to two.

### Sibling ambiguity — tested, immaterial

The CER provider group was split into two sibling subfamilies (rotation, a
velocity; ion temperature, a temperature) per §11's direction that a provider
grouping is not by itself a sibling relation. The alternative reading — one CER
family — was evaluated explicitly and **leaves the winner unchanged**, since no
CER candidate is competitive at Level 1. No §11 human review triggered.
`manifests/SIBLING_AMBIGUITY_SENSITIVITY.json`.

## 13–14. Selected target and sanity audit

**`vsurf`** — surface loop voltage, V, `DIRECT_MEASUREMENT`, magnetics, 20.0 ms
native, inventory index 5, **zero signal-specific major flags**.

Sanity audit inspected identity, description, unit, provenance and flags only;
reconstructability, correlation, reconstructions and baselines were **not**
inspected. No new defect → `TARGET_SELECTION_CONFIRMED`. The defect-substitution
procedure was not invoked.

Recorded but not a selection input: `vsurf` is among the 16 upstream-upsampled
quantities, carrying `resolution_flag = UPSTREAM_UPSAMPLED` for S7.5's derivative
policy. Inventing a flag class after seeing candidates is forbidden, so it did
not enter Level 1.

## 15–17. Primary boundary, sibling sensitivity, exclusion census

```
95  ->  1 target + 15 unresolved-ancestry  ->  79 admissible primitives
```

| Category | n |
|---|---|
| target itself | 1 |
| duplicate / alias | 0 |
| definitional descendant | 0 |
| verified target ancestry | 0 |
| unresolved target ancestry | **15** |
| sibling exclusion | 0 |
| other `P_rec` reason | 0 |
| **surviving primary** | **79** |

Families: ECE 40 · CER 14 · beams 10 · magnetics 4 · filterscopes 4 · gas 4 ·
density 3.

**Sibling sensitivity: `NOT_APPLICABLE`** — `vsurf` belongs to no same-quantity
channel series; magnetics holds five distinct quantities.

`pcbcoil`/`pcdiamag3` survive as predictors with permanent `UNCALIBRATED_SIGNAL`
type, and the 14 actuation quantities survive as predictors — target eligibility
and predictor admissibility are different questions. 18 survivors carry
`ALIASING_RISK`.

**Primary cadence 20.0 ms**, set by `vsurf` itself under the no-super-resolution
rule. 60/60 development blocks valid; calibration 75–140+ samples, evaluation
19–23.

## 18. Data-access audit

20 development shots, one logged read each, all 95 signals read for time support
with values used only for the 64 candidate targets. Zero external reads.

## 19. Files produced

6 Markdown, 13 CSV, 10 JSON, 3 scripts — all hashed in `S7_3_FREEZE.json`.

## 20. Reproduction

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$S = "S7\03_target_feasibility_and_boundary\scripts"
& $P $S\s7_3_a_metadata.py      # metadata only; opens no archive
& $P $S\s7_3_b_feasibility.py   # development values only
& $P $S\s7_3_c_select.py        # ranking, selection, boundary, freeze
```

Deterministic; no seeds. Stage A exits non-zero on parent drift or on an
explicit raw-RMSE encoding; stage B exits non-zero on any external read.

## 21. Recommendation for S7.4

**`READY_FOR_S7.4`.**

S7.4 inherits: `y* = vsurf`; 79 primitives across 7 families; a 20.0 ms primary
cadence; 18 predictors carrying `ALIASING_RISK` and the target carrying
`UPSTREAM_UPSAMPLED`, both of which constrain derivative construction at S7.5;
and an external cohort still sealed until S7.10.

**S7.4 is not authorised by this document.**
