### S7.8 Utility And Qualification Rules

The preceding stage produced an explored frontier of 162 845 candidate
coordinate supports and a complete record of where the frozen search looked.
It deliberately produced no judgement about which of those representations is
scientifically preferable. This section fixes that judgement rule — in full,
and before any result is visible.

#### Lexicographic Scientific Utility

The utility `U_rec` is **lexicographic**, not a weighted score. Each criterion
is applied only among candidates that are practically equivalent on every
criterion above it:

1. **primary fit quality** — calibration-normalized RMSE on held-out
   development validation blocks;
2. **generalization / stability** — behaviour aggregated across development
   discharges and all three predeclared temporal blocks;
3. **parsimony** — fewer scientific coordinates, then fewer active relation
   terms;
4. **conditioning** — a better-conditioned design matrix;
5. **support stability** — survival under development-shot resampling and fold
   perturbation.

The ordering carries a scientific argument. Fit is necessary but not
sufficient: a representation that fits only some discharges, or only one
temporal block, has not found structure. Among representations that cannot be
distinguished on fit, the smaller and better-conditioned one is the better
scientific object. And a support that changes identity under resampling was not
discovered — it was fitted.

There is no weighted sum, no Pareto-weight tuning, no scientific-family bonus,
no constructor preference, and no penalty attached to any coordinate family.

**Practical equivalence** is what makes the ladder operate rather than collapse
into pure accuracy ranking. Two representations are practically equivalent when

```
|NRMSE_A − NRMSE_B| ≤ max(SE_delta, 0.01)
```

in calibration-normalized RMSE units, where `SE_delta` is the standard error of
the paired per-discharge difference across the 20 development discharges. The
0.01 floor is 1 % of the calibration target scale — below any difference that
would be scientifically meaningful for a reconstruction claim. It was fixed
before any result existed and is immutable.

The floor is not decoration. A one-standard-error rule alone degenerates when
the standard error is small: in the Lorenz task-conditioning benchmark in this
project, `SE ≈ 3 × 10⁻⁷` collapsed every equivalence set to a singleton, which
silently made parsimony inoperative. The floor prevents that. The disjunction
(`max`, not `and`) is itself a correction: the original conjunctive wording left
the floor inoperative in exactly the case it was written for.

#### Development Selection Protocol

Selection reduces the frontier through nested survivor sets
`E0 ⊇ E1 ⊇ … ⊇ E5`, recording every elimination with the quantity that caused
it. Rank 1 forms the practical-equivalence set around the best fit — not a
top-*K* truncation. Rank 2 minimizes the worst temporal block, then the 90th
percentile across discharges, so that a representation cannot win by averaging
over a block or a discharge where it fails. Rank 3 prefers fewer coordinates
without any coefficient-magnitude threshold. Rank 4 ranks by the median
`log10` condition number of the calibration-standardized design, computed from
singular values rather than the squared normal-equation quantity, and introduces
no condition-number cutoff: conditioning ranks candidates, it never declares one
inadmissible. Rank 5 asks how often the same representation would have been
selected under 1000 resamplings of the development discharges and under each of
the three block omissions.

Every step is deterministic given the frozen inputs; the only randomness in the
procedure is the seeded discharge bootstrap. Ties are resolved by canonical
support identity, never by discretion.

Selection occurs **only within the frozen explored frontier**. `Ahat_rec` covers
roughly 3 × 10⁻³³ per cent of the unconstrained size-1…12 support space; the
remaining ≈ 5.1 × 10³⁹ admissible combinations are `ADMISSIBLE_UNSEARCHED` and
carry no negative finding of any kind. A representation selected here is *the
one the frozen utility rule prefers among those the frozen search found* — not
the best representation in `A_rec`.

The relation estimator is ordinary least squares with a fitted intercept and
discharge-local coefficients, chosen so that any positive result is attributable
to the **coordinate representation** rather than to estimator sophistication.
The support is shared; the numbers are local. This is a structural-transfer
claim, not universal fixed-coefficient transfer.

One semantic point is preserved deliberately. The Rank-1 fit term is arithmetic
that coincides with the navigation score that guided the search. That
coincidence is an identity of arithmetic, not of scientific role: the navigation
score determined *where the search looked*, while fit is *one criterion inside
the utility applied to what was found*. Search frequency is not scientific
importance, and search priority is not validation.

#### Numerical Conditioning And Stability

Conditioning is evaluated on the calibration-standardized explanatory design
with the intercept excluded, per discharge and block, from singular values. A
design whose smallest singular value vanishes receives an infinite condition
number rather than a rescued one; no epsilon is introduced anywhere in the
metric or the standardization.

Stability is an **analyst-defined qualification procedure**, and is labelled as
one throughout. The observational error model `E` is not instantiated in this
study, so no numerical perturbation is described as observational uncertainty
and no measurement-error weight enters the utility. What the resampling
measures is whether the selection is a property of the data or an artefact of
which 20 discharges happened to be in the development cohort. No pass/fail
threshold is attached: a low selection frequency is a finding to report, not a
disqualification.

#### Qualification Gates

Ten gates govern whether a result may be presented as a successful structural
transfer. Nine are mandatory; sensitivity is not, because a single influential
discharge is a finding to report rather than a disqualification, provided it is
reported.

The gates are deliberately split across stages. Information boundary, common
support, discharge-level inference and numerical provenance are protocol
properties, verifiable now from the lineage. Development-only discovery becomes
final when the support and estimator are hashed. Nontrivial skill against the
trivial baselines, fair comparison against raw-coordinate baselines, external
structural transfer and processing-era robustness are **not evaluable before
external evaluation**, and none is marked as passing here. Era robustness is
assessed on the external cohort's 24 earlier and 18 later discharges — not on
the 62 parent-object counts that an earlier draft of the contract quoted.

Skill is required against the trivial baselines; fairness, not victory, is
required against the raw-coordinate ones. The purpose of the baseline ladder is
not to beat machine learning but to establish whether relational representation
contributes utility beyond trivial and raw alternatives given identical
calibration. Outcomes in which it does not are honest negative results and are
reported as such.

#### Gate To Development Freeze

These rules specify how the explored frontier will be reduced to one
development-selected representation without reference to the sealed external
cohort. S7.9 executes the frozen utility rule, fixes the support, estimator and
all remaining model state, and hashes them before external evaluation.
