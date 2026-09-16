# S7.1 — Final audit report

**Stage:** S7.1R-FINAL · **Date:** 2026-09-02
**Freeze ID:** `D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1`
**Status:** `FROZEN_WITH_QUALIFICATIONS` · acceptance tests **32/32**

---

## 1. Executive verdict

S7.1 is closed. The observational object is fully enumerated, fully accessible,
fully unit-typed, and hashed. **No CRITICAL items remain** — all three of the
original critical blockers were resolved or reduced on evidence, not on
convenience.

The object is **62 discharges × 95 quantities**, complete and finite in every
one of the 5890 signal × discharge pairs. All 95 load through the analysis
backend. All 95 carry a unit determination. Every quantity has an origin
classification; none is left `UNKNOWN`.

Three qualifications travel with the freeze, and they are why the status is
`FROZEN_WITH_QUALIFICATIONS` rather than unqualified:

- the object is the **archived, resampled** object — the upstream resampling
  code is absent, and 18 quantities were downsampled by interpolation with no
  anti-aliasing;
- the **equilibrium reconstruction is identified only at family level** (EFIT),
  so ancestry for 15 quantities is undecidable on present evidence;
- the cohort is **not homogeneous** — two upstream processing eras split it
  cleanly at shot 189646.

None of these blocks S7.2. All three constrain what S7.2 may claim.

## 2. Final observational-object definition

```
O_DIIID = (D, Omega_obs, S, E, Pi, A)
```

| | Status | Substance |
|---|---|---|
| **D** | `INSTANTIATED` | 95 quantities, 8 families, one-to-one identity at every level |
| **Ω_obs** | `INSTANTIATED` | DIII-D, 62 discharges, ms time bases, 7 ordered periods |
| **S** | `INSTANTIATED` | discharge-level realization; 0.02–20.0 ms native; discharge-specific 1000-point grid |
| **E** | `NOT_INSTANTIATED` | no uncertainty metadata exists; none invented |
| **Π** | `PARTIALLY_INSTANTIATED` | analysis side code-verified; upstream and EFIT partial |
| **A** | `PARTIALLY_INSTANTIATED` | 5890 resampling records, units, channel identity, cohort flags |

`O_DIIID_FINAL.json` / `.md`. **Admissibility is not in O** — it belongs to the
task contract `q`.

## 3. Source-of-truth hierarchy

16 artifacts classified in `SOURCE_ARTIFACT_INVENTORY.csv`; narrative in
`SOURCE_OF_TRUTH_MAP.md`. Path names were not trusted; every artifact was opened.

The archive is the object. One artifact is **cited but absent**:
`smallELM_freq_v6_ZL_data/{shot}_metadata.json`, the units registry's source,
together with its generator `build_signal_units.py`. Neither exists in any local
tree, which is why units are `LOCAL_DOCUMENTED` rather than `CODE_VERIFIED`.

## 4. 95-signal census

Rebuilt from the archive, not inherited from the earlier count. Every one of the
62 archives was opened and its `<signal>_data` keys enumerated.

| Family | n |
|---|---|
| ECE electron temperature | 40 |
| equilibrium / shape | 15 |
| CER rotation / ion temperature | 14 |
| neutral beams | 10 |
| magnetics | 5 |
| filterscope D-alpha | 4 |
| gas injection | 4 |
| density | 3 |
| **total** | **95** |

Matches the expected breakdown exactly. Set equality with the frozen manifest;
identical set in all 62 archives; no duplicates; no aliases.
`FINAL_SIGNAL_INVENTORY.csv` — the literal 95-name inventory, 20 fields.

## 5. Backend accessibility and parity

```
DALIA_ACCESSIBLE_SIGNALS = 95 / 95
```

All 95 `EXACT_IDENTITY`. Nothing `ALIAS_ONLY`, `MISMATCH` or `UNRESOLVED`.

Three legs: catalog parity (95 names, identical order); code-path identity
(same `_load_signal`, same files); and **12 numerical spot checks** through the
live backend across both cohort eras and all eight families, exact on length,
min and max. Separately, 5890/5890 pairs load through the reference provider
with `finite_fraction = 1.0` throughout.

`DALIA_SIGNAL_PARITY.csv`, `DALIA_LOADING_AUDIT.md`.

## 6. Units registry and the ECE correction

```
units_resolved   = 95 / 95
  with a physical unit          93
  documented as uncalibrated     2    pcbcoil, pcdiamag3
units_unresolved =  0 / 95
ECE assigned keV = 40 / 40
```

The 40 ECE channels were identified from the registry — description-based and
name-based sets computed independently and required to match — not assumed. None
carried a conflicting unit, so the STOP condition did not fire. The 55 non-ECE
entries are byte-identical to a pre-change snapshot.

pre `bbebdc23…d6d4f6` → post `b8b3cead…98e72`

`pcbcoil` and `pcdiamag3` are **resolved as unit-less**: upstream reports `raw`,
uncalibrated digitiser output. Recording a unit for them would be fabrication.

Three scale inconsistencies are documented rather than harmonised: `pinj` kW vs
`pinj_*` W; `density` cm⁻³ vs `prmtan_neped` m⁻³; `ece*` keV vs `cerqtit*` /
`prmtan_teped` eV. Within-discharge z-scoring hides all three — they matter only
when a construction crosses a pair, which is what a relational ontology does.

`SIGNAL_UNITS_AUDIT.csv` / `.md`.

## 7. Origin classification

| Classification | n | Change |
|---|---|---|
| `DIAGNOSTIC_RECONSTRUCTION` | 57 | 54 → 57 |
| `EQUILIBRIUM_DERIVED` | 15 | unchanged |
| `CONTROL_COMMAND_OR_ACTUATION` | **14** | new category |
| `DIRECT_MEASUREMENT` | **9** | 0 → 9 |
| `UNKNOWN` | **0** | 26 → 0 |

The registry's descriptions resolve what group membership could not. Gas
channels are **valve command voltages** — actuation, not diagnosis. Beam channels
are actuator outputs. Filterscopes are calibrated photon-flux measurements, not
uncalibrated photodiodes.

The nine direct measurements include `pcbcoil` and `pcdiamag3`, documented
upstream as `raw`: **the two least-processed signals in the object are the only
two without a unit.** The magnetics trio `ip`/`bt`/`vsurf` is direct at
`STRONGLY_INFERRED` only — the local record documents the quantity but never the
sensor or compensation chain.

`SIGNAL_ORIGIN_CLASSIFICATION.csv`, `semantic_types_and_units.csv`.

## 8. Provenance DAG

13 nodes, 13 edges, every edge carrying parent, child, dependency type,
evidence, evidence class, confidence and notes.

Analysis-side edges are `CODE_VERIFIED` end to end. The upstream resample edge
is `CODE_VERIFIED` for the *operation* (metadata records it per signal per
discharge) with the generator absent. EFIT→output edges are `LOCAL_DOCUMENTED`
for 2 and `STRONGLY_INFERRED` for 13. Input→EFIT edges are `UNRESOLVED` and
annotated *"NOT verified for this pipeline"*.

**Statistical correlation appears nowhere as evidence of ancestry** — verified
programmatically as an acceptance test.

## 9. Equilibrium lineage

```
LINEAGE_RESOLVED 0 · LINEAGE_PARTIAL 15 · LINEAGE_UNRESOLVED 0
```

Advance: the family is **EFIT**, named explicitly in the `aminor` and `area`
descriptions. All 15 now have documented units and scientific definitions.

Still unresolved for all 15: EFIT settings, inputs, constraints, and whether the
reconstruction was kinetically constrained. All carry
`suitable_for_target_independence_decision = False`.

Plasma-current ancestry is *very likely* — definitional for `q95` and `betan`,
conventional for the rest — and *not proven from the project's own record*. The
Figure 6 result (7.3% residual scatter) is consistent but is not admitted as
proof.

`EQUILIBRIUM_LINEAGE_AUDIT.md` + 3 CSVs.

## 10. Temporal-grid reconciliation

```
FIXED_20_MS_CANONICAL_GRID = FALSE      -- formally retired
```

8 stages traced separately in `FINAL_TEMPORAL_LINEAGE.csv`:

| Grid | Δt (ms) |
|---|---|
| native — equilibrium | **20.0** |
| native — filterscope | **0.02** |
| full 95-signal provider | ~20 (coarsest requested rule) |
| **canonical Paper 8-signal** | **4.084 / 4.965 / 6.026** |
| full-object 95-signal | 3.754 / 4.595 / 5.365 |
| q_desc realizations | 4.764 median |
| dFL export | 4.764, inherited |

20 ms is the equilibrium native cadence and the full provider's coarsest-dt
rule, code-verified at L140–143 with the reasoning stated in the source. It was
never the Paper grid. Confirmed here: reference provider on shot 155537 with the
paper eight returns **4.7644 ms**, matching the documented 4.764 ms.

**Consequence:** equilibrium quantities are ~4× oversampled on the analysis grid
(~16× in 2 discharges), because the provider block-averages denser signals but
linearly interpolates sparser ones — and equilibrium is always sparser. Any
derivative-valued coordinate over them is governed by the interpolant.

`TEMPORAL_GRID_FINAL_VERDICT.md`.

## 11. Upstream resampling limitation

**`MAJOR_LIMITATION`.** Not critical, and not downgraded to unblock anything.

The *operation* is characterized for all 5890 pairs — method ∈ {`cubic_spline`,
`cubic_spline_simple`, `pchip_careful`, `pchip_no_smoothing`,
`decimate_with_antialiasing`}, category, and original/resampled counts. Only the
generator code is missing. The backend loads **after** this operation.

**Can O be rigorously defined as the archived object? Yes** — with claim
boundaries.

*Permitted:* relational analysis of the frozen object; comparisons among
coordinates constructed from it; reproducible downstream processing.

*Not permitted without qualification:* claims about native high-frequency
physics; claims requiring exact raw-diagnostic bandwidth; derivative
interpretation above the archived resolution. **18 signals were downsampled by
interpolation with no anti-alias stage** — all 14 CER channels plus `bt`, `ip`,
`prmtan_neped`, `prmtan_teped` — so aliased content is not separable from
signal (U010).

## 12. 62-discharge cohort

62 discharges, 155537–195659, all 95 signals in all 62, finite fraction 1.0
throughout. 89 near-constant pairs and 84 identically-zero pairs, the latter
entirely beam channels that never fired — an operational fact, retained.

Two upstream processing eras split cleanly at shot 189646: 35 discharges
`cubic_spline`, 27 `decimate_with_antialiasing`. **Independently corroborated**
by the units registry's 35/62 – 27/62 unit-string variant split, reached from
different metadata (U009).

7 ordered operational periods; no calendar dates; regimes not assigned.

**These 62 are the complete finite object available to this study, not a random
or representative sample of DIII-D operations.**

`COHORT_PROVENANCE.md`, `FINAL_SHOT_INVENTORY.csv`.

## 13. Final O instantiation

See §2 and `O_DIIID_FINAL.json`. No reconstruction target is encoded anywhere.

## 14. Corrections to earlier S7.1 statements

12 material corrections in `S7_1_REVISION_LEDGER.md`. Nothing erased. The
headline items:

`A` re-read from admissibility to ancillary information (R-2) · units from
"unknown for all 95" to 95/95 determined (R-3) · ECE assigned keV (R-4) ·
backend from 12 to 95 signals (R-5) · fixed-20-ms retired (R-6) · `UNKNOWN`
origin from 26 to 0 (R-7) · EFIT identified (R-8) · U001 reclassified (R-9) ·
cohort discontinuity and anti-alias gaps newly found (R-10, R-11) · cohort
ordering recovered (R-12).

The ledger also records where the **interim S7.1R pass was wrong**: it inferred
units from external convention and got `pcbcoil`, `pcdiamag3`, `betan`, `fs*`
and `gas*` wrong. The registry is authoritative over that inference. Two interim
inferences it confirmed — the kW/W and cm⁻³/m⁻³ splits — were derived
independently from magnitude and additivity.

## 15. Unresolved issues

**CRITICAL — none.**

**MAJOR (5)**

| ID | Issue |
|---|---|
| U001 | upstream resampling generator code absent (operation documented) |
| U003 | EFIT settings/inputs/constraints unresolved; 15 quantities `LINEAGE_PARTIAL` |
| U004 | no measurement-uncertainty metadata; `E` cannot be instantiated |
| U009 | cohort processing discontinuity at shot 189646 (35 / 27) |
| U010 | 18 signals downsampled by interpolation with no anti-aliasing |

**MODERATE (3)** — U002 units are `LOCAL_DOCUMENTED`, source tree absent ·
U005 cohort selection algorithm and parent population unknown · U006 magnetics
sensor/compensation chain undocumented (partly relieved: `pcbcoil`/`pcdiamag3`
now documented as raw).

**MINOR (2)** — U007 `prmtan_*` fit lineage · U008 no calendar dates (ordering
recovered).

## 16. Files produced

```
reconciliation_final/
  s7_1r_final_units.py     s7_1r_final_census.py     s7_1r_final_freeze.py
  FINAL_SIGNAL_INVENTORY.csv        FINAL_SHOT_INVENTORY.csv
  SIGNAL_ORIGIN_CLASSIFICATION.csv  semantic_types_and_units.csv
  SIGNAL_UNITS_AUDIT.csv            SIGNAL_UNITS_AUDIT.md
  SIGNAL_UNITS.pre_S7_1R.json       SIGNAL_UNITS.pre_S7_1R.sha256
  SIGNAL_UNITS.post_S7_1R.sha256
  DALIA_SIGNAL_PARITY.csv           DALIA_LOADING_AUDIT.md
  provenance_nodes.csv  provenance_edges.csv  provenance_graph.json
  equilibrium_lineage_nodes.csv  equilibrium_lineage_edges.csv
  equilibrium_lineage_status.csv  EQUILIBRIUM_LINEAGE_AUDIT.md
  FINAL_TEMPORAL_LINEAGE.csv        TEMPORAL_GRID_FINAL_VERDICT.md
  PROVIDER_SURFACE_COMPARISON.md    COHORT_PROVENANCE.md
  SOURCE_ARTIFACT_INVENTORY.csv     SOURCE_OF_TRUTH_MAP.md
  availability_by_shot.csv  availability_matrix.csv  signal_quality_summary.csv
  CENSUS_CHECKS.json
  O_DIIID_FINAL.json                O_DIIID_FINAL.md
  S7_1_REVISION_LEDGER.md           S7_1_FINAL_FREEZE.json
  S7_1_OBSERVATIONAL_OBJECT_AND_PROVENANCE_FINAL.md
  IMPLEMENTATION_PROVENANCE_FINAL.md
  S7_1_FINAL_AUDIT_REPORT.md
```

Modified outside: `S7/SIGNAL_UNITS.json` (40 ECE entries), `S7/STATUS.md`,
`S7/README.md`, backend `data_provider.py` (v164),
`DIIID_example/diiid_sir_data_provider.py` (created).

Original S7.1 and interim S7.1R artifacts preserved unchanged at this stage.

## 17. Reproduction

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$R = "S7\01_observational_object\reconciliation_final"

& $P diiid_sir_data_provider.py    # verify manifest against all 62 archives
& $P $R\s7_1r_final_units.py
& $P $R\s7_1r_final_census.py
& $P $R\s7_1r_final_freeze.py
```

Deterministic; no seeds. The units script preserves a pre-change snapshot and
refuses to overwrite conflicting content.

## 18. Gate recommendation for S7.2

**`READY_WITH_QUALIFICATIONS`.**

The object is frozen, hashed and defensible. S7.2 may define `K_rec` — subject
to the inherited constraints in the response summary, chiefly: O is the 95, not
the 8; the equilibrium 15 have undecidable ancestry; derivative coordinates over
the equilibrium group are interpolation-governed; the cohort has a processing
discontinuity; and `E` is empty, so no uncertainty-weighted contract can be
written.

**S7.2 is not authorised by this document.**
