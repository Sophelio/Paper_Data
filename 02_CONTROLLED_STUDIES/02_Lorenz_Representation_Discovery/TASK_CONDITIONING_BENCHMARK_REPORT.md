# Lorenz task-conditioning benchmark — report

**Date:** 2026-08-27
**Classification: B — TASK_CONDITIONING_WITH_REPRESENTATIONAL_PARITY**
**`SIR_IMPLEMENTATION_STATUS` = `MCP_NATIVE_PRIMITIVES_PLUS_AUDITED_CONTRACT_HARNESS`**
**Implementation surface: `IMPLEMENTATION_SURFACE_PARTIAL`**

---

## 1. What motivated this design

The first benchmark (`Lorenz/benchmark/`) established containment and showed
that an expanded coordinate library helps, but three of its findings shaped this
study and are therefore **exposed**: accuracy and parsimony already disagreed
(C_all 1.30e−5 vs C* 3.32e−5 with 38 vs 12 coordinates); the clean MLP advantage
vanished under 1% noise; and the selected coordinates were `Q[ẏ|x], Q[y|x]`,
which satisfy the analytic identity `z = ρ − (ẏ+y)/x`.

Those observations motivated a *compact* contract, a *robust* contract, and a
strong polynomial baseline. Full disclosure:
`audit/PRIOR_KNOWLEDGE_AND_POSTHOC_DESIGN_AUDIT.md`.

## 2. Why the old test set is exposed

Its protected results were inspected and used for design. Reusing them as
confirmatory evidence would be circular. All 48 trajectories are therefore
**development** data here, used with 6-fold GroupKFold rather than a re-invented
internal test split.

## 3. The new confirmation ensemble

24 trajectories, seed `20260827904` (≠ development `20260827`), from a different
seed trajectory (x₀ = −3.1, 2.7, 19.4; tmax 900; burn-in 40 vs development
(1,1,1)/400/20). Minimum initial-state separation from all 48 development
states **0.676** against a declared threshold of 0.5; **0 violations**.
Development data are referenced by hash and never copied.

`run_confirmation.py` verified all **12 frozen hashes** before reading
confirmation data and aborts otherwise.

## 4. What the SIR MCP actually did

**Natively:** the containment contract. Three runs on
`lorenz_dt001_exact_derivatives`, exact support in all three equations.

**Not natively:** contracts B/C/D. The MCP exposes no held-out validation, no
declarable task utility and no qualified-model-set primitive. Those ran in the
audited `sir_contract/` harness with PySINDy STLSQ as `R_q(C)`. Every operation
is mapped in `audit/FRAMEWORK_VS_MCP_IMPLEMENTATION_AUDIT.md`.

One semantic finding: SIR splits `data_processing` into a feature family (`x`)
and a target family (`y`), so the target's own level is unavailable unless `y` is
included. A first run with `data_processing=["x"]` could not express
`dz/dt = xy − (8/3)z` and returned error 1431.

## 5. Object and contracts

`O = (D, Ω_obs, S, E, Π, A)` with `D = {x, y}` explanatory and `z` supervised-only;
`I_k = {x[k−2..k+2], y[k−2..k+2]}`; `E` numerical (clean) or Gaussian on x,y
applied **before** all coordinate construction (noisy). Definitions:
`contracts/CONTRACT_DEFINITIONS.md`.

| Contract | Utility |
|---|---|
| `q_accuracy` | minimum mean grouped-CV RMSE |
| `q_compact` | accuracy-equivalent, then fewest coordinates → fewest terms → best conditioning → most stable |
| `q_robust` | minimum worst-case CV error over σ ∈ {0, 0.005, 0.01}, then the same hierarchy |

## 6. Containment (MCP-native)

| | SIR (MCP) | true | error |
|---|---|---|---|
| dx/dt | `10.000[y] − 10.000[x]` | 10y − 10x | 1.4e−6 |
| dy/dt | `27.998[x] − 0.999[y] − 1.000[x][z]` | 28x − y − xz | 5.3e−6 |
| dz/dt | `−2.667[z] + 1.000[x][y]` | xy − (8/3)z | 6.7e−6 |

Exact support, all three. Max coefficient deviation ≈ 2×10⁻³ — larger than
PySINDy's ~10⁻¹⁴ in benchmark 1 because SIR's search normalises and optimises
differently. **Containment, not superiority.**

## 7–9. Contract selections (development only)

| Contract | Selected | Coords | Equivalent set | Margin from |
|---|---|---|---|---|
| `q_accuracy` | **C_all** | 38 | 1 | — |
| `q_compact` | **C0+Q_pair** | 12 | 4 | practical floor |
| `q_robust` | **C_all** | 38 | 1 | SE |

## 10. Did the representation change across contracts?

**Yes, twice, and for different reasons.**

- `q_accuracy` ≠ `q_compact` on the **same clean object**: accuracy wants all 38
  coordinates; compactness accepts 12 at 2.4× the error but 4 orders better
  conditioned (2.7e12 vs 8.4e16). This is the central positive result.
- `q_robust` ≠ `q_compact`: adding an uncertainty model to the object reverts
  the choice to `C_all`. The reason is visible on confirmation data — under 1%
  noise `C*_compact` degrades to 5.12 while `C_all` degrades only to 2.25. The
  robust contract detected the quotient representation's noise fragility from
  development data alone.

`q_robust` = `q_accuracy` in *coordinates*, so uncertainty changed the
qualification rather than the representation. Reported as found.

## 11–15. Protected confirmation (24 unseen trajectories, σ_z = 9.04)

**PySINDy STLSQ** (common sparse solver on supplied coordinate matrices):

| Representation | Coords | Clean RMSE | 1% noise RMSE |
|---|---|---|---|
| C0_matched (raw) | 10 | 8.607 | 8.607 |
| **C0_poly2 (conventional)** | 10 → 65 | **2.267** | **3.004** |
| C0_poly3 | 10 → 285 | 2.317 | 3.004 |
| C_all = C*_accuracy = C*_robust | 38 | **1.353e−5** | **2.245** |
| C*_compact | 12 | 3.258e−5 | 5.120 |

The degree-2 polynomial baseline is genuinely strong — it improves on linear raw
by 3.8× — and it is **not** removed by the expanded representation on clean data
(5 orders) but *is* competitive under noise (3.00 vs 2.25).

**MLP** (fixed 64-64, 5 seeds):

| Representation | Params | Clean | 1% noise |
|---|---|---|---|
| C0_matched | 4 929 | 0.2892 ± 0.025 | 0.8394 ± 0.032 |
| C_all | 6 721 | 0.0460 ± 0.003 | 0.8419 ± 0.038 |
| C*_compact | 5 057 | **0.0183 ± 0.003** | **0.8025 ± 0.032** |

Clean: `C*_compact` is best — 16× better than raw for +2.6% parameters, and
better than `C_all` with a third of the coordinates. **Under noise all three
collapse to ≈0.80–0.84, within ~1.3 SE.** The first benchmark's negative
finding replicates on genuinely unseen data.

## 12. PySINDy(C_all) and SIR-selected representations

PySINDy given the full expanded library reaches 1.353e−5 — identical to
`C*_accuracy`, because `q_accuracy` selected `C_all`. On clean data PySINDy with
all the coordinates is the best sparse result available; the compact
representation costs a factor 2.4 in RMSE to gain 4 orders of conditioning.

## 14. External-contract PySINDy wrapper

`pysindy/external_contract_wrapper/wrapper.py` reimplements grouped CV, the
one-SE/floor equivalence rule and the lexicographic ordering **without importing
`sir_contract`**, enforced by 5 passing tests (static AST analysis + dynamic
module check). Its rules were verified on a synthetic score table to reproduce
the harness's decisions (`choose_min` → the accuracy pick; floor-based
equivalence → the compact pick).

**A full end-to-end wrapper re-selection over all 17 candidates was not executed**
— see Limitations. What is established is that the decision logic is
independently implemented and behaves identically on controlled inputs.

## 16. Complexity, conditioning, coverage, stability

| | C0 | poly2 | C_all | C*_compact |
|---|---|---|---|---|
| coordinates | 10 | 10 (65 features) | 38 | 12 |
| active terms (clean) | 10 | 65 | 32 | 12 |
| condition number | 2.6e12 | — | **8.4e16** | **2.7e12** |
| coverage | 88.5% | 88.5% | 88.5% | 88.5% |

All methods scored on the identical retained support.

## 17. Robustness

`C*_compact` degrades 3.26e−5 → 5.12 (×1.6e5); `C_all` degrades 1.35e−5 → 2.25
(×1.7e5) but from a base that leaves it below the polynomial baseline. Quotient
coordinates divide by a near-zero denominator and differentiate noisy signals;
that is the mechanism.

## 18–19. Audit verdicts

| Audit | Verdict |
|---|---|
| Prior-knowledge / post-hoc design | **disclosed**, design demonstrably informed by exposed results |
| Confirmation integrity | **PASS** — new seed, new seed trajectory, 0 near-duplicates, hash-verified |
| Framework vs MCP implementation | **IMPLEMENTATION_SURFACE_PARTIAL** — mapped operation by operation |
| Equivalence rule | **corrected pre-freeze**; selection stable across 4 decades |
| PySINDy capability | **PASS** — no claim contradicts the 2.1.0 API |
| Wrapper independence | **PASS** — 5 tests |
| Freeze enforcement | **PASS** — 12 hashes verified before confirmation |

## 20. Classification

**B — TASK_CONDITIONING_WITH_REPRESENTATIONAL_PARITY.**

Different contracts produced meaningfully different qualified representations
(38 vs 12 coordinates; 8.4e16 vs 2.7e12 conditioning) at predictive performance
that is comparable on the scale that matters (both ~10⁻⁵, five orders below the
strongest conventional baseline). It is **not A**, because the distinctions are
tradeoffs in complexity and conditioning rather than a protected-utility
*advantage*, and because the task-conditioning layer is not MCP-native. It is
**not D**, because the contracts demonstrably selected differently on new data.
It is **not E**: no leakage, no post-confirmation tuning, the freeze held, and
coordinate provenance is established.

## 21. Strongest justified claim

> Restricted to the conventional full-state problem, an MCP-native SIR contract
> recovers the canonical Lorenz generator exactly. Posed against one clean
> partially-observed object, an accuracy contract and a compactness contract
> select *different* qualified representations — 38 coordinates versus 12, with
> four orders of magnitude difference in conditioning and comparable
> reconstruction error on 24 previously unseen trajectories. Adding an
> observational-uncertainty model to the same object reverts the selection,
> because the compact representation is noise-fragile. There is no
> task-independent best representation here.

## 22. Explicit non-claims

- **Not** that PySINDy cannot do this. It consumed every coordinate, served as
  the solver throughout, and with the full library gives the best clean sparse
  result.
- **Not** that SIR beats PySINDy or the MLP.
- **Not** an MCP-native demonstration of task conditioning.
- **Not** a discovery of `Q[ẏ|x], Q[y|x]` — the first benchmark already exposed
  them.
- **Not** learner independence: the MLP advantage does not survive 1% noise.

## Limitations

1. Task-conditioning is executed in the harness, not the MCP.
2. The one-SE rule was corrected mid-study (pre-freeze, on development
   evidence); it changed a headline outcome. Mitigated by a 4-decade sensitivity
   sweep, not eliminated.
3. The external wrapper's rules are verified on controlled inputs, not by a full
   independent re-selection over all candidates.
4. Selection CV used a stride-8 row subsample for tractability (confirmation is
   stride 1).
5. `C_all_poly2` was dropped from the candidate set pre-freeze for runtime.
6. One system, one task; the noiseless problem is near-degenerate because z is
   almost exactly linear in the quotient coordinates.
