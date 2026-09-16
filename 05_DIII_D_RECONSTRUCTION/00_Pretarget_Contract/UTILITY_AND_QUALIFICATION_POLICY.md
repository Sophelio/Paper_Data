# S7.2 — Utility `U_rec` and qualification `V_rec`

## Utility is not training RMSE

`U_rec` is **lexicographic**: each criterion is applied only among candidates
that are practically equivalent on all criteria above it.

| Rank | Criterion | Measure |
|---|---|---|
| 1 | **primary fit quality** | calibration-normalized RMSE on development validation blocks, held out |
| 2 | **generalization / stability** | aggregated across development discharges and all three predeclared temporal blocks |
| 3 | **parsimony** | fewer scientific coordinates, then fewer active relation terms |
| 4 | **conditioning** | better-conditioned design matrix (lower condition number) |
| 5 | **support stability** | survives development-shot resampling and fold perturbation |

Ordering rationale: fit is necessary but not sufficient; a representation that
fits only some development discharges or only one temporal block has not found
structure; among equivalent representations, the smaller and better-conditioned
one is the better scientific object; and a support that changes under
resampling was not discovered, it was fitted.

## Practical equivalence — declared BEFORE search

Two representations are practically equivalent when **both** hold:

```
one_standard_error_rule       : difference within 1 SE of the better,
                                SE over development discharges
practical_equivalence_floor   : |difference| <= 0.01 in calibration-normalized
                                RMSE units
```

### Why a floor as well as a one-SE rule

A one-SE rule alone degenerates when the standard error is tiny. In the Lorenz
task-conditioning benchmark in this project, `SE ≈ 3e-7` collapsed every
equivalence set to a singleton, which made the parsimony criterion inoperative
and silently identical to pure accuracy selection. The absolute floor prevents
that.

**0.01 in calibration-normalized RMSE units** is 1% of the calibration-interval
target scale — below any difference that would be scientifically meaningful for
a reconstruction claim. It is fixed here, before any result exists, and **may
not be adjusted afterwards**.

## No fabricated error weighting

`E` is not instantiated. Therefore:

- **no** measurement-error weights, in the utility or anywhere else;
- **no** description of numerical perturbations as observational uncertainty;
- bootstrap and sensitivity analyses are permitted and must be labelled
  **analyst-defined qualification procedures**.

---

## Qualification gates `V_rec`

Each gate resolves to `PASS` · `PASS_WITH_QUALIFICATION` · `FAIL` ·
`NOT_APPLICABLE`.

| Gate | Requirement | Mandatory |
|---|---|---|
| **V1** information boundary | no target leakage; no admitted quantity with unresolved target ancestry in the primary boundary | **yes** |
| **V2** development-only discovery | target, ontology, support, estimator and thresholds chosen without external outcomes | **yes** |
| **V3** nontrivial skill | frozen representation beats **B0** and **B1** in the predeclared aggregate sense | **yes** |
| **V4** raw-coordinate comparison | fair comparison against **B2** and **B3** on identical information and geometry | **yes** |
| **V5** external structural transfer | support frozen and hashed before any external evaluation | **yes** |
| **V6** processing-era robustness | external results reported separately for the 35 earlier and 27 later discharges | **yes** |
| **V7** common support | cross-representation comparisons use identical scored samples | **yes** |
| **V8** discharge-level inference | discharge, not time sample, is the independent unit | **yes** |
| **V9** sensitivity | no result depends catastrophically on one discharge, one temporal block, or one numerical realization | no |
| **V10** numerical provenance | no claim rests on interpolation-created resolution without qualification | **yes** |

> **If a mandatory gate fails, `Q_rec` may not be presented as a successful
> structural transfer result.**

V4 requires *fairness*, not victory: the gate passes if the comparison was
conducted properly, whatever the outcome. V3 requires actual skill — it is the
gate the retired q_rec failed.

V9 is non-mandatory because a single influential discharge is a finding to
report rather than a disqualification, provided it is reported.

## Deferred

- **S7.9:** instantiated utility computation on development.
- **S7.10:** gate evaluation.
- **S7.11:** V9 sensitivity study.
- **S7.12:** the qualified result `Q_rec*` with its gate table.
