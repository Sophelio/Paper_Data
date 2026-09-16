### S7.11 Sensitivity And Failure-Mode Interpretation

The external gate failed. This stage asks what kind of failure it was, using
only analyses that were written down and hashed before the external cohort was
opened. None of it can change the primary result, and none of it does.

#### Support-Family Sensitivity

The development bootstrap that selected the frozen representation also produced
two hundred and seventeen distinct winning supports, and the sensitivity that
evaluates all of them externally was predeclared one hundred seconds before the
first external value was read. Two hundred and thirteen are evaluable on the
full external domain; four contain level–rate coordinates whose denominators
fail the inherited admissibility rule on six calibration blocks and are
reported as such rather than quietly dropped.

Seventy of the two hundred and thirteen — about a third — satisfy the frozen
skill criterion. The negative primary result is therefore not a uniform
property of the development-equivalent family. But neither is the family
successful: no member anywhere improves on persistence by more than 0.029 in
calibration-normalized RMSE, the passing members clear the frozen practical
floor by at most 0.019, and the family's median paired difference against
persistence is −0.0004, which is parity. The family straddles the trivial
baseline rather than beating it.

Where the family differs from itself is almost entirely in the tail. Median
error is tightly clustered across all two hundred and thirteen supports, from
0.146 to 0.193; mean error ranges from 0.18 to 4.94. Every one of the seventy
passing supports keeps all forty-two discharges below an NRMSE of one, while
ninety-three of the one hundred and forty-three failing supports do not. A
hundred and eighty-six supports are better than persistence typically; only a
hundred and seven are better on average. What separates passing from failing is
not typical accuracy but whether a catastrophic extrapolation occurs at all.

Two findings about the canonical representative follow, and they are the
substance of this stage. The frozen representation sits at the eighty-sixth
percentile of external mean error within its own equivalence class — among the
worst seventh of the family — while its typical-case accuracy is unremarkable
at the fifty-seventh percentile. And it carried the single highest development
bootstrap selection frequency of any member. Across the family, the correlation
between how often the development bootstrap chose a support and how well it
transferred is −0.09: indistinguishable from none.

Development equivalence, in other words, did not merely fail to identify the
externally best support. It carried essentially no information about external
robustness at all, and the support it favoured most strongly was among its more
fragile members. The lowest-error member of the family had been selected by the
development bootstrap about a third as often. It is not a replacement, is not
promoted, and confers no claim; it is reported because concealing it would
misrepresent the family.

#### Same-Family Density Sensitivity

Neither predeclared ablation of the pedestal-density diagnostic passes, and
neither improves the result.

Removing all five coordinates carrying that ancestry makes the external outcome
worse on every axis — higher mean, higher median, worse paired difference, and
a larger worst discharge. The catastrophic tail survives the removal, because
it was never a pedestal-density phenomenon.

The pedestal-density diagnostic alone achieves a better *mean* than the full
twelve-coordinate support and a nearly three times worse *median*. Its apparent
advantage is entirely the absence of a tail: a single level coordinate cannot
extrapolate catastrophically. On the typical discharge it is much the poorer
reconstructor.

Both statements therefore hold together. The relational construction adds
substantial typical-case accuracy over the semantically close observable on its
own, and it also introduces the tail exposure that fails the gate. Neither
object approaches nontrivial skill, so neither yields a claim. And none of this
disturbs the information boundary: the pedestal diagnostic remains a same-family
observable whose provenance is certified independent of the target signal, which
is a statement about ancestry and not about physical or statistical
independence from line-averaged density.

#### Discharge And Temporal-Block Dependence

The single-discharge component is clean. None of the forty-two
leave-one-discharge-out cohorts changes the verdict, a result recomputed
independently here and matching the frozen record exactly. The two catastrophic
discharges are individually insufficient precisely because there are two of
them.

The temporal-block component is not clean. Omitting the middle validation block
alone flips the verdict, by a narrow margin of 0.0014 in normalized RMSE. That
block is where the protected-window excursion occurs on both catastrophic
discharges. Under the frozen criterion — whether removal of one unit changes
the verdict — this is direct dependence on one temporal block, and the
sensitivity gate resolves negative on that basis. It is non-mandatory, and it
changes nothing mandatory; an influential unit is a finding to report rather
than a disqualification, provided it is reported.

#### Numerical-Realization Scope

Nothing was tested here, and that is itself the finding. Every coordinate of
the frozen support carries no alternative numerical realization, and the support
contains no derivative coordinate, so the study's one frozen derivative
realization never enters it. No alternative realization was invented after the
external outcomes became visible. Robustness may not be inferred from the
absence of a test, so this component is recorded as untested rather than passed.

#### Range-Support Failure Mode

The failure geometry identified externally is unchanged and was not repaired.
The squared gas-injection command remains in the frozen support; nothing was
clipped, winsorized, range-gated or removed, and no removal experiment was run.

The coordinate-participation table required across passing and failing supports
nevertheless places it first: that coordinate appears in none of the seventy
passing supports and in sixty-seven of the one hundred and forty-three failing
ones — the strongest failure association of any coordinate in the family. Its
presence barely moves the median error and moves the mean by a factor of three
and a half, the same tail-only signature diagnosed externally.

The conceptual lesson is a distinction the contract did not draw. Mathematical
domain support is not observational range support. A squared quantity is
defined for every finite argument, yet a relation calibrated on one interval
becomes numerically unsupported when that argument moves far outside it. The
frozen admissibility rule guards denominators, and states explicitly that
product constructors have no denominator and no gate; the failure arrived
through a product. That is a prospective recommendation for a future contract,
recorded as such. It is not operationalized here, not added retrospectively to
the frozen preprocessing policy, and not a repair.

#### Interpretation

Five things should be kept distinct, and this stage separates them. The primary
external failure stands. The development-equivalent family is heterogeneous
externally but uniformly marginal, straddling the trivial baseline rather than
beating it. Exact support identifiability is absent, and development selection
frequency does not predict external behaviour. Ingredient-level stability, which
development resampling did show, does not confer external robustness. And the
semantic proximity of the pedestal-density diagnostic explains neither the
successes nor the failure.

These sensitivity analyses do not modify the failed primary external gate. They
determine whether that failure is representative of the broader
development-equivalent support family and identify which aspects of the
representation are stable or fragile. S7.12 assembles the resulting qualified
negative output.
