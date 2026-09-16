### S7.6 Admissible Coordinate–Relation Universe

#### Hardened Atomic Instantiation

The nine constructor families of the hardened ontology were instantiated
mechanically over the seventy-primitive hardened basis. Every coordinate
signature was regenerated from the primitive basis and the frozen constructor
catalogue; nothing was imported from the superseded universe built on the
earlier seventy-eight-primitive ontology, which is retained unchanged as audit
history.

The enumeration yields twenty-three thousand eight hundred and sixty-one
symbolic atomic coordinates: seventy levels, sixty-three first temporal
derivatives, two thousand three hundred and forty-six pairwise products, four
thousand five hundred and fifty-six pairwise ratios, three thousand nine hundred
and six trajectory-relational derivatives, sixty-eight reciprocals, and four
thousand two hundred and eighty-four instances each of the three level–rate
families. Maximum construction depth is one throughout.

Admissibility was then applied in the frozen order: information boundary,
provenance, dimensional typing, semantic admissibility, temporal resolution,
numerical support, denominator domain, and leakage. No metadata gate rejected
any coordinate, because the operand-eligibility rules frozen with the ontology
already encode those conditions — the two uncalibrated quantities appear only as
levels, and the five interpolated quantities never appear in a rate role.

#### Numerical And Partial-Domain Qualification

Numerical qualification used development-cohort predictor values only, on the
three nested block-local calibration intervals. Target values were never opened;
external-cohort values were never opened; no model, baseline, or
predictor–target statistic was computed at any point.

A coordinate was required to be finite, non-constant, and of finite dynamic
range on every required calibration block. Constancy was detected exactly rather
than through a variance threshold, so a beamline that did not fire during a
calibration interval renders its own level coordinate inadmissible, as it
carries no observational variation there.

Five of the nine families are partial maps. Their denominators were qualified
first, because a constructed coordinate is not a real-valued function on a block
where its denominator is singular. The already-frozen denominator rule was
verified by hash and applied unchanged: on each required development calibration
block the denominator must be finite, must not change sign, must have non-zero
root-mean-square scale, and its minimum absolute value must remain at least five
per cent of that scale. No regularisation of any kind was permitted, and none
was used.

Two reusable denominator tables were built. Of the sixty-eight typed level
denominators, thirty-nine satisfy the condition on every required block. Of the
sixty-three rate denominators, **none** does: sixty-one fail first because a
time derivative crosses zero within every calibration interval, and two fail
earlier still because the corresponding beamline never fired, leaving a
derivative of zero scale.

#### Constructor-Family Survival

Ten thousand seven hundred and seventy-eight atomic coordinates are admissible,
about forty-five per cent of the symbolic space.

| Family | symbolic | admissible |
|---|---|---|
| C0 level | 70 | 66 |
| C1 derivative | 63 | 59 |
| C2 product | 2 346 | 2 080 |
| C3 ratio | 4 556 | 2 457 |
| C4 phase derivative | 3 906 | **0** |
| C5 reciprocal | 68 | 39 |
| C6 level–rate | 4 284 | 3 776 |
| C7 rate over level | 4 284 | 2 301 |
| C8 level over rate | 4 284 | **0** |

The two families that place a rate in a denominator contribute nothing. This is
a statement about the observational object, not about the constructors: the
grammar admits them, and the object does not support stable primary instances of
them under the frozen numerical-domain condition. The gate was not weakened and
the ontology was not revised.

The level–rate interaction, which the hardened grammar introduced precisely
because it relates a level to a rate without placing either in a denominator, is
the largest surviving family. These counts describe what the task permits; they
carry no implication of predictive relevance.

#### Exact Dependency Constraints

The deterministic identity between aggregate injected beam power and its eight
per-beamline components was re-derived over the hardened catalogue rather than
copied forward. It restates exactly in eight constructor contexts — level,
derivative, product, ratio, phase derivative, both operand roles of the
level–rate interaction, rate-over-level with the aggregate as numerator, and
level-over-rate with the aggregate as numerator — giving four hundred candidate
groups. It does not restate where the aggregate enters a denominator, nor under
the reciprocal, which is not linear in its operand.

Every one of those four hundred groups is vacuous in this universe. Four of the
eight per-beamline component coordinates are themselves inadmissible, because
those beamlines were inactive throughout at least one required calibration
interval. No admissible support can therefore contain a complete exact set. The
constraint is retained, well defined, and currently excludes nothing; neither
the aggregate nor the component representation is privileged.

#### Factorized A_rec

The admissible universe is defined intensionally. A representation is a set of
between one and twelve admissible atomic coordinates satisfying the set-level
predicates — no duplicates, no sensitivity-only coordinate, no complete exact
dependency group, and the target absent — paired with the unchanged relation
template. The coordinate set together with those predicates is an exact finite
representation; enumerating supports individually is unnecessary and
astronomically large, and was not attempted.

#### Gate To Search

The resulting A_rec specifies what the hardened task permits. No coordinate has
yet been preferred or evaluated for reconstruction utility. S7.7 freezes the
search policy and defines the explored frontier.
