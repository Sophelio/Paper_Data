# S7.4 §4 — `vsurf` temporal-provenance audit

Machine-readable: `target_temporal_provenance.json`,
`vsurf_temporal_provenance.csv` (62 rows)

**Method:** frozen S7.1 metadata and the per-shot metadata sidecars only. **No
archive was opened; no signal value, development or external, was read.**

---

## Verdict

```
C_SOURCE_CADENCE_VARIES_BY_DISCHARGE
no_super_resolution_rule_satisfied = FALSE

-> TARGET_TEMPORAL_RESOLUTION_RECONCILIATION_REQUIRED
-> S7.4 STOPS. X_rec is NOT instantiated. S7.5 is NOT authorised.
```

## The three cadences, kept distinct

The word "native" was used ambiguously in earlier stages. Disentangled:

| Cadence | Definition | Value |
|---|---|---|
| **`SOURCE_SUPPORTED_CADENCE`** | archived support ÷ (source sample count − 1), where source count is the `original_length` the upstream pipeline received | **19.93 – 82.91 ms**, median 20.24, **varies by discharge** |
| **`ARCHIVED_CADENCE`** | median Δt of the archived `vsurf` time axis | **20.0 ms**, uniform in all 62 |
| **`ANALYSIS_CADENCE`** | S7.3 primary grid, set by the coarsest admitted quantity — which is `vsurf` itself | **20.0 ms** |

S7.3's "native cadence = 20.0 ms" was the **archived** cadence. It is not the
source-supported cadence, and the two differ.

## What `UPSTREAM_UPSAMPLED` actually means for `vsurf`

Not a bookkeeping detail.

`vsurf` was resampled by **`cubic_spline` in all 62 discharges**. In **36 of 62**
the archive contains *more* samples than the pipeline received (ratio > 1.01).
Those extra archived samples are **spline interpolations, not observations**.

| | |
|---|---|
| shots upsampled by > 1% | **36 / 62** |
| shots where source cadence is coarser than the 20 ms grid | **20 / 62** |
| — of which development | **7 / 20** |
| — of which external | 13 / 42 |
| worst discharge | `165027` — **56 source samples → 229 archived**, source Δt ≈ **82.9 ms** |
| worst development discharge | `165861` — 198 → 240, source Δt ≈ **24.3 ms** |

### The seven affected development discharges

| Shot | Source n | Archived n | Support (ms) | Archived Δt | **Source Δt** | Ratio |
|---|---|---|---|---|---|---|
| `165861` | 198 | 240 | 4780 | 20.00 | **24.26** | 1.21 |
| `160720` | 210 | 240 | 4780 | 20.00 | **22.87** | 1.14 |
| `165022` | 218 | 239 | 4760 | 20.00 | **21.94** | 1.10 |
| `160715` | 224 | 240 | 4780 | 20.00 | **21.43** | 1.07 |
| `170396` | 234 | 246 | 4900 | 20.00 | **21.03** | 1.05 |
| `195273` | 287 | 298 | 5940 | 20.00 | **20.77** | 1.04 |
| `165028` | 234 | 240 | 4780 | 20.00 | **20.52** | 1.03 |

## Why this blocks the stage

The frozen numerical-resolution policy states that **interpolation-created
samples are not independent observational evidence**, and requires the analysis
grid to be **no finer than the coarsest native cadence among admitted
quantities**.

S7.3 set the grid to 20.0 ms because `vsurf` is the coarsest admitted quantity at
20.0 ms *archived*. But in 20 of 62 discharges the target's **source-supported**
cadence is coarser than 20 ms. In those discharges the 20 ms analysis grid is
finer than the target can support, and a fraction of the target samples the study
would score against are spline output rather than measurement.

This is a **direct conflict with the no-super-resolution rule, on the target
itself** — the one quantity where interpolated samples matter most, because they
are what the reconstruction is scored against.

§4 is explicit: on outcome B or C with the grid finer than source support, stop
and return `TARGET_TEMPORAL_RESOLUTION_RECONCILIATION_REQUIRED`. Silently
redefining `X_rec` around it is forbidden.

## One important caveat, in the conservative direction

`original_length` is the length the **upstream pipeline received**, not
necessarily the raw diagnostic cadence. The pipeline generator is absent (U001).
The source-supported cadence computed here is therefore a **lower bound on
coarseness**: the true source could be coarser still, never finer.

The finding cannot be weakened by better information about U001. It can only get
worse.

## Second finding — flagged, not acted on

**`vsurf` shares the equilibrium group's time base exactly, in all 62
discharges.** Identical `original_length`, `resampled_length`, `t_start`,
`t_end` and `n_samples` as all 15 equilibrium quantities, in every discharge —
62/62, no exceptions.

That is a strong indication `vsurf` is carried on the same EFIT time base as the
15 quantities S7.3 excluded from its own boundary as `LINEAGE_PARTIAL`.

It does **not** prove `vsurf` is an EFIT output. Its registry description is
"Surface loop voltage" with no EFIT attribution, unlike `aminor` and `area` which
name EFIT explicitly, and its origin class is `DIRECT_MEASUREMENT` at
`STRONGLY_INFERRED` — inferred, not documented. The resampling *method* also
differs from the equilibrium group's within a shot.

But it raises a question S7.3 never asked, because `vsurf`'s class made it
unnecessary: **is `vsurf`'s own ancestry relative to the equilibrium
reconstruction resolved?** Under fail-closed the answer for the 15 was "no". If
`vsurf` sits on their time base, the same question applies to the target.

**I have not acted on this.** S7.4 may not rerank targets or change `I_rec`. It
is recorded here as a second item for the reconciliation, and it is logically
independent of the temporal finding: resolving one does not resolve the other.

## What reconciliation would need to decide

Not decided here — these are the options the finding leaves open, listed so the
reconciliation has somewhere to start:

1. **Coarsen the analysis grid** to the worst source-supported cadence in the
   evaluated cohort. Expensive: 82.9 ms in the worst external discharge would
   gut the sample counts, and S7.2's validation-feasibility audit was never run
   at that cadence.
2. **Per-discharge cadence** at each discharge's own source support. Breaks the
   single-grid assumption that the frozen validation geometry and the shared-
   support gate V7 rest on.
3. **Restrict `Omega_rec`** to discharges whose source support is consistent with
   20 ms — 42 of 62, and only 13 of 20 development. Changes the cohort, which
   is frozen.
4. **Re-open target selection** under a corrected cadence definition. The runner-
   up `density` has 1 ms archived cadence and was not upsampled; the ranking was
   resolved at Level 4 by a margin of 0.081, so a corrected feasibility
   computation could plausibly change the winner.
5. **Accept and qualify** — declare O as the archived object and state that a
   fraction of target samples are interpolated. This is the weakest option and
   sits uneasily with a rule the contract states in absolute terms.

Option 4 interacts with the second finding: if `vsurf`'s EFIT relationship is
also unresolved, both point the same way.

**The choice is a human decision and is outside S7.4's authority.**
