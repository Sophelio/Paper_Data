# S7.2 — External cohort firewall

## The rule

> **S7.3–S7.9 may know external shot IDs and frozen S7.1 metadata, but may not
> inspect external target values or use external outcomes for target selection,
> ontology design, candidate pruning, support selection, hyperparameter choice
> or threshold setting.**

The external cohort is **42 discharges**, listed in `COHORT_PARTITION.json` and
hashed in `manifests/COHORT_PARTITION_FREEZE.json`.

## Sealed until S7.10

| Stage | External signal values | External target values | External outcomes |
|---|---|---|---|
| S7.3 target feasibility | **SEALED** | **SEALED** | **SEALED** |
| S7.4 mathematical interpretation | **SEALED** | **SEALED** | **SEALED** |
| S7.5 ontology generation | **SEALED** | **SEALED** | **SEALED** |
| S7.6 admissible universe | **SEALED** | **SEALED** | **SEALED** |
| S7.7 search | **SEALED** | **SEALED** | **SEALED** |
| S7.8 utility rules | **SEALED** | **SEALED** | **SEALED** |
| S7.9 development freeze | **SEALED** | **SEALED** | **SEALED** |
| **S7.10 external validation** | open | calibration intervals only | open |

At S7.10, external **target** values remain restricted: calibration intervals
may be used to fit coefficients; protected intervals are used only for scoring.

## What may be known before S7.10

Permitted, because none of it is outcome information:

- external shot **identifiers**;
- their **period** and **processing era**;
- **temporal support** — window start, end, duration, sample counts;
- **availability and finite-fraction** metadata from S7.1;
- per-signal **resampling method and category**;
- **units and provenance** classifications.

All of this is frozen S7.1 metadata and was established before any target
existed. It is needed to construct the partition and to audit validation
feasibility, both of which were done in S7.2 without reading a single value.

## What may not be known before S7.10

- external **signal values**, of any signal;
- external **target values**;
- any **statistic** computed from external values — mean, variance, range,
  correlation, spectrum;
- any **model output** evaluated on external discharges;
- any **comparison** between external and development behaviour.

## Enforcement

1. **Code-level.** Analysis scripts in S7.3–S7.9 load the development shot list
   from `COHORT_PARTITION.json` and must not enumerate archive files directly.
2. **Audit.** Each stage records which discharges it read.
3. **Gate V2.** A stage that touched external values fails V2, and the study
   cannot present a structural transfer result.
4. **Freeze before crossing.** S7.9 hashes the support, estimator and all
   hyperparameters. S7.10 verifies those hashes before evaluating anything.

## If the firewall is breached

A breach is **not** silently correctable. The affected decision must be
re-derived from development data only, or the study must report that the
external cohort was compromised for that decision. There is no repair that
preserves the claim while keeping the contaminated choice.

## Why this matters more than usual here

The retired q_rec result failed for reasons that were only visible once
baselines were computed. If the external cohort had been consulted during
development, that failure would have been invisible — the model would have been
adjusted until it passed, and the adjustment would not have been recorded.

The firewall is what makes a **negative** external result meaningful, and this
contract explicitly prefers a clean negative to an arranged positive.
