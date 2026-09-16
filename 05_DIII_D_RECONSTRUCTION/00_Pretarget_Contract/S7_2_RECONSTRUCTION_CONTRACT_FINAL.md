### S7.2 Reconstruction Contract

#### Scientific Reconstruction Question

The reconstruction task is deliberately simple: recover one observed scalar
plasma or state quantity from the other admissible quantities observed at the
same instants, across a frozen finite collection of DIII-D discharges. The
question the study asks of that task is not whether a particular quantity can be
predicted accurately, but whether a **relational representation identified on one
set of discharges remains useful on discharges it was never shown**.

The scientific object of interest is therefore the *support* of the relation —
which coordinates enter it, and in what constructed form — rather than any
particular set of fitted numerical values.

#### Target-Blind Contract Design

Every rule described below was fixed and hashed **before a reconstruction target
was chosen**. At the close of this stage no target had been selected, no
candidate target had been ranked, no relational coordinate had been constructed,
and no reconstruction performance of any kind had been computed.

This ordering is the central methodological commitment of the study. It fixes
what would count as a valid result before it is known which target would make a
result easy to obtain. The contract records not only each decision but the
information deliberately withheld from it, so that the analysis cannot be, and
cannot appear to have been, arranged around its own outcome.

#### Development And External Cohorts

The 62 discharges were partitioned into 20 development and 42 external
discharges by a deterministic rule using only discharge identifiers, membership
of the seven ordered operational periods, and the documented upstream processing
era. No signal value and no target value entered the partition; the data
archives were not opened. Because the rule is deterministic, no random seed is
involved and the split is reproducible from the discharge list alone.

Both processing eras are represented in both cohorts in proportions close to
those of the object as a whole, and every operational period containing more
than one discharge contributes to both.

The external cohort is **sealed**. From the moment of partition until external
validation, its signal values, target values, and any statistic or model output
derived from them are unavailable to target selection, ontology design, candidate
pruning, support selection, hyperparameter choice, and threshold setting. Only
discharge identifiers and frozen provenance metadata may be known.

The seal exists because the following stage must examine candidate-target
properties to assess feasibility, and those diagnostics must not touch the data
on which the eventual claim will be tested.

#### Information-Boundary Principle

For any chosen target, the admissible explanatory information is obtained by
removing the target, its duplicates and aliases, every quantity whose definition
contains it, every quantity with verified upstream dependence on it, and every
quantity constructed from anything so removed. Exclusion is transitive through
the coordinate graph and is applied **before** coordinate generation, so that an
inadmissible coordinate is never constructed rather than constructed and later
discarded.

Two principles govern the boundary. The first is that **statistical association
is never evidence of ancestry**: quantities are excluded because of a
definitional or computational relationship established from provenance, never
because they correlate with the target, and equally are never admitted because
they fail to correlate. The second is that the boundary **fails closed**: where
ancestry relative to the target cannot be resolved from the available record,
the quantity is not certified independent and does not enter the primary
boundary.

The second principle carries a substantial and deliberately accepted cost. The
fifteen equilibrium and shape quantities have only partially resolved lineage,
and for some targets all fifteen will be excluded on those grounds alone. The
alternative — admitting them because dependence merely could not be demonstrated
— would make any independence claim unfalsifiable.

Where a target belongs to a multichannel diagnostic family, neighbouring
channels of the same family are excluded from the primary boundary, because
reconstructing one channel from its immediate neighbours is spatial
interpolation and would not test relational structure. The variant admitting
them is retained as a declared sensitivity, fixed in advance so that neither can
be selected after its result is known.

#### Numerical And Dimensional Admissibility

The observational object contains quantities recorded in inconsistent unit
scales — power in kilowatts and watts, density in inverse cubic centimetres and
inverse cubic metres, temperature in kiloelectronvolts and electronvolts. These
differences are invisible under within-discharge standardisation and become
consequential precisely when algebraic constructions combine the affected
quantities. All quantities are therefore converted to canonical units before any
coordinate constructor operates, conversions are recorded, and every algebraic
construction is dimensionally checked at the point of construction. Two
quantities documented upstream as uncalibrated retain a permanent uncalibrated
type and never acquire an invented physical dimension.

Native sampling spans three orders of magnitude, and placing coarse quantities
on a fine common grid manufactures apparent temporal resolution: equilibrium
quantities sampled every twenty milliseconds are approximately four times
interpolated on a five-millisecond grid. The contract therefore requires that the
analysis grid be **no finer than the coarsest native cadence among the quantities
admitted to the task**. Interpolated samples are not observations and may not
serve as independent evidence.

The same principle bounds derivatives. No derivative may claim resolution finer
than its source; derivatives of quantities known to have been interpolated
upstream are excluded from the primary ontology or explicitly marked as
sensitivity-only; and second and higher temporal derivatives are presumed
inadmissible.

#### Utility And Qualification

Utility is lexicographic rather than a single score. Held-out fit quality is
assessed first; among representations that are practically equivalent on fit,
preference passes in turn to stability across discharges and temporal blocks, to
parsimony, to numerical conditioning, and finally to the stability of the support
itself under resampling of the development discharges.

Practical equivalence is defined before any search takes place, by a
one-standard-error rule together with an absolute tolerance. The absolute
tolerance is necessary: a standard-error rule alone degenerates when the standard
error is small, silently reducing the criterion to accuracy alone and rendering
parsimony inoperative.

No measurement-error weighting appears anywhere in the utility, because the
observational object contains no uncertainty model. Numerical perturbation and
resampling analyses are used later as analyst-defined qualification procedures
and are never described as observational uncertainty.

#### Protected Validation

Each discharge contributes three evaluation blocks defined on normalised
discharge time: calibration intervals covering the first forty, sixty and eighty
per cent, with protected intervals immediately following each and spanning ten
per cent. Protected intervals are thus distributed through the trajectory rather
than concentrated at its end.

This replaces an earlier protocol that evaluated only the final fifth of each
discharge, which proved degenerate: the terminal interval was nearly constant,
and a predictor emitting a single number outperformed the model under test. The
geometry adopted here was fixed without reference to any target value and was
verified feasible at every native sampling cadence present in the object.

All fitted quantities — scalings, thresholds, smoothing parameters, regularisation
choices, and relation coefficients — are estimated from calibration data only and
applied unchanged to protected intervals. Predictor values within a protected
interval are used, since they are observed contemporaneously with the target and
their use is what makes the task reconstruction; target values within a protected
interval are used only for final scoring.

#### Baselines

Four comparators are fixed in advance and receive identical calibration
intervals, identical scored samples, and identical admissible information: the
calibration-set mean; persistence of the last calibration value; a transparent
regularised linear model on the primitive admissible quantities; and one
predeclared off-the-shelf nonlinear learner on the same primitive quantities.

The first two establish that the task is not trivial. The second two establish
whether relational construction contributes anything beyond what the same
information yields without it. The purpose is not to outperform machine
learning, and an outcome in which the relational representation matches rather
than exceeds a nonlinear learner while remaining interpretable is a meaningful
result, reported as such.

#### Claim Boundary

The claim is **structural transfer with local calibration**: a coordinate support
identified on development discharges, frozen before external evaluation, remains
useful on unseen discharges when relation coefficients are estimated from a
declared calibration interval of each new discharge. It is not a claim of
zero-shot transfer with fixed coefficients.

The claim domain is the frozen 62-discharge object and nothing larger. The
discharges are the complete finite collection available to the study, not a
random or representative sample of device operations; their parent population and
selection criterion are not recorded. The object is the archived, resampled
record rather than the native acquisition chain, so statements about native
high-frequency behaviour or diagnostic bandwidth lie outside its scope. The task
is reconstruction from contemporaneous observations and supports no claim about
forecasting, causal structure, or control. Discharge, not time sample, is the
independent unit of inference.

#### Gate To Target Selection

At this stage no reconstruction target, task-specific information boundary,
relational ontology, search policy or validation outcome had been defined. Target
feasibility and the instantiated information boundary are evaluated only in S7.3,
using development discharges alone.
