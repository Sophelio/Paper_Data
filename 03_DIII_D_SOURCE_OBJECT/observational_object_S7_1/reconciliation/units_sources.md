# S7.1R — Sources consulted for unit recovery

Search order was local-first. An external convention was admitted only after
the local search for a given signal was exhausted.

## 1. Local sources searched

| # | Source | Result |
|---|---|---|
| 1 | `data/resampled_data_v6/shot_*_resampled.npz` — 190 array keys per shot | **No units.** Keys are exactly `<signal>_data` / `<signal>_times`; no attribute, no sidecar array, no `__unit__` key. |
| 2 | `data/resampled_data_v6/shot_*_metadata.json` — 62 files | **No units.** Per-signal fields are exactly `method`, `category`, `original_length`, `resampled_length`. |
| 3 | `sir-web/providers/diiid_elm_data_provider.py` (full 95-signal provider) | **No units.** No `unit`, `units`, `Units` token anywhere in the file. |
| 4 | `Paper Examples/.../SIR_to_dFL_provider_on_ELM_shots_with_phaseders.py` | **Blank units, explicitly.** `_units_for()` returns `{"data": "", "times": TIME_UNITS}` with the comment *"SIR export columns are already processed (e.g. z-scored); keep data units blank while labeling the shared time axis in milliseconds."* |
| 5 | `D3D_CANONICAL_DATA_AND_PREPROCESSING_PROVENANCE.md` (449 lines) | **No units table.** Documents cohort, alignment, normalisation, realizations; units are not among them. |
| 6 | `build_d3d_discharge_ledger.py` + discharge ledger CSV | **No units column.** |
| 7 | `Figure_data/*` summary exports | **No units.** |
| 8 | Project `README`s, `MODEL_CONSTRUCTION.md`, validation audits | **No units.** |
| 9 | Local MDSplus / OMFIT metadata | **Not present.** No MDSplus tree, tag dictionary, or OMFIT module exists in any local tree. |

**Result: zero of 95 signals has a locally recorded unit.** This is not an
oversight in the search; the one function in the project whose job is to report
units returns the empty string by design, because the exported columns are
z-scored and the author deliberately declined to claim a unit for them.

## 2. External conventions used

Where the local search returned nothing, the signal's unit was assigned from
the standard DIII-D pointname convention for that tag. These are conventions of
the device and its diagnostics, not artifacts of this project, and are recorded
as `AUTHORITATIVE_EXTERNAL` or, once magnitude-tested, `STRONGLY_INFERRED`.

| Tag family | Convention applied |
|---|---|
| `ip`, `pcbcoil` | plasma / coil current in amperes |
| `bt` | toroidal field in tesla |
| `vsurf` | surface loop voltage in volts |
| `betan` | normalised beta, `%·m·T/MA` |
| `q95`, `li`, `kappa`, `tritop`, `tribot` | dimensionless equilibrium scalars |
| `aminor`, `rmaxis`, `zmaxis`, `rsurf`, `zsurf`, `zcur`, `drsep` | metres |
| `area`, `volume` | m², m³ |
| `density` | line-averaged density, cm⁻³ |
| `prmtan_neped`, `prmtan_teped` | pedestal fit outputs, density and temperature |
| `ece1…ece40` | ECE radiometer electron temperature |
| `cerqtit*`, `cerqrott*` | CER ion temperature and toroidal rotation |
| `pinj`, `pinj_*`, `tinj` | injected beam power and torque |
| `gasa…gasd` | gas injection flow |
| `fs*` | filterscope photodiode, conventionally uncalibrated |

## 3. The magnitude test

Every unit hypothesis carrying a physically-bounded expectation was tested
against the observed median `|value|` pooled over all 62 discharges. The test's
purpose is to **falsify**, not to fit:

- `CONSISTENT` — observed magnitude lies in the expected band. Corroboration
  only; the hypothesis is *not* promoted past `STRONGLY_INFERRED`.
- `REFUTED` — observed magnitude lies outside the band. The unit is
  **withdrawn** to `UNRESOLVED`. No rescaled alternative is substituted;
  inventing a factor to make the number fit would be fabrication.
- `OUTLIER_IN_COHERENT_GROUP` — the channel fails, but ≥80% of its tag family
  passes. A unit is a property of the group's storage convention, so this is
  recorded as a **value anomaly**, not a unit failure.
- `NOT_TESTED_INACTIVE` — the channel is identically zero across the cohort and
  therefore carries no information about its own unit.
- `NOT_TESTED` — no physically bounded expectation exists (dimensionless
  scalars, uncalibrated photodiodes).

Bands are in `MAGNITUDE_BANDS` / `PREFIX_BANDS` in `build_s7_1r.py` and are set
from ordinary DIII-D H-mode operating ranges, deliberately wide.

## 4. What the test changed

Two hypotheses did not survive contact with the data, and one was corrected by
an internal consistency check rather than by convention:

1. **`pinj_*` is stored in W, not kW.** The eight per-beam channels each read
   ~1.4–2.2 × 10⁶ while the aggregate `pinj` reads ~9.25 × 10³. Under a common
   unit the parts would exceed the sum by a factor of ~1000. Applying W to the
   parts and kW to the aggregate makes them add: Σ per-beam ≈ 10.5 MW against an
   aggregate of 9.25 MW. The correction rests on **additivity within the
   project's own data**, which is stronger evidence than either convention alone.

2. **`pcdiamag3` is not stored in joules.** Diamagnetic stored energy on DIII-D
   is O(10⁵–10⁶) J. The observed median is 9.69, with range −28 to +33. The
   joule hypothesis is refuted by four to five orders of magnitude. The signal
   is left `UNRESOLVED`.

3. **`tinj` is a torque (N·m), not an angular impulse (N·m·s).** Observed median
   5.9 matches injected torque directly.

## 5. Unit systems are not consistent within the object

Three same-quantity pairs are stored in different unit systems. Any downstream
dimensional typing that assumes one unit per physical quantity will be wrong:

| Physical quantity | Signals | Stored as |
|---|---|---|
| Number density | `density` vs `prmtan_neped` | cm⁻³ vs m⁻³ (10⁶ apart) |
| Temperature | `ece*` vs `cerqtit*`, `prmtan_teped` | keV vs eV (10³ apart) |
| Power | `pinj` vs `pinj_*` | kW vs W (10³ apart) |

This is the single most actionable result of the unit pass. It is invisible
under within-discharge z-scoring — which is exactly why it survived undetected
through the earlier analyses.
