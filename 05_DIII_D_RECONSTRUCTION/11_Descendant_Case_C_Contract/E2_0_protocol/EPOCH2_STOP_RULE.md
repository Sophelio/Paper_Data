# Epoch 2 — stop rule

```
EPOCH2_IS_FINAL_QREC_ATTEMPT = true
```

Machine-readable: `EPOCH2_PROTOCOL.json → stop_rule`.

---

## The rule

Discovery Epoch 2 is the **final `q_rec` discovery epoch authorised for this
manuscript**. If the fully frozen Epoch-2 protocol fails, the following are all
forbidden:

- ✗ revise `K_rec` again for this paper
- ✗ add another threshold
- ✗ change the split
- ✗ remove shots
- ✗ launch Discovery Epoch 3

Instead:

> Close `q_rec` as a **qualified iterative case study**, and use `q_desc` as the
> positive DIII-D headline result.

## Why this rule exists

The audit trail is only worth something because each stage was frozen before its
outcome was visible. That discipline has already survived one mandatory-gate
failure, one refuted hypothesis, and one contract revision.

A third epoch, launched after seeing a second failure, would be the first stage
in this entire history whose *existence* was conditioned on an outcome. Every
subsequent choice would inherit that contingency, and the trustworthiness the
earlier stages bought would be spent. Two disciplined epochs and an honest stop
is a stronger scientific object than three epochs with a happy ending.

## What counts as failure

Any of:

- **V3 fails** — `Δ₀ > −0.01` or `Δ₁ > −0.01` on the 62 out-of-fold results;
- **`FULL_CROSSFITTED_DOMAIN_RANGE_SUPPORT` fails** — at least one held-out
  block is `RANGE_SUPPORT_NOT_APPLICABLE` under its fold's support;
- **V6 fails** — an era is `MATERIAL_ADVERSE` while the pooled result passes.

Note the second bullet carefully. Prospective target-blind analysis puts the
six-fold applicability gate at roughly **1 in 5** under random support draws
(`manifests/APPLICABILITY_FEASIBILITY.json`). **Failing on applicability counts
as failure.** It does not license loosening `τ`, dropping a block, or re-running
a fold — those are precisely the moves K_REC_V2 exists to forbid.

## What is *not* failure

A `FORMAL_PASS` that misses `CLEAN_DEMO_PASS` is a pass. The scientific gate is
V3 at −0.01, unchanged. The `CLEAN_DEMO_PASS` tier is a reporting standard for
how the result is presented in the manuscript, and it may never be promoted into
a gate or used to retrospectively fail a formal pass.

## What "close q_rec as a qualified iterative case study" means

It is not a null result and should not be written as one. The `q_rec` branch
would then have demonstrated, end to end and with a complete frozen audit trail:

1. relational discovery producing a promising development-side representation;
2. external qualification failing a mandatory gate;
3. failure localized by provenance to a single coordinate under extrapolation;
4. an attractive operational-state explanation **tested and refuted** on
   predictor-side evidence;
5. reconciliation localizing the defect to `P_rec` rather than to any
   instantiated object;
6. one generic, dimensionless, prospectively frozen contract condition added;
7. a fresh cross-fitted epoch under the hardened contract — and its outcome,
   whatever it is.

That is a complete demonstration of iterative qualified discovery. Its value does
not depend on step 7 being positive.

## Authority

This stop rule is frozen at E2.0, **before** Epoch 2 runs and before any Epoch-2
outcome exists. Overriding it later would require an explicit, recorded human
decision that acknowledges it was frozen prospectively — not a quiet
continuation.
