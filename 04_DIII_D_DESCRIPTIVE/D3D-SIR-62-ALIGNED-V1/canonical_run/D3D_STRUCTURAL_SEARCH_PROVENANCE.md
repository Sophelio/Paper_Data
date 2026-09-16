# D3D Structural-Search Provenance — D3D-SIR-62-ALIGNED-V1

## Verdict labels

| Topic | Status |
|-------|--------|
| Historical `.psir` with 62 realizations and `1_8*` | **RESOLVED** (`RESULTS/output.pcdiamag3.psir`) |
| Seven-term support identity | **RESOLVED** (matches `D3D_RELATION` / mean of `1_8*`) |
| Per-realization calibration (`1_8` → `1_8*`) | **RESOLVED** (both keys present; `1_8*` matches OLS RMSE) |
| Term index list `bestindex` | **PARTIALLY RESOLVED** (`[[[0], [56], [105], [41], [57], [98], [106], [96]]]` — library indices, full name map not dumped here) |
| Full admitted coordinate-family checklist at discovery | **UNKNOWN** |
| Candidate library size at discovery | **UNKNOWN** (export has 65 feature columns; search-time checklist not frozen) |
| Forward-selection hyperparameters (iterations, jobs, seeds) | **UNKNOWN** for the discovery run |
| Current `.bin/settings.json` | **NOT** treated as discovery config (incomplete `data_processing` vs export richness; target_variable null) |
| Support selection pooled vs per-realization | **PARTIALLY RESOLVED**: greedy indices stored once (`bestindex`); coefficients vary per realization; calibration produces `1_8*` |
| Whether support was later hard-coded into `D3D_RELATION` | **RESOLVED** as present state: `D3D_RELATION` embeds mean coefficients; interactive validation uses model coeffs |

## RESOLVED

- Cohort: 62 shots; 1000 samples each.
- Target: `[d[pcdiamag3]/d[t]]` (`outexpr` in `.psir`).
- Equation keys: `1_8`, `1_8*` with coefficient shape `(62, 8)`.
- FinalError on `1_8`: ≈0.00332005; calibrated `1_8*` pooled MSE ≈0.00331599.
- Provider admitted ontology (eight signals) and `ALLOWED_SIGNALS` order affecting relational orientation.
- Smoothing for canonical export: `none` (manifest).

## PARTIALLY RESOLVED

- `bestindex` library positions for the eight selected slots (intercept + 7 terms).
- Mean coefficients ≈ `D3D_RELATION` scientific embedding.

## UNKNOWN

- Exact UI `data_processing` checklist, `order`, `numerators`, `iterations`, `jobs`, `nmin`, seeds at the moment of structural discovery.
- Number of random starts / parallel pool settings for that run.
- Exact `shiftval` / `nmin` numeric values per realization during export generation.

## CONTRADICTORY

- None proven between historical `.psir` `1_8*` predictions and per-discharge OLS on the frozen export (coeffs match ≤1e-6; RMSE identical to reference).

## REGENERATION_CONFIGURATION_NOT_ORIGINAL_DISCOVERY_CONFIGURATION

If rediscovering without the `.psir`, the frozen reconstruction is:

- Features: seven columns in psir order from the canonical export.
- Fit: `numpy.linalg.lstsq` per discharge with intercept.
- This **reproduces** discharge-specific predictions/RMSE but **does not** re-run structural search.
