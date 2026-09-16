# S7.1 — Observational Object and Provenance Census: audit report

**Stage:** S7.1 (Stage 1 of 12) · **Date:** 2026-09-02
**Verdict:** `READY_WITH_QUALIFICATIONS`

---

## 1. Executive verdict

The observational object is **larger and less documented than previous work
implied**. It comprises **62 DIII-D discharges × 95 scientific quantities**, all
95 present in all 62. Prior analyses used **eight** of those 95; the other 87
were excluded by historical convention, not by any documented scientific
reasoning.

Provenance is substantially better documented than the previous audit concluded
— a detailed canonical provenance ledger exists in the sir-web tree that the
earlier audit did not locate — but three **critical** gaps remain: the upstream
resampling pipeline, physical units for every quantity, and the equilibrium
reconstruction lineage behind 15 quantities.

Two components of the formal object **cannot** be instantiated from the data as
possessed: the uncertainty model and admissibility. A third, provenance, is
partial.

The stage gate held: no target, no ontology, no coordinates, no regression.

## 2. Source trees located

| Tree | Role |
|---|---|
| `D:\sir-web\Paper Examples\Relational Coordinates for Multimodal Plasma Observations\` | **primary implementation and provenance lineage** — providers, canonical run package, discharge ledger, provenance ledger |
| `D:\sir-web\providers\diiid_elm_data_provider.py` | full 95-signal provider; **authoritative signal-group documentation** |
| `D:\SIR_paper\DIIID_example\` | 62-shot data archive + derived/paper-facing exports |
| `D:\DIII-D ELM data set\resampled_data_v6` | original archive root recorded in documentation (outside both repos) |

The single most valuable artifact is
`canonical_d3d_62_shot_provenance/D3D_CANONICAL_DATA_AND_PREPROCESSING_PROVENANCE.md`
(449 lines). It documents cohort construction, alignment, normalisation and the
three numerical realizations, and is itself candid about what it cannot resolve.

**Correction to a prior finding.** The earlier Figure 6 audit concluded that
"documentary provenance is unavailable", having inspected only the per-shot
metadata JSON. That conclusion was **too strong**: it was true of the metadata
files but false of the project as a whole. Much of what was previously marked
unresolved is in fact documented.

## 3. Canonical versus derived artifacts

15 source artifacts inventoried, all resolved
(`SOURCE_ARTIFACT_INVENTORY.csv`): 6 `PRIMARY`, 2 `DERIVED`,
1 `SUMMARY_EXPORT`, 2 `LEGACY_RESULT`, 3 `DOCUMENTATION`, 1 dataset directory.

The three `Figure_data/*` files under `DIIID_example` are **summary exports**,
not primary results; their own lineage field points back into sir-web.

## 4. Signal census

95 distinct quantities, complete across all 62 discharges:

| Group | n | Median native Δt |
|---|---|---|
| ECE temperature channels | 40 | 0.20 ms |
| Equilibrium / shape | 15 | 20.0 ms |
| CER rotation / Ti | 14 | 10.0 ms |
| Neutral beams | 10 | 0.10 ms |
| Magnetics | 5 | 1.00 ms |
| Filterscopes (D-alpha) | 4 | 0.02 ms |
| Gas injection | 4 | 2.00 ms |
| Density | 3 | 10.0 ms |

Native sampling spans **three orders of magnitude** (0.02–20 ms), which is the
central structural fact about this object: any common grid necessarily discards
information from the fast channels or interpolates the slow ones.

## 5. Shot / cohort census

62 discharges, common-support duration 4.08 / 4.96 / 6.02 s (min/median/max),
1000 aligned samples each. Historical cohort roles (q_desc member, q_rec
development/external) are recorded as **provenance flags only** and were not
used for any inclusion decision.

## 6. Provenance DAG

`provenance_nodes.csv` / `provenance_edges.csv` / `provenance_graph.json`.
Confidence levels: `CODE_VERIFIED` for the analysis-side chain, `DOCUMENTED` for
upstream resampling effects, `STRONGLY_INFERRED` for equilibrium ancestry
(group-level only), `UNRESOLVED` for the equilibrium inputs.

Statistical association was never admitted as evidence of ancestry — a rule
adopted because the previous audit demonstrated that conflating the two produces
both false leakage findings and false clearances.

## 7. Direct / reconstructed / derived

| Classification | n |
|---|---|
| `DIAGNOSTIC_RECONSTRUCTION` | 54 |
| `UNKNOWN` | 26 |
| `EQUILIBRIUM_DERIVED` | 15 |
| `DIRECT_MEASUREMENT` | **0** |

**No quantity could be proven to be a direct measurement.** This is a statement
about the completeness of the record, not a claim that the archive contains no
direct measurements. The 26 `UNKNOWN` entries — magnetics, density, filterscope,
gas and beam groups — have documented group membership but no artifact
establishing whether each is a raw sensor signal or a compensated product.

## 8. Temporal / preprocessing lineage

Six documented stages (`preprocessing_lineage.csv`): upstream resample
(**unresolved code**) → finite-clean/sort/dedupe → common-window intersection →
grid construction (1000 points) → numerical realization (none / spline k=5 s=0.1
/ RTS R=1 Q=1e-4) → within-discharge z-score (ddof=0, no pooled statistics).

**Verified correction:** the analysis Δt is **not** a fixed 20 ms. It varies
4.1–6.0 ms across discharges because the window varies while the point count is
fixed at 1000.

## 9. Units and semantic types

`semantic_types_and_units.csv` exists but is **almost entirely `UNKNOWN`**.
No units table exists in the archives, the metadata, the provider code, or the
provenance ledger. Units were not invented. This blocks dimensional typing for
the ontology stage.

## 10. Data quality and availability

- Availability: **100%** — every quantity in every discharge.
- Finite fraction: **1.0** for all 5890 signal × discharge pairs.
- Near-constant pairs: **88 / 5890** (1.5%) — flagged descriptively, not excluded.
- Median repeat ratio: 0.243, consistent with upstream resampling of coarse
  signals onto denser grids.

No signal was ranked by usefulness; usefulness is task-conditioned and no task
exists.

## 11. Instantiated O

| Component | Status |
|---|---|
| D — data channels | **INSTANTIATED** (95 quantities) |
| Ω_obs — observational support | **INSTANTIATED** (62 discharges, ms time bases) |
| S — sampling structure | **INSTANTIATED** |
| E — uncertainty model | **NOT_INSTANTIATED** |
| Π — provenance | **PARTIALLY_INSTANTIATED** |
| A — admissibility | **NOT_INSTANTIATED** (task-conditioned; no task) |

**The manuscript definition of O could not be located.** No local artifact
defines `O = (D, Ω_obs, S, E, Π, A)`. The only manuscript file present,
`Lorenz/SIR_paper_orig.pdf` (22 pages), contains **zero** occurrences of
"observational object", "scientific object" or "information boundary", so it
predates the Section 1.1 architecture. Component semantics therefore follow the
names supplied in the task specification and are flagged as ungrounded in
`O_DIIID.json`. **This must be reconciled against the current manuscript before
S7.2.**

## 12. Critical unresolved provenance

| ID | Item | Severity | Blocks |
|---|---|---|---|
| U001 | upstream resampling pipeline unidentified | **CRITICAL** | target selection + coordinates |
| U002 | physical units unknown for all 95 | **CRITICAL** | coordinates (dimensional typing) |
| U003 | equilibrium reconstruction lineage (15 quantities) | **CRITICAL** | target selection + coordinates |
| U004 | no measurement-uncertainty metadata | MAJOR | E cannot be instantiated |
| U005 | cohort selection algorithm unknown | MAJOR | domain claims |
| U006 | magnetics raw vs compensated | MAJOR | target selection + coordinates |
| U007 | `prmtan_*` pedestal fit lineage | MODERATE | target selection |
| U008 | date range / operating regime | MODERATE | domain claims |

## 13. Legacy q_rec separation

Firewall documented in `_legacy_reference/LEGACY_QREC_STATUS.md`. The retired
admissible set, supports, comparator and performance numbers were **not**
consulted. Historical membership appears only as boolean provenance flags.
S7.2 must not assume the target is plasma current.

## 14. Files produced

```
S7/README.md                    S7/STATUS.md
S7/_manifests/INITIAL_STATE_MANIFEST.json
S7/_legacy_reference/LEGACY_QREC_STATUS.md
S7/01_observational_object/
  build_s7_1_census.py            finalize_s7_1.py
  signal_inventory.csv            shot_inventory.csv
  availability_by_shot.csv        availability_matrix.csv
  signal_quality_summary.csv      temporal_support.csv
  preprocessing_lineage.csv       semantic_types_and_units.csv
  provenance_nodes.csv            provenance_edges.csv
  provenance_graph.json           SOURCE_ARTIFACT_INVENTORY.csv
  UNRESOLVED_PROVENANCE.csv       CONSISTENCY_CHECKS.json
  O_DIIID.json                    O_DIIID.md
  OBSERVATIONAL_DOMAIN.md         IMPLEMENTATION_PROVENANCE.md
  S7_1_OBSERVATIONAL_OBJECT_AND_PROVENANCE.md
  S7_1_OBSERVATIONAL_OBJECT_AUDIT_REPORT.md
```

## 15. Reproduction

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
& $P S7\01_observational_object\build_s7_1_census.py
& $P S7\01_observational_object\finalize_s7_1.py
```

Deterministic; no seeds required.

## 16. Gate recommendation for S7.2

**`READY_WITH_QUALIFICATIONS`.** The census is complete and internally
consistent (10/10 checks pass), and the object is characterised well enough to
define a contract. But S7.2 should not begin until four things are settled:

1. the **manuscript definition of O** is located and reconciled;
2. a decision on **units** — recover them, or accept an ontology without
   dimensional typing and state that limitation;
3. a decision on the **15 equilibrium quantities**, whose ancestry is undecidable
   on present evidence and which will otherwise have to be treated
   conservatively;
4. explicit acknowledgement that **87 quantities are newly in scope**, so the
   contract must state which parts of the object it admits and why — on
   scientific grounds, not historical ones.

<!-- S7.1R-CORRECTION -->

---

## Correction — S7.1R (2026-09-02)

**Applied by addendum; nothing above has been deleted.** Full detail:
`reconciliation/O_COMPONENT_A_ADDENDUM.md`.

### `A` was read incorrectly

S7.1 read the sixth component of `O = (D, Ω_obs, S, E, Π, A)` as
**admissibility** and recorded it `NOT_INSTANTIATED`, flagging the reading as
ungrounded because no manuscript definition could be located.

An authoritative local artifact has since been found:
`D:\SIR_paper\General\sir_representational_prism.py`, the manuscript's own visual-abstract figure generator. It draws the
scientific object `𝒪` and the task contract `q` as separate boxes, and lists the
contract's attributes as **"Admissibility · Information · Intended Use"**.

**Admissibility belongs to the task contract `q`, not to `𝒪`.**

`A` is therefore re-read as **ancillary observational information** — annotations
and metadata carried by the object, but not a task-conditioned admissibility
rule.

### `A` is `PARTIALLY_INSTANTIATED`, not `NOT_INSTANTIATED`

Under the corrected reading the object carries 5890 per-signal ancillary records
(62 discharges × 95 signals): upstream resampling `method` and `category`, and
original/resampled sample counts — plus signal-group membership, cohort
provenance flags, and shot identifiers. Absent: units, uncertainty, dates,
regime labels, and — despite the archive being an ELM dataset — any ELM event
annotation.

### Other S7.1 statements corrected or extended

| S7.1 statement | S7.1R |
|---|---|
| units "unknown", U002 `CRITICAL` | correct as to the *local record* — no local artifact states any unit. But 94/95 are recoverable by external convention at `STRONGLY_INFERRED`; recommend `MAJOR`. `pcdiamag3` is `UNRESOLVED` (joule hypothesis refuted by magnitude). |
| upstream pipeline "unresolved", U001 `CRITICAL` | the *operation* is characterized per signal per discharge; only the generator code is absent. Recommend `MAJOR (conditional)`. |
| "no date range or campaign identifier is recorded" | shot-number families order the cohort into 7 operational periods; U008 partially resolved (ordering, not dates). |
| 15 equilibrium quantities, ancestry undecidable | unchanged — all 15 `LINEAGE_PARTIAL`; none resolved. |

### New findings that qualify the object

- **The cohort is not homogeneous.** `ip` was resampled by `cubic_spline` in all
  35 discharges ≤ shot 187024 and by `decimate_with_antialiasing` in all 27
  ≥ shot 189646. `bt`, `prmtan_neped`, `prmtan_teped` vary likewise.
- **Unit systems are internally inconsistent**: `density` (cm⁻³) vs
  `prmtan_neped` (m⁻³); `ece*` (keV) vs `cerqtit*` (eV); `pinj` (kW) vs
  `pinj_*` (W).
- **Equilibrium quantities are ~4× oversampled** on the analysis grid (20.0 ms
  native onto a 4.96 ms median grid), reaching ~16× in 2 discharges.
- **The 20 ms question is settled** — Outcome C. See
  `reconciliation/TEMPORAL_GRID_RECONCILIATION_REPORT.md`.
