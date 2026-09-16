# DIII-D Discharge Reconstruction Validation — Code-Path Audit

**Date:** 2026-08-04  
**Scope:** Trace and independently reproduce the pooled RMSE reported by the sir-web custom graph “Discharge Reconstruction Validation” registered in `diiid_elm_data_provider.py`, and explain the numerical gap versus the earlier provenance value ≈0.4125.  
**Constraint:** Evidence from code and local artifacts only. No analysis/manuscript files were modified. Differences are stated only where inputs or code paths differ by direct inspection.

---

## 1. Executive finding

There are **two front-ends** that share the same metric/render core (`dash_app/utils/discharge_validation.py`) but **differ in how \(y_{\mathrm{pred}}\) is obtained**:

| Front-end | Entry | \(y_{\mathrm{pred}}\) source | Reproduced pooled RMSE |
|-----------|--------|-----------------------------|-------------------------|
| **Interactive sir-web graph** | `get_discharge_reconstruction_validation` in `diiid_elm_data_provider.py` | Live model via `backend.output_plot_modelVdata` → **per-realization** coefficients from the `.psir` / model output (`OUTPUT_PLOTTER.y_hat`) | **≈ 0.05758** (near 0.058) when the same 7-term support is fit per discharge on the canonical export features |
| **Publication / prior provenance Panel C** | `analysis/plot_d3d_discharge_validation.py` | Hard-coded **mean** coefficients `D3D_RELATION` applied to every shot’s feature columns | **0.4125238315775986** (artifact text: `0.4125`) |

The earlier provenance document reported **0.4125** because it audited the **export + `D3D_RELATION`** path (`figures/d3d_discharge_validation_summary.txt`). That is **not** the prediction source used by the interactive provider graph.

Independent reproduction on the canonical 62-shot feature export:

- Mean-coefficient reconstruction (`D3D_RELATION`): **pooled RMSE = 0.4125238315775986**
- Per-discharge OLS on the same seven terms + intercept: **pooled RMSE = 0.05758467247445343**
- \(\sqrt{3.31599\times 10^{-3}}\) from a recent calibrated fixed-equation SIR log line matches the per-shot OLS RMSE to floating precision (**0.05758463336689746**)

No manuscript TeX stating “0.058” was found in this repository; the ≈0.058 figure is confirmed as the pooled RMSE of **per-realization** reconstructions of the audited seven-term support on the paper feature export, which is the same *class* of prediction the interactive graph builds from `modelVdata`.

---

## 2. Code path — interactive graph (provider)

### 2.1 Registration

**File:** `Paper Examples/Relational Coordinates for Multimodal Plasma Observations/diiid_elm_data_provider.py`

| Item | Location |
|------|----------|
| Custom grapher id | `"Per-discharge_normalized_RMSE"` (L372–382) |
| Display name | `"Discharge Reconstruction Validation"` (L373) |
| Requires | `["backend", "model"]` (L374) |
| Function | `get_discharge_reconstruction_validation` (L274–339, wired L381) |

### 2.2 Call chain (exact)

```
get_discharge_reconstruction_validation(app_control_parameters, parameters)
  backend.all_equations(model)                          # choose equation key
  backend.get_variables(k, model)                       # richness for default key
  backend.output_plot_modelVdata(model, equation_key, number_samples=None)
    → OUTPUT_PLOTTER(model.output_path).plot_modelVdata(..., plot=False)
       → y_hat: per-realization ŷ = C_i @ X_i           # visualization.py L247–260, L268–273
  filenames = model.output_dict.get("filenames")        # optional shot ids
  build_records_from_modelVdata(vdata, filenames)       # discharge_validation.py L387–409
  prepare_discharge_reconstruction_data(records)        # L144–195
  compute_discharge_metrics(records)                    # L210–234
  compute_pooled_metrics(records, per_discharge)        # L237–277
  select_median_error_discharge(per_discharge)          # L282–302
  make_interactive_discharge_validation_figure(...)     # L623–787
```

**Equation selection (provider L309–317):**

- If UI parameter `Per-discharge_normalized_RMSE_equation` is a non-empty key present in `equations`, use it.
- Else default: `max(equations, key=lambda k: (len(backend.get_variables(k, model)), k))` — richest equation (most terms; last key on ties).

**Prediction math in Archaieus** (`submodules/Archaieus/src/Archaieus/sir/visualization.py`):

```text
coeff[i]  = output_dict[equation_key]['x'][i]     # coefficients for realization i
X[i]      = output_dict[f'O{order}_variables'][i]
y_hat[i]  = coeff[i] @ X[i][:n_coef]
y_obs[i]  = output_dict['output']['x'][i]
time[i]   = output_dict['timing'][i]
```

This is **not** `reconstruct_prediction(..., D3D_RELATION)`.

### 2.3 Shared metric definitions

**File:** `dash_app/utils/discharge_validation.py`

Residual:

\[
e = y_{\mathrm{obs}} - y_{\mathrm{pred}}
\]

Per-discharge RMSE (L222–227):

\[
\mathrm{RMSE}_d = \sqrt{\mathrm{mean}_t(e_{d,t}^2)}
\]

Pooled RMSE (L250–266) — over **all** retained observations, not the mean of per-discharge RMSEs:

\[
\mathrm{RMSE}_{\mathrm{pooled}} = \sqrt{\mathrm{mean}_{d,t}(e_{d,t}^2)}
\]

Also computed: pooled MAE, residual mean/std, pooled \(R^2\), and Q1/median/Q3 of the **per-discharge RMSE** distribution.

**Display:** Plotly annotation `Pooled RMSE = {_fmt(...)}` with `_fmt` → 3 decimal places (L532–535, L686–687). A true value 0.05758 would display as **`0.058`**.

**Weighting / masks / exclusions** (`prepare_discharge_reconstruction_data`, L144–195):

- Row kept iff `time`, `y_obs`, `y_pred` (and any attached feature columns of matching length) are finite.
- Discharges with zero retained rows are dropped.
- **No sample weights**; equal weight per retained time sample.
- On the canonical export reproduction: 62000 loaded, 62000 retained, 0 excluded, 62/62 discharges.

---

## 3. Code path — publication export (source of 0.4125)

**File:** `analysis/plot_d3d_discharge_validation.py`

| Item | Value |
|------|--------|
| Default input | `FEATURE_EXPORTS/pcdiamag3_none_2026-07-17_05-21-18PM_CDT_raw_final_paper_normalized` (L55–58) |
| Records | `build_records_from_export_dir` (L437–526 in `discharge_validation.py`) |
| If no prediction column | `reconstruct_prediction(df, D3D_RELATION)` (L412–434) |
| Metrics / figure | Same `prepare_*` / `compute_*` / `make_publication_*` as interactive |

**Artifact already on disk:**

- `figures/d3d_discharge_validation_summary.txt` — `pooled RMSE : 0.4125`, 62 files, 62000 rows, `predictions: reconstructed`
- SHA-256: `63466d679d50d3bda410a01130fbd97c7938091af0a3adf1120662dce67bd34a`

---

## 4. Exact 62-shot inputs / export

### 4.1 Upstream NPZ cohort

| Item | Evidence |
|------|----------|
| Directory | `D:\DIII-D ELM data set\resampled_data_v6` (`DEFAULT_DATASET_URL`, provider L41–42) |
| Pattern | `shot_*_resampled.npz` (L44, L357–360) |
| Ledger | `canonical_d3d_62_shot_provenance/d3d_discharge_ledger.csv` (62 rows) |
| Ledger SHA-256 | `4e7d6275abdd0b23423f5862ad9f092de235509a3ee9a7572f0fd608b6f6d67e` |

Provider discovery returns **all** matching NPZ files under `dataset_url` (sorted). Canonical membership of the paper cohort is the 62 shots in the ledger / `ADMISSIBLE_SHOTS` (see prior provenance doc); the interactive graph uses whatever realizations the completed SIR run ingested.

### 4.2 Feature export used for numerical reproduction

| Item | Value |
|------|--------|
| Path | `FEATURE_EXPORTS/pcdiamag3_none_2026-07-17_05-21-18PM_CDT_raw_final_paper_normalized/` |
| Files | 62 × `shot_*_resampled__model.parquet` |
| Manifest SHA-256 | `c70dac99847cc63b87f4de0362dca8bbcfd05049b17c331112fd687353c217c0` |
| Sample parquet (shot 155537) SHA-256 | `a78317e5e6a9cb39e310917cf03fbeba3ffcb2a395ee4b36b055e8f6f98b9c51` |
| Manifest fields | `normalization: "zscore"`, `smoothing_method: "none"`, `n_features: 65`, target `pcdiamag3` |
| Rows per file | 1000 (first file checked); 62×1000 = 62000 |

---

## 5. Target and reconstructed quantities

| Quantity | Identifier | Notes |
|----------|------------|--------|
| Target (obs) | `[d[pcdiamag3]/d[t]]` | `D3D_RELATION["target_term"]` (L53); manuscript symbol `dW_dia/dt` (L67–68) |
| Axis label | “Normalized RMSE” / inset “normalized dW_dia/dt” | RMSE on **already z-scored** target columns — not a second normalization of the RMSE itself |
| Reconstruction (export path) | Linear combination of seven feature columns + intercept | `reconstruct_prediction` |
| Reconstruction (interactive path) | Model `y_hat` from per-realization coeffs × design matrix | `OUTPUT_PLOTTER.y_hat` |

First export file target stats (audit script): mean `0.0`, std (ddof=0) `1.0` → per-discharge z-scored target.

---

## 6. Selected seven terms and coefficient source

Hard-coded in `dash_app/utils/discharge_validation.py` L52–64 (`D3D_RELATION`):

```text
intercept = -5.773e-19
+2.480e-01  [d[pcdiamag3]/d[kappa]]
+8.928e-01  [d[kappa]/d[t]]
-1.062e-02  [r[q95]/r[kappa]]
+1.075e+00  [d[pcdiamag3]/d[betan]]
-1.070e+00  [d[kappa]/d[betan]]
+5.091e-02  [d[betan]/d[t]]
-1.500e-02  [d[li]/d[betan]]
```

**Role of `D3D_RELATION`:**

- Used **only** when building records from a feature-export directory that has **no** prediction column (`build_records_from_export_dir` / `reconstruct_prediction`).
- **Not** read by `get_discharge_reconstruction_validation` (interactive path).

Mean of per-discharge OLS coefficients on the export (audit script) matches `D3D_RELATION` to printed precision — consistent with `D3D_RELATION` being the **cohort-mean** coefficient vector, not the per-shot vectors used in `modelVdata`.

Provider comment on variable order (`ALLOWED_SIGNALS` L49–58) documents that canonical order fixes relational term **orientation** (e.g. `[r[q95]/r[kappa]]`, `[d[kappa]/d[betan]]`).

---

## 7. Preprocessing and normalization actually applied

### 7.1 Provider (`diiid_elm_data_provider.py`)

| Step | Implementation | Lines |
|------|----------------|-------|
| Allowed signals | `pcdiamag3, pinj, density, ip, q95, li, kappa, betan` | L59–68 |
| Load / clean | finite, time-sort, drop duplicate timestamps | `_load_signal` L75–102 |
| Common window | intersection of requested signals’ time ranges | `_common_grid_fetch` L181–187 |
| Grid | `np.linspace(t0, t1, TARGET_N=1000)` | L47, L189 |
| Resample | block-average if denser than grid; else linear interp | `_resample_to_grid` L155–162 |
| Smoothing request | `SMOOTH_RATE = 0.0` | L72, L349 |
| `freq` / `dt` | `float(grid[1]-grid[0])` in **milliseconds** (docstring L13, L421) | L190–194, L348 |

### 7.2 Archaieus consumer (downstream of provider)

**File:** `submodules/Archaieus/src/Archaieus/sir/consumer_function.py`

| Step | Behavior | Lines |
|------|----------|-------|
| Level-0 z-score | Per-realization `zscore` on signals (when enabled) | ~L294–330 |
| `dt` for FD | `timing_data[0,1]-timing_data[0,0]` else `freq` — **as provided (ms)** | L345–348 |
| Derivatives | `TRANSFORMS.differentiate(..., dt=dt)` when no smoother | L376–398 |
| XPhaseders / xi/xj | `make_Quotients(..., add_inverse=True)` | L400–406 |
| YPhaseders | Target-in-numerator only | L416–420 |
| Optional total_normalization | Additional z-score of derived features | L428+ |

Canonical export manifest: `smoothing_method: "none"`, `normalization: "zscore"`.

---

## 8. Time-grid units and ms vs s

| Fact | Evidence |
|------|----------|
| Provider times | Documented as **ms**; figure inset label `Time (ms)` (`discharge_validation.py` L638, L813) |
| Provider `freq` | Spacing of ms grid (e.g. first shot ≈ 4.764 ms) |
| FD uses that `dt` directly | `consumer_function.py` L345–348, L377+ |
| Phase / relational coords | Ratios of derivatives → **global unit rescaling of time cancels** in \(D_g f\) |
| Absolute \(\mathrm{d}/\mathrm{d}t\) features | Scale with \(1/\mathrm{dt}\); subsequent **per-feature z-score** (export / `total_normalization`) removes a global unit factor from standardized columns |

**Audit check on export:** first file `times` range ≈ `[105.32, 4865.0]` with median \(\Delta t \approx 4.764\) ms — consistent with provider ms grid, not a fixed 0.020 s grid.

**Effect on pooled RMSE of standardized target:** a uniform ms↔s mistake would rescale absolute derivative columns before z-scoring; after per-column z-score, the standardized-target RMSE computed from those columns is invariant to that global factor. Therefore **ms vs s does not explain the 0.4125 vs 0.058 gap** on this metric definition.

---

## 9. Exact numerical reproduction

### 9.1 Commands

```bash
conda activate sir_web
cd D:\sir-web

# Official export path (mean D3D_RELATION) — matches figures summary
python analysis/plot_d3d_discharge_validation.py \
  --input-dir "FEATURE_EXPORTS/pcdiamag3_none_2026-07-17_05-21-18PM_CDT_raw_final_paper_normalized"

# Audit script: mean-coef vs per-discharge OLS on same features
python "Paper Examples/Relational Coordinates for Multimodal Plasma Observations/canonical_d3d_62_shot_provenance/_audit_discharge_rmse.py"
```

### 9.2 Reproduced values (2026-08-04, this host)

| Metric | Mean `D3D_RELATION` (export path) | Per-discharge OLS (same 7 terms) |
|--------|-----------------------------------|----------------------------------|
| Pooled RMSE | **0.4125238315775986** | **0.05758467247445343** |
| Pooled MAE | 0.2868222766081056 | 0.03116503381195452 |
| Median per-discharge RMSE | 0.3784671322678298 | 0.050090976186570546 |
| Selected median-error shot | 195650 (RMSE 0.378163…) | 165031 (RMSE 0.049676…) |
| \(n_{\mathrm{obs}}\) | 62000 | 62000 |
| \(n_{\mathrm{discharges}}\) | 62 | 62 |

Display rounding: `_fmt(0.05758467)` → **`0.058`**; `_fmt(0.41252383, d=4)` in summary → **`0.4125`**.

Machine-readable dump: `_audit_discharge_rmse_results.json` (same folder).

### 9.3 Decisive input hashes

| Artifact | SHA-256 |
|----------|---------|
| `dash_app/utils/discharge_validation.py` | `8153f0217ceb039e4d6fda1052a576669bb5217d3c56166420444f664dc3cc0a` |
| `diiid_elm_data_provider.py` | `afc42723426bde480fa1fc0746fa6e85d653fe3d8fcf7c28564cb7a066dad5ff` |
| `figures/d3d_discharge_validation_summary.txt` | `63466d679d50d3bda410a01130fbd97c7938091af0a3adf1120662dce67bd34a` |
| `figures/d3d_discharge_validation_metrics.csv` | `0166636dbd02d85957cb0745af1292a7e83f0f19a3d0f7feec4ae8cce0f3028a` |
| Export `manifest.json` | `c70dac99847cc63b87f4de0362dca8bbcfd05049b17c331112fd687353c217c0` |
| `shot_155537_resampled__model.parquet` | `a78317e5e6a9cb39e310917cf03fbeba3ffcb2a395ee4b36b055e8f6f98b9c51` |
| `d3d_discharge_ledger.csv` | `4e7d6275abdd0b23423f5862ad9f092de235509a3ee9a7572f0fd608b6f6d67e` |

---

## 10. Why earlier provenance got ≈0.4125 (exact difference)

| Dimension | Prior provenance / `figures/*_summary.txt` | Interactive provider graph / ≈0.058 class |
|-----------|--------------------------------------------|---------------------------------------------|
| Record builder | `build_records_from_export_dir` | `build_records_from_modelVdata` |
| \(y_{\mathrm{pred}}\) | `reconstruct_prediction` with **one** coefficient vector (`D3D_RELATION`) for all 62 shots | `OUTPUT_PLOTTER.y_hat`: **per-realization** coefficient rows |
| Metric definition | Identical (`compute_pooled_metrics`) | Identical |
| Feature table | Same paper export when comparing OLS vs mean-coef on disk | Live run’s design matrix inside `.psir` (same ontology when run matches export settings) |
| Normalization / masks | Same export columns; 0 exclusions | Same finite-row mask logic |
| Time units | Not the cause of the gap (see §8) | Same |

**Direct evidence of the gap on identical features:** applying mean `D3D_RELATION` vs refitting the same seven columns per shot changes pooled RMSE from **0.4125 → 0.05758** with no other changes to metric code, masks, or time grids.

---

## 11. Remaining ambiguities (not resolved without further artifacts)

1. **Manuscript prose / TeX** stating “≈0.058” is **not present** in this repo; confirmation is numerical/code-path only.
2. **Live GUI value** depends on the completed SIR run’s `.psir` (equation key, term support, calibration). This audit did not reload a fresh interactive run’s model file from `.tmp/` (none listed at audit time). The ≈0.058 value is reproduced from (a) per-discharge OLS on the canonical export’s seven-term support and (b) consistency with a recent calibration log MSE.
3. If the interactive run’s richest equation is `1_8*` (calibrated) vs `1_8`, coefficients differ slightly; both remain per-realization fits, not mean `D3D_RELATION`.
4. Provider `fetch_identifiers_from_url` returns **all** NPZ under the folder; ensuring the run uses exactly the 62 ledger shots depends on the dataset directory contents / sample limit at run time.
5. Ledger column `grid_dt_seconds` stores values numerically equal to **seconds** converted from ms spacing (e.g. 0.00476 s ≡ 4.76 ms); provider code itself returns **ms** spacing as `freq`. Naming inconsistency only — does not alter the RMSE gap analysis above.

---

## 12. File index for this audit package

| Path | Role |
|------|------|
| `D3D_DISCHARGE_RECONSTRUCTION_VALIDATION_AUDIT.md` | This document |
| `_audit_discharge_rmse.py` | Reproduction script (mean-coef vs per-shot OLS) |
| `_audit_discharge_rmse_results.json` | Numeric dump from last run |
| `d3d_discharge_ledger.csv` | 62-shot source inventory |
| `D3D_CANONICAL_DATA_AND_PREPROCESSING_PROVENANCE.md` | Prior provenance (reported 0.4125 from export path) |
