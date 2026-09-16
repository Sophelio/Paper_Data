# S7.2 — Search-bound policy `B_rec`

No ontology is generated here. This fixes the complexity regime S7.5–S7.7 must
work inside, so that the search space cannot be widened after seeing which
candidates would help.

## Governing intent

The primary ontology stays **low-order and interpretable**. The scientific claim
is about relational *structure*, so a representation that cannot be stated in
words cannot support it — however well it fits.

---

## Constructor bounds — FROZEN

| Allowed in the primary search | |
|---|---|
| primitive coordinates | levels of admitted signals |
| first temporal derivative | at most first order |
| pairwise trajectory-relational derivatives | ratios of rates |
| pairwise products | where semantic and dimensional rules permit |
| pairwise ratios | where denominator conditioning permits |

| Excluded from the primary search | Reason |
|---|---|
| recursive relational depth > 1 | interpretability collapses; combinatorics explode |
| triple and higher products | same |
| second and higher temporal derivatives | source cadence cannot support them; presumed inadmissible under D4 |
| arbitrary transcendental library | no scientific motivation; a free function library turns discovery into curve-fitting |

**Depth = 1** means a relational coordinate may be built from primitives and
their first derivatives, but not from other relational coordinates.

Exclusions are **defaults with reasons**. Any promotion requires explicit human
review recorded in the decision ledger, and **may not be justified by
performance**.

---

## Representation size — FROZEN

```
support size searched over 1 ... 12 scientific coordinates
```

### Justified before any target exists

- **Lower bound 1.** A one-coordinate representation must be reachable, or the
  parsimony criterion cannot express "almost nothing was needed".
- **Upper bound 12.** Set by *sample economy under the worst admissible grid*.
  The binding case is a 20 ms analysis grid — forced whenever an equilibrium
  quantity is admitted — where the smallest calibration interval across all 62
  discharges holds **75 samples** (audited in `validation_windows.json`). At 12
  coordinates that is ~6 calibration samples per fitted coefficient, which is
  already thin for a stable fit; beyond that, coefficient estimates on the
  narrowest calibration interval stop being meaningful.
- Time samples within a discharge are strongly autocorrelated, so the effective
  sample size is well below 75. The bound is therefore **generous**, not tight.
- 12 also keeps the representation humanly readable, which criterion G
  (semantic admissibility) requires.

### The REL10 coincidence, recorded explicitly

The retired model was named REL10. **10 was not inherited, and 12 is not 10.**
The bound above derives from calibration-sample economy on the coarsest
admissible grid, computed from frozen S7.1 temporal metadata with no reference
to any prior result. The coincidence is recorded here so a reviewer can check
that the number was not reverse-engineered.

---

## Candidate-count bound

The generated candidate set is bounded by the constructor rules plus
admissibility, not by a hand-set cap. If the admissible set is large, S7.7 uses
the frozen prioritisation from `KNOWLEDGE_POLICY.md` and **reports the explored
frontier explicitly**.

> Any bound on coverage — top-N, sampling, early stopping — must be **declared
> and logged**. Silent truncation reads as "everything was covered" when it was
> not.

`NOT SEARCHED != INADMISSIBLE`.

---

## Estimator complexity

Deliberately capped so that utility is attributable to the **representation**
rather than to estimator sophistication. See `RELATION_AND_TRANSFER_POLICY.md`.

## Deferred

- **S7.5:** instantiated constructor set; generated candidate count.
- **S7.6:** admissible candidate count after `P_rec`.
- **S7.7:** explored frontier; searched/unsearched boundary; selected support
  size within 1–12.
