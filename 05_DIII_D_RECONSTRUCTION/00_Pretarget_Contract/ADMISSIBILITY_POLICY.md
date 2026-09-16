# S7.2 — Scientific admissibility policy `P_rec`

Target-invariant rules. No target-specific coordinate is generated here.

## Four distinctions that carry the whole contract

```
AVAILABLE     != ADMISSIBLE      presence in O is not permission to use
ADMISSIBLE    != PRIORITIZED     permission is not preference
PRIORITIZED   != VALIDATED       preference is not evidence
NOT SEARCHED  != INADMISSIBLE    a gap in the search is not a scientific claim
```

The fourth matters most for honest reporting. When S7.7 reports the explored
frontier `Ahat_rec` it must distinguish *"this was ruled out"* from *"this was
never reached"*. Only the first is a finding.

---

## The eight admissibility classes

### A. Provenance admissibility
A quantity is provenance-admissible if its origin classification and lineage
status are recorded, and its ancestry relative to the target is either resolved
or explicitly carried as `UNRESOLVED`. **Fail-closed** applies: unresolved
ancestry is not independence.
→ `INFORMATION_BOUNDARY_POLICY.md`

### B. Information-boundary compliance
No coordinate may derive, at any depth, from a quantity excluded by `I_rec`.
Transitive closure over the coordinate graph. Checked at construction.

### C. Dimensional admissibility
Every construction passes the type rules in `UNIT_AND_TYPE_POLICY.md` on
canonicalised units. Sums require identical dimensions; transcendental arguments
must be dimensionless; `UNCALIBRATED_SIGNAL` propagates.

### D. Numerical-support admissibility
Evaluated **on calibration data only**, never on protected intervals:

- sufficient finite samples in every calibration interval;
- not identically constant on the calibration interval;
- not identically zero across development discharges (S7.1 found 84
  identically-zero pairs, all beam channels that never fired);
- finite dynamic range.

### E. Denominator / singularity admissibility
For ratios and trajectory-relational derivatives:

- the denominator must be bounded away from zero on the calibration interval by
  a predeclared margin, **or**
- a declared regularisation must be applied and recorded as part of the
  coordinate's definition — never tuned per result.

Predeclared: a denominator whose calibration-interval sign changes, or whose
minimum absolute value falls below a fixed fraction of its calibration-interval
scale, is inadmissible unless regularised by a declared scheme.

### F. Temporal-resolution admissibility
No coordinate may claim resolution finer than its coarsest source. Derivatives
of upstream-upsampled signals are excluded or flagged
`NUMERICAL_SENSITIVITY_ONLY`. Second and higher derivatives are presumed
inadmissible.
→ `NUMERICAL_RESOLUTION_POLICY.md`

### G. Semantic admissibility
A coordinate must be **stateable in words**. If a constructor produces something
with no expressible scientific meaning, it is inadmissible regardless of its
numerical behaviour. This is a deliberate constraint on the search: the study is
about interpretable relational structure, and an uninterpretable coordinate
cannot support the claim even if it fits.

### H. Leakage admissibility
No coordinate may depend on any quantity fitted using protected-interval data —
means, scales, thresholds, smoothing parameters, or coefficients.
→ `PREPROCESSING_AND_LEAKAGE_POLICY.md`

---

## Evaluation order

Cheap and target-independent first, so that expensive checks never run on
already-doomed candidates, and so that no rejected candidate has touched
protected data:

```
B  boundary compliance      (graph reachability)
A  provenance               (metadata)
C  dimensional              (type algebra)
G  semantic                 (constructor definition)
F  temporal resolution      (cadence metadata)
D  numerical support        (calibration data only)
E  denominator conditioning (calibration data only)
H  leakage                  (audit of fitted quantities)
```

**A, B, C, F and G are decidable without touching any data at all.** Only D, E
and H require calibration values, and none requires protected values.

## Recording

Every rejection is recorded with the class that rejected it and the evidence.
The rejection log is part of `Ahat_rec` at S7.7 and is what makes
*"not searched"* distinguishable from *"inadmissible"*.

## Deferred

- **S7.5/S7.6:** instantiated admissibility over the generated ontology;
  per-class rejection counts.
- **S7.7:** the explored frontier and the searched/unsearched boundary.
