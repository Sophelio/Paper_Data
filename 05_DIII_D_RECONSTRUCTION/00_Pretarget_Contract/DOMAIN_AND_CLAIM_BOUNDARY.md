# S7.2 — Claim domain `Omega_rec` and claim boundary

## `Omega_rec_candidate` — FROZEN

> **The frozen 62-discharge DIII-D observational object
> `D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1`.**

This is the **maximum** initial domain. Nothing larger is available, and nothing
larger may be claimed.

## `Omega_rec_final` — DEFERRED

The final domain is a subset of the candidate domain: the target-admissible
discharges that survive target feasibility (S7.3) and provenance closure, and on
which external evaluation is actually performed (S7.10).

It can only shrink. Any discharge dropped is recorded with a reason that is
**not** connected to results.

---

## The claim boundary

### What may be claimed

- **Relational analysis of the frozen archived object.** Statements about
  structure in these 62 discharges as archived.
- **Comparisons among coordinates constructed from that object**, under the
  frozen contract.
- **Reproducible downstream processing** from the archive forward.
- **Structural transfer with local calibration** — that a support discovered on
  development discharges remains useful on unseen discharges from this cohort
  when coefficients are locally calibrated.

### What may not be claimed

| Not claimed | Why |
|---|---|
| **all DIII-D operations** | parent population and selection algorithm unresolved; the 62 are a finite convenience object, not a sample |
| **all operating regimes** | no regime labels exist; assigning them would be inference, not record |
| **unseen devices** | nothing in the object supports cross-device transfer |
| **prospective control** | no actuation decision is proposed or evaluated |
| **forecasting** | predictors are contemporaneous; nothing is predicted forward |
| **causal structure** | provenance closure establishes ancestry, not causation |
| **native high-frequency physics** | the object is the resampled archive; 18 signals were downsampled with no anti-aliasing |
| **exact diagnostic bandwidth** | upstream resampling generator code is absent |
| **derivative structure near the resolution limit** | interpolation-created resolution is not observational evidence |
| **universal plasma relations** | the domain is 62 discharges |

### Why the object-scoping is load-bearing

O is the **frozen archived and resampled** object, not the native DIII-D
acquisition chain. That scoping is what makes the claim defensible despite an
unresolved upstream pipeline: the study is about a well-defined object it fully
possesses, and it says so.

The cost is that any statement requiring the *native* signal — bandwidth,
high-frequency structure, exact diagnostic response — is out of scope. Those are
not weaknesses in the analysis; they are outside the object it analyses.

## Generalisation and cohort structure

The cohort spans **seven operational periods** with **two upstream processing
regimes** (35 earlier, 27 later, splitting at shot 189646). Any claim of
cross-discharge generality must contend with that discontinuity, which is why
gate **V6** requires external results reported separately by era.

If a result holds in one era and not the other, that is a finding about the
processing discontinuity, and must be reported as such rather than averaged away.

## Statistical scope

**Discharge is the independent inferential unit.** With 42 external discharges
the effective sample size is 42 — not the tens of thousands of time samples they
contain, which are strongly autocorrelated. Confidence statements are made at
discharge level and nowhere else.

## Deferred

- **S7.3:** target-admissible discharge subset.
- **S7.10:** discharges actually evaluated.
- **S7.12:** `Omega_rec_final` with the qualified result.
