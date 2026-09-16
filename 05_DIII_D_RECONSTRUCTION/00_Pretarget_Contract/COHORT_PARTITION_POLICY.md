# S7.2 — Cohort partition policy

Machine-readable: `COHORT_PARTITION.json` ·
Freeze: `manifests/COHORT_PARTITION_FREEZE.json`

## Why the partition is frozen now, before S7.3

S7.3 will need to inspect candidate-target properties — dynamic range, temporal
variation, missingness — to apply eligibility criteria 6, 9 and 10. **Those
diagnostics must not touch the eventual external cohort.** If the partition were
made after that inspection, external data would already have influenced target
selection.

So the firewall must exist before the first target value is ever examined.

## Method — deterministic, target-blind

**Inputs used:** shot identifiers; operational period membership; processing era.
**Inputs not used:** any signal value, any target value, any outcome. The script
does not open a single archive.

**Rule:** within each operational period, sort discharges ascending and select
those at position `i` with `i % 3 == 1`.

Position 1 rather than 0 avoids systematically claiming the first discharge of
every period. **No randomness, therefore no seed.** The rule is reproducible from
the shot list alone.

### The singleton

Period 1 holds one discharge (155537) and cannot be split. It is assigned to
**external**, so the external cohort — where the generalisation claim is tested
— covers all seven periods. Development covers six. The alternative would give
development a period the external cohort lacks, which is the worse trade.

---

## The frozen partition

| | n | share | earlier era | later era | periods |
|---|---|---|---|---|---|
| **development** | **20** | 32.3% | 11 | 9 | 2–7 (6 of 7) |
| **external** | **42** | 67.7% | 24 | 18 | 1–7 (7 of 7) |
| total | 62 | | 35 | 27 | 7 |

Era balance is close to the object's own 35/27 = 56/44 split: development 55/45,
external 57/43. Neither cohort is era-skewed.

### Per period

| Period | Shots | n | Era | Dev | Ext |
|---|---|---|---|---|---|
| 1 | 155537 | 1 | earlier | 0 | 1 |
| 2 | 159310–161414 | 10 | earlier | 3 | 7 |
| 3 | 165017–165965 | 13 | earlier | 4 | 9 |
| 4 | 170394–170411 | 3 | earlier | 1 | 2 |
| 5 | 186997–187024 | 8 | earlier | 3 | 5 |
| 6 | 189646–189652 | 6 | later | 2 | 4 |
| 7 | 195261–195659 | 21 | later | 7 | 14 |

Every period with more than one discharge contributes to both cohorts,
including the small period 4.

### Development (20)

```
160715 160720 161138 165022 165028 165042 165861 170396 187017 187020
187024 189647 189651 195264 195267 195273 195638 195647 195650 195655
```

### External (42)

```
155537 159310 160717 160719 160721 161136 161145 161414 165017 165026
165027 165029 165031 165043 165860 165955 165965 170394 170411 186997
187018 187019 187021 187022 189646 189649 189650 189652 195261 195265
195266 195268 195269 195274 195626 195642 195645 195648 195649 195651
195652 195659
```

---

## Rationale for ~1/3 : 2/3

Development is large enough to support representation discovery across both
eras and six periods, while the external cohort stays large enough (42
discharges) that the discharge-level bootstrap in
`STATISTICAL_INFERENCE_PLAN` has real power. Since **discharge is the
inferential unit**, external cohort size *is* the effective sample size — 42 is a
respectable n; 20 would not be.

## Immutability

The partition is frozen and hashed. It may not be revised for any reason
connected to results. If a discharge later proves unusable for a specific target
on **provenance or availability** grounds, it is dropped from that target's
`Omega_rec` with a recorded reason — the partition itself does not change, and
no discharge ever moves between cohorts.
