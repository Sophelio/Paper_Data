# S7.10 — Qualification gate results

Machine-readable: `V_REC_EXTERNAL_RESULTS.json`.

**Two mandatory gates failed: V3 and V6.** Under the frozen contract, the
primary `q_rec` result may **not** be presented as a successful nontrivial
structural-transfer result.

---

## The table

| Gate | Requirement | Mand. | Result |
|---|---|---|---|
| **V1** information boundary | no target leakage; no unresolved target ancestry | yes | **PASS** |
| **V2** development-only discovery | target, ontology, support, estimator, thresholds fixed without external outcomes | yes | **PASS** |
| **V3** nontrivial skill vs B0/B1 | `Δ₀ ≤ −0.01` **and** `Δ₁ ≤ −0.01` | yes | **FAIL** |
| **V4** fair raw comparison vs B2/B3 | fairness on identical information and geometry | yes | **PASS** |
| **V5** external structural transfer | support frozen and hashed before any external evaluation | yes | **PASS** |
| **V6** processing-era robustness | results reported separately for 24 earlier / 18 later | yes | **FAIL** |
| **V7** common support | identical scored samples | yes | **PASS** |
| **V8** discharge-level inference | discharge is the independent unit | yes | **PASS** |
| **V9** sensitivity | no catastrophic dependence on one discharge/block/realization | **no** | **PENDING_S7.11** |
| **V10** numerical provenance | no claim on interpolation-created resolution without qualification | yes | **PASS** |

---

## V3 — nontrivial skill · **FAIL**

```
Delta_0 = mean_external( NRMSE_REL − NRMSE_B0 ) = −0.180095    meets  ≤ −0.01
Delta_1 = mean_external( NRMSE_REL − NRMSE_B1 ) = +0.532091    FAILS  ≤ −0.01
PASS requires BOTH.
```

The frozen representation beats the calibration-mean baseline comfortably and is
**materially worse than persistence**. This is the same failure mode that
retired the previous `q_rec` attempt — and it was retired *after* the fact,
which is precisely why this gate was frozen before the target existed.

**The failure is robust.** Across the 42 leave-one-discharge-out cohorts,
**0 of 42** satisfy V3. No single discharge is responsible.

Confidence intervals are **reported, not used as a significance threshold**.
The pooled 95 % CI for `Δ₁` is `[−0.037, +1.374]` — wide, and straddling zero,
which reflects the heavy tail rather than rescuing the verdict.

No rescue was attempted: the support was not changed, `FIT_best` was not
substituted, no bootstrap winner was swapped in, no metric or threshold was
altered, no discharge was deleted, no era was dropped.

## V6 — processing-era robustness · **FAIL**

| Era | n | `Δ₀` | direction | `Δ₁` | direction |
|---|---|---|---|---|---|
| earlier | 24 | **+0.291** | `MATERIAL_ADVERSE` | **+0.954** | `MATERIAL_ADVERSE` |
| later | 18 | **−0.808** | `MATERIAL_IMPROVEMENT` | **−0.030** | `MATERIAL_IMPROVEMENT` |

The S7.2C three-valued outcome schema (`PASS` / `PASS_WITH_QUALIFICATION` /
`FAIL_FOR_FULL_DOMAIN`) is **conditioned on pooled V3 passing**. Pooled V3 did
not pass, so none of those three branches applies and V6 resolves to **FAIL**
under the parent four-state gate vocabulary.

> The later era meets both V3 thresholds on its own. **This is recorded as
> evidence and is not a claim.** Narrowing the domain to the later era in order
> to obtain a passing V3 is explicitly forbidden, and was not done. V6 may not
> rescue V3.

## V4 — fair raw comparison · **PASS**

V4 asks whether B2 and B3 were compared *fairly*, not whether the relational
representation won. Verified: identical 42-discharge cohort, identical
calibration and protected rows, identical target, identical calibration-fitted
preprocessing, the frozen information boundary, and **zero external
hyperparameter tuning** (`B2 α=1`, `H0 α=1`, `B3` at defaults with
`random_state=2026090502`, all frozen before external access).

The relational representation is materially worse than B2, B3 and H0 in the
pooled mean. Under the frozen outcome reading this is the row
*"relational ≈ B2 or worse"* — **no representational accuracy claim is
available**. The gate still passes, because the comparison was conducted
properly.

## V5 — external structural transfer · **PASS**

```
PRE_EXTERNAL_MODEL_FREEZE   2026-09-05T20:32:08.992754+00:00
FIRST_EXTERNAL_VALUE_ACCESS 2026-09-05T22:48:51.998142+00:00
```

Strict ordering verified; all 13 substantive pinned hashes reproduced before the
first external value was opened. Local external calibration changed
**coefficients only** — never the support, never a coordinate definition. V5
governs freeze discipline, not performance; performance is V3's business.

## V1 — information boundary · **PASS**

All 13 primitive ancestors of `C_dev_star` are `certified_independent_of_target`
under the frozen S7.3R boundary, and all 12 coordinates carry
`TRANSITIVE_FROM_TARGET_INDEPENDENT_BOUNDARY`.

> **Required language.** `prmtan_neped` (pedestal electron density from a tanh
> fit) is a same-family observable whose provenance is **certified independent of
> the target signal** under the frozen information boundary. This establishes no
> target-signal ancestry. It does **not** establish physical or statistical
> independence from line-averaged density.

## V2 — development-only discovery · **PASS**

S7.9 recorded `V2_EVIDENCE_COMPLETE` across nine decisions. The representation
lock precedes every baseline hyperparameter; the pre-external package verified
13/13; zero external information existed before the freeze.

## V7 — common support · **PASS**

All 126 external blocks were comparison-eligible; every method scored on
**identical protected rows**; zero blocks excluded; no selective deletion. No
method silently scored a different mask.

## V8 — discharge-level inference · **PASS**

Blocks are aggregated to the discharge before every inferential quantity. All
paired differences, all bootstrap resampling (10 000 replicates over the 42
discharges) and all LODO operate on discharges, never on time samples.

## V9 — sensitivity · **PENDING_S7.11**

Not resolved here, and non-mandatory. LODO is computed and reported. The
S7.11 sensitivities were predeclared and hashed **before** first external
access and were **not executed**.

## V10 — numerical provenance · **PASS**

The S7.3R/S7.4 V2 source-cadence record is carried unchanged. No selected
coordinate carries an aliasing or upsample flag.

> `ID(pcdiamag3)` is `UNCALIBRATED_SIGNAL` — uncalibrated digitiser output for
> which no unit exists. Its fitted coefficient has **no certified
> physical-dimensional interpretation**. This is recorded whether or not the
> coordinate appears influential.

---

## Consequence

```
PRIMARY_EXTERNAL_RESULT = NO_QUALIFIED_NONTRIVIAL_STRUCTURAL_TRANSFER
```

Two mandatory gates failed. The result is not obscured by an overall average
score, and no era-specific success is offered as a substitute.
