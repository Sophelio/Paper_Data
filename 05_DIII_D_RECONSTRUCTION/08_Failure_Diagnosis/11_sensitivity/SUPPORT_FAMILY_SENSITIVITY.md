# S7.11 — Support-family external sensitivity

The predeclared `SUPPORT_FAMILY_EXTERNAL_SENSITIVITY`: all **217** unique
Rank-4 winning supports from the frozen S7.9 development bootstrap, evaluated
externally under the identical geometry, estimator, metric and domain rule used
in S7.10.

No top-K. No external-result-based selection. No support omitted for looking
poor. **No support may replace `C_dev_star`.**

Machine-readable: `support_family_external_metrics.csv`,
`support_family_v3_results.csv`, `support_family_applicability.csv`,
`support_family_distributions.csv`, `support_family_coordinate_summary.csv`,
`S7_11_SUPPORT_FAMILY_V3_SUMMARY.json`.

---

## Applicability

| | |
|---|---|
| supports evaluated | **217 / 217** |
| full-domain (all 126 blocks, all 42 discharges) | **213** |
| not full-domain | **4** |
| reason | `E_DENOM` on 6 of 126 blocks; 40 of 42 discharges evaluable |

The four non-full-domain supports each contain `LEVEL_RATE` (C6) coordinates
whose companion denominators fail the inherited admissibility rule on six
external calibration blocks. They are **not hidden and not deleted** — they are
reported and excluded from the full-domain V3-style tally, because a support
that cannot be evaluated on the full frozen external domain may not be called a
successful full-domain transfer support.

All family-level statistics below are over the **213 full-domain** supports.

## V3-style outcome

`SENSITIVITY_V3_STYLE_PASS` — **not** the primary V3 gate, which only
`C_dev_star` owns — using the already-frozen rule
`Δ₀ ≤ −0.01 AND Δ₁ ≤ −0.01`:

| | |
|---|---|
| **V3-style pass** | **70 / 213 = 0.3286** |
| V3-style fail | 143 / 213 |
| fail on `Δ₁` only | **139** |
| fail on `Δ₀` only | 0 |
| fail on both | 4 |

Persistence is the binding comparator for essentially the entire family: no
support fails against the calibration mean alone.

## Distributions over the 213 full-domain supports

| | p0 | p5 | p25 | p50 | p75 | p95 | p100 |
|---|---|---|---|---|---|---|---|
| mean NRMSE | 0.1815 | 0.1882 | 0.1982 | 0.2099 | 0.5236 | 0.7925 | 4.9385 |
| median NRMSE | 0.1464 | 0.1520 | 0.1607 | 0.1685 | 0.1736 | 0.1813 | 0.1929 |
| `Δ₀` | −0.7409 | −0.7343 | −0.7243 | −0.7126 | −0.3988 | −0.1300 | +4.0161 |
| `Δ₁` | −0.0287 | −0.0221 | −0.0121 | **−0.0004** | +0.3133 | +0.5822 | +4.7282 |

The median-NRMSE distribution is tight (0.146–0.193 across the whole family);
the mean-NRMSE distribution is not (0.18–4.94). The family differs from itself
almost entirely in the tail.

**The passing subfamily is marginal.** Among the 70 passers, `Δ₁` ranges
−0.0287 … −0.0103, median −0.0144. **No support anywhere in the family beats
persistence by more than 0.0287 NRMSE**, and the family median `Δ₁` is −0.0004
— parity. Thirteen supports exceed the floor by more than 0.02; none by more
than 0.05. "70 supports passed" must not be read as "the family transfers
well".

## Where `C_dev_star` sits

| | value | percentile (ascending) | rank of 213 |
|---|---|---|---|
| mean NRMSE | 0.7424 | **86.4** | 184 |
| median NRMSE | 0.1699 | 56.8 | 121 |
| `Δ₁` | +0.5321 | **86.4** | 184 |

`C_dev_star` is **middling on typical-case accuracy and among the worst ~14 %
on mean error and on the persistence comparison**. It is an externally fragile
representative of its own equivalence class.

## Development selection did not predict external behaviour

| | |
|---|---|
| Spearman(development bootstrap freq, external mean NRMSE) | **−0.093** |
| Spearman(development bootstrap freq, `Δ₁`) | −0.093 |
| median bootstrap freq of V3-style passers | 0.0020 |
| median bootstrap freq of V3-style failures | 0.0010 |
| `C_dev_star` bootstrap freq | **0.093 — the highest in the family** |

The support the development bootstrap favoured most strongly is among the worst
external performers in its own family, and the correlation across the family is
essentially zero. **Development-side selection frequency carried no information
about external robustness.**

For completeness: the lowest-external-error member —
`LOWEST_EXTERNAL_ERROR_SUPPORT_IN_PREDECLARED_SENSITIVITY`, mean 0.1815, median
0.1672, `Δ₀` −0.7409, `Δ₁` −0.0287 — had a development bootstrap frequency of
**0.034**, roughly a third of `C_dev_star`'s. It is **not** a replacement
primary support, may not be called `C_star`, and confers no claim.

## What separates passers from failures

| | passers (70) | failures (143) |
|---|---|---|
| any discharge with NRMSE > 1 | **0** | **93** |
| median of max single-discharge NRMSE | 0.536 | 7.543 |

| | count |
|---|---|
| supports with median NRMSE below the persistence median (0.1765) | **186 / 213** |
| supports with mean NRMSE below the persistence mean (0.2103) | 107 / 213 |

V3-style outcome tracks **the presence of a catastrophic extrapolation tail**,
not typical-case accuracy. Most of the family is better than persistence
typically, and only half of it is better on average.

## Coordinate participation — required reporting, not selection

Participation was computed for **every** one of the 88 distinct coordinates
across four groups (`ALL_217`, `FULL_DOMAIN`, `V3_STYLE_PASS`,
`V3_STYLE_FAIL`). It is descriptive: it selects nothing, prunes nothing, gates
nothing, and asserts no causality.

Most associated with V3-style **failure**:

| coordinate | pass share | fail share | difference |
|---|---|---|---|
| **`PROD(gasa,gasa)`** | **0.000** | **0.469** | **−0.469** |
| `PROD(ece37,ece39)` | 0.271 | 0.615 | −0.344 |
| `PROD(pinj,cerqrott6)` | 0.271 | 0.538 | −0.267 |
| `RECIP(prmtan_neped)` | 0.000 | 0.217 | −0.217 |
| `RATIO(ece21,prmtan_neped)` | 0.014 | 0.210 | −0.196 |

Most associated with V3-style **pass**:

| coordinate | pass share | fail share | difference |
|---|---|---|---|
| `PROD(fs03da,cerqtit11)` | 0.871 | 0.490 | +0.382 |
| `RATIO(prmtan_neped,cerqtit10)` | 0.471 | 0.112 | +0.360 |
| `RATIO(gasd,bt)` | 0.271 | 0.014 | +0.257 |
| `PROD(bt,bt)` | 0.300 | 0.105 | +0.195 |
| `PROD(prmtan_neped,ece39)` | 0.871 | 0.692 | +0.179 |

`PROD(gasa,gasa)` is the top row of this table: it appears in **0 of 70**
passers and **67 of 143** failures. Notably its presence barely moves the
*median* (0.1643 with, 0.1698 without) while moving the *mean* from 0.201 to
0.732 — the same tail-only signature S7.10 diagnosed.

This emerged from the participation table required for every coordinate. **No
removal test was run, nothing was clipped or gated, and `PROD(gasa,gasa)`
remains in `C_dev_star`.**

`ID(pcdiamag3)` appears in **100 %** of all 217 supports. Its recurrence is
reported; **no physical coefficient meaning is inferred** — it remains
`UNCALIBRATED_SIGNAL`.

## Era structure is family-wide

| | count of 213 |
|---|---|
| `Δ₁,later ≤ −0.01` | **206** |
| `Δ₁,earlier ≤ −0.01` | **7** |

The era asymmetry S7.10 observed for `C_dev_star` is a property of the
**cohort**, not of the canonical representative: essentially the whole
development-equivalent family transfers in the later era and essentially none
of it in the earlier era. Diagnostic only — `Omega_rec` is **not** narrowed.

## Reading

The negative primary result is **not** a uniform property of the
development-equivalent family: about a third of it clears the V3-style
criterion. Nor is it evidence that the family transfers: no member exceeds
persistence by more than 0.029 NRMSE and the family median is at parity.

What the family analysis establishes is narrower and sharper — development
equivalence did not identify external robustness, and the canonical
representative was among the family's more fragile members despite being its
most frequently selected one.

**The primary S7.10 verdict is unchanged.**
