# `C_E2_ALL_DESC` — the full-object descriptive representation

Freeze **`D3D-SIR-S7.E2.2-FULL-OBJECT-DESCRIPTIVE-REPRESENTATION-V1`**
Status **`FULL_OBJECT_DESCRIPTIVE_REPRESENTATION_FROZEN`** · 34/34 acceptance
`sha256 = e7935c35fd30…` · size **12**

> **This is not validation evidence.** The qualification evidence for `q_rec` is
> the six cross-fitted supports of E2.1 and their out-of-fold result. This
> representation was selected using all 62 discharges *after* that verdict was
> frozen, for visualization, figure annotation and exposition. It is
> **representative**, not unique, not held out, not externally validated, and not
> a canonical equation.

---

## The 12 coordinates

| # | coordinate | constructor | scientific families | in *k* of 6 folds |
|---|---|---|---|---|
| 1 | `ID(pcdiamag3)` | C0 level | magnetics | **6** |
| 2 | `RATIO(ece21,cerqtit10)` | C3 ratio | ECE Te · CER rotation/Ti | **6** |
| 3 | `RATIO(tinj,ece20)` | C3 ratio | neutral beams · ECE Te | 5 |
| 4 | `RECIP(cerqtit10)` | C5 reciprocal | CER rotation/Ti | 4 |
| 5 | `PROD(ece37,ece39)` | C2 product | ECE Te profile | 3 |
| 6 | `RATIO(fs03da,cerqtit3)` | C3 ratio | filterscope Dα · CER | 3 |
| 7 | `RATIO(ip,ece39)` | C3 ratio | magnetics · ECE Te | 3 |
| 8 | `RATIO(pinj_33r,cerqtit10)` | C3 ratio | neutral beams · CER | 2 |
| 9 | `RATIO(prmtan_neped,ece38)` | C3 ratio | density · ECE Te | 1 |
| 10 | `PROD(pinj,pinj_30l)` | C2 product | neutral beams | **0** |
| 11 | `RATIO(gasc,cerqtit10)` | C3 ratio | gas injection · CER | **0** |
| 12 | `RATIO(gasc,cerqtit11)` | C3 ratio | gas injection · CER | **0** |

**Composition.** C3 level–level ratios 8 · C2 products 2 · C0 level 1 · C5
reciprocal 1. No derivative-bearing coordinate (C1, C6, C7) was selected — the
same pattern the six cross-fitted supports show, where C6 and C7 contributed two
slots each out of seventy-two and C1 none.

**Primitives (17).** `cerqtit3` `cerqtit10` `cerqtit11` · `ece20` `ece21`
`ece37` `ece38` `ece39` · `pinj` `pinj_30l` `pinj_33r` `tinj` · `ip`
`pcdiamag3` · `fs03da` · `gasc` · `prmtan_neped`.

**Families (7).** CER rotation/Ti 6 · ECE Te profile 5 · neutral beams 3 ·
magnetics 2 · gas injection 2 · filterscope Dα 1 · density 1.

## How it was selected

One fresh search over `C_E2_FULL_DOMAIN` (**3 451** range-supported coordinates,
hash verified before any target was opened), under
`SIGMA_REC_ONE_SEED_PRIMARY_V2` adapted mechanically to the whole object: 108
strata, a 461-coordinate constructor-balanced shortlist capped at 96 per
constructor, one seed per stratum, lockstep greedy expansion to at most 12.

**127 642 proposals** against the frozen 300 000 budget; 102 100 distinct
supports on the frontier. No second seed, no budget extension, no reuse of the
six E2.1 supports as candidates.

`U_rec` was applied unchanged. Rank 1 admitted **3 212** practically equivalent
supports; Rank 2 stability reduced that to **one**, so Ranks 3–5 were
non-binding — the same structure as every fold of Epoch 2 and as Epoch 1.

| `U_rec` quantity | |
|---|---|
| FIT | 0.177509 |
| best FIT in the frontier | 0.170105 |
| BLOCK_WORST (block A) | 0.190286 |
| SHOT_P90 | 0.244117 |
| support size / active terms | 12 / 12 |
| `COND_MEDIAN` / P90 / MAX | 2.004 / 2.380 / 2.933 |
| bootstrap selection frequency | **0.009** |
| block-omission frequency | **0.000** |
| distinct bootstrap winners | **365** |

The size was not forced. `U_rec` selected 12 on its own.

## Descriptive fit — in-sample, not a validation metric

Over the 186 discharge–block cells of the whole object:

| | |
|---|---|
| mean discharge NRMSE | 0.1775 |
| median | 0.1539 |
| p90 | 0.2441 |
| max | **0.9242** (187024) |
| discharges above 1.0 | **0** |
| earlier era (35) / later era (27) | 0.1963 / 0.1532 |

**These numbers must never be compared with the E2.1 cross-fitted result as
though they were competing accuracy claims.** They are in-sample by
construction: every discharge here contributed its own target values to the
search that chose this support. The cross-fitted 0.1891 is the qualification
evidence; this 0.1775 is a description of the same object by a representation
that saw all of it. That the two are close is unsurprising and is not evidence
of anything.

## Relation to the six cross-fitted supports

Compared **after** freezing, and the comparison did not influence selection.

| fold | shared | Jaccard |
|---|---|---|
| 0 | 4 | 0.200 |
| 1 | **8** | **0.500** |
| 2 | 4 | 0.200 |
| 3 | 6 | 0.333 |
| 4 | **8** | **0.500** |
| 5 | 3 | 0.143 |

Mean Jaccard **0.313**, and **it is identical to none of them**. It shares both
coordinates that appear in all six folds — `ID(pcdiamag3)` and
`RATIO(ece21,cerqtit10)` — plus `RATIO(tinj,ece20)` (5 of 6) and
`RECIP(cerqtit10)` (4 of 6).

Three coordinates appear in **no** fold support: `PROD(pinj,pinj_30l)`,
`RATIO(gasc,cerqtit10)`, `RATIO(gasc,cerqtit11)`.

This is the seventh independent search over this object and it produced a
seventh distinct support. **Support non-uniqueness is reinforced, not resolved.**

## A note on the gas coordinates

Two of the twelve coordinates are ratios built on `gasc`. Gas actuation was the
site of the Epoch-1 failure, where `PROD(gasa,gasa)` extrapolated some 8 979
calibration standard deviations outside its calibrated range. Its reappearance
here, in a different form and under the range-support contract, is worth
observing and worth **not** over-reading:

- the failing Epoch-1 coordinate was a **self-product**; these are **ratios**
  against a CER temperature channel, and are dimensionless in the actuator;
- both satisfy `P-RANGE-SUPPORT` at `tau = 1` on every one of the 186 cells,
  which is why they are in the basis at all;
- **no causal claim** follows. This is one descriptive search, not a controlled
  comparison, and gas actuation was never shown to be the *only* thing that
  differed between the epochs.

`gasa`…`gasd` remain **actuator command voltages**, not fueling rates.

## Carried qualifications

- **`pcdiamag3` remains `UNCALIBRATED_SIGNAL`.** It appears here, in all six
  cross-fitted supports, and in 100 % of Epoch-1's 217 bootstrap winners. That
  recurrence is a real observation about the search; it confers **no certified
  physical-dimensional interpretation** on its fitted coefficient.
- **`prmtan_neped`** is provenance-certified independent of the target *signal*
  under the frozen information boundary. That is not physical or statistical
  independence from line-averaged density.
- **Coefficients are locally calibrated** per discharge and per block. There is
  no universal coefficient vector, and structural recurrence of a coordinate
  does not imply coefficient transfer.
- Bootstrap selection frequency **0.009** with **365** distinct winners: this
  support is one member of a large practically equivalent family, selected by a
  frozen deterministic rule, not a uniquely identified relation.

## What it may be used for

Figure-6 coordinate labels · a descriptive relational schematic · a
representative relation display · explanation of relational coordinate
composition · a supplemental coordinate table.

Any displayed equation must be labelled a **representative full-object
descriptive relation** — never a validated DIII-D equation, a canonical
relation, or a universal relation.
