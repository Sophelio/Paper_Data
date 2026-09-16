# Final adversarial reviewer audit

**Date:** 2026-08-27 · **Classification: C — LEARNER_SPECIFIC_AUGMENTATION**

Second-pass review conducted as a skeptical referee.

---

## Q1. Could PySINDy already do this if given the same features?
**Yes, and it was given them.** PySINDy(C_all) reaches test RMSE 1.30×10⁻⁵,
marginally *better* than PySINDy(C*) at 3.32×10⁻⁵. The objection is valid and is
answered by testing it rather than deflecting. What remains SIR-specific is not
accuracy: it is that the grammar, admissibility constraint, selection rule and
provenance were declared and frozen, and that the selected subset is 12
coordinates at cond 10¹² instead of 38 at cond 10¹⁶.

## Q2. Did the SIR-expanded learner get more raw information?
**No.** C0-matched is exactly the five-point x,y stencil from which every derived
coordinate is built. This matters: the MLP improves 1.319 → 0.248 from the center
baseline to the matched baseline on raw inputs alone, so reporting only the
2-coordinate baseline would have inflated the apparent representation effect
about 5×.

## Q3. Did target information enter indirectly?
**No.** 38/38 coordinates z-free by declared DAG and by source inspection; the
module never indexes a z column. Empirically, raw features correlate with z at
|r| ≈ 0.004.

## Q4. Were hyperparameters tuned on test?
**No.** ρ, κ and scale method are canonical defaults, untuned. Scales,
clearances, ḡ and masking floors are train-fitted; C* is selected on
train+validation; STLSQ thresholds on validation; MLP early stopping on an
internal train split. Verified load-bearing: refitting on train+test shifts
s_eff (3.377100 → 3.378517), and the train-only values are the ones used.

## Q5. Is improved accuracy simply more parameters?
**No.** MLP(C*) uses 5 057 parameters vs 4 929 for C0 — **+2.6%** — for an 8.6×
RMSE reduction. And the sparse estimator, whose capacity does not scale with
input width the same way, shows the same ordering. Capacity does not explain it.

## Q6. Does C_all perform as well as C*?
**For the sparse estimator, marginally better** (1.3e−5 vs 3.3e−5). For the MLP,
worse (0.053 vs 0.029). Neither difference is presented as an accuracy win; the
honest framing is parity with a parsimony and conditioning advantage for C*.

## Q7. Is C* actually more stable, or merely smaller?
**Both, measurably.** 12 vs 38 coordinates, and cond 2.6×10¹² vs 7.5×10¹⁶ — the
latter effectively rank-deficient. The stability claim rests on the condition
number, not on RMSE.

## Q8. Are the quotient/phase features numerically conditioned?
Partly. The selected coordinates are **masked plain quotients**, conditioned by
dropping |denominator| below the 5th train percentile — a hard mask, not a
regulariser. The reference-shifted and sensitivity-centered coordinates, which
*are* smoothly regularised, were available and **were not selected**. On clean
data the mask suffices; under noise it does not, which is precisely where the
result degrades (Q11).

## Q9. How much data is masked?
11.5% of test samples dropped (88.5% retained). Applied identically to every
method, so no method is scored on a different support.

## Q10. Does the result survive trajectory-level holdout?
**Yes.** All splits are whole-trajectory; 8 protected test trajectories never
touched until final scoring. Per-trajectory RMSE and bootstrap CIs are reported.

## Q11. Does it survive noise and resolution perturbation?
**Resolution yes; noise only partly — this is the load-bearing negative.** At
σ=0.01 the MLP ordering *inverts*: C0 0.757 beats C* 0.817 and C_all 0.847. The
sparse estimator retains a large benefit (9.0 → 2.2). Differentiating and
dividing noisy signals amplifies noise enough to cancel the structural gain for a
learner that could already approximate the relation from raw inputs.

## Q12. Does the MLP comparison support learner independence?
**On clean data yes, under noise no.** Both learners improve substantially at
σ=0, which is genuine evidence the effect is representational. But the transfer
is not robust, so "learner independence" cannot be claimed without the noise
qualifier. This is the single reason the classification is C and not A.

## Q13. Reconstruction or accidentally forecasting?
**Reconstruction, explicitly.** Centered stencils are deliberate; z(t_k) is
recovered from observations around t_k. Declared in the config, the figure and
the report. No forecasting claim is made anywhere.

## Q14. Representation discovery, or feature engineering?
**Honestly, closer to constrained search than to discovery.** The grammar was
hand-declared; the search chose within it. What is more than feature engineering:
the admissibility constraint (z-free) is enforced and tested, selection is frozen
before protected evaluation with a hash, and the procedure recovered the exact
analytic relation *including* ρ=28 without being given the identity. What is less:
a human specified the 38 candidates, and the winning coordinates were among the
obvious ones for this system.

---

## Additional issues found and corrected during the audit

1. **STLSQ intercept.** pysindy's STLSQ has no intercept; the first run fitted
   mean-centered features against a target with mean ≈24, producing RMSE ≈25 for
   *every* representation. Corrected by centering the target on the train mean.
   Uncaught, this would have made all four representations look equally useless.
2. **Self-matching audit.** The z-dependency check searched its own source for
   `base["z"]` and matched its own search literal, so it could never pass.
   Corrected to assemble needles at runtime.

## Classification and why it is not upgraded

**C — LEARNER_SPECIFIC_AUGMENTATION.**

A is defensible on the noiseless primary benchmark alone. It is rejected because
the predeclared noise ablation shows the benefit does not transfer to the MLP
once observational noise is present. Upgrading would mean privileging the primary
number over a secondary analysis declared before any test evaluation. Per the
standing instruction, the classification is not raised because a stronger result
would read better.

## Recommendation for Section 1.4 / Figure 6

**Include, with the framing narrowed.** Panel A (containment) and Panel B
(representation → recovered relation) are clean, novel and defensible. Panel C
should be read as a clean-data result with the noise caveat stated in the caption,
not buried in SI. If the manuscript needs an unqualified "representation transfers
across learners" claim, this benchmark does **not** support it, and the honest
options are to narrow the claim to the sparse estimator or to add a
noise-robust coordinate family (the regularised RS/SC variants are the natural
candidates and were not selected here only because clean data did not need them).
