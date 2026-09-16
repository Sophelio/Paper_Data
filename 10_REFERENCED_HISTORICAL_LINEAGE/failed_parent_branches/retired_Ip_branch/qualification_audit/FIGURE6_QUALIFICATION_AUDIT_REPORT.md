# Figure 6 qualification audit — DIII-D

**Date:** 2026-09-01
**Audit IDs:** `D3D-FIG6-PROVENANCE-AUDIT-V1`,
`D3D-FIG6-CORRECTED-UNIVERSE-PROBE-V1`
**Scope completed:** Audit A (target provenance) and an unplanned but decisive
evaluation-protocol check. **Audits B–L were not completed** — see §19.

---

## 1. Executive verdict

**q_rec (I_p reconstruction) is NOT figure-ready. Two independent findings each
suffice to retire it.**

| # | Finding | Verdict |
|---|---|---|
| 1 | **Target-provenance leakage.** 6/10 REL10 and 4/10 RAW10 features carry upstream I_p dependence. `q95` is very nearly the algebraic function `shape·a²B_t/I_p` in this archive. | `RESULT_RETIRED` |
| 2 | **No demonstrated skill over a trivial baseline.** A constant persistence predictor achieves median normalised RMSE **0.0685** on the protected final 20%, beating REL141 (0.1137), REL10 (0.1257) and RAW10 (0.1821). | `CORRECTION_REQUIRED` |

**q_desc is not affected by finding 1** — it is explicitly a target-containing
descriptive closure, so target-dependent coordinates are admissible by design.
Its audits (B, H–L) remain outstanding.

**Nothing canonical was modified.** All new work is in
`Figure6_qualification_audit/` and `fig6data/`.

---

## 2. Frozen inputs and run identity

**The DIII-D canonical tree is not under `D:\SIR_paper\`.** It is at

    D:\sir-web\Paper Examples\Relational Coordinates for Multimodal Plasma Observations\

containing `canonical_d3d_62_shot_run_v1/`, `Coefficient_conditioning/`,
`Implicit_elimination_and_denominator_conditioning/`, `DIII-D Ip relational
discovery/`, `DIII-D Ip relational reconstruction 62-shot confirmation/`, and
others. `D:\SIR_paper\DIIID_example\` holds the 62-shot source data and three
frozen summary exports only:

| Artifact | Role |
|---|---|
| `Figure_data/d3d_description_support.csv` | the 7 q_desc coordinates |
| `Figure_data/d3d_reconstruction_external_55.csv` | 55-discharge external table |
| `Figure_data/d3d_reconstruction_summary.json` | pooled q_rec summary, run id `D3D-SIR-62-ALIGNED-V1` |
| `data/resampled_data_v6/` | 62 shots, 95 signals each |

The summary's `source_lineage` points back into the sir-web tree, confirming
`DIIID_example` holds derived exports rather than primary run artifacts.

---

## 3. Dalia-native vs audit-harness

| Operation | Classification |
|---|---|
| DIII-D signal serving, transform family | `DALIA_NATIVE` (project `DIIID_SIR_Paper`) |
| Provenance-lineage tracing | `AUDITED_EXTERNAL_ANALYSIS` — Dalia exposes no provenance-lineage primitive |
| Empirical dependence tests, feasibility probe, baselines | `AUDITED_EXTERNAL_ANALYSIS` |

The audit reads the same archived NPZ inputs Dalia serves. No Python-side
surrogate is presented as Dalia-native.

---

## 9. q_rec provenance audit — `CORRECTION_REQUIRED` / `RESULT_RETIRED`

### Documentary provenance is unavailable

Shot metadata records only resampling `method` and `category` (e.g.
`cubic_spline`, `smooth_high_snr`). **No physical provenance, formula, or
upstream diagnostic lineage is archived.** Documentary provenance therefore
could not establish independence, and the conservative rule applies.

### Empirical dependence test

The archive contains `aminor`, `bt`, `area`, which permits testing the textbook
definitions directly (62 discharges):

| Signal | median \|corr\| with I_p form | rel. scatter after removing I_p | Verdict |
|---|---|---|---|
| `q95` | **0.945** (vs 1/I_p) | **7.3%** | **TARGET_DEPENDENT** |
| `betan` | 0.664 (vs 1/I_p) | 47.5% | **TARGET_DEPENDENT** |
| `li` | 0.393 | — | **PROVENANCE_UNRESOLVED** → conservatively dependent |
| `kappa` | 0.483 | — | **PROVENANCE_UNRESOLVED** → conservatively dependent |
| `pcdiamag3` | 0.506 | — | TARGET_INDEPENDENT |
| `pinj` | 0.695 | — | TARGET_INDEPENDENT |
| `density` | 0.746 | — | TARGET_INDEPENDENT |

`q95` is the severe case: removing I_p algebraically via `q95·I_p/(a²B_t)`
leaves only **7.3%** relative scatter, i.e. `q95` *is* essentially
`shape·a²B_t/I_p` in this archive. An inversion test recovers I_p from
`a²B_t/q95` with a single per-shot scale factor at **median R² = 0.79**
(R² > 0.9 on 15/62 discharges). Reconstructing I_p from `q95` is therefore close
to algebraic circularity.

`betan = β_t·a·B_t/I_p` contains I_p explicitly. `li` and `kappa` are EFIT
outputs and EFIT is constrained by the measured I_p; no archived record severs
that dependence.

### A methodological correction inside this audit

The first version of the verdict logic treated **statistical correlation** with
I_p as evidence of **ancestry**, which wrongly condemned `pcdiamag3`, `pinj` and
`density` (|corr| 0.51–0.75) and would have made every reconstruction task
inadmissible. Ancestry is definitional/computational, not statistical: those
three are direct diagnostics (diamagnetic loop, beam power, interferometer) that
co-evolve with I_p within a discharge. Corrected; correlation is now reported as
context only. This correction is recorded rather than silently patched.

### Decision gate

| Representation | Leaking features |
|---|---|
| REL10 | **6/10** — `PROD_pcdiamag3_q95`, `L_q95`, `PROD_q95_li`, `CU_li`, `CU_q95`, `L_kappa` |
| RAW10 | **4/10** — `Z_q95`, `L_q95`, `Z_kappa`, `L_kappa` |

**GATE FAILED.** Both the relational representation and its comparator are
contaminated, so the reported "REL10 beats RAW10 on 46/55" is a comparison
between two leaking representations and cannot be interpreted as evidence for
relational structure.

### Corrected admissible universe

Only `{pcdiamag3, pinj, density}` survive. A fair probe over 24 derived
coordinates from those three (levels, derivatives, cubics, lags 1–2, products,
regularised ratios, derivative-ratios), same 80/20 protocol, calibration-only
scaling, ridge chosen inside calibration:

| | median normalised RMSE | median R² | frac R² > 0 |
|---|---|---|---|
| naive linear on 3 raw levels | 0.4210 | −25.60 | 0.000 |
| 24 relational coordinates | **0.2001** | −3.00 | 0.016 |

This is a **feasibility probe, not a corrected q_rec result** — no
development-cohort selection, no frozen support. It establishes only that a
corrected universe is far weaker, not that the task is impossible.

---

## 10-13. Evaluation-protocol check — `CORRECTION_REQUIRED`

This was not on the requested list; it emerged from the R²/RMSE disagreement in
the probe and is decisive.

On the protected final 20% of each discharge:

| Predictor | median normalised RMSE |
|---|---|
| **persistence (last calibration value, constant)** | **0.0685** |
| calibration mean (constant) | 0.4430 |
| REL141 (reported) | 0.1137 |
| REL10 (reported) | 0.1257 |
| RAW10 (reported) | 0.1821 |
| corrected-universe probe | 0.2001 |

**A constant predictor beats all three reported models.** The cause is
structural: `var(evaluation) / var(calibration)` has median **0.0032** — the
final 20% carries about 0.3% of the calibration-segment variance, because it
sits in current flat-top termination or ramp-down. Normalising RMSE by the
calibration scale makes all numbers look small while the segment is nearly
constant.

**Caveat:** my baseline uses the `ip` time base with an index-based 80/20 split
and may not match the frozen study's mask, normalisation or resampling exactly.
The numbers are **indicative and require exact-protocol confirmation** before
being quoted. The variance ratio, however, is a property of the data and holds
regardless.

**Consequence:** no q_rec skill claim is currently supported. Any corrected
experiment must report skill against persistence, not only normalised RMSE.

---

## 15. Retired claims

| Claim | Status |
|---|---|
| "REL10 beats RAW10 on 46/55 external discharges" | **RETIRED** — both representations leak |
| "pooled RMSE REL141 0.114 / REL10 0.126 / RAW10 0.182" | **RETIRED** — leaking, and worse than persistence |
| "REL141 ≈ 99 effective DoF, REL10 ≈ 10.6" | **UNVERIFIED** — not reproduced from primary artifacts |
| "target-free I_p reconstruction" | **RETIRED** — the universe was not target-free |
| "structural transfer improves reconstruction" | **RETIRED** pending a corrected, skill-referenced experiment |

Preserved, not patched: `Figure_data/d3d_reconstruction_summary.json` is
unmodified and now carries the status `RETIRED_FOR_PROVENANCE_LEAKAGE` in
`fig6data/RETIREMENT_RECORD.json`.

---

## 19. Audits not completed

**Audits B–L were not run.** Specifically: q_desc reproduction, numerical-
realization stability (aligned/spline/RTS), coefficient conditioning and TSVD
truncation, individual coefficient qualification (REML + moving-block
bootstrap), multivariate eigenspectrum with matched null, implicit-elimination
conditioning, RAW10 fairness beyond provenance, common-support scoring, paired
55-discharge statistics, and effective-DoF reproduction.

Reason: they require the primary run artifacts in the sir-web canonical tree,
and the q_rec audits among them are moot until a corrected experiment exists.
The q_desc audits (H–L) are **independent of the provenance failure** and remain
the most promising surviving Figure 6 material.

---

## 20. Regeneration

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
& $P Figure6_qualification_audit\provenance\run_provenance_audit.py
& $P Figure6_qualification_audit\provenance\corrected_universe_probe.py
```

Seeds fixed at 20260901; both scripts are deterministic. Outputs land in
`fig6data/` and `Figure6_qualification_audit/`.
