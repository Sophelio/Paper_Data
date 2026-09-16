# S7.2 — Reconstruction contract: internal audit report

**Freeze:** `D3D-SIR-S7.2-RECONSTRUCTION-CONTRACT-PRETARGET-V1`
**Status:** `FROZEN_READY_FOR_S7.3` · acceptance **31/31** · **Date:** 2026-09-02

---

## 1. Executive verdict

The target-blind contract skeleton is complete and frozen. Every rule that will
govern target selection, boundary construction, ontology generation, search,
validation and qualification was fixed **before any target exists**, and each
decision records the information deliberately withheld from it.

Four components are fully frozen (`q`, `H`, `U`, and the `V` protocol); four are
partially frozen with their target-dependent instantiation explicitly deferred.
That incompleteness is declared per field rather than hidden.

**No target selected. No target ranked. No coordinate constructed. No model
fitted. No external signal value read.**

Two things are worth flagging up front. First, a **defect in the parent freeze**
was found and documented (§2). Second, the fail-closed provenance rule may
remove **all 15 equilibrium quantities** from the primary boundary for some
targets — a real cost, accepted explicitly in advance rather than discovered
later (§5).

## 2. S7.1 freeze verification

**9/9 hashes verified; 12/12 object expectations hold.** 62 discharges, 95
signals, 5890 pairs, 95/95 backend-accessible, 95/95 unit determinations, zero
critical issues, `E` not instantiated, no target encoded.

### A defect in the parent freeze

The S7.1 freeze recorded artifact hashes under **two different rules**.
Artifacts built in memory were hashed as written to disk; two —
`FINAL_SIGNAL_INVENTORY.csv` and `signal_quality_summary.csv` — were re-read
with `pd.read_csv` first, which reformats floats (`0.0200` → `0.02`), so their
recorded hashes do not equal the file bytes.

Both rules are stable and reproducible. But a verifier applying **either** rule
uniformly reports false drift on the other subset — which is exactly what
happened on the first verification attempt here.

**Data integrity impact: none.** Every artifact verifies under one rule, and no
content changed. S7.2 verifies under both, records which applied per artifact,
and emits a uniform `canonical_raw_byte_hashes` set so later stages have one
rule. **The S7.1 freeze file was not modified** — the mixed record persists
there and is flagged for human attention (§21).

## 3. Scientific task class

`q_rec` = **continuous reconstruction** of one observed scalar quantity from
other admissible **contemporaneous** observations.

**Transfer:** structural transfer with local calibration — support shared and
frozen, coefficients discharge-specific. Explicitly **not** zero-shot.

Excluded by name: ELM detection, event classification, forecasting, causal
inference, control, universal equation discovery. The archive contains **no
event annotations at all**, so any event task would require importing an
unresolved label pipeline.

## 4. Target eligibility

Frozen, **not applied**. Eligible classes: `DIRECT_MEASUREMENT` and
`DIAGNOSTIC_RECONSTRUCTION` with resolved unit. Normally excluded: actuation
(14), equilibrium-derived (15), uncalibrated raw (2), event labels (0).

Twelve criteria; nine decidable from frozen metadata, three (residual
information, algebraic duplication, temporal variation) requiring
**development-only** inspection. Four numeric thresholds predeclared. **No model
is fitted for eligibility**, and candidates are never compared on
reconstructability.

**Noted consequence:** this excludes `pcdiamag3` — one of the historical eight
and the target of the retired dFL export — because S7.1 established it is
uncalibrated with no physical unit.

## 5. Information-boundary policy

Six exclusion rules, applied **before** ontology generation and **transitive**
over the coordinate graph.

**Fail-closed:** unresolved ancestry ⟹ not independence-certified ⟹ excluded.

The cost is stated in advance: for a target whose relationship to the
equilibrium group cannot be resolved, **all 15 equilibrium quantities leave the
primary boundary**. Three escapes are pre-declared — resolve the EFIT lineage;
run a labelled `PROVENANCE_RELAXED` secondary variant; or accept the exclusion.
Escape 2 must be declared before results are seen.

**Correlation is never ancestry** — neither to exclude nor to admit. This rule
exists because an earlier audit in this project demonstrated that conflating the
two produces both false leakage findings and false clearances.

**Sibling rule:** same-family channels excluded from the primary boundary;
full-boundary variant is a declared sensitivity. Both frozen now so neither can
be chosen afterwards.

## 6. Development / external partition

**20 development / 42 external**, deterministic (`i % 3 == 1` within each
period), **no seed**, **no signal value read** — the archives were not opened.

| | n | earlier | later | periods |
|---|---|---|---|---|
| development | 20 (32.3%) | 11 | 9 | 6 of 7 |
| external | 42 (67.7%) | 24 | 18 | 7 of 7 |

Era balance closely matches the object's own 56/44. The singleton period 1
(155537) goes to external so the external cohort covers all seven periods.

Since discharge is the inferential unit, 42 **is** the effective external sample
size.

## 7. External firewall

External signal values, target values, derived statistics and model outputs are
**sealed from S7.3 through S7.9**. Only shot identifiers and frozen S7.1
metadata may be known.

Enforced at four levels: code loads the development list from
`COHORT_PARTITION.json`; each stage records what it read; gate V2 fails a stage
that crossed; and S7.9 hashes the support before S7.10 verifies it.

A breach is **not silently correctable** — the affected decision must be
re-derived from development data or the study must report contamination.

## 8. Validation geometry

Three rolling-origin blocks per discharge; calibration `[0,0.4)`/`[0,0.6)`/
`[0,0.8)`, protected `[0.4,0.5)`/`[0.6,0.7)`/`[0.8,0.9)`.

Replaces the retired final-20% protocol, which was degenerate:
`var(eval)/var(calib) = 0.0032` meant a constant predictor won.

**Feasibility audited at all seven native cadences — 186/186 at every one.**
Worst case (20 ms, forced by admitting any equilibrium quantity) still gives ≥18
protected and ≥75 calibration samples per block per discharge, against
predeclared minima of 10 and 30. Audited using only common-window durations from
S7.1; no value of any kind was read. **Frozen as specified; no alternative
needed.**

## 9. Preprocessing and leakage

All fitted transforms estimated from calibration data only and applied unchanged
to protected intervals. 25 operations tabulated in `leakage_matrix.csv`.

The key asymmetry: **predictor** values inside the protected block are allowed
(that is what makes it reconstruction); **target** values are not.

**Whole-discharge z-scoring is forbidden** for primary evaluation where its
statistics include protected target values — which the historical pipeline's
within-discharge z-scoring would. RMSE is therefore reported in
calibration-normalized units.

## 10. Numerical resolution

**No super-resolution as primary observational evidence.** Analysis grid **no
finer than the coarsest admitted native cadence** — the rule the full 95-signal
provider already implements, so that implementation is preferred over a new one.

Derivatives: first order only; no derivative claims resolution finer than its
source; derivatives of the 16 upstream-upsampled signals excluded or flagged
`NUMERICAL_SENSITIVITY_ONLY`; equilibrium derivatives restricted to grids no
finer than 20 ms; second and higher orders presumed inadmissible.

The 18 signals downsampled without anti-aliasing remain admissible as levels,
carry an `ALIASING_RISK` flag on their derivatives, and support no
high-frequency claim.

The historical fixed-N grid is **not** the primary rule — it produces exactly
the super-resolution this policy forbids, and is allowed only for labelled
comparability runs.

## 11. Units and semantic types

Canonicalisation to SI (eV retained for temperature) **before** any constructor
runs; conversions recorded; dimensional checking at construction. Three scale
traps addressed: kW/W, cm⁻³/m⁻³, keV/eV.

Constructor type rules frozen for sums, ratios, products, derivatives,
trajectory-relational derivatives, normalization and transcendentals.
Normalization must record whether its reference is **physical** or **empirical**
— the latter is a fitted quantity subject to the leakage firewall.

`pcbcoil` and `pcdiamag3` keep a permanent `UNCALIBRATED_SIGNAL` type; no
invented dimensions. They remain admissible as *predictors*.

## 12. Scientific admissibility

Eight invariant classes (A–H), evaluated cheapest-first. **A, B, C, F and G
decide without touching any data**; only D, E and H need calibration values, and
none needs protected values.

Four distinctions carried explicitly: `AVAILABLE ≠ ADMISSIBLE ≠ PRIORITIZED ≠
VALIDATED`, and `NOT SEARCHED ≠ INADMISSIBLE`. Every rejection is logged with
its class, which is what makes the last distinction reportable at S7.7.

## 13. Knowledge policy

Knowledge may admit, reject, type or prioritise. **It may not count as validation
evidence.**

**Seeding firewall** — q_desc's seven coordinates, the retired q_rec support and
the dFL target-conditioned export may not seed `q_rec`; dFL features may not
serve as primitives. Each is firewalled for a distinct recorded reason.

## 14. Search bounds

Primitives, first derivatives, pairwise relational derivatives, pairwise
products and ratios. Relational depth 1. No triple products, no higher
derivatives, no free transcendental library.

**Support size 1–12.** Derived from calibration-sample economy on the worst
admissible grid: at 20 ms the smallest calibration interval holds 75 samples, so
12 coordinates is ~6 samples per coefficient — already thin given
autocorrelation.

**The REL10 coincidence is recorded explicitly**: 10 was not inherited, and 12
was derived from S7.1 temporal metadata with no reference to any prior result.

## 15. Utility

Lexicographic: fit → generalization/stability → parsimony → conditioning →
support stability.

**Practical equivalence:** one-SE rule **and** an absolute floor of 0.01
calibration-normalized RMSE. The floor exists because a one-SE rule alone
degenerated in this project's Lorenz benchmark (`SE ≈ 3e-7` collapsed every
equivalence set to a singleton, silently disabling parsimony).

No fabricated error weights — `E` is not instantiated.

## 16. Baselines

**B0** calibration mean · **B1** persistence · **B2** raw ridge linear ·
**B3** `HistGradientBoostingRegressor` — all fixed by name before any target
exists, all on identical geometry and identical admissible information.

Five outcome readings agreed in advance, including two that are honest negative
results. B0 is the baseline that defeated the retired q_rec.

## 17. Qualification gates

Ten gates **V1–V10**; **nine mandatory** (all but V9). If a mandatory gate
fails, `Q_rec` may not be presented as a successful structural transfer result.

V4 requires *fairness* of comparison, not victory. V3 requires actual skill —
the gate the retired q_rec failed.

## 18. Statistical inference

**Discharge is the inferential unit; n = 42 external.** Metrics per block →
aggregated within discharge → paired differences → paired discharge bootstrap
≥10,000 replicates → 95% CIs → win/tie/loss → LODO → split by era.

Explicitly forbidden: treating time samples as independent replicates; p-value
thresholds as gates; selective block/era/discharge reporting; post-hoc metric
substitution.

## 19. Domain and claim boundary

`Omega_rec_candidate` = the frozen 62-discharge object. `Omega_rec_final`
deferred; can only shrink.

Out of scope by name: all DIII-D, all regimes, other devices, control,
forecasting, causal structure, native high-frequency physics, diagnostic
bandwidth, universal relations.

## 20. Formal `K_rec^pre`

| Component | Status |
|---|---|
| `q_rec` | **FROZEN** |
| `I_rec` | **PARTIALLY_FROZEN** — policy frozen; instantiation → S7.3; closure → S7.5 |
| `P_rec` | **PARTIALLY_FROZEN** — invariants frozen; target closure → S7.3; instantiation → S7.6 |
| `B_rec` | **PARTIALLY_FROZEN** — depth rules frozen; counts → S7.5/S7.6; frontier → S7.7 |
| `H_rec` | **FROZEN** |
| `U_rec` | **FROZEN** — computation → S7.9 |
| `V_rec` | **PARTIALLY_FROZEN** — protocol frozen; evaluation → S7.10 |
| `Omega_rec` | **PARTIALLY_FROZEN** — candidate frozen; final → S7.10/S7.12 |

## 21. Unresolved human decisions

| # | Decision | When |
|---|---|---|
| 1 | Whether to attempt **EFIT lineage recovery** from the device archive. Resolving it would return up to 15 quantities to the primary boundary; not resolving it means fail-closed removes them for some targets. | before S7.3 |
| 2 | Whether a **`PROVENANCE_RELAXED` secondary variant** is wanted. Must be declared **before** results exist. | before S7.3 |
| 3 | The **primary target**, from the S7.3 eligible set. The eligibility rule is frozen; the final selection needs human sign-off. | S7.3 |
| 4 | Whether any **normally-excluded class override** is wanted (D-04). | S7.3 |
| 5 | Whether to **promote second-order derivatives** or **widen support beyond 12**. Both require recorded review and may not be justified by performance. | S7.5 |
| 6 | Whether to **correct the S7.1 freeze's mixed hash record** (§2). S7.2 works around it; the parent file still carries it. | advisory |

## 22. Files produced

31 artifacts, all hashed in `S7_2_FREEZE.json`. See `README.md` for the layout.

## 23. Reproduction

```powershell
cd D:\SIR_paper\DIIID_example
$P = "..\.venv_lorenz_benchmark\Scripts\python.exe"
$S = "S7\02_reconstruction_contract\scripts"
& $P $S\verify_s7_1_input.py
& $P $S\build_partition_and_validation.py
& $P $S\build_contract_and_freeze.py
```

Deterministic; no seeds. The verifier exits non-zero on parent-freeze drift.

## 24. Gate recommendation for S7.3

**`READY_FOR_S7.3`**, subject to human decisions 1 and 2 above, both of which are
better settled **before** S7.3 begins because they change which quantities the
instantiated boundary admits.

**S7.3 is not authorised by this document.**
