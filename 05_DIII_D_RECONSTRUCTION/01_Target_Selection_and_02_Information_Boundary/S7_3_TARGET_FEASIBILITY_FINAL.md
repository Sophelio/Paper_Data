### S7.3 Target Feasibility And Information-Boundary Selection

#### Candidate Target Set

The classes of quantity eligible to serve as a reconstruction target were fixed
before any signal value was inspected, and were not revisited afterwards. Only
directly measured quantities and diagnostic reconstructions with a resolved
physical meaning and unit were admissible. Actuator commands were excluded
because reconstructing one describes the control system rather than the plasma;
equilibrium reconstruction outputs were excluded because their lineage is only
partially resolved; and two channels documented upstream as uncalibrated
digitiser output were excluded because a reconstruction error expressed in an
undefined unit cannot be interpreted.

Applying these frozen classes to the ninety-five archived quantities left
sixty-four candidates. The count follows from the class policy; it was not
chosen.

#### Development-Only Feasibility

Feasibility was assessed on the twenty development discharges alone. The
forty-two external discharges were known only as identifiers; their archives
were never opened, and this was enforced in code and recorded in a complete
access log.

Every statistic computed at this stage concerns the candidate target by itself.
No relationship between a target and any predictor was examined, no model was
fitted, and no baseline was evaluated. Ranking a target by how well it can be
predicted would have made the selection depend on the outcome it is meant to
precede.

Target values were converted to canonical units before any statistic was formed,
and were represented on the analysis grid that the frozen resolution policy
would actually produce for that candidate, so that feasibility was never
measured on a finer grid than the study will use.

Two criteria did work. Variation was assessed by a robust, zero-safe relative
statistic — the scaled median absolute deviation divided by the root mean
square, taken as the median across development discharges — which is defined for
quantities whose mean lies near zero or whose trajectory changes sign, where an
ordinary coefficient of variation is not. Two candidates fell below the
predeclared floor: both are flat-top quantities whose variation is a few tenths
of a percent of their magnitude, for which a constant predictor would be nearly
exact by construction. Separately, every candidate was required to admit valid
normalised scoring on all sixty development evaluation blocks, which requires a
non-degenerate calibration scale in each.

Sixty-two of the sixty-four candidates satisfied all twelve criteria.

#### Provenance-Closed Boundaries

A separate information boundary was instantiated for every candidate before any
ranking took place, so that no candidate could be advantaged by a boundary drawn
after its properties were known.

Each boundary removes the target itself, any duplicate or alias, any quantity
whose definition contains it, any quantity with verified upstream dependence on
it, and any quantity whose ancestry relative to it cannot be resolved. The last
rule fails closed: absence of evidence of dependence is not evidence of
independence. Statistical association was never used, in either direction —
neither to exclude a quantity nor to admit one.

Where a candidate belongs to a series of channels measuring the same physical
quantity, the remaining channels of that series are excluded from the primary
boundary, since reconstructing one channel from its neighbours is spatial
interpolation rather than relational structure. A shared diagnostic system is
not by itself such a series: rotation and ion temperature from the same
charge-exchange system are different physical quantities and were treated as
separate series. Because that reading could in principle affect the ranking, the
alternative was evaluated explicitly and shown to leave the outcome unchanged.

#### Deterministic Target Selection

Among candidates satisfying every criterion, the target was selected by a rule
frozen in advance, applied lexicographically: fewest major provenance or
numerical qualifications attaching to the target itself; then the largest number
of provenance-certified explanatory quantities surviving the boundary; then the
greatest number of distinct scientific families among them; then the largest
margin above the variation floor; and finally, to guarantee a unique outcome,
the lowest index in the frozen signal inventory.

No weighted score was formed, no ranks were normalised and combined, and no
human preference was exercised. The rule's ordering is consequential: the
candidate with the largest variation margin ranks third, because it belongs to a
channel series and its boundary is correspondingly narrower.

#### Selected Reconstruction Target

The selected target is the **surface loop voltage**, a directly measured
electromagnetic quantity recorded in volts at a native cadence of twenty
milliseconds. None of the object's signal-specific major qualifications attaches
to it; the two object-wide limitations — an absent upstream resampling
implementation and the absence of any uncertainty model — attach to every
quantity equally.

It was resolved at the fourth level of the rule, having tied with line-averaged
electron density on qualifications, surviving explanatory quantities and family
breadth, and separated on variation margin.

Its development-only feasibility is unremarkable in the way the contract
requires: variation comfortably above the floor and present in every development
discharge, no degenerate discharge, no invalid evaluation block, and
availability across both upstream processing eras.

Nothing about its reconstructability has been examined. No reconstruction has
been attempted.

#### Final Information Boundary

Of the ninety-five archived quantities, sixteen were removed: the target itself,
and the fifteen equilibrium reconstruction outputs whose ancestry relative to the
target cannot be certified. No duplicate, definitional descendant, verified
dependent or channel sibling arose for this target.

**Seventy-nine** provenance-certified primitive explanatory quantities survive,
spanning **seven** distinct scientific families: electron-temperature channels,
charge-exchange rotation and ion temperature, neutral-beam injection, magnetics,
filterscope emission, gas injection, and density.

Two of the survivors remain permanently typed as uncalibrated, and eighteen
carry an aliasing qualification inherited from their upstream downsampling;
both are recorded per quantity and constrain later construction rather than
admissibility.

The analysis cadence implied by this admitted set is twenty milliseconds, set by
the coarsest admitted quantity. Finer channels are aggregated down to it. The
alternative — interpolating the coarser quantities onto a finer grid — would
manufacture resolution the observations do not contain, and is excluded by the
frozen policy.

#### Gate To Mathematical Interpretation

No relational coordinate or reconstruction model had yet been generated. S7.4
interprets the frozen task-admissible record mathematically; ontology generation
begins only in S7.5.
