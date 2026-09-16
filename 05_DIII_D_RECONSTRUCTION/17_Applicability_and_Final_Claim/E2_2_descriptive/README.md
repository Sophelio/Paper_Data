# S7.E2.2 — Full-object descriptive representation

Freeze **`D3D-SIR-S7.E2.2-FULL-OBJECT-DESCRIPTIVE-REPRESENTATION-V1`**
Status **`FULL_OBJECT_DESCRIPTIVE_REPRESENTATION_FROZEN`** · 34/34 acceptance

```
C_E2_ALL_DESC   size 12   sha256 e7935c35fd30...
```

---

## What this is, and what it is not

| | |
|---|---|
| **is** | one representation of the whole 62-discharge object, for visualization, figure annotation, coordinate inspection and exposition |
| **is not** | externally validated · held out · the support that produced the cross-fitted metric · a canonical equation |

It was selected **after** the E2.1 qualification verdict was frozen, and it
**cannot alter** `FORMAL_PASS`, `CLEAN_DEMO_NOT_MET`, V3, V6, V-RANGE or any
cross-fitted metric. The validation evidence for `q_rec` is, and remains, the six
cross-fitted supports of E2.1.

## The support

```
ID(pcdiamag3) | PROD(ece37,ece39) | PROD(pinj,pinj_30l) |
RATIO(ece21,cerqtit10) | RATIO(fs03da,cerqtit3) | RATIO(gasc,cerqtit10) |
RATIO(gasc,cerqtit11) | RATIO(ip,ece39) | RATIO(pinj_33r,cerqtit10) |
RATIO(prmtan_neped,ece38) | RATIO(tinj,ece20) | RECIP(cerqtit10)
```

C3 ratios 8 · C2 products 2 · C0 level 1 · C5 reciprocal 1 · no derivative
family. 17 primitives across 7 scientific families.

## Selection

One fresh search over the same **3 451**-coordinate range-supported basis, hash
verified before any target was opened, under `SIGMA_REC_ONE_SEED_PRIMARY_V2`
adapted mechanically to all 62 discharges. **127 642** proposals of 300 000; one
seed per stratum; no second seed; no budget extension; the six E2.1 supports were
not reused as candidates.

`U_rec` unchanged: Rank 1 left 3 212 equivalents, Rank 2 left one. FIT 0.1775 ·
`COND_MEDIAN` 2.004 · bootstrap selection frequency **0.009** across **365**
distinct winners.

## Descriptive fit — in-sample

mean 0.1775 · median 0.1539 · max 0.9242 · 0 discharges above 1.0.

**Not a validation metric.** Every discharge contributed its own targets to the
search that chose this support. Do not compare it with the cross-fitted 0.1891 as
a competing accuracy claim.

## Seventh search, seventh support

| fold | shared / 12 | Jaccard |
|---|---|---|
| 0 | 4 | 0.200 |
| 1 | 8 | 0.500 |
| 2 | 4 | 0.200 |
| 3 | 6 | 0.333 |
| 4 | 8 | 0.500 |
| 5 | 3 | 0.143 |

Mean **0.313**, identical to **none**. Shares both coordinates common to all six
folds — `ID(pcdiamag3)`, `RATIO(ece21,cerqtit10)` — and contributes three that no
fold selected. **Support non-uniqueness is reinforced.**

## Carried qualifications

`pcdiamag3` remains **`UNCALIBRATED_SIGNAL`** — no certified physical-dimensional
meaning for its coefficient, however often it recurs. `prmtan_neped` is
independent of the target *signal*, not of density. `gasc` is an actuator
**command voltage**. Coefficients are locally calibrated; no universal
coefficient vector.

## Start here

| Document | Purpose |
|---|---|
| `E2_2_DESCRIPTIVE_REPRESENTATION_FINAL.md` | the representation in full |
| `E2_2_DESCRIPTIVE_REPRESENTATION_AUDIT_REPORT.md` | internal audit, 12 sections |

## Reproduce

```bash
python scripts/e2_2_a_verify.py   # eight parents, basis, no target access
python scripts/e2_2_b_search.py   # one fresh full-object search + U_rec
python scripts/e2_2_c_freeze.py   # comparison, acceptance, freeze
```

`EPOCH2_IS_FINAL_QREC_ATTEMPT = true`. This is not a discovery epoch, not a
rescue, not a second validation.
