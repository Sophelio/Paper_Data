# E2.0A — Recommendation

```
READY_FOR_EPOCH2_SEARCH
```

35/35 acceptance. `E2_0A_PROTOCOL` is authoritative for Epoch-2 execution;
`E2_0_PROTOCOL_V1` is preserved as its historical parent.

---

## What E2.1 executes

**Global pre-search — no target value opens:**

1. verify `O_q` and `K_REC_V2`
2. open non-target predictors for all 62 discharges
3. instantiate `P-RANGE` at `τ = 1`
4. verify and load `C_E2_FULL_DOMAIN` = **3 451** coordinates
5. **hash the common candidate basis**

**Then, independently per outer fold `k`:**

6. expose `D_train⁽ᵏ⁾` targets
7. fresh fold-specific search over `C_E2_FULL_DOMAIN`
8. apply frozen `U_rec`
9. select `C_k*`
10. **write and hash `C_k*` — it can never change after this**
11. freeze estimators and baseline configurations
12. open `D_test⁽ᵏ⁾` **calibration** targets
13. fit local coefficients and baseline calibration
14. open `D_test⁽ᵏ⁾` **protected** targets **last**
15. score

Held-out targets may never cause support reselection, coordinate replacement, a
`τ` change, a fold change, or a search extension.

## Three things E2.1 must get right

**1. Verify the basis before searching, don't assume it.** Recompute
`C_E2_FULL_DOMAIN` from the frozen predicate and check `n = 3451` and the
constructor counts `C0 51 · C1 18 · C2 1488 · C3 382 · C5 8 · C6 965 · C7 539`
against `E2_0A_CANDIDATE_BASIS.json`. A mismatch is a lineage failure, not a
result.

**2. `V-RANGE` is now an integrity check, and must still run.** Supports drawn
only from the certified basis pass by construction. If one does **not**:

> **STOP EXECUTION FOR AUDIT.** This is a protocol or implementation
> inconsistency — the closure property was verified twice — and must **not** be
> recorded as ordinary scientific failure before the lineage is checked.

**3. Emit a per-fold access log.** The ordering above is the protocol. Each fold
must record what was opened at each step, so that step 10 preceding step 12 is
auditable rather than asserted.

## What has not changed, and must not be adjusted

`τ = 1` · the six outer folds · `K_REC_V2` · `G_rec` · `A_rec` · `P_rec` ·
`U_rec` · `V3` at `−0.01` · `V6` · all six baselines · 300 000 per fold and
1 800 000 total · one-seed · `CLEAN_DEMO_PASS` at `Δ₁ ≤ −0.05` as a reporting
tier only · the forbidden claim wording.

**Nothing was relaxed elsewhere to compensate for this amendment**, and nothing
should be.

## The stop rule is untouched

```
EPOCH2_IS_FINAL_QREC_ATTEMPT = true
```

If Epoch 2 fails on the unchanged scientific gates — skill or era robustness —
close `q_rec` as a qualified iterative case study and make `q_desc` the positive
DIII-D headline. Do not revise `K_rec`, add a threshold, change the split, remove
shots, or launch Epoch 3.

Note what has changed about *how* Epoch 2 can fail. Under E2.0 the most likely
failure was the applicability gate. That route is now closed by construction, so
**Epoch 2 will now succeed or fail on the science** — which is the point of the
amendment, and also removes the excuse that a technical gate ended the branch.

## What must be written honestly if Epoch 2 succeeds

Permitted: *target-cross-fitted reconstruction over a predictor-qualified finite
observational object.*

Not permitted, and not weakened by this amendment: virgin external validation ·
untouched cohort · zero-shot transfer · prospective confirmation · universal
DIII-D generalization · unknown-predictor-distribution transfer · fully inductive
held-out predictor generalization · future-discharge applicability.

And the cost must appear alongside the result: because predictor-side
applicability was instantiated over the whole object, Epoch 2 tests whether the
**target relationship** transfers to held-out discharges, not whether the
support's **predictor geometry** would survive discharges never consulted. That
is a real reduction in what a positive result means, and it belongs in the text,
not only in the audit trail.

## Manuscript clarification recommended

One sentence, no notation change:

> The information boundary is transition-specific: observations admissible for
> coordinate construction or applicability need not be admissible for relation
> selection. In the reconstruction example, non-target observations across the
> finite scientific object determine range-support applicability, while held-out
> target values remain unavailable to support discovery.

## Recommendation

**`READY_FOR_EPOCH2_SEARCH`.** No further protocol work is needed, and none
should be done — additional protocol iteration before E2.1 would start to look
like tuning the rules until the answer is agreeable.

Epoch 2 not started. S7.12 remains paused.
