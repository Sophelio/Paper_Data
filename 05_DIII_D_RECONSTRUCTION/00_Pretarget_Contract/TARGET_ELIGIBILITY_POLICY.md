# S7.2 — Target eligibility policy

Machine-readable: `target_eligibility_schema.json`.

**This policy is frozen here and applied in S7.3.** S7.2 produces **no target
ranking and no target selection.** Nothing below has been evaluated against any
signal values.

---

## Class policy

Applied to the frozen S7.1 origin classification (57 / 15 / 14 / 9 / 0).

### Eligible as primary target

| Class | n | Rationale |
|---|---|---|
| `DIRECT_MEASUREMENT` with resolved physical meaning and unit | ≤9 | least processed; cleanest scientific statement |
| `DIAGNOSTIC_RECONSTRUCTION` with resolved physical meaning and unit | ≤57 | genuine plasma state quantities; well documented |

### Normally excluded as primary target

| Class | n | Reason |
|---|---|---|
| `CONTROL_COMMAND_OR_ACTUATION` | 14 | reconstructing an actuator command is a statement about the control system, not the plasma; gas channels are valve command voltages and beam channels are actuator outputs |
| `EQUILIBRIUM_DERIVED` | 15 | all `LINEAGE_PARTIAL`; EFIT ancestry unresolved, so provenance closure against them cannot be certified either way |
| uncalibrated raw digitiser output | 2 | `pcbcoil`, `pcdiamag3` — no physical unit exists; reconstruction error would be uninterpretable |
| derived event labels | 0 | none exist in the archive |

The exclusions are **defaults with stated reasons**, not prohibitions. S7.3 may
overturn one, but only by an argument that does not reference model performance,
and the override must be recorded in the decision ledger.

### A consequence worth stating

Excluding the uncalibrated pair removes **`pcdiamag3`**, one of the historical
eight and the target of the retired dFL export. That is intended. Its physical
identity is formally open after S7.1, so it cannot anchor a clean scientific
claim. The exclusion follows from provenance, and was fixed before any target
was examined.

---

## Eligibility criteria

All twelve must hold. Criteria 1–5 and 11–12 are decidable from frozen S7.1
metadata alone; 6, 9 and 10 require inspection and are **restricted to
development discharges**.

| # | Criterion | Decidable from | Test |
|---|---|---|---|
| 1 | scalar time series | S7.1 metadata | inventory is scalar throughout |
| 2 | available across the frozen object | S7.1 metadata | present in all 62; finite fraction 1.0 |
| 3 | physically interpretable | units registry | a scientific description exists |
| 4 | resolved physical unit | units registry | not `uncalibrated`, not null |
| 5 | calibrated diagnostic or state quantity | origin classification | in an eligible class |
| 6 | plausible residual explanatory information after boundary closure | **development only** | ≥ a predeclared minimum of admissible predictors survive `I_rec` |
| 7 | no event taxonomy required | task definition | continuous quantity |
| 8 | no specialist regime classification required | task definition | no regime label needed to interpret |
| 9 | no obvious algebraic duplicate among admitted predictors | provenance + **development only** | no admitted predictor is a definitional restatement |
| 10 | meaningful temporal variation | **development only** | predeclared variation floor, below |
| 11 | usable in both processing eras | S7.1 metadata | present and finite in all 35 and all 27 |
| 12 | no dependence on an unresolved label-generation pipeline | provenance | no label pipeline upstream |

### Predeclared thresholds

Fixed now, before any candidate is examined, so they cannot be tuned:

```
min_admissible_predictors_after_closure     = 10
min_coefficient_of_variation_development    = 0.05
min_distinct_values_fraction                = 0.10
max_identically_zero_development_discharges = 0
```

The variation floor exists to exclude a quantity that is near-constant on
development discharges, where any reconstruction claim would be defeated by the
constant baseline by construction. It is a **feasibility** screen, not a
performance screen: it is evaluated on the target alone, with **no model of any
kind fitted**, and it may not be relaxed after S7.3 begins.

`max_identically_zero_development_discharges = 0` reflects the S7.1 finding that
84 identically-zero pairs exist, all beam channels that never fired.

---

## Firewall

- Criteria 6, 9, 10 use **development discharges only** (20 shots).
- **External discharges are sealed.** No external target value may be inspected
  for eligibility, ranking, or any other purpose before S7.10.
- Eligibility is assessed **per candidate independently**. No candidate is
  compared to another on any quantity related to reconstructability.
- **No model is fitted at S7.3 for eligibility purposes.** Eligibility is about
  the target and the boundary, never about how well anything predicts it.

## Multichannel families

If a candidate belongs to a multichannel family — ECE (40), CER (14), beams
(10), filterscopes (4) — the sibling rule in `INFORMATION_BOUNDARY_POLICY.md`
applies. A target whose siblings make the task trivial interpolation is not
thereby ineligible, but the primary boundary must exclude the siblings, and the
full-boundary variant becomes a reported sensitivity rather than the headline
result.

## Output of S7.3

An **eligible set**, with a recorded pass/fail against each criterion and the
evidence used. Selection of the primary target from that set requires the
recorded rule plus human review. **S7.2 produces no ranking.**
