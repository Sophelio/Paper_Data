### Predictor-Side Admissibility Reconciliation

#### A Restriction Stronger Than The Claim

The Epoch-2 protocol as first frozen forbade held-out predictor ranges from
influencing which coordinates a fold's search could consider. That restriction is
appropriate to an inductive-transfer task, in which the distribution of future
predictors is genuinely unknown. It is stronger than the claim actually frozen
for this epoch, which is a reconstruction claim over a finite observational
object of sixty-two discharges.

Two pieces of the frozen lineage make the mismatch concrete rather than a matter
of taste. The sibling partial-map condition — denominator admissibility, frozen
long before — was always an application-time predicate: a selected support
containing a partial-map coordinate must satisfy the rule on each block where it
is applied, and was never required to be forecastable from development data
alone. And the revised contract's own coverage policy cited, as its feasibility
evidence, the three thousand four hundred and fifty-one coordinates certified
range-supported across all sixty-two discharges, reasoning that a search
restricted to them would yield fully supported supports by construction. The
protocol had imposed a blinding that the contract it implemented did not ask for.

#### Two Information Roles

The reconciliation separates two roles that the earlier protocol had merged.

Predictor-side admissibility asks whether a coordinate is observationally
applicable over the intended domain. Because the intended domain *is* the finite
object, that question is answerable from the object's predictor side. It is
target-blind, error-blind and performance-blind, and it governs the applicability
condition in the preprocessing component.

Target-side discovery asks which relation to select. Here nothing is relaxed:
within each fold, held-out target values remain unavailable to the search, to the
utility, to support selection, and to estimator selection. Only the training
discharges' targets may influence which support is chosen.

The guarantee being tested is therefore precise: no discharge's own target values
influenced the support used to reconstruct it. The principle is
predictor-qualified, target-cross-fitted reconstruction.

This is a statement about information boundaries being transition-specific. The
existing definition already accommodates it, because that definition is a
variable-set boundary concerned with ancestry relative to the target, and never
governed which observations of an admitted variable are available at which stage.
That has always been the business of the preprocessing and validation components.
No notation changes; one clarifying sentence in the manuscript is recommended so
the two ideas are not conflated.

#### The Applicability Bound

The bound itself is unchanged and worth stating plainly, because it is easy to
mistake for something it is not. For a coordinate, write the smallest and largest
values it takes on the calibration interval, and measure how far the application
values reach beyond that hull, in units of the hull's own width. A calibration
range of two to six has width four; an application value of seven scores a
quarter, eight scores a half, ten scores one, and eleven scores one and a quarter
and is not applicable.

The threshold is one, and it means application values may extend beyond the
observed calibration hull by no more than one complete calibration-range width.
It is not a regression parameter, a regularisation parameter, a performance
threshold, a learned constant, a physical constant, a confidence level, or a
tuning knob. It is an observational-applicability bound.

With predictor-side admissibility restored to the whole object, the additional
training-side headroom margin introduced in the first protocol is unnecessary and
is retired, with no replacement threshold of any kind. There is exactly one
threshold in the contract, and it is unchanged.

#### The Common Candidate Basis

Every fold now searches the same certified basis: the three thousand four hundred
and fifty-one coordinates with full-domain range support, spanning all seven
constructor families in the counts the contract audit recorded. Because the
support condition is a conjunction of coordinate conditions over the same blocks,
any support assembled from this basis is fully supported by construction. That
closure was verified rather than assumed, at several support sizes, together with
an adversarial control confirming that a single unsupported coordinate always
breaks a support.

The applicability gate is consequently expected to pass by construction. It is
not deleted. It must still be recomputed during execution, where it now functions
as an integrity check: an unexpected failure would indicate a protocol or
implementation inconsistency and must halt execution for audit rather than be
recorded as an ordinary scientific failure.

#### What The Amendment Costs

This should be stated as plainly as what it buys. The stricter protocol would
have tested two things on held-out data — whether the target relationship
transfers, and whether the support's predictor geometry survives discharges whose
ranges were never consulted. The amended protocol tests only the first. A
positive result is a weaker statement than the original protocol would have
produced, and the claim boundary records this rather than absorbing it silently.

Accordingly the claim remains what it was and is not strengthened: target-
cross-fitted reconstruction over a predictor-qualified finite observational
object. Transfer to an unknown predictor distribution, to future discharges, or
to untouched data is not claimed and must not be written.

#### What Did Not Move

The claim type, the six outer folds, the applicability threshold, the revised
contract, the ontology, the admissible universe, the utility, the skill gate, the
era-robustness logic, the six baselines, the search budget, the one-seed policy,
the reporting tier, and the one-attempt stop rule are all unchanged. The
forbidden claim wording was not weakened. Nothing was adjusted elsewhere to
compensate for the amendment.

The earlier feasibility estimate — that fully cross-fitted applicability had
roughly a one-in-five chance under the retired training margin — is preserved as
historical record. It is not the justification for this amendment, and the
amendment would stand without it.
