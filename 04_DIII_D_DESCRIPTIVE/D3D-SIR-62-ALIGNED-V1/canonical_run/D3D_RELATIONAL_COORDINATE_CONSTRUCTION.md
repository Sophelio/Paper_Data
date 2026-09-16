# D3D Relational / Phase Coordinate Construction — D3D-SIR-62-ALIGNED-V1

Evidence from current Archaieus sources and the frozen feature export. Exact per-realization numerical `shift` values from the export-generating run are **not** stored in the parquet files → `EXACT_SHIFT_VALUE_UNKNOWN`.

## Code path

1. Provider grid (`diiid_elm_data_provider.py`): signals on shared 1000-point ms grid; `freq = dt` in **milliseconds**; `smooth_rate = 0`.
2. `consumer_function.py`: per-realization z-score of primitives; `dt` from `timing_data` (ms); finite-difference `TRANSFORMS.differentiate(..., dt=dt)`.
3. `get_shiftval(..., out_type='Derivative')` (`consumer_function.py` ~L122–126):
   `shift = abs(min(vstack(x, dx))) + nmin` with `nmin` typically 100 in UI settings — **exact historical nmin/shift not in export**.
4. XPhaseders / quotients: `TRANSFORMS.make_Quotients(VAR, keys, shift, add_inverse=True)` (`transforms.py` L218–240):
   `(X_i + shift) / (X_j + shift)`; inverse via `1/out` when `add_inverse=True`.
5. YPhaseders: target temporal derivative in numerator only (`consumer_function.py` ~L416–420).
6. When `total_normalization` / export z-score applies: derived columns are z-scored per realization before packaging.

## Answers to required questions

1. **Expressions (pre-standardization, with shift):**
   - `[d[a]/d[b]]` ≡ `(d[a]/d[t] + s) / (d[b]/d[t] + s)` for phase pairs among non-target and Y-phaseders with target-in-numerator for `[d[pcdiamag3]/d[*]]`.
   - `[r[q95]/r[kappa]]` ≡ `(r[q95] + s) / (r[kappa] + s)`.
   - `[d[betan]/d[t]]`, `[d[kappa]/d[t]]`: temporal FD derivatives (then standardized).
2. **Numerator and denominator shifted?** Yes for quotients/phaseders via `make_Quotients` / yPhaseder construction.
3. **Shift definition:** `abs(min(relevant blob)) + nmin` (`get_shiftval`).
4. **Shift scope:** **per realization** (computed inside consumer from that realization’s arrays). Not a single global constant across the cohort.
5. **Numerical shift values:** `EXACT_SHIFT_VALUE_UNKNOWN` (not serialized into parquet). Minimum artifact to resolve: consumer logs or pickled `meanSTDinfo`/realization objects from the export run, or re-ingest with recorded `nmin` and dump `shiftval`.
6. **Denominator masks:** none inside `make_Quotients`; positivity encouraged by additive shift. Downstream finite mask in validation prep only.
7. **Quotient columns standardized after construction?** Export manifest `normalization: zscore` — yes in the frozen export columns.
8. **Primitives standardized before differentiation?** Yes in the consumer path when z-score is enabled (export processing `zscore`).
9. **`dt` units:** milliseconds as returned by the Paper provider.
10. **ms↔s invariance after z-score:** phase/quotient ratios of derivatives are invariant to global time-unit rescaling; absolute `d[*]/d[t]` scale with `1/dt` but z-scoring removes a global factor from standardized columns used in RMSE.
11. **Exported vs simple symbolic quotient:** exported columns are **shift-augmented then (export) z-scored**, not bare `a/b`.
12. **Eliminated rational form:** for a phase coordinate, with affine z-score `z = (u - μ)/σ` on the shifted ratio `u = (ṅ_num + s)/(ṅ_den + s)`, the paper-facing symbol is an affine transform of that shifted ratio — **not** the unshifted elimination identity unless `s=0` and no z-score (not the case here).

Machine-readable twin: `d3d_relational_coordinate_manifest.json`.
