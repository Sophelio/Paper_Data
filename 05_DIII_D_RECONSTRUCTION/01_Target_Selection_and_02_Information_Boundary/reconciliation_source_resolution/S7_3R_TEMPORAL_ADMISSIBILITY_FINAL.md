### S7.3R Source-Supported Temporal Admissibility

#### The Correction

The observational object is the product of an upstream resampling step whose
implementation is not available. For most quantities that step reduced or
preserved the sample count, but for some it produced **more** archived samples
than it received: those additional samples are interpolations rather than
measurements.

The initial instantiation of the numerical-support rules used each quantity's
**archived** cadence — the spacing of the stored series. The frozen policy
requires the analysis grid to be no finer than what the observations actually
support, which is the **source-supported** cadence: the spacing implied by the
samples the archival pipeline received. Where a quantity was interpolated
upward, the two differ, and the archived cadence overstates the resolution.

This distinction was applied uniformly to all ninety-five quantities across all
sixty-two discharges. No rule, threshold, admissibility class, selection
criterion or cohort was altered. The correction is to how an existing rule is
instantiated, not to the rule.

#### What The Audit Found

Twenty-two quantities were interpolated upward in at least one discharge. An
earlier count of sixteen had been computed from a median across discharges,
which cannot detect a quantity upsampled in only a minority of them; the count
is corrected rather than reconciled to the earlier figure. The six additional
quantities are the two pedestal-fit parameters and the four filterscope
channels.

The remaining seventy-three quantities are never interpolated upward, and their
source-supported cadence never exceeds their archived cadence.

Interpolation alone does not make a quantity inadmissible. The frozen policy
already separates the use of a quantity as an observed level from its use in
constructing derivatives, and only requires that the analysis grid respect the
resolution the observations support. Admissibility was therefore decided by the
existing grid and validation rules rather than by a categorical exclusion of
interpolated signals.

#### Consequence For Admissibility

For each candidate target the analysis grid is set, per discharge, by the
coarsest source-supported cadence among the admitted quantities. A quantity is
inadmissible when retaining it would force a grid so coarse that the frozen
validation geometry no longer holds — when a required calibration or evaluation
interval would contain fewer samples than the predeclared minima.

Exactly one quantity in the object fails that test: the surface loop voltage. In
one discharge its source-supported cadence approaches eighty-three
milliseconds, and the resulting grid leaves every evaluation interval below the
required minimum. It fails as a candidate target for the same reason, and it is
inadmissible as an explanatory quantity in every other candidate's boundary.

The alternative — coarsening the entire experiment to accommodate a single
quantity — was rejected, as was restricting the discharge cohort to those where
that quantity happens to be better sampled. The cohort is unchanged and no
discharge was removed.

#### Corrected Target And Boundary

Applying the unchanged selection rule to the corrected admissibility, the
reconstruction target is the **line-averaged electron density**, a diagnostic
reconstruction recorded in inverse cubic metres after canonicalisation. It
carries no signal-specific provenance or numerical qualification, and it was
never interpolated upward in any discharge, so its archived and source-supported
cadences coincide.

It was selected at the second level of the rule, on the number of
provenance-certified explanatory quantities surviving its boundary. As before,
the candidate with the largest variation margin does not win: it belongs to a
channel series and its boundary is correspondingly narrower. The ordering
prefers breadth of surviving information over target variability, which is what
it was frozen to do.

Of the ninety-five quantities, seventeen are removed — the target itself, the
fifteen equilibrium reconstruction outputs whose ancestry cannot be certified,
and the one quantity failing numerical support. **Seventy-eight** primitive
explanatory quantities survive, across **seven** scientific families.

The corrected analysis cadence is discharge-specific, between approximately six
and fourteen milliseconds, bounded in each discharge by the pedestal-fit and
charge-exchange channels. It is *finer* than the cadence the earlier
instantiation implied, because removing the coarsest quantity removes the
constraint it imposed — and every sample on it is now supported by an
observation rather than produced by an interpolant. The validation geometry
holds in all sixty-two discharges with a wide margin.

#### Interpretation

The original target selection was not biased toward any outcome. It applied a
frozen deterministic rule to the metadata available at the time, and no
reconstruction was ever attempted, then or since. The subsequent mathematical
interpretation stage exposed a provenance fact that had not been resolved
earlier, and the study stopped rather than proceeding on a grid the contract
forbids.

The defect was then generalised into the existing numerical-support rule and
re-applied uniformly to every candidate, rather than repaired for the affected
quantity alone. The selected target changed; the standard of evidence did not.

#### Gate

At this stage the corrected task-admissible record and its temporal semantics
were frozen, but no mathematical interpretation had been instantiated and no
coordinate had been constructed. S7.4 assigns the mathematical interpretation to
the corrected record; ontology generation begins only in S7.5.
