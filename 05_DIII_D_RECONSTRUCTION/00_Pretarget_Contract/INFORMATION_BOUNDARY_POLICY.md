# S7.2 — Information-boundary policy `I_rec`

The **rule** is frozen here. The **instantiated signal set** is deferred to S7.3,
because it cannot exist until a target does.

```
O_rec = I_rec(O)
```

Applied **before** ontology generation — not as a filter afterwards. A coordinate
that should never have existed must never be constructed, because a candidate
that is generated and then dropped has already influenced the search.

---

## Exclusion rules

For a chosen target `y`, `I_rec` excludes from the explanatory inputs:

| # | Excluded | Basis |
|---|---|---|
| 1 | `y` itself | trivial |
| 2 | every exact duplicate or alias of `y` | identity |
| 3 | every derived quantity whose **definition contains** `y` | definitional ancestry |
| 4 | every quantity with **verified upstream dependence** on `y` | computational ancestry |
| 5 | every quantity whose **ancestry relative to `y` is unresolved**, when the claim requires target independence | fail-closed |
| 6 | every downstream coordinate derived from anything excluded above | closure |

Rule 6 makes the boundary **transitive**. Exclusion propagates through the
coordinate graph: if a primitive is excluded, every constructed coordinate
touching it is excluded, at every depth.

---

## FAIL CLOSED

> **Unresolved ancestry relative to the target ⟹ NOT independence-certified
> ⟹ excluded from the primary information boundary.**

Absence of proof of dependence is **not** proof of independence.

### What this costs, stated in advance

The 15 equilibrium quantities are all `LINEAGE_PARTIAL`. If a target is chosen
for which their ancestry cannot be resolved, **all 15 leave the primary
boundary**. That is a real and possibly large cost, accepted deliberately.

Three escapes exist, in order of preference:

1. **Resolve the lineage** — recover EFIT settings and inputs from the device
   archive. Converts unresolved to resolved and the question disappears.
2. **Report a qualified secondary variant** — a `PROVENANCE_RELAXED` boundary
   admitting the partial-lineage quantities, reported *alongside* the primary
   result and never as the headline.
3. **Accept the exclusion.**

Escape 2 must be **declared before results are seen** and labelled as
qualification, not as the primary claim.

---

## Statistical correlation is never ancestry evidence

Binding, and the most important rule here.

A quantity is excluded because of a **definitional or computational** relation to
the target, established from provenance. It is **never** excluded because it
correlates with the target, and — equally — it is **never admitted** because it
fails to correlate.

This rule exists because an earlier audit in this project demonstrated
concretely that conflating correlation with ancestry produces **both** false
leakage findings **and** false clearances. Correlation may be *reported* as
context. It may not enter a boundary decision.

---

## Sibling / near-duplicate rule

The multichannel families are ECE (40), CER rotation and ion temperature (14),
beams (10), filterscopes (4).

If the target belongs to such a family, neighbouring channels of the **same
family** may make the task trivial spatial interpolation — reconstructing
`ece20` from `ece19` and `ece21` says almost nothing about relational structure.

**Primary boundary: same-family sibling channels are excluded.**

The full-boundary variant (siblings admitted) is then run as a **declared
sensitivity** and reported alongside. Both are frozen before S7.3 so neither can
be chosen after seeing which flatters the result.

S7.3 must record, for the selected target: family membership, the sibling set,
sibling channel count, and which variant is primary.

---

## Target-label usage

Target **timestamps and support** may be used to define where reconstruction can
be scored. Target **values** may not be used for anything below except where the
table permits.

| Operation | Calibration | Validation (dev) | External before S7.10 | Reason |
|---|---|---|---|---|
| fit relation coefficients | **ALLOWED** | no | **ALLOWED** (calibration interval only) | this is what local calibration means |
| compute development utility | no | **ALLOWED** | no | development selection signal |
| final protected scoring | no | no | **ALLOWED at S7.10 only** | the result |
| feature / coordinate construction | **NO** | **NO** | **NO** | would embed the target in its own predictors |
| ontology generation | **NO** | **NO** | **NO** | ontology must be target-independent |
| target-specific predictor normalization outside calibration | **NO** | **NO** | **NO** | leaks protected statistics |
| smoothing-parameter selection using protected intervals | **NO** | **NO** | **NO** | leaks protected structure |
| choosing protected intervals | **NO** | **NO** | **NO** | intervals are fixed by `VALIDATION_PROTOCOL.md` |
| choosing the target | **NO** | dev only, per eligibility policy | **NO** | external must not influence target choice |
| selecting the coordinate support | **NO** | **ALLOWED (dev only)** | **NO** | support is frozen before external |
| determining common support from target VALUES | **NO** | **NO** | **NO** | support is a temporal fact, not a value fact |
| determining scoreable region from target TIMESTAMPS | **ALLOWED** | **ALLOWED** | **ALLOWED** | timestamps carry no target information |

Machine-readable: `leakage_matrix.csv`.

---

## Deferred to S7.3

- the instantiated excluded set, per rule, with evidence per exclusion;
- the surviving admissible predictor set;
- family/sibling determination for the selected target;
- provenance-closure certification, or an explicit `PROVENANCE_RELAXED` variant.

## Deferred to S7.5

- closure over constructed coordinates (rule 6 applied to the generated
  ontology).
