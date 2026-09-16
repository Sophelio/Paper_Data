# Known limitations

Stated plainly, because a reviewer needs them more than the headline numbers.

## 1. The staged manuscript is stale and has no source

No TeX exists for the main manuscript or the Supplement anywhere in
`D:\SIR_paper\`, and no `\releasepending` placeholder exists. The staged PDF
(2026-09-02) reports the **retired** `I_p` reconstruction branch: 16 occurrences
of `REL10`, zero of `cross-fitted` or `3451`. It also predates all five current
main-text figure assets.

Consequence: the figure allow-list could not be parsed from TeX. It was derived
from on-disk assets and **verified by tracing each script's declared output
stem**, which is stronger than filename matching but weaker than reading the
actual `\includegraphics` calls.

## 2. What the `q_rec` result does and does not establish

**Does:** within the predictor-qualified frozen 62-discharge object,
relational supports discovered without a discharge's own target values
reconstruct that discharge nontrivially relative to the frozen baselines.

**Does not:** external validation · future-discharge transfer · zero-shot
inference · a universal DIII-D relation · a unique equation · universal
coefficients.

Two limits travel with it. The margin over persistence is **modest and
era-asymmetric** (-0.0273 pooled; +0.0076 earlier vs -0.0726 later;
32-5-25 at discharge level). And predictor-side applicability was
instantiated from the **whole finite object**, so what was tested is transfer of
the target relationship, not of predictor geometry.

## 3. Support non-uniqueness

Six folds produced six **different** size-12 supports, union 35, mean
pairwise Jaccard 0.285244. A seventh full-object search produced a seventh
distinct support. No fold support is canonical, and the descriptive
`C_E2_ALL_DESC` is representative, not validated.

## 4. Coefficients are not physical constants

`q_desc` coefficients are locally calibrated per discharge. The verdict is
`D3D-MIXED-COEFFICIENT-IDENTIFIABILITY`: 5 of 7 robustly resolved, 2
uncertainty-dominated, 2 of 5 multivariate directions
resolved. `pcdiamag3` remains an uncalibrated signal wherever it appears.

## 5. Restricted source data is not bundled

The 62 resampled `.npz` archives (1.1 GB) are **not** in this package. They are
indexed with SHA-256 in
`03_DIII_D_SOURCE_OBJECT/source_access_notes/RESTRICTED_SOURCE_INDEX.csv`, and all
derived metadata is included. This is *not bundled because access is restricted*,
not *missing*. See `ACCESS_AND_LICENSE.md`.

## 6. Gaps recorded rather than papered over

- No `q_desc` explored-frontier record exists (the `q_rec` one is complete).
- No frozen paired-bootstrap interval for Δ₁; per-discharge Δⱼ is present, so it
  is computable.
- Spline and RTS numerical realizations are untied to a frozen run manifest.
- The Figure 1 script → asset mapping is **ambiguous**; both candidate scripts
  are bundled.

All are itemised in `90_AUDIT_REPORTS/missing_artifacts.csv` and
`ambiguous_artifacts.csv`.
