# S7.1R Issue 4 — Temporal grid reconciliation

**Mandatory pass.** Determines exactly where "20 ms" originated and whether it
is a real property of any stage.
**Data:** `temporal_grid_reconciliation.csv`.

## 1. Verdict

**Outcome C — different stages genuinely use different grids, and both numbers
are real.**

> **20 ms is the native sampling cadence of the equilibrium group, and the grid
> spacing the *full 95-signal provider* would produce whenever an equilibrium
> signal is among those requested. It is not, and never was, the spacing of the
> paper-facing analysis grid, which is a 1000-point linspace at 4.08–6.03 ms.**

Neither number is an error. They belong to different objects and were conflated
because both were described as "the grid".

## 2. Where each number comes from

### 20 ms — measured, and codified

Two independent local confirmations:

1. **Measured.** The S7.1 census computed the native median Δt of all 95 signals
   across all 62 discharges. All 15 equilibrium quantities return **exactly
   20.0 ms**, the coarsest group in the object.

2. **Codified.** `sir-web/providers/diiid_elm_data_provider.py` sets the common
   grid to the **coarsest** requested signal's native cadence
   (L140–143: `dts = {name: _native_dt(times) ...}`), with the reasoning stated
   in the code itself:

   > *"the coarsest requested signal sets the rate — interpolating a 20 ms
   > equilibrium signal onto a 0.02 ms filterscope grid would fabricate…"*

   and again at L162–163, on anti-aliasing *"e.g. fs04da at 0.02 ms onto a 20 ms
   grid"*.

So for the full provider, a request including any equilibrium quantity yields a
~20 ms grid **by design**. This is a correct engineering decision — it refuses to
manufacture resolution — and it is the origin of the number.

### 4.08–6.03 ms — the paper-facing analysis grid

The paper provider does something different: it takes the intersection window of
the requested signals and lays a **fixed 1000-point** linspace across it
(`TARGET_N = 1000`). Because the window varies by discharge while the point count
does not, Δt varies:

| Statistic | Value |
|---|---|
| min | 4.08 ms |
| median | 4.96 ms |
| max | 6.03 ms |

Corroborated independently by the discharge ledger's `grid_dt_seconds` column,
by the validation audit (median Δt ≈ 4.764 ms), and by the finite-window study
(median Δt ≈ 4.784 ms on run `run_20260810_152325_fw_scout`).

## 3. Every stage traced separately

| Stage | Grid rule | Δt | Evidence |
|---|---|---|---|
| Archive `resampled_data_v6` | per-signal native, no common grid | equilibrium 20.0; filterscope 0.02 | direct measurement, 62 shots |
| Full 95-signal provider | coarsest requested native dt | ~20 if equilibrium requested | `CODE_VERIFIED` L140–167 |
| Paper-facing export (8 signals) | 1000-point linspace on intersection | 4.08–6.03 | `CODE_VERIFIED` + ledger |
| q_desc canonical run | inherited | 4.764 median | `LOCAL_DOCUMENTED` |
| retired q_rec run | inherited | 4–6 | `STRONGLY_INFERRED` (run retired) |
| spline realization | inherited; `UnivariateSpline k=5, s=0.1` | inherited | `LOCAL_DOCUMENTED` |
| RTS realization | inherited; `R=1, Q=1e-4`, derivatives scaled `1/dt^order` | inherited | `LOCAL_DOCUMENTED` |

No stage was forced into agreement with another. The two grids are recorded as
what they are.

## 4. Which claims are wrong

| Claim | Status |
|---|---|
| "the analysis used a fixed 20 ms grid" | **INCORRECT** for every paper-facing run |
| "equilibrium quantities are natively sampled at ~20 ms" | **CORRECT**, measured |
| "the full provider grids to ~20 ms when equilibrium signals are requested" | **CORRECT**, code-verified |
| "the analysis Δt is fixed" | **INCORRECT** — it varies by discharge |

The canonical provenance ledger had already flagged this at its line 203
(*"Fixed Δt = 0.020 s — Not supported by Paper provider outputs / ledger"*) and
line 428 (*"Both real; Paper path is authoritative"*). S7.1R confirms that
reading and adds the code-level mechanism behind it.

**Any manuscript or figure caption stating a 20 ms analysis step must be
corrected to the variable 4.1–6.0 ms grid.** This report is the citable basis.

## 5. The consequence that matters

The reconciliation is not merely bookkeeping. Placing 20 ms equilibrium
quantities on a 4.96 ms grid **oversamples them by ~4.0×**: four of every five
grid points on `betan`, `q95`, `li`, `kappa` and the other eleven are values the
interpolant invented, not values the reconstruction produced.

Two further factors compound it:

- In 2 of 62 discharges the *upstream* pipeline had already upsampled the
  equilibrium group (length ratio up to 4.09), pushing the compounded factor to
  ~16× in those shots.
- The paper provider block-averages signals **denser** than the grid but
  linearly interpolates signals **sparser** than it. The equilibrium group is
  always in the second category.

For a framework whose coordinates are phase derivatives, this is a first-order
concern: at 4× oversampling a numerical derivative of an equilibrium quantity is
governed by the interpolation scheme, and the spline and RTS realizations then
differ not because the physics differs but because they interpolate differently.

This is stated as a structural property of the object. It is **not** a
performance claim, and no reconstruction result was inspected to reach it.

## 6. Recommendation

1. Correct any 20 ms statement in manuscript or figure text.
2. Record both grids explicitly wherever the object is described — they are
   properties of *different providers*, not competing accounts of one.
3. Carry the ~4× equilibrium oversampling into S7.2 as a declared constraint on
   derivative-valued coordinates over the equilibrium group.
