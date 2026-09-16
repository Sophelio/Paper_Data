# S7.9 — Pre-external immutable freeze

`PRE_EXTERNAL_MODEL_FREEZE.json` is the object **S7.10 must verify before
opening a single external value**. Everything a comparison could depend on is
fixed and hashed inside it.

---

## Firewall state at the moment of freezing

| | |
|---|---|
| external predictor value reads | **0** |
| external target value reads | **0** |
| external model evaluations | **0** |
| external derived statistics | **0** |
| external cohort state | **`SEALED`** |
| baselines run | **0** |
| development discharges opened | 20 (of 62) |

External artifacts were read for **metadata only** — discharge ids, processing
era, cohort counts, partition policy. Metadata is not value-bearing. Every
development read is logged in `manifests/DEVELOPMENT_ACCESS_LOG.json`.

## What the package pins

| | Content |
|---|---|
| **A** target | `density` (S7.3R V2) |
| **B** selected representation | `support_id`, 12-atom list, coordinate definitions, canonical parse rule |
| **C** lineage | `G_rec`, `A_rec`, `Sigma_rec`, `Ahat_rec` (162 845) and all ten authoritative parent freeze ids |
| **D** utility | `U_REC_OPERATIONAL_V1` hash, `E0`–`E5` counts, elimination-ledger hash |
| **E** estimator | `DEVELOPMENT_RELATION_OLS_V1`; **no global coefficients exist** |
| **F** preprocessing | calibration-only mean/sd, `ddof=0`, `sd<=0 → divisor 1.0`, no epsilon |
| **G** validation geometry | A/B/C blocks, `BLOCK_LOCAL_PROTECTION` |
| **H** denominator / domain rules | `std(y_calibration, ddof=0)`; zero scale → `INVALID_FOR_NORMALIZED_SCORING`; ratio-denominator rule inherited |
| **I** interpretation flags | `UNCALIBRATED_SIGNAL`, C6/C7 absence, ECE ancestry, aliasing/upsample flags |
| **J** baseline configurations | B0, B1, B1A, B2, B3, H0 with per-file hashes |
| **K** selected alphas | B2 = 1, H0 = 1, plus the pre-value rule hash |
| **L** B3 configuration | sklearn 1.9.0, `random_state=2026090502`, all inherited defaults |
| **M** `S_pers` | `S_PERS_V1` definition, zero-denominator behaviour, not used for selection |
| **N** external cohort | 42 ids, 24 earlier / 18 later, partition policy — **metadata only** |
| **O** inference protocol | discharge unit, ≥10 000 gate bootstrap, V3 pass condition, V6 counts |
| **P** two-seed sensitivity | `DECLARED_OPTIONAL`, `NOT_EXECUTED`, no outcome trigger |
| **Q** global optimality claim | **false** |
| **R** external value reads | **0** |

## The ordering that makes V5 and V2 meaningful

```
1.  E0 -> E5 executed on development data only
2.  C_dev_star determined
3.  DEVELOPMENT_REPRESENTATION_LOCK written and hashed      <-- support fixed
4.  baseline penalty rule frozen and hashed (pre-value)     <-- rule fixed
5.  B2 / H0 alphas selected on development data
6.  all six baseline configurations frozen
7.  PRE_EXTERNAL_MODEL_FREEZE written and hashed
    ---------------------------------------------------------
8.  S7.10 may open the external cohort                       <-- NOT AUTHORISED
```

Step 3 precedes step 5, so baseline behaviour cannot have influenced which
support was selected. Step 7 precedes any external access, which is the
precondition V5 requires: without a hash that predates the first external read,
per-discharge local calibration would make the transfer claim vacuous.

## Reproducibility

Every substantive manifest entry was re-read and re-hashed after writing:
**13 entries, 0 mismatches**. The freeze file itself is excluded from its own
manifest under the established convention (a file cannot contain its own hash).

The selection is deterministic. The only randomness in the whole procedure is
the Rank-5 discharge bootstrap, seeded `2026090501`; its stream was verified
identical on reseed and its winner vector hashes to `918166f2…`.

## What S7.10 must do first

1. re-verify every hash in `PRE_EXTERNAL_MODEL_FREEZE.json`;
2. confirm the freeze timestamp precedes its first external access;
3. re-run the canonical-parse checksum before touching the support;
4. only then open the external cohort.

If S7.10 finds that persistence wins, that raw coordinates win, that the
nonlinear baseline wins, that one processing era fails, or that transfer fails
entirely — **that is the result**. The frozen object stands or falls as frozen.
Nothing here may be reopened to repair it.
