# DIII-D source object

The observational object shared by **both** DIII-D branches: **62
discharges** and **95 quantities**, 5890 signal-discharge pairs.

Supports Supplement S7.1–S7.2 and every downstream claim.

| Subfolder | Contents |
|---|---|
| `observational_object_S7_1/` | cohort and signal inventories, provenance graph, units, temporal support, availability matrix, equilibrium lineage, quality summary, and the full S7.1 reconciliation history |
| `provenance/` | discharge ledger, preprocessing provenance, reconstruction validation audit |
| `units_and_availability/` | `SIGNAL_UNITS.json`, the frozen units registry |
| `retrieval_metadata/` | the data provider, transform realization, and per-shot resampling metadata |
| `source_access_notes/` | what is restricted, its hashes, and how to obtain it |

## Units

Units are read from `SIGNAL_UNITS.json` and are **never inferred from signal
names**. That registry is hashed into the S7.1 freeze as
`units_registry_sha256`.

## Restricted data

The 62 `.npz` archives are **not bundled**. Every one is listed with its SHA-256
in `source_access_notes/RESTRICTED_SOURCE_INDEX.csv`. See
`00_START_HERE/ACCESS_AND_LICENSE.md`.

## Ancestry

The information boundary that reduces 95 quantities to 78
admitted predictors is in `05_DIII_D_RECONSTRUCTION/01_Target_Selection...`.
15 EFIT-derived quantities are excluded **fail-closed** on unresolved
ancestry — the class that contaminated the retired branch.
