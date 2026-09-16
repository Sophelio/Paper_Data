# S7.2C — Deterministic primary-target selection rule

Machine-readable: `target_selection_schema.json` · Supersedes clause **C-05**.

**No target is ranked or selected in this run.** The rule is frozen here and
applied in S7.3.

## Why this replaces human choice

V1 froze eligibility but left the choice among eligible candidates to human
review *after* S7.3 computed candidate feasibility. That is precisely the moment
at which relative attractiveness becomes visible — and therefore the moment at
which discretion is most dangerous. Removing it is the point of this correction.

---

## Stage 1 — eligibility (unchanged from V1)

S7.3 applies **every** eligibility criterion independently. Only candidates that
**pass all of them** proceed to ranking.

```
min_admissible_predictors_after_closure       = 10
min_median_robust_relative_variation          = 0.05     <- replaces ordinary CV
min_distinct_values_fraction                  = 0.10
max_identically_zero_development_discharges   = 0
```

Class policy, the twelve criteria, and the development-only firewall are all
unchanged.

## Stage 2 — lexicographic ranking

Applied only to candidates passing stage 1. Each level is consulted only to
break ties left by the level above.

| Level | Key | Direction | Definition |
|---|---|---|---|
| **1** | target-side major flags | **fewer** is better | count of MAJOR provenance or numerical flags attaching to the **target itself** — *not* flags on predictors that `I_rec` later removes |
| **2** | provenance-certified primary predictors surviving `I_rec` | **more** is better | the admissible predictor count after boundary closure |
| **3** | distinct scientific signal families surviving `I_rec` | **more** is better | breadth of the surviving admissible set |
| **4** | margin above the RRV floor | **larger** is better | `RRV_dev − 0.05` |
| **5** | frozen signal order | **lower index** wins | position in `FINAL_SIGNAL_INVENTORY.csv` |

**Level 5 guarantees a unique winner.** The frozen inventory order is fixed,
target-independent, and was established in S7.1 before any of this existed, so
it is a legitimate arbitrary tiebreak rather than a discretionary one.

### Reading of the ordering

Level 1 first because a target carrying provenance or numerical defects
compromises the claim regardless of how well it reconstructs. Level 1 counts
flags on the **target only** — a candidate should not be penalised for
predictors that the information boundary is going to remove anyway.

Levels 2 and 3 prefer a target that leaves a **larger and broader** admissible
set, because a reconstruction study is only interesting if there is something
left to reconstruct from. Breadth (level 3) is separated from count (level 2) so
that forty channels of one family do not outrank a smaller but genuinely
multi-family set.

Level 4 prefers a target with more room above the variation floor, which makes
the trivial baselines a more meaningful test.

### The outcome

> **The top-ranked eligible candidate IS the primary target.**

Not a recommendation, not a shortlist.

---

## Forbidden inputs

None of the following may enter the ranking at any level:

- any reconstruction model or its output;
- any baseline performance;
- correlation between the target and any predictor;
- any external-cohort information;
- any development performance.

Every ranking key is computable from frozen S7.1 metadata, the instantiated
information boundary, and the target's own development-only variation score. **No
model is fitted at any point in the selection.**

## Human review, after S7.3

**May:**
- verify the rule was applied correctly;
- identify a previously unknown scientific or provenance defect in the
  top-ranked candidate.

**May not:**
- choose a lower-ranked target because it seems more interesting;
- choose a lower-ranked target because it appears easier to reconstruct;
- inspect model performance before the target is frozen.

## If the top candidate has a genuine defect

1. **Freeze the defect** in the decision ledger — what it is, how it was found,
   and confirmation that it was not found by looking at performance.
2. Re-apply the **identical rule** to the remaining eligible set.
3. Repeat if necessary.

The rule never changes; only the eligible set shrinks. This is the one legitimate
route to a different target, and it leaves a record of exactly why.
