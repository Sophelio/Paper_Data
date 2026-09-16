# DIII-D canonical 62-shot data and preprocessing provenance

**Purpose.** Forensic ledger of the exact cohort and transformations that precede coordinate construction for the DIII-D relational-coordinates analysis in this repository. This document does **not** refit models, alter the selected relation, or regenerate scientific results.

**Companion artifact.** [`d3d_discharge_ledger.csv`](d3d_discharge_ledger.csv) — one row per canonical discharge (62 rows).

**Ledger builder.** [`build_d3d_discharge_ledger.py`](build_d3d_discharge_ledger.py) (re-runnable; inspects local `resampled_data_v6` npz files).

**Provenance record generated (UTC).** `2026-08-04T19:52:22Z` (ledger build timestamp in `_ledger_build_stats.json`).

---

## 1. Canonical status

| Item | Value | Evidence |
|------|-------|----------|
| Canonical cohort size | **62 discharges** | `ADMISSIBLE_SHOTS` (exactly 62 IDs); 11× `FEATURE_EXPORTS/pcdiamag3_*` dirs with 62 parquets each; `figures/d3d_discharge_validation_metrics.csv` (62 rows) |
| Authoritative shot-list artifact | `Paper Examples/Relational Coordinates for Multimodal Plasma Observations/SIR_to_dFL_provider_on_ELM_shots_with_phaseders.py` (`ADMISSIBLE_SHOTS`, lines 40–51) | SHA-256 `d988ecf00b2a77c558e1ec3f840edd0b11577e3855366c63cf88b0d7c41c5556` |
| Duplicate of same set | `providers/SIR_to_dFL_provider_on_ELM_shots_with_phaseders.py` | Same literal set |
| Corroborating inventory | `figures/d3d_discharge_validation_metrics.csv` | SHA-256 `0166636dbd02d85957cb0745af1292a7e83f0f19a3d0f7feec4ae8cce0f3028a`; shot column matches ledger exactly |
| Canonical run identifier | `D3D-CANONICAL-62SHOT-UNASSIGNED` | No formal tagged run ID found in-repo; **must be replaced** once a run is formally tagged |
| Closest machine-readable “paper” export stamp | `FEATURE_EXPORTS/pcdiamag3_none_2026-07-17_05-21-18PM_CDT_raw_final_paper_normalized` | Cited by `analysis/plot_d3d_discharge_validation.py` L55–58 and `figures/d3d_discharge_validation_summary.txt` |
| Git commit (sir-web HEAD) | `bc123d63b5e49d9c160808fdc97ba0442ce4bdd0` | `git rev-parse HEAD` at provenance generation |
| Branch | `SIR_paper_CEM` (tracking `origin/SIR_paper_CEM`, **behind 19**) | `git status -sb` |
| Worktree state | **Dirty** | Modified panel A/B figure scripts/outputs; dirty Archaieus submodule; untracked `FEATURE_EXPORTS/`, provenance folder, etc. |
| Archaieus submodule HEAD | `aefd942ea111f7bd24d1d86cafb954639aff3fb1` on `feature/fixed-equation-fit` (**behind 1**, dirty: `consumer_function.py` modified for XPhaseder/xi-xj inverses) | Submodule status |
| Analysis type | **Retrospective** reconstruction / sparse identification on the cohort | No held-out split artifact found for the canonical paper export; validation reconstructs from hard-coded `D3D_RELATION` |
| Manuscript “63” | Treat as **typographical error** relative to this cohort | No 63-shot inventory found in repository artifacts |
| “42 realizations” | **No 42-shot / 42-realization cohort found in repository artifacts** | Searched providers, FEATURE_EXPORTS, figures metrics, Paper Examples scripts. Incidental `42` values are fonttype/layout constants only. If a manuscript sentence says “42,” status is **UNKNOWN** whether typo or an external subset **not present here**; resolving it requires the manuscript source + any external run log that defines 42 |

**`realization_index` convention (ledger).** Zero-based integer `0 … 61`, assigned after sorting shot numbers ascending. Deterministic; independent of FEATURE_EXPORTS filename order.

---

## 2. Data source and acquisition lineage

### 2.1 Local derived archive

| Field | Value |
|-------|-------|
| Local root | `D:\DIII-D ELM data set\resampled_data_v6` (outside repo) |
| File naming | `shot_<id>_resampled.npz` + companion `shot_<id>_metadata.json` |
| Shot count on disk matching ADMISSIBLE_SHOTS | 62 / 62 present |
| Format | NumPy npz: for each signal `<name>`, arrays `<name>_data`, `<name>_times` |
| Time units | **Milliseconds** (provider docstrings; Paper Examples provider L12–14; full provider L19) |
| Signals per shot (upstream) | ~95 base signals (190 npz keys = data+times) |
| Who generated local files | **UNKNOWN** (no generator script / MD5 manifest for `resampled_data_v6` found in sir-web). Companion JSON records per-signal resampling methods such as `cubic_spline`, `cubic_spline_simple`, categories `smooth_high_snr` / `slow_varying`, and `original_length` / `resampled_length` — implying an upstream resampling pipeline not checked into this repo |
| Remote DIII-D archive query | **UNKNOWN** — not recorded in-repo |
| Alternate path in full provider | `/Users/ganatma/SapientAI/ELM Prediction/resampled_data_v6` (`providers/diiid_elm_data_provider.py` L60) — macOS path; not used by the active Paper Examples provider |

### 2.2 Quantity lineages (high level)

Distinguish without implying causality:

| Class | Examples in this dataset | Notes |
|-------|--------------------------|-------|
| Magnetics / energetic | `pcdiamag3`, `ip`, `bt`, … | Listed under Magnetics in full provider docstring |
| Neutral-beam actuation | `pinj`, beam-specific `pinj_*` | Actuation |
| Density | `density`, `prmtan_neped`, `prmtan_teped` | Pedestal quantities available upstream |
| Equilibrium / shape | `betan`, `q95`, `li`, `kappa`, `aminor`, … | Full provider lists equilibrium/shape group; metadata marks many as `cubic_spline` resampled |
| Fast diagnostics | filterscopes `fs*`, ECE, CER | Present upstream; **not** in the 8-signal admitted search |

### 2.3 Access limitations

- Local Windows absolute path is machine-specific.
- `FEATURE_EXPORTS/` is untracked in git (and `.gitignore` line for it appears corrupted / missing a newline in the checked-in ignore file). External reproduction requires the npz tree and/or the paper-normalized parquet export directory.
- No public DOI / archive accession for `resampled_data_v6` found in-repo → **UNKNOWN**.

### 2.4 Active providers

1. **Canonical paper / UI provider (8 signals):**  
   `Paper Examples/Relational Coordinates for Multimodal Plasma Observations/diiid_elm_data_provider.py`  
   - `ALLOWED_SIGNALS` L59–68  
   - `TARGET_N = 1000` L47  
   - `SMOOTH_RATE = 0.0` L72  
   - Referenced by `.bin/settings.json` → `data_provider_path`

2. **Full 95-signal provider (not the admitted search ontology):**  
   `providers/diiid_elm_data_provider.py` — coarsest-native-dt common grid + boxcar anti-alias

3. **Feature-export / dFL provider:**  
   `Paper Examples/.../SIR_to_dFL_provider_on_ELM_shots_with_phaseders.py` — reads parquets; filters to `ADMISSIBLE_SHOTS`

---

## 3. Cohort construction

### 3.1 Origin of the 62-shot list

- **Primary:** hard-coded `ADMISSIBLE_SHOTS` set (62 string IDs) in both SIR→dFL provider copies.
- Comment at L18–20 / L40 of the Paper Examples dFL provider: shots for which “the upstream ELM provider can form a common grid when all 95 signals are selected.”
- **Corroboration:** every `FEATURE_EXPORTS/pcdiamag3_*` directory inspected contains exactly those 62 `shot_<id>_resampled__model.parquet` files; discharge-validation metrics CSV uses the same IDs.

### 3.2 Inclusion / exclusion

| Topic | Finding |
|-------|---------|
| Inclusion criteria (algorithmic details) | **Partially documented** only as common-grid viability for all 95 upstream signals. Exact algorithm that selected these 62 from a larger ELM library is **UNKNOWN** (no candidate-list CSV / exclusion log in-repo) |
| Fit-quality as inclusion criterion | **Not evidenced** in cohort construction artifacts |
| Manual vs algorithmic interval selection | Intervals are **algorithmic per fetch**: intersection of requested signals’ time ranges (Paper provider). Upstream npz already contains per-signal resampled intervals from an external pipeline |
| Noncanonical shots on disk | Full `resampled_data_v6` may contain only these 62 or more — ledger scopes **only** the 62 ADMISSIBLE IDs. Broader directory census: **UNKNOWN** (not required for ledger) |
| All 62 share the eight search signals | **Yes** — ledger inspection: all eight `*_available = TRUE` for 62/62 |

### 3.3 Common support (per shot, paper provider)

For the eight admitted signals:

```text
t0 = max_i  min(time_i)
t1 = min_i  max(time_i)
grid = linspace(t0, t1, TARGET_N=1000)   # inclusive endpoints
dt_ms = grid[1] - grid[0]
dt_s  = dt_ms / 1000
```

Each signal is mapped onto `grid` by block-averaging if denser than `TARGET_N` in-window, else linear interpolation (`_resample_to_grid`, Paper provider L155–162).

**Ledger summary (common-support duration after intersection):**

| Statistic | Value |
|-----------|-------|
| Aligned sample count min / median / max | 1000 / 1000 / 1000 |
| Common-support duration (s) min / median / max | 4.080 / 4.960 / 6.020 |

**Important:** `grid_dt_seconds` is **not** a fixed `0.020`. Across the 62 shots it ranges ≈ **0.00408–0.00603 s** (~4.1–6.0 ms), because spacing is \((t_1-t_0)/(999)\) with variable windows. Native equilibrium sampling ~20 ms is discussed in the **full** provider docstring as a design constraint for the coarsest-dt grid, **not** as the Paper provider’s fixed output Δt.

---

## 4. Signal ontology and role in the search

### 4.1 Eight canonical search quantities

Order below matches `ALLOWED_SIGNALS` (Paper provider L59–68). Order is **significant** for relational-term orientation (provider comment L51–58).

| Manuscript symbol | Source key | Units before normalization | Lineage (provider grouping) | Role | Available in 62/62 | Admitted to coordinate generation | Appears in hard-coded selected support (`D3D_RELATION`) |
|-------------------|------------|----------------------------|-----------------------------|------|--------------------|-----------------------------------|--------------------------------------------------------|
| \(W_{\mathrm{dia}}\) | `pcdiamag3` | **UNKNOWN** (not stored in npz metadata) | Magnetics / diamagnetic energy | Target-bearing energetic signal | Yes | Yes | Yes (`d[pcdiamag3]/d[t]` target; also phase numerators) |
| \(P_{\mathrm{NBI}}\) | `pinj` | UNKNOWN | Neutral beams | Actuation | Yes | Yes | No |
| \(n_e\) | `density` | UNKNOWN | Density | Current / density state | Yes | Yes | No |
| \(I_p\) | `ip` | UNKNOWN | Magnetics | Current state | Yes | Yes | No |
| \(\beta_N\) | `betan` | UNKNOWN | Equilibrium | Pressure / equilibrium state | Yes | Yes | Yes |
| \(q_{95}\) | `q95` | UNKNOWN | Equilibrium geometry | Equilibrium geometry | Yes | Yes | Yes (`r[q95]/r[kappa]`) |
| \(\ell_i\) | `li` | UNKNOWN | Equilibrium | Equilibrium geometry / inductance | Yes | Yes | Yes |
| \(\kappa\) | `kappa` | UNKNOWN | Equilibrium geometry | Equilibrium geometry | Yes | Yes | Yes |

Physical units for each key are **UNKNOWN** in the local artifacts (no units table in npz/JSON). Manuscript units must not be invented here.

### 4.2 Excluded contextual signal: `prmtan_teped`

> `prmtan_teped` (\(T_{\mathrm{ped}}\)) was not included in the original or canonical DIII-D search space and therefore was neither eligible for nor rejected by the seven-term greedy selection. Any upstream availability is recorded only as contextual data provenance, not as part of the candidate ontology used to obtain the reported relation.

| Field | Value |
|-------|-------|
| Upstream availability | **Present in all 62** inspected npz archives (`prmtan_teped_data` / `_times`) |
| `prmtan_teped_admitted_to_search` | **FALSE** for every ledger row |
| Present in Paper `ALLOWED_SIGNALS` | **No** |
| Listed in full provider density group | Yes (`providers/diiid_elm_data_provider.py` L39) |
| Correlation / predictive importance | **Not evaluated** by the canonical search — do not infer |

Do **not** describe \(T_{\mathrm{ped}}\) as an available candidate that the greedy algorithm failed to select.

---

## 5. Temporal support, alignment, and the grid

### 5.1 Native time bases

- Each signal has its own `<name>_times` array in **ms**.
- Native median spacings differ by signal (example shot 155537 from direct inspection): `pcdiamag3` ~0.75 ms; equilibrium-like signals coarser (often ~20 ms class per full-provider documentation). Per-shot native medians are summarized in the ledger `notes` field.
- Companion metadata JSON records upstream resampling lengths/methods — **not** the SIR common grid.

### 5.2 Cleaning before alignment (Paper provider `_load_signal`)

1. Cast to float64.  
2. Drop non-finite time/value pairs.  
3. Stable argsort by time.  
4. Drop duplicate / non-increasing timestamps (`diff(times) > 0`).  

### 5.3 Alignment procedure (Paper provider — canonical for the 8-signal search)

```text
series[name] = cleaned (times_ms, values)
t0 = max_name times[0]
t1 = min_name times[-1]
assert t1 > t0
grid = linspace(t0, t1, 1000)          # inclusive endpoints
for each signal:
    if (# native samples in [t0,t1]) > 1000:
        block-average into bins centered on grid
        (empty bins → linear interp fallback)
    else:
        linear interpolate onto grid
dt_ms = grid[1] - grid[0]
return data (8×1000), timing_data (1×1000), dt_ms
```

Endpoint convention: `linspace` includes both endpoints. Last bin in block-averaging folds `times == edges[-1]` into the final bin (L136–139).

### 5.4 Verified Δt

| Claim | Status |
|-------|--------|
| Fixed \(\Delta t = 0.020\) s | **Not supported** by Paper provider outputs / ledger |
| Variable \(\Delta t \approx 4.1\text{–}6.0\) ms | **Verified** from ledger `grid_dt_seconds` |
| Native ~20 ms equilibrium | Documented in full provider as design rationale for coarsest-dt mode; **not** the Paper `TARGET_N` grid |

### 5.5 Export path times

FEATURE_EXPORTS parquets use a shared `times` column labeled **ms** (`TIME_UNITS = "ms"` in dFL provider). Discharge-validation summary: 62×1000 = 62000 rows retained.

---

## 6. Missing values, invalid intervals, masks, and quality control

| Mechanism | Implementation |
|-----------|----------------|
| Non-finite drop | `_load_signal` finite mask before alignment |
| Duplicate times | Removed |
| Empty common window | Raises `ValueError` in provider |
| Block-average empty bins | Linear interpolation fallback |
| Masks across signals before SIR | Intersection window only; no explicit Boolean mask product beyond finite cleaning |
| Minimum samples | ≥2 usable points per signal required |
| Manual QC decisions for the 62 | **UNKNOWN** (no QC log). Validation summary: `rows excluded: 0` for the paper-normalized export |

**Ledger finite fractions.** All eight canonical signals and `prmtan_teped` report finite fractions after load (see CSV). Summaries: all availability counts = 62 for search signals and for `prmtan_teped`.

---

## 7. Scaling and normalization

Implemented in `submodules/Archaieus/src/Archaieus/sir/consumer_function.py` → `standard_transformations`.

### 7.1 Scheme (when `total_normalization=True`)

1. **Per realization (per discharge), per signal:**  
   \(z = (x - \mu)/\sigma\) along the time axis (`scipy.stats.zscore`, `axis=-1` for features).  
2. Target \(y\) z-scored independently.  
3. If a smoother is used: smooth the z-scored signal, then **re-z-score** (second stage); params stored as `x_smoothed_mSD` / `y_smoothed_mSD`.  
4. Derivatives and phase coordinates are z-scored independently after construction when normalization is on.

### 7.2 Weighting implications

- Each discharge contributes `TARGET_N = 1000` aligned samples → **equal sample count per discharge** under the Paper provider.  
- Pooled metrics over 62000 samples therefore give **equal weight per discharge in sample count**, not duration-weighted differently (durations differ but \(N\) is fixed).  
- **No global μ/σ fitted across all 62 shots** for the consumer_function path — standardization is **within-shot**.  
- Degrees of freedom / `ddof` for `zscore`: SciPy default (`ddof=0`) unless overridden — **confirm in SciPy 1.17.1** as population std.  
- Zero-variance handling: **UNKNOWN** edge-case behavior if a signal is constant after cleaning (not observed in ledger).

### 7.3 Retrospective vs held-out

Present claim is retrospective on the full cohort. For a future held-out claim, **all** scaling parameters (and smoother hyperparameters if estimated) must be fit on training discharges only — **not** currently implemented as a train/test split in the paper export pipeline.

---

## 8. Reconstruction variants

Three export families exist under `FEATURE_EXPORTS/` (all 62 shots):

| Variant | Directory pattern | Hyperparameters evidenced |
|---------|-------------------|---------------------------|
| Aligned / unsmoothed (`none`) | `pcdiamag3_none_*` including `..._raw_final_paper_normalized` | `smoothing_method='none'`; Paper provider `SMOOTH_RATE=0.0` |
| Spline | `pcdiamag3_spline_*_spline_0.1` / `*_spline_01_final_paper_normalized` | Folder tag `0.1` ⇒ `Splsmooth=0.1` (not the code default 100) |
| RTS | `pcdiamag3_rts_*_RTS_R1_Q.0001*` | Folder tags ⇒ `measurement_noise=1` (`R1`), `process_noise=1e-4` (`Q.0001`) |

Exact UI settings JSON for the historical export runs (iterations, jobs, data_processing flags) are **UNKNOWN** (not stored inside FEATURE_EXPORTS manifests beyond target/`n_features`/paths). Manifests record per-shot model parquet paths and `target: pcdiamag3`.

### 8.1 Aligned / unsmoothed

Still includes: finite cleaning, intersection window, block-average or linear resample to 1000 points. **No** spline/Kalman/RTS. Derivatives via finite differences in `TRANSFORMS.differentiate` with `dt` from the realization grid (`consumer_function.py` finite-diff branch).

### 8.2 Spline

- Class: `SplineProcessor` (`sir/utils/spline_processor.py`)  
- Library: `scipy.interpolate.UnivariateSpline`  
- Degree: **k=5** (quintic)  
- Smoothing factor: `s=Splsmooth` (export family indicates **0.1**)  
- Boundary weights: first point and last `bc_window` points get weight `bc_weight` (defaults `bc_window=2`, `bc_weight=2` unless overridden — **override for paper export UNKNOWN**)  
- Fit: **per signal, per discharge**  
- Derivatives: analytic via `UnivariateSpline` derivative evaluation  

### 8.3 Rauch–Tung–Striebel (`KalmanProcessor`, `use_rts=True`)

- State: `[position, velocity, acceleration, jerk, snap]` (5D)  
- Transition: integrated Wiener / constant-snap kinematic `F` on **unit step** `dt=1` internally  
- Observation: \(H = [1,0,0,0,0]\), \(R = [[R]]\) with `measurement_noise`  
- Process noise: only snap entry \(Q_{44} = Q \cdot dt\) with `process_noise`  
- Init: state zeros; \(P = 10^3 I\)  
- Forward: filterpy `KalmanFilter` predict/update  
- Backward: custom RTS pass with `pinv` on prior covariance  
- Derivatives rescaled by \(1/\Delta t_{\mathrm{physical}}^{\mathrm{order}}\)  
- Parameters for paper RTS export (from folder name): **R=1**, **Q=1e-4**, fixed (not estimated per signal)  
- Edge handling: broad prior; duplicate-x averaging  

---

## 9. Derivative construction

| Item | none | spline / RTS |
|------|------|----------------|
| Quantity | Aligned (and z-scored if enabled) signals | Smoother level-0 then analytic/state derivatives |
| Order vs resampling | After provider alignment | After alignment + smoother fit |
| Physical spacing | `dt` from realization timing (ms→used as provided by coordinator; Paper returns ms grid — **unit consistency for FD:** `freq`/`dt` handling must match `validate_timing_data`; Paper `fetch_data` returns `dt` in **ms**) | Same physical `dt_physical` median for Kalman rescale |
| Estimator | `TRANSFORMS.differentiate` finite difference | Spline analytic / Kalman state |
| Phase coords | Numerator & denominator use same reconstruction path | Same |
| Small-denominator | Global `shiftval` from `get_shiftval(...)` before quotients/phaseders | Same |

**Unresolved detail:** whether the Paper provider’s millisecond `dt` is converted to seconds before finite differences in every historical export — requires checking `fetch_data` return and `validate_timing_data` usage in the exact export run. Code path uses coordinator `dt` directly in `differentiate(..., dt=dt)`. Mark **UNIT_CONSISTENCY_CHECK_NEEDED** if reconstructing absolute derivative units; z-scored targets make pooled RMSE scale-invariant to a global unit factor after standardization.

---

## 10. Coordinate construction immediately downstream of preprocessing

| Item | Evidence |
|------|----------|
| Target | Standardized \(\mathrm{d}W_{\mathrm{dia}}/\mathrm{d}t\) ≡ `[d[pcdiamag3]/d[t]]` (`D3D_RELATION["target_term"]`) |
| Primitive set | Eight `ALLOWED_SIGNALS` |
| Admitted library classes (UI) | Raw `x`, `dx/dt`, `XPhaseder`, `YPhaseder`, `xi/xj`, `y`, `y/x` (user settings at time of provenance inspection); higher-order f2–f4 optional |
| Phase coordinate | \(D_g f = (\mathrm{d}f/\mathrm{d}t)/(\mathrm{d}g/\mathrm{d}t)\) with shift in num/den (`make_Quotients` / phaseders) |
| Denominator policy | Additive `shiftval` so denominators stay positive |
| Candidate-library size | Manifest `n_features` varies by export (e.g. 62 or 65 feature columns) — exact search-time checklist **UNKNOWN** without the run’s saved settings |
| Seven-term greedy budget | Hard-coded relation has **7 terms + intercept≈0**; search hyperparameters (order, num_terms) for the original discovery run: **UNKNOWN** (not in export manifests) |
| Selected support identifier | `dash_app/utils/discharge_validation.py` → `D3D_RELATION` terms |

Selected support (identifiers only; not recomputed here):

```text
[d[pcdiamag3]/d[kappa]], [d[kappa]/d[t]], [r[q95]/r[kappa]],
[d[pcdiamag3]/d[betan]], [d[kappa]/d[betan]], [d[betan]/d[t]],
[d[li]/d[betan]]
```

---

## 11. Randomness, software, and execution environment

| Item | Value |
|------|-------|
| Preprocessing randomness | Alignment / zscore / spline / RTS paths are **deterministic** given inputs and hyperparameters (no RNG seeds in these processors) |
| Python | 3.11.15 (conda-forge) |
| numpy / scipy / pandas / sklearn / filterpy / matplotlib | 1.26.4 / 1.17.1 / 2.3.3 / 1.9.0 / 1.4.5 / 3.11.0 |
| Env file | `environment.yml` (`sir_web`) |
| OS (this provenance host) | Windows 10/11 (`win32 10.0.26200`) |
| Hardware effects | **UNKNOWN** / not claimed |
| Commands used to generate this package | See §14 |

---

## 12. Metric terminology relevant to provenance

Implementation: `dash_app/utils/discharge_validation.py`.

| Metric | Definition in code |
|--------|--------------------|
| Residual | \(e = y_{\mathrm{obs}} - y_{\mathrm{pred}}\) |
| Per-discharge RMSE | \(\sqrt{\mathrm{mean}(e^2)}\) within discharge |
| Per-discharge MAE | \(\mathrm{mean}(|e|)\) |
| Pooled RMSE | \(\sqrt{\mathrm{mean}(e^2)}\) over **all** retained observations (not mean of per-discharge RMSEs) — L243–266 |
| Pooled MSE | Not named; equals \((\mathrm{pooled\ RMSE})^2\) |
| Median discharge RMSE | Median of per-discharge RMSE distribution; representative discharge = closest to that median (`select_median_error_discharge`) |
| Units | Standardized-target units of the export columns |

**Label caution.** Custom graph id `Per-discharge_normalized_RMSE` and axis text “Normalized RMSE” refer to RMSE on the **already standardized** target — not an extra normalization of RMSE by another scale. Paper summary reports pooled RMSE `0.4125` on 62000 rows.

Hard-coded coefficients in `D3D_RELATION` / network figure docstrings are **scientific values embedded in source**, not loaded from a fit dump.

---

## 13. Figure and table lineage

| Output | Generator script | Inputs | Values hard-coded? |
|--------|------------------|--------|--------------------|
| Ontology figure (`figures/d3d_tokamak_ontology_*`) | `Paper Examples/.../make_ontology_vector.py` | Manual SVG geometry | Selection styling; shows \(n_e, T_{\mathrm{ped}}\) as “available but unselected” (**documentation error relative to admitted search**) |
| Relational network (`figures/d3d_relational_network.*`) | `plot_d3d_relational_network.py` (+ `_revised.py`) | Manual layout; coeffs in module docstring / `COORDINATES` | **Yes** — coefficients hard-coded |
| Discharge-resolved residual Panel C | `analysis/plot_d3d_discharge_validation.py` + `discharge_validation.py` | `FEATURE_EXPORTS/..._raw_final_paper_normalized` | Coefficients from `D3D_RELATION` hard-coded; metrics computed |
| Metrics table CSV/TXT | same | same | Computed |
| Displayed equation | Network script docstring + `D3D_RELATION` | — | Hard-coded |

---

## Manuscript corrections implied by the canonical search space

No manuscript `.tex` / Supplementary Table S3 file is present in `D:\sir-web`. Corrections below are limited to **in-repository figure/source locations** that incorrectly treat \(T_{\mathrm{ped}}\) as part of the admitted candidate ontology or as “available but unselected” by the search.

| Location | Issue | Required correction (documentation only; not applied here) |
|----------|-------|--------------------------------------------------------------|
| `make_ontology_vector.py` L445–471 | Renders \(n_e, T_{\mathrm{ped}}\) under “Additional context” with key text **“available but unselected”** | Remove \(T_{\mathrm{ped}}\) from that ontology panel or relabel as **not admitted to search** (upstream-only). \(n_e\)/`density` **was** admitted but unselected by the sparse relation — keep distinct from \(T_{\mathrm{ped}}\) |
| Rendered ontology SVG/PNG/PDF under `figures/` | Same visual claim | Regenerate after source fix |
| `plot_d3d_relational_network.py` L132 | Comment: “\(I_p, P_{\mathrm{NBI}}, n_e, T_{\mathrm{ped}}\) are intentionally excluded” | \(T_{\mathrm{ped}}\) was **never in the search space**; \(I_p, P_{\mathrm{NBI}}, n_e\) were admitted but not selected. Split these cases in wording |
| `plot_d3d_relational_network_revised.py` L131 | Same comment | Same |
| Main Results / Methods / Supplementary Table S3 (external manuscript) | **UNKNOWN paths** — not in this repo | Author must locate every list that includes \(T_{\mathrm{ped}}\) among the eight (or nine) “initial quantities” and delete it from the **candidate ontology**; mention upstream availability only as excluded context |

These are **documentation errors**, not search results.

---

## 14. Validation of the provenance package

### 14.1 Ledger validation (from `_ledger_build_stats.json`)

| Check | Result |
|-------|--------|
| Row count | **62** |
| Unique shots | **62** |
| Unique `realization_index` | **62** (0–61) |
| Eight canonical signals available | **62/62 each** |
| `prmtan_teped` available upstream | **62/62**, admitted **FALSE** |
| 42-shot subset artifact | **None found** |
| Aligned \(N\) min/median/max | 1000 / 1000 / 1000 |
| Common-support duration (s) min/median/max | 4.080 / 4.960 / 6.020 |
| CSV SHA-256 | `4e7d6275abdd0b23423f5862ad9f092de235509a3ee9a7572f0fd608b6f6d67e` |

### 14.2 Unresolved `UNKNOWN` fields (package-level)

1. Formal `canonical_run_id` tag (placeholder `D3D-CANONICAL-62SHOT-UNASSIGNED`).  
2. Physical units for each of the eight keys.  
3. Upstream generator of `resampled_data_v6` and archive accession/DOI.  
4. Exact exclusion algorithm that produced ADMISSIBLE_SHOTS from a larger library.  
5. Full SIR run settings (order, num_terms, data_processing checklist, seeds) for the discovery that produced `D3D_RELATION`.  
6. Whether manuscript “42 realizations” is a typo (no in-repo subset).  
7. Whether FD `dt` was interpreted as seconds or milliseconds in every export (unit consistency).  
8. Spline `bc_window` / `bc_weight` actually used in the `spline_0.1` export (defaults vs overrides).  
9. Manuscript `.tex` / Table S3 paths (not in repo).

### 14.3 Contradictions (not silently reconciled)

| Conflict | Parties | Resolution status |
|----------|---------|-------------------|
| Fixed 20 ms grid vs Paper `TARGET_N` linspace | Full-provider docs (~20 ms coarsest) vs Paper provider (variable ~4–6 ms) | **Both real**; Paper path is authoritative for the 8-signal canonical search |
| \(T_{\mathrm{ped}}\) “available but unselected” vs not admitted | Ontology figure vs `ALLOWED_SIGNALS` | Figure/docs wrong; search ontology excludes teped |
| Dirty git / submodule vs frozen science | Worktree dirty at provenance time | Recorded; does not change the 62-shot npz/export inventories |
| Tests still expecting 95 variables | `tests/test_diiid_elm_provider.py` vs Paper 8-signal provider | Stale tests — not used as cohort authority |

### 14.4 Commands used

```bash
conda activate sir_web
python "Paper Examples/Relational Coordinates for Multimodal Plasma Observations/canonical_d3d_62_shot_provenance/build_d3d_discharge_ledger.py"
# then this Markdown was authored from the stats JSON + code inspection
```

---

## 15. Provenance-qualified summary

**Established.** The canonical cohort is exactly the 62 shots in `ADMISSIBLE_SHOTS`, all present as local `resampled_data_v6` npz files and as paper FEATURE_EXPORTS. The admitted search ontology is exactly eight signals (`pcdiamag3` + seven others); `prmtan_teped` is upstream-available but **not admitted**. The Paper provider aligns each shot to 1000 samples on the intersection window with **variable** \(\Delta t\sim 4\text{–}6\,\mathrm{ms}\), not a fixed 0.020 s grid. Standardization is per-discharge z-scoring in Archaieus. Three reconstruction export families (none / spline≈0.1 / RTS R=1,Q=1e-4) exist with 62 files each. Downstream metrics and the seven-term relation are implemented/hard-coded in `discharge_validation.py` and network figure scripts.

**Unresolved.** Formal run ID; physical units; upstream archive provenance; original greedy search hyperparameters; manuscript “42” wording; FD time-unit consistency; manuscript TeX/Table S3 locations; ontology-figure wording that misstates \(T_{\mathrm{ped}}\)’s search status.

**Not claimed here.** Predictive generalization, causal mechanism, or any importance ranking of \(T_{\mathrm{ped}}\).
