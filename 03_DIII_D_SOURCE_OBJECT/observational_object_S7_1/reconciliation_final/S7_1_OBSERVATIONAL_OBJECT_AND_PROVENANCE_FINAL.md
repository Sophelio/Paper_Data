### S7.1 Observational Object And Provenance Census

#### Finite DIII-D Observational Object

The observational object underlying this study is a finite, provenance-bearing
collection of tokamak discharges from the DIII-D device. It comprises **62
discharges**, each represented by an archived multi-signal record containing
**95 distinct scientific quantities**. Every one of the 95 is present in all 62,
so the object is complete in the signal × discharge sense, and every one of the
5890 resulting series is finite throughout.

The cohort was assembled upstream of this study. Its documented inclusion
criterion is that the archival pipeline could construct a common temporal grid
across all 95 signals for a given discharge. The selection algorithm itself, and
the parent population from which these discharges were drawn, are not recorded
in any available artifact. The cohort is therefore treated as the complete
finite object available to this study, and explicitly not as a random or
representative sample of DIII-D operations.

A historically important subset of eight quantities carried the earlier analyses
in this project. That subset is a small part of the object, not its definition.
The remaining 87 quantities are equally present in the archive and equally
available; they were excluded from earlier work by convention rather than by any
documented scientific reasoning. Recording this explicitly matters, because the
observational object must be fixed before any task-conditioned admissibility
rule is permitted to reshape it.

#### Signal Families And Multirate Structure

The 95 quantities fall into eight documented families: electron-cyclotron-emission
temperature channels (40), equilibrium and shape quantities (15),
charge-exchange recombination rotation and ion temperature (14), neutral-beam
channels (10), magnetics (5), filterscope D-alpha channels (4), gas injection
(4), and density quantities (3).

Native sampling densities span **three orders of magnitude**, from filterscope
channels at approximately 0.02 ms to equilibrium quantities at exactly 20.0 ms.
This multirate structure is the central structural fact about the object: any
common grid must either discard information from the fast channels or
interpolate the slow ones.

#### Backend And Archive Consistency

All 95 quantities were verified accessible through the analysis backend used for
this study. Accessibility was established on three independent grounds: the
backend's signal catalogue matches the frozen archive manifest exactly, in
order; the backend and the reference loader share an identical loading routine
operating on the same archive files; and twelve signal × discharge fetches
through the live backend, spanning both upstream processing eras and all eight
signal families, agree with the reference loader exactly on sample count,
minimum and maximum.

#### Units And Semantic Types

A frozen units registry covers all 95 quantities. Ninety-three carry a physical
unit; the remaining two are documented upstream as uncalibrated digitiser
output, for which no physical unit exists. They are recorded as resolved
unit-less rather than as missing. The forty electron-temperature channels are
recorded in keV on explicit domain authority, and are labelled as expert
assignment rather than as recovered metadata.

Three unit-scale inconsistencies exist within the object and are documented
rather than silently harmonised: total injected beam power is stored in kW while
the per-beamline channels are in W; core density is stored in cm⁻³ while the
pedestal density is in m⁻³; and the electron-temperature channels are in keV
while the ion-temperature and pedestal-temperature channels are in eV. Because
standardisation is applied within each discharge, these differences are
invisible to any downstream statistic, and they become significant only when a
construction forms ratios, sums, or dimensional types across the affected pairs.

Unit knowledge and provenance knowledge are recorded separately. A quantity may
have a well-documented unit while its upstream reconstruction remains only
partially resolved, and fifteen quantities are in exactly that position.

#### Sampling, Alignment And Numerical Realization

Each discharge is stored with per-signal native time axes in milliseconds. The
analysis-ready series are produced by intersecting the requested signals' time
ranges and laying a fixed count of 1000 inclusive points across that common
window. Signals denser than the resulting grid are block-averaged before
placement, so fast transients are anti-aliased rather than point-sampled;
signals sparser than the grid are linearly interpolated.

Because the point count is fixed while the window varies by discharge, **the
grid spacing is not fixed**. For the historical eight-signal surface it ranges
from approximately 4.1 to 6.0 ms, with a median of 4.97 ms; over all 95
quantities the common window narrows and the spacing becomes approximately 3.8
to 5.4 ms. Any statement of a uniform 20 ms analysis step is not supported by
the artifacts: 20 ms is the native resolution of the coarsest, equilibrium-class
signals, and is separately the spacing that a provider gridding to the coarsest
requested signal would produce.

One consequence follows directly and is carried forward as a constraint. The
equilibrium quantities are natively sampled at 20.0 ms and are placed on a grid
roughly four times finer, so four of every five grid points on those quantities
are interpolated rather than reconstructed. Any derivative-valued coordinate
built over them is therefore governed by the interpolation scheme rather than by
the equilibrium reconstruction.

Three numerical realizations of the same quantities exist — unsmoothed, quintic
spline, and a fixed-interval smoother. These are alternative numerical
realizations, not different scientific quantities, and they are not treated as
observational uncertainty.

#### Provenance And Derived Quantities

A stored column is not necessarily a primitive measurement. Classification used
only evidence available in the study's own materials. Fifty-seven quantities are
diagnostic reconstructions, fifteen are equilibrium-derived, fourteen are
actuation or control quantities, and nine are direct measurements. Separating
actuation from diagnosis matters: the gas channels are valve command voltages
and the beam channels are actuator outputs, and neither is a measurement of the
plasma.

The two most defensibly direct quantities are the two documented upstream as
raw, uncalibrated digitiser output — the least processed signals in the object
are also the only ones without a physical unit.

The analysis-side transformation chain is verified against the implementing
code. Two elements of the lineage are not. The upstream resampling that produced
the archive is documented per signal and per discharge — method, category, and
original and resampled sample counts are recorded for all 5890 pairs — but the
implementing code is absent. The equilibrium reconstruction family is identified
as EFIT, named explicitly in two of the fifteen quantity descriptions, but its
settings, inputs and constraints are not present in any available artifact.

Throughout, statistical association was never admitted as evidence of ancestry,
a discipline adopted deliberately because an earlier audit in this project
demonstrated that conflating the two produces both false leakage findings and
false clearances.

#### Instantiation Of O

| Component | Instantiation |
|---|---|
| **D** — scientific data | 95 scalar time-series quantities, complete across 62 discharges, with archive, canonical and backend identities in one-to-one correspondence |
| **Ω_obs** — observational support | DIII-D; 62 discharges; per-signal millisecond time bases; a documented inclusion criterion but an unrecorded selection algorithm and unknown parent population |
| **S** — sampling structure | discharge as the primary realization unit; native spacings from 0.02 to 20.0 ms; a discharge-specific 1000-point common grid; eight channel families with channel-local identity |
| **E** — uncertainty | **not instantiated**; no measurement-error metadata exists and none was invented |
| **Π** — provenance | **partially instantiated**; the analysis-side chain is code-verified, the upstream resampling operation is documented but its code absent, and the equilibrium reconstruction is identified only at family level |
| **A** — ancillary information | **partially instantiated**; per-signal resampling records for all 5890 pairs, family membership, channel identity, units, and cohort annotations. Absent: uncertainty, calendar dates, regime labels, and event annotations |

Declaring the uncertainty model absent rather than supplying a plausible default
is deliberate. An error model asserted without evidence would propagate silently
into every downstream weighting, qualification and confidence statement.

Admissibility is not a component of the observational object. It is an attribute
of the task contract and enters later, through the task-specific information
boundary and the admissible coordinate-relation universe.

#### Boundary Of The Scientific Claim

O is the frozen archived and resampled observational object. It is not a claim
to reproduce the complete native DIII-D acquisition chain.

This scoping is load-bearing. The archive is itself the product of an upstream
resampling whose implementation is unavailable, and eighteen quantities were
downsampled by interpolation with no anti-aliasing stage, so content above the
new sampling limit is not separable from signal. Relational analysis of the
frozen object, comparisons among coordinates constructed from it, and
reproducible downstream processing are all supported. Claims about native
high-frequency physics, about exact raw-diagnostic bandwidth, or about
derivative structure near the archived resolution limit are not, and are not
made.

The cohort spans seven ordered operational periods and contains two distinct
upstream processing regimes, which any later claim of cross-discharge
generality must accommodate.

#### Gate To Task Conditioning

At this stage no reconstruction target, task-specific information boundary,
relational ontology, search policy or validation protocol had been defined.
These enter only after the observational object is frozen.
