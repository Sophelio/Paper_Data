### Observational Range-Support Qualification

#### Contract Defect Exposed By Qualification

The first discovery epoch failed a mandatory external gate, and the reconciliation
audit that followed established two things. The pooled interpretation of the
observational record was not at fault — an operational-state explanation was
tested against predictor-side evidence and refuted. And no instantiated object in
the discovery chain had been built incorrectly: the admissible universe admitted
the coordinate that failed *by rule*, because the contract's only partial-map
guard covers denominators, and product constructors have no denominator and
therefore no gate.

What remained was a gap in the contract itself. Mathematical totality had been
treated as sufficient for admissibility. It is not. A squared quantity is defined
for every finite argument, yet a relation fitted on one interval of that argument
becomes empirically unsupported when the argument is evaluated far outside it.
The contract distinguished coordinates that are *undefined* from coordinates that
are defined; it did not distinguish relations that are *supported* from relations
that are merely defined.

#### Range-Support Admissibility

Observational range support is a property of a coordinate together with a
calibration interval and an application interval — never of the constructor type
alone. Writing `L` and `U` for the smallest and largest values a coordinate takes
during calibration, the score

```
E = max( L − min(c_app),  0,  max(c_app) − U ) / (U − L)
```

measures how far beyond the calibration hull the application values reach, in
units of the calibration range itself. It is dimensionless, unchanged if the
coordinate is rescaled by any nonzero constant, symmetric in both directions,
monotone in departure, and computed identically for every constructor family
from four numbers per block.

A coordinate is range-supported on a block when `E ≤ 1`: application values may
extend no farther beyond the calibration hull than one full calibration range. A
support is range-supported only when every one of its coordinates is, with no
averaging and no cancellation, and the failing coordinate remains identifiable. A
coordinate constant on calibration receives an explicit degenerate status rather
than a hidden epsilon.

Failure is local. It means the fitted relation is not empirically supported on
that block — never that the coordinate is globally meaningless. The ontology and
the admissible universe stay expressive; the coverage requirement lives in search
and qualification.

The condition is separate from, and additional to, the existing denominator
admissibility rule, which is unchanged. That the two are genuinely distinct is
confirmed empirically: across all ten thousand seven hundred and seventy-eight
admissible coordinates and one hundred and eighty-six blocks there is not a
single non-finite coordinate value, so the denominator condition binds nowhere in
the atomic universe.

#### Contract Revision

One normative component changed. `P_rec` gains the range-support predicate;
`V_rec` gains a consequential coverage clause requiring that any primary
full-domain reconstruction claim be range-supported on every qualification block,
which adds no performance threshold and modifies no existing gate. The target,
the information boundary, the baseline ladder, the utility and the intended
domain are all unchanged — the utility deliberately so, since relaxing it would
make the next epoch easier to pass for reasons unrelated to the defect. The
previous contract is not overwritten; the transition from it is recorded with its
full provenance.

A parallel provenance question was resolved along the way. The gas-actuator
signals carried two conflicting unit records, which the reconciliation audit had
treated as an unresolved inconsistency. They are not of equal standing: the
frozen units registry records the upstream unit string literally as "volt" on
fifty-one of sixty-two shots, superseding a first-pass external-convention
hypothesis held at low confidence with an ambiguous dimensional signature. These
are actuator command voltages, not fueling rates, and the frozen ontology was
correct.

#### Prospective Status

Everything that could bias the rule was frozen before it could. The conceptual
definition preceded any numerical realization; the fourteen desiderata were
hashed before any candidate was computed; the threshold grid was hashed before
any applicability count was inspected. The metric was chosen over its alternative
on constructor neutrality — its behaviour varies by a factor of four across
constructor families where the alternative varies by a factor of thirty-five —
and not on any reconstruction outcome. No target value, residual, error metric or
qualification label was read at any point during construction.

The clearest evidence that the threshold was not tuned is that it is maximally
unfavourable to the first epoch. At the chosen threshold none of the two hundred
and seventeen previously winning supports is range-supported across the domain,
and the previously selected representation has only half its coordinates
supported. A threshold chosen to flatter the earlier result would have been
larger.

A retrospective check, run only after the policy was hashed, confirms that the
frozen rule would have marked both catastrophic blocks unsupported, by three
orders of magnitude, while the same discharges' later blocks — which
reconstructed normally — pass. That is motivating evidence. It is not validation,
and it cannot be: this stage establishes only that the condition is coherent,
generic, stable and non-vacuous. Whether it improves reconstruction is the next
epoch's question.

#### Decision

Discovery may resume under the revised contract. Roughly a third of the
admissible coordinates retain full-domain support, spanning every constructor
family, and because the support predicate is a conjunction over the same blocks,
any combination of them is supported by construction — leaving on the order of
ten to the thirty-third candidate supports of the previous size. The rule
constrains without collapsing.

One consequence must be accepted rather than worked around: the earlier explored
frontier cannot be reused, because it was searched under a utility that never
applied this condition. The next epoch searches afresh.
