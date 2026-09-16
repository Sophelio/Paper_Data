### S7.9 Development Selection And Freeze

The previous stages fixed where the search looked and by what rule its output
would be judged, but deliberately made no choice. This stage executes that rule
and makes the irreversible development-side choice, then closes the model before
any external observation is available.

#### Lexicographic Reduction Of The Explored Frontier

The frozen utility was applied to all 162 845 supports of the explored frontier
in the order fit, stability, parsimony, conditioning, support stability, each
criterion acting only among candidates practically equivalent on those above it.

| Set | Count | Criterion | Bound? |
|---|---|---|---|
| `E0` | 162 845 | explored frontier | — |
| `E1` | 1 055 | primary fit quality | yes |
| `E2` | **1** | development generalization / stability | **yes — decisive** |
| `E3` | 1 | parsimony | no |
| `E4` | 1 | conditioning | no |
| `E5` | 1 | support stability | no |

Rank 1 admitted 1 055 candidates. Of these, 1 024 fell within the 0.01
practical-equivalence floor and 31 entered only because their paired standard
error exceeded it — the floor did the great majority of the work, exactly the
behaviour the S7.2C correction was written to produce. All survivors were of
size 10 to 12; no smaller support survived on fit.

Rank 2 was decisive. Every one of the 1 055 candidates had **block A** — the
block with the shortest calibration window — as its worst temporal block, so the
worst-block comparison was made on common ground. 227 candidates were
practically equivalent on that worst block, and among them one candidate
attained the strictly minimum 90th-percentile discharge NRMSE, with no tie.
Parsimony, conditioning and support stability could not alter a set that already
contained a single member; they were executed, recorded, and found non-binding.

#### Development-Selected Representation

The development-selected representation is a twelve-coordinate support built
from three identity levels, four level–level products, three level–level ratios
and two unary reciprocals, drawing on seven scientific families — magnetics,
ECE electron-temperature profile, CER rotation and ion temperature, pedestal
density, gas injection, neutral beams and filterscope D-α.

Its development-side quantities are a mean calibration-normalized RMSE of
0.1664, a worst-block value of 0.1943, a 90th-percentile discharge value of
0.2114, and a median log₁₀ condition number of 1.99 with no infinite cells. All
twelve coordinates are active; parsimony's second subcriterion was non-binding,
as anticipated.

It is not the best-fitting support in the frontier. The minimum fit, 0.16628,
belongs to a different size-12 support; the selected one sits 0.00012 away,
inside the frozen equivalence set, and won on temporal and per-discharge
robustness instead. That is the lexicographic utility behaving as designed:
among representations that cannot be distinguished on fit, the one that fails
least badly on its worst block and its worst discharges is preferred.

Two properties are carried forward as qualifications rather than corrections.
The support contains an uncalibrated diamagnetic-loop signal, so coefficients
involving it have no certified physical-dimensional interpretation. It also
contains a pedestal-density diagnostic — a predictor from the same scientific
family as the target — which the frozen information boundary certifies as
independent of the target signal, and which is flagged here so that the point is
addressed rather than discovered. Neither property caused the support to be
rejected; the frozen rule contains no mechanism for that, and inventing one
after seeing the outcome is precisely what the stage discipline forbids.

Selection occurred **within the frozen explored frontier**. Approximately
5.1 × 10³⁹ admissible support combinations were never searched and carry no
negative finding. Nothing here is a claim of global optimality.

#### Stability And Conditioning

Conditioning is unremarkable and was never binding: the selected design has a
median log₁₀ condition number near 2 across all sixty discharge-block cells,
with no rank-deficient and no degenerate-scale cell.

Selection stability is the honest weak point of this stage and is reported as
found. Resampling the twenty development discharges 1 000 times produced **217
distinct winners**; the selected representation was chosen in **9.3 %** of
replicates, and the ten most frequent winners together account for under 40 %.
Under the three block-omission perturbations it was selected once. In every one
of the 1 000 replicates the procedure again resolved to a single candidate at
Rank 2, so the instability is not indecision within the rule — it is genuine
sensitivity of *which* support the rule lands on to which discharges are in the
development cohort.

Two things follow, and only two. First, the frozen policy attaches no pass/fail
threshold to support stability, so this does not and may not alter the
selection. Second, because the surviving set at Rank 4 already contained exactly
one candidate, the stability quantities were diagnostic rather than selective —
they could not have changed the outcome even had they been higher.

What the number does constrain is interpretation, and a descriptive look at the
same bootstrap output sharpens the point. Instability is concentrated at the
level of the *whole support*, not at the level of the coordinates. Across the
217 winning supports, the uncalibrated diamagnetic-loop level appears in every
single one; the plasma-current-to-ECE ratio appears in 84 %, the
D-α-to-pedestal-density ratio in 75 %, and a pedestal-density–ECE product in
74 %. Eight coordinates recur in at least half of all winners, four of which are
in the selected support. The development cohort, in other words, identifies a
recurring set of relational ingredients far more reliably than it identifies any
particular twelve-element combination of them. The selected support should be
read as one representative of a broad equivalence class that twenty discharges
cannot resolve between, not as a uniquely identified physical structure. This
observation is reporting only: it defines no criterion, applies no threshold and
changes nothing that was frozen.

The Rank-1 fit term is arithmetically the same quantity as the navigation score
that guided the search, and the selected support's fit reproduces it to float32
storage precision. This is an identity of arithmetic, not independent
confirmation: the navigation score determined where the search looked, and fit
is one criterion of the frozen utility applied to what was found.

#### Pre-External Freeze

The selected support was hashed into an immutable lock **before** any baseline
hyperparameter was chosen, so comparator behaviour could not feed back into
representation selection. Only then were the six comparators instantiated: the
calibration-mean and persistence baselines and the AR(1) diagnostic carried
verbatim from their parents; the raw ridge comparator on the full
seventy-eight-predictor target-admissible basis and the hardened-basis ablation
on seventy, each tuning its penalty independently under a grid and selection
rule frozen and hashed before a single penalty value was evaluated; and the
gradient-boosting comparator at library defaults with only its random seed
fixed. None was run. No development comparison between any baseline and the
selected representation is made, reported, or implied at this stage.

Support, coordinate definitions, estimator, preprocessing, validation geometry,
denominator rules, interpretation flags, every comparator configuration, the
inference protocol and the sealed external cohort's metadata are all recorded and
hashed in a single pre-external package, re-verified after writing with zero
mismatches. Zero external predictor values, zero external target values and zero
external model evaluations were opened at any point in this stage.

#### Gate To External Validation

The selected representation and every comparison configuration are now
immutable. S7.10 opens the previously sealed external cohort and evaluates
structural transfer and the frozen baseline ladder without altering the
representation.
