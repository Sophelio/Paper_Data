# S7.10 — External domain and processing-era results

Machine-readable: `OMEGA_REC_EXTERNAL.json`, `external_era_results.csv`,
`external_denominator_audit.csv`, `common_support_audit.csv`,
`external_extrapolation_audit.csv`.

---

## Applicability — the whole intended domain was evaluated

| | |
|---|---|
| external discharges | **42** (24 earlier, 18 later) |
| discharges evaluated | **42 / 42** |
| blocks | **126** |
| blocks comparison-eligible | **126 / 126** |
| blocks `NOT_APPLICABLE` | **0** |
| denominator-block checks | 378 (3 denominators × 126 blocks) |
| denominator failures | **0** |
| minimum observed `eta` | **0.0997** on `cerqtit10` (195642, block C) — threshold 0.05 |

`C_dev_star` requires three level denominators — `prmtan_neped`, `ece22`,
`cerqtit10`. Under the inherited `DENOMINATOR_ADMISSIBILITY_PRIMARY_V1` rule
(finite · `RMS ≠ 0` · no sign change · `eta = min|d| / RMS(d) ≥ 0.05`), **every
one of the 378 checks passed** on the external local-calibration blocks. Per
denominator, the minimum `eta` observed was 0.0997 (`cerqtit10`), 0.1107
(`prmtan_neped`) and 0.1689 (`ece22`) — all at least twice the threshold. No
epsilon, no clipping, no shift, no bounded reciprocal, no repair — none was
needed and none was applied.

The relational representation was therefore applicable everywhere, and no
discharge or block was excluded for any reason. There is no
result-dependent discharge deletion, and the domain was never expanded beyond
the frozen candidate object.

## Processing-era results — reported in full

Discharge-level mean NRMSE:

| Method | Earlier (24) | Later (18) |
|---|---|---|
| **REL** | **1.1643** | **0.1798** |
| B0 | 0.8735 | 0.9877 |
| B1 | 0.2104 | 0.2101 |
| B1A | 0.3325 | 0.3744 |
| B2 | 0.2657 | 0.3000 |
| B3 | 0.3566 | 0.2384 |
| H0 | 0.2644 | 0.3073 |

Discharge-level **median** NRMSE:

| Method | Earlier (24) | Later (18) |
|---|---|---|
| **REL** | **0.1821** | **0.1696** |
| B1 | 0.1753 | 0.1909 |
| B2 | 0.1974 | 0.1629 |
| B3 | 0.1806 | 0.1735 |
| H0 | 0.1914 | 0.1735 |

The two eras are **indistinguishable in the median** (0.182 vs 0.170) and
separated by a factor of six in the mean (1.164 vs 0.180). The entire era
difference is two earlier-era discharges.

## V6 operational reading

| Era | `Δ₀` vs B0 | direction | `Δ₁` vs B1 | direction |
|---|---|---|---|---|
| earlier (24) | **+0.291** | `MATERIAL_ADVERSE` | **+0.954** | `MATERIAL_ADVERSE` |
| later (18) | **−0.808** | `MATERIAL_IMPROVEMENT` | **−0.030** | `MATERIAL_IMPROVEMENT` |

Era 95 % CIs (10 000 replicates; seeds `2026090504` earlier, `2026090505` later):

| Comparator | Earlier `Δ` [CI] | Later `Δ` [CI] |
|---|---|---|
| B0 | +0.291 [−0.712, +1.714] | −0.808 [−0.913, −0.698] |
| B1 | +0.954 [−0.037, +2.418] | −0.030 [−0.071, +0.007] |
| B2 | +0.899 [−0.052, +2.300] | −0.120 [−0.241, −0.019] |
| B3 | +0.808 [−0.172, +2.198] | −0.059 [−0.119, −0.006] |
| H0 | +0.900 [−0.049, +2.299] | −0.128 [−0.253, −0.022] |

**V6 = FAIL.** The three-valued S7.2C schema presupposes pooled V3 passing; it
did not.

> The later era meets both V3 thresholds on its own, and its CI against B0
> excludes zero. **This is evidence, not a claim.** Narrowing `Omega_rec` to the
> later era in order to obtain a passing V3 is explicitly forbidden by the
> frozen contract, and was not done. A materially adverse era is not averaged
> away, and neither is it discarded.

## Why the earlier era fails — diagnosis, not repair

`external_extrapolation_audit.csv` records, for every block, the maximum
standardized excursion of the twelve coordinates on the protected rows relative
to their calibration distribution.

| Shot | Era | Block | max \|z\| protected | worst coordinate | discharge NRMSE |
|---|---|---|---|---|---|
| **187019** | earlier | **B** | **8 978.6** | `PROD(gasa,gasa)` | **11.95** |
| **187022** | earlier | **B** | **8 958.6** | `PROD(gasa,gasa)` | **11.77** |
| 160717 | earlier | C | 13.0 | `RATIO(ip,ece22)` | 0.37 |
| 195269 | later | B | 12.4 | `PROD(prmtan_neped,prmtan_neped)` | 0.21 |

The next-largest excursion in the entire cohort is **13 σ**. Two blocks reach
~9 000 σ.

On 187019 block B the gas-injection valve command `gasa` spans
5.3 × 10⁻³ … 4.1 × 10⁻² across the calibration interval and reaches **1.63**
inside the protected window — a ~40× excursion beyond anything the local
calibration saw. Squaring it puts `PROD(gasa,gasa)` roughly 9 000 calibration
standard deviations out, and the affine relation extrapolates linearly into
catastrophe.

The log–log correlation between a discharge's maximum protected excursion and
its relational NRMSE is **0.930**.

**Why the frozen domain rule did not catch it.** `DENOMINATOR_ADMISSIBILITY_PRIMARY_V1`
guards *denominators*. The frozen S7.6R partial-map policy states plainly that
*"C0, C1, C2 and C6 have no denominator and no gate"*. `PROD(gasa,gasa)` is a C2
self-product, so it carries **no domain gate at all**. This is not a violation
of the rule, not leakage, and not an implementation error — it is an unguarded
*range* excursion in a product coordinate, in a contract whose only partial-map
guard was written for division.

That observation is recorded as a finding. It is **not** acted on here: no
coordinate was removed, no range rule was added, no discharge was deleted. Any
prospective range-admissibility rule for non-denominator constructors would be a
new contract decision for a future study, not a repair of this one.

## `Omega_rec` — the externally supported claim domain

```
supported_claim_domain : EMPTY
```

The full intended external domain — all 42 discharges, all 126 blocks — was
evaluated successfully and completely. But mandatory gate V3 failed on that
domain, and V6 cannot resolve to PASS while it does. **No external domain
supports a successful structural-transfer claim.**

`Omega_rec` was not narrowed to an era, and it was never expanded beyond the
frozen candidate object.
