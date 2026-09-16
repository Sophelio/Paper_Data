# Multiplicity control: what the policy did, and what the search then did

Machine-readable: `multiplicity_audit.csv`, `constructor_audit.csv`,
`search_seed_registry.csv`, `constructor_shortlist.csv`

---

## The two questions, kept apart

1. **Was search opportunity allocated fairly?** That is the policy's job, it is
   decided before any value is read, and it is a pass/fail question.
2. **What did the performance-guided expansion do with that opportunity?** That
   is an empirical development-search outcome. It is reported as found and is
   **never** rebalanced.

Conflating them is exactly the failure mode `ADMISSIBLE ≠ PRIORITIZED` exists to
prevent.

## The opportunity ladder, by scientific family

| family | P_hard | atom ancestry | shortlist | **seeds** | explored | retained | lowest-J |
|---|---|---|---|---|---|---|---|
| **ECE** | 0.471 | **0.842** | 0.420 | **0.307** | 0.958 | 0.854 | 1.000 |
| CER | 0.200 | 0.347 | 0.310 | 0.307 | 0.878 | 0.709 | 0.833 |
| NBI | 0.143 | 0.144 | 0.172 | 0.220 | 0.508 | 0.382 | 0.250 |
| gas | 0.057 | 0.097 | 0.173 | 0.220 | 0.552 | 0.376 | 0.500 |
| magnetics | 0.057 | 0.071 | 0.232 | 0.307 | 0.743 | 0.705 | 0.917 |
| filterscope | 0.043 | 0.045 | 0.102 | 0.134 | 0.716 | 0.604 | 0.583 |
| density-aux | 0.029 | 0.041 | 0.181 | 0.228 | 0.860 | 0.831 | 0.917 |

Columns are *participation* shares — a support with two operand families counts
in both — so they do not sum to 1.

### Question 1: opportunity — **balanced**

Read the ECE row left to right across the three columns the policy controls:

```
atom ancestry  0.842   ->   shortlist  0.420   ->   seeds  0.307
```

The round-robin shortlist halves it; one-seed-per-stratum takes it to 0.307,
**below ECE's 0.471 share of the primitive basis itself**. Meanwhile the
sparsely instrumented families are lifted well above their atom shares —
magnetics from 0.071 to 0.307, density-aux from 0.041 to 0.228, gas from 0.097
to 0.220. Opportunity now tracks *how many kinds of relation a family can
participate in*, not how many channels the device happens to carry.

**Initial search opportunity is not proportional to raw atomic multiplicity.**
That is the §22 success criterion, and it is met.

### Question 2: outcome — **ECE still dominates, and that stands**

```
seeds  0.307   ->   explored  0.958   ->   retained  0.854   ->   lowest-J  1.000
```

ECE ancestry appears in **85.4%** of retained-path supports and in **every one**
of the twelve lowest-navigation-score supports. The greedy expansion, offered a
balanced menu at every step, repeatedly chose coordinates with an ECE operand.

This is recorded, not corrected. No family penalty was added to `J_search`, no
coordinate was removed, and no threshold was revisited after the result was
seen. Electron temperature is physically informative about line-averaged
electron density; the search finding so is a substantive result rather than an
artefact of channel count — precisely because the opportunity stage had already
removed the channel-count advantage.

### The other half of the same result

The low-multiplicity families did **not** disappear. Magnetics, at 5.7% of the
primitive basis, appears in **91.7%** of the lowest-J supports; density-aux, at
2.9%, also 91.7%; gas at 50.0%. The single-coordinate leader is a cross-family
ratio, `RATIO(ece16, cerqtit10)`, and by size eight the leading support spans
seven scientific families.

A proportional-to-atom-count search would have spent most of its budget inside
the ECE block. This one did not, and the sparse families earned places in the
leading supports on their own merits.

## By constructor family

| | atoms | share | shortlist | seeds | explored | retained |
|---|---|---|---|---|---|---|
| C0 level | 66 | 0.006 | 66 | 7 | 0.597 | 0.565 |
| C1 derivative | 59 | 0.005 | 59 | 5 | 0.071 | 0.056 |
| C2 product | 2 080 | 0.193 | 96 | 28 | 0.765 | 0.706 |
| C3 ratio | 2 457 | 0.228 | 96 | 28 | 0.902 | 0.778 |
| C5 reciprocal | 39 | 0.004 | 39 | 4 | 0.588 | 0.419 |
| C6 level–rate | 3 776 | 0.350 | 96 | 35 | 0.511 | **0.046** |
| C7 rate/level | 2 301 | 0.213 | 96 | 20 | 0.368 | **0.026** |

The cap does the work it was designed for: C6 carries 35.0% of all admissible
atoms and receives 17.5% of shortlist slots, while C0 carries 0.6% of atoms and
receives 12.0%.

**A finding worth flagging for S7.8.** The two largest families by atom count,
C6 and C7 — the level–rate constructors introduced by the S7.5H hardening —
received substantial seed opportunity (27.6% and 15.7%) and were retained on
almost nothing (4.6% and 2.6%). Their best single coordinates score 0.974 and
0.897 against 0.480 for the best ratio. On this target, under this proxy, the
level–rate grammar contributed the bulk of the admissible universe and almost
none of the retained structure. That is a development-search observation, not a
qualification result, and S7.8 owns what follows from it.

**C4 and C8** remain `DECLARED_IN_ONTOLOGY / ZERO_PRIMARY_ATOMS /
ZERO_SEARCH_OPPORTUNITY`. They have no admissible atoms to offer, inherited from
S7.6R. That is not a search exclusion, and neither was rescued, shifted, or
bounded.

## What was not done

- no coordinate deleted to control multiplicity;
- `P_hard` unaltered, `A_rec` unaltered, strata definitions unaltered;
- no family bonus, penalty, or weight anywhere in `J_search`;
- no global top-K atomic pruning — all 10,778 atoms scored and retained in the
  registry with their scores;
- no threshold, cap, or rule revisited after seeing a score;
- no retrospective rebalancing of the retained paths.
