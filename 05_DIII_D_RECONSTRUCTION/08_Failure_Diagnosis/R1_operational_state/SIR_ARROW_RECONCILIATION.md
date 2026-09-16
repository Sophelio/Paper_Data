# S7.R1 — SIR arrow reconciliation

Machine-readable: `SIR_ARROW_RECONCILIATION.json`, `K_REC_CHANGE_AUDIT.json`.

---

## Result

**No instantiated SIR object was invalidated.**

```
earliest_invalidated_stage = NONE_OF_THE_INSTANTIATED_OBJECTS
```

Every object in the chain was constructed **correctly under `K_rec` as
written**. The defect is in `K_rec` itself.

## Arrow by arrow

| Arrow | Instantiated object | Status |
|---|---|---|
| `O → O_q` | `O_DIIID_FINAL`, 62 discharges, 95 signals | **VALID** — the actuator information needed to test the hypothesis was already present and admitted |
| `O_q → X_rec` | `X_rec⁽¹⁾`, pooled discharge ensemble | **VALID — NOT INVALIDATED** |
| `X_rec → G_rec` | `G_REC_DENSITY_HARDENED_V2` | **VALID** |
| `G_rec → A_rec` | `A_REC_DENSITY_HARDENED_V2` | **VALID under contract as written** — but the admissibility *condition* is incomplete |
| `A_rec → Ahat_rec` | `AHAT_REC_DENSITY_ONE_SEED_V2` | **VALID** |
| `Ahat_rec → (C*, R*)` | `C_dev_star` + `DEVELOPMENT_RELATION_OLS_V1` | **VALID** |
| `(C*, R*) → Q_rec` | `Q_rec⁽¹⁾`, V3 FAIL / V6 FAIL | **VALID AND INFORMATIVE** — the qualification is what exposed the gap |

## Why `X_rec` is *not* the invalidated object

The motivating hypothesis was that `X_rec⁽¹⁾` pooled two physically meaningful
operational states. **That hypothesis was tested against predictor-side evidence
and refuted.**

The strong-gas condition *is* represented in the development object: development
`gasa` spans −0.019…7.51 against external −0.018…7.98, and development discharge
195650 reaches 7.447 — higher than either catastrophic discharge. An actuator
two-cluster partition places both catastrophic blocks among 75 ordinary blocks,
and external discharge 187018 sits further from development in actuator space
than 187022/B while reconstructing normally.

So the observational record genuinely **is** one operational ensemble with
respect to gas actuation. A state-indexed `X_rec⁽²⁾` would encode a distinction
the evidence does not support.

What development lacks is not a state but a **block alignment**: an actuator
transition inside the protected window following a quiet calibration window.
Maximum development protected/calibration `gasa` ratio is **1.018**; the two
catastrophic blocks are **40.2** and **41.0**. That is a property of the frozen
rolling-origin validation geometry, not of the plasma, and it is not something
`X_rec` is responsible for representing.

## Where the defect actually lives

`A_rec` admitted `PROD(gasa,gasa)` **by rule, not by oversight**.
`DENOMINATOR_ADMISSIBILITY_PRIMARY_V1` guards denominators, and S7.6R states
explicitly that *"C0, C1, C2 and C6 have no denominator and no gate."* A C2
self-product is unguarded **by design**.

The contract therefore contains a genuine gap:

> **Mathematical domain support is not observational range support.** `x²` is
> defined for every finite `x`, yet a calibration-fitted affine relation in `x²`
> becomes numerically unsupported when `x` leaves the calibration region.

This is the same conceptual lesson S7.11 recorded prospectively. S7.R1 localizes
it precisely: it is a `K_rec` incompleteness, not an `X_rec` mis-organization.

## `K_rec` change audit

```
K_REC_REVISION_REQUIRED = true
revision_class          = MINIMAL_K_REC_REVISION_REQUIRED
minimal component       = P_rec
```

| Component | Change |
|---|---|
| **`P_rec`** | **the minimal component.** Add an observational range-support admissibility condition for total nonlinear constructors (products, powers), analogous to the existing denominator guard for partial maps |
| `V_rec` | consequential only — a per-block applicability outcome analogous to `RELATIONAL_REPRESENTATION_NOT_APPLICABLE` would follow from the `P_rec` condition. No independent `V_rec` defect was found; all ten gates behaved exactly as frozen |
| `I_rec`, `B_rec`, `H_rec`, `U_rec`, `Omega_rec`, `q_rec` | **unchanged** |

`I_rec` already admits the actuator variables that would be needed for any
state-conditioned analysis — which is precisely why the state hypothesis could
be tested at all, and why its refutation is credible rather than a limitation of
the information boundary.

**No `K_rec` component was modified in this stage.** The revision is recorded as
belonging to a **future contract epoch**, to be declared prospectively before any
new discovery — never retrofitted onto Epoch 1.

## What this means for SIR

The governing question was:

> *Did qualification expose observational organization that the pooled
> mathematical interpretation failed to represent?*

The answer is **no** — and establishing that took a real test rather than an
assumption. Qualification exposed something different and arguably more useful:
an **incomplete admissibility condition in the contract**. Those are distinct
reconciliation targets, and conflating them would have produced a state label
that was really an artifact of where a validation boundary fell.

Epoch 1 remains intact and frozen. The reconciliation target is `K_rec`, for a
future epoch.
