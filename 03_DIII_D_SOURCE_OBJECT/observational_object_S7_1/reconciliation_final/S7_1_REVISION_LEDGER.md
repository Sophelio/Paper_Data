# S7.1 Revision Ledger

Every material correction made to the original S7.1 audit. Nothing earlier has
been erased: the original artifacts remain in
`S7/01_observational_object/`, the interim S7.1R pass remains in
`reconciliation/`, and superseded statements are retired explicitly below.

Format: **R-n** · prior statement → corrected statement · basis · where it lives now.

---

## R-1 — Documentary provenance

**Prior (Figure 6 audit, carried into early S7.1):** documentary provenance is
unavailable.

**Corrected:** substantial project-level preprocessing and provenance
documentation exists — a 449-line canonical provenance ledger, a per-discharge
ledger builder, and validation audits.

**Basis:** the earlier conclusion rested on inspecting only the per-shot
metadata JSON. It was true of those files and false of the project.

**Status:** RETIRED. Already corrected in the S7.1 report §2; restated here for
completeness.

---

## R-2 — The meaning of `A` in `O = (D, Ω_obs, S, E, Π, A)`

**Prior:** `A` = admissibility; recorded `NOT_INSTANTIATED` because
admissibility is task-conditioned and no task exists.

**Corrected:** `A` = **ancillary observational information**. Admissibility is
an attribute of the task contract `q`, entering through `I_q` / `P_q` and `A_q`.
`A` is **`PARTIALLY_INSTANTIATED`**.

**Basis:** `D:\SIR_paper\General\sir_representational_prism.py`, the
manuscript's own visual-abstract figure generator, draws the scientific object
and the task contract as separate boxes and lists the contract's attributes as
**"Admissibility · Information · Intended Use"**. `LOCAL_DOCUMENTED`
(figure source). No prose artifact states the 6-tuple; `SIR_paper_orig.pdf`
predates the Section 1.1 architecture entirely.

**Status:** RETIRED. Original block preserved in `O_DIIID.json` under
`_s7_1_original_A_admissibility`.

---

## R-3 — Units

**Prior:** units are unknown for all 95 quantities; U002 `CRITICAL`; "no units
table exists in the archives, the metadata, the provider code, or the provenance
ledger."

**Corrected:** a units registry exists at `S7/SIGNAL_UNITS.json`, recovered from
upstream fetch metadata and audited across all 62 shots. After the S7.1R-FINAL
ECE correction: **93/95 carry a physical unit, 2 are documented as
uncalibrated (no unit exists), 0 are unresolved.**

**Basis:** the prior statement was accurate about the four places it named —
`resampled_data_v6` genuinely stores no units, and `_units_for()` returns a
blank data unit by design. It was wrong to generalise from those to the project.

**Also corrected — the interim S7.1R pass inferred units from external
convention and got several wrong.** The registry is authoritative over that
inference:

| Signal | S7.1R inferred | Registry | Note |
|---|---|---|---|
| `pcbcoil` | `A` | **uncalibrated** | upstream reports `raw` |
| `pcdiamag3` | UNRESOLVED (J refuted) | **uncalibrated** | refutation was right, cause now known |
| `betan` | `%·m·T/MA` | **`1`** | MDSplus reports explicit dimensionless |
| `fs*` | "arbitrary (photodiode)" | **`ph/(sr cm² s)`** | calibrated after all |
| `gas*` | `Torr·L/s` | **`V`** | valve *command* voltage, not a flow |

Two S7.1R inferences the registry **confirmed**: `pinj` kW vs `pinj_*` W, and
`density` cm⁻³ vs `prmtan_neped` m⁻³. Both were derived from magnitude and
additivity, independently of the registry.

**Status:** U002 `CRITICAL` → **`MODERATE`**.

---

## R-4 — ECE units (this stage)

**Prior:** 40 ECE channels `units: null`, status `unresolved`, "no authoritative
public documentation was found. Left null deliberately: NOT inferred."

**Corrected:** all 40 assigned **`keV`**, status `domain_authorized`, evidence
class `DOMAIN_AUTHORIZED`.

**Basis:** explicit domain-expert instruction. This is expert assignment, not
recovered metadata, and is labelled as such in every artifact. No ECE entry
carried a conflicting unit; no non-ECE entry was touched (verified
programmatically against a pre-change snapshot).

**Hashes:** pre `bbebdc23…d6d4f6`, post `b8b3cead…98e72`.

---

## R-5 — Backend accessibility

**Prior:** the 95-signal object's accessibility through the analysis backend was
not established; the backend exposed 12 signals (the paper eight plus four
filterscopes) and hard-restricted SIR to the eight via an allow-list.

**Corrected:** **95/95 accessible**, verified.

**Basis:** the backend provider was updated to the full manifest; catalog
returns 95 signals in manifest order; 12 signal × discharge fetches across both
cohort processing eras and all eight groups agree with the reference loader
**exactly** on length, minimum and maximum.

**Status:** closed.

---

## R-6 — The temporal grid

**Prior:** ambiguity between a "fixed 20 ms grid" and a 4.1–6.0 ms grid.

**Corrected:** `FIXED_20_MS_CANONICAL_GRID` is **false** and is formally
retired. 20 ms is the native cadence of the equilibrium group and the spacing
the *full 95-signal provider* produces whenever an equilibrium signal is
requested. The canonical Paper grid is a discharge-specific 1000-point linspace
at **4.08–6.03 ms** (median 4.965). Over all 95 signals the window narrows and
the grid becomes **3.75–5.37 ms** (median 4.595).

**Basis:** code-verified at `sir-web/providers/diiid_elm_data_provider.py`
L140–143, which sets the grid to the coarsest requested native dt and says so in
the source; and `TARGET_N = 1000` in the Paper provider, corroborated
independently by the discharge ledger, the validation audit (4.764 ms) and the
finite-window study (4.784 ms).

**Status:** RETIRED. Any manuscript or caption text stating a 20 ms analysis
step must be corrected.

---

## R-7 — Origin classification

**Prior:** `DIAGNOSTIC_RECONSTRUCTION` 54, `EQUILIBRIUM_DERIVED` 15,
`UNKNOWN` 26, `DIRECT_MEASUREMENT` 0.

**Corrected:** `DIAGNOSTIC_RECONSTRUCTION` 57, `EQUILIBRIUM_DERIVED` 15,
`CONTROL_COMMAND_OR_ACTUATION` 14, `DIRECT_MEASUREMENT` 9, `UNKNOWN` **0**.

**Basis:** the registry's descriptions resolve what group membership alone could
not. The gas channels are *valve commands in volts*, so they are actuation, not
diagnosis — forcing them into `UNKNOWN` lost real information. The beam channels
are actuator-side outputs. The filterscopes are calibrated photon-flux
measurements. And `pcbcoil` / `pcdiamag3` are documented as `raw` digitiser
output, which makes them the most defensible direct measurements in the object —
the two signals with no unit are the two least processed.

**Status:** superseded.

---

## R-8 — Equilibrium reconstruction family

**Prior:** the equilibrium reconstruction's implementation, inputs and
constraints are not present in any available artifact; identity `UNRESOLVED`.

**Corrected:** the family is **EFIT**, named explicitly in the registry
descriptions of `aminor` and `area`. Settings, inputs and constraints remain
unresolved, so all 15 stay `LINEAGE_PARTIAL`.

**Basis:** `LOCAL_DOCUMENTED` for the 2 signals that name EFIT;
`STRONGLY_INFERRED` for the other 13 by group coherence — all 15 share one
reconstruction and one 20.0 ms time base.

**Status:** partially corrected. U003 `CRITICAL` → **`MAJOR`**.

---

## R-9 — Upstream resampling gap

**Prior:** the upstream resampling pipeline is unidentified; U001 `CRITICAL`
because "the entire object rests on it".

**Corrected:** the *operation* is characterized per signal per discharge for all
5890 pairs — method, category, original and resampled sample counts. Only the
generator code is absent. **`MAJOR_LIMITATION`**, conditional on `Ω_obs` being
defined as the archived object.

**Status:** reclassified, with claim boundaries stated in the final report §11.

---

## R-10 — Cohort homogeneity (new finding, no prior statement)

**New:** the cohort is **not homogeneous**. `ip` was resampled by
`cubic_spline` in all 35 discharges ≤ shot 187024 and by
`decimate_with_antialiasing` in all 27 ≥ shot 189646 — a clean split with no
overlap. `bt`, `prmtan_neped` and `prmtan_teped` vary likewise.

Independently corroborated: the units registry reports upstream unit-string
variants splitting **35/62 and 27/62** for `bt` (`t` vs blank), `ip` (`a` vs
`amps`) and the filterscopes (`ph/(sr cm2 s)` vs `ph/cm2/sr/s`) — the same
partition, arrived at from different metadata. Two upstream processing eras are
present in one cohort.

**Status:** new MAJOR issue **U009**.

---

## R-11 — Anti-aliasing (new finding, no prior statement)

**New:** 18 signals were downsampled by interpolation with no anti-alias stage —
all 14 CER channels plus `bt`, `ip`, `prmtan_neped`, `prmtan_teped`.

**Status:** new MAJOR issue **U010**.

---

## R-12 — Date range and operating regime

**Prior:** no date range, campaign identifier, or operating-regime label is
recorded; U008 `MODERATE`.

**Corrected:** contiguous shot-number families partition the cohort into **7
ordered operational periods** spanning 155537–195659. DIII-D shot numbers
increase monotonically with time, so this orders the cohort without inventing
calendar dates. Regime labels remain unassigned — assigning them would be
inference.

**Status:** U008 `MODERATE` → **`PARTIALLY_RESOLVED`** (ordering only).

---

## Summary of severity changes

| ID | Original S7.1 | S7.1R-FINAL |
|---|---|---|
| U001 upstream resampling | CRITICAL | **MAJOR** |
| U002 units | CRITICAL | **MODERATE** |
| U003 equilibrium lineage | CRITICAL | **MAJOR** |
| U004 uncertainty metadata | MAJOR | MAJOR (unchanged) |
| U005 cohort selection algorithm | MAJOR | MAJOR (unchanged) |
| U006 magnetics raw vs compensated | MAJOR | **MODERATE** — `pcbcoil` / `pcdiamag3` now documented as raw/uncalibrated |
| U007 `prmtan_*` lineage | MODERATE | MODERATE (unchanged) |
| U008 date range / regime | MODERATE | **PARTIALLY_RESOLVED** |
| **U009** cohort processing discontinuity | — | **MAJOR (new)** |
| **U010** downsampling without anti-aliasing | — | **MAJOR (new)** |

**No CRITICAL items remain.**
