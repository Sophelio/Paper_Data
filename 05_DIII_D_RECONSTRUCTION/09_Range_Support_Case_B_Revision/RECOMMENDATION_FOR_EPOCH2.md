# S7.K2 — Recommendation

```
READY_FOR_DISCOVERY_EPOCH_2
```

All seven go/no-go gates pass. 47/47 acceptance. `K_REC_V2` frozen with a
`MINIMAL_P_ONLY` revision class.

---

## Go / no-go

| Gate | | |
|---|---|---|
| **K2-A** | concept mathematically coherent | **PASS** |
| **K2-B** | one realization satisfies the frozen desiderata | **PASS** |
| **K2-C** | threshold justified by target-blind stability, not tuning | **PASS** |
| **K2-D** | non-vacuous and non-destructive | **PASS** |
| **K2-E** | full-domain supports available in meaningful numbers | **PASS** |
| **K2-F** | revision remains scientifically narrow | **PASS** — `MINIMAL_P_ONLY` |
| **K2-G** | no target or model outcome used | **PASS** |

## Epoch-2 viability

At `τ = 1`, **3 451 of 10 778** coordinates (32.0 %) retain full-domain range
support across all 62 discharges, spanning **all seven** populated constructor
families:

| C0 | C1 | C2 | C3 | C5 | C6 | C7 |
|---|---|---|---|---|---|---|
| 51 | 18 | 1 488 | 382 | 8 | 965 | 539 |

Because the support predicate is a conjunction over the same cells, **any
combination of full-domain coordinates is automatically a full-domain support**
— roughly **10³³** of size 12. The search space is not meaningfully constrained.

The rule is simultaneously non-vacuous: 68 % of coordinates lose full-domain
support, and 1.4 % of all coordinate-blocks fail.

## The one thing Epoch 2 must accept

**None of the 217 Epoch-1 bootstrap winners is full-domain at `τ ≤ 1`**, and
`C_dev_star` has only 6 of its 12 coordinates individually supported.

This is expected, not alarming: that frontier was searched under a utility with
**no range-support pressure**, so its winners were never selected against this
condition. But it has a hard consequence — **Epoch 2 must search afresh. It
cannot reuse or re-rank the Epoch-1 frontier.**

## Evidence the threshold was not outcome-tuned

The strongest available evidence is that `τ = 1` is **maximally unfavourable to
every Epoch-1 object**:

- 0 of 217 Epoch-1 supports pass;
- `C_dev_star` fails, with 6 of 12 coordinates unsupported;
- a threshold chosen to flatter Epoch 1 would have been `τ ≥ 2`, where 13 of 217
  pass.

Beyond that: the grid was hashed before any count was inspected; the desiderata
were hashed before any candidate was computed; the metric was selected on
constructor-neutrality (p90 spread ratio 4.3 vs 35.1); and the access log
records `target_reads = 0`, `model_error_reads = 0`, `residual_reads = 0`,
`V3_label_reads = 0`.

## What K2 does and does not establish

**Establishes:** the condition is mathematically coherent, target-blind,
dimensionless, constructor-generic, numerically stable, non-vacuous and
non-destructive, and it is expressible in one equation and one sentence.

**Does not establish:** that it improves reconstruction. That is Epoch 2's
question, and K2 cannot answer it. The retrospective sanity check — which
confirms the frozen rule would have flagged both Epoch-1 catastrophic blocks
(scores 1 641 and 1 705 against `τ = 1`, while their normally-reconstructing C
blocks score 0.81) — is **motivating evidence only**, run after the policy was
hashed, and is not prospective validation.

## Paper utility

```
PAPER_UTILITY = HIGH
```

The narrative is now complete and each step is short:

1. pooled relational discovery looked promising;
2. external qualification failed on a mandatory gate;
3. provenance localized the failure to one coordinate under extrapolation;
4. an operational-state explanation was proposed;
5. **predictor-side evidence refuted it** — development covered the actuator range;
6. reconciliation localized the defect to `P_rec`, not to any instantiated object;
7. the contract was minimally hardened with one dimensionless predicate;
8. discovery may resume under the refined contract.

The rule is one equation, one sentence, one threshold with a plain reading. No
constructor-specific exceptions, no special cases, no arbitrary constants, no
plasma-physics digression. This is a clean demonstration of iterative qualified
discovery — a contract learning from its own failure without rewriting its
history.

## What Epoch 2 must do

1. **Search afresh** under `K_REC_V2` — the Epoch-1 frontier is not reusable.
2. Restrict candidate coordinates to those with full-domain range support over
   the intended domain, which yields full-domain supports by construction.
3. Redraw the cohort partition. The Epoch-1 external cohort is **no longer
   sealed** — it has been used. That is a protocol decision for the Epoch-2
   design stage, **not** for K2, and it is the single largest open question.
4. Carry `U_rec` unchanged. It was deliberately **not** relaxed to make Epoch 2
   easier to pass.

## Not done here

No model run, no baseline run, no V3 recomputation, no support selected, no
`Ahat` extension, two-seed still `NOT_EXECUTED`, `Omega_rec` not
outcome-narrowed, `K_REC_V1` not overwritten, zero Epoch-1 files edited.

**Discovery Epoch 2 not started. S7.12 remains paused.**
