# S7.9 — Development selection and pre-external freeze: internal audit report

Stage **S7.9** · Freeze `D3D-SIR-S7.9-DEVELOPMENT-SELECTION-AND-PREEXTERNAL-FREEZE-V1`
Parent `D3D-SIR-S7.8-UTILITY-AND-QUALIFICATION-RULES-V1`

---

## 1. Executive verdict

**`FROZEN_WITH_QUALIFICATIONS`** · 54/54 acceptance checks · `FIREWALL_INTACT`.

The frozen utility was executed exactly over the frozen frontier, one
representation was selected deterministically, its support and estimator were
locked and hashed before any baseline hyperparameter existed, all six comparator
configurations were frozen without being run, and the pre-external package was
written and re-verified. Zero external values were opened.

Seven qualifications are recorded. The one that matters scientifically is
**low support-level selection stability**: the selected representation was
chosen in 9.3 % of the 1 000 bootstrap replicates, which produced 217 distinct
winners. It is reported as found. The frozen policy attaches no threshold to
support stability, so it does not and may not change the selection.

## 2. Parent verification

Ten authoritative lineage entries verified, plus four historical/superseded
freezes preserved and located. **All 41 S7.7R artifacts and all 26 S7.8
artifacts reproduce byte-for-byte.** S7.8 status confirmed
`FROZEN_READY_FOR_S7.9`.

| Confirmation | Result |
|---|---|
| `target == density` | ✔ |
| external cohort == 42, 24 earlier / 18 later, `SEALED` | ✔ |
| `Ahat_rec == 162 845` | ✔ |
| search policy `ONE_SEED_PRIMARY` | ✔ |
| `U_rec == U_REC_OPERATIONAL_V1` | ✔ |
| `V_rec == V_REC_OPERATIONAL_V1` | ✔ |
| estimator `DEVELOPMENT_RELATION_OLS_V1` | ✔ |
| two-seed sensitivity `NOT_EXECUTED` | ✔ |
| baselines `NOT_RUN` upstream | ✔ |

Verdict `ZERO_SUBSTANTIVE_DRIFT`.

## 3. External firewall

| | |
|---|---|
| external predictor value reads | **0** |
| external target value reads | **0** |
| external model evaluations | **0** |
| external derived statistics | **0** |
| development discharges opened | 20 |

The coordinate engine asserts membership against the frozen external id set and
raises `FIREWALL_BREACH` on any external shot. External artifacts were read for
metadata only — ids, era, counts, partition policy. All development reads are
logged in `manifests/DEVELOPMENT_ACCESS_LOG.json`.

## 4. Array reuse preconditions

All five verified → **`ARRAY_REUSE_AUTHORISED`**.

1. **Hashes** — 41/41 S7.7R artifacts reproduce.
2. **Estimator equivalence** — S7.7R's recorded proxy check (max relative
   deviation 1.7 × 10⁻¹³ against `lstsq`), *and* an independent S7.9
   re-derivation: `DEVELOPMENT_RELATION_OLS_V1` implemented explicitly as
   `lstsq` on `[1, Z]` reproduces the stored 60-cell NRMSE profile of the
   selected support to a maximum relative deviation of **4.4 × 10⁻⁸**, below the
   float32 storage epsilon of 1.19 × 10⁻⁷. The reuse is numerically justified,
   not merely hash-justified.
3. **Metric equivalence** — scale definition, `ddof=0`, zero-scale behaviour and
   `epsilon_added=false` all unchanged.
4. **Support identity** — array ids map bijectively onto the 162 845 registry
   rows.
5. **Block identity** — 60 cells over the 20 frozen development discharges and
   blocks A/B/C.

## 5. Canonical parse check

The frozen parenthesis-depth-aware parser was used operationally; the naive
splitter was used **only** to quantify the hazard.

| Check | Result |
|---|---|
| `parsed_atom_count == registry.support_size` | **162 845 / 162 845** |
| canonical re-serialization == stored `support_id` | **162 845 / 162 845** |
| atoms ascending-sorted | **162 845 / 162 845** |
| rows a naive `split('|')` would misparse | **116 608 (71.6 %)** |

The historical audit reference from S7.8 (116 608 rows, 71.6 %) is reproduced
exactly. No naive parsing was used operationally at any point.

## 6. Input matrix integrity

162 845 candidates × 60 cells; 20 development discharges × 3 blocks;
**9 770 700 / 9 770 700 finite primary cells** — verified, not assumed. Zero
overlap between the atomic and explored id sets. Rows are joined to the registry
**by `support_id`**, never by position; no row-order assumption was made
anywhere.

## 7. Rank 1 — primary fit

`E0 = 162 845 → E1 = 1 055`.

| | |
|---|---|
| `FIT_best` | 0.166281515 |
| `C_fit_best` | the size-12 lowest-navigation-score support |
| `FIT` range in `E1` | [0.166282, 0.180701] |
| `SE_delta` range in `E1` | [5.4 × 10⁻¹⁰, 0.01511] |
| admitted within the 0.01 floor | **1 024** |
| admitted by `SE_delta` beyond the floor | **31** |

The floor did the great majority of the admitting, and `SE_delta` fell below it
for most pairs — the exact degeneracy the S7.2C `max(SE, 0.01)` correction was
written to prevent. No transitive closure, no top-K, floor unchanged at 0.01.
Equivalence was tested pairwise against the canonical-first argmin.

`E1` contains only sizes 10 (3), 11 (97) and 12 (955). No support smaller than
10 survived Rank 1.

## 8. Rank 2 — development stability

`E1 = 1 055 → E2 = 1`. **This is the binding rank.**

`b_star` was block **A for all 1 055 candidates** — block A has the shortest
calibration window ([0, 0.40)), and it is uniformly the hardest. The worst-block
comparison was therefore made on common ground rather than across different
blocks.

| | |
|---|---|
| `BLOCK_WORST` reference | 0.183989767 |
| `BLOCK_WORST` range in `E1` | [0.183990, 0.242796] |
| `BLOCK_WORST`-practically-equivalent survivors | **227** |
| minimum `SHOT_P90` | 0.211412116 |
| ties at the minimum | **none** |

The worst-block paired standard error was used as frozen: each candidate
contributed its own `b_star`, `SE_delta_worst = sd(d_s, ddof=1)/sqrt(20)`, and
the threshold was `max(SE_delta_worst, 0.01)`. **The 0.01-only fallback was NOT
invoked** — S7.8 established that a discretion-free paired SE exists, and it
was used. `SHOT_P90` used `numpy.percentile(..., method='linear')` and was
minimized exactly, with no new epsilon.

## 9. Rank 3 — parsimony

`E2 = 1 → E3 = 1`. Non-binding: a singleton cannot be reduced.

`ACTIVE_TERMS` for the survivor is **12 of 12** under the frozen union rule (a
column is active iff its OLS coefficient is not exactly `0.0` in at least one of
the 60 calibration fits). No magnitude threshold, no p-value, no significance
test, intercept excluded. **`RANK3_ACTIVE_TERMS_NONBINDING` recorded** — as
S7.8 anticipated, exact zeros do not occur under full-rank OLS. No threshold was
invented to force the subcriterion to bind.

## 10. Rank 4 — conditioning

`E3 = 1 → E4 = 1`. Non-binding.

Computed from **singular values** of the calibration-standardized design with
the intercept column excluded — never the normal-equation condition number.

| | |
|---|---|
| `COND_MEDIAN` (log₁₀ κ) | 1.991754 |
| `COND_P90` | 2.173042 |
| `COND_MAX` | 2.259641 |
| infinite cells | **0** |
| degenerate-sd cells | **0** |

No condition-number cutoff was introduced and no candidate was called
inadmissible on conditioning grounds. Conditioning is comfortable throughout —
a median κ near 10² over 60 cells.

## 11. Rank 5 — bootstrap

Exactly **1 000** replicates, `numpy.random.default_rng(2026090501)`, 20
**discharges** resampled with replacement, blocks never resampled, integer
multiplicities applied to every discharge-level aggregation. The search was not
rerun. Runtime 21 s.

| | |
|---|---|
| distinct Rank-4 winners | **217** |
| `BOOT_SELECTION_FREQ` of `C_dev_star` | **0.093** (the modal winner) |
| next most frequent | 0.055, 0.052, 0.039, 0.034 |
| cumulative top-10 frequency | 0.398 |
| winners with frequency ≥ 0.02 | 10 |
| winner size distribution | 10 → 9, 11 → 32, 12 → 176 |
| replicate `E1` size | min 1, max 4 336, mean 522 |
| replicate `E2` size | **1 in every replicate** |

Two structural facts deserve emphasis. First, `E2` collapsed to a singleton in
**all 1 000** replicates, so the instability is not indecision inside the rule —
it is genuine sensitivity of *which* support the rule lands on to cohort
composition. Second, because the unresampled `E4` contained one candidate,
`BOOT_SELECTION_FREQ` was **diagnostic, not selective**: Rank 5 could not have
changed the outcome at any value.

Conditioning and `ACTIVE_TERMS` were memoized (1 candidate each was ever
needed), which changed how the procedure was computed and nothing about what it
computes.

**Reproducibility.** The RNG stream was identical on reseed; an independent
recheck of every 97th replicate reproduced its winner exactly; the complete
winner vector hashes to `918166f2…`.

## 12. Fold perturbations

Exactly three block omissions, each recomputing Ranks 1–4 over the remaining two
blocks on the same `Ahat_rec`. The search was not rerun.

| Perturbation | `E1` | `E2` | Winner is `C_dev_star`? |
|---|---|---|---|
| omit A | 941 | 1 | no |
| omit B | 455 | 1 | **yes** |
| omit C | 1 243 | 1 | no |

`FOLD_SELECTION_FREQ(C_dev_star) = 1/3 = 0.333`. Consistent with the bootstrap:
which support wins is sensitive to which temporal block is dropped.

## 13. E0–E5 survivor ledger

| Set | Count | Criterion | Bound |
|---|---|---|---|
| `E0` | 162 845 | explored frontier | — |
| `E1` | 1 055 | primary fit quality | **yes** |
| `E2` | 1 | development generalization / stability | **yes — decisive** |
| `E3` | 1 | parsimony | no |
| `E4` | 1 | conditioning | no |
| `E5` | 1 | support stability | no |

`utility_elimination_ledger.csv` carries **162 844 rows** — exactly `|E0| − |E5|`
— each with the rank, criterion, reason, comparison quantity, candidate value,
reference value and applied threshold.

## 14. Selected representation

```
ID(cerqtit6)|ID(pcdiamag3)|ID(prmtan_neped)|PROD(ece37,ece39)|PROD(gasa,gasa)|
PROD(pinj,cerqrott6)|PROD(prmtan_neped,prmtan_neped)|RATIO(ece21,prmtan_neped)|
RATIO(fs03da,prmtan_neped)|RATIO(ip,ece22)|RECIP(cerqtit10)|RECIP(prmtan_neped)
```

Size 12. Constructors C0×3, C2×4, C3×3, C5×2. Seven scientific families.
`FIT` 0.166398 · `BLOCK_WORST` 0.194252 (`b_star` = A) · `SHOT_P90` 0.211412 ·
`ACTIVE_TERMS` 12/12 · `COND_MEDIAN` 1.9918 · `BOOT` 0.093 · `FOLD` 0.333.

**`C_dev_star` is not the fit-best candidate.** It sits 0.000116 above
`FIT_best`, inside the frozen equivalence set, and won on Rank-2 robustness.
That is the lexicographic utility working as designed, and it is worth stating
plainly because a reader expecting "best fit wins" will otherwise read it as an
error.

Full metadata — units, temporal-resolution rules, provenance lineage,
realization ids, ancestry — in `SELECTED_REPRESENTATION.json` and
`SELECTED_REPRESENTATION.md`.

## 15. Interpretation flags

**`UNCALIBRATED_SIGNAL` carried.** `ID(pcdiamag3)` is uncalibrated digitiser
output with no upstream unit. Coefficients involving it have no certified
physical-dimensional interpretation. The support was **not** rejected for it.
Notably, `pcdiamag3` appears in **100 % of the 217 bootstrap winners** — it is
the single most persistent ingredient in the whole development analysis.

**Density-family predictor — flagged deliberately.** `prmtan_neped` (pedestal
electron density from a tanh fit) is in the `density` family, the same family as
the target. All thirteen primitive ancestors are
`certified_independent_of_target` under the frozen S7.3R boundary, and all
twelve coordinates carry `TRANSITIVE_FROM_TARGET_INDEPENDENT_BOUNDARY`, so V1 is
not compromised by the frozen rules. It is raised here because a
density-family predictor for a density target will draw scrutiny, and it should
be addressed explicitly at S7.12 rather than discovered by a referee.
`prmtan_neped` is structurally central: it appears in five of the twelve
coordinates.

**C6/C7:** absent — reported naturally, not treated as surprising and not
repaired. **ECE ancestry:** present (four ECE channels) — no penalty, quota,
bonus or correction. **Aliasing / upsample flags:** none set. **All coordinates
`PRIMARY`**, none from a sensitivity lane. **Partial map:** none — the support
is total on the development support.

## 16. Development representation lock

`DEVELOPMENT_REPRESENTATION_LOCK.json`, sha256 `c7c6a36b8676…`, locked
`2026-09-05T20:22:16Z`.

It pins the support, coordinate ids, target, estimator, preprocessing,
validation geometry, utility policy and selection provenance, and hashes the
four selection artifacts. `support_may_change_after_this_lock: false`.

**The lock timestamp precedes the baseline pre-value freeze**, which itself
precedes the first alpha evaluation. Verified programmatically in the acceptance
checks, not merely asserted.

## 17. Baseline specification audit

Parents win. B0, B1, B3 and B1A were already complete and are carried verbatim —
B1A from `PRE_SEARCH_CONTRACT_COMPLETION_V1` with `hyperparameter_selection:
NONE`. H0 was complete in S7.5H except that its penalty rule is defined *by
reference to B2*.

**Only B2 was numerically incomplete**: no parent contains a penalty grid or
selection algorithm. §19 therefore applies, and H0 inherits the completion.

`BASELINE_SPECIFICATION_COMPLETION_PREVALUE.json` records
`RIDGE_ALPHA_SELECTION_V1` and was hashed (`fd05fcc0…`) **before any alpha was
evaluated**. This is implementation completion of an already-frozen family, not
family selection.

## 18. B2 / H0 penalty selection

Both tuned independently under the identical procedure, development data only,
after the lock.

| | B2 | H0 |
|---|---|---|
| predictors | **78** full target-admissible primitive levels | **70** hardened levels `P_hard` |
| restricted to the hardened basis | **no** | — |
| selected alpha | **1** | **1** |

The eight primitives in B2 but not H0 (`ece17`, `ece23`, `ece24`, `ece26`,
`ece32`, `ece34`, `ece40`, `fs04da`) are the S7.5H redundancy removals, which is
what makes the later `B2 vs H0` and `H0 vs relational` readings possible.

Per-alpha tuning criteria are recorded in `baseline_b2_alpha_tuning.csv` and
`baseline_h0_alpha_tuning.csv` **as the tuning audit only**. No comparison
between any baseline and the relational representation is made, reported or
implied.

## 19. B3 reproducibility

`sklearn` **1.9.0**; `HistGradientBoostingRegressor` has 21 constructor
parameters, all recorded — the single explicit parameter and every inherited
default.

```
HistGradientBoostingRegressor(random_state=2026090502)
```

`random_state` is the only departure from defaults and is required for
determinism. No compatibility departure was necessary, so the human-review stop
in §24 was not triggered. B3 was not tuned.

## 20. Baseline configuration freeze

All six — B0, B1, B1A_AR1, B2, B3, H0_RAW_HARDENED — **`FROZEN_NOT_RUN`**, each
hashed in `BASELINE_CONFIGURATION_MANIFEST.json`. `S_PERS_V1` carried unchanged,
not used for selection, not used to reopen any rank, required reporting at
S7.10.

## 21. V2 evidence

`V2_EVIDENCE_COMPLETE`. Nine decisions — target, ontology, admissible universe,
search policy, explored frontier, utility rules and thresholds, support
selection, estimator, baseline hyperparameters — each traced to the stage that
fixed it, each with `external_outcomes_used: false`, plus the programmatically
verified lock-before-tuning ordering and zero external reads.

The status is **evidence completeness, not a resolved gate**: the S7.8 schema
assigns V2 `PENDING_S7.9` and reserves formal resolution for the S7.10 gate
table and S7.12 assembly. No status outside the parent schema was invented.

## 22. Pre-external freeze

`PRE_EXTERNAL_MODEL_FREEZE.json` pins items **A through R** as specified.
Re-read and re-verified after writing: **13 substantive entries, 0 hash
mismatches**. The freeze file is excluded from its own manifest under the
established convention. No external value had been opened before the freeze
timestamp, and none after.

## 23. Search-boundary statement

Every artifact carries `selection_domain: AHAT_REC_DENSITY_ONE_SEED_V2` and
`global_optimality_claim: false`. Approximately 5.1 × 10³⁹ admissible support
combinations remain `ADMISSIBLE_UNSEARCHED` and carry no negative finding.
`C_dev_star` means *selected from the frozen explored frontier* — not *best
representation in `A_rec`*.

The Rank-1 fit term is arithmetically the same quantity as `J_search`, and the
selected support reproduces it to float32 storage precision. Recorded
explicitly: this is **not** independent confirmation. `J_search` determined
where the search looked; `FIT` is Rank 1 of the frozen utility over what was
found. Search frequency is not scientific importance.

`TWO_SEED_SEARCH_DEPTH_SENSITIVITY` remains `DECLARED_OPTIONAL`,
`NOT_EXECUTED`, with no outcome trigger defined.

## 24. Files

6 Markdown (limit 20) · 12 result CSV · 13 policy/config JSON · 8 manifests ·
7 scripts.

## 25. Reproduction

```bash
python scripts/s7_9_a_verify.py           # hard gates
python scripts/s7_9_b_ranks12.py          # Rank 1, Rank 2
python scripts/s7_9_d_rank345.py          # Rank 3, 4, 5 + bootstrap + folds
python scripts/s7_9_e_select_and_lock.py  # ledger, representation, LOCK
python scripts/s7_9_f_baselines.py        # baseline audit, completion, freeze
python scripts/s7_9_h_coord_stability.py  # coordinate participation (reporting)
python scripts/s7_9_g_freeze.py           # V2, pre-external, acceptance, freeze
```

Environment: Python 3.13.5, numpy 2.5.2, pandas 3.0.5, scikit-learn 1.9.0,
Windows-11-10.0.26200-SP0.

## 26. Recommendation for S7.10

**`READY_WITH_QUALIFICATIONS`.**

The qualifications do not compromise V2 or V5: the representation was locked and
hashed before any comparator hyperparameter existed, the pre-external package
re-verifies with zero mismatches, and zero external values were opened. Under
§38 this permits S7.10 **after human review of the qualifications**.

The reviewer should focus on one thing. Support-level selection stability is
**0.093** across 217 distinct bootstrap winners. That is a genuine limitation of
what twenty development discharges can resolve, and it constrains interpretation
of the specific twelve coordinates — though coordinate-level participation is
far more stable (`ID(pcdiamag3)` in 100 % of winners, three further coordinates
above 70 %). It does not affect the validity of the external test: the frozen
object is unambiguous and immutable, and S7.10 evaluates exactly that object.

Before opening any external value, S7.10 must re-verify every hash in
`PRE_EXTERNAL_MODEL_FREEZE.json`, confirm the freeze timestamp precedes its
first external access, and re-run the canonical-parse checksum.

If the external cohort shows that persistence wins, that raw coordinates win,
that the nonlinear baseline wins, that one processing era fails, or that
transfer fails entirely — that is the result. S7.7, S7.8 and S7.9 may not be
reopened to repair it.
