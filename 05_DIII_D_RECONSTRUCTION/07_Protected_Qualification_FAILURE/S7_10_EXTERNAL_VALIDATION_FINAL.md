### S7.10 External Validation And Baselines

The external cohort had been sealed since the reconstruction contract was
written. This stage opened it once, evaluated the frozen object against it, and
recorded the answer.

#### Frozen Structural Transfer

Before any external value was read, the pre-external package was re-verified:
thirteen substantive hashes covering the selected support and its coordinate
definitions, the ontology and admissible-universe lineage, the search policy and
explored frontier, the utility policy and its selection ledger, the estimator,
the preprocessing and denominator rules, the validation geometry, the
interpretation flags, and all six comparator configurations. All thirteen
reproduced. The freeze stamp precedes the first external read by design and by
record.

What transferred to the external cohort was the support identity, the coordinate
definitions, the numerical construction rules and the estimator procedure —
never a fitted coefficient. On each external discharge and block the twelve
coordinates were constructed, standardized on that block's calibration interval
alone, and an affine relation was fitted there and applied to the protected
interval. Coefficients are discharge-local and block-local throughout. Six
comparators — the calibration mean, persistence, an AR(1) diagnostic, ridge on
the full seventy-eight-predictor raw basis, gradient boosting on the same basis,
and a hardened seventy-level ridge ablation — were evaluated on identical
protected rows with identical calibration geometry and no external tuning of any
kind.

All forty-two discharges and all one hundred and twenty-six blocks were
evaluable. The frozen denominator-admissibility rule was satisfied on every one
of its three hundred and seventy-eight external checks, so no block was excluded
and no repair was applied or needed.

#### External Reconstruction

On the typical external discharge the frozen representation transferred at
essentially its development level: the median external calibration-normalized
RMSE is 0.170, against a development value of 0.166. Forty of the forty-two
discharges lie in that regime.

Two earlier-era discharges do not. On both, the reconstruction error is roughly
seventy times the median, and those two discharges move the cohort mean from
0.17 to 0.74. The frozen gate is defined on the mean.

#### Trivial And Raw Baselines

In the pooled mean the relational representation is better than the
calibration-mean baseline and worse than every other comparator, including
persistence. In the median it is marginally ahead of or level with the raw
comparators. Both are reported; the gate uses the mean.

Against persistence the paired discharge-level record is eighteen wins, seven
ties and seventeen losses, with a median paired difference of −0.005 and a mean
of +0.532. Every comparator shows the same signature — a slightly negative
median and a strongly positive mean — which is the arithmetic of a heavy tail,
not a summary of typical behaviour.

#### Paired Discharge-Level Evidence

Inference treats the discharge as the independent unit throughout. Ten thousand
paired discharge-bootstrap replicates were drawn from a single shared index
matrix per cohort so that comparator geometry is preserved, and confidence
intervals are reported as percentile intervals; they are reported, not used as
significance thresholds. The pooled interval against persistence,
[−0.037, +1.374], is wide and straddles zero, which reflects the tail rather
than qualifying the result.

Leave-one-discharge-out analysis shows the failure is not an artefact of a single
discharge: none of the forty-two leave-one-out cohorts satisfies the skill gate,
and removing the single worst discharge still leaves the paired difference
against persistence at +0.26.

#### Processing-Era Robustness

Reported separately for the twenty-four earlier and eighteen later external
discharges, as required. The earlier era is materially adverse against both
trivial baselines; the later era is materially favourable against both and meets
the skill thresholds on its own. The two eras are nevertheless
indistinguishable in the median, 0.182 against 0.170. The entire era difference
is the same two discharges.

The era result is recorded as evidence. It is not a claim, and the domain was not
narrowed to the later era: doing so in order to obtain a passing skill gate is
forbidden by the frozen contract, and a materially adverse era may not be
averaged away either.

#### Qualification Gates

Seven mandatory gates pass: the information boundary, development-only
discovery, fair raw comparison, external structural transfer, common support,
discharge-level inference, and numerical provenance. Sensitivity remains pending
its own stage and is non-mandatory.

Two mandatory gates fail. Nontrivial skill fails because the relational
representation is materially worse than persistence in the frozen pooled mean.
Processing-era robustness fails because its outcome schema presupposes the skill
gate passing.

Under the frozen contract, a mandatory failure means the result may not be
presented as a successful nontrivial structural transfer. It is recorded as
such, without an averaging score to soften it, and the externally supported
claim domain is empty.

The comparison itself remains valid — the fairness gate passes — which is what
makes the negative result usable rather than merely disappointing.

#### Interpretation Boundary

The proximate cause of the two catastrophic discharges is identifiable and worth
stating, because it is a general lesson about relational construction rather
than a defect of this dataset. On both, the gas-injection valve command
undergoes a large excursion inside the protected window, roughly forty times
beyond anything its local calibration interval contained. The support includes
that command squared, so the excursion enters the design about nine thousand
calibration standard deviations out, and an affine relation fitted on
calibration extrapolates linearly into failure. Across the cohort, the
correlation between a discharge's maximum protected excursion and its relational
error is 0.93.

The frozen admissibility rule could not have caught this. It guards
denominators, and the contract states explicitly that product constructors have
no denominator and no gate. A squared actuator command is unguarded by
construction. Recognising that is a finding; acting on it would be a repair, and
the frozen object was left exactly as frozen.

Three qualifications carry forward unchanged. The development selection of this
particular support was unstable — it was chosen in nine per cent of a thousand
development resamplings, which produced two hundred and seventeen distinct
winners — so it is one representative of a broad equivalence class, never a
uniquely identified structure, and coordinate-level recurrence is
ingredient-level stability rather than support identification. The support
contains an uncalibrated diamagnetic-loop signal whose coefficient has no
certified physical-dimensional interpretation. And it contains a pedestal
electron density diagnostic: a same-family observable whose provenance is
certified independent of the target signal under the frozen information
boundary, which establishes no target-signal ancestry but does not establish
physical or statistical independence from line-averaged density. Selection
throughout occurred within the explored frontier only, with no claim of global
optimality.

#### Gate To Sensitivity Analysis

The external cohort was evaluated only after the support, estimator and
comparator configurations were frozen. S7.11 now tests the predeclared
sensitivity questions without altering the primary external result.
