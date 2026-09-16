# S7.3R — corrected primary information boundary for `y* = density`

Machine-readable: `I_REC_SELECTED_V2.json`, `O_REC_SELECTED_V2.json`,
`corrected_selected_target_boundary.csv` (95 rows),
`corrected_selected_target_exclusions.csv`

**Supersedes** the S7.3 V1 boundary for all subsequent stages. V1 is preserved.

## Exclusion census

| Category | n |
|---|---|
| initial quantities in O | **95** |
| target itself (`density`) | 1 |
| duplicate / alias | 0 |
| definitional descendant | 0 |
| verified target ancestry | 0 |
| **unresolved target ancestry** (fail-closed, 15 equilibrium) | **15** |
| sibling exclusion | 0 |
| **numerical-support exclusion** | **1** |
| **surviving primary predictors** | **78** |

```
95 quantities  ->  17 removed  ->  78 admissible primitive explanatory quantities
```

## The one numerical-support removal

**`vsurf`**, under `PRIMARY_NUMERICAL_SUPPORT_FAIL`.

Retaining it would force the analysis grid to its source-supported cadence of
**82.909 ms** at discharge `165027`, giving 50 grid samples and blocks
A(cal=20, eval=4), B(cal=30, eval=4), C(cal=40, eval=4) — all three evaluation
blocks below the frozen minimum of 10.

**Rule invoked:** `P_rec` class D numerical-support admissibility, together with
the no-super-resolution policy and the frozen validation minima (cal ≥ 30,
eval ≥ 10 on all three blocks). **Not** removed for correlation, predictive
usefulness or model performance — none of which was computed.

Across all 64 candidate boundaries there were **63 numerical-support removals,
and every one of them is `vsurf`.** No other signal in the object forces an
infeasible grid. The bottleneck is a single quantity, and the contract removes
it rather than degrading the whole experiment to accommodate it (§14).

## The 78 surviving primitives, by scientific family

| Family | n | Signals |
|---|---|---|
| **ECE electron temperature** | 40 | `ece1` … `ece40` |
| **CER rotation / ion temperature** | 14 | `cerqrott{3,6,8,10,11,12,13}`, `cerqtit{3,6,8,10,11,12,13}` |
| **Neutral beams** | 10 | `pinj`, `pinj_{15l,15r,21l,21r,30l,30r,33l,33r}`, `tinj` |
| **Magnetics** | 4 | `bt`, `ip`, `pcbcoil`, `pcdiamag3` |
| **Filterscope D-alpha** | 4 | `fs03da`, `fs04`, `fs04da`, `fs05da` |
| **Gas injection** | 4 | `gasa`, `gasb`, `gasc`, `gasd` |
| **Density** | 2 | `prmtan_neped`, `prmtan_teped` |
| | **78** | across **7** families |

Magnetics drops from 5 to 4 (`vsurf` removed); density from 3 to 2 (`density`
is now the target). Everything else is unchanged from V1.

`pcbcoil` and `pcdiamag3` remain admissible predictors with permanent
`UNCALIBRATED_SIGNAL` type, and the 14 actuation quantities remain admissible
predictors — target eligibility and predictor admissibility stay distinct.

## Corrected primary analysis cadence

```
rule : no finer than the coarsest SOURCE-SUPPORTED cadence among admitted
       quantities, evaluated per discharge
```

| | |
|---|---|
| **Discharge-specific** | **yes** — not a single fixed value |
| Range across all 62 | **5.853 – 14.187 ms** |
| Median | 6.824 ms |
| Maximum in development | 13.27 ms |
| Minimum grid samples, any discharge | **325** |
| All 62 discharges validation-feasible | **yes** |

**Binding signal by discharge:** `prmtan_teped` (26), `cerqrott3` (25),
`cerqrott8` (10), `cerqrott13` (1). The binding families are the pedestal fits
and CER — the two 10 ms-archived families whose source support is occasionally
coarser.

This is a genuine tightening relative to V1's flat 20 ms: the corrected grid is
**finer**, because removing `vsurf` removes the 20 ms-class bottleneck, and the
remaining admitted quantities support 6–14 ms. Every one of those samples is now
source-supported.

### Handing a discharge-specific cadence to S7.4

The cadence is not a single number, and that is a real property of a multirate
object with per-discharge source support — not an ambiguity. It is compatible
with the frozen contract because:

- the validation geometry is specified in **normalised time `tau`**, so the
  block fractions are cadence-independent;
- feasibility was checked at each discharge's own corrected cadence and passes
  everywhere, with a wide margin (min 325 samples against a requirement of 100);
- gate V7 (common support) constrains comparisons **within** a discharge, where
  the cadence is fixed.

## Temporal semantics handed to S7.4

Per signal, in `corrected_selected_target_boundary.csv`:
`source_supported_dt_min_ms`, `source_supported_dt_max_ms`,
`archived_dt_median_ms`, `n_shots_upsampled`, `source_temporal_status`,
`numerical_support_status`, `aliasing_flag`, `derivative_qualification`.

Among the 78 survivors:

- **6 carry `UPSTREAM_UPSAMPLED`** — `prmtan_neped`, `prmtan_teped` and the four
  filterscopes — and are therefore `NUMERICAL_SENSITIVITY_ONLY` for derivative
  construction at S7.5. They are admissible **as levels**, because the corrected
  grid respects their source support.
- **18 carry `ALIASING_RISK`** — the 14 CER channels plus `bt`, `ip`,
  `prmtan_neped`, `prmtan_teped`. Levels admissible; derivatives flagged; no
  high-frequency claim.

## The `vsurf` / equilibrium time-base observation

S7.4 found `vsurf` shares the equilibrium family's temporal support and sample
counts in all 62 discharges. **Preserved as provenance history.**

No inference that `vsurf` is an EFIT output is drawn from shared time base
alone, and no EFIT recovery campaign was undertaken.

Since `vsurf` is now neither the target nor a primary predictor, its status is:

```
NOT_MATERIAL_TO_PRIMARY_Q_REC_AFTER_RECONCILIATION
```

The observation remains on record in case a later stage brings `vsurf` back into
scope.

## Unchanged

Fail-closed EFIT removal · sibling rule · target exclusion · target-history
exclusion · unit and type rules · no `PROVENANCE_RELAXED` branch · the 20/42
cohort · the class policy · every threshold.
