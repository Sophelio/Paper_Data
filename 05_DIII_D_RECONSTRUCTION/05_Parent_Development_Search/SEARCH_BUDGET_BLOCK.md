# The search-budget block, and the decision it hands you

Machine-readable: `search_budget_block.json`,
`manifests/SEARCH_BUDGET_PREFLIGHT.json`

---

## What happened

Section 16 requires the deterministic policy's projected candidate support
evaluations to be computed **from metadata only, before any target value is
opened**, and requires an unconditional STOP if that projection exceeds
`MAX_SUPPORT_EVALUATIONS = 300,000`.

The frozen policy of sections 12–15 projects:

```
atomic scoring                                                10,778
main lane      252 seeds x 11 growth steps x 127 proposals =  352,044
raw-only lane   14 seeds x 11 growth steps x   7 proposals =    1,078
                                                             --------
maximum projected support evaluations                        363,900
strict lower bound                                           346,484
MAX_SUPPORT_EVALUATIONS                                      300,000
```

**Overrun: 63,900 at the maximum, 46,484 at the strict lower bound.**

The stage therefore stopped. **No density value was opened. No archive was
opened. No atom was scored.**

## This is not an artifact of a loose bound

The strict lower bound assumes the most favourable stratum exhaustion the policy
permits: that at proposal time for size `m`, every one of the `m−1` atoms
already in the support has exhausted a *distinct* stratum, removing its
proposal. That is the best case, and it still overruns by 46,484.

**No execution of this policy can come in under 300,000.** The block does not
depend on which reading of "maximum projected" is taken.

## Where the number comes from

The 127 proposals per growth step is the binding term, and it is
metadata-determined:

| constructor | atoms | strata | shortlist | seeds |
|---|---|---|---|---|
| C0 | 66 | 7 | 66 | 14 |
| C1 | 59 | 5 | 59 | 10 |
| C2 | 2 080 | 28 | 96 | 56 |
| C3 | 2 457 | 28 | 96 | 55 |
| C5 | 39 | 4 | 39 | 7 |
| C6 | 3 776 | 35 | 96 | 70 |
| C7 | 2 301 | 20 | 96 | 40 |
| **total** | **10 778** | **127** | **548** | **252** |

Round 1 of the section-12 round-robin gives **every** stratum a shortlist slot,
so all 127 strata are represented and all 127 propose at every growth step.

## What was *not* done

- the policy was **not** truncated;
- the policy was **not** changed to fit the budget;
- no seed count, cap, stratum, or support bound was adjusted;
- no admissible coordinate was pruned;
- no density value was opened;
- no atom was scored.

Section 16 says *"Do NOT truncate silently. Do NOT change the policy after
target scoring."* Changing the policy *before* scoring to make the number fit
would satisfy the letter and defeat the purpose: the budget exists to force this
decision into the open, prospectively, in front of a human.

---

## The remedies, computed but not chosen

| option | lever | max projected | fits 300 000 |
|---|---|---|---|
| **`SEEDS_PER_STRATUM = 1`** | §14 seed rule | **188,736** | **yes** |
| `SEEDS_PER_STRATUM = 2` (current) | — | 363,900 | no |
| **raise `MAX_SUPPORT_EVALUATIONS` ≥ 363,900** | §16 allowance | 363,900 | n/a — redefines the gate |

**`SEEDS_PER_STRATUM = 1`** keeps every stratum's starting path — coverage is
untouched — but a stratum whose single best atom leads into a poor basin gets no
second independent start. It changes search semantics.

**Raising the allowance** changes no search semantics at all; it is purely a
larger computational budget. At roughly 364,000 local OLS fits of ≤ 12
predictors over 60 discharge-blocks, the run is well within tractable range.

Both must be **re-frozen prospectively**, before any density value is opened,
with a new `SEARCH_POLICY_PREVALUE` hash recorded. Adjusting either after target
outcomes are seen is forbidden by §§13 and 16 and would make the stage
`SEARCH_POLICY_CONTAMINATED`.

## Things that look like levers and are not

| candidate | why it does not help |
|---|---|
| lower the 96-atom cap | proposals per step equal the number of **strata** in the shortlist, not the number of atoms. Any cap ≥ 35 (the largest per-constructor stratum count) yields the same 127. A cap below a constructor's stratum count trips the §13 STOP instead. |
| reduce the support bound below 12 | forbidden by §0; `B_rec` is frozen |
| count deduplicated supports instead | §18 dedup governs the **registry**, not the number of proposals. And which supports coincide across paths depends on target-dependent greedy choices, so a dedup-based projection is not computable from metadata — it cannot certify the budget *before* target access, which is what §16 requires. |
| prune strata, atoms, or families | would delete admissible coordinates to fit a computational allowance, inverting `ADMISSIBLE ≠ PRIORITIZED` and contradicting §5's explicit prohibition |

---

## What is already complete and does not need redoing

Everything metadata-only in this stage is finished and hashed:

- all 11 parent freezes verified, 0 drift;
- `S_pers` and `B1A_AR1` frozen (neither run);
- all 10,778 atoms assigned to exactly one of 127 search strata;
- the complete §§5–15 policy written and hashed;
- the §13 cap-sufficiency gate **passed** (96 ≥ 35);
- the opportunity-side multiplicity audit computed — and it shows the policy
  works: ECE would fall from **84.2%** of atomic ancestry to **31.0%** of
  projected seed opportunity.

A re-run needs only the budget decision. Stage A's artifacts carry forward
unchanged; stage B re-freezes with the amended constant.
