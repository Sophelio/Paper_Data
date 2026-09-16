### S7.5H Primitive-Space And Ontology Hardening

#### Motivation

The task-admissible observational record is dominated numerically by
repeated-channel instrumentation. Of the seventy-eight admissible quantities,
forty are channels of a single electron-temperature radiometer and fourteen are
chords of a single charge-exchange system. Because the relational grammar builds
coordinates from pairs of primitives, a diagnostic that contributes many similar
channels contributes quadratically many candidate coordinates, and can occupy a
disproportionate share of the combinatorial weight of the ontology for reasons
of instrumentation design rather than of physics.

This is not a statement that many channels are bad data. A well-instrumented
profile diagnostic is valuable, and every channel remains a legitimate
observation. The concern is only that channel multiplicity should not, by
itself, determine how much of the search space a single diagnostic family
occupies.

The hardening stage therefore tests a different architectural balance: a
smaller, target-blind, non-redundant primitive basis combined with a broader but
still low-order constructor grammar. Both choices were fixed before any
reconstruction model existed.

#### Target-Blind Redundancy Hardening

Compression was permitted only within groups of quantities that are genuinely
repeated measurements of the same scientific quantity — same family, same
physical dimension, same measurement class, and a documented channel series
rather than distinct actuators. Four such groups were identified from frozen
metadata alone: the electron-temperature channels, the charge-exchange rotation
chords, the charge-exchange ion-temperature chords, and the filterscope
channels. Neutral-beam lines, gas valves, magnetics and the pedestal-fit
parameters were ruled ineligible before any value was examined, because
correlation between distinct actuators or distinct physical quantities is not
redundancy.

Within eligible groups, a pair was declared stably near-redundant only if the
magnitude of its correlation was at least 0.99 in the median and at least 0.97
in the tenth percentile across all development discharge and calibration-block
cells, with consistent sign, on at least ninety per cent of cells. These
thresholds were frozen and hashed before any value was opened. Representatives
were then chosen by a deterministic rule, and a channel could be deferred only
on a direct witness to its own representative; transitive chains were not
sufficient.

**Density values were never read.** No correlation with the target, no mutual
information, no feature importance, and no model of any kind entered the
procedure. A signal could not be removed because it seemed unlikely to matter
for density; scientific plausibility may later inform search priority, but it is
not an admissibility criterion.

#### Hardened Primitive Basis

Of eight hundred and twenty-eight within-group pairs, nine met the frozen
criterion, deferring eight channels: seven adjacent electron-temperature
channels and one filterscope channel. The hardened basis therefore contains
seventy primitives.

Neither charge-exchange group yielded a single qualifying pair, and all fourteen
chords are retained.

The reduction in instrumentation dominance is small. The
electron-temperature share of the primitive basis falls from 51.3 per cent to
47.1 per cent. A target-blind audit of the linear effective rank of each group
suggests far lower dimensionality than the number of retained representatives —
around three components for ninety-five per cent of the variance in the
electron-temperature group, against thirty-three retained channels. That
disagreement is recorded and was deliberately not acted upon: the frozen
criterion is pairwise and conservative, and a group may have low collective rank
while no individual pair meets a direct-witness threshold. Replacing observed
channels by variance components would also abandon scientifically legible
primitives, which the ontology exists to preserve.

#### Expanded Relational Grammar

The constructor catalogue was broadened from five families to nine, prospectively
and before the resulting primitive count was known. The original families —
levels, first temporal derivatives, pairwise products, pairwise ratios, and
trajectory-relational derivatives — are joined by a unary reciprocal, a
level–rate interaction, a rate-over-level relation, and a level-over-rate
relation.

The three new pairwise families fill a gap in the previous grammar, which
related levels to levels and rates to rates but never a level to a rate. Their
self-operand cases are physically familiar: a rate divided by its own level is a
fractional or logarithmic rate, and a level divided by its own rate is a local
characteristic timescale.

Maximum construction depth remains one. The new families are primitive-pair
constructors with an internal declared rate operator; they do not consume
constructed coordinates, and are not recursive. The derivative realisation, the
relation template, the support-size bound, the treatment of uncalibrated and
interpolated quantities, and the propagation of dimensional, temporal and
provenance metadata are all unchanged.

Because the four new families are pairwise, the hardened ontology is
substantially larger than the one it supersedes — roughly twenty-four thousand
symbolic coordinates against thirteen thousand six hundred — despite using ten
per cent fewer primitives. Narrowing the basis did not offset broadening the
grammar.

#### Full Versus Primary Ontology

The full seventy-eight-primitive ontology is preserved unmodified as an extended
sensitivity ontology. The eight deferred channels are recorded as
redundancy-deferred, which is neither a claim of scientific inadmissibility nor
of irrelevance to the target, and they remain available for later sensitivity
analysis.

An additional diagnostic ablation was frozen but not run: a raw linear model on
the hardened primitive levels alone. Together with the unchanged full-information
raw comparator, it separates the effect of narrowing the primitive space from
the effect of relational coordinate construction on the same information. The
mandatory comparator itself was not weakened.

#### Gate To S7.6

The hardened ontology fixes a smaller target-blind primitive basis and a broader
low-order relational grammar before any reconstruction model is fitted. S7.6
instantiates and numerically qualifies the resulting atomic coordinate universe.
