# S7.2 — Claim boundary (summary card)

Full treatment: `DOMAIN_AND_CLAIM_BOUNDARY.md`. This page is the one-screen
version, for citation in figures, captions and review correspondence.

---

## The claim, in one sentence

> A relational coordinate **support** discovered on 20 development discharges of
> a frozen 62-discharge DIII-D archive remains useful on 42 unseen discharges of
> that same archive, when relation **coefficients** are calibrated locally from a
> declared calibration interval and the support itself is frozen beforehand.

## Domain

`Omega_rec_candidate` = the frozen 62-discharge object
`D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1`. `Omega_rec_final` can only be a
subset, fixed at S7.10.

## Transfer type

**Structural transfer with local calibration.** Support shared; coefficients
discharge-specific. **Not** zero-shot fixed-coefficient transfer.

## Task type

**Continuous reconstruction** from contemporaneous observations. **Not**
forecasting, event detection, classification, causal inference, or control.

## Inferential unit

**Discharge.** n = 42 external. Not time samples.

## Out of scope — do not claim

all DIII-D · all operating regimes · other devices · prospective control ·
forecasting · causal structure · native high-frequency physics · diagnostic
bandwidth · derivative structure near the archived resolution limit ·
universal plasma relations

## Three inherited limits that bound every result

1. **The object is the resampled archive**, not the native acquisition chain —
   upstream generator code is absent, and 18 signals were downsampled with no
   anti-aliasing.
2. **The 15 equilibrium quantities have unresolved ancestry**; fail-closed may
   remove all of them from the primary boundary.
3. **The cohort is not homogeneous** — two processing eras split at shot 189646;
   external results must be reported separately for each.

## The standard of success

A negative result under this contract is a valid, reportable outcome.
A positive result obtained by changing the contract is not.
