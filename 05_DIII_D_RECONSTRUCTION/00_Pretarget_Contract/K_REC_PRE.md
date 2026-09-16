# `K_rec^pre` — the pre-target reconstruction contract

Machine-readable: `K_REC_PRE.json` · Freeze: `S7_2_FREEZE.json`

```
K_rec = (q, I, P, B, H, U, V, Omega)
```

**No target has been selected.** Components that depend on one cannot be
instantiated, and this document says so rather than pretending otherwise. The
explicit incompleteness is the point: it makes visible exactly which decisions
remain, so none can be made quietly later.

---

## Component status

| Component | Status | Frozen now | Deferred |
|---|---|---|---|
| **q** task class | **FROZEN** | continuous reconstruction; structural transfer with local calibration | target → S7.3 |
| **I** information boundary | **PARTIAL** | exclusion rules, fail-closed, sibling rule, leakage matrix | instantiated set → S7.3; coordinate closure → S7.5 |
| **P** admissibility | **PARTIAL** | 8 invariant classes, unit canonicalisation, resolution rule | target-specific closure → S7.3; instantiation → S7.6 |
| **B** search bounds | **PARTIAL** | depth 1, first derivative, pairwise only, support 1–12 | candidate counts → S7.5/S7.6; frontier → S7.7 |
| **H** knowledge | **FROZEN** | allowed uses, forbidden use, seeding firewall | — |
| **U** utility | **FROZEN** | lexicographic criteria, practical-equivalence rule | computation → S7.9 |
| **V** validation | **PARTIAL** | geometry, baselines, 10 gates, inference plan | gate evaluation → S7.10 |
| **Ω** domain | **PARTIAL** | candidate domain, cohort partition | final domain → S7.10/S7.12 |

---

## q — task class · FROZEN

**Continuous reconstruction** of one observed scalar plasma or state quantity
from other task-admissible **contemporaneous** observations.

**Transfer:** structural transfer with local calibration. Support shared and
frozen; coefficients discharge-specific.

Not: ELM detection · event classification · forecasting · causal inference ·
control · zero-shot coefficient transfer · universal plasma equation discovery.

## I — information boundary · PARTIAL

Six exclusion rules, applied **before** ontology generation and **transitively**
over the coordinate graph: the target; its duplicates and aliases; quantities
whose definition contains it; quantities with verified upstream dependence;
quantities with **unresolved** ancestry (fail-closed); and everything downstream
of any of those.

**Fail-closed.** Unresolved ancestry is not independence.
**Correlation is never ancestry** — neither to exclude nor to admit.
**Sibling rule.** Same-family channels excluded from the primary boundary;
full-boundary variant is a declared sensitivity.

## P — admissibility · PARTIAL

Eight invariant classes: **A** provenance · **B** boundary compliance ·
**C** dimensional · **D** numerical support · **E** denominator/singularity ·
**F** temporal resolution · **G** semantic · **H** leakage.

Evaluated cheapest-first; **A, B, C, F, G decide without touching any data**,
and no check requires protected values.

Unit canonicalisation to SI (eV retained for temperature) precedes every
constructor. Analysis grid **no finer than the coarsest admitted native
cadence**.

## B — search bounds · PARTIAL

Primitives · first temporal derivative · pairwise trajectory-relational
derivatives · pairwise products · pairwise ratios.

Excluded: relational depth > 1 · triple products · second and higher derivatives
· arbitrary transcendental library.

**Support size 1–12**, derived from calibration-sample economy on the worst
admissible grid — not inherited from REL10.

## H — knowledge · FROZEN

Knowledge may admit, reject, type or prioritise. **Knowledge may not count as
validation evidence.**

**Seeding firewall:** q_desc's support, the retired q_rec support, and the dFL
target-conditioned export may **not** seed `q_rec`; dFL features may not serve
as primitives.

## U — utility · FROZEN

Lexicographic: fit quality → generalization/stability → parsimony →
conditioning → support stability.

**Practical equivalence:** one-standard-error rule **and** an absolute floor of
0.01 calibration-normalized RMSE. Both declared before search.

No fabricated measurement-error weights — `E` is not instantiated.

## V — validation · PARTIAL

Three rolling-origin blocks per discharge: calibration `[0,0.4)`/`[0,0.6)`/
`[0,0.8)`, protected `[0.4,0.5)`/`[0.6,0.7)`/`[0.8,0.9)`. Audited feasible at
every native cadence (186/186).

Baselines **B0** calibration mean · **B1** persistence · **B2** raw ridge ·
**B3** `HistGradientBoostingRegressor`.

Ten gates **V1–V10**; nine mandatory (all but V9).

Discharge is the inferential unit; paired discharge bootstrap ≥10,000
replicates.

## Ω — domain · PARTIAL

**Candidate:** the frozen 62-discharge object
`D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1`.

**Partition:** 20 development / 42 external, deterministic and target-blind.
External sealed until S7.10.

**Final domain:** deferred; can only shrink.

---

## Stage gate

No target selected · no targets ranked · no SIR run · no regression · no
coordinates generated · no `G_rec` · no `A_rec` · no `Ahat_rec` · no performance
inspected · **no external signal value inspected** · S7.3 not started.
