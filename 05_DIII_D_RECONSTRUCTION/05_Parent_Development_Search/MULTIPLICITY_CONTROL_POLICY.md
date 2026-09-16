# Multiplicity control: how search opportunity was to be allocated

Machine-readable: `SEARCH_POLICY_PREVALUE.json`, `search_strata.csv`,
`atom_stratum_assignment.csv`, `multiplicity_opportunity_audit.csv`

**This policy is complete, frozen and hashed.** It is specified entirely from
metadata and does not depend on the budget block. What the block prevented is
its *execution*, not its definition.

---

## The problem, restated

S7.5H could only modestly compress repeated-channel instrumentation: the ECE
share of `P_hard` fell from 51.3% to 47.1%. S7.6R then found the effect
*amplified* in the atomic universe, because pairwise constructors turn channel
multiplicity into quadratic coordinate multiplicity, and because ECE channels
are strictly positive and smooth and therefore survive the level-denominator
gate where fluctuating diagnostics do not.

```
ECE share of P_hard                              47.1%
ECE ancestry share of admissible atoms           84.2%
ECE share of surviving level denominators        33 of 39
```

**This is not an admissibility defect.** No ECE coordinate was deleted, `P_hard`
was not altered, and no constructor family was touched. The thing to prevent is
narrower and precise:

```
atom count  ->  automatic search priority
```

## The mechanism: stratify opportunity, not admissibility

Search opportunity is allocated by **stratum**, never by atom count. A stratum
is a pair:

```
search_stratum(c) = ( constructor_family , scientific_family_signature )
```

Every one of the 10,778 admissible atoms belongs to **exactly one** stratum. A
mixed-family atom is not double-counted; it belongs to its ordered or unordered
pair signature, not to each of its ancestor families separately.

| constructor | signature | role semantics |
|---|---|---|
| C0, C1, C5 | `(family_i)` | unary |
| C2 | `{family_i, family_j}` | **unordered** — the product is symmetric |
| C3 | `(numerator \| denominator)` | ordered |
| C6 | `(level \| rate)` | ordered |
| C7 | `(rate \| denominator level)` | ordered |

C4 and C8 have no admissible atoms and therefore no active strata. That is
`DECLARED_IN_ONTOLOGY / ZERO_PRIMARY_ATOMS / ZERO_SEARCH_OPPORTUNITY` — an
inherited admissibility outcome, **not** a search exclusion.

### 127 active strata

| constructor | atoms | strata | shortlist | seeds |
|---|---|---|---|---|
| C0 | 66 | 7 | 66 (all) | 14 |
| C1 | 59 | 5 | 59 (all) | 10 |
| C2 | 2 080 | 28 | 96 | 56 |
| C3 | 2 457 | 28 | 96 | 55 |
| C5 | 39 | 4 | 39 (all) | 7 |
| C6 | 3 776 | 35 | 96 | 70 |
| C7 | 2 301 | 20 | 96 | 40 |
| **total** | **10 778** | **127** | **548** | **252** |

## Three devices, each doing a distinct job

**1. Within-stratum ranking, never a global top-K.** Atoms are ranked by
`J_search` *inside* their own stratum. A single global ranking followed by
"take the first K" would hand the 3,776-atom C6 family and the 33-channel ECE
group exactly the proportional advantage the policy exists to remove.

**2. Constructor-balanced round-robin shortlist.** Each constructor gets a fixed
expansion allowance of at most 96 atoms, filled by round-robin over its strata:
round 1 takes the best atom of every stratum, round 2 the second-best, and so
on. Consequences: C0, C1 and C5 are retained entirely; the three large pairwise
families each get 96 rather than 2,080–3,776; and every stratum is represented
before any stratum gets a second candidate.

> **96 is a search budget, not a scientific threshold.** It carries no claim
> that rank 97 is scientifically inferior. An atom not shortlisted is
> `ADMISSIBLE_NOT_IN_EXPANSION_SHORTLIST` — never `INADMISSIBLE`. Changing it
> after target outcomes are seen is forbidden.

The §13 sufficiency gate — 96 must give at least one slot to every nonempty
stratum of every constructor — **passes**: the largest per-constructor stratum
count is 35 (C6).

**3. Up to two seeds per stratum, and stratum-balanced proposals at every growth
step.** Each stratum starts up to two independent greedy paths, and at every
growth step every stratum represented in the shortlist proposes exactly one
atom. The *opportunity set* is balanced; the *choice among proposals* is
performance-guided by `J_search` alone.

## What it would have achieved, measured from metadata

| family | primitives | atom ancestry | projected seed share | amplification removed |
|---|---|---|---|---|
| **ECE** | 33 | **0.842** | **0.310** | **−0.532** |
| CER | 14 | 0.347 | 0.310 | −0.037 |
| NBI | 10 | 0.144 | 0.222 | +0.078 |
| gas | 4 | 0.097 | 0.222 | +0.125 |
| magnetics | 4 | 0.071 | 0.310 | +0.238 |
| filterscope | 3 | 0.045 | 0.135 | +0.090 |
| density-aux | 2 | 0.041 | 0.222 | +0.181 |

(Shares sum above 1: a two-operand stratum touches two families.)

ECE's share of *initial search opportunity* falls from 84.2% of atomic ancestry
to 31.0% of projected seeds — a 53-point reduction — while the sparsely
instrumented families are lifted to a floor set by how many relation types they
can participate in, not by how many channels the device happens to carry.

**Initial search opportunity is not proportional to raw atomic multiplicity.**
That is the criterion §22 sets for success, and the policy meets it before a
single value is read.

## What the policy deliberately does *not* do

- It does **not** require the eventual discovered representation to contain
  balanced scientific families. If ECE dominates the retained paths after
  equalized opportunity, because it genuinely produces better development
  reconstruction, that is a legitimate development-search outcome and is to be
  reported, not rebalanced away.
- It does **not** add family bonuses, parsimony terms, conditioning terms, or
  baseline skill to `J_search`. The navigation score is one number: mean
  development NRMSE. Balance lives in the *opportunity set*, never in the score.
- It does **not** convert an unsearched admissible region into a negative
  finding.

```
ADMISSIBLE != PRIORITIZED
NOT SEARCHED != INADMISSIBLE
SEARCH PRIORITY != SCIENTIFIC VALIDATION
```
