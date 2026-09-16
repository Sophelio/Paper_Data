### S7.6 Admissible Coordinate–Relation Universe

#### Coordinate Instantiation

The frozen grammar was instantiated mechanically. Applying the five constructor
families to the seventy-eight task-admissible primitives, at the frozen maximum
construction depth of one and with the frozen operand-eligibility rules,
produces exactly **13 604** symbolic coordinate instances: seventy-eight levels,
seventy first temporal derivatives, 2 926 pairwise products under canonical
operand ordering, 5 700 directed pairwise ratios, and 4 830 directed
trajectory-relational derivatives. The count reproduced the combinatorial
prediction of the previous stage exactly, before any coordinate value was
examined. Six further derivatives of upstream-interpolated quantities were
instantiated separately as sensitivity-only constructions and were never
admitted to the primary universe.

#### Instance-Level Admissibility

Admissibility was then applied in the frozen order: information-boundary
compliance, provenance, dimensional typing, semantic expressibility, temporal
resolution, numerical support, denominator conditioning, and leakage. The first
five are decidable from metadata alone and rejected nothing, confirming that the
instantiation faithfully reproduced the ontology's own eligibility rules.

Numerical support was evaluated using development predictor values only, on the
calibration intervals of the three frozen evaluation blocks in each of the
twenty development discharges. A coordinate had to be finite and non-constant on
every one of those sixty intervals. Constancy was tested exactly rather than
against a tuned variance threshold. Four beam-power channels are constant on at
least one required interval — two of them never fired anywhere in the cohort —
and they, their derivatives, and constructions built from them were rejected on
that basis alone.

No coordinate was rejected for having a large but finite magnitude. Products of
quantities in different physical units are legitimately large numbers, and
pruning them would have been a conditioning preference rather than an
admissibility rule.

#### Partial Coordinate Domains

Ratios and trajectory-relational derivatives are partial maps: they are defined
only where their denominators stay away from zero. The governing principle was
frozen in the reconstruction contract, but its numerical constants had never
been instantiated. That specification was completed and hashed before any
coordinate value was inspected, so that no threshold could be chosen in
knowledge of how many candidates it would admit.

A denominator is admissible on a calibration interval when it is finite, does
not change sign, and has a minimum absolute value of at least five per cent of
its root-mean-square scale on that interval; a coordinate is admissible only if
its denominator satisfies this on every required interval. No shifted, bounded,
clipped or otherwise regularised denominator is permitted, because those are
different coordinate constructions and none was frozen as a primary
constructor.

Forty-six of the seventy-six candidate ratio denominators satisfy the rule,
leaving 3 266 admissible ratios. The failures are physically legible: toroidal
rotation reverses sign, filterscope and gas-valve signals pass through zero
between events, and beam powers switch off entirely.

**No trajectory-relational derivative is admissible.** None of the seventy
candidate denominators — each a time derivative — survives, and almost all fail
by sign change. A time derivative changes sign at every local extremum of its
source, and over a calibration interval spanning most of a discharge
essentially every plasma quantity rises and falls at least once.

This is a statement about the instance-level domain requirement of this task on
this observational object. It is not a search result and carries no information
about predictive value: nothing was fitted, and no coordinate was compared with
the target at any point. The constructor remains part of the ontology; what the
admissible universe records is that no instance of it satisfies the frozen
domain rule here.

The same domain rule is frozen prospectively for external application. Should a
selected coordinate fail its domain predicate on an unseen discharge, it may not
be shifted, regularised or replaced, and the support may not be refitted; the
representation is simply recorded as not applicable there, and whether the
claimed domain survives is decided at qualification.

#### Exact Dependency Constraints

One deterministic relation holds among the admitted quantities: the aggregate
beam power is the exact sum of its eight per-line components. That identity
propagates through every construction that is linear in the aggregate with all
other context held fixed — levels, derivatives, products against a common
factor, and ratios or trajectory-relational derivatives with the aggregate in
the numerator — but not through constructions with the aggregate in the
denominator, where no such identity exists.

Neither the aggregate nor the component form is privileged, and no coordinate is
deleted for belonging to such a family. The constraint acts on representations
rather than coordinates: a candidate support may contain the aggregate together
with some components, but not together with all eight restatements in the same
linear context. Deterministic restatements must not be counted as independent
evidence.

On this object all such groups are, in the event, empty of consequence: four of
the eight components are numerically inadmissible, so no admissible
representation can contain a complete group. The constraint remains active and
would bind immediately under any revision that restored those components.

#### Factorized Representation Of `A_rec`

Six thousand and thirty-four atomic coordinates survive. The number of candidate
supports of size one to twelve drawn from them is a thirty-seven-digit integer,
and materialising them would be pointless as well as impossible.

The admissible universe is therefore represented factorially, by the atomic
coordinates together with the predicates that define an admissible support. This
representation is exact rather than approximate: membership of any candidate
support is decidable directly, and nothing about the universe is left implicit.
The predicates constrain size, membership, duplication, sensitivity-only status,
exact dependency and target exclusion, and deliberately impose no preference
for any constructor family or scientific family.

#### Gate To Search

`A_rec` defines what may be searched. No search priority or empirical preference
has yet been assigned, no estimator has been fitted, and no coordinate has been
compared with the reconstruction target. S7.7 freezes the search policy and
constructs the actually explored frontier `Ahat_rec`.
