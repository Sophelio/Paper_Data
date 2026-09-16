# S7.9 — Development-selected representation

**Terminology: `DEVELOPMENT_SELECTED_REPRESENTATION`.** Not externally
validated, not a structural-transfer success, not a global optimum, not a
universal relation. Selected *within* the frozen explored frontier
`AHAT_REC_DENSITY_ONE_SEED_V2`.

Machine-readable form: `SELECTED_REPRESENTATION.json`.

---

## `C_dev_star`

```
ID(cerqtit6)|ID(pcdiamag3)|ID(prmtan_neped)|PROD(ece37,ece39)|PROD(gasa,gasa)|
PROD(pinj,cerqrott6)|PROD(prmtan_neped,prmtan_neped)|RATIO(ece21,prmtan_neped)|
RATIO(fs03da,prmtan_neped)|RATIO(ip,ece22)|RECIP(cerqtit10)|RECIP(prmtan_neped)
```

Support size **12** (the frozen maximum). Atoms are ascending-sorted; the
canonical serialization reproduces the registry `support_id` exactly.

## The twelve coordinates

| # | Coordinate | Constructor | Physical reading | Frozen output dimension |
|---|---|---|---|---|
| 1 | `ID(cerqtit6)` | C0 identity level | CER ion temperature, channel 6 | `eV` |
| 2 | `ID(pcdiamag3)` | C0 identity level | diamagnetic loop signal — **uncalibrated** | `UNCALIBRATED` |
| 3 | `ID(prmtan_neped)` | C0 identity level | pedestal electron density (tanh fit) | `m^-3` |
| 4 | `PROD(ece37,ece39)` | C2 level–level product | ECE radiometer ch. 37 × ch. 39 | `(eV)*(eV)` |
| 5 | `PROD(gasa,gasa)` | C2 self-product | gas injection valve command A, squared | `(V)*(V)` |
| 6 | `PROD(pinj,cerqrott6)` | C2 level–level product | injected beam power × CER toroidal rotation ch. 6 | `(W)*(m s^-1)` |
| 7 | `PROD(prmtan_neped,prmtan_neped)` | C2 self-product | pedestal density squared | `(m^-3)*(m^-3)` |
| 8 | `RATIO(ece21,prmtan_neped)` | C3 level–level ratio | ECE ch. 21 / pedestal density | `(eV)/(m^-3)` |
| 9 | `RATIO(fs03da,prmtan_neped)` | C3 ratio | filterscope D-α / pedestal density | `(ph sr^-1 m^-2 s^-1)/(m^-3)` |
| 10 | `RATIO(ip,ece22)` | C3 ratio | plasma current / ECE ch. 22 | `(A)/(eV)` |
| 11 | `RECIP(cerqtit10)` | C5 unary reciprocal | 1 / CER ion temperature ch. 10 | `(eV)^-1` |
| 12 | `RECIP(prmtan_neped)` | C5 unary reciprocal | 1 / pedestal density | `(m^-3)^-1` |

Dimensions are quoted verbatim from the frozen coordinate universe. Units are
canonical (ECE keV → eV, `pinj` kW → W, `cerqrott6` km/s → m s⁻¹, `fs03da`
ph/(sr cm² s) → ph sr⁻¹ m⁻² s⁻¹) under the S7.5H canonicalization.
`ID(pcdiamag3)` carries `UNCALIBRATED` rather than a unit because no unit
exists upstream.

Exact units, temporal-resolution rules, provenance lineage and realization ids
for each coordinate are in `SELECTED_REPRESENTATION.json`.

## Composition

**Constructors:** C0 × 3 · C2 × 4 · C3 × 3 · C5 × 2.
**No C6, no C7** — and no C1 derivative coordinate either. The support is built
entirely from levels, products, ratios and reciprocals.

**Scientific ancestor families (7):** `cer_rotation_ti`, `density`,
`ece_te_profile`, `filterscope_dalpha`, `gas_injection`, `magnetics`,
`neutral_beams`.

**Thirteen primitive ancestors:** `cerqrott6`, `cerqtit10`, `cerqtit6`,
`ece21`, `ece22`, `ece37`, `ece39`, `fs03da`, `gasa`, `ip`, `pcdiamag3`,
`pinj`, `prmtan_neped`.

`prmtan_neped` is the structural centre of the support: it appears in five of
the twelve coordinates — as a level, squared, as a reciprocal, and as the
denominator of two ratios.

## Development-side utility quantities

| Quantity | Value |
|---|---|
| `FIT` | **0.166397565** |
| `FIT_best` in `E0` (different support) | 0.166281515 |
| gap to `FIT_best` | +0.000116050 |
| `SE_delta` vs best | 0.000254 |
| `delta_equiv` vs best | 0.01 (floor binding) |
| `BLOCK_WORST` | **0.194251699** |
| `b_star` | **A** |
| `SHOT_P90` | **0.211412116** |
| `ACTIVE_TERMS` | 12 of 12 |
| `COND_MEDIAN` (log₁₀ κ) | **1.991754** |
| `COND_P90` | 2.173042 |
| `COND_MAX` | 2.259641 |
| infinite conditioning cells | 0 |
| degenerate-sd cells | 0 |
| `BOOT_SELECTION_FREQ` | **0.093** |
| `FOLD_SELECTION_FREQ` | **0.333** |

All quantities are development-side. None is a claim about external transfer.

## Interpretation flags

**`UNCALIBRATED_SIGNAL` — carried.** The support contains `pcdiamag3`, recorded
in S7.1 as uncalibrated digitiser output for which no unit exists.

> Coefficients involving the uncalibrated primitive have **no certified
> physical-dimensional interpretation**.

This is an *interpretation qualification*, not a selection exclusion. The
support was not rejected for it.

**Density-family predictor.** `prmtan_neped` belongs to the `density` scientific
family — the same family as the target. All thirteen primitive ancestors are
`certified_independent_of_target` under the frozen S7.3R information boundary,
and every one of the twelve coordinates carries
`TRANSITIVE_FROM_TARGET_INDEPENDENT_BOUNDARY`. V1 is therefore not compromised.
It is flagged here because a density-family predictor for a density target will
attract reader scrutiny and should be addressed explicitly rather than left to
be discovered.

**C6/C7:** absent. Reported naturally — no pruning, no penalty, no repair, and
their absence is an outcome of the frozen utility rule, not a rule about them.

**ECE ancestry:** present (`ece21`, `ece22`, `ece37`, `ece39`). No penalty, no
quota, no diversity bonus, no correction. The multiplicity-control question was
settled at S7.7 on *opportunity*.

**Other flags:** no aliasing flag set; no upsample flag set; all coordinates
`PRIMARY` (none from a sensitivity lane); no partial-map domain predicate — the
support is total on the development support.

## Selection provenance

| Set | Count | Criterion |
|---|---|---|
| `E0` | 162 845 | explored frontier |
| `E1` | 1 055 | Rank 1 primary fit |
| `E2` | **1** | Rank 2 stability ← **binding** |
| `E3` | 1 | Rank 3 parsimony (non-binding) |
| `E4` | 1 | Rank 4 conditioning (non-binding) |
| `E5` | 1 | Rank 5 support stability (non-binding) |

The binding criterion was **Rank 2**: the exact minimum `SHOT_P90` among the 227
`BLOCK_WORST`-practically-equivalent survivors, with no tie. Ranks 3–5 could
not change the outcome because `E2` was already a singleton.

## Estimator

`DEVELOPMENT_RELATION_OLS_V1` — calibration-only standardization, fitted
intercept, discharge/block-local coefficients. **There are no learned global
coefficients.** What transfers externally is the support identity, the
coordinate definitions, the numerical construction rules and the estimator
procedure. See `RELATIONAL_ESTIMATOR_CONFIG.json`.
