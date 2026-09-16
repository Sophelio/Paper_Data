# S7.2 — Contract decision ledger

Every material decision, with what was known and what was deliberately not
consulted. The point of this document is to make it checkable that the
experiment was **not** tuned after seeing its outcome.

**Nothing in this ledger was informed by any target, any model, or any
reconstruction result. None exists.**

---

## D-01 · Continuous reconstruction, not event classification

**Question.** What task class should `q_rec` be?
**Options.** continuous reconstruction · ELM detection · event classification ·
forecasting · control.
**Selected.** Continuous reconstruction of a scalar quantity from
contemporaneous observations.
**Reason.** The archive contains **no ELM or event annotations at all** (S7.1),
so any event task would require importing an unresolved label pipeline. A
continuous target also keeps reviewers out of plasma-event taxonomy, which is
not where the novelty lies.
**Evidence at decision time.** S7.1 component `A`: no event annotations present.
**Not consulted.** Any target; any signal values.
**Affects.** All stages. **Reversible?** No — this defines the study.
**Human review?** No.

## D-02 · Structural transfer with local calibration, not zero-shot

**Question.** What transfers between discharges?
**Options.** zero-shot fixed coefficients · structural transfer with local
calibration · full per-discharge refit.
**Selected.** Support shared and frozen; coefficients discharge-specific.
**Reason.** Zero-shot would be a stronger claim that discharges' differing
configurations would defeat for reasons unrelated to representation quality.
Full refit would be vacuous. Freezing the *support* keeps a real constraint
while making the claim honest.
**Evidence.** S7.1: 7 operational periods, 2 processing eras — the cohort is
heterogeneous.
**Not consulted.** Any performance under either regime.
**Affects.** S7.9, S7.10. **Reversible?** No. **Human review?** No.

## D-03 · Fail-closed provenance

**Question.** How to treat unresolved ancestry relative to the target?
**Options.** admit (fail-open) · exclude (fail-closed) · admit with a flag.
**Selected.** **Fail-closed** — unresolved ancestry is not independence-certified
and leaves the primary boundary.
**Reason.** Absence of proof of dependence is not proof of independence. The
Figure 6 audit retired the previous q_rec partly for admitting features carrying
plasma-current ancestry.
**Cost, accepted in advance.** If the target makes their ancestry unresolvable,
**all 15 equilibrium quantities leave the primary boundary.**
**Evidence.** S7.1: 15 quantities `LINEAGE_PARTIAL`; EFIT settings absent.
**Not consulted.** Whether excluding them would help or hurt.
**Affects.** S7.3, S7.5, gate V1. **Reversible?** Only by resolving the lineage.
**Human review?** Yes, if a `PROVENANCE_RELAXED` variant is wanted.

## D-04 · Target eligibility classes

**Question.** Which origin classes may host the primary target?
**Selected.** Eligible: `DIRECT_MEASUREMENT` and `DIAGNOSTIC_RECONSTRUCTION`
with resolved unit. Normally excluded: actuation, equilibrium-derived,
uncalibrated raw, event labels.
**Reason.** Actuation commands describe the control system, not the plasma;
equilibrium quantities carry unresolved ancestry; uncalibrated signals have no
unit, so reconstruction error is uninterpretable.
**Consequence, noted deliberately.** This excludes **`pcdiamag3`**, one of the
historical eight and the target of the retired dFL export.
**Evidence.** S7.1 origin classification; units registry `uncalibrated` status.
**Not consulted.** Any target's reconstructability.
**Affects.** S7.3. **Reversible?** Yes, with recorded justification not
referencing performance. **Human review?** Yes for any override.

## D-05 · Target-history exclusion

**Question.** May lagged target values serve as predictors?
**Selected.** **No.** The target may not appear among its own predictors at any
lag.
**Reason.** Autoregression would make the task trivially easy and would convert
a representational claim into a smoothness claim. Persistence baseline **B1**
already measures exactly what target history contributes.
**Not consulted.** Any autocorrelation statistic.
**Affects.** S7.3, S7.5. **Reversible?** No. **Human review?** No.

## D-06 · Cohort split policy

**Question.** How to partition development and external?
**Options.** random with seed · stratified deterministic · era-blocked ·
period-blocked.
**Selected.** Deterministic stratified — within each period, take `i % 3 == 1`.
20 development / 42 external.
**Reason.** Deterministic needs no seed and is reproducible from the shot list.
Stratifying by period balances both eras (dev 55/45, ext 57/43 against the
object's 56/44). ~1/3 : 2/3 keeps the external cohort at 42, and since discharge
is the inferential unit, that **is** the effective sample size.
**Evidence.** S7.1: shot IDs, 7 periods, era split at 189646.
**Not consulted.** Any signal value; the archives were never opened.
**Affects.** S7.3 onward. **Reversible?** No — frozen and hashed.
**Human review?** No.

## D-07 · Singleton period to external

**Question.** Where does period 1 (one discharge, 155537) go?
**Selected.** External.
**Reason.** It cannot be split. The external cohort tests the generalisation
claim and benefits more from covering all 7 periods; development loses only a
singleton and still covers 6.
**Not consulted.** Anything about shot 155537's values.
**Affects.** Coverage reporting. **Reversible?** No. **Human review?** No.

## D-08 · Rolling validation blocks

**Question.** What within-discharge validation geometry?
**Options.** final-20% (retired) · k-fold in time · rolling origin 40/60/80 →
10% · random blocks.
**Selected.** Rolling origin, three blocks: calibration `[0,0.4)`/`[0,0.6)`/
`[0,0.8)`, protected `[0.4,0.5)`/`[0.6,0.7)`/`[0.8,0.9)`.
**Reason.** The retired final-20% protocol was degenerate —
`var(eval)/var(calib) = 0.0032`, so a constant predictor won. Distributing three
protected blocks through the trajectory removes that artifact. Leaving
`[0.9,1.0]` unscored avoids end-of-discharge behaviour.
**Evidence.** Feasibility audited at all 7 native cadences: **186/186 feasible**,
worst case (20 ms) ≥18 protected and ≥75 calibration samples. Used only common
window durations from S7.1 — no signal values.
**Not consulted.** Any target value; any target's temporal behaviour.
**Affects.** S7.9, S7.10. **Reversible?** No. **Human review?** No — feasible as
specified, so no alternative was needed.

## D-09 · Baseline set

**Question.** What must the representation be compared against?
**Selected.** B0 calibration mean · B1 persistence · B2 raw ridge linear ·
B3 `HistGradientBoostingRegressor`.
**Reason.** The retired q_rec was beaten by a constant predictor — discovered
*after* the fact. Freezing the ladder now makes that failure mode detectable and
non-negotiable. B2 isolates the contribution of relational construction on
identical information; B3 tests against a competent off-the-shelf nonlinear
learner.
**B3 fixed by name now** so it cannot be chosen by running comparisons.
**Not consulted.** Any performance of any estimator.
**Affects.** S7.10, gates V3/V4. **Reversible?** No. **Human review?** No.

## D-10 · Unit canonicalization before construction

**Question.** How are the three unit-scale traps handled?
**Selected.** Canonicalise to SI (eV retained for temperature) **before** any
constructor runs; dimensional checking at construction; z-scoring never relied
on to hide mismatch.
**Reason.** S7.1 found `pinj` kW vs `pinj_*` W (10³), `density` cm⁻³ vs
`prmtan_neped` m⁻³ (10⁶), `ece*` keV vs `cerqtit*` eV (10³). All invisible under
within-discharge z-scoring, and all become live the moment a coordinate crosses
a pair.
**Not consulted.** Which coordinates would be affected in practice.
**Affects.** S7.5. **Reversible?** No. **Human review?** No.

## D-11 · Numerical-resolution policy

**Question.** What analysis grid?
**Options.** fixed-N 1000 (historical) · coarsest admitted native cadence ·
finest native cadence.
**Selected.** **No finer than the coarsest native cadence among admitted
quantities.**
**Reason.** Fixed-N manufactures resolution: equilibrium at 20 ms native on a
~5 ms grid is ~4× interpolated (~16× in 2 discharges), and the provider
block-averages denser signals but *interpolates* sparser ones. The coarsest-dt
rule removes that asymmetry. The full 95-signal provider already implements it.
**Cost, accepted.** Admitting any equilibrium quantity forces a ~20 ms grid on
the whole task.
**Evidence.** S7.1 temporal lineage; validation feasible at 20 ms.
**Not consulted.** Which grid gives better reconstruction.
**Affects.** S7.5, S7.9. **Reversible?** No for the primary path; fixed-N is
allowed only for labelled comparability runs. **Human review?** No.

## D-12 · Derivative-order bound

**Question.** What temporal derivative orders are admissible?
**Selected.** First order at most. Second and higher **presumed inadmissible**.
Derivatives of upstream-upsampled signals excluded or flagged
`NUMERICAL_SENSITIVITY_ONLY`. Equilibrium derivatives restricted to grids no
finer than 20 ms.
**Reason.** A derivative cannot carry resolution its source lacks. S7.1 found 16
signals upsampled upstream (14 of 15 equilibrium plus `vsurf`, up to 4.09×) and
18 downsampled with no anti-aliasing.
**Not consulted.** Whether higher derivatives would improve fit.
**Affects.** S7.5. **Reversible?** Yes, by recorded human review — never by
performance. **Human review?** Yes for any promotion.

## D-13 · Relation complexity bound

**Question.** How large may the representation be?
**Selected.** Support size **1–12**; relational depth 1; pairwise products and
ratios only; no transcendental library.
**Reason.** 12 derives from calibration-sample economy on the worst admissible
grid: at 20 ms the smallest calibration interval across all 62 discharges holds
**75 samples**, so 12 coordinates is ~6 samples per coefficient — already thin,
and time samples are autocorrelated so the effective count is lower.
**Recorded explicitly.** The retired model was named REL10. **10 was not
inherited**, and 12 was derived independently from S7.1 temporal metadata.
**Not consulted.** Any representation's performance at any size.
**Affects.** S7.5–S7.7. **Reversible?** By recorded human review.
**Human review?** Yes to widen.

## D-14 · Processing-era handling

**Question.** How is the 35/27 discontinuity handled?
**Selected.** Both eras represented in both cohorts by construction;
**mandatory gate V6** requires external results reported separately by era.
**Reason.** S7.1 found a clean upstream processing split at shot 189646 —
`ip` resampled by `cubic_spline` in all 35 earlier discharges and
`decimate_with_antialiasing` in all 27 later — corroborated independently by the
units registry's 35/62–27/62 unit-string variants. A result holding in one era
only is a finding, not something to average away.
**Not consulted.** Whether results differ by era.
**Affects.** S7.10. **Reversible?** No. **Human review?** No.

## D-15 · Inferential unit

**Question.** What is the independent replicate?
**Selected.** **Discharge.** n = 42 external. Paired discharge bootstrap,
≥10,000 replicates.
**Reason.** Time samples within a discharge are strongly autocorrelated and many
are interpolated from the same underlying observation. Treating them as
independent would inflate significance by orders of magnitude — the most common
way a study of this shape overstates itself.
**Not consulted.** Any variance estimate from any model.
**Affects.** S7.10. **Reversible?** No. **Human review?** No.

## D-16 · Sibling-channel rule

**Question.** What if the target has same-family neighbours?
**Selected.** Primary boundary **excludes** same-family siblings; the
full-boundary variant is a **declared sensitivity**.
**Reason.** Reconstructing `ece20` from `ece19` and `ece21` is spatial
interpolation and says almost nothing about relational structure. Freezing both
variants now prevents choosing afterwards whichever flatters the result.
**Not consulted.** Any sibling correlation.
**Affects.** S7.3, S7.5. **Reversible?** No. **Human review?** No.

## D-17 · Practical-equivalence floor

**Question.** When are two representations equivalent?
**Selected.** One-standard-error rule **and** an absolute floor of **0.01**
calibration-normalized RMSE.
**Reason.** A one-SE rule alone degenerates when SE is tiny — in this project's
Lorenz task-conditioning benchmark, `SE ≈ 3e-7` collapsed every equivalence set
to a singleton and silently made parsimony inoperative. The floor prevents that.
0.01 is 1% of calibration-interval target scale, below scientific relevance.
**Not consulted.** Any observed difference between any representations.
**Affects.** S7.7, S7.9. **Reversible?** No — fixed before search.
**Human review?** No.

## D-18 · Estimator choice

**Question.** What relation estimator?
**Selected.** Transparent linear — OLS or ridge with a development-selected
penalty, intercept fitted.
**Reason.** Utility should be attributable to the **representation**, not the
estimator; a strong estimator makes a positive result ambiguous. An intercept is
fitted because this project's Lorenz benchmark established that a no-intercept
estimator silently destroys performance on an uncentred target.
**Not consulted.** Any estimator's performance here.
**Affects.** S7.9, S7.10. **Reversible?** Only for recorded conditioning
reasons, never performance. **Human review?** Yes for any departure.

## D-19 · Seeding firewall

**Question.** May prior supports inform `q_rec`?
**Selected.** **No.** q_desc's seven coordinates, the retired q_rec support and
the dFL export are all firewalled. dFL features may not be used as primitives.
**Reason.** q_desc solved a different contract against a different target;
retired q_rec failed for provenance and triviality; the dFL export is
target-conditioned (`pcdiamag3_none_…`) and holds z-scored derived coordinates,
not primitive observations. Importing any of them would smuggle a target
decision or a solved answer into the search.
**Not consulted.** The contents of any of the three.
**Affects.** S7.5–S7.7, gate V2. **Reversible?** No. **Human review?** No.

## D-20 · S7.1 hash-method defect

**Question.** The parent freeze recorded hashes under two different rules. Stop,
or proceed?
**Selected.** Proceed. Verify under both rules, require one to match, record the
defect, and emit a uniform `canonical_raw_byte_hashes` set for later stages.
**Reason.** The files are **unmodified** — all nine verify. The defect is in
record-keeping, not data: artifacts built in memory were hashed as written,
while `FINAL_SIGNAL_INVENTORY.csv` and `signal_quality_summary.csv` were re-read
with `pd.read_csv` first, which reformats floats. A verifier applying either
rule uniformly reports false drift on the other subset.
**Not consulted.** Nothing — this is a bookkeeping matter.
**Affects.** All later verification. **Reversible?** n/a.
**Human review?** Advisory: the S7.1 freeze file was deliberately **not**
modified, so the mixed record persists there.
