### Discovery Epoch 2 — Protocol And Resampling

#### Why The Validation Architecture Had To Change

The first discovery epoch was qualified against a cohort of forty-two discharges
that had been sealed since the reconstruction contract was written. That seal is
gone. Those target values were opened to evaluate the frozen representation, and
the discharges then informed the reconciliation audit and the contract revision
that followed. Every discharge in the observational object has now contributed to
what the contract knows.

Carving a fresh "never seen" cohort out of the same sixty-two discharges would
therefore be fabrication, and it would spend exactly the credibility that the
first epoch's discipline earned. The honest alternative is cross-fitting. It
claims something weaker than external validation and defensible in full: no
discharge's own target informed the support used to reconstruct it.

#### Discharge-Grouped Cross-Fitting

The sixty-two discharges are partitioned into six outer folds by a deterministic
rule with no randomness and no search: sort by processing era and then by
discharge identifier, and assign each discharge to the fold given by its position
modulo six. Exactly one partition was generated, so none could have been selected
for its appearance. The rule uses processing era and the identifier alone — no
target value, no reconstruction error, no Epoch-1 outcome label.

The result is two folds of eleven and four of ten, with the earlier era
distributed six-six-six-six-six-five and the later era five-five-four-four-four-
five. Every discharge is held out exactly once, and the discharge remains the
statistical unit throughout; there is no row-level split and no block-level split
across roles.

#### Information Boundary Within A Fold

Each fold follows a fixed thirteen-step order, and the order is the protocol. The
candidate basis is built from training predictors alone. The search then opens
training targets and nothing else. The utility runs, a support is selected, and
that support is written and hashed — after which it can never change. Only then
may the held-out predictors be opened, so that range-support qualification can be
evaluated on data that played no part in choosing the support. Only after that
status is recorded may the held-out calibration targets be opened to fit local
coefficients, and the protected targets are opened last, for scoring alone.

Held-out predictor ranges are deliberately excluded from candidate filtering. If
the held-out fold were allowed to shape which coordinates are even considered, the
transfer being tested would no longer be a transfer.

#### Range Support Inside A Fold

The contract's condition is applied twice, in two different roles. Candidates may
enter a fold's search only if, across every training discharge and block, their
application values leave the calibration hull by at most half a calibration range.
The contractual qualification threshold on held-out data remains one full
calibration range, exactly as frozen in the revised contract. The stricter
training-side requirement is a search-side admissibility choice, frozen
prospectively; it does not alter the contract. It exists because a coordinate
admitted at exactly the threshold on training data has no headroom at all when it
meets a discharge it has never seen.

After a support is frozen, every one of its coordinates must satisfy the
contractual condition on every held-out block. One failure means the fold does not
qualify for full-domain success, and the response is to record it — never to
reselect a support, drop a block, drop a discharge, or loosen the threshold.

#### What Is Deliberately Unchanged

The utility is untouched. No tail penalty was added, the fit rank was not
modified, the practical-equivalence tolerance stands, and range support was not
rewarded inside the utility. That separation is the point: range support is an
admissibility condition, not a performance objective, and blurring the two would
reintroduce exactly the confusion the contract revision was meant to remove.

The skill gate is likewise unchanged: the mean paired difference against the
calibration-mean and persistence baselines must each be at most minus one
hundredth. The era logic, the baseline ladder, the block geometry and the
discharge-level aggregation all carry over. The first epoch's explored frontier
is not reused or re-ranked; each fold searches afresh over its own admissible
basis, under a budget frozen before any target access.

#### The Risk That Was Measured Before Committing

One number deserves to be stated plainly, because it was measured
target-blindly before any search: the full-domain applicability requirement is
demanding. Across six folds, a support drawn at random from a fold's admissible
basis has roughly a one-in-five chance of surviving the held-out range-support
gate everywhere. Epoch 2 is therefore more likely to fail on applicability than on
reconstruction quality.

This is not caused by any pathological discharge. Every discharge retains at least
ninety-four per cent of its fold's basis, and the coordinate that destroyed the
first epoch is excluded from every basis by the contract itself. The difficulty is
arithmetic: a support must clear twelve coordinates across roughly ten unseen
discharges, and small per-coordinate attrition compounds.

The standard was not weakened to improve those odds. It is disclosed instead.

#### Decision

The protocol is frozen and Epoch 2 may proceed. It is also the final `q_rec`
attempt authorised for this manuscript. If it fails — on skill, on era robustness,
or on applicability — the branch closes as a qualified iterative case study rather
than being revised again, and the descriptive result becomes the positive DIII-D
headline.
