# S7.11 — Sensitivity and failure interpretation: internal audit report

Stage **S7.11** · Freeze `D3D-SIR-S7.11-SENSITIVITY-AND-FAILURE-INTERPRETATION-V1`
Parent `D3D-SIR-S7.10-EXTERNAL-VALIDATION-AND-GATE-EVALUATION-V1`

---

## 1. Executive verdict

**`FROZEN_WITH_QUALIFICATIONS`** · 39/39 acceptance · V9 resolved.

```
S7_11_DEVELOPMENT_EQUIVALENCE_DOES_NOT_IDENTIFY_EXTERNAL_ROBUSTNESS
  __CANONICAL_REPRESENTATIVE_EXTERNALLY_FRAGILE
  __PRIMARY_FAILURE_UNCHANGED
```

The primary S7.10 verdict is untouched and immutable:
`NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER`, V3 FAIL, V6 FAIL, `Omega_rec`
EMPTY, `C_dev_star` unchanged.

Three findings carry the stage:

1. The development-equivalent family is **heterogeneous** externally —
   70 of 213 full-domain supports satisfy the V3-style criterion — but
   **uniformly marginal**: no member beats persistence by more than 0.0287
   NRMSE and the family median `Δ₁` is −0.0004.
2. `C_dev_star` is **externally fragile within its own family** (86.4th
   percentile of mean error) despite carrying the family's **highest**
   development bootstrap selection frequency. Development selection frequency
   and external error are essentially uncorrelated (Spearman −0.09).
3. **V9 = FAIL** (non-mandatory) on the temporal-block component: omitting
   block B flips the V3-style verdict. The discharge component is clean.

## 2. Parent verification

Twelve authoritative freezes through S7.10. **All 31 S7.10 artifacts and all 45
S7.9 artifacts reproduce byte-for-byte.** Verified unchanged: target, external
cohort 42 = 24 + 18, `C_dev_star` support id and size 12, estimator, all six
baseline configurations (`B2 α=1/78`, `B3` sklearn 1.9.0 `random_state`
2026090502, `H0 α=1/70`), two-seed `NOT_EXECUTED`. Installed sklearn matches the
frozen version. Verdict: zero substantive drift.

## 3. Primary-result immutability

`PRIMARY_S7_10_RESULT_IMMUTABLE = true` written before any calculation, pinning
`C_dev_star`, V3 FAIL, V6 FAIL, `Omega_rec` EMPTY, S7.10 stage status and the
full gate table. No S7.11 output modifies any of those fields, and the final
freeze re-asserts every one.

## 4. Predeclaration verification

| | |
|---|---|
| file sha256 | `da24fbe38141f0c7…` — prefix matches |
| declared | `2026-09-05T22:47:11.395345Z` |
| first external access | `2026-09-05T22:48:51.998142Z` |
| **lead time** | **100.6 s before external access** |
| executed in S7.10 | false |

The 217 support ids re-hash to `d33bf22348…`, matching the value recorded inside
the predeclaration, and all 217 lie within `Ahat_rec`.

The minus-prmtan construction was **re-derived independently** from each
coordinate's recorded primitive ancestry rather than assumed: 5 removed, 7
retained, agreeing exactly with the predeclared lists.

**Scope discipline.** The predeclaration authorises exactly three analyses plus
the carried two-seed status. Only those were run. The V9 temporal-block
omission was executed as part of V9's own inherited definition — the three
components (discharge, temporal block, numerical realization) were frozen in
S7.2 V1, long before external access — and is recorded as such, not as an
extension of the predeclaration. **No post-hoc `PROD(gasa,gasa)` removal test
and no joint two-discharge removal diagnostic were run**, as neither is
predeclared.

## 5. Support-family registry

217 unique supports recovered from `bootstrap_selection_frequency.csv`; sizes
10 (9), 11 (32), 12 (176); 88 distinct coordinates; 91 distinct atoms realised
across the family plus the two prmtan sensitivities; 10 level denominators in
play; 0 rate denominators.

## 6. Support-family domain audit

| | |
|---|---|
| full-domain (126/126 blocks, 42/42 discharges) | **213** |
| not full-domain | **4** |
| reason | `E_DENOM` on 6 of 126 blocks; 40/42 discharges evaluable |

The four are `LEVEL_RATE`-bearing supports whose companion level denominators
fail the inherited `DENOMINATOR_ADMISSIBILITY_PRIMARY_V1` rule on six external
calibration blocks. No epsilon, shift, clipping or denominator repair was
applied. They are reported and excluded from full-domain tallies — a support not
evaluable on the full frozen external domain may not be called a successful
full-domain transfer support.

Common support was preserved mechanically: each support aggregates over its own
eligible blocks and **B0/B1 are aggregated over the same blocks**, so every
paired comparison uses identical masks. B0/B1 were reused from S7.10 only after
hash verification of `external_block_metrics.csv`.

## 7–9. Support-family metrics and distributions

Over the 213 full-domain supports:

| | p0 | p5 | p25 | p50 | p75 | p95 | p100 |
|---|---|---|---|---|---|---|---|
| mean NRMSE | 0.1815 | 0.1882 | 0.1982 | 0.2099 | 0.5236 | 0.7925 | 4.9385 |
| median NRMSE | 0.1464 | 0.1520 | 0.1607 | 0.1685 | 0.1736 | 0.1813 | 0.1929 |
| `Δ₀` | −0.7409 | −0.7343 | −0.7243 | −0.7126 | −0.3988 | −0.1300 | +4.0161 |
| `Δ₁` | −0.0287 | −0.0221 | −0.0121 | **−0.0004** | +0.3133 | +0.5822 | +4.7282 |

**V3-style pass: 70 / 213 = 0.3286.** Failure breakdown: 139 fail `Δ₁` only,
0 fail `Δ₀` only, 4 fail both. Persistence is the binding comparator throughout.

**The passing subfamily is marginal**: `Δ₁` among passers spans −0.0287 …
−0.0103; none beats persistence by more than 0.05; thirteen by more than 0.02.

`C_dev_star`: mean 0.7424 (**86.4th percentile**, rank 184/213), median 0.1699
(56.8th, rank 121), `Δ₁` +0.5321 (86.4th).

`LOWEST_EXTERNAL_ERROR_SUPPORT_IN_PREDECLARED_SENSITIVITY`: mean 0.1815, median
0.1672, `Δ₀` −0.7409, `Δ₁` −0.0287, development bootstrap frequency 0.034.
**Explicitly not a replacement primary support and not `C_star`.**

Development frequency vs external behaviour: Spearman **−0.093**; passers'
median frequency 0.0020 vs failures' 0.0010; `C_dev_star` held the family
maximum at 0.093.

Tail vs typical: 0/70 passers have any discharge above NRMSE 1, against 93/143
failures; median of the max single-discharge NRMSE is 0.536 for passers and
7.543 for failures. 186/213 supports beat the persistence median; only 107/213
beat the persistence mean.

Era: 206/213 meet `Δ₁,later ≤ −0.01`; 7/213 meet `Δ₁,earlier ≤ −0.01`. The era
asymmetry is family-wide, not canonical-specific. **`Omega_rec` not narrowed.**

## 10. Coordinate participation

Computed for all 88 coordinates across `ALL_217`, `FULL_DOMAIN`,
`V3_STYLE_PASS`, `V3_STYLE_FAIL`. Descriptive only — selects nothing, prunes
nothing, gates nothing, asserts no causality.

Most failure-associated: `PROD(gasa,gasa)` (0.000 pass / 0.469 fail, **−0.469**)
· `PROD(ece37,ece39)` (−0.344) · `PROD(pinj,cerqrott6)` (−0.267) ·
`RECIP(prmtan_neped)` (−0.217) · `RATIO(ece21,prmtan_neped)` (−0.196).

Most pass-associated: `PROD(fs03da,cerqtit11)` (+0.382) ·
`RATIO(prmtan_neped,cerqtit10)` (+0.360) · `RATIO(gasd,bt)` (+0.257) ·
`PROD(bt,bt)` (+0.195) · `PROD(prmtan_neped,ece39)` (+0.179).

`PROD(gasa,gasa)` heads the table: 0 of 70 passers, 67 of 143 failures. Its
presence moves the median from 0.1698 to 0.1643 (negligible) and the mean from
0.201 to 0.732. This fell out of the required table; **no removal test was run
and the coordinate remains in `C_dev_star`.**

`ID(pcdiamag3)` appears in **100 %** of all 217 supports. Recurrence reported;
no physical coefficient meaning inferred — it remains `UNCALIBRATED_SIGNAL`.

## 11–12. prmtan sensitivities

Both full-domain (42/42, 126/126). **Neither passes.**

| | `C_dev_star` | minus-prmtan (7) | prmtan-only (1) |
|---|---|---|---|
| mean | 0.7424 | 0.8351 | 0.4632 |
| median | 0.1699 | 0.1764 | 0.4660 |
| `Δ₀` | −0.1801 | −0.0873 | −0.4593 |
| `Δ₁` | +0.5321 | +0.6248 | +0.2529 |
| V3-style | FAIL | FAIL | FAIL |
| max discharge NRMSE | 11.95 | 13.78 | 0.96 |

Paired vs `C_dev_star`: minus-prmtan **+0.0928** (worse), prmtan-only
**−0.2792** (better mean). minus-prmtan vs prmtan-only: +0.3719.

Removing the same-family density ancestry makes the result **worse** on every
axis — the tail survives, because `PROD(gasa,gasa)` is retained. The
pedestal-density diagnostic alone has a better mean purely because a single
level coordinate cannot extrapolate, and a 2.7× worse median. The relational
construction adds substantial typical-case accuracy over it; neither reaches
nontrivial skill.

## 13–16. V9

**Discharge** — 0/42 LODO cohorts satisfy V3, independently recomputed and
matching S7.10 exactly. `Δ₁` range +0.2579 … +0.5514. Most influential 187019,
then 187022, both earlier era. **Zero verdict flips** →
`NO_SINGLE_DISCHARGE_VERDICT_DEPENDENCE`.

**Temporal block** — omit A: `Δ₁` +0.808 FAIL · **omit B: `Δ₀` −0.7299,
`Δ₁` −0.0114 PASS** · omit C: `Δ₁` +0.800 FAIL. One flip →
`DIRECT_TEMPORAL_BLOCK_DEPENDENCE`. Margin 0.0014 below threshold. No new
temporal windows created.

**Numerical realization** — `NUMERICAL_REALIZATION_SENSITIVITY_NOT_INSTANTIATED`.
All coordinates carry `numerical_realization_id = NONE`; constructors are
C0/C2/C3/C5 only, so no derivative coordinate and no `FD2_PHYSICAL_TIME_V1`
dependence. Nothing invented post hoc. Robustness may not be inferred from
absence of a test.

**Resolution: V9 = FAIL**, non-mandatory, changing no mandatory gate.

## 17. Product-extrapolation carry-forward

The S7.10 diagnosis is carried unchanged and **not repaired**:
`PROD(gasa,gasa)` under protected-window extrapolation, calibration range
5.3 × 10⁻³ … 4.1 × 10⁻² against a protected value of 1.63, ≈ 8 979 calibration
σ, next-largest excursion 13 σ, log–log correlation 0.930. The family
participation table independently corroborates it.

Not done: removal, clipping, winsorization, rescaling, range gating, refitting
without it, or any outcome-triggered experiment.

## 18. Range-support prospective lesson

`OBSERVATIONAL_RANGE_SUPPORT_ADMISSIBILITY`, status
`PROSPECTIVE_CONTRACT_RECOMMENDATION`.

Mathematical domain support ≠ observational range support. `x²` is defined for
every finite `x`, yet a calibration-supported relation involving `x²` becomes
numerically unsupported when `x` moves far outside the calibration region. The
frozen `DENOMINATOR_ADMISSIBILITY_PRIMARY_V1` guards denominators, and S7.6R
states explicitly that C0/C1/C2/C6 have no denominator and no gate. A future SIR
contract should consider prospective range-support admissibility for rapidly
amplifying nonlinear total-map constructors — products and powers — alongside
the existing denominator guard.

**Not operationalized in this study. Not added retrospectively to `P_rec`.**

## 19. Support identifiability

Three concepts kept distinct, as required:

- **exact support identifiability** — **absent**. Development frequency does not
  predict external behaviour (Spearman −0.09); the most-selected support is
  among the family's more fragile members.
- **relational ingredient stability** — **present in development**
  (`ID(pcdiamag3)` in 100 % of winners) and reported per coordinate here, but it
  **does not confer external robustness**.
- **external utility of the support family** — **heterogeneous and marginal**:
  32.9 % V3-style pass, none by more than 0.0287.

`BOOT_SELECTION_FREQ = 0.093` and the 217-winner count are carried unchanged. No
unique-support and no global-optimality claim is made anywhere.

## 20. Interpretation boundary

No new primary claim was produced and none could be: the primary result is
immutable regardless of how many sensitivity supports pass. `prmtan_neped`
language distinguishes provenance certification from physical or statistical
independence. `ID(pcdiamag3)` remains `UNCALIBRATED_SIGNAL` with no certified
dimensional coefficient interpretation. `Omega_rec` remains EMPTY and was not
narrowed to the later era despite 206/213 supports meeting the later-era
threshold.

## 21. Files

6 Markdown (limit 20) · 9 CSV · 8 JSON · 2 manifests · 4 scripts.

## 22. Reproduction

```bash
python scripts/s7_11_a_verify.py   # lineage, predeclaration, immutability
python scripts/s7_11_b_family.py   # 217 supports + 2 prmtan + block omission
python scripts/s7_11_c_v9.py       # V9 resolution
python scripts/s7_11_d_freeze.py   # summaries, acceptance, freeze
```

Python 3.13.5 · numpy 2.5.2 · pandas 3.0.5 · scikit-learn 1.9.0. Family
evaluation runtime ≈ 8 s after a 5 s external load.

## 23. Recommendation for S7.12

**`READY_FOR_S7.12`** with qualifications.

S7.12 assembles a **qualified negative result**. The material S7.11 adds:

- the failure is **not** a uniform property of the development-equivalent
  family (70/213 pass V3-style), so it may not be reported as "relational
  representations of this class do not transfer";
- nor may the passing third be reported as success — none exceeds persistence by
  more than 0.0287, and the family median is at parity;
- the sharpest defensible statement is about **method, not physics**:
  development-side support equivalence carried no information about external
  robustness, and the canonical representative was among its family's more
  fragile members despite being its most frequently selected one;
- V9 closes FAIL on temporal-block dependence, with the numerical-realization
  component untested rather than passed;
- the range-support lesson is a prospective recommendation for a future
  contract, not a defect of this one's execution.

S7.12 must not convert any of this into a structural-transfer claim, must not
narrow `Omega_rec`, and must not promote any sensitivity support.
