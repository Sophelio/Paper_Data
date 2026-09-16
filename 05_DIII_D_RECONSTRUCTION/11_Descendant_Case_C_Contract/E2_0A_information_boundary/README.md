# S7.E2.0A — Predictor-side admissibility reconciliation

Freeze **`D3D-SIR-S7.E2.0A-PREDICTOR-SIDE-ADMISSIBILITY-RECONCILIATION-V1`**
Status **`FROZEN_READY_FOR_EPOCH2_SEARCH`** · 35/35 acceptance

```
E2_0_PROTOCOL_V1  = PRESERVED_AS_HISTORICAL_PARENT
E2_0A_PROTOCOL    = AUTHORITATIVE_FOR_EPOCH2_EXECUTION
```

> Protocol reconciliation only. **No search, no fit, no baseline, no target
> read.** Epoch 2 not started. S7.12 remains paused.

---

## The mismatch — confirmed on contract grounds

E2.0 forbade held-out predictor ranges from influencing candidate filtering. That
suits an **inductive-transfer** task. The frozen claim is a **finite-object**
reconstruction claim. Two parts of the lineage show the restriction was stronger
than the contract asks:

1. **S7.6R's sibling rule is application-time.** A selected support with a
   partial-map coordinate *"must satisfy the same rule on each external
   local-calibration block"* — never required to be forecastable from training.
2. **K2's own architecture presumed full-object applicability.** Its coverage
   policy cites the **3 451 atoms certified over all 62 discharges** as its
   feasibility evidence, and reasons that a search restricted to them yields
   supported supports *by construction*.

E2.0 imposed a blinding the parent contract did not ask for.

## Two roles

| | Role A — predictor-side | Role B — target-side |
|---|---|---|
| permitted | **all 62** discharges' non-target predictors | — |
| forbidden | — | **held-out targets**, in search / utility / selection |
| governs | `P-RANGE` applicability (`P_rec`) | relation selection |

```
PREDICTOR_QUALIFIED  ·  TARGET_CROSS_FITTED  ·  RECONSTRUCTION
```

**Guarantee tested:** no discharge's **own target values** influenced the support
used to reconstruct it.

**Not target leakage:** `density` stays sealed to the held-out fold during
discovery; applicability uses only non-target predictors, frozen definitions,
frozen geometry, frozen `τ = 1`.

## τ — unchanged at 1

```
E(c) = max( L − min(c_app), 0, max(c_app) − U ) / (U − L)
```

Distance outside the calibration hull, in units of the hull's width. Calibration
range `[2,6]`, width 4:

| app reaches | 2–6 | 7 | 8 | 10 | 11 |
|---|---|---|---|---|---|
| `E` | 0 | 0.25 | 0.50 | 1.00 | **1.25 → NOT APPLICABLE** |

**τ is not** a regression, regularisation, performance, learned, physical,
confidence or tuning parameter. **τ is** an observational-applicability bound.

**`tau_train = 0.5` is RETIRED** — conceptually, not for odds — with **no
replacement threshold of any kind**.

## Common candidate basis

```
C_E2_FULL_DOMAIN = 3 451 of 10 778     (matches K2 exactly)
C0 51 · C1 18 · C2 1 488 · C3 382 · C5 8 · C6 965 · C7 539
```

**Closure verified, not assumed** — sizes 1/2/5/8/12, all pass; adversarial
control (11 supported + 1 unsupported) → **0.0**, so the check is not vacuous.

`G_rec`, `A_rec`, `P_rec` all unchanged; the 7 327 locally partial atoms are
**not erased**. The basis constrains the Epoch-2 *search frontier* only.

## Access order

**Global pre-search (no target opens):** verify → open all 62 predictors →
instantiate `P-RANGE` → load and verify the 3 451 → **hash the basis**.

**Per fold:** expose `D_train` targets → search → `U_rec` → select →
**write and hash `C_k*`** → freeze estimators/baselines → open `D_test`
**calibration** targets → fit local coefficients → open `D_test` **protected**
targets **last** → score.

## V-RANGE — now an integrity check

Passes **by construction** for supports from the certified basis. **Still
recomputed during execution.** An unexpected failure is a
`PROTOCOL_OR_IMPLEMENTATION_INCONSISTENCY` → **stop for audit**, not ordinary
scientific failure.

## ⚠ What the amendment costs

E2.0 would have tested **two** things on held-out data: whether the target
relationship transfers, **and** whether the support's predictor geometry survives
discharges never consulted. **E2.0A tests only the first.**

**A positive Epoch-2 result is a weaker statement than E2.0 would have
produced.** This is recorded in the claim boundary and belongs in the manuscript,
not only in the audit trail.

The upside: under E2.0 the likeliest failure was the applicability gate. That
route is now closed by construction, so **Epoch 2 will succeed or fail on the
science.**

## Unchanged — nothing compensated elsewhere

Claim type · six outer folds (byte-identical) · `τ = 1` · `K_REC_V2` · `G_rec` ·
`A_rec` · `P_rec` · `U_rec` · `V3` at −0.01 · `V6` · six baselines · 300 k/fold,
1.8 M total · one-seed · `CLEAN_DEMO_PASS` at −0.05 (reporting tier) ·
`EPOCH2_IS_FINAL_QREC_ATTEMPT = true` · forbidden wording **not weakened**.

## `I_q` — no notation change

`I_rec` is a **variable-set** boundary about target ancestry; it never governed
stage-wise availability of an admitted variable's observations — that was always
`P_rec` / `V_rec`. **One-sentence manuscript clarification recommended**, in
`E2_0A_INFORMATION_FLOW.md`.

## Start here

| Document | Purpose |
|---|---|
| `E2_0A_PROTOCOL_RECONCILIATION_FINAL.md` | manuscript-ready section |
| `E2_0A_PROTOCOL_RECONCILIATION_AUDIT_REPORT.md` | full internal audit, 18 sections |
| `E2_0A_INFORMATION_FLOW.md` | the two roles, the flow, the `I_q` audit |
| `RECOMMENDATION_FOR_E2_1.md` | what E2.1 executes and must get right |

## Governance

Parent artifacts modified **0** (S7.K2 29/29, S7.E2.0 22/22 reproduce) · E2.0
**not overwritten** · `K_REC_V2` / `τ` / folds / `U_rec` / `V3` / `V6` /
baselines / budget / stop rule / `CLEAN_DEMO_PASS` all unmodified · claim **not**
strengthened · forbidden wording **not** weakened ·
`TAU_TRAIN_REINTRODUCED_UNDER_ANOTHER_NAME = false` · `target_reads = 0` ·
no search, fit, baseline or support selection.

## Reproduce

```bash
python scripts/e2_0a_a_verify.py    # parents, firewall, basis, closure + control
python scripts/e2_0a_b_protocol.py  # protocol, boundary, basis, changeset, freeze
```

**`READY_FOR_EPOCH2_SEARCH`. Epoch 2 not started. S7.12 remains paused.**
