# S7.K2 — Gas-signal provenance resolution

```
GAS_SIGNAL_UNIT_RESOLVED_COMMAND_VOLTAGE
```

Machine-readable: `GAS_SIGNAL_PROVENANCE_CORRECTION.json`.

---

## What R1 found, and what K2 corrects

R1 recorded (`K-R1-02`) that `gasa`…`gasd` carried two conflicting unit records
and treated them as an unreconciled inconsistency between records of equal
standing.

**They are not of equal standing.** K2 traced the lineage and found the conflict
is a *supersession*, already resolved inside the frozen S7.1 branch.

| | record | unit | evidence | confidence |
|---|---|---|---|---|
| first pass | `S7.1 reconciliation/units_recovery.csv`; provider `SIGNAL_MANIFEST`; `units_sources.md` | `Torr*L/s`, `gas_flow` | `STRONGLY_INFERRED` external convention | **low**, dimensional signature **ambiguous**, magnitude test **NOT_TESTED** |
| **final pass** | **`S7/SIGNAL_UNITS.json`** → `SIGNAL_UNITS_AUDIT.csv`, `semantic_types_and_units.csv` | **`V`**, "Gas injection valve command, manifold A" | **`LOCAL_DOCUMENTED` (units registry)** | upstream unit string is literally **`"volt"`** |

The registry records, per signal:

```json
"gasa": { "units": "V", "status": "resolved_partial",
          "description": "Gas injection valve command, manifold A",
          "upstream_variants": { "volt": 51, "": 11 } }
```

| signal | upstream variants | status |
|---|---|---|
| `gasa` | `volt` × 51, empty × 11 | `resolved_partial` |
| `gasb` | `volt` × 51, empty × 11 | `resolved_partial` |
| `gasc` | `volt` × 51, empty × 11 | `resolved_partial` |
| `gasd` | **`volt` × 62** | `documented` |

The eleven non-reporting shots return an **empty** string — never a conflicting
unit. Units source: `smallELM_freq_v6_ZL_data/{shot}_metadata.json`, audited over
all 62 shots. (`resampled_data_v6` itself stores no units, which is exactly what
the first-pass search correctly reported.)

## Why this is decisive

This is the **same registry and the same evidence mechanism** that resolved
`pcdiamag3` → `{"upstream_variants": {"raw": 62}, "status": "uncalibrated"}` —
a resolution the entire downstream lineage accepted, and which I relied on
myself through S7.9 and S7.10 when carrying the `UNCALIBRATED_SIGNAL`
qualification. One cannot accept that resolution and reject this one.

## Consequences

- `gasa`…`gasd` are **gas injection valve command signals in volts** — actuator
  **commands**, not fueling rates.
- The frozen ontology (S7.3, S7.5H) is **correct**. The stale record is the
  **provider manifest**, which still carries the superseded first-pass
  hypothesis.
- The frozen coordinate dimension `PROD(gasa,gasa) → (V)*(V)` is **correct**.
  **R1's concern is withdrawn.**
- Numerical impact: **none, in either direction.** `CANON` contains neither `V`
  nor `Torr*L/s`, so the applied scale factor is exactly `1.0` under either
  label and every archived value used in Epoch 1 is unchanged.

## Physical reading carried into Epoch 2

A squared gas command, `PROD(gasa,gasa)`, is dimensionally **V²** and carries no
direct physical interpretation as a fueling quantity. This **strengthens** the
S7.11 and R1 reading of the Epoch-1 pathology: the coordinate that failed was a
squared actuator *command voltage*, not a squared physical flow.

## Discipline

`epoch1_files_edited = 0`. This is a **future-epoch superseding provenance
record**. No Epoch-1 artifact was corrected in place, and R1's ledger entry
stands as written with this correction recorded alongside it.

The resolution did **not** block K2, and could not have: the frozen range-support
metric is dimensionless and invariant under `c → k·c`, so it is independent of
the unit label either way.
