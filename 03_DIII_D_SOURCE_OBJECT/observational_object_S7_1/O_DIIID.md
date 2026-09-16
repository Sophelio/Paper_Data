# O — the DIII-D observational object (S7.1 instantiation)

Machine-readable form: `O_DIIID.json` (`O_DIIID_S7_V1`).

## Status of the formal definition

**The manuscript definition of `O = (D, Ω_obs, S, E, Π, A)` was not located.**
No local artifact defines it. The only manuscript file present,
`Lorenz/SIR_paper_orig.pdf` (22 pages), contains zero occurrences of
"observational object", "scientific object" or "information boundary", and so
predates the Section 1.1 architecture. The component semantics used below follow
the names given in the S7 task specification and are **not** grounded in a
located definition. This must be reconciled before S7.2.

## D — data channels · INSTANTIATED

95 scientific quantities, each a scalar time series, all present in all 62
discharges. Eight of these carried prior analyses; the object is **not** reduced
to them here. Groups: ECE temperature (40), equilibrium/shape (15), CER
rotation/Ti (14), neutral beams (10), magnetics (5), filterscopes (4), gas
injection (4), density (3).

## Ω_obs — observational support · INSTANTIATED

62 DIII-D discharges from an ELM-study library. Per-signal native time bases in
milliseconds. Common-support duration 4.08–6.02 s. Date range **unresolved**;
operating regimes **not documented**; inclusion criterion was common-grid
viability across all 95 signals, with the exact algorithm and parent population
unknown.

## S — sampling structure · INSTANTIATED

Native spacing spans 0.02 ms (filterscopes) to 20 ms (equilibrium). The analysis
grid is the intersection window sampled at 1000 inclusive points, so Δt **varies
by discharge** across 4.1–6.0 ms. Signals denser than the grid are
block-averaged (anti-aliased); sparser ones are linearly interpolated. The
grouping unit is the discharge.

## E — uncertainty model · NOT INSTANTIATED

No per-signal measurement-uncertainty metadata exists in any artifact — not in
the archives, the metadata files, the provider code, or the provenance ledger.

Declaring E absent is deliberate. Supplying a plausible default would propagate
an unevidenced assumption into every downstream weighting and confidence
statement while looking like knowledge.

## Π — provenance · PARTIALLY INSTANTIATED

**Documented and code-verified:** cleaning (float64, finite drop, stable sort,
dedupe); common-window intersection; grid construction; the block-average versus
interpolation rule; three numerical realizations (unsmoothed; quintic spline,
s=0.1; RTS, R=1, Q=1e-4); within-discharge z-score standardisation with ddof=0
and no pooled statistics.

**Unresolved:** the upstream resampling pipeline that produced the archive
(effects documented, code absent); the equilibrium reconstruction and its inputs
and constraints; physical units for every quantity.

## A — admissibility · NOT INSTANTIATED

Admissibility is task-conditioned. No reconstruction target has been selected at
S7.1, so no target-dependence classification has been or may be performed. The
object is fixed **before** any task-conditioned rule is permitted to reshape it —
which is the point of separating this stage.

## Gate

| Assertion | Value |
|---|---|
| target selected | no |
| ontology generated | no |
| coordinates generated | no |
| regression run | no |
| canonical artifact modified | no |

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
