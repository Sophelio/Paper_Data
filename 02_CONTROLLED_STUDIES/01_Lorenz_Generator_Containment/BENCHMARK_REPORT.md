# Lorenz nested-representation benchmark

**Date:** 2026-08-27
**Classification: C — LEARNER_SPECIFIC_AUGMENTATION** (see §13 and
`audit/FINAL_REVIEWER_AUDIT.md`)

---

## 1. Scientific question

Three narrow claims, not a superiority contest:

1. **Containment** — restricted to the same coordinates, library, derivatives and
   sparse family, does SIR reduce to the same discovery problem as SINDy?
2. **Representation expansion** — PySINDy is extensible, so it is *given* the same
   expanded coordinate library. The question is whether making construction,
   admissibility, selection and qualification part of the declared search adds
   anything.
3. **Learner independence** — does a SIR-selected representation also help an
   otherwise unchanged generic MLP?

No SIR advantage is manufactured. Parity and negative results are reported as
found, and one is (§9).

## 2. Dataset provenance

Canonical generator **reused**: `Lorenz/Lorenz_attractor.py::generate_lorenz`
(DOP853, rtol=atol=1e-12), σ=10, ρ=28, β=8/3.

| | Source | Size |
|---|---|---|
| Containment | **reused** `lorenz_dt001_exact_derivatives.parquet` verbatim | 40 001 samples, dt=0.001 |
| Ensemble | **generated** with the same generator | 48 × 2401 samples, dt=0.005, tmax=12 |

The existing example had only one trajectory, so a 48-trajectory ensemble was
generated for trajectory-level splits. Initial states are drawn reproducibly from
a long canonical trajectory after burn-in, so all start on the attractor.

Frozen whole-trajectory splits: **32 train / 8 validation / 8 protected test**.
Full lineage with hashes: `shared/manifests/source_lineage.json`.

## 3. Containment

Both estimators received the same full state, the same **exact analytic**
derivatives, the same cubic library (20 terms), and STLSQ threshold 0.1.

| Equation | Support recovered | max abs coeff error |
|---|---|---|
| dx/dt | exact, both | 8.9×10⁻¹⁵ (PySINDy), 7.1×10⁻¹⁵ (SIR) |
| dy/dt | exact, both | 3.2×10⁻¹⁴ (PySINDy), 7.1×10⁻¹⁵ (SIR) |
| dz/dt | exact, both | 2.7×10⁻¹⁵ (PySINDy), 3.1×10⁻¹⁵ (SIR) |

Zero false positives, zero false negatives, both methods, all three equations.
Maximum coefficient difference **between** methods: 3.9×10⁻¹⁴.

**Containment holds.** This is parity by construction and is not presented as a
SIR result.

*Caveat:* the restricted-SIR side was executed locally, not through the SIR MCP —
see §11.

## 4. Expanded coordinate grammar

38 candidates from x and y only, within I_k = {x[k−2..k+2], y[k−2..k+2]}:
10 raw · 2 rate · 2 curvature · 8 product · 4 masked quotient · 4 CA · 4
reference-shifted · 4 sensitivity-centered. Denominators include levels and
rates. Details and fitted constants: `audit/COORDINATE_AUDIT.md`.

Information boundary: 4th-order centered 5-point stencils. **This is
retrospective reconstruction, not forecasting** — symmetric stencils are
deliberate and admissible.

## 5. Selected representation

    C* = C0 + { Q[ẏ|x], Q[y|x] }        12 coordinates

Selected on train+validation only, frozen to
`sir/frozen_selection/FROZEN_REPRESENTATION.json` (sha256 `96ee24b2c5f22e51…`).

The search chose the **plain masked quotients** — not the phase derivative, not
the reference-shifted or sensitivity-centered variants, all of which were
available. Reported as found.

The recovered relation is

    z = 28.0000048 − 0.9999995·Q[ẏ|x] − 1.0000067·Q[y|x]

against the analytic identity `z = ρ − (ẏ+y)/x`, ρ=28. The search independently
recovered both the structure and the parameter, from z-free inputs.

## 6. Sparse-estimator results (PySINDy STLSQ)

PySINDy STLSQ was used as the common sparse estimator on the evaluated coordinate
matrices (precomputed features, not a state-derivative SINDy call).

| Representation | coords | terms | test RMSE | R² | cond |
|---|---|---|---|---|---|
| C0-center | 2 | 0 | 9.043 | −0.0005 | 3.9 |
| C0 matched | 10 | 10 | 9.044 | −0.0009 | 2.6×10¹² |
| C_all | 38 | 29 | **1.30×10⁻⁵** | 1.000 | 7.5×10¹⁶ |
| C* | 12 | 12 | 3.32×10⁻⁵ | 1.000 | 2.6×10¹² |

σ_z = 9.04, so both raw baselines are at predict-the-mean. **PySINDy(C_all)
slightly beats PySINDy(C\*)** — stated directly, as required.

## 7. MLP results (5 seeds, identical architecture)

| Representation | coords | params | test RMSE (mean ± sd) | R² |
|---|---|---|---|---|
| C0-center | 2 | 4 417 | 1.319 ± 0.012 | 0.9787 |
| C0 matched | 10 | 4 929 | 0.2476 ± 0.0332 | 0.9992 |
| C_all | 38 | 6 721 | 0.0534 ± 0.0051 | 0.99997 |
| C* | 12 | 5 057 | **0.0288 ± 0.0056** | 0.99999 |

Here C* is best — 8.6× better than the matched raw baseline for a 2.6% parameter
increase, and better than C_all with a third of the coordinates.

## 8. Complexity, conditioning, coverage

C* uses 12 of 38 coordinates and is 4 orders better conditioned than C_all
(2.6×10¹² vs 7.5×10¹⁶, the latter effectively rank-deficient). Retained sample
support 88.5% of test samples, identical rows for every method.

## 9. Robustness (predeclared secondary analyses)

**Noise** (added to x, y *before* any coordinate is built; coordinates refitted
on noisy train):

| σ_noise | learner | C0 | C_all | C* |
|---|---|---|---|---|
| 0 | STLSQ | 9.044 | 1.3e−5 | 3.3e−5 |
| 0 | MLP | 0.267 | 0.0523 | 0.0258 |
| 0.01 | STLSQ | 9.012 | **2.211** | 5.331 |
| 0.01 | MLP | **0.757** | 0.847 | 0.817 |
| 0.05 | STLSQ | 8.921 | **2.995** | 7.501 |
| 0.05 | MLP | **1.598** | 1.672 | 1.616 |

**This is the headline negative result.** Under 1% observational noise the MLP's
representation advantage disappears entirely — the raw matched baseline becomes
the best input. The derived quotients differentiate and divide noisy signals, and
that amplification outweighs the structural gain. The sparse estimator keeps a
large benefit (9.0 → 2.2) because it cannot express the nonlinear relation from
raw inputs at all.

**Sample efficiency** (at σ=0.01): no advantage. MLP with C0 is best at every
training fraction (10% → 100%); STLSQ keeps its ~4× advantage throughout. There
is no low-data regime where the expanded representation rescues the MLP.

**Resolution** (noiseless): the advantage degrades gracefully. STLSQ(C*)
3.3e−5 → 5.2e−4 → 8.0e−3 at stride 1/2/4; MLP(C*) 0.026 → 0.043 → 0.077.

## 10. Audits

All pass: `DATA_AUDIT.md`, `LEAKAGE_AUDIT.md`, `FAIRNESS_AUDIT.md`,
`COORDINATE_AUDIT.md`, `REPRODUCIBILITY_AUDIT.md`. 27/27 tests
(`logs/pytest_final.txt`).

The near-exact result was audited under rule 9 and is **structural, not
leakage**: the recovered coefficients reproduce ρ=28 and −1, −1 from z-free
inputs; raw features correlate with z at |r|≈0.004.

## 11. Limitations

1. **The SIR MCP was not used for the SIR-side computations.** Dalia binds one
   project environment at a time and the Lorenz project could not be loaded from
   the MCP; there is no MCP operation to switch it. The restricted-SIR contract
   and the end-to-end SIR evaluation were therefore executed locally. The
   relational coordinates are *not* ad hoc — they come from the audited reference
   implementation verified against Archaieus at 1e-12 — but Step 8's
   "SIR selection + SIR relation fitting vs SIR selection + PySINDy fitting"
   comparison is **not** available. See `audit/SIR_MCP_CAPABILITY_AUDIT.md`.
2. **The noiseless task is degenerate.** z is *exactly* linear in C*, so the
   primary comparison saturates at machine precision and cannot discriminate
   further. The noise sweep carries the real signal.
3. **One system, one task.** Lorenz with hidden z; no claim generalises beyond it.
4. **Selection is greedy**, not exhaustive; a different rule might select
   differently.
5. **MLP is small** (64,64). A larger network might close the noiseless gap.
6. `run_benchmark.py` re-derives rather than loads the freeze (see
   `REPRODUCIBILITY_AUDIT.md`).

## 12. Strongest justified conclusion

> Conventional sparse recovery is contained exactly within a restricted SIR
> contract (agreement to 4×10⁻¹⁴). On a hidden-variable reconstruction task,
> searching over an admissible z-free coordinate grammar produced a 12-coordinate
> representation that reduces held-out error by five orders of magnitude for a
> sparse estimator and 8.6× for an unchanged MLP, and that independently
> recovers the exact analytic relation including its parameter. **However, the
> MLP benefit does not survive 1% observational noise**, so representation
> utility here is demonstrated for the sparse estimator and, on clean data only,
> for the neural learner.

What this does **not** show: that SIR beats PySINDy. PySINDy consumes the same
expanded features and does marginally better with all of them than with the
selected subset. The defensible SIR-specific contribution is that construction,
admissibility, selection and provenance were part of the declared procedure, and
that the selected representation is smaller (12 vs 38) and far better conditioned
(10¹² vs 10¹⁶) at comparable accuracy.

## 13. Classification

**C — LEARNER_SPECIFIC_AUGMENTATION.**

The noiseless primary benchmark alone would support A: containment holds and the
expanded representation improves both learners substantially. It is *not*
upgraded, because the predeclared robustness ablation shows the benefit is
learner-specific once observational noise is present — retained by the sparse
estimator, lost by the MLP. Reporting A would require ignoring a predeclared
secondary analysis.
