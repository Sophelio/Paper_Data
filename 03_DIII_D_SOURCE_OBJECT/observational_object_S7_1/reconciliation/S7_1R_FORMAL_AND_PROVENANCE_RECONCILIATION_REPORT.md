# S7.1R — Formal and Provenance Reconciliation

**Stage:** S7.1R (addendum to S7.1) · **Date:** 2026-09-02
**Scope:** four issues raised against S7.1, plus a mandated reassessment of U001.
**Status:** `COMPLETE_PENDING_HUMAN_REVIEW`

No target was selected. No coordinates, ontology, or `G_rec` were generated. No
regression was run. No reconstruction performance was inspected. S7.2 is not
authorised and is not begun.

---

## Executive summary

Four issues were opened against S7.1. Three are now closed and one is closed with
a residual. Along the way the pass turned up five properties of the observational
object that S7.1 could not have found, because they live in the *metadata* rather
than in the data — and S7.1 was reading the metadata for the wrong thing.

| # | Issue | Outcome |
|---|---|---|
| 1 | Formal meaning of `A` in `O` | **CLOSED** — authoritative local artifact found; S7.1 reading corrected; `A` is `PARTIALLY_INSTANTIATED` |
| 2 | Units for all 95 signals | **CLOSED with residual** — 0 locally verified, 94/95 recoverable externally, 1 refuted |
| 3 | Equilibrium lineage (15 quantities) | **CLOSED as negative** — all 15 `LINEAGE_PARTIAL`; none resolvable locally |
| 4 | The 20 ms temporal grid | **CLOSED** — Outcome C; both numbers real, belonging to different providers |
| 5 | U001 upstream resampling gap | **RECLASSIFY** `CRITICAL` → `MAJOR (conditional)` |

The single most consequential result is not on that list. It is that **the
cohort is not homogeneous**: upstream processing of `ip` changes cleanly at shot
189646, and three other signals vary likewise. Any later claim of cross-discharge
generality now has to contend with a known processing discontinuity that
coincides with a campaign boundary.

---

## 1. Issue 1 — the formal meaning of `A`

**S7.1 read `A` as admissibility and recorded it `NOT_INSTANTIATED`.** That
reading is wrong, and an authoritative local artifact settles it.

`D:\SIR_paper\General\sir_representational_prism.py` is the manuscript's own
visual-abstract figure generator. It draws the scientific object `𝒪` and the task
contract `q` as **separate boxes**, and lists the contract's attributes as
exactly:

> **Admissibility · Information · Intended Use**

Admissibility is an attribute of `q`. It is not a component of `𝒪`.

`A` is therefore re-read as **ancillary observational information** — annotations
and metadata carried by the object, not a task-conditioned rule. This matches the
working semantics supplied in the S7.1R specification, and is now backed by local
evidence rather than assumed.

No prose artifact states the 6-tuple; `SIR_paper_orig.pdf` predates the Section
1.1 architecture entirely. The figure source is `LOCAL_DOCUMENTED`, not
`CODE_VERIFIED`, and a prose definition in the current manuscript would supersede
it. **That search should still be completed before S7.2.**

### `A` is `PARTIALLY_INSTANTIATED`

Under the corrected reading `A` is far from empty. The object carries **5890
per-signal ancillary records** (62 × 95), each giving the upstream resampling
`method` and `category` and the original and resampled sample counts — plus
signal-group membership for all 95, cohort provenance flags for all 62, and shot
identifiers.

Absent: units, uncertainty, calendar dates, campaign identifiers, regime labels,
operator commentary — and, despite the archive being an ELM dataset, **any ELM
event annotation whatsoever**. The 190 keys per shot are exactly `<signal>_data`
and `<signal>_times`.

Detail: `O_COMPONENT_A_ADDENDUM.md`. Applied to the S7.1 artifacts by addendum;
the original `A` block is preserved in `O_DIIID.json` under
`_s7_1_original_A_admissibility`.

---

## 2. Issue 2 — units

| Evidence class | n |
|---|---|
| `CODE_VERIFIED` / `LOCAL_DOCUMENTED` | **0** |
| `AUTHORITATIVE_EXTERNAL` | 8 |
| `STRONGLY_INFERRED` | 86 (74 magnitude-corroborated) |
| `UNRESOLVED` | 1 |

**No unit is locally verified for any of the 95 signals**, and this is not a
search failure. The one function whose job is to report units, `_units_for()`,
returns a blank data unit *by design*, because the exported columns are z-scored.
Nine local source classes were searched, including any local MDSplus or OMFIT
metadata, which do not exist in this environment.

Units were recovered from standard DIII-D pointname conventions and then **tested
against the project's own data**. The test is a falsifier, not a fitter: a
hypothesis whose observed magnitude falls outside its physically expected band is
*withdrawn*, never rescaled to fit. Three results changed:

1. **`pinj_*` is stored in W while `pinj` is stored in kW.** The eight per-beam
   channels read ~1.4–2.2 × 10⁶ against an aggregate of ~9.25 × 10³. Under a
   common unit the parts exceed their own sum by ~1000×; under W-and-kW they add
   (Σ ≈ 10.5 MW vs 9.25 MW). This one rests on **additivity inside the project's
   own data**, which is stronger than convention.

2. **`pcdiamag3` is not in joules — `UNRESOLVED`.** Stored energy is O(10⁵–10⁶) J;
   the observed median is 9.69, range −28 to +33. Refuted by four to five orders
   of magnitude, and no rescaled alternative is asserted. **`pcdiamag3` is one of
   the eight signals used by every prior analysis in this project, including the
   canonical q_desc run.** Its physical identity is now formally open.

3. **`tinj` is a torque (N·m), not an angular impulse.**

### Unit systems are inconsistent within the object

| Quantity | Signals | Stored as | Ratio |
|---|---|---|---|
| Number density | `density` / `prmtan_neped` | cm⁻³ / m⁻³ | 10⁶ |
| Temperature | `ece*` / `cerqtit*`, `prmtan_teped` | keV / eV | 10³ |
| Power | `pinj` / `pinj_*` | kW / W | 10³ |

Within-discharge z-scoring hides all three, which is why they survived undetected.
They become live the moment any stage forms a ratio, a sum, or a dimensional type
across a pair.

Two value anomalies are flagged rather than treated as unit failures: `ece33`
(33.9 keV) and `ece34` (21.5 keV) fall outside the ECE band while 38 of 40
channels pass, so group coherence carries the unit. `pinj_21l`/`pinj_21r` are
identically zero across the cohort — beam 21 never fired.

**U002: recommend `CRITICAL` → `MAJOR`.** Dimensional typing is available at
`STRONGLY_INFERRED` for 94/95. What stays blocked is any claim that the units are
known *from the project's own record*.

Detail: `units_recovery_report.md`, `units_sources.md`, `units_recovery.csv`.

---

## 3. Issue 3 — equilibrium lineage

**All 15 are `LINEAGE_PARTIAL`. None is `LINEAGE_RESOLVED`.** This is a closed
issue with a negative answer, not an open one.

Established: all 15 belong to the documented `Equilibrium / shape` group; all 15
share a native cadence of **exactly 20.0 ms** across all 62 discharges; all 15
share an identical upstream length ratio within each discharge. Together these
corroborate a single-producer origin.

Not established, for any of them: the reconstruction code's identity, its inputs,
its constraints, whether any archived quantity feeds it, or whether it is
magnetics-only or kinetically constrained. **No code, settings file, namelist,
version string, or run record exists in any local tree.** No edge in the lineage
graph is `CODE_VERIFIED`, because there is nothing local to verify against.

On `I_p` ancestry: under standard definitions `q95` and `betan` contain `I_p`
explicitly, and equilibrium reconstructions are normally `I_p`-constrained — but
both are *external convention*. The Figure 6 audit reached a compatible
conclusion independently, finding `q95 ≈ shape·a²B_t/I_p` at 7.3% residual
scatter. The rule adopted in S7.1 and retained here is that **statistical
agreement is not proof of ancestry** — a discipline this project adopted after
an earlier audit demonstrated that conflating the two produces both false leakage
findings and false clearances. So: `I_p` ancestry is very likely and not proven.

All 15 are marked `suitable_for_target_independence_decision = False`. No target
was selected and no predictor was classified.

Detail: `equilibrium_lineage_audit.md` + three CSVs.

---

## 4. Issue 4 — the 20 ms grid (mandatory)

**Outcome C. Both numbers are real; they belong to different providers.**

> 20 ms is the **native cadence of the equilibrium group** and the grid spacing
> the **full 95-signal provider** produces whenever an equilibrium signal is
> requested. It is not, and never was, the paper-facing analysis grid — a
> 1000-point linspace at **4.08–6.03 ms**.

The origin is code-verified. `sir-web/providers/diiid_elm_data_provider.py`
L140–143 sets the common grid to the *coarsest* requested signal's native
cadence, and says why in the source: *"the coarsest requested signal sets the
rate — interpolating a 20 ms equilibrium signal onto a 0.02 ms filterscope grid
would fabricate…"*. That is a correct engineering decision, and it is where 20 ms
comes from.

The paper provider instead lays `TARGET_N = 1000` points across the intersection
window, so Δt varies with the window: 4.08 / 4.96 / 6.03 ms (min/median/max),
corroborated independently by the discharge ledger, the validation audit (4.764
ms), and the finite-window study (4.784 ms).

Seven stages were traced separately and none was forced into agreement.

**Any manuscript or figure statement of a 20 ms analysis step is incorrect** and
must be replaced by the variable 4.1–6.0 ms grid.

### The consequence that matters

Placing 20.0 ms equilibrium quantities on a 4.96 ms grid **oversamples them by
~4.0×**: four of every five grid points on `betan`, `q95`, `li`, `kappa` and the
rest are interpolated, not reconstructed. In 2 of 62 discharges the upstream
pipeline had *already* upsampled the group (ratio up to 4.09), compounding to
~16×. And the paper provider block-averages signals denser than the grid but
**linearly interpolates** those sparser than it — the equilibrium group is always
in the second category.

For a framework whose coordinates are phase derivatives this is first-order: at
4× oversampling a numerical derivative of an equilibrium quantity is governed by
the interpolant, and the spline and RTS realizations then differ because they
interpolate differently, not because the physics does. Stated as a structural
property of the object; no reconstruction result was inspected.

Detail: `TEMPORAL_GRID_RECONCILIATION_REPORT.md`.

---

## 5. Issue 5 — reassessment of U001

**Recommend `CRITICAL` → `MAJOR (conditional)`.**

S7.1 recorded the upstream resampling pipeline as unidentified and rated it
`CRITICAL` because "the entire object rests on it". Reading the ancillary
metadata changes the picture: **the operation is characterized, per signal, per
discharge, for all 5890 pairs.** What is missing is the generator code, not the
knowledge of what it did.

Recorded per pair: `method` ∈ {`cubic_spline`, `cubic_spline_simple`,
`pchip_careful`, `pchip_no_smoothing`, `decimate_with_antialiasing`}, `category` ∈
{`smooth_high_snr`, `slow_varying`, `fast_transient`, `noisy`}, and the original
and resampled sample counts — which give the exact resampling ratio.

### The condition

The reclassification holds **only if `Ω_obs` is defined as the archived object**:
the 62 × 95 resampled series as they exist, with the upstream operation treated
as part of the object's definition rather than as a transformation applied to
some deeper ground truth.

This is defensible, and it is what the project has effectively assumed all along.
It has real costs, which must be declared rather than absorbed:

- **Fast diagnostics.** Filterscopes at 0.02 ms native are the fastest channels
  and the ELM markers. Their archived form is already resampled; ELM-resolved
  claims are claims about the archived realization, not the raw diagnostic.
- **Derivative coordinates.** 18 signals were **downsampled by interpolation with
  no anti-alias stage** — all 14 CER channels, plus `bt`, `ip`, `prmtan_neped`,
  `prmtan_teped`. Spline downsampling does not remove content above the new
  Nyquist frequency; any aliased content is now indistinguishable from signal,
  and differentiation amplifies it.
- **High-frequency interpretation.** No claim about structure near the archived
  Nyquist limit is supportable for those 18.
- **Numerical-realization sensitivity.** The object already contains one
  interpolation the study did not choose. The spline and RTS realizations are a
  *second* one layered on the first.
- **Ontology depth.** The ontology is over the archived object. It cannot reach
  below the resampling boundary, and should say so.

This recommendation is **not** made to unblock the study. It is made because the
evidence changed: S7.1 rated U001 `CRITICAL` on the belief that the upstream
operation was unknown, and it is not unknown — it is documented per signal per
discharge, and only the code is missing. The residual risk is real and is
enumerated above.

### And the pipeline is not uniform

| Signal | ≤ shot 187024 (35 discharges) | ≥ shot 189646 (27 discharges) |
|---|---|---|
| `ip` | `cubic_spline`, ~2:1 downsample | `decimate_with_antialiasing`, ~20:1 downsample |

A clean split with **no overlap**. `bt`, `prmtan_neped` and `prmtan_teped` vary
similarly. In the earlier 35 discharges `ip` was downsampled 2:1 by cubic spline
— i.e. **without anti-aliasing** — while in the later 27 it was properly
decimated.

This alone justifies the conditional rating: the object contains a known
processing discontinuity that coincides with a campaign boundary.

Detail: `upstream_resampling_characterization.csv`,
`ancillary_metadata_inventory.csv`.

---

## 6. New findings not requested but material

1. **The cohort is stratified into 7 operational periods** — contiguous
   shot-number families spanning 155537–195659. DIII-D shot numbers increase
   monotonically with time, so this orders the cohort without inventing calendar
   dates. **U008 is partially resolved** (ordering only). Any later
   generalization claim should be evaluated against this stratification rather
   than treating the 62 as exchangeable.

2. **Processing regime aligns with campaign** (§5), so the stratification is not
   merely nominal.

3. **`pcdiamag3` — one of the historical eight — has no established physical
   identity** (§2).

4. **Three internal unit-system inconsistencies** (§2).

5. **No ELM event annotations exist** in an archive described as an ELM dataset
   (§1).

`cohort_campaign_strata.csv`.

---

## 7. Effect on the S7.1 unresolved register

| ID | S7.1 | S7.1R | Basis |
|---|---|---|---|
| U001 upstream pipeline | `CRITICAL` | **`MAJOR (conditional)`** | operation characterized per signal × discharge; only generator code absent |
| U002 units | `CRITICAL` | **`MAJOR`** | 94/95 recoverable at `STRONGLY_INFERRED`; 1 refuted |
| U003 equilibrium lineage | `CRITICAL` | **`CRITICAL` (unchanged)** | closed as negative; nothing local to resolve it |
| U004 uncertainty metadata | MAJOR | unchanged | |
| U005 cohort selection algorithm | MAJOR | unchanged | stratification does not reveal the criterion |
| U006 magnetics raw vs compensated | MAJOR | **elevated in practice** | `pcdiamag3` unit refuted; `ip`/`bt` processing varies by campaign |
| U007 `prmtan_*` lineage | MODERATE | unchanged | method varies across shots |
| U008 date range / regime | MODERATE | **`PARTIALLY_RESOLVED`** | 7 ordered strata; no calendar dates |
| **U009** *(new)* | — | **MAJOR** | cohort processing discontinuity at shot 189646 |
| **U010** *(new)* | — | **MAJOR** | 18 signals downsampled without anti-aliasing |

**One critical item remains: U003.** It cannot be closed from local materials.

---

## 8. Files produced

```
reconciliation/
  build_s7_1r.py                            apply_addenda.py
  units_recovery.csv                        units_recovery_report.md
  units_sources.md
  equilibrium_lineage_nodes.csv             equilibrium_lineage_edges.csv
  equilibrium_lineage_status.csv            equilibrium_lineage_audit.md
  temporal_grid_reconciliation.csv          TEMPORAL_GRID_RECONCILIATION_REPORT.md
  ancillary_metadata_inventory.csv          upstream_resampling_characterization.csv
  cohort_campaign_strata.csv                O_COMPONENT_A_ADDENDUM.md
  S7_1R_FORMAL_AND_PROVENANCE_RECONCILIATION_REPORT.md
  S7_1R_VERDICT.json
```

Modified by addendum, originals preserved: `O_DIIID.json`, `O_DIIID.md`,
`S7_1_OBSERVATIONAL_OBJECT_AND_PROVENANCE.md`,
`S7_1_OBSERVATIONAL_OBJECT_AUDIT_REPORT.md`.

## 9. Reproduction

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
& $P S7\01_observational_object\reconciliation\build_s7_1r.py
& $P S7\01_observational_object\reconciliation\apply_addenda.py
```

Deterministic; no seeds. `apply_addenda.py` is idempotent.

## 10. Gate

Not authorised and not performed: target selection, coordinate generation,
ontology construction, `G_rec`, regression, inspection of reconstruction
performance, S7.2, S7.3.

**S7.2 is not authorised by this document.** The residual blocker for S7.2 is
U003, together with the human decision on how the 15 equilibrium quantities are
to be treated when their ancestry cannot be decided.
