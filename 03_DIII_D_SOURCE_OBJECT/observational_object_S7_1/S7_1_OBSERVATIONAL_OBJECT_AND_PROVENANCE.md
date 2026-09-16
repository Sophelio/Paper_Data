# S7.1 Observational Object and Provenance Census

## Observational Scope

The observational object underlying this study is a finite, provenance-bearing
collection of tokamak discharges from the DIII-D device. It comprises **62
discharges**, each represented by an archived multi-signal record containing
**95 distinct scientific quantities**. Every one of the 95 quantities is present
in all 62 discharges, so the object is complete in the signal × discharge sense.

The cohort was assembled upstream of this study. Its documented inclusion
criterion is that the archival pipeline could construct a common temporal grid
across all 95 signals for that discharge. The exact selection algorithm, and the
parent population from which these 62 were drawn, are not recorded in any
available artifact. The cohort must therefore be treated as a **convenience
sample of unknown provenance with respect to operating regime**, not as a random
or exhaustive sample of any physical class of discharge.

## Source Data and Discharge Cohort

Each discharge is stored as an array archive in which every signal carries its
own independent time axis, recorded in milliseconds. Native sampling densities
span roughly three orders of magnitude, from fast filterscope channels at
approximately 0.02 ms to equilibrium quantities at approximately 20 ms.

The authoritative discharge list is a hard-coded set of 62 identifiers held in
the study's data-access layer and corroborated by an independent per-discharge
ledger and by the feature-export inventories. All three sources agree exactly.

No date range, campaign identifier, or operating-regime label is recorded for
any discharge in the available artifacts. Regime labels are therefore **not**
assigned; inferring them from the signal traces would constitute interpretation
rather than provenance.

## Signal Inventory

The 95 quantities fall into eight documented groups:

| Group | Count |
|---|---|
| Electron-cyclotron-emission temperature channels | 40 |
| Equilibrium and shape quantities | 15 |
| Charge-exchange recombination rotation and ion temperature | 14 |
| Neutral-beam injection channels | 10 |
| Magnetics | 5 |
| Filterscope (D-alpha / ELM marker) channels | 4 |
| Gas injection channels | 4 |
| Density quantities | 3 |

A historically important subset of eight quantities — diamagnetic stored energy,
injected neutral-beam power, density, plasma current, normalised beta, the
safety factor at the 95% flux surface, internal inductance, and elongation — has
carried prior analyses in this project. **That subset is a small part of the
object, not its definition.** The remaining 87 quantities are equally present in
the archive and equally available to subsequent stages. Recording this
explicitly matters: the observational object must be fixed before any
task-conditioned admissibility rule is permitted to reshape it.

## Direct, Reconstructed and Derived Quantities

A stored column is not necessarily a primitive measurement. Each quantity was
classified using only evidence available in the study's own materials:

| Classification | Count | Basis |
|---|---|---|
| Diagnostic reconstruction | 54 | the temperature-profile and charge-exchange groups are labelled as profile and inference products |
| Unknown | 26 | magnetics, density, filterscope, gas and beam groups: group membership is documented, but whether each entry is a raw sensor signal or a compensated/derived quantity is not established by any available artifact |
| Equilibrium-derived | 15 | the equilibrium and shape group consists of reconstruction outputs |

No quantity is currently classifiable as a proven direct measurement. This is a
statement about the completeness of the record, not a claim that no direct
measurements exist in the archive. Where classification could not be supported
by evidence, `UNKNOWN` was recorded rather than inferred.

The equilibrium group deserves particular care. Its members are outputs of an
equilibrium reconstruction whose implementation, inputs and constraints are not
present in any available artifact. Their ancestry can therefore be asserted only
at group level and with explicitly limited confidence.

## Temporal Alignment and Numerical Realization

The transformation chain from archive to analysis-ready series is documented and
was verified against the implementing code:

1. **Upstream resampling.** An external pipeline produced the archived series.
   Per-signal resampling method and category are recorded, but the pipeline
   itself is not available. This is the deepest unresolved element of the
   lineage.
2. **Cleaning.** Cast to double precision; non-finite samples dropped; stable
   sort by time; duplicate and non-increasing timestamps removed.
3. **Common window.** The analysis window is the intersection of the requested
   signals' time ranges.
4. **Grid construction.** A uniform grid of 1000 inclusive points spans that
   window. Because the window varies by discharge, the grid spacing is **not
   fixed**: it ranges from approximately 4.1 to 6.0 ms. Any statement of a
   uniform 20 ms analysis step is not supported by the artifacts.
5. **Alignment.** Signals denser than the grid are block-averaged before
   placement, so fast transients are anti-aliased rather than point-sampled;
   sparser signals are linearly interpolated.
6. **Numerical realization.** Three variants exist: unsmoothed, quintic spline
   smoothing, and a fixed-interval smoother. These are alternative numerical
   realizations of the same scientific quantities, not different quantities.
7. **Standardisation.** Where applied, standardisation is computed **within each
   discharge**, along the time axis, with no pooled statistics across
   discharges.

## Provenance Graph

An explicit dependency graph was constructed. Edges record only real
dependencies, each annotated with its evidence and a confidence level ranging
from code-verified to strongly-inferred to unresolved. Statistical association
was never admitted as evidence of ancestry — a discipline adopted deliberately,
because a previous audit in this project established that conflating the two
produces both false leakage findings and false clearances.

The graph is honest about its own limits. The upstream resampling operation
appears as a node with documented effects but unresolved implementation, and the
equilibrium reconstruction appears as a node whose inputs are entirely unknown.

## Missingness and Availability

Availability is complete at the signal × discharge level: all 95 quantities are
present in all 62 discharges. Per-signal finite fractions, sample counts,
temporal extents, native spacings, dynamic ranges, repeat ratios and simple
outlier counts were computed descriptively for every signal in every discharge.

These are quality-control descriptors only. No signal was ranked by usefulness,
because usefulness is a task-conditioned notion and no task has been defined.

## Unresolved Provenance

Eight items remain unresolved, three of them critical:

- the identity and algorithm of the **upstream resampling pipeline**, on which
  the entire object rests;
- the **physical units** of every quantity, which are recorded nowhere and must
  not be invented;
- the **equilibrium reconstruction** that produced fifteen of the quantities,
  together with its inputs and constraints.

Three further items are major: the absence of any measurement-uncertainty
metadata, the unknown cohort-selection algorithm, and the unestablished status
of the magnetics group as raw or compensated.

## Instantiation of the Scientific Object O

Instantiating the formal object requires care, and one component of that care is
negative. Two of its six components **cannot** be instantiated from the data as
possessed:

| Component | Status |
|---|---|
| Data channels | Instantiated — 95 quantities, complete across 62 discharges |
| Observational support | Instantiated — 62 DIII-D discharges, per-signal millisecond time bases |
| Sampling structure | Instantiated — native spacings, common-window grid, discharge as grouping unit |
| Uncertainty model | **Not instantiated** — no uncertainty metadata exists |
| Provenance | **Partially instantiated** — the analysis-side chain is documented; the upstream pipeline and equilibrium reconstruction are not |
| Admissibility | **Not instantiated** — admissibility is task-conditioned and no task exists yet |

Declaring the uncertainty model absent rather than supplying a plausible default
is deliberate. An error model asserted without evidence would propagate silently
into every downstream weighting, qualification and confidence statement.

## Consequences for Subsequent Task Conditioning

Three consequences follow for the stages that come next.

First, the object is substantially larger than the eight quantities that carried
earlier analyses, and the additional 87 have not been excluded by any documented
scientific reasoning — only by historical convention.

Second, the absence of units and of an uncertainty model constrains what a typed
ontology can express. Dimensional consistency cannot presently be checked, so
either units are recovered or the ontology must be constructed without
dimensional typing and that limitation stated.

Third, fifteen equilibrium quantities have unresolved ancestry. Any future
admissibility rule that turns on upstream dependence will be undecidable for
those quantities on present evidence, and they will have to be treated
conservatively or the lineage recovered.

No reconstruction target, task-specific information boundary, or relational
ontology was defined at this stage.

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
