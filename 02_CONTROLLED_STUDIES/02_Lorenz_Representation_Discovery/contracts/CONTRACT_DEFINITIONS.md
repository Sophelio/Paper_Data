# Discovery contracts

Every contract is a pair `(O, K_q)`: a scientific object and a discovery
contract. All were declared before any confirmation evaluation and are hashed
into `PRECONFIRMATION_FREEZE.json`.

Manuscript convention: `D_g f = (df/dt)/(dg/dt)`; the subscript is the reference.

---

## The scientific object O = (D, Ω_obs, S, E, Π, A)

Shared by contracts B, C and D (the hidden-z reconstruction object). Only **E**
differs between the clean and noisy variants.

**D — data channels**
`x(t)`, `y(t)` are the admissible observed channels. `z(t)` is a supervised
target and evaluation quantity **only**: it may be the response during fitting,
and may never appear in the explanatory dependency graph.

**Ω_obs — observational support**
A trajectory ensemble of the Lorenz system on `t ∈ [0, 12]`, 2401 samples per
trajectory. Development: 48 exposed trajectories. Confirmation: 24 new,
protected trajectories.

**S — sampling / structure**
Uniform Δt = 0.005; centered five-point stencil; interior mask dropping 2 edge
samples per side; trajectory identity is the grouping variable and the
statistical unit.

**E — uncertainty model**
- *Clean object* (`O_clean`): numerical and sampling uncertainty only
  (DOP853 at rtol=atol=1e-12; discretisation error of the 4th-order stencil).
- *Noisy object* (`O_noisy`): additive Gaussian observational noise on `x` and
  `y` with σ ∈ {0, 0.005, 0.01} × the development per-channel standard
  deviation, applied **before** differentiation, smoothing, quotient
  construction, phase-coordinate construction and normalisation.

**Π — provenance**
Canonical generator `Lorenz/Lorenz_attractor.py::generate_lorenz`, σ=10, ρ=28,
β=8/3, DOP853, rtol=atol=1e-12. Source hashes in
`shared/manifests/confirmation_lineage.json` and
`prior_benchmark_reference/imported_hashes.json`. Coordinate transforms from the
audited reference implementation.

**A — admissibility**
`x`, `y` and their retrospective local history within `I_k` are available.
`z`, `dz/dt`, z-history and every z-derived quantity are forbidden as explanatory
coordinates. Retrospective symmetric local history is permitted because the task
is reconstruction, not forecasting.

**I_k — information boundary**
`I_k = { x[k−2 … k+2], y[k−2 … k+2] }`, identical for every method. Baselines:
`C0_center` = {x_k, y_k}; `C0_matched` = all ten stencil values (the primary raw
comparator).

---

## Contract A — K_containment

| | |
|---|---|
| **q** | recover the canonical full-state Lorenz generator |
| **O** | full state (x,y,z) with exact analytic derivatives, single canonical trajectory |
| **I_q** | full state, no partial observation |
| **C_q** | fixed state coordinates {x,y,z} |
| **R_q(C)** | fixed polynomial library (cubic for PySINDy; SIR order 1–2 per equation) |
| **U_q** | support and coefficient recovery against the known generator |
| **V_q** | comparison to the analytic right-hand side |
| **Ω_q** | `lorenz_dt001_exact_derivatives` |

Purpose: establish **containment**, not superiority.

---

## Contract B — K_accuracy_clean

| | |
|---|---|
| **q** | reconstruct hidden z with minimum error |
| **O** | `O_clean` |
| **I_q** | `I_k` |
| **C_q** | the 18 declared candidate representations |
| **R_q(C)** | identity / poly2 / poly3 as declared per candidate |
| **U_q** | **minimum mean grouped-CV RMSE** over 6 folds of the 48 development trajectories |
| **V_q** | GroupKFold by trajectory; development only |
| **Ω_q** | 48 exposed development trajectories |

No compactness preference beyond whatever regularisation is intrinsic to STLSQ.
It is scientifically acceptable for this contract to select a large model.

---

## Contract C — K_compact_clean

Same `O_clean`, same `I_k`, same candidates as B. **Only the objective differs.**

| | |
|---|---|
| **q** | find a compact, target-free, numerically stable representation whose accuracy is statistically indistinguishable from the best admissible clean reconstruction |
| **U_q** | one-standard-error rule, then lexicographic tie-breaking |
| **V_q** | as B |

Procedure, declared in advance:

1. Find the candidate with minimum mean CV RMSE.
2. Compute the standard error across the 6 validation folds.
3. Accuracy-equivalent set: `mean_RMSE(C) ≤ mean_RMSE(best) + SE(best)`.
4. Within that set choose lexicographically:
   **(a)** fewer coordinates → **(b)** better conditioning →
   **(c)** fewer active terms → **(d)** greater fold stability.

No weighted score was constructed after seeing results. The one-SE rule is the
conventional choice and was not tuned.

**This contract exists to test whether `C*_accuracy ≠ C*_compact` for the same
clean object.** If they are identical, that is reported.

---

## Contract D — K_robust_noise

Same reconstruction question; the object now carries observational uncertainty.

| | |
|---|---|
| **q** | find a representation that remains useful when the observational object includes realistic uncertainty |
| **O** | `O_noisy` |
| **U_q** | **worst-case** mean CV RMSE over the declared envelope σ ∈ {0, 0.005, 0.01}, then the same one-SE + lexicographic rule as C |
| **V_q** | as B, with three fixed development noise seeds per level |
| **Ω_q** | 48 development trajectories × noise envelope |

σ = 0.05 is reserved as a **stress test only** and is not used for selection.
Confirmation uses **independent** noise seeds (901/902/903).

---

## Contract E — joint solver (secondary, optional)

`(C*, R*) ∈ argmax U_q` over a small predeclared set of relation primitives
(STLSQ on the supplied coordinates; raw polynomial PySINDy; fixed MLP) under the
robust task. Secondary; it must not destabilise or replace the primary
representation-only comparison.

---

## Fairness rules binding on all contracts

1. No explanatory coordinate may depend on z.
2. Confirmation trajectories contribute to nothing but final scoring.
3. All matched baselines receive the same `I_k`.
4. Direct representation comparisons use the same sample mask; where coverage
   differs intrinsically, both common-support and native-coverage numbers are
   reported.
5. Feature scaling, noise scaling and every fit-dependent transform parameter
   are estimated on development data only and frozen.
6. Polynomial PySINDy baselines are genuinely competitive (degrees 2 and 3 over
   the full 10-dimensional matched stencil), not crippled.
7. No confirmation result may be used to redesign any contract.
