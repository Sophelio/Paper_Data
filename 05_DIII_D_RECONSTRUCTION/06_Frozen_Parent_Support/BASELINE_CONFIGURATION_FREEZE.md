# S7.9 — Baseline configuration freeze

Six comparator families are instantiated and frozen here. **None has been run.**
S7.10 evaluates them externally.

Ordering guarantee: `DEVELOPMENT_REPRESENTATION_LOCK.json` was written and
hashed **before** the first alpha was evaluated. The selected support cannot
change, so no baseline behaviour can feed back into representation selection.

Machine-readable form: `BASELINE_CONFIGURATION_MANIFEST.json` and the six
`BASELINE_*_CONFIG.json` files.

---

## Parent specification audit — parents win

| Family | Parent source | Complete? | S7.9 action |
|---|---|---|---|
| **B0** | S7.2 `BASELINE_PROTOCOL.md` | yes, 0 hyperparameters | carry verbatim |
| **B1** | S7.2 `BASELINE_PROTOCOL.md` | yes, 0 hyperparameters | carry verbatim |
| **B1A_AR1** | S7.7 `PRE_SEARCH_CONTRACT_COMPLETION_V1` | yes, `hyperparameter_selection: NONE` | carry verbatim |
| **B2** | S7.2 `BASELINE_PROTOCOL.md` + `RELATION_AND_TRANSFER_POLICY.md` | **no** — no numeric penalty grid or selection algorithm exists in any parent | complete prospectively (§19) |
| **B3** | S7.2 `BASELINE_PROTOCOL.md` | yes — "library defaults except what determinism requires" | carry verbatim + fix `random_state` |
| **H0_RAW_HARDENED** | S7.5H `hardened_raw_ablation.json` | yes, but its penalty rule is defined by reference to B2 | inherits the B2 completion |

A search across S7.2 and S7.3 artifacts, `PRE_SEARCH_CONTRACT_COMPLETION.json`
and `hardened_raw_ablation.json` found **no stronger parent rule** for the ridge
penalty. §19 therefore applies to B2, and H0 inherits it by reference.

## `RIDGE_ALPHA_SELECTION_V1` — frozen before any alpha was evaluated

```
predictors standardized from the CALIBRATION interval only; sd<=0 -> divisor 1.0
intercept fitted, NOT penalized
grid: 0, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1,
      1, 10, 100, 1e3, 1e4, 1e5, 1e6
alpha = 0  ->  unregularized affine linear regression via lstsq
fit separately per discharge/block on the 20 development discharges,
same A/B/C rolling geometry, frozen NRMSE
aggregate within discharge over blocks, then over discharges
select minimum mean development NRMSE;  tie -> SMALLER alpha
no one-SE enlargement; no preference for stronger regularization
```

B2 and H0 tune **independently** under the same rule. The specification was
written to `BASELINE_SPECIFICATION_COMPLETION_PREVALUE.json` and hashed
(`fd05fcc0…`) before the first alpha was evaluated. This is *implementation
completion of an already-frozen baseline family*, not baseline-family selection.

## The six configurations

### B0 — `B0_CALIBRATION_MEAN_V1` · mandatory (V3)
Predict `mean(y_calibration)` throughout the protected block. No
hyperparameters. No future target use.

### B1 — `B1_PERSISTENCE_V1` · mandatory (V3)
Predict the final target value immediately before the protected block — the
last calibration sample — held constant across it. No hyperparameters. This
remains the mandatory persistence comparator for V3.

### B1A — `B1A_AR1` · diagnostic
Carried verbatim from the frozen parent. Calibration fit
`y_k = a + phi·y_{k-1} + eps_k` by OLS; protected prediction initialised from
the final calibration target value and recursed **without teacher forcing**;
`a` and `phi` frozen across the protected block. Lag order 1, no additional
lags, `hyperparameter_selection: NONE`. Not added to the mandatory V3
thresholds.

### B2 — `B2_RAW_RIDGE` · mandatory (V4)
Ridge with fitted, unpenalized intercept on the **full 78 target-admissible
primitive levels** from `I_rec`. No constructed coordinates. **Explicitly not
shrunk to the 70 hardened basis** — B2 is the full-information raw linear
comparator.

**Selected development alpha: `1`.**

### B3 — `B3_RAW_HIST_GRADIENT_BOOSTING` · mandatory (V4)
`sklearn.ensemble.HistGradientBoostingRegressor` on the same 78 primitives.
sklearn **1.9.0**, 21 constructor parameters. Library defaults throughout, with
exactly one departure required for determinism:

```
HistGradientBoostingRegressor(random_state=2026090502)
```

Every inherited default is recorded in `BASELINE_B3_CONFIG.json`. No
compatibility departure was necessary, so no human review was triggered. B3 was
not tuned, and was not tuned "because relational performance is known".

### H0 — `H0_RAW_HARDENED` · diagnostic ablation, **not** a mandatory gate baseline
Ridge on **exactly the 70 hardened primitive levels** `P_hard`. No constructed
coordinates. Same penalty-selection procedure as B2, independently selected.

**Selected development alpha: `1`.**

The eight primitives in B2 but not in H0 — `ece17`, `ece23`, `ece24`, `ece26`,
`ece32`, `ece34`, `ece40`, `fs04da` — are those removed by the S7.5H redundancy
hardening. This is what makes the later `B2 vs H0` reading (effect of primitive-
space hardening) and `H0 vs relational` reading (effect of relational
construction on the hardened information) possible.

## No comparison claim

The per-alpha development tuning criterion is recorded in
`baseline_b2_alpha_tuning.csv` and `baseline_h0_alpha_tuning.csv` **solely as
the tuning audit**. Nothing in S7.9 interprets those numbers as B2, H0 or B3
being better or worse than the relational representation, or as persistence
skill. Those are S7.10 results and are not available yet.

`S_PERS_V1` is carried unchanged, was not used to select `C_dev_star`, was not
used to reopen any utility rank, and remains required reporting at S7.10.

## Status

All six: **`FROZEN_NOT_RUN`**. External evaluation: S7.10.
