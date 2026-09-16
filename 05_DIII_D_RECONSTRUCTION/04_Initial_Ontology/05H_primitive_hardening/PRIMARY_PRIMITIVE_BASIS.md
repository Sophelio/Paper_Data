# The hardened primary primitive basis `P_hard`

Machine-readable: `primitive_basis_full.csv` (78), `primitive_basis_hardened.csv`
(70), `primitive_basis_deferred.csv` (8), `pairwise_redundancy_audit.csv` (828
pairs), `redundancy_representatives.csv`, `effective_rank_audit.csv`

```
|P_full| = 78      |P_hard| = 70      |P_deferred| = 8
```

---

## The frozen rule, and what it did

Thresholds were hashed **before any development value was read**
(`d8c81421…`), and were not changed afterwards:

```
STABLY_NEAR_REDUNDANT(i,j)  iff
    n_valid_cells   >= 54        (of a nominal 60 = 20 discharges x 3 blocks)
    R_med           >= 0.99      median |Pearson r| over cells
    R_10            >= 0.97      10th percentile |r| over cells
    sign_consistency>= 0.95
```

**828 within-group pairs audited. 9 qualified.**

## The 8 deferred primitives, each with a direct witness

| Deferred | Representative | `R_med` | `R_10` | sign | cells |
|---|---|---|---|---|---|
| `fs04da` | `fs04` | **1.000000** | **1.000000** | 1.00 | 60 |
| `ece17` | `ece16` | 0.999449 | 0.998156 | 1.00 | 60 |
| `ece23` | `ece22` | 0.998590 | 0.977778 | 1.00 | 60 |
| `ece24` | `ece25` | 0.998555 | 0.971624 | 1.00 | 60 |
| `ece26` | `ece25` | 0.998391 | 0.975619 | 1.00 | 60 |
| `ece32` | `ece31` | 0.997947 | 0.980865 | 1.00 | 60 |
| `ece34` | `ece33` | 0.997668 | 0.977173 | 1.00 | 60 |
| `ece40` | `ece39` | 0.994571 | 0.983873 | 1.00 | 60 |

Every deferral rests on a **direct** witness to its own representative. No
transitive deletion was performed: `A→B` and `B→C` never justified deferring
`C` to `A`.

Every qualifying pair is **adjacent in channel index** — the expected signature
of a spatially contiguous radiometer array — except `fs04`/`fs04da`.

### A provenance flag: `fs04` and `fs04da`

These two correlate at **|r| = 1.000000 in all 60 cells**. That is not the
behaviour of two distinct viewing chords; it is consistent with one underlying
measurement stored under two names, possibly rescaled. S7.1 recorded them as
separate filterscope channels with identical units and identical resampling
records.

Recorded here as a **provenance item for follow-up**. It is not asserted as
identity, and it changed nothing: the frozen rule defers `fs04da` to `fs04`
regardless of the cause.

## Groups where little or no redundancy was found

| Group | n | Representatives | Redundant pairs |
|---|---|---|---|
| `X_ECE` | 40 | **33** | 8 of 780 |
| `X_CER_Ti` | 7 | **7** | **0** of 21 |
| `X_CER_v` | 7 | **7** | **0** of 21 |
| `X_fs` | 4 | **3** | 1 of 6 |

**Neither CER group yielded a single redundant pair.** The seven rotation
chords and the seven ion-temperature chords are each retained in full — the
frozen criterion found no pair stable enough to call one a restatement of
another.

## The 20 non-eligible primitives, all retained automatically

`X_NBI` (10), `X_mag` (4), `X_gas` (4), `X_density_aux` (2) were ruled
redundancy-ineligible on **metadata alone**, before values were opened:
different beamlines and a torque quantity; four distinct magnetic and
uncalibrated quantities; four distinct gas valves; a density and a temperature.

None was tested for correlation, and none could have been deferred however
strongly its members happened to correlate. That is the point of §7: correlation
between *distinct actuators* is not redundancy.

## Family composition — before and after

| Family | before | after | share before | share after |
|---|---|---|---|---|
| **ECE** | 40 | **33** | **0.513** | **0.471** |
| CER rotation / Ti | 14 | 14 | 0.179 | 0.200 |
| neutral beams | 10 | 10 | 0.128 | 0.143 |
| magnetics | 4 | 4 | 0.051 | 0.057 |
| gas injection | 4 | 4 | 0.051 | 0.057 |
| filterscope | 4 | 3 | 0.051 | 0.043 |
| density | 2 | 2 | 0.026 | 0.029 |

> **Instrumentation-density bias was NOT materially reduced.** The ECE share of
> the primitive basis falls only from **51.3% to 47.1%**. The stated motivation
> — preventing one diagnostic family from occupying disproportionate
> combinatorial weight — is barely served by the primitive-space component of
> this hardening.

That is the honest outcome of a conservative rule frozen in advance. It was not
tuned to produce a better-looking number.

## The effective-rank audit disagrees strongly

`AUDIT_ONLY_NEVER_SELECTION`.

| Group | members | representatives | median rank @95% | @99% |
|---|---|---|---|---|
| `X_ECE` | 40 | **33** | **3.0** | 7.0 |
| `X_CER_v` | 7 | 7 | 3.0 | 4.0 |
| `X_CER_Ti` | 7 | 7 | **2.0** | 3.5 |
| `X_fs` | 4 | 3 | 2.0 | 3.0 |

A target-blind SVD on the calibration intervals suggests each group's linear
effective rank is **far below** the number of representatives selected — ECE
needs about 3 components for 95% of variance, against 33 retained.

**The disagreement is recorded and was not acted on.**

The reconciliation is that the frozen criterion is **pairwise and conservative**
by design. A group can have low collective rank while no individual *pair* meets
a direct-witness bar. Concretely: **40 of 780 ECE pairs reach `R_med ≥ 0.99`,
but 32 of those fail `R_10 ≥ 0.97`** — they are near-redundant typically, and
not in the worst tenth of discharge/block cells. `R_10` is the binding
threshold, and it is doing exactly what §8 designed it to do.

A rank-based rule would compress far harder. It was explicitly forbidden as a
selection mechanism (§9), and rightly: replacing observed channels with SVD
components would abandon scientifically legible primitives, which is the
opposite of what this ontology is for.

## What was never used

No density value. No predictor–target correlation, mutual information, or
feature importance. No model, no baseline. No signal was deferred because it
"probably does not matter for density".

`REDUNDANCY_DEFERRED` ≠ `SCIENTIFICALLY_INADMISSIBLE` ≠ `TARGET_IRRELEVANT`.
All 8 deferred channels remain in the extended sensitivity ontology.
