# S7.1R-FINAL — Implementation provenance

Implementation-specific record, deliberately kept separate from
`S7_1_OBSERVATIONAL_OBJECT_AND_PROVENANCE_FINAL.md`, which is manuscript-facing
prose and does not name the backend.

## Environment

```
python      3.13.5
numpy       2.5.2
pandas      3.0.5
platform    Windows-11-10.0.26200-SP0
interpreter D:\SIR_paper\.venv_lorenz_benchmark\Scripts\python.exe
git         not a git repository (verified)
```

## Paths

| Role | Path |
|---|---|
| archive | `D:\SIR_paper\DIIID_example\data\resampled_data_v6` |
| reference provider / manifest | `D:\SIR_paper\DIIID_example\diiid_sir_data_provider.py` |
| units registry | `D:\SIR_paper\DIIID_example\S7\SIGNAL_UNITS.json` |
| full 95-signal provider | `D:\sir-web\providers\diiid_elm_data_provider.py` |
| canonical Paper 8-signal provider | `D:\sir-web\Paper Examples\Relational Coordinates for Multimodal Plasma Observations\diiid_elm_data_provider.py` |
| dFL export provider | `…\SIR_to_dFL_provider_on_ELM_shots_with_phaseders.py` |
| dFL export bundle | `D:\sir-web\FEATURE_EXPORTS\pcdiamag3_none_2026-07-13_03-08-23PM_CDT` |
| provenance ledger | `…\canonical_d3d_62_shot_provenance\D3D_CANONICAL_DATA_AND_PREPROCESSING_PROVENANCE.md` |
| architecture figure source | `D:\SIR_paper\General\sir_representational_prism.py` |
| **absent** — cited units source | `smallELM_freq_v6_ZL_data\{shot}_metadata.json` |
| **absent** — units generator | `build_signal_units.py` |

## Analysis backend

```
product              dalia
project              DIIID_SIR_Paper
project_id           36a4813a-23b1-4c9f-abc3-592f98b4abe2
provider version     164   (was 163 before this stage)
dataset_id           diiid_elm_sir_paper
data_folder          D:\SIR_paper\DIIID_example\data\resampled_data_v6
catalog              95 signals, 62 records
```

### Provider change applied at this stage

`data_provider.py` was rewritten from a 12-signal surface to the full 95-signal
manifest. Two independent restrictions were removed:

1. `all_possible_signals` previously listed 12 (the paper eight plus four
   filterscopes);
2. `_common_grid_fetch` carried a hard allow-list that raised `KeyError` for any
   signal outside the paper eight, so the SIR path was locked to 8 even for
   signals that were graphable.

`PAPER_EIGHT` is retained in its original order, which carries relational-term
direction in the manuscript. `SIR_DEFAULT_SIGNALS` now defaults to all 95.

### Backend calls used for verification

```
list_projects
read_provider_file  (project_id, "data_provider.py")
save_provider_file  (project_id, "data_provider.py", <full 95-signal manifest>)
check_syntax        (project_id)                      -> ok, 0 errors
reload_provider     (project_id)                      -> "Loaded provider dataset_id=diiid_elm_sir_paper"
get_catalog         (project_id)                      -> 95 signals, 62 records
get_project         (project_id)                      -> v164, layout intact
fetch_signal_stats  (project_id, "195659", [ip, pcdiamag3, q95, betan,
                                            prmtan_neped, gasa, cerqrott3, cerqtit13])
fetch_signal_stats  (project_id, "155537", [ece40, cerqtit13, prmtan_neped, q95])
```

Both `fetch_signal_stats` calls returned `errored_signals: []`.

### Parity caveat

The stats RPC caps `count` at 20000 samples, so `mean` and `std` are computed on
a capped subset for longer signals. `length`, `min` and `max` are exact and are
what the comparison used.

## Reference loader calls

```python
import diiid_sir_data_provider as P
P.fetch_record_ids()                       # 62 ids
P.fetch_native(shot, signals)              # native per-signal axes
P.fetch_common_grid(shot, signals)         # 1000-point common grid
P.describe(signal)                         # manifest entry
P.verify_against_archive()                 # manifest vs every archive on disk
```

`python diiid_sir_data_provider.py` re-verifies the manifest against all 62
archives and prints the group breakdown.

## Scripts run, in order

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$R = "S7\01_observational_object\reconciliation_final"

& $P $R\s7_1r_final_units.py     # ECE keV correction, hashes, units audit
& $P $R\s7_1r_final_census.py    # census, inventory, semantic types, quality
& $P $R\s7_1r_final_freeze.py    # parity, provenance, lineage, temporal, freeze
```

Deterministic; no seeds. `s7_1r_final_units.py` is **not** idempotent by design —
it refuses to run twice against changed content and preserves a pre-change
snapshot at `SIGNAL_UNITS.pre_S7_1R.json`.

## Hashes

| File | sha256 |
|---|---|
| `SIGNAL_UNITS.json` (pre) | `bbebdc234b35eccb9682b7a38dc26137c721fe960642972d40c34a14a1d6d4f6` |
| `SIGNAL_UNITS.json` (post) | `b8b3cead0d1d23d8fc42a54824421472847c0744fb293b6fd2196ac93e598e72` |

Remaining artifact hashes are in `S7_1_FINAL_FREEZE.json` and tabulated in
`O_DIIID_FINAL.md`.

## Artifacts modified outside `reconciliation_final/`

| File | Change |
|---|---|
| `S7\SIGNAL_UNITS.json` | 40 ECE entries assigned `keV`; 55 non-ECE entries byte-identical (verified) |
| `S7\STATUS.md` | stage status updated |
| `S7\README.md` | stage status updated |
| dalia `data_provider.py` | v163 → v164, 12 → 95 signals |
| `DIIID_example\diiid_sir_data_provider.py` | created — reference provider and frozen manifest |

The original S7.1 artifacts in `01_observational_object/` and the interim S7.1R
artifacts in `reconciliation/` were **not modified at this stage**. The
correction blocks appended to them during the earlier interim pass remain as
they were.
