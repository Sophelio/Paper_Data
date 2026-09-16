# S7.1 implementation provenance (internal — not manuscript-facing)

This file records backend and code detail deliberately excluded from
`S7_1_OBSERVATIONAL_OBJECT_AND_PROVENANCE.md`, which stays implementation-agnostic.

## Operation classification

| Operation | Classification | Detail |
|---|---|---|
| Signal inventory (95 quantities) | `DIRECT_FILE_INSPECTION` | enumerated from `<name>_data` keys in the 62 npz archives |
| Signal grouping / category | `AUDITED_EXTERNAL_METADATA` | transcribed verbatim from the docstring of `D:\sir-web\providers\diiid_elm_data_provider.py` |
| Cohort list (62 ids) | `AUDITED_EXTERNAL_METADATA` | `ADMISSIBLE_SHOTS` in `SIR_to_dFL_provider_on_ELM_shots_with_phaseders.py`; corroborated by the discharge ledger |
| Preprocessing chain | `AUDITED_EXTERNAL_METADATA` + code read | provider `_load_signal` / `fetch_data`; provenance doc §5 |
| Standardisation semantics | `AUDITED_EXTERNAL_METADATA` | provenance doc §7, pointing at `Archaieus/sir/consumer_function.py::standard_transformations` |
| Numerical realizations | `AUDITED_EXTERNAL_METADATA` | provenance doc §8 (none / spline k=5 s=0.1 / RTS R=1 Q=1e-4) |
| Availability, quality, temporal census | `DIRECT_FILE_INSPECTION` | computed here from the archives |
| Units | `UNRESOLVED` | absent from every artifact |
| Upstream resampling pipeline | `UNRESOLVED` | not present in any local tree |

## Dalia backend

The Dalia project `DIIID_SIR_Paper` (`36a4813a-23b1-4c9f-abc3-592f98b4abe2`)
serves this dataset and hosts the audited transform family. It was **not** used
as the census source, for a specific reason:

* its embedded `data_provider.py` exposes `ALLOWED_SIGNALS` = the **eight**
  historical quantities only;
* the object actually possessed contains **95**.

Using Dalia as the inventory source would therefore have silently reproduced the
historical eight-signal reduction and defeated the purpose of S7.1. Dalia access
is classified `DALIA_NATIVE` but **covers 8/95 of the object**, and is recorded
here as an availability class rather than used as ground truth.

Availability classes assigned:

* `AVAILABLE_IN_FROZEN_STUDY_OBJECT` — all 95, from the archives.
* `AVAILABLE_THROUGH_EXISTING_BACKEND` — the 8 in `ALLOWED_SIGNALS`.
* `REFERENCED_BUT_NOT_LOCALLY_RESOLVED` — the upstream resampling pipeline; the
  equilibrium reconstruction; the macOS dataset path in the full provider.

## Environment

Recorded in `_manifests/INITIAL_STATE_MANIFEST.json`: Python and platform
strings, numpy/pandas versions, per-file SHA-256 for 9 canonical artifacts and
all 62 shot archives, with UTC modification times. S7.1 is fully deterministic;
no stochastic procedure is used, so no seeds are required.

The sir-web HEAD commit `bc123d63b5e49d9c160808fdc97ba0442ce4bdd0` is carried
forward from the canonical provenance document and was **not** re-verified in
this run.

## Scripts

    01_observational_object/build_s7_1_census.py   census, DAG, quality, temporal
    01_observational_object/finalize_s7_1.py       artifacts, O, consistency
