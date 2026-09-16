# Status of the full ontology, and of the already-built S7.6

Machine-readable: `G_REC_HARDENED.json`,
`manifests/PARENT_FREEZE_VERIFICATION.json`

---

## `G_REC_DENSITY_V1` — preserved

```
status : SUPERSEDED_FOR_PRIMARY_SEARCH
         PRESERVED_AS_EXTENDED_SENSITIVITY_ONTOLOGY
```

Not deleted, not rewritten, hash-verified unchanged against the S7.5 freeze.

Its full **78-primitive** universe and its five-family grammar remain
scientifically available for S7.11 sensitivity analysis. The 8 deferred channels
live there in full.

The distinction that makes this necessary:

```
REDUNDANCY_DEFERRED  !=  SCIENTIFICALLY_INADMISSIBLE
PRIMARY ONTOLOGY     !=  COMPLETE SCIENTIFIC ONTOLOGY
```

A channel was deferred because another retained channel carries the same
observational direction stably across development discharges — not because it
is uninformative, and certainly not because of anything to do with density.

## `G_REC_DENSITY_HARDENED_V2` — new primary

70 primitives · nine families C0–C8 · depth 1 · 23 861 symbolic coordinates.

Unchanged from the parent contract: target, canonical target unit, support-size
bound 1–12, shared-support semantics, discharge-specific coefficients, intercept
rule, target exclusion, provenance rules, external cohort of 42 sealed,
validation geometry, `T_REC_V1`, `FD2_PHYSICAL_TIME_V1`, and the
`DEP_NBI_POWER_SUM` exact-dependency constraint.

`pinj` and all eight per-beam components remain in `P_hard`; neither the
aggregate nor the component form is privileged, and exact dependency stays a
**representation-set-level** constraint for S7.6.

---

## A stage-sequence conflict, and how it was handled

The stage instruction asserted:

> "S7.6 HAS NOT STARTED."

**That is not the repository state.** `S7.6` was completed and frozen as
`D3D-SIR-S7.6-ADMISSIBLE-UNIVERSE-V1` (`FROZEN_READY_FOR_S7.7`, 40/40
acceptance, 6 034 atoms), built on the full 78-primitive `G_REC_DENSITY_V1`.

### Contamination analysis

The question that matters is whether S7.6 V1's existence could bias this stage.

| | |
|---|---|
| S7.6 V1 target values accessed | **0** |
| S7.6 V1 external values accessed | **0** |
| S7.6 V1 model fitted | no |
| S7.6 V1 predictor–target statistic computed | no |

S7.6 V1 read development **predictor** values only, to evaluate numerical
support and denominator conditioning. **No target-derived information exists
anywhere in the lineage**, so none can leak into S7.5H.

### Discretion analysis

The residual concern is subtler: could *knowing* S7.6 V1's outcome have shaped
S7.5H's choices?

Every S7.5H decision is fully specified by the stage instruction — the
thresholds (`0.99 / 0.97 / 0.95 / 54`), the C0–C8 catalogue, and the
deterministic representative rule. No discretion was available to exercise.

The single judgement call is **redundancy-group semantics**, decided strictly
from frozen metadata (same family, same quantity, same dimension, same origin
class, repeated-channel series) and independent of any S7.6 result. It produced
four eligible groups — ECE, CER rotation, CER ion temperature, filterscopes —
and four ineligible ones, each with a recorded reason.

Residual risk: `LOW_AND_RECORDED`.

### Resolution

```
PROCEED_AND_SUPERSEDE
S7.6 V1 -> SUPERSEDED_FOR_PRIMARY_SEARCH_PENDING_RERUN_ON_HARDENED_ONTOLOGY
```

S7.6 V1 is **preserved unmodified** as audit history, exactly as S7.3 V1 and
S7.4 V1 were before it. It must be **re-run** on
`G_REC_DENSITY_HARDENED_V2` before S7.7.

The stage's premise was wrong about the repository, but its *intent* was
unaffected: harden the ontology before the primary admissible universe is fixed.
Stopping outright would have blocked work whose reasoning is sound; proceeding
silently would have hidden a real inconsistency. The conflict is therefore
recorded prominently and flagged for human review.

**One acceptance item could not be asserted truthfully.** The instruction listed
`[ ] S7.6 not started`. It has started. That item is recorded as reconciled
rather than passed, and the freeze carries the qualification.

## What S7.6 must do on re-run

Nothing about its method changes. It will:

- instantiate the 23 861 symbolic coordinates of `Lambda_rec^H` over `P_hard`;
- apply the same admissibility classes B/A/C/G/F/D/E/H;
- apply the **same** frozen denominator rule (`eta ≥ 0.05`, RMS scale, no sign
  change, no regularisation) — already frozen and hashed at `6d4004eb…`, and
  **not** re-openable;
- extend the denominator gate to the three new partial maps C5, C7 and C8;
- rebuild the exact dependency groups over the new coordinate space.

One inherited result is worth carrying forward as an expectation rather than an
assumption: in S7.6 V1, **no C4 phase-derivative instance survived** the
denominator gate, because time derivatives change sign within every calibration
interval. C4 is unchanged here, and C7 and C8 also place a rate in a
denominator — so the same mechanism will bear on them. Whether they survive is
for S7.6 to determine, not for this stage to predict.
