# Target selection audit

Machine-readable: `target_ranking.csv`, `target_eligibility_matrix.csv`,
`target_feasibility_metrics.csv`, `algebraic_duplicate_audit.csv`

## Chain

```
95 quantities in O
  -> 64 candidates          (frozen class policy, metadata only)
  -> 62 eligible            (12 criteria, development-only values)
  -> 1 primary target       (deterministic lexicographic rule)
```

## 95 → 64: class policy, no override

| Excluded | n | Reason |
|---|---|---|
| `EQUILIBRIUM_DERIVED` | 15 | all `LINEAGE_PARTIAL`; EFIT ancestry unresolved |
| `CONTROL_COMMAND_OR_ACTUATION` | 14 | reconstructing an actuator command describes the control system |
| uncalibrated raw | 2 | `pcbcoil`, `pcdiamag3` — no physical unit exists |
| **candidates** | **64** | 7 `DIRECT_MEASUREMENT` + 57 `DIAGNOSTIC_RECONSTRUCTION` |

Decided from frozen metadata alone, before any value was opened. No override was
exercised (H-C).

## 64 → 62: eligibility

All twelve criteria applied independently, plus the NRMSE-scale requirement.

| Criterion | Failures |
|---|---|
| C1 scalar · C2 available · C3 interpretable · C4 unit · C5 class | 0 |
| C6 ≥10 predictors after closure | 0 (range 40–79) |
| C7 no event taxonomy · C8 no regime classification | 0 |
| C9 no algebraic duplicate | 0 |
| **C10 meaningful variation (`RRV_dev` ≥ 0.05)** | **2** |
| C11 both processing eras | 0 |
| C12 no label pipeline | 0 |
| invalid NRMSE blocks > 0 | 0 |

**The two failures are `bt` (`RRV_dev` = 0.0037) and `ip` (0.0042).** Both are
flat-top quantities: on a 20 ms grid their median absolute deviation is a few
tenths of a percent of their RMS, so a constant predictor would be nearly
exact by construction. This is precisely what the robust variation floor exists
to catch, and it is why S7.2C replaced ordinary CV — for `ip`, with a large
non-zero mean, ordinary CV would also have been small, but for a sign-changing
candidate it would have been meaningless or undefined.

Both would have failed at Level 1 anyway, each carrying two major flags.

### C9 method

Definitional and provenance only. S7.1 records one-to-one signal identity with
no aliases; the sole documented deterministic algebraic relation in the object
is `pinj = Σ pinj_*`, removed by rule R3 where applicable; same-quantity channel
series are removed by the sibling rule. **No correlation, regression, inversion
or performance was used.**

## 62 → 1: deterministic ranking

| Rank | Candidate | L1 flags | L2 predictors | L3 families | L4 `RRV_dev` | L4 margin | L5 index | Resolved at |
|---|---|---|---|---|---|---|---|---|
| **1** | **`vsurf`** | **0** | **79** | **7** | **0.1797** | **0.1297** | **5** | — |
| 2 | `density` | 0 | 79 | 7 | 0.0983 | 0.0483 | 21 | **L4** |
| 3 | `fs05da` | 0 | 76 | 6 | 0.4640 | 0.4140 | 27 | L2 |
| 4 | `fs04` | 0 | 76 | 6 | 0.3314 | 0.2814 | 24 | L2 |
| 5 | `fs04da` | 0 | 76 | 6 | 0.3314 | 0.2814 | 26 | L2 |
| 6 | `fs03da` | 0 | 76 | 6 | 0.2375 | 0.1875 | 25 | L2 |
| 7 | `ece7` | 0 | 40 | 6 | 0.2537 | 0.2037 | 48 | L2 |
| 8 | `ece6` | 0 | 40 | 6 | 0.2519 | 0.2019 | 47 | L2 |

`rank_resolution_level` = the first level at which each candidate ceased to tie
with the winner.

**Note what the rule did *not* do.** `fs05da` has by far the largest variation
margin (0.4140 against `vsurf`'s 0.1297) and would win any variation-weighted
score. It ranks third because Level 2 comes first: as a filterscope target it
loses its three siblings, leaving 76 predictors across 6 families rather than 79
across 7. The lexicographic ordering is doing real work — it prefers a broader
surviving information set over a more variable target, exactly as frozen.

Similarly, all 40 ECE channels are tied at Level 1 with 0 flags and several have
larger margins than `vsurf`, but each loses 39 siblings, collapsing to 40
predictors.

**No weighted score. No rank normalisation. No human choice.** `vsurf` is rank 1
and is therefore the primary target.

## Sibling-grouping ambiguity — tested, immaterial

S7.2 named "CER rotation and ion temperature (14)" as one multichannel family,
which is the *provider* group. S7.3 §11 directs that a provider grouping is not
by itself a sibling relation, and that the rule exists to prevent trivial
same-quantity channel interpolation.

CER toroidal rotation (a velocity, m/s) and CER ion temperature (a temperature,
eV) are different physical quantities with different dimensions. The primary
reading therefore splits them into two sibling subfamilies of 7.

Because this could in principle move CER candidates' Level 2 key, the
alternative reading was evaluated explicitly: treating the whole CER group as
one sibling family removes 7 further predictors from every CER candidate.

**The winner is `vsurf` under both readings** — no CER candidate is competitive
at Level 1 (all carry U010) let alone Level 2. Recorded in
`manifests/SIBLING_AMBIGUITY_SENSITIVITY.json`. The ambiguity is immaterial to
selection, so no human review was triggered under §11.

## Post-selection sanity audit

Inspected: signal identity, scientific description, unit, provenance class,
target-side flags, and whether the value belongs to the scientific object
described. **Not inspected:** reconstructability, correlation with predictors,
any reconstruction, any baseline.

No new documentation or provenance defect found → **`TARGET_SELECTION_CONFIRMED`**.
The defect-substitution procedure was not invoked.

## Firewall

20 development discharges opened for values; **0 external**. External identifiers
were known and their archives never touched. `manifests/DATA_ACCESS_LOG.csv`,
`manifests/EXTERNAL_FIREWALL_AUDIT.json`.

The target-side major-flag mapping was frozen and hashed **before** any value was
opened (`manifests/TARGET_FLAG_MAPPING_FREEZE.json`), so no flag could have been
shaped by candidate behaviour.
