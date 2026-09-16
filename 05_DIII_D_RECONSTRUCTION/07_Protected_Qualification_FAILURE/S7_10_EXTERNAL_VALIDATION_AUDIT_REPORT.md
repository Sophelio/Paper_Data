# S7.10 — External validation and gate evaluation: internal audit report

Stage **S7.10** · Freeze `D3D-SIR-S7.10-EXTERNAL-VALIDATION-AND-GATE-EVALUATION-V1`
Parent `D3D-SIR-S7.9-DEVELOPMENT-SELECTION-AND-PREEXTERNAL-FREEZE-V1`

---

## 1. Executive verdict

Two verdicts, reported separately because they differ.

**Stage execution: `EXECUTED_AS_FROZEN`** — 57/57 acceptance checks, artifact
integrity `COMPLETE_AND_VERIFIED`. Every preflight gate passed before the first
external value was opened; the frozen object was evaluated exactly as frozen;
nothing was repaired after the results appeared.

**Primary scientific result: `NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER`.**
Mandatory gates **V3** and **V6** failed. Stage status is
`PRIMARY_EXTERNAL_GATE_FAILURE`, not `FROZEN_WITH_QUALIFICATIONS`, so the
failure is not hidden inside a qualified pass.

```
Delta_0 = -0.180095   meets  <= -0.01
Delta_1 = +0.532091   FAILS  <= -0.01     (persistence beats the representation)
```

The failure is robust: 0 of 42 leave-one-discharge-out cohorts satisfy V3.

The result is highly structured, and the structure is reported in full because
it is scientifically informative: the **median** external NRMSE is 0.1699 —
essentially the development FIT of 0.1664 — and 40 of 42 discharges transfer at
that level. Two earlier-era discharges reach NRMSE ≈ 11.9 and dominate the mean,
which is the quantity the frozen gate uses. The median was **not** substituted
for the mean.

## 2. Parent verification

Eleven authoritative freezes verified through S7.9. **All 45 S7.9 artifacts
reproduce byte-for-byte.** Confirmed unchanged: target `density`; `C_dev_star`
support id and size 12; `DEVELOPMENT_REPRESENTATION_LOCK` hash;
`DEVELOPMENT_RELATION_OLS_V1`; B0/B1/B1A definitions; `B2 α=1` with 78
predictors; `B3` sklearn 1.9.0 with `random_state=2026090502`; `H0 α=1` with 70
predictors; external cohort 42 = 24 + 18; two-seed sensitivity `NOT_EXECUTED`.
The installed sklearn was checked against the frozen version and matches exactly.

Verdict: zero substantive drift.

## 3. Pre-external freeze verification

**13 substantive entries, 0 mismatches.** The `PRE_EXTERNAL_MODEL_FREEZE.json`
file hash also matches the value recorded independently inside `S7_9_FREEZE.json`.
Covered: selected support and coordinate definitions, canonical parser, ontology,
admissible universe, search policy, explored frontier, utility policy and
elimination ledger, estimator, preprocessing, validation geometry, denominator
rules, interpretation flags, all six baseline configurations, inference protocol,
cohort partition metadata.

## 4. Timestamp ordering

```
PRE_EXTERNAL_MODEL_FREEZE   2026-09-05T20:32:08.992754+00:00
FIRST_EXTERNAL_VALUE_ACCESS 2026-09-05T22:48:51.998142+00:00
```

Strict ordering asserted in code before the first archive was opened; the
evaluation script refuses to run unless the preflight verdict is
`PREFLIGHT_PASSED`. No external value was opened during preflight.

## 5. Canonical parse

Frozen parenthesis-depth-aware parser: 12 atoms recovered, canonical
serialization identical to the frozen `support_id`, identical to the S7.9
artifact's atom list, and the full registry checksum re-run at
**162 845 / 162 845**. The naive splitter was never used operationally.

## 6. S7.11 sensitivity predeclaration

Written and hashed (`da24fbe38141f0c7…`) **before** first external access, and
**not executed**. Three sensitivities declared: the support-family external
sensitivity over all 217 unique development-bootstrap winning supports (no
top-K, no external-result-based selection); `PRIMARY_MINUS_PRMTAN_NEPED_ANCESTRY`
(the 7 coordinates without `prmtan_neped` ancestry, no replacements, no
re-search); and `PRMTAN_NEPED_ONLY`. The two-seed search-depth sensitivity is
carried unchanged as `DECLARED_OPTIONAL` / `NOT_EXECUTED`.

Declaring these before the external result existed is what makes them
interpretable now that the result is negative.

## 7. Inference policy pre-value freeze

Parent audit first: the inferential unit, the ≥10 000 replicate requirement, the
95 % level, blocks-to-discharge aggregation, the V3 rule, the CI's reporting-only
role, the V6 external counts and outcome vocabulary, the 0.01 win/tie/loss floor
and the LODO requirement were **already frozen upstream** and were used as
found. Only genuinely unspecified implementation details were completed: RNG
seeds, percentile-interval CI type, interpolation method, index sharing across
methods, and the era practical-direction thresholds. No parent requires BCa.

Hashed `812920c4edecd844…` before first external access.

## 8. First external access

Recorded in `manifests/FIRST_EXTERNAL_ACCESS.json`. Zero development discharges
were opened in the external loop; the loop asserts membership and would raise
`FIREWALL_BREACH` on any development id.

## 9. External cohort

42 discharges, 24 earlier / 18 later, verified against the frozen partition and
the trajectory index. 78 raw predictors plus the target read per discharge;
runtime 39 s.

## 10. Domain / denominator audit

Three level denominators are required by `C_dev_star`: `prmtan_neped`, `ece22`,
`cerqtit10`. Under the inherited `DENOMINATOR_ADMISSIBILITY_PRIMARY_V1`,
**378 / 378 checks passed**. Minimum observed `eta` 0.0997 (`cerqtit10`,
195642 block C) against a threshold of 0.05; per-denominator minima 0.0997,
0.1107, 0.1689. Zero blocks marked `RELATIONAL_REPRESENTATION_NOT_APPLICABLE`.
No epsilon, clipping, shift, bounded reciprocal or repair.

## 11. Common support

All 126 blocks comparison-eligible; every method scored on identical protected
rows; zero ineligible blocks; no selective deletion; no method scored a
different mask. **V7 PASS.**

## 12. Relational evaluation

`C_dev_star` applied exactly: coordinates constructed from the frozen
definitions, standardized on calibration rows only with the `sd ≤ 0 → 1.0`
convention, applied unchanged to protected rows, affine OLS with fitted
intercept, coefficients discharge-local and block-local. No global coefficient
exists or was used.

## 13–18. Comparators

| | configuration | external tuning |
|---|---|---|
| **B0** | calibration mean over the protected block | none |
| **B1** | last calibration sample held constant | none |
| **B1A** | `y_k = a + φ y_{k−1}`, OLS on calibration, recursed from the final calibration value, no teacher forcing | none |
| **B2** | ridge `α=1`, 78 target-admissible primitive levels, unpenalized intercept | none |
| **B3** | `HistGradientBoostingRegressor(random_state=2026090502)`, sklearn 1.9.0, 78 predictors | none |
| **H0** | ridge `α=1`, 70 hardened levels | none |

All six evaluated exactly as frozen. No alpha was re-selected, B3 was not tuned,
and no configuration was touched after any result was visible.

## 19. Primary metrics

| Method | mean | median | earlier mean | later mean |
|---|---|---|---|---|
| **REL** | **0.7424** | **0.1699** | 1.1643 | 0.1798 |
| B0 | 0.9225 | 0.9100 | 0.8735 | 0.9877 |
| B1 | 0.2103 | 0.1765 | 0.2104 | 0.2101 |
| B1A | 0.3504 | 0.3329 | 0.3325 | 0.3744 |
| B2 | 0.2804 | 0.1893 | 0.2657 | 0.3000 |
| B3 | 0.3060 | 0.1806 | 0.3566 | 0.2384 |
| H0 | 0.2828 | 0.1846 | 0.2644 | 0.3073 |

By block, REL means: A 0.2089 · **B 1.8475** · C 0.1708. The pooled failure lives
entirely in block B.

## 20. `S_pers`

Defined on all 42 discharges. Mean **−402.52**, median **+0.0943**, positive on
**24 of 42**, range −11 672 … +0.798; earlier mean −704.37, later mean −0.0475.
Reporting only; not a V3 threshold and not a replacement for NRMSE. Its mean is
uninformative — an unbounded ratio metric — which is precisely why V3 was frozen
on NRMSE.

## 21. Paired comparisons

| Comparator | mean `Δ` | median `Δ` | W/T/L |
|---|---|---|---|
| B0 | −0.1801 | −0.7318 | 40/0/2 |
| **B1** | **+0.5321** | −0.0052 | 18/7/17 |
| B1A | +0.3919 | −0.1693 | 35/0/7 |
| B2 | +0.4620 | −0.0208 | 23/4/15 |
| B3 | +0.4364 | −0.0147 | 22/2/18 |
| H0 | +0.4596 | −0.0192 | 23/5/14 |

Sign convention fixed throughout: negative = relational lower error.

## 22. Bootstrap CIs

10 000 replicates; seeds 2026090503 pooled, 2026090504 earlier, 2026090505 later;
percentile interval `[2.5, 97.5]` with `method="linear"`; **one shared
discharge-index matrix per cohort reused across every comparator**, preserving
paired geometry. Pooled CI against B1: `[−0.0366, +1.3737]`. No CI was converted
into a gate.

## 23. Win / tie / loss

Uses the already-frozen 0.01 floor; reporting only; does not alter V3. The
pattern is diagnostic: near-even against persistence (18/7/17) while the mean is
strongly adverse.

## 24. LODO

Full 42-fold leave-one-discharge-out for every comparator.
**0 of 42 cohorts satisfy V3.** Most influential discharge 187019 (187022 for
the B0 comparison). LODO range ≈ 0.29–0.31 for every comparator. LODO is
sensitivity evidence and does not replace the full-cohort verdict.

## 25. Processing-era results

| Era | `Δ₀` | direction | `Δ₁` | direction |
|---|---|---|---|---|
| earlier (24) | +0.291 | `MATERIAL_ADVERSE` | +0.954 | `MATERIAL_ADVERSE` |
| later (18) | −0.808 | `MATERIAL_IMPROVEMENT` | −0.030 | `MATERIAL_IMPROVEMENT` |

Era medians are 0.182 (earlier) and 0.170 (later) — indistinguishable. The mean
separation is entirely the two outlier discharges. The later era meets both V3
thresholds on its own; this is recorded as evidence and **not** used to narrow
the domain, which the contract forbids.

## 26. V1–V10 gate table

| Gate | Mandatory | Result |
|---|---|---|
| V1 information boundary | yes | PASS |
| V2 development-only discovery | yes | PASS |
| **V3 nontrivial skill** | yes | **FAIL** |
| V4 fair raw comparison | yes | PASS |
| V5 external structural transfer | yes | PASS |
| **V6 processing-era robustness** | yes | **FAIL** |
| V7 common support | yes | PASS |
| V8 discharge-level inference | yes | PASS |
| V9 sensitivity | no | PENDING_S7.11 |
| V10 numerical provenance | yes | PASS |

Full rules, evidence, qualifications and claim consequences in
`QUALIFICATION_GATE_RESULTS.md` and `V_REC_EXTERNAL_RESULTS.json`.

V6's three-valued S7.2C schema is conditioned on pooled V3 passing; it did not,
so V6 resolves to FAIL under the parent four-state gate vocabulary rather than to
an invented status.

## 27. `Omega_rec`

All 42 discharges and 126 blocks were evaluated; none was `NOT_APPLICABLE`; no
result-dependent deletion occurred; the domain was never expanded. The
**supported claim domain is EMPTY**, because a mandatory gate failed on the full
external domain and no era-specific success may substitute for it.

## 28. Interpretation qualifications

**Failure mode — diagnosis, not repair.** The pooled failure is unguarded linear
extrapolation of the C2 self-product `PROD(gasa,gasa)`. On 187019 block B the
gas-injection valve command spans 5.3 × 10⁻³ … 4.1 × 10⁻² on calibration and
reaches 1.63 on the protected block; squared, that is ~8 979 calibration standard
deviations. The next-largest excursion anywhere in the cohort is 13 σ. Log–log
correlation between maximum protected excursion and discharge error: **0.930**.

The frozen `DENOMINATOR_ADMISSIBILITY_PRIMARY_V1` rule guards denominators only —
the S7.6R policy states that C0, C1, C2 and C6 have no denominator and no gate —
so a squared actuator command is unguarded by construction. This is not a rule
violation, not leakage, and not an implementation error. It was recorded and
**not acted on**: no coordinate removed, no range rule added, no discharge
deleted. Any prospective range-admissibility rule for non-denominator
constructors is a new contract decision for a future study.

**Support identifiability.** Development `BOOT_SELECTION_FREQ = 0.093` across
217 distinct winners. `C_dev_star` is one deterministically selected
representative of a broad development-side support-equivalence family. No
unique-support claim, no canonical-equation claim, no global-optimality claim
appears anywhere. Coordinate-level recurrence is reported as ingredient-level
stability only.

**`prmtan_neped`.** Retained exactly. Pedestal electron density is a same-family
observable whose provenance is certified independent of the target signal under
the frozen information boundary. This establishes no target-signal ancestry; it
does **not** establish physical or statistical independence from line-averaged
density. That semantic proximity is the reason the S7.11 ablations were
predeclared.

**`pcdiamag3`.** `UNCALIBRATED_SIGNAL`. Its fitted coefficient has no certified
physical-dimensional interpretation, recorded whether or not the coordinate
appears influential.

**Support size.** Twelve coordinates over thirteen primitive ancestors, at the
frozen maximum support size. Not described as minimal, uniquely parsimonious or
sensor-compressed.

**Development versus external.** Development FIT 0.166398 alongside external
median 0.1699 and external mean 0.7424, reported descriptively. No
train/test degradation gate exists and none was introduced; similar medians are
not evidence of distributional identity.

## 29. Files

6 Markdown (limit 20) · 10 result CSV · 6 JSON · 5 manifests · 5 scripts.

## 30. Reproduction

```bash
python scripts/s7_10_a_preflight.py           # gates; opens no external value
python scripts/s7_10_b_external_eval.py       # FIRST EXTERNAL ACCESS; evaluation
python scripts/s7_10_c_inference.py           # paired stats, bootstrap, gates
python scripts/s7_10_d_failure_diagnostic.py  # failure mode (reporting only)
python scripts/s7_10_e_freeze.py              # Omega_rec, acceptance, freeze
```

Python 3.13.5 · numpy 2.5.2 · pandas 3.0.5 · scikit-learn 1.9.0 ·
Windows-11-10.0.26200-SP0.

## 31. Recommendation for S7.11

**`PRIMARY_EXTERNAL_GATE_FAILURE`.**

The frozen object failed a mandatory external gate. Under the governing
principle that is the answer, not a workflow fault, and S7.7–S7.9 may not be
reopened to repair it.

S7.11 should still run, and its predeclared design is now more valuable than it
was when written:

- the **support-family sensitivity** over all 217 development-bootstrap winners
  answers whether every member of the equivalence class fails externally, or
  whether `C_dev_star` was an unlucky draw from a family that mostly transfers —
  a question with real bearing on how the negative result should be interpreted;
- the **`prmtan_neped` ablations** quantify how much of the observed
  reconstruction is associated with the semantically close pedestal-density
  diagnostic;
- V9 remains open and the two catastrophic discharges are exactly the kind of
  single-discharge dependence V9 exists to characterise.

None of those may alter the S7.10 result, and none was executed here. One
observation is worth carrying into whatever follows this study: the contract's
only partial-map guard was written for division, and the failure arrived through
a product.
