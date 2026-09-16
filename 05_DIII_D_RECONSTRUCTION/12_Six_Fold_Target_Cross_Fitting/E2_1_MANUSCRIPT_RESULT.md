### Cross-Fitted Relational Discovery Under The Revised Contract

The first discovery epoch produced a relational representation that failed
external qualification, and the failure was traced to a coordinate whose values
left the range on which its relation had been calibrated. The contract was
minimally hardened with a single dimensionless observational range-support
condition, frozen before any new search, and discovery resumed over the
coordinates that condition admits.

Six outer folds partition the sixty-two discharges so that each is held out
exactly once. Within each fold a fresh search over the three thousand four
hundred and fifty-one range-supported coordinates, using only the training
discharges' target values, selected one representation under the unchanged
lexicographic utility. Each support was hashed before any held-out target value
was opened, and protected values were opened last, for scoring alone. The
sixty-two out-of-fold results are therefore each produced by a support that never
saw that discharge's own target.

The frozen skill gate passes. Against the calibration-mean baseline the mean
paired difference in calibration-normalized RMSE is −0.764, and against
persistence it is −0.027; both clear the threshold of −0.01 fixed before any
result existed. Every one of the two thousand two hundred and thirty-two
held-out range-support checks passed, as the contract's closure property
predicts, and no held-out discharge exceeded a normalized error of one. The
worst discharge in the entire cross-fitted set scores 0.92, against 11.95 in the
first epoch; the two discharges that destroyed that epoch now score 0.30 and
0.44. The hardening did what it was designed to do.

Two qualifications must travel with the result. First, the margin over
persistence is modest and unevenly distributed: pooled it is −0.027, but the
later processing era contributes −0.073 while the earlier era is practically tied
at +0.008, and the discharge-level record against persistence is thirty-two wins
to twenty-five losses. The prospectively declared clean-demonstration tier, which
required a margin of −0.05 and material improvement in both eras, is not met.
Against the raw-coordinate comparators the picture is different and much
stronger: the relational representation improves on ridge regression over the
full seventy-eight-predictor basis by −0.096, on gradient boosting over the same
basis by −0.157, and on the hardened-basis ablation by −0.095. The defensible
representational statement is that relational coordinates add substantial utility
over raw representations of the same information, and modestly over persistence.

Second, the six folds produced six different supports, sharing on average about a
quarter of their coordinates and none identical. As in the first epoch, the object
supports a family of adequate relational representations rather than identifying
one. Two coordinates recur in all six, one of them an uncalibrated diagnostic
whose fitted coefficient carries no certified physical interpretation regardless
of how often it is selected.

The claim is bounded accordingly. Predictor-side applicability was instantiated
from the non-target observations of the whole finite object, so what has been
tested is whether the target relationship transfers to discharges whose targets
were withheld — not whether the representation would apply to discharges never
observed at all. This is target-cross-fitted reconstruction over a
predictor-qualified finite observational object, not external validation, and not
a claim about future or unseen discharges.
