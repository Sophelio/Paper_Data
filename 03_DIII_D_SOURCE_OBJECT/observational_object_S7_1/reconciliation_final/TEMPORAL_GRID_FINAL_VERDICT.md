# S7.1R-FINAL — Temporal grid: final verdict

Machine-readable form: `FINAL_TEMPORAL_LINEAGE.csv` (8 stages).

## Verdict

```
FIXED_20_MS_CANONICAL_GRID = FALSE          -- formally retired
```

> The canonical Paper provider used a **discharge-specific 1000-point common
> grid**, with Δt ≈ **4.08–6.03 ms** (median 4.965). The ~20 ms figure is the
> **native resolution of the equilibrium-class signals**, and the spacing the
> **full 95-signal provider** produces because it grids to the coarsest
> requested signal. It was never the Paper analysis grid.

Verified, not assumed. Both numbers are real; they belong to different objects.

## The chain, stage by stage

| # | Stage | Signals | n | Spacing rule | Δt (ms) | Evidence |
|---|---|---|---|---|---|---|
| 1 | native source time bases | 95 | per signal | diagnostic-native | equilibrium **20.0**, filterscope **0.02** | CODE_VERIFIED |
| 2 | upstream resampled archive | 95 | per signal | upstream pipeline, per-signal method | 0.02 – 20.0 | LOCAL_DOCUMENTED |
| 3 | full 95-signal provider grid | requested | window/dt | coarsest requested native dt | **~20** if any equilibrium signal is requested | CODE_VERIFIED |
| 4 | canonical Paper 8-signal grid | 8 | **1000** | `(t1−t0)/999`, per discharge | **4.084 / 4.965 / 6.026** | CODE_VERIFIED |
| 4b | full-object 95-signal grid | 95 | **1000** | `(t1−t0)/999`, per discharge | **3.754 / 4.595 / 5.365** | CODE_VERIFIED |
| 5 | paper feature exports | 8 + derived | 1000 | inherited | 4.965 | LOCAL_DOCUMENTED |
| 6 | q_desc numerical realizations | 8 | 1000 | inherited | 4.764 median | LOCAL_DOCUMENTED |
| 7 | dFL feature export | derived | 1000 | inherited | 4.764 | CODE_VERIFIED |

(min / median / max over the 62 discharges.)

## Where 20 ms comes from

Two independent confirmations, and neither is the analysis grid.

**Measured.** All 15 equilibrium quantities return a native median Δt of
**exactly 20.0 ms** across all 62 discharges — the coarsest group in the object,
1000× slower than the filterscopes.

**Codified.** `sir-web/providers/diiid_elm_data_provider.py` L140–143 sets the
common grid to the coarsest requested signal's native cadence, and states the
reasoning in the source itself:

> *"the coarsest requested signal sets the rate — interpolating a 20 ms
> equilibrium signal onto a 0.02 ms filterscope grid would fabricate…"*

That is a correct engineering decision — it refuses to manufacture resolution —
and it is the origin of the number.

## Where 4–6 ms comes from

`TARGET_N = 1000` points laid across the intersection window. The point count is
fixed and the window is not, so Δt varies by discharge. Corroborated
independently by the discharge ledger's `grid_dt_seconds`, by the validation
audit (median 4.764 ms) and by the finite-window study (median 4.784 ms on run
`run_20260810_152325_fw_scout`).

Confirmed again here: reference provider on shot 155537 with `PAPER_EIGHT`
returns Δt = **4.7644 ms**, matching the documented canonical 4.764 ms.

## Which statements are wrong

| Claim | Status |
|---|---|
| "the analysis used a fixed 20 ms grid" | **INCORRECT** for every paper-facing run |
| "the analysis Δt is fixed" | **INCORRECT** — it is discharge-specific |
| "equilibrium quantities are natively sampled at ~20 ms" | **CORRECT**, measured |
| "the full provider grids to ~20 ms when equilibrium signals are requested" | **CORRECT**, code-verified |

**Any manuscript or figure text stating a 20 ms analysis step must be corrected**
to the variable 4.1–6.0 ms grid. This document is the citable basis.

## The consequence that matters

Placing 20.0 ms equilibrium quantities on a ~4.96 ms grid **oversamples them by
~4×**: four of every five grid points on `betan`, `q95`, `li`, `kappa` and the
other eleven are interpolated, not reconstructed.

The provider block-averages signals **denser** than the grid but **linearly
interpolates** those **sparser** than it. The equilibrium group is always in the
second branch. In 2 of 62 discharges the upstream pipeline had already upsampled
that group (length ratio up to 4.09), compounding to ~16×.

For a framework whose coordinates are phase derivatives this is first-order: at
4× oversampling a numerical derivative of an equilibrium quantity is governed by
the interpolant, and the spline and RTS realizations then differ because they
interpolate differently, not because the physics does.

Stated as a structural property of the object. No reconstruction result was
inspected to reach it.

## Note for S7.2

Requesting all 95 signals narrows the common window to ~90% of the paper-eight
window (median 4590 ms vs 4960 ms), giving Δt ≈ 4.595 ms. **A run over all 95 is
therefore not on the same grid as the canonical q_desc run.** No discharge loses
more than half its window.
