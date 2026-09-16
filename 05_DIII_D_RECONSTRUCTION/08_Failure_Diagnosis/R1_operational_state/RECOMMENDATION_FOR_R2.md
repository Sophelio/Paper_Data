# S7.R1 — Recommendation

```
STOP_OPERATIONAL_STATE_ROUTE
```

**S7.R2 state-conditioned requalification is NOT authorised.**

---

## Why

R2 authorisation requires **R1-A, R1-B and R1-C all to pass**. Two fail and the
third was never reached:

| Gate | Result | Reason |
|---|---|---|
| R1-A state identification | **FAIL** | no simple, physically interpretable, predictor-defined state separates the catastrophic blocks — neither in the primary 1D `gasa` audit nor in the single permitted multivariate fallback |
| R1-B support coverage | **FAIL** | the strong-gas condition **was** represented in development; development `gasa` covers the external range and development discharge 195650 exceeds both catastrophic discharges |
| R1-C failure alignment | **NOT_REACHED** | no state rule was frozen, so there was nothing to align |

There is no state to condition on. Running R2 would require inventing one, and
the only quantity that separates — the block-relative excursion ratio — is a
property of the validation geometry rather than of the plasma. Promoting it to a
state label would be exactly the error this audit existed to prevent.

## What should happen instead

The reconciliation target is `K_rec`, not `X_rec`:

```
MINIMAL_K_REC_REVISION_REQUIRED
minimal component = P_rec
```

Add an **observational range-support admissibility condition** for total
nonlinear constructors — products and powers — analogous to the existing
denominator guard for partial maps. `V_rec` would carry the consequential
per-block applicability outcome. Nothing else changes.

This belongs to a **future contract epoch**, declared **prospectively before any
new discovery**. It must never be retrofitted onto Epoch 1, whose result stands
as frozen.

## Paper utility

```
PAPER_UTILITY = MEDIUM
```

The audit is clean, short and manuscript-explainable, and it needs no plasma-physics
digression: four gas-valve command channels, one support-coverage comparison, one
counterexample discharge. What it does *not* deliver is the hoped-for arc —
"revise the interpretation, then requalify conditional on state" — because the
evidence refuted the premise of that arc.

What it delivers instead is arguably the more honest SIR demonstration. The
sequence is: pooled relational discovery looked promising; qualification exposed
two failures; provenance localized both to an actuator coordinate; a
predictor-side audit **tested the operational-state explanation and refuted it**;
and the defect was localized instead to a missing admissibility condition in the
contract. That is a complete reconciliation story in six steps, and it shows SIR
rejecting an attractive post-hoc explanation on evidence — which is a stronger
methodological claim than confirming one would have been.

The rating is MEDIUM rather than HIGH only because the demonstration now ends in
a contract lesson rather than a requalified result, so it carries less narrative
payoff. It is not LOW: nothing here is complicated, arbitrary, threshold-tuned or
hand-selected.

**Recommendation for the manuscript:** the existing Epoch-1 result (S7.1–S7.10),
the S7.11 sensitivity analysis and this refutation together already constitute a
complete and publishable SIR demonstration. No further audit stage is needed to
make that story work, and extending the DIII-D example further risks turning a
methods demonstration into a plasma-physics campaign.

## Explicitly not done

No state rule was frozen. No requalification was computed — no state-conditioned
NRMSE, no state-conditioned V3, no revised `Omega_rec`, no new external verdict.
`C_dev_star` is unchanged, `PROD(gasa,gasa)` was not removed, no shot or block was
deleted, no support was promoted, no search was rerun, the two-seed search
remains `NOT_EXECUTED`, and no `K_rec` component was modified in this stage.

S7.R2 not started. S7.12 remains paused.

## One item to carry forward regardless

The `gasa` unit discrepancy (`Torr*L/s` in the provider and S7.1 versus `V` in
S7.3/S7.5H) has **no numerical consequence** — the scale factor is 1.0 under
either label — but the frozen coordinate `PROD(gasa,gasa)` carries
`output_dimension = (V)*(V)`, which may be wrong. Any manuscript text making a
dimensional statement about that coordinate must resolve the discrepancy first.
Logged as `K-R1-02`.
