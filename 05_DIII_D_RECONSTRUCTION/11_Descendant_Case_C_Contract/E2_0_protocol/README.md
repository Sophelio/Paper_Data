# S7.E2.0 — Discovery Epoch 2 protocol and resampling freeze

Freeze **`D3D-SIR-S7.E2.0-DISCOVERY-EPOCH2-PROTOCOL-V1`**
Status **`FROZEN_WITH_QUALIFICATIONS`** · 34/34 acceptance · lineage 15/15
Parent `D3D-SIR-S7.K2-OBSERVATIONAL-RANGE-SUPPORT-CONTRACT-V1`

> **No search, no fit, no baseline, no scoring.** Epoch 2 not started.
> S7.12 remains paused. Epoch 1 immutable.

---

## Architecture

```
DISCHARGE_GROUPED_CROSS_FITTED_DISCOVERY_AND_QUALIFICATION
```

**Claim type:**
`CROSS_DISCHARGE_QUALIFIED_RECONSTRUCTION_WITHIN_THE_FROZEN_62_DISCHARGE_OBSERVATIONAL_OBJECT`

**Why no new external cohort:** the former 42-discharge cohort is no longer
sealed — its targets were opened in S7.10 and it informed R1 and K2. Carving a
fresh "never seen" set from the same 62 would be fabrication. Cross-fitting
claims only that **no discharge's own target informed the support used to
reconstruct it**.

## Six deterministic outer folds

Sort by `(era ∈ [earlier, later], then discharge id)`; assign `fold = position mod 6`.
No seed. **One partition generated** — none could be chosen for its appearance.

| fold | n | earlier | later | discharges |
|---|---|---|---|---|
| 0 | 11 | 6 | 5 | 155537 160721 165022 165042 170394 187019 189647 195264 195273 195647 195655 |
| 1 | 11 | 6 | 5 | 159310 161136 165026 165043 170396 187020 189649 195265 195274 195648 195659 |
| 2 | 10 | 6 | 4 | 160715 161138 165027 165860 170411 187021 189650 195266 195626 195649 |
| 3 | 10 | 6 | 4 | 160717 161145 165028 165861 186997 187022 189651 195267 195638 195650 |
| 4 | 10 | 6 | 4 | 160719 161414 165029 165955 187017 187024 189652 195268 195642 195651 |
| 5 | 10 | 5 | 5 | 160720 165017 165031 165965 187018 189646 195261 195269 195645 195652 |

Every discharge held out exactly once. Discharge is the statistical unit.

## The access ordering (step 6 is the hinge)

```
1-2  build D_train candidate basis      → D_train PREDICTORS only
3-4  fresh search + frozen U_rec        → D_train predictors + D_train TARGETS
5-6  write and HASH the support         → SUPPORT CAN NEVER CHANGE AFTER THIS
7    freeze estimator + baselines       → D_train only
8-9  open D_test predictors, run V-RANGE
10-11 open D_test CALIBRATION targets, fit local coefficients
12-13 open D_test PROTECTED targets, score
```

Held-out predictor ranges may **not** influence candidate filtering — otherwise
the held-out fold shapes what is even considered, and the transfer is not a
transfer.

## Range support in two roles

| | threshold | from | role |
|---|---|---|---|
| training admissibility | **τ_train = 0.5** | `D_train` predictors | search-side, frozen here |
| held-out qualification | **τ = 1.0** | `D_test`, after support hash | contractual, K_REC_V2, **unchanged** |

Per-fold basis: **2 217–2 352** coordinates, all seven families. No global
pre-filter over all 62.

## ⚠ The disclosed risk

**`FULL_CROSSFITTED_DOMAIN_RANGE_SUPPORT` is the dominant risk to Epoch 2 —
larger than the reconstruction question.**

Measured target-blindly, before any search, over 4 000 random 12-coordinate draws
per fold:

| τ_train | basis | P(all 12 held-out supported), per fold | six-fold |
|---|---|---|---|
| 0.25 | 1 072–1 293 | 0.578–1.000 | **0.352** |
| **0.50** | **2 217–2 352** | **0.604–0.930** | **0.200** |
| 1.00 | 3 653–3 817 | 0.299–0.510 | 0.004 |

**Roughly 1 in 5.** Epoch 2 is more likely to fail on applicability than on
skill. **The standard was not weakened to improve those odds**, and τ_train was
chosen on interpretability, **not** by maximising the pass probability.

**No hostile discharge exists** — every discharge retains ≥ 93.8 % of its fold's
basis (median 99.8 %). The difficulty is compounding attrition across 12
coordinates × ~10 unseen discharges. The Epoch-1 culprit `PROD(gasa,gasa)` is
excluded from every basis by K_REC_V2 itself.

## Unchanged, deliberately

`U_rec` — no tail penalty, Rank 1 untouched, range support **not** rewarded
inside utility. `V3` — `Δ₀ ≤ −0.01 AND Δ₁ ≤ −0.01`. `V6` logic, block geometry,
all six baselines, discharge-level aggregation. **Epoch-1 frontier not reused.**

## Result tiers

`FORMAL_PASS` = the frozen gates. `CLEAN_DEMO_PASS` = formal pass **and**
`Δ₁ ≤ −0.05` (5× the frozen 0.01 floor) **and** full range support **and** no
out-of-fold discharge above NRMSE 1.0 **and** both eras improving. A reporting
tier only — it can never change the gate.

## Stop rule

```
EPOCH2_IS_FINAL_QREC_ATTEMPT = true
```

If Epoch 2 fails — on skill, era robustness, **or applicability** — do not revise
`K_rec`, add a threshold, change the split, remove shots, or launch Epoch 3.
Close `q_rec` as a qualified iterative case study; `q_desc` becomes the positive
DIII-D headline.

## Start here

| Document | Purpose |
|---|---|
| `E2_0_PROTOCOL_FINAL.md` | manuscript-ready section |
| `E2_0_PROTOCOL_AUDIT_REPORT.md` | full internal audit, 16 sections |
| `EPOCH2_CLAIM_BOUNDARY.md` | permitted and forbidden wording |
| `EPOCH2_STOP_RULE.md` | the one-attempt rule and what failure means |

## Two decisions for the human before E2.1

1. **τ_train = 0.5 or 0.25?** 0.25 roughly doubles the applicability odds on a
   basis half the size. I chose 0.5 on interpretability and recorded the
   alternative rather than optimising for odds.
2. **Accept that Epoch 2 will probably end on the applicability gate.** That is a
   legitimate outcome under the stop rule — but it should be entered with open
   eyes, not discovered in E2.1.

## Governance

Parent artifacts modified **0** (S7.9 45/45, S7.10 31/31, S7.11 26/26, S7.R1
21/21, S7.K2 29/29 reproduce) · `K_REC_V2` not modified · `U_rec` not modified ·
`V3` not modified · τ not modified · Epoch-1 frontier not reused · no search, fit,
baseline or scoring · target reads for protocol **0** · performance reads for
partition **0** · partitions generated **1**.

## Reproduce

```bash
python scripts/e2_0_a_folds.py        # lineage, firewall, folds, per-fold basis
python scripts/e2_0_c_feasibility.py  # target-blind applicability feasibility
python scripts/e2_0_b_policies.py     # protocol, access, range, budget, gates, freeze
```

**`PAPER_UTILITY = MEDIUM_HIGH`. Epoch 2 not started. S7.12 remains paused.**
