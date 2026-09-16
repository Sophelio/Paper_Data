# `Q_rec*` — claim boundary

The boundary is **part of the result**, not a caveat appended to it. Any
restatement of `Q_rec*` that drops these lines is a misstatement of it.

---

## Supported

> Within the predictor-qualified frozen 62-discharge observational object,
> relational supports discovered without a discharge's own target values
> reconstruct that discharge nontrivially relative to the frozen baselines.

Three qualifiers in that sentence do real work:

| qualifier | what it excludes |
|---|---|
| **within the frozen 62-discharge object** | any discharge not in the object |
| **predictor-qualified** | any claim that the predictor geometry would survive unseen data |
| **without a discharge's own target values** | this is what makes it evidence at all |

## Not supported

- virgin external validation
- untouched external validation
- unknown-predictor-distribution transfer
- fully inductive predictor generalization
- future-discharge applicability
- zero-shot transfer
- universal DIII-D relation
- universal DIII-D generalization
- cross-device generalization
- unique physical equation
- universal coefficient vector

## The qualification that must survive every restatement

**Predictor-side applicability was instantiated from the non-target observations
of the entire finite 62-discharge object.**

Range-support admissibility was evaluated on every discharge–block cell of the
whole object, including the cells later held out. Epoch 2 therefore tests
**transfer of the target relationship to withheld targets**, not transfer of
predictor geometry to genuinely unseen discharges.

This was a deliberate, documented decision (E2.0A), taken on contract-internal
grounds: the sibling partial-map rule the contract already carried is an
**application-time** predicate, evaluated where a support is applied rather than
forecast from training. Retiring the training-only threshold made Epoch 2
consistent with that precedent. The epistemic cost is exactly the sentence above,
and it is carried everywhere the result is.

**This is not target leakage.** No held-out target value was available to any
search that selected the support under which that discharge is scored; supports
were hashed before held-out targets were opened, and protected windows were
opened last.

## Two limits on the accuracy claim

**1 — The margin over persistence is modest and era-asymmetric.**

`Δ₁ = −0.027308` pooled; 32 wins, 5 ties, 25 losses at discharge level; earlier
era (35) **+0.0076**, a practical tie; later era (27) **−0.0726**. The pooled
pass is carried by the later era. Never write "both eras improve materially".

Context, not excuse: Epoch 1's sensitivity analysis found no support in the
development-equivalent family beating persistence by more than 0.0287. The
ceiling looks like a property of the object and task rather than of any
representation.

**2 — The representation is not identified.**

Six folds, six different supports, all size 12, none identical, mean pairwise
Jaccard 0.285, 35 distinct coordinates. A seventh independent search produced a
seventh distinct support. Bootstrap selection frequencies across all searches run
from 0.001 to 0.121 with hundreds of distinct winners.

`Q_rec*` names a **procedure and a family**, not an equation.

## Coefficients

- locally calibrated per discharge and block; **no universal coefficient vector**
- support recurrence does **not** confer coefficient transfer
- **`pcdiamag3`**: `UNCALIBRATED_SIGNAL`; its coefficient has no certified
  physical-dimensional interpretation, in any support, however often selected
- **`prmtan_neped`**: independent of the target *signal* by provenance; **not**
  physically or statistically independent of line-averaged density
- **`gasa`…`gasd`**: actuator **command voltages**, not fueling rates

## Causal language about the improvement

Permitted:

> The revised range-support-qualified discovery procedure eliminated the
> catastrophic extrapolation tail observed in Epoch 1.

> The disappearance of the failure mode is consistent with the reconciliation
> having localized the relevant contract defect.

Forbidden:

> ~~K2 proved the range-support rule caused the improvement.~~

The contract, the candidate basis, the validation geometry and the supports all
changed between the epochs. The comparison is not controlled, and no stronger
causal claim is warranted.

## `C_E2_ALL_DESC`

Representative. Not unique, not held out, not externally validated, not the
support that produced the cross-fitted metric, not canonical. Any displayed
relation must be labelled a **representative full-object descriptive relation**.

## Tier language

`FORMAL_PASS` and `CLEAN_DEMO_NOT_MET` are separate facts and must be reported
separately. The formal scientific result is positive; the more demanding
prospective editorial tier was not reached because `Δ₁` did not reach −0.05 and
the eras did not both improve materially. Neither threshold was moved after the
fact.
