# `K_rec^pre` V2 — corrected pre-target contract

**Freeze:** `D3D-SIR-S7.2-RECONSTRUCTION-CONTRACT-PRETARGET-V2`
**Supersedes:** `…-V1` (preserved unmodified, 35/35 artifacts verified)
**Machine-readable:** `K_REC_PRE_V2.json`, `metric_and_gate_definitions.json`

> **V2 inherits V1 in full and supersedes only the nine clauses listed below.**
> Every V1 rule not named here remains binding and is not restated.

**No target selected. No signal value inspected. No model fitted.**

---

## Superseded clauses

Machine-readable: `manifests/SUPERSEDED_CLAUSES.csv`.

| ID | What changed | Type |
|---|---|---|
| **C-01** | practical equivalence: `AND` → `max(SE, 0.01)` | FULL |
| **C-02** | ordinary CV → robust relative variation | FULL |
| **C-03** | NRMSE denominator defined exactly | ADDS_DEFINITION |
| **C-04** | rolling-origin protection → block-local, prequential | CLARIFIES |
| **C-05** | target selection → deterministic lexicographic rule | FULL |
| **C-06** | gate V3 aggregate defined exactly | ADDS_DEFINITION |
| **C-07** | gate V6 external counts 35/27 → 24/18 | FULL |
| **C-08** | six open human decisions → all frozen | FULL |
| **C-09** | hash manifest: self-referential files excluded | FULL |

---

## C-01 · Practical equivalence

```
delta_equiv = max(SE_delta, 0.01)

A and B practically equivalent  iff  |RMSE_A - RMSE_B| <= delta_equiv
```

Read as **within one SE OR within the 0.01 floor**.

V1 required *both* conditions, which made the floor inoperative in exactly the
case it was introduced to handle: when `SE` is tiny, the tiny `SE` remains
binding and the floor never relaxes anything. The floor **value** is unchanged.

**`SE_delta`, operationally:** aggregate the three validation blocks within each
development discharge → compute the paired candidate difference per development
discharge → `SE_delta` is the standard error of that paired discharge-level
difference across the **20 development discharges**.

## C-02 · Robust relative variation

Retires `min_coefficient_of_variation_development`. Ordinary `CV = sd/|mean|`
is undefined or explosive for near-zero means and meaningless for sign-changing
trajectories — corrected **prospectively**, before any candidate value has been
seen.

```
RRV_s   = 1.4826 * MAD(y_s) / RMS(y_s)
MAD(y)  = median(|y - median(y)|)
RMS(y)  = sqrt(mean(y^2))
RRV_s   = 0                        if RMS(y_s) == 0
RRV_dev = median_s(RRV_s)          over the 20 development discharges

min_median_robust_relative_variation = 0.05
```

All other eligibility thresholds unchanged.

## C-03 · Primary metric, defined exactly

```
scale_{s,b}  = std(y_calibration_{s,b}, ddof=0)
NRMSE_{s,b}  = RMSE(y_protected_{s,b}, yhat_protected_{s,b}) / scale_{s,b}
```

- `ddof = 0`, recorded explicitly.
- The scale uses **calibration target values only**; no protected statistic
  enters it.
- **`scale == 0` ⟹ `INVALID_FOR_NORMALIZED_SCORING`** for that block. **No
  epsilon** is added — a degenerate block is declared invalid, not rescued by a
  constant that would have to be chosen with outcomes in view.
- Raw RMSE in physical units is also reported.
- S7.3 must report whether any zero-scale calibration block exists; the primary
  target must have valid normalized scoring across all required development
  blocks.

This makes the 0.01 floor exactly **1% of the calibration target
standard-deviation scale**.

## C-04 · Block-local protection

Time fractions are **unchanged**:

| Block | Calibration | Evaluation |
|---|---|---|
| A | `[0.00, 0.40)` | `[0.40, 0.50)` |
| B | `[0.00, 0.60)` | `[0.60, 0.70)` |
| C | `[0.00, 0.80)` | `[0.80, 0.90)` |

V1's "protected" wording could be read as permanently sealing block A's
evaluation values — which contradicts block B calibrating on `[0, 0.60)`, a
window that contains them. The semantics are **sequential / prequential**:

```
STEP A   fit on [0,0.40)  ->  score A on [0.40,0.50)  ->  freeze the A score
         only after A scoring is irrevocably complete may those target values
         become ordinary historical calibration observations
STEP B   fit on [0,0.60)  ->  score B on [0.60,0.70)  ->  freeze the B score
STEP C   fit on [0,0.80)  ->  score C on [0.80,0.90)
```

A target value may **never** influence its own evaluation block's fit, any
earlier evaluation block, or any choice that is supposed to be frozen (target,
ontology, support, hyperparameters).

The correct term is **BLOCK-LOCAL PROTECTION**, not permanent global sealing.

**The external cohort remains globally sealed before S7.10.** Block-local
protection governs only within-discharge rolling-origin sequencing; it grants
nothing across the cohort firewall.

## C-05 · Deterministic target selection

See `TARGET_SELECTION_RULE.md` and `target_selection_schema.json`. Eligibility
criteria are unchanged; only the **selection** step among eligible candidates is
superseded.

## C-06 · Gate V3, defined exactly

```
NRMSE_method,s = mean over blocks A,B,C of NRMSE_method,s,b
Delta_j        = mean over EXTERNAL discharges s of (NRMSE_REL,s - NRMSE_Bj,s)

V3 PASS  iff  Delta_0 <= -0.01  AND  Delta_1 <= -0.01
```

The relational representation must improve by at least the practical floor
against **both** B0 (calibration mean) and B1 (persistence).

Confidence intervals are **reported but are not significance thresholds for
V3**. Also reported: median paired difference, wins/ties/losses, 95% paired
discharge-bootstrap CI, block-specific values.

## C-07 · Gate V6, corrected counts

V1 cited 35/27 — those are **parent-object** counts. The gate operates on the
**external cohort**:

| | earlier | later | total |
|---|---|---|---|
| **external cohort (the gate)** | **24** | **18** | **42** |
| parent object (reference only) | 35 | 27 | 62 |

| Outcome | Condition |
|---|---|
| `PASS` | pooled V3 passes and the practical direction is non-adverse in both eras |
| `PASS_WITH_QUALIFICATION` | pooled V3 passes, but one era is practically tied against a trivial baseline; report and narrow the interpretation |
| `FAIL_FOR_FULL_DOMAIN` | pooled V3 passes only because one era dominates while the other is materially worse than B0 or B1 by > 0.01 |

`FAIL_FOR_FULL_DOMAIN` **does not erase the result.** It requires the final
`Omega_rec` claim to be **narrowed** rather than averaged across the processing
discontinuity.

## C-08 · Human decisions frozen

All six V1 open decisions are closed — see `S7_2C_DECISION_LEDGER.md` (H-A
through H-F). Most consequentially: **no EFIT-lineage recovery campaign** and
**no `PROVENANCE_RELAXED` variant**.

## C-09 · Hash-manifest construction

V1's manifest recorded stale hashes for `S7_2_ACCEPTANCE_CHECKS.json` and
`S7_2_FREEZE.json`: both are written *after* the manifest is built, so a file
cannot carry its own hash. V2 excludes self-referential files explicitly and
lists them under `self_referential_excluded`.

---

## Unchanged and still binding

20/42 partition · external firewall · continuous reconstruction · structural
transfer with local calibration · target-history exclusion · sibling-channel
primary exclusion · fail-closed provenance · canonical-unit conversion ·
no-super-resolution · first derivatives only · relational depth 1 · support
size 1–12 · B0/B1/B2/B3 · discharge-level inference · seeding firewall ·
claim-domain limits · the eight admissibility classes · the ten gates V1–V10 ·
the lexicographic utility ordering.

## Component status (unchanged from V1)

`q` FROZEN · `I` PARTIAL · `P` PARTIAL · `B` PARTIAL · `H` FROZEN ·
`U` FROZEN · `V` PARTIAL · `Ω` PARTIAL

## Stage gate

No target selected · no targets ranked · **no signal value inspected** · no
coordinates · no `G_rec` / `A_rec` / `Ahat_rec` · no SIR run · no regression ·
no performance inspected · no external values accessed · S7.3 not started.
