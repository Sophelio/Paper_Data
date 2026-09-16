# E2.1 — Support stability (descriptive)

Six outer folds produced **six different supports**, all of size 12. This is
reported descriptively. **No exact-support agreement is required and no
support-stability gate exists.**

Machine-readable: `support_recurrence.csv`, `coordinate_recurrence.csv`,
`constructor_recurrence.csv`.

---

## Overlap

| | |
|---|---|
| supports | 6, all size 12 |
| any two identical | **no** |
| mean pairwise Jaccard | **0.285** |
| max pairwise Jaccard | 0.600 |
| distinct coordinates across all six | **35** |

Six supports of twelve coordinates drawn from a 3 451-coordinate basis share on
average about a quarter of their content. The relational representation is
**not uniquely identified** by this object.

## Coordinate recurrence

**In all six supports:**

- `ID(pcdiamag3)`
- `RATIO(ece21,cerqtit10)`

**In at least four:**

- `ID(pcdiamag3)` · `RATIO(ece21,cerqtit10)` ·
  `RATIO(prmtan_neped,cerqtit3)` · `RECIP(cerqtit10)` · `RATIO(tinj,ece20)`

## Constructor recurrence

| C0 | C2 | C3 | C5 | C6 | C7 |
|---|---|---|---|---|---|
| 7 | 16 | **34** | 11 | 2 | 2 |

Level–level **ratios (C3)** dominate — 34 of the 72 selected coordinate slots —
followed by products (16) and reciprocals (11). Derivative-bearing families
(C6, C7) appear only twice each; C1 not at all.

## Reading

This repeats, under a different contract and a fresh search, the lesson S7.9 and
S7.11 established in Epoch 1:

> **Stable reconstruction utility with non-unique relational supports.**

Six independent searches, each blind to its own fold's target values, converged
on comparable reconstruction performance through substantially different
coordinate sets. That is a scientifically meaningful finding in its own right —
the object supports a *family* of adequate relational representations rather than
identifying one.

It must **not** be described as identifying a canonical DIII-D density equation.

## `ID(pcdiamag3)` — recurring, and still uncalibrated

`ID(pcdiamag3)` appears in **all six** supports, as it appeared in 100 % of
Epoch-1's 217 bootstrap winners. Its persistence across two contracts, two
epochs and nine independent searches is a real observation.

It changes nothing about its interpretation:

> `pcdiamag3` remains **`UNCALIBRATED_SIGNAL`** — uncalibrated digitiser output
> for which no unit exists. Its fitted coefficient has **no certified
> physical-dimensional interpretation**, however often it is selected.

## Carried coefficient qualifications

- shared structural support does **not** imply universal coefficients;
- the six fold-specific supports genuinely differ;
- coefficients are locally calibrated per discharge and block;
- `prmtan_neped`, where selected, is provenance-certified independent of the
  target *signal* — not physically or statistically independent of line-averaged
  density;
- `gasa`…`gasd` are actuator **command voltages**, not fueling rates.

The Epoch-2 primary result is **reconstruction utility and relational
organization** — not universal plasma coefficients.
