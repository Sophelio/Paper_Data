### S7.4 Mathematical Interpretation

#### Discharge-Indexed Trajectory Ensemble

The task-admissible record is interpreted as a finite ensemble of typed sampled
trajectories indexed by discharge. Each of the sixty-two discharges is a
separate realization with its own physical-time support; they are never
concatenated into a single trajectory, and samples from different discharges are
not treated as draws from one continuous orbit.

The analysis supports are deliberately not identical across discharges. Each
discharge carries its own grid spacing, between approximately six and fourteen
milliseconds, set by the coarsest temporal resolution its admitted quantities
support. Fifty-three distinct spacings occur across the sixty-two discharges,
and the number of analysis samples ranges from three hundred and twenty-five to
eight hundred and thirty-three.

What the ensemble shares is the typed coordinate support — which quantities
enter, with what units and types — not a common set of timestamps. This is
consistent with the frozen contract: the validation windows are specified in a
normalized time coordinate, so the calibration and evaluation fractions do not
depend on the spacing; relation coefficients are discharge-specific under the
structural-transfer contract; and comparisons between methods use identical
scored samples within each discharge, which is what the common-support
requirement asks for.

#### Typed Multimodal Predictor Trajectory

The seventy-eight target-independent primitives are interpreted as a typed
product of blocks rather than as an undifferentiated vector. They span seven
broad scientific families and eight mathematical type blocks: the charge-exchange
family separates into toroidal rotation and ion temperature, which share a
diagnostic system but not a physical dimension.

Four of the eight blocks are not dimensionally homogeneous — the neutral-beam
block mixes power with torque, the magnetics block mixes field, current and two
uncalibrated channels, and the auxiliary density block mixes a density with a
temperature. This is recorded explicitly, because dimensional admissibility must
later be assessed per component rather than per block.

These quantities are not a physical state vector. They mix diagnostics,
diagnostic reconstructions, electromagnetic measurements, actuator commands and
uncalibrated channels, and no claim is made that they constitute a complete or
closed description of the plasma state. Channel indices within a multichannel
family are labels; the frozen object documents no channel geometry, so a channel
index is not interpreted as a spatial coordinate.

All quantities are expressed in canonical physical units. Standardization, where
it is later applied, is a fitted numerical transformation and not part of the
scientific identity of a coordinate.

#### Reconstruction Target

The target is the line-averaged electron density, expressed in inverse cubic
metres after canonicalisation from the archived inverse cubic centimetres. It is
a diagnostic reconstruction — a line integral divided by a chord length — and its
provenance classification is carried forward unchanged.

The target is maintained separately from the predictor trajectory. Neither the
target, nor any lagged value of it, nor any quantity derived from it enters the
explanatory coordinate space. No time derivative of the target is constructed at
this stage. Prior target values enter the study only through the persistence
comparator defined elsewhere in the contract.

Predictor and target values at the same index are contemporaneous. The eventual
reconstruction relation is written schematically only; no coordinate map and no
estimator are instantiated here, and no prediction horizon exists.

#### Physical And Normalized Time

Two time parameters are distinguished and kept apart. Physical time, in seconds,
is the independent parameter of the sampled trajectories and the only parameter
with respect to which any later scientific temporal or trajectory-relational
derivative may be taken. Normalized time, running from zero to one within each
discharge, exists solely to express the frozen calibration and evaluation
fractions.

Differentiating with respect to normalized time is forbidden for primary
scientific coordinate construction. Discharge durations differ by roughly forty
per cent across the ensemble, so a derivative taken in normalized time would be
rescaled differently in each discharge and would no longer carry a consistent
physical dimension.

#### Sampled Trajectories And Numerical Realizations

Three distinct objects are separated explicitly. The observational sampled
trajectory is the finite set of archived values the study actually possesses. A
numerical realization is any interpolant, smoother, finite-difference rule or
derivative estimator later applied to construct a coordinate; it is a declared
analyst choice, not a property of the observations. The latent physical
trajectory is not observed and is not assumed to be exactly recoverable.

The sampled trajectories are not assumed to be smooth, continuously
differentiable, or solutions of an ordinary differential equation. Any
derivative-valued coordinate constructed later is therefore a constructor acting
through a declared numerical realization, and not evidence that the observations
possess an exact classical derivative.

#### Temporal Resolution And Provenance

The analysis grids are built from a provenance-supported temporal-resolution
estimate: for each quantity and discharge, the archived temporal support divided
by the number of samples the archival pipeline received. This is a support-based
average, not an exact native sampling interval. Original timestamps are
unavailable, nonuniform original sampling cannot be reconstructed from the
available metadata, and the upstream resampling implementation remains
unavailable.

The defensible statement is therefore narrow and is made in exactly this form:
the primary analysis grid is no finer than the provenance-supported
temporal-resolution estimate used by the frozen numerical-admissibility policy.
It is not claimed that every grid point is a direct observation, nor that the
grid recovers the native sampling of any diagnostic.

Six of the seventy-eight primitives were interpolated upward by the upstream
pipeline in at least one discharge. They remain admissible as observed levels,
because the corrected grid respects their resolution estimate, but their
derivative construction is qualified as sensitivity-only. A further eighteen
carry an aliasing qualification inherited from their upstream downsampling. The
two qualifications are independent, and neither is removed by the coarser
analysis grid: aliasing is already embedded in the archived values, and
coarsening the grid does not undo it.

#### Gate To Ontology Construction

At this stage the corrected task-admissible record had been assigned a
mathematical interpretation, but no constructed coordinate had yet been
generated. S7.5 applies the frozen constructor and admissibility rules to this
typed trajectory ensemble to form `G_rec`.
