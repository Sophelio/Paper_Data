# Equivalence-rule audit

**Date:** 2026-08-27
**Status:** declared on DEVELOPMENT evidence, **before** the preconfirmation
freeze and before any confirmation data were inspected.

---

## The defect found

The plain one-standard-error rule **degenerates on this problem.**

Across the 6 grouped-CV folds of a near-exact fit, the standard error of the
best candidate is ≈ 3×10⁻⁷. The threshold `best + SE` therefore admits only the
single best candidate:

| Contract | equivalent-set size under plain one-SE | selected |
|---|---|---|
| q_accuracy | 1 | C_all |
| q_compact | **1** | **C_all** |
| q_robust | 1 | C_all |

`q_compact` collapsed onto `q_accuracy` **by construction**. The lexicographic
hierarchy (fewer coordinates → fewer terms → better conditioning → stability)
could never engage, because the equivalence set never contained more than one
member. The comparison the benchmark exists to make was unobservable — not
because the science said the representations were equivalent, but because the
rule measured the wrong thing.

**Root cause:** the SE measures *fold-to-fold variability of one candidate*, not
*the resolution at which candidates are scientifically distinguishable*. When the
fit is near-exact, fold variability → 0 and the rule becomes infinitely strict.

## The fix

Tie practical equivalence to the **declared resolution of the scientific object
(E)** rather than to fold noise:

    threshold = best + max( SE(best), practical_equivalence_abs )
    practical_equivalence_abs = 1.0e-3

Justification: σ_z ≈ 9.04, so a reconstruction difference of 10⁻³ is ≈ 1.1×10⁻⁴
of the target's own scale. Two representations differing by less than that are
not scientifically distinguishable given the object, whatever the fold noise
happens to be. This is a statement about the object, which is exactly where the
SIR framework says such a statement belongs.

Under noise the SE grows (0.031 for `q_robust`) and legitimately dominates the
floor — so the floor only acts where fold noise is unrealistically small.

## Is the floor tuned to produce a desired answer?

**No — and this is the check a reviewer should demand.** The sensitivity sweep
over five decades (`tables/equivalence_sensitivity.csv`):

| floor | q_compact | \|equiv\| | q_robust | \|equiv\| |
|---|---|---|---|---|
| 1e-5 | C_all | 1 | C_all | 1 |
| 1e-4 | **C0+Q_pair** | 4 | C_all | 1 |
| 1e-3 *(chosen)* | **C0+Q_pair** | 4 | C_all | 1 |
| 1e-2 | **C0+Q_pair** | 4 | C_all | 1 |
| 1e-1 | **C0+Q_pair** | 4 | C_all | 1 |

The `q_compact` selection is **stable across four decades** (10⁻⁴ … 10⁻¹). The
chosen value sits in the middle of that plateau, not at an edge. Only at 10⁻⁵ —
below the object's own resolution — does it revert to `C_all`.

`q_robust` selects `C_all` at **every** floor, so that result does not depend on
this parameter at all.

## Honest characterisation

This is a **methodological correction made on development evidence**, and it
changed a headline outcome (`q_compact`: C_all → C0+Q_pair). It must be reported
as such. The mitigating facts:

1. No confirmation data had been generated-into-evidence or inspected when the
   change was made; the freeze was written afterwards.
2. The correction was forced by a *structural* defect (a degenerate rule), not by
   dissatisfaction with a result.
3. The resulting selection is insensitive to the new parameter over four
   decades.
4. The prior benchmark had already exposed `Q[ẏ|x], Q[y|x]`, so selecting them
   again is **not** a new discovery and is not claimed as one.

The residual risk a reviewer may still press: the floor was introduced *knowing*
that a compact quotient representation existed. The defence is the sweep — any
floor in [10⁻⁴, 10⁻¹] gives the same answer — plus the fact that `q_accuracy` and
`q_robust` were left free to choose, and both chose `C_all`.
