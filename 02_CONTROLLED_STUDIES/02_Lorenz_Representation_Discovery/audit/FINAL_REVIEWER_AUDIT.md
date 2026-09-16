# Final adversarial reviewer audit

**Date:** 2026-08-27 · **Classification: B — TASK_CONDITIONING_WITH_REPRESENTATIONAL_PARITY**

Reviewed as a skeptical SINDy/PySINDy referee.

---

**1. Could PySINDy reproduce this given the same features?**
Yes, and it did — PySINDy STLSQ is the solver in *every* branch. Given `C_all`
it reaches 1.353e−5, the best clean sparse result here. Nothing in this
benchmark is numerically inaccessible to PySINDy.

**2. Could a user build the SIR task logic around PySINDy?**
Yes. `pysindy/external_contract_wrapper/wrapper.py` does exactly that,
independently (5 tests enforce it imports nothing from `sir_contract`). This is
reported as **support** for the nesting interpretation, not as a failure.

**3. Are we comparing a rational SIR feature against an unfairly linear raw baseline?**
No. Degree-2 and degree-3 polynomial libraries over the full 10-dimensional
matched stencil are included. They matter: poly2 improves on linear raw by 3.8×
(8.607 → 2.267 clean).

**4. Does the raw polynomial control remove the apparent advantage?**
**Partially, and this must be stated.** Clean: no — 2.267 vs 1.35e−5, five
orders. Noisy: largely yes — 3.004 vs 2.245, a factor 1.34. Under realistic
observational noise a conventional polynomial PySINDy workflow is *within the
same order* as the expanded representation.

**5. Did task-conditioning merely encode the answer after seeing the old benchmark?**
This is the sharpest objection and it is **partly conceded**. The compact and
robust contracts were designed knowing accuracy/parsimony had already disagreed
and that the MLP advantage was noise-fragile. Fully disclosed in
`PRIOR_KNOWLEDGE_AND_POSTHOC_DESIGN_AUDIT.md`. What is *not* pre-encoded: which
of 17 candidates each contract would select, and that `q_robust` would revert to
`C_all`.

**6. Is the NEW confirmation set genuinely unseen?**
Yes. New seed, new seed trajectory, different x₀, longer burn-in, independent
noise seeds; min initial-state separation 0.676 vs a 0.5 threshold, 0 violations;
12 frozen hashes verified before any confirmation file was opened.

**7. Were thresholds chosen because they retained the previously discovered quotient?**
The equivalence **floor** was introduced after seeing that the plain one-SE rule
collapsed every equivalent set to a singleton. That is a genuine risk and is
audited in `EQUIVALENCE_RULE_AUDIT.md`. Defence: the `q_compact` selection is
identical across **four decades** of the floor (1e−4 … 1e−1), and `q_robust`
selects `C_all` at **every** floor. STLSQ thresholds were chosen on development
folds only.

**8. Does q_compact choose for defensible reasons or arbitrary weights?**
No weights. A lexicographic hierarchy declared in the config before the freeze:
coordinates → terms → conditioning → stability. The winner has the fewest
coordinates (12) in a 4-member equivalent set.

**9. Does the one-SE rule behave stably?**
**Not on its own — it degenerated**, and that is reported as a methodological
finding rather than hidden. With the object-scaled floor the behaviour is stable
over four decades.

**10. Does q_robust actually select for noise robustness?**
Yes, and it is corroborated out of sample: it rejected `C*_compact` on
development data, and on confirmation `C*_compact` degrades to 5.12 versus 2.25
for the selection it made. The contract's stated purpose is met.

**11. Does any selected representation become singular or poorly conditioned?**
`C_all` is effectively rank-deficient (cond 8.4e16) — the accuracy and robust
contracts both selected it anyway, because neither penalises conditioning at the
top level. Only `q_compact` trades accuracy for conditioning (2.7e12). This is a
real weakness of `q_accuracy`/`q_robust` as specified, not a hidden one.

**12. Are masked samples hiding failures?**
88.5% of samples retained, identical support for every method and regime.

**13. Does the MLP confirm or contradict learner independence?**
Clean: confirms (C*_compact 0.0183 vs raw 0.2892, +2.6% parameters). Noisy:
**contradicts** — 0.803 / 0.842 / 0.839 are within ~1.3 SE. Learner independence
holds only on clean data. This replicates the first benchmark's negative finding
on unseen trajectories.

**14. Task-conditioned discovery, or ordinary feature engineering?**
Honestly, in between. In favour: the candidate grammar, admissibility, utility
and equivalence rule are declared objects; contracts were frozen with hashes
before confirmation; and two contracts over one object provably diverged. Against:
a human wrote the 17 candidates, and the winning coordinates were already known.

**15. Any claim contradicted by PySINDy's API?**
No. `PYSINDY_CAPABILITY_AUDIT.md` verifies the 2.1.0 surface directly and
recommends the qualifier "in the conventional workflow examined here" so the
manuscript sentence describes *where the formulation sits*, not a capability
limit.

---

## Defects found and fixed

| Defect | Where | Fix |
|---|---|---|
| One-SE rule degenerate (SE≈3e−7 → singleton sets) | qualification | object-scaled practical floor; pre-freeze; 4-decade sweep |
| `PolynomialLibrary` returns `AxesArray`, breaking matmul | `engine.expand` | cast to `np.ndarray`; regression test |
| STLSQ has no intercept | solver | target centred on train mean; regression test |
| SIR target/feature family split blocked `dz/dt` | MCP contract | include the `y` family; recorded in the capability audit |
| 8-hour selection runtime | CV | pre-freeze stride-8 selection subsample; `C_all_poly2` dropped |
| Wrapper could have been tautological | Step 12 | 5 independence tests (static + dynamic) |

None of these "fixes" changed an unfavourable scientific finding into a
favourable one; the noise results remain negative for the MLP and near-parity
for poly2.

## Why not A, and why not D or E

**Not A:** the distinctions are complexity/conditioning tradeoffs, not a
protected-utility advantage; the task-conditioning layer is not MCP-native; and
learner transfer fails under noise.
**Not D:** the contracts demonstrably selected different representations on new
data, for mechanistically confirmed reasons.
**Not E:** no leakage, freeze held, no post-confirmation redesign, coordinate
provenance established.

## Recommendation

Suitable for main-text Section 1.4 **if** the claim is framed as contract
dependence with parity, and the noise caveat plus the non-MCP-native scope are
stated in the text rather than the SI.
