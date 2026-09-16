# Audit — Dalia transform family, DIIID_SIR_Paper

**Date:** 2026-08-25
**Project:** `DIIID_SIR_Paper` · `36a4813a-23b1-4c9f-abc3-592f98b4abe2`
**Scope:** all seven registered transform blocks, verified three ways —
intended design vs canonical Archaieus vs the Dalia runtime.

**Outcome:** 4 transforms repaired, 3 left unchanged. All four relational
transforms now agree with Archaieus to floating-point precision on the real
62-shot cohort. **Two items are flagged STOP and were deliberately not
changed** (§8).

---

## 1. Notation

    D_g f = (df/dt) / (dg/dt)

The subscript is the **reference (denominator)**; the operand follows it.
`D_{x2} x1 = (dx1/dt)/(dx2/dt)`. There is no two-subscript form. A
superscript marks the variant, e.g. `D^{sc}_{x2} x1`.

---

## 2. Project authority and provenance

Three copies of the project document exist, with **independent version
counters** — the version number alone does not establish authority:

| Copy | Version before | `transforms.py` sha256 (pre-fix) |
|---|---|---|
| Live Dalia server | 146 | `1c0722e673307250` |
| `.dalia/projects/…json` | 134 | `1c0722e673307250` |
| `DIIID_example/.dalia/projects/…json` | 165 | `1c0722e673307250` |

All three carried **byte-identical** transform code. An apparent size
difference (live reported 15 723 bytes vs 15 701 on disk) is UTF-8 byte count
vs Python character count — exactly 22 multibyte characters (7 `•`, 1 `…`,
2 `—`, `ρ`, `κ`). The version numbers had diverged through layout/settings
edits, not code.

**Backups taken before any modification:**

    .dalia/backups/36a4813a_v134_20260825_prefix.json
    .dalia/backups/36a4813a_bundle_v165_20260825_prefix.json

The pre-fix implementation is also preserved verbatim as
`DIIID_example/_dalia_prefix_transforms.py`.

**Versions after modification:**

| Copy | After | How |
|---|---|---|
| Live Dalia server | **147** | `save_provider_file` (undo available in Dalia) |
| `.dalia/projects/…json` | **135** | deliberate sync, `transforms.py` only |
| `DIIID_example/.dalia/projects/…json` | **166** | deliberate sync, `transforms.py` only |

The live server **does not persist to either on-disk copy** — after the live
save to v147, both disk files were still pre-fix. Its store is outside
`D:\SIR_paper`. The two disk copies were therefore synchronized explicitly,
updating **only** `files["transforms.py"]` and incrementing the version;
layout, settings, labels and the other 11 files were left untouched, and both
copies were re-verified to compile.

The Dalia backend at `D:\dalia` was not modified.

---

## 3. Where the math actually lives

`DIIID_example/` has **no** `data_provider.py` and **no** `transforms.py` of
its own; both exist only inside the project document. The embedded
`data_provider.py:241` registers the blocks via
`"custom_transform_dictionary": build_transforms(data_folder)`. The
`blocks/*.py` files are thin re-exports (699–726 bytes each) via
`blocks/_shared.py`.

The historical sir-web provider does **not** contain the math: it only passes
`normalization_mode=mode` into `Dataset_Constructor`
(`diiid_elm_data_provider.py:620`). The canonical implementations are in
Archaieus.

### Source locations

| Transform | Archaieus | Dalia (project `transforms.py`) |
|---|---|---|
| Per-realization Z | `consumer_function.py:309` `zscore(x, axis=-1)` | `per_realization_zscore` |
| Per-channel Z | `utils/channel_normalization.py:134,182` | `per_channel_zscore`, `_fit_channel_z` |
| Conditioning-aware | `conditioning_consumer.py:566` (`_build_physical_quotients`, level/level), `:868` (x-phase, rate/rate), `:1251` (y-phase, level/rate); ratio `utils/conditioning_aware.py:202` | `conditioning_aware`, `_fit_ratio_z` |
| Level-rate relational | `conditioning_consumer.py:1139-1174`, `:818-831` | `level_rate_relational` |
| Reference-shifted phase | `conditioning_consumer.py:1151-1174`, `:818-834`; ratio `utils/conditioning_aware.py:226` | `reference_shifted_phase` |
| Sensitivity-centered phase | `conditioning_consumer.py:1013-1032`, `:758-774`; kernel `utils/conditioning_aware.py:257`; `g_bar` `:277` via `_mean_gain_for:330` | `sensitivity_centered_phase`, `_fit_mean_gain` |
| Tangent-direction | `utils/conditioning_aware.py:331`; drivers `conditioning_consumer.py:712-756` (rate/rate), `:916-939` (level/rate) | `tangent_direction` |

Shared machinery: operand scales `utils/conditioning_aware.py:92-199`;
clearance `:210`; gain `:246`; shared post-coordinate Z
`conditioning_consumer._complete_one:472`.

**Pipeline note.** Archaieus applies a third stage after every coordinate — a
cohort-fitted, frozen shared Z (`_complete_one` → `apply_channel_stat`). The
Dalia blocks emit the **pre-Z coordinate** (Archaieus' `C_pre_z`), which is
the quantity under audit; in Dalia the shared Z is the separate SIR prep step
`sir_feature_zscore`. `conditioning_aware` is the one block that historically
carried its own Z — see §5.3.

---

## 4. Formulas

With `u_n = n/S_n`, `u_d = d/S_d` (**normalize first**),
`s_0 = max(0, -min_fit(u_d))`, `s_eff = s_0 + kappa`, `w = u_d + s_eff`,
`g = w/(w² + ρ²)`:

| Transform | Formula | Numerator | Denominator |
|---|---|---|---|
| Per-realization Z | `(x - μ_r)/σ_r`, record-local | — | — |
| Per-channel Z | `(x - μ_ch)/σ_ch`, cohort-frozen | — | — |
| Conditioning-aware | `Z[ u_n·u_d/(u_d² + ρ²) ]` | level | level |
| Level-rate relational | `(u_n + s_eff)·g` | **level** | rate |
| Reference-shifted phase | `(u_n + s_eff)·g` | **rate** | rate |
| Sensitivity-centered phase | `(u_n + s_eff)·g − ḡ·u_n` | rate | rate |
| Tangent-direction | `(T_n,T_d) = (u_n,u_d)/√(u_n²+u_d²+ρ²)` | level* | level* |

`ḡ = mean_fit[g]`, frozen. Defining property `mean_fit(g − ḡ) = 0`.
\* flagged — see §8.

**Level-rate vs reference-shifted phase share the same formula.** Archaieus
states this explicitly as the "CRITICAL SEMANTIC SPLIT of the target-phase
numerator" (`conditioning_consumer.py:1132-1136`): the only difference is the
numerator operand — scaled level `y_raw` vs scaled `dy/dt`. They are not the
same coordinate and their units differ; the shared helper does not make them
interchangeable.

---

## 5. Three-way comparison

| # | Transform | Intended | Archaieus | Dalia pre-fix | Dalia post-fix | Verdict |
|---|---|---|---|---|---|---|
| 1 | Per-realization Z | record-local `(x-μ_r)/σ_r` | same | same | unchanged | **MATCH** (degenerate policy differs, §5.1) |
| 2 | Per-channel Z | cohort-pooled, frozen | same | same | unchanged | **MATCH** (zero-variance policy differs, §5.2) |
| 3 | Conditioning-aware | `Z[reg ratio]`, frozen Z | same | **per-record Z** | frozen cohort Z | **FIXED** — was semantic |
| 4 | Level-rate relational | `(u_n+s_eff)·g`, `s_0` on normalized | same | raw `s_0`, unshifted numerator | corrected | **FIXED** — was scientifically material |
| 5 | Reference-shifted phase | `(u_n+s_eff)·g`, `s_0` on normalized | same | raw `s_0`, unshifted numerator | corrected | **FIXED** — was scientifically material |
| 6 | Sensitivity-centered phase | `C_RS − ḡ·u_n`, ḡ frozen | same | 4 defects | corrected | **FIXED** — was scientifically material |
| 7 | Tangent-direction | `(u_n,u_d)/R` | same kernel | **level/level operands; only T_n emitted** | unchanged | **STOP** — §8.1 |

**A == B for all seven.** No case was found where Archaieus contradicts the
intended design, so the "stop before changing either" rule was not triggered
on that axis.

### 5.1 Per-realization Z — intentionally record-local
Archaieus `zscore(x, axis=-1)` under `total_normalization`. Statistics come
from that realization alone, and applying to a new realization deliberately
computes **new** local statistics. This is the design, and the one place in
the family where per-record fitting is correct: it removes shot-to-shot gain
and offset so only within-shot shape survives. Dalia matches.
*Divergence (documented, not changed):* Dalia returns zeros for a constant
record and ignores NaNs when estimating μ/σ; `scipy.stats.zscore` yields
NaN/Inf and propagates NaNs. Visible only on constant or NaN-bearing records.

### 5.2 Per-channel Z — cohort-pooled and frozen
"Channel" = one semantic signal (`ip`, `q95`, …); μ/σ pooled over **both**
time and every training realization, one pair per signal, then frozen.
Formula matches exactly (`ddof=0`).
*Divergence (documented, not changed):* on a constant channel Archaieus
**raises**; Dalia substitutes `std = 1.0`. Dalia's behaviour keeps a GUI plot
alive; Archaieus' refuses to fabricate a Z-score. Not scientifically material
for any non-degenerate channel.

### 5.3 Conditioning-aware — operands correct, Z was leaking
The Dalia block's level/level operands are **correct**: they mirror Archaieus'
`_build_physical_quotients` (`:566`), which scales `x_raw` by
`get_scale("level", …)` and forms `regularized_ratio`. (Archaieus also has
rate/rate and level/rate variants of the same kernel in other branches.)
The defect was the trailing `_zscore_local` — a **per-record** z-score where
Archaieus uses a cohort-fitted frozen one, so training and held-out records
passed through different affine maps. Now `_fit_ratio_z`, cohort-fitted and
cached.
*Simplification (documented):* Dalia always uses the regularized branch;
Archaieus can certify an exact ratio under `policy="auto_certified"`. Dalia
corresponds to `regularized_all`.

---

## 6. Bugs found

| # | Bug | Transform(s) | Class |
|---|---|---|---|
| B1 | Clearance `s_0` computed from the **raw** rate, then added to a **normalized** rate | level-rate, reference-shifted, sensitivity-centered | **scientifically material** |
| B2 | Numerator not reference-shifted: `u_n·g` instead of `(u_n + s_eff)·g` | level-rate, reference-shifted, sensitivity-centered | **scientifically material** |
| B3 | Ordinary mean-centering `C_RS − mean(C_RS)` instead of `C_RS − ḡ·u_n` | sensitivity-centered | **scientifically material** |
| B4 | Centering constant re-estimated **per record** | sensitivity-centered | **scientifically material** (train/apply leak) |
| B5 | Conditioning-aware ratio z-scored **per record** | conditioning-aware | **semantic** (train/apply leak) |
| B6 | `_fit_rate_scale` bypassed `_scale_cache` — recomputed over 62 shots on every call | all rate-based | **numerical/perf** (no output change) |
| B7 | `robust_zero_mad` returned `min_scale` on a degenerate MAD instead of falling back to pooled RMS | all, when `scale_method=robust_zero_mad` | **numerical** |

### Why B1 is severe
On the real cohort the `ip` rate has magnitude ~10⁵ A/s while `u_d` is O(1)–
O(100) by construction. The raw clearance made `s_eff` **3836× too large**
(445 179 vs 116.039). Then `w = u_d + 445179 ≈ 445179`, so `g` was constant to
2×10⁻⁶ relative spread and the coordinate collapsed to an affine rescaling of
the numerator — `|corr(output, u_n)| = 1.00000000` on **every** shot.

---

## 7. Fixes applied

All in the project-embedded `transforms.py` (live v146 → v147):

1. **`_fit_clearance_normalized`** (new) — fits `s_0` on `u_d = rate/scale`,
   cohort-pooled and cached. Replaces `_fit_clearance`. *(B1)*
2. **`_clearance_shifted_ratio`** (new) — `(u_n + s_eff)·g(w)`, with
   `_denominator_gain` factored out. Used by level-rate and both phase
   transforms. *(B2)*
3. **`sensitivity_centered_phase`** — now `C_RS − ḡ·u_n`. *(B3)*
4. **`_fit_mean_gain`** (new) — `ḡ` pooled over the cohort and cached in
   `_gbar_cache`, so held-out records reuse the training constant. *(B4)*
5. **`_fit_ratio_z`** (new) — cohort-fitted frozen z-stats for the
   conditioning-aware ratio. *(B5)*
6. **`_fit_rate_scale`** — now uses `_scale_cache` under a `d1_` key. *(B6)*
7. **`_robust_zero_mad`** — falls back to pooled RMS on a degenerate MAD,
   matching `conditioning_aware.fit_robust_zero_mad`. *(B7)*

Untouched: `per_realization_zscore`, `per_channel_zscore`,
`tangent_direction`, and all block keys, display names and parameter schemas
(so existing pipelines keep loading).

---

## 8. STOP items — deliberately not changed

### 8.1 Tangent-direction operands
Dalia forms the tangent pair from **level/level**. Archaieus forms it from
**rate/rate** (`conditioning_consumer.py:716`, operands `s["dx"]`) or
**level/rate** (`:922`, operands `uT`/`v`) — never level/level.

Geometrically the rate/rate form is the one that deserves the name: the
tangent to a trajectory in the `(x_i, x_j)` plane *is* `(dx_i, dx_j)`. With
levels the block returns the direction of the position vector, not a tangent.

This is a material change to what the coordinate means, so it is reported
rather than guessed. **Which operand pair should the Dalia block use?**

### 8.2 Tangent-direction drops a component
Archaieus emits **both** `T_n` and `T_d` as separate coordinates
(`td_num_*`, `td_den_*`). Dalia returns only `T_n`. They are not redundant:
together they fix the direction, and their common shrinkage
(`T_n² + T_d² < 1`) encodes proximity to a stagnation point. Recommend adding
a `component` parameter (`numerator` / `denominator`); the reference
implementation already exposes one.

Neither item affects the four repaired transforms.

---

## 9. Verification

### 9.1 Regression suite — `Figures/test_dalia_transform_family.py`
**71 tests, all passing.** Loads all three implementations and compares them.
Archaieus is loaded by file path because `Archaieus.sir.__init__` pulls the
whole SIR stack (`xlsxwriter`), which need not be installed.

Covers: math kernels vs closed-form intended expressions and vs Archaieus over
5 `(ρ,κ)` settings; the `mean_fit(g − ḡ) = 0` property; explicit proof that
mean-centering is *not* being substituted; `ḡ = 0` reducing to `C_RS`; block
outputs driven through the real Dalia fit/apply plumbing on three synthetic
cohorts (smooth, denominator turning point, mixed channel scales) × 3 `(ρ,κ)`;
frozen-`ḡ` and frozen-CA-Z checks; the collapse guard; record-local vs frozen
Z semantics; operand-rescaling invariance; degenerate inputs (zero variance,
zero MAD, all-zero, NaN locality, infinities, empty); rejection of negative
`s_eff` and of unfitted `ḡ`; and held-out application with frozen parameters.

Tolerance `rtol=0, atol=1e-12` wherever the formulas should be identical.

**The suite discriminates.** Pointed at the pre-fix implementation it produces
**31 failures**; pointed at the corrected one, **0**.

*(One nuance: the collapse guard passes on synthetic cohorts because their
denominators are O(1), so raw ≈ normalized clearance. The collapse needs a
denominator whose physical scale is far from 1 — which is why the real-cohort
check below matters.)*

### 9.2 62-shot DIII-D cohort — `DIIID_example/verify_transforms_62shot.py`
Numerator `pcdiamag3`, denominator `ip`, `ρ=0.1, κ=1.0, pooled_rms`;
330 055 finite samples per transform.

| Transform | worst max abs diff | worst RMS diff | min corr | verdict |
|---|---|---|---|---|
| reference_shifted_phase | 7.105e-15 | 1.384e-16 | 1.000000000000 | agree to float precision |
| level_rate_relational | 1.776e-15 | 1.097e-16 | 1.000000000000 | agree to float precision |
| sensitivity_centered_phase | 0.000e+00 | 0.000e+00 | 1.000000000000 | agree to float precision |
| tangent_direction | 0.000e+00 | 0.000e+00 | 1.000000000000 | agree to float precision |

Fitted: `S_n=0.186886`, `S_d=3869.81`, `s_0=115.039`, `s_eff=116.039`,
`ḡ=0.00861813`. Pre-audit `s_eff` was 445 179 — **3836.5×** larger.

**The headline regression, reproduced and resolved** — `|corr(output, u_n)|`:

| | median | min | max |
|---|---|---|---|
| pre-audit | 1.0000000000 | 0.9999999999 | 1.0000000000 |
| corrected | **0.0388573258** | 0.0017062274 | 0.2891322203 |

Centering property on the real cohort: `mean_fit(g − ḡ) = 5.706e-19`.

### 9.3 Live verification
`check_syntax` clean; `reload_provider` → `Loaded provider
dataset_id=diiid_elm_sir_paper`; `preview_transform` on shot 155537 returns
198 finite samples with mean `3.19e-8` — no longer identically zero-mean,
confirming the per-record centering is gone.

---

## 10. Provenance — what may need regenerating

**Unaffected.** Anything produced through **sir-web / Archaieus** —
`canonical_d3d_62_shot_run_v1`, the DIII-D Ip reconstruction studies, and the
other dated study folders — used the correct implementation throughout. No
Archaieus-side defect was found in any of the seven transforms.

**Affected.** Any output produced through the **Dalia** `DIIID_SIR_Paper`
project using `sensitivity_centered_phase`, `reference_shifted_phase`,
`level_rate_relational`, or `conditioning_aware` **with a denominator**. For
the three relational transforms the change is qualitative, not a refinement:
old and new outputs have median correlation ≈ 0.

**Current evidence says no manuscript number is affected, but this needs your
confirmation.** The saved project shows `prepSteps = [sir_feature_zscore,
sir_nmin]` and a single grapher pipeline using `normalize_zscore`. Neither
routes through a defective block, so the last recorded SIR run
(`activeRunId 20260814-113126-fabf`) appears clean, with phase-derivative
content coming from SIR's own `xPhaseder`/`yPhaseder` path.

The gap: a transform added ad hoc in a graph or a Data Maker export leaves no
trace in the saved project document. **If any figure or table was produced
that way, it is invalid and must be regenerated.** Only you can close that.

Figures already regenerated from corrected code: `Figures/lift_map.py` and
`Figures/lift_map_reveal.py` (previous audit).

---

## 11. Deliverables

| Path | What |
|---|---|
| `DIIID_example/transforms.py` | Standalone documented reference implementation |
| `DIIID_example/_dalia_runtime_transforms.py` | Importable mirror of the Dalia runtime (test target) |
| `DIIID_example/_dalia_prefix_transforms.py` | Pre-fix implementation, preserved |
| `DIIID_example/verify_transforms_62shot.py` | Real-cohort consistency check |
| `Figures/test_dalia_transform_family.py` | 71-test regression suite |
| `.dalia/backups/*.json` | Pre-fix project documents |
| `AUDIT_dalia_transform_family.md` | This report |

---

## 12. Architecture recommendation

**Keep the Dalia runtime as a separately tested mirror. Do not make it import
the standalone reference.**

The Dalia project executes inside its own worker sandbox with the project
document as the unit of persistence and distribution. Importing
`D:\SIR_paper\DIIID_example\transforms.py` at runtime would couple a
scientific project to an absolute path on one workstation: the project would
stop being self-contained, would break whenever it is opened from a different
checkout or machine, and would fail silently into a stale copy if the path
resolved somewhere unexpected. Importing Archaieus directly is worse — it
would bind the project to a development checkout of a submodule.

The divergence risk is real but is better handled by testing than by coupling.
That is what is now in place: `Figures/test_dalia_transform_family.py` pins
the runtime mirror against both Archaieus and the reference at `atol=1e-12`,
and `verify_transforms_62shot.py` re-checks on real data. Two cheap habits
keep it honest:

1. run both after any edit to the project `transforms.py`;
2. keep `_dalia_runtime_transforms.py` a byte-copy of the project file — the
   suite is only meaningful if the mirror is current.

If drift is still a concern later, the sound fix is to vendor the shared math
**into** the project document as a `blocks/_math.py` module that the runtime
imports and the tests import too — self-contained, no absolute paths, one
copy of the formulas.
