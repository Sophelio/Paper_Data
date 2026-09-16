# E2.0A — Transition-specific information boundaries

Machine-readable: `E2_0A_INFORMATION_BOUNDARY.json`.

---

## The principle

```
PREDICTOR_QUALIFIED  ·  TARGET_CROSS_FITTED  ·  RECONSTRUCTION
```

The information boundary is **transition-specific**. It need not hide the same
variables — or the same observations — from every arrow in the discovery chain.

## Two roles, kept apart

### Role A — predictor-side admissibility / applicability

All admissible **non-target** predictor observations in the frozen 62-discharge
object may instantiate `P-RANGE-SUPPORT`.

**Why this is admissible:** the intended domain `Ω_rec` *is* the frozen
62-discharge object. Asking whether a coordinate is observationally applicable
over that domain is a question about the domain, answerable from the domain's
predictor side. It is not a peek at an unseen one.

Target-blind · error-blind · performance-blind. Governs `P_rec`.

### Role B — target-side relational discovery

Within outer fold *k*, held-out **target** values may not influence search,
utility, support selection, estimator selection, or any relation-selection
decision. Only `D_train⁽ᵏ⁾` targets may.

**The epistemic guarantee actually tested:**

> No discharge's **own target values** influenced the support used to
> reconstruct it.

## The flow

```
O_q
 │  all admissible predictor values (62 discharges)
 ▼
P-RANGE applicability  (τ = 1)
 │
 ▼
C_E2_FULL_DOMAIN   (3 451 coordinates)
 │
 │  + D_train⁽ᵏ⁾ TARGET values
 ▼
fold-k exploration  →  U_rec  →  support selection
 │
 ▼
HASH(C_k*)          ←── the support can never change after this
 │
 │  + held-out CALIBRATION targets
 ▼
local coefficient estimation
 │
 │  + held-out PROTECTED targets  ←── LAST
 ▼
qualification
```

## Why this is not target leakage

The target — `density` — remains unavailable to the held-out fold throughout
support discovery. The applicability calculation uses only non-target predictor
values, frozen coordinate definitions, frozen block geometry, and the frozen
`τ = 1`.

| | |
|---|---|
| **predictor-side domain knowledge** | admissible under this finite-object claim |
| **target-side discovery information** | remains cross-fitted |

## Contract-internal grounds — not convenience

Two independent pieces of the frozen lineage already say this:

**1. The sibling rule is an application-time predicate.** S7.6R's
`PARTIAL_MAP_ADMISSIBILITY.md` states that a finally selected support containing a
partial-map coordinate *"must satisfy the **same** rule on each external
local-calibration block"*. Denominator admissibility was **never** required to be
forecastable from development data alone — it is evaluated where the relation is
applied. `P-RANGE` is its sibling under the same partial-map semantics and is
correctly treated the same way.

**2. K2's own architecture presumed it.** `K_REC_V2`'s `coverage_policy` records
`FULL_DOMAIN_RANGE_SUPPORT` as *"feasible target-blindly"*, with its evidence
being the **3 451 full-domain atoms computed over all 62 discharges**, and its
`A_rec_architecture_decision` reasons that *"a search restricted to full-domain
coordinates yields full-domain supports by construction."*

E2.0's predictor-blinding therefore contradicted the parent contract it was
implementing. The mismatch is real.

## What this does *not* buy — recorded, not hidden

Forbidden: unknown-predictor-distribution transfer · fully inductive held-out
predictor generalization · future-discharge applicability · untouched external
validation.

Permitted description: *target-cross-fitted reconstruction over a
predictor-qualified finite observational object.*

> **The epistemic cost.** E2.0's stricter rule would have tested **two** things on
> held-out data: whether the target relationship transfers, **and** whether the
> support's predictor geometry survives discharges whose ranges were never
> consulted. E2.0A tests only the first — the second is now true by construction.
> A positive Epoch-2 result is therefore a **weaker** statement than E2.0 would
> have produced. The claim boundary must say so, and does.

## Does `I_q` already permit this?

**Yes. No notation revision is required.**

`I_rec` is defined as `O_rec = I_rec(O)`: a **variable-set** boundary whose six
exclusion rules are all about **ancestry relative to the target** — the target
itself, aliases, definitional descendants, verified upstream dependence,
unresolved ancestry (fail-closed), and transitive closure.

`I_rec` never governed *which observations of an admitted variable* are available
*at which stage*. That is a different concept, and in Epoch 1 it already lived in
`P_rec` (calibration-only preprocessing) and `V_rec` (block-local protection,
external sealing). The arrangement here is expressible under the existing
components without redefining anything.

### Recommended manuscript clarification

One sentence, because readers will otherwise conflate `I_q` (which variables may
enter) with stage-wise observation availability (`P_q` / `V_q`):

> The information boundary is transition-specific: observations admissible for
> coordinate construction or applicability need not be admissible for relation
> selection. In the reconstruction example, non-target observations across the
> finite scientific object determine range-support applicability, while held-out
> target values remain unavailable to support discovery.

This is a clarification, not a redefinition. No canonical chain or notation
changes.
