# Audit — sensitivity-centered reference-shifted regularized phase

**Date:** 2026-08-25
**Scope:** the coordinate `D^sc` as implemented in (A) the SIR paper figure code,
(B) the Dalia project `DIIID_SIR_Paper`, and (C) the historical sir-web/Archaieus
source.
**Status:** A is **fixed**. B is **not modified** — this report is the
prerequisite for that decision.

---

## 1. The intended coordinate

With numerator rate `n`, denominator (reference) rate `d`, fitted over a
training cohort:

```
u_n = n / S_n                      u_d = d / S_d          normalize FIRST
s_0   = max(0, -min_fit(u_d))                             clearance AFTER
s_eff = s_0 + kappa
w     = u_d + s_eff
g(w)  = w / (w^2 + rho^2)                                 denominator gain
C_RS  = (u_n + s_eff) * g(w)                              numerator shifted too
g_bar = mean_fit[g(w)]                                    frozen on the cohort
C_SC  = C_RS - g_bar * u_n = u_n * (g - g_bar) + s_eff * g
```

Paper convention `D_g f = (df/dt)/(dg/dt)`, written `D^sc_g f` — one subscript,
the reference. The figure coordinate is `D^sc_{x_2} x_1 ~ dx1/dx2`:
**numerator `dx1/dt`, denominator/reference `dx2/dt`.**

The defining property of `g_bar` is `mean_fit(g - g_bar) = 0`. Sensitivity
centering removes the mean **direct numerator sensitivity** `g_bar·u_n`. It is
**not** ordinary mean-centering `C_RS - mean(C_RS)`; that would instead force
`mean(C_SC) = 0`, a different and weaker condition that discards no sensitivity
at all.

---

## 2. Provenance actually traced

| Claim | Verified |
|---|---|
| Dalia transforms come from the **project document**, not `DIIID_example/data_provider.py` | Yes, and more strongly than stated: **`DIIID_example/` contains no `data_provider.py` and no `transforms.py` at all.** Both exist only inside the project JSON. Note the *embedded* `data_provider.py:241` **does** register them at load time via `"custom_transform_dictionary": build_transforms(data_folder)` — so the blocks are provider-registered, but from the embedded provider, and the math is entirely in the embedded `transforms.py` |
| `blocks/sensitivity_centered_phase.py` is a thin re-export | Yes — 726 bytes, re-exports from `transforms.py` via `blocks/_shared.py` |
| The math lives in the embedded `transforms.py` | Yes — 15 701 chars inside the project JSON |
| sir-web `diiid_elm_data_provider.py` holds the historical math | **No.** Line 620 only passes `normalization_mode=mode` into `Dataset_Constructor`. The math is in `Archaieus.sir.conditioning_consumer` + `Archaieus/sir/utils/conditioning_aware.py` |
| On-disk project JSON is current | **No.** Disk is version **134**; the live Dalia server reports **146**. The *transform math is byte-identical* between them, so the audit is unaffected, but the disk copy is stale |

Historical implementation, exactly located:
- `Archaieus/sir/utils/conditioning_aware.py:210` `fit_denominator_clearance`
- `…:246` `regularized_denominator_gain`
- `…:257` `sensitivity_centered_clearance_ratio`
- `…:277` `fit_training_mean_gain`
- driver: `Archaieus/sir/conditioning_consumer.py:1013-1032` (mode
  `sensitivity_centered_reference_shifted_regularized_phase`)

---

## 3. Component-by-component comparison

| # | Component | (A) Figure — **corrected** | (B) Dalia project | (C) Archaieus (historical) |
|---|---|---|---|---|
| 1 | Numerator normalization | `u_n = n/S_n` | `u = rate_y/scale_u` | `apply_operand_scale(dy, S_dy)` |
| 2 | Denominator normalization | `u_d = d/S_d` | `rate_x/scale_v` | `apply_operand_scale(dx_j, S_j)` |
| 3 | Scale estimator | pooled RMS of the rate | pooled RMS of the rate over 62 shots | pooled RMS / robust-zero-MAD over cohort |
| 4 | Numerator vs denominator | num `dx1/dt`, den `dx2/dt` | num = block's signal, den = `denominator` param | num = target `dy/dt`, den = feature `dx_j/dt` |
| 5 | Reference shift | `w = u_d + s_eff` | `v = u_d + s_eff` | `w = v + s_eff` |
| 6 | **Shift computed before/after normalization** | **AFTER** ✓ | **BEFORE — on the RAW rate** ✗ | **AFTER** ✓ |
| 7 | Clearance | `s_0 = max(0,-min u_d)` | `max(0,-min(raw rate))` ✗ | `max(0,-min u_d)` ✓ |
| 8 | kappa | `s_eff = s_0 + kappa` | `s_eff = raw_clearance + kappa` | `s_eff = s0 + kappa` |
| 9 | rho | `+rho^2` in denominator | same | same |
| 10 | Regularized gain | `g = w/(w²+rho²)` | `u*v/(v²+rho²)` — never isolates `g` | `g = w/(w²+rho²)` |
| 11 | **Is the numerator shifted?** | **Yes**, `(u_n+s_eff)` ✓ | **No** ✗ | **Yes** ✓ |
| 12 | **Sensitivity centering** | `− g_bar·u_n` ✓ | `− nanmean(series)` ✗ | `− g_bar·u_n` ✓ |
| 13 | `mean(C)` vs `mean(g)·u_n` | `mean(g)·u_n` | **`mean(C)`** | `mean(g)·u_n` |
| 14 | Fit samples | whole trajectory | scales+clearance: 62-shot cohort; **centering: the single record** | training cohort, all realizations |
| 15 | Params frozen at apply time | yes (`PhaseParams`) | scales/clearance yes; **centering re-fit per record** ✗ | yes — frozen in `registry`, reused on held-out |
| 16 | NaN/Inf | non-finite dropped from fits; NaN stays local | same; `_align_to` yields NaN outside overlap | `_finite()` on every fit; raises if no finite samples |
| 17 | Near denominator turning points | `g` peaks at `w=rho`, sign-safe via `s_0` | `s_0` wrong ⇒ **`g` never varies** (see §4) | `g` peaks at `w=rho`, sign-safe |
| 18 | Clipping / hidden stabilization | none; `MIN_SCALE=1e-15` floor only | none; same floor | `min_scale` floor + documented MAD→RMS fallback |
| 19 | Fit-time vs transform-time | identical | **differs** (per-record centering) | identical |
| 20 | Derivative orientation | `D^sc_{x_2} x_1`, label derived from `PHASE_LABEL` | n/a (no derivative) | target-numerator, feature-denominator |

### Verdicts

| Pair | Verdict |
|---|---|
| **(A) corrected figure ↔ (C) Archaieus** | **MATCH** — agree elementwise to `rtol=0, atol=1e-12` across 4 signal cases × 5 (rho,kappa) settings |
| **(A) *pre-fix* figure ↔ (C)** | **SCIENTIFICALLY MATERIAL DIFFERENCE** — three independent defects (6/7, 11, 12) |
| **(B) Dalia ↔ (C) Archaieus** | **SCIENTIFICALLY MATERIAL DIFFERENCE** — see §4 |
| **(B) Dalia ↔ (A) corrected** | **SCIENTIFICALLY MATERIAL DIFFERENCE** — same three defects |

---

## 4. Measured impact on the real 62-shot DIII-D cohort

Numerator `pcdiamag3`, denominator `ip`, `rho=0.1, kappa=1.0, pooled_rms` —
the project's own defaults.

| Quantity | Dalia | Intended |
|---|---|---|
| `S_n` (rate RMS `pcdiamag3`) | 0.186886 | 0.186886 |
| `S_d` (rate RMS `ip`) | 3869.81 | 3869.81 |
| clearance | **445 178** (raw A/s) | **115.039** (normalized) |
| `s_eff` | **445 179** | **116.039** |
| `g_bar` | not computed | 0.00861813 |

**`s_eff` is too large by a factor of 3836.** The clearance is taken from the
raw `ip` rate, whose units are ~10⁵ A/s, and then added to `u_d`, which is
O(1)–O(100) by construction.

The consequence is not a small bias. Since `w = u_d + 445179 ≈ 445179`, the
gain `g = w/(w²+rho²)` is **constant to 2×10⁻⁶ relative spread**. The
coordinate therefore collapses to

```
C_Dalia = u_n · g − mean(u_n · g)  ≈  const · u_n − const
```

Measured directly on all 62 shots:

- `|corr(Dalia output, u_n)| = 1.00000000` — median **and** minimum.
- `corr(Dalia, intended)` — median **−0.017**, range [−0.130, +0.289].
- normalized RMS difference — median **125×** the intended coordinate's own σ.

**The Dalia "sensitivity-centered reference-shifted phase" is, on this dataset,
an affine rescaling of the numerator's own time derivative.** It carries no
relational information about the reference channel whatsoever. It is not a
degraded version of the intended coordinate; it is a different quantity that
happens to share its name.

The intended construction satisfies `mean_fit(g − g_bar) = 5.7×10⁻¹⁹` ✓.
The Dalia construction satisfies `mean(C) = 0` — the wrong invariant.

### Secondary defect: per-record centering

`transforms.py::sensitivity_centered_phase` computes `mu = nanmean(series)` on
**the record currently being transformed**. Archaieus freezes `g_bar` on the
training cohort and reuses it for held-out realizations
(`conditioning_consumer.py:330-341`). Even after the clearance and
numerator-shift defects are fixed, this remains a train/apply leak: every
record would receive its own centering constant, so held-out records are not
mapped through the same function as training records.

---

## 5. Consequences

**Were historical DIII-D results generated with this discrepancy?**
Two distinct pipelines must be separated:

- **sir-web / Archaieus runs** (`canonical_d3d_62_shot_run_v1`, the DIII-D
  Ip reconstruction studies, and the other dated study folders) used the
  **correct** implementation. Nothing there is affected by the Dalia defect.
- **Anything produced through the Dalia `DIIID_SIR_Paper` project** using the
  `sensitivity_centered_phase` block — graph pipelines, Data Maker exports, SIR
  prep — used the defective coordinate.

**Would fixing it change existing transformed data?** Yes, completely. Not a
refinement: median correlation between old and new output is ≈ 0. Any number,
plot, fitted model, or discovered relation that passed through the Dalia block
would change qualitatively.

**Do manuscript numbers need rerunning?** Depends entirely on provenance, and
this is the open question I could not close from the code alone:

- The project's SIR settings (`module_settings.sir`) show `dataProcessing =
  [x, dx, xPhaseder, yPhaseder]`, target `pcdiamag3`, and `prepSteps =
  [sir_feature_zscore, sir_nmin]`. The **prep steps do not include
  `sensitivity_centered_phase`**, and the sole saved grapher pipeline uses
  `normalize_zscore`, not the phase block.
- On that evidence, the last recorded Dalia SIR run (`activeRunId
  20260814-113126-fabf`) did **not** route through the defective block, and the
  phase-derivative content came from SIR's own `xPhaseder/yPhaseder` path.
- **This needs your confirmation.** If any figure or table was produced by
  adding the "Sensitivity-centered reference-shifted phase" transform in a graph
  or Data Maker export — which leaves no trace in the saved project document —
  that output is invalid and must be regenerated.

---

## 6. Recommended fix for Dalia (NOT applied)

Replace `reference_shifted_phase` + `sensitivity_centered_phase` in the project
`transforms.py` so that:

1. `_fit_clearance` divides by the fitted rate scale **before** taking the min —
   or, better, takes the already-normalized samples as its argument.
2. `reference_shifted_phase` returns `(u + s_eff) * g` with
   `g = w/(w²+rho²)`, `w = v + s_eff`.
3. `sensitivity_centered_phase` computes a **cohort-fitted, cached** `g_bar`
   (mirroring `_scale_cache`) and returns `C_RS - g_bar * u`, never `nanmean`.

Items 1–2 also affect **`level_rate_relational`**, which shares
`_fit_clearance(..., is_rate=True)` and the unshifted `_regularized_ratio`. It
has the same units defect and should be fixed in the same pass. `conditioning_aware`
and `tangent_direction` do not use a clearance and are unaffected.

Nothing in the Dalia project has been modified.

---

## 7. Changes made to the figure code (Task 1)

`Figures/lift_map.py`
- Rewrote the phase block: added `regularized_denominator_gain`,
  `reference_shifted_ratio`, `sensitivity_centered_ratio`.
- `PhaseParams` now carries `scale_n, scale_d, s_0, s_eff, g_bar`
  (was `scale_u, scale_v, s_eff, mean`).
- `fit_phase_params` fits `s_0` on the **normalized** denominator and fits
  `g_bar = mean(g)`.
- `sensitivity_centered_phase` returns `(u_n+s_eff)·g − g_bar·u_n`.
- `d_sensitivity_centered_phase_dt` implements the analytic derivative
  `u̇_n(g−g_bar) + (u_n+s_eff)·ġ`, `ġ = u̇_d(rho²−w²)/(w²+rho²)²`.
- Orientation pinned to named aliases `_numerator_rate = dx1_dt`,
  `_denominator_rate = dx2_dt`; axis symbol derived from a single
  `PHASE_LABEL` so it cannot drift from the math.
- Label corrected `D^sc_{ẋ1 ẋ2}` → `D^sc_{x_2} x_1` (the old two-subscript
  form is not valid in the paper's notation).

`Figures/lift_map_reveal.py`
- Imports `PHASE_LABEL`; z-label and title formula corrected the same way.
- Reports all fitted quantities and per-crossing rate-space points + `D_sc`.

`Figures/test_sensitivity_centered_phase.py` — new, **97 tests, all passing**.

Fitted values on the analytical trajectory:
`S_n=3.307489, S_d=3.416106, rho=0.1, kappa=1.0, s_0=1.516972,
s_eff=2.516972, g_bar=0.457921`.

| Crossing | `(ẋ1,ẋ2)` at `t_i` | `D_sc` | `(ẋ1,ẋ2)` at `t_i+π` | `D_sc` | `|ΔD|` |
|---|---|---|---|---|---|
| A | (−5.3069, −0.6649) | 1.126917 | (−3.7220, 2.9289) | 0.927367 | 0.199550 |
| B | (−1.5399, −2.0360) | 1.278203 | (2.9856, −4.5179) | 2.429648 | 1.151445 |
| C | (4.0417, −0.5906) | 1.032583 | (5.0991, −3.3940) | 1.946753 | 0.914170 |
