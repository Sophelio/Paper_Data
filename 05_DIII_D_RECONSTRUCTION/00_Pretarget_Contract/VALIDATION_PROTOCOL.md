# S7.2 — Validation protocol

Machine-readable: `validation_windows.json` ·
Audit: `manifests/validation_feasibility_audit.csv`

## The old protocol is retired

The previous final-20%-only design produced a nearly constant terminal target
interval and therefore did not discriminate: a constant predictor scored 0.0685
against 0.1137 for the relational model, because `var(eval)/var(calib) = 0.0032`.
The protocol, not the model, made the test uninformative.

## The frozen geometry

For normalised discharge time `tau` in `[0,1]` over each discharge's common
support:

| Block | Calibration | Protected |
|---|---|---|
| **A** | `[0.00, 0.40)` | `[0.40, 0.50)` |
| **B** | `[0.00, 0.60)` | `[0.60, 0.70)` |
| **C** | `[0.00, 0.80)` | `[0.80, 0.90)` |

**Three target-blind evaluation blocks per discharge.** Rolling origin,
expanding calibration, disjoint protected blocks.

### Why this design

- protected blocks are **distributed through the trajectory**, not concentrated
  at the terminus;
- **no block was chosen because target behaviour looked interesting** — the
  fractions were fixed before any target exists;
- later blocks have **increasing calibration support**, so calibration adequacy
  can be examined as a covariate;
- **persistence has a clean definition** — the last calibration sample before
  each protected block;
- the design is easy to state and hard to argue with;
- the final `[0.90, 1.00]` is deliberately **left unscored**, avoiding the
  end-of-discharge behaviour that made the retired protocol degenerate.

### It is still reconstruction, not forecasting

Predictors are observed **contemporaneously** during the protected block. The
expanding-calibration geometry resembles a forecasting design but nothing is
predicted forward: only the *target* is withheld, never the predictors. Stated
here because the shape invites the wrong reading.

---

## Feasibility — audited and FROZEN

The analysis grid depends on which families a target admits
(`NUMERICAL_RESOLUTION_POLICY.md`), so feasibility was audited at **every native
cadence in the object** — 62 discharges × 3 blocks = 186 checks per cadence.

Predeclared minima, fixed before the audit:

```
min_protected_samples    = 10
min_calibration_samples  = 30
```

| Grid Δt | Feasible | min protected | min calibration |
|---|---|---|---|
| 0.02 ms | 186/186 | 18750 | 75000 |
| 0.10 ms | 186/186 | 3750 | 15000 |
| 0.20 ms | 186/186 | 1875 | 7500 |
| 1.00 ms | 186/186 | 375 | 1500 |
| 2.00 ms | 186/186 | 187 | 750 |
| 10.00 ms | 186/186 | 37 | 150 |
| **20.00 ms** | **186/186** | **18** | **75** |

**`FEASIBLE_AT_ALL_CANDIDATE_CADENCES`.** The 20 ms case is the worst — forced
whenever an equilibrium quantity is admitted — and still clears both minima on
every discharge and every block. The geometry is therefore frozen as specified;
no alternative was needed.

The audit used **only** common-window durations from the frozen S7.1 shot
inventory. **No signal value and no target value was read.** The archives were
not opened.

---

## Scoring

- Metrics computed **per protected block**, then aggregated within discharge.
- **Discharge is the independent inferential unit** — never the time sample.
- Common support: cross-representation comparisons use **identical scored
  samples** (gate V7).
- Results reported **separately for the two processing eras** (gate V6).

## Development use

The same three blocks are used on development discharges to compute development
utility. Development validation blocks are the selection signal; external
protected blocks are the result and are untouched until S7.10.

## Deferred

- **S7.9:** instantiated sample indices per discharge and block, once the grid
  cadence is fixed by the admitted set.
- **S7.10:** external protected scoring.
