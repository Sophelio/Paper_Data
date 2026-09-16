# Task-conditioning audit

**Date:** 2026-08-27

For each contract: what was asked, of what object, under what constraints, what
won, what was task-equivalent, and why.

---

## `q_accuracy` — clean accuracy

| | |
|---|---|
| **q** | reconstruct hidden z with minimum error |
| **O** | `O_clean` — x,y observed; z supervised-only; E = numerical uncertainty only |
| **I_q** | `{x[k−2..k+2], y[k−2..k+2]}` |
| **C_q** | 17 declared candidate representations |
| **R_q(C)** | identity / poly2 / poly3 per candidate; PySINDy STLSQ as solver |
| **U_q** | minimum mean grouped-CV RMSE |
| **V_q** | 6-fold GroupKFold by trajectory, development only |
| **Ω_q** | 48 exposed development trajectories |
| **Winner** | **C_all** (38 coordinates), mean CV 1.3216e−5 ± 3e−7 |
| **Task-equivalent** | none — singleton |
| **Why** | no compactness preference; the largest admissible set wins outright |

## `q_compact` — clean compactness

Identical `O`, `I_q`, `C_q`, `R_q`, `V_q`, `Ω_q`. **Only `U_q` differs.**

| | |
|---|---|
| **U_q** | accuracy-equivalent set, then fewest coordinates → fewest terms → best conditioning → most stable |
| **Winner** | **C0+Q_pair** (12 coordinates), mean CV 3.3256e−5 ± 1.8e−7 |
| **Task-equivalent** | 4: `C0+Q_pair`, `C0+Q_all`, `C0+Q_pair+RS_pair`, `C_all` |
| **Margin** | 1e−3, from the practical floor (SE was 1.8e−7) |
| **Why preferred** | fewest coordinates among the equivalent set (12 vs 14, 16, 38) |

**Would another contract choose differently? Yes — and this is the result.**
`q_accuracy` and `q_compact` interrogate the *same clean object* with the *same*
information boundary, candidates and solver, and select **different**
representations. The difference is caused by the declared scientific objective,
not by the optimiser, the data, or the observation quality.

## `q_robust` — reconstruction under observational uncertainty

| | |
|---|---|
| **O** | `O_noisy` — Gaussian noise on x,y at σ ∈ {0, 0.005, 0.01} × development channel std, applied **before** all coordinate construction |
| **U_q** | minimum worst-case mean CV RMSE over the envelope, then the same hierarchy as `q_compact` |
| **V_q** | as above, 3 fixed development noise seeds per level |
| **Winner** | **C_all** (38 coordinates), worst-case CV 2.2903 ± 0.031 |
| **Task-equivalent** | none — singleton |
| **Margin** | 0.0309, from the **SE** (the 1e−3 floor is negligible here) |
| **Why** | under noise the candidates separate by far more than the floor, so the equivalence set collapses legitimately and compactness never engages |

**Would another contract choose differently? Yes.** `q_robust` ≠ `q_compact`:
adding an uncertainty model to the object reverts the selection from the compact
12-coordinate representation to the full 38. Confirmation data show why —
`C*_compact` degrades to 5.12 under 1% noise while `C_all` degrades only to 2.25.
The quotient coordinates divide by a near-zero denominator and differentiate
noisy signals; the robust contract detected that fragility from development data
alone, before any confirmation trajectory was read.

`q_robust` = `q_accuracy` in coordinates. **Observational uncertainty changed the
qualification, not the representation.** Reported as found; a coordinate change
would have been a cleaner story and did not occur.

---

## Is the difference caused by task, observation quality, or optimiser?

| Comparison | Differs in | Attribution |
|---|---|---|
| `q_accuracy` vs `q_compact` | **objective only** | **scientific task.** Same object, same data, same solver, same candidates, same folds. |
| `q_compact` vs `q_robust` | **objective and E** | **observation quality**, mechanistically confirmed: the compact representation's noise fragility is visible in the confirmation numbers. |
| any pair | — | **not the optimiser.** PySINDy STLSQ is the solver in every branch, with the same threshold grid. |

## Admissibility

All 17 candidates passed `ScientificObject.assert_admissible`: 0 coordinates
depend on z, dz or d2z, checked against the declared dependency graph and
against the source (`test_no_coordinate_depends_on_target`).

## Caveat carried into the manuscript

`Q[ẏ|x], Q[y|x]` were already exposed by the first benchmark. Their selection
here is **not** a fresh discovery. The new claim is the *contract dependence* of
the selection, which the first benchmark did not test.
