### S7.5 Typed Relational Ontology

#### Primitive Coordinate Types

All seventy-eight task-admissible quantities enter the ontology as primitive
level coordinates. Each carries its scientific dimension class, canonical
physical unit, origin classification, provenance status, temporal-resolution
qualification and any aliasing or upsampling flag, and a constructed coordinate
inherits that metadata through explicit propagation rules rather than by
convention.

Dimensional typing is applied at the level of individual quantities rather than
of the organizational blocks introduced in the previous stage. Three of those
eight blocks are dimensionally heterogeneous, and the forty-eight quantities
sharing an energy dimension are distributed across three different blocks, so
block membership carries no dimensional guarantee.

Two quantities are documented upstream as uncalibrated. They remain admissible
as levels, where no dimensional argument is required of them, but they are
excluded from every constructed coordinate, because the dimensional type of a
construction containing them could not be certified. This is a fail-closed
typing decision and not a claim that they carry no information.

#### Coordinate Constructors

The primary grammar is deliberately low-order and contains five constructor
families: primitive levels; first temporal derivatives; pairwise products;
pairwise ratios; and pairwise trajectory-relational derivatives, abbreviated
throughout this work as phase derivatives.

Every constructor acts directly on primitives. No constructor consumes another
constructed coordinate, so recursive constructions — a derivative of a product,
a ratio of ratios, a product of phase derivatives — are outside the primary
grammar by rule rather than by omission.

Products are commutative and are canonicalised by operand ordering, so a product
and its transpose are one coordinate rather than two; self-products are the
canonical equal-operand case. Ratios and phase derivatives are directional and
are partial maps, defined where their denominators are non-zero; the degenerate
self-cases are excluded because they are constant. Denominator shifts,
regularising offsets and bounded reciprocal transforms are not admitted into the
symbolic coordinate definitions: they are different constructions, and the
numerical conditioning of an instantiated ratio is handled where instances are
evaluated, without redefining the constructor.

Pairwise sums and differences are absent by design. The relation template is
affine-linear in the selected coordinates, so a sum or difference of two
primitives is already representable by including both with appropriate
coefficients; introducing them as coordinates would enlarge the candidate set
without enlarging the span of the relation family. The exclusion is an
algebraic-redundancy argument, not a performance result.

A representation whose coordinates are all primitive levels is an admissible
special case of the ontology. The raw-coordinate comparator is therefore nested
inside the relational search space rather than standing outside it, which is
what makes the eventual comparison a statement about representation rather than
about two different frameworks.

#### Numerical Realization Of Derivatives

Derivative-valued coordinates are constructed through a single declared
realization: a second-order finite difference taken with respect to actual
physical time, using each discharge's own analysis support rather than an
assumed common spacing. The realization carries no fitted smoothing parameter,
involves no target values, uses no stencil that crosses a discharge boundary,
and is never taken with respect to the normalized validation coordinate.
Smoothed alternatives belong to the later sensitivity qualification, not to the
primary ontology.

The realization was verified on synthetic data at the representative discharge
cadences, reproducing second-order convergence exactly.

This makes explicit a distinction established in the previous stage: a
derivative coordinate is a constructor acting through a declared numerical
realization of a sampled trajectory, and not evidence that the observations
possess an exact classical derivative. Six quantities that the archival pipeline
interpolated upward remain admissible as levels but have their derivatives
labelled sensitivity-only and excluded from the primary grammar, since a
derivative of an interpolated series reports the interpolant.

#### Dimensional And Provenance Typing

Each constructor has an explicit output dimension: a derivative divides by time,
a product multiplies dimensions, and a ratio or phase derivative divides them,
so that the time dimensions of a phase derivative cancel and its type is the
ratio of its operands' types. Numerical standardization applied later does not
alter a coordinate's scientific type.

Temporal qualifications propagate conservatively: a constructed coordinate is
limited by the coarser resolution of its operands, and no construction may claim
temporal information finer than either input. Aliasing qualifications propagate
from any operand to the output, and no high-frequency claim may rest on a
coordinate carrying one.

Every coordinate retains an exactly recoverable set of primitive ancestors, and
target independence is transitive: a coordinate is forbidden if any ancestor is.
One exact deterministic relation among the admitted quantities — an aggregate
beam power equal to the sum of its per-line components — is retained as an
explicit dependency group rather than resolved by deletion, so that a later
stage can prevent a representation from counting the same information twice
without discarding either form now.

#### Reconstruction Relation

The relation template is affine-linear in the selected coordinates, with an
intercept that does not count toward the representation size, a coordinate
support shared across all discharges, and coefficients estimated per discharge.
Because a coefficient carries the ratio of the target dimension to its
coordinate's dimension, coordinates within one relation need not share physical
units. Where a coordinate is uncalibrated its coefficient remains numerically
admissible but carries no physical dimensional interpretation, and this is
recorded rather than left implicit.

The relation family is frozen here; the numerical estimator is not, and no
estimator was run.

#### Gate To Admissible-Universe Construction

`G_rec` defines the grammar of scientifically admissible relational
constructions but does not yet instantiate their finite task-specific universe.
S7.6 applies these constructor and typing rules to the seventy-eight primitives
to form `A_rec`.
