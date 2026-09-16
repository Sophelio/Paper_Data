# S7.1R-FINAL — Equilibrium lineage audit

Machine-readable: `equilibrium_lineage_nodes.csv`, `equilibrium_lineage_edges.csv`,
`equilibrium_lineage_status.csv`.

No target is selected here and no quantity is declared admissible or
inadmissible. This pass records ancestry only, in enough detail that S7.3 can
later propagate target dependence.

## The 15

`aminor`, `area`, `betan`, `drsep`, `kappa`, `li`, `q95`, `rmaxis`, `rsurf`,
`tribot`, `tritop`, `volume`, `zcur`, `zmaxis`, `zsurf`.

## Verdict

```
LINEAGE_RESOLVED    0
LINEAGE_PARTIAL    15
LINEAGE_UNRESOLVED  0
```

## What is now established

**The reconstruction family is EFIT.** The units registry names it explicitly in
two descriptions — *"Plasma minor radius (EFIT)"* and *"Plasma poloidal
cross-sectional area (EFIT)"*. This is `LOCAL_DOCUMENTED` for those two and
`STRONGLY_INFERRED` for the other thirteen by group coherence.

This is a genuine advance on the original S7.1 finding, which recorded the
reconstruction's identity as entirely unresolved.

Three facts support treating all 15 as outputs of one reconstruction:

- all 15 share a native cadence of **exactly 20.0 ms** across all 62 discharges;
- all 15 share an identical upstream resampling length ratio within each
  discharge;
- all 15 carry the same provider group label.

Every one now has a documented unit and a scientific definition — see
`equilibrium_lineage_status.csv`.

## What remains unresolved

For all 15: EFIT's **settings, inputs, constraints, fitting weights, and whether
the reconstruction was magnetics-only or kinetically constrained**. No code,
namelist, settings file, version string, or run record exists in any local tree.

Consequently **no edge from an input to the reconstruction is better than
`UNRESOLVED`**, and no edge in this graph is `CODE_VERIFIED` — there is nothing
local to verify against.

## On plasma-current ancestry

Under standard definitions `q95` and `betan` contain `I_p` explicitly, and EFIT
is normally constrained by measured plasma current, which would place `I_p`
upstream of all 15. Both statements are **external convention**, recorded as
`ip_appears_upstream = BY_DEFINITION_EXTERNAL` (2 signals) and
`STRONGLY_INFERRED_EXTERNAL` (13).

The Figure 6 audit reached a compatible conclusion independently, finding
`q95` approximately proportional to `shape * a^2 * B_t / I_p` with 7.3% residual
scatter across this cohort. That is a strong empirical result and it is
consistent with definitional ancestry — but **statistical agreement is not
admitted as proof of ancestry** here. That rule was adopted after an earlier
audit in this project demonstrated concretely that conflating the two produces
both false leakage findings and false clearances.

So: plasma-current ancestry is *very likely* and *not proven from the project's
own record*.

## Consequence for S7.2 / S7.3

All 15 carry `suitable_for_target_independence_decision = False`.

If a later stage adopts a target and an admissibility rule turning on upstream
dependence, that rule is **undecidable on present evidence** for these 15. Three
responses exist, and the choice belongs to the human reviewer:

1. recover the EFIT lineage from the device archive (resolves it);
2. treat the whole group as carrying plasma-current ancestry (conservative);
3. treat ancestry as unknown and exclude the group from any independence claim.

Option 2 is effectively what the Figure 6 audit adopted when it retired q_rec.

## A structural caveat that travels with these 15

They are the coarsest-sampled group in the object (20.0 ms native) and are
therefore **~4x oversampled** on the analysis grid, reaching ~16x in 2
discharges. Any derivative-valued coordinate built over them is governed by the
interpolant rather than by the reconstruction. This does not affect lineage
classification, but the ontology stage must not adopt such coordinates unaware.
