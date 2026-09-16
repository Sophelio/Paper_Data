# S7.1R Issue 3 — Equilibrium reconstruction lineage

**Scope:** the 15 equilibrium / shape quantities.
**Data:** `equilibrium_lineage_nodes.csv`, `equilibrium_lineage_edges.csv`,
`equilibrium_lineage_status.csv`.

No target is selected here and no predictor is classified as admissible or
inadmissible. This pass establishes only what can and cannot be said about where
these 15 quantities came from.

## 1. The 15 quantities

`aminor`, `area`, `betan`, `kappa`, `li`, `q95`, `volume`, `drsep`, `tritop`,
`tribot`, `rmaxis`, `zmaxis`, `rsurf`, `zsurf`, `zcur`.

## 2. Verdict

**All 15 are `LINEAGE_PARTIAL`. None is `LINEAGE_RESOLVED`.**

What is established:

- All 15 belong to the group the full provider's docstring labels
  `Equilibrium / shape`. This is the only local documentary statement about
  their origin, and it is group-level.
- All 15 share a **single native cadence of exactly 20.0 ms**, measured across
  all 62 discharges. A shared cadence to that precision is strong evidence that
  they are outputs of one reconstruction evaluated on one time base, rather than
  independently produced quantities.
- All 15 share an identical upstream resampling length ratio within each
  discharge (median 1.0119, identical across the group per shot), which
  corroborates single-producer origin.

What is **not** established, for any of the 15:

- the identity of the reconstruction code (no code, settings file, run record,
  namelist, or version string exists in any local tree);
- its inputs;
- its constraints or fitting weights;
- whether any archived quantity is itself an input to the reconstruction that
  produced the others;
- whether the reconstruction is magnetics-only or kinetically constrained.

## 3. Why `I_p` ancestry cannot be settled here

Under the standard definitions, `q95` and `betan` contain `I_p` explicitly, and
an equilibrium reconstruction is normally constrained by measured plasma
current, which would place `I_p` upstream of all 15. Both statements are
**external convention**, not local evidence. They are recorded in
`equilibrium_lineage_status.csv` as `ip_appears_upstream =
STRONGLY_INFERRED_EXTERNAL`.

The Figure 6 audit reached a compatible conclusion by an independent route,
finding `q95 ≈ shape·a²B_t/I_p` to hold with 7.3% residual scatter across this
cohort. That is a strong empirical result and it is consistent with definitional
ancestry — but the rule adopted in S7.1, and retained here, is that
**statistical agreement is not admitted as proof of ancestry**. The earlier
provenance audit in this project demonstrated concretely that conflating the two
produces both false leakage findings and false clearances.

So: `I_p` ancestry for the equilibrium group is *very likely* and *not proven
from the project's own record*.

## 4. Consequence for a later admissibility rule

Recorded in `equilibrium_lineage_status.csv` as
`suitable_for_target_independence_decision = False` for all 15.

If a future stage adopts a target and an admissibility rule turning on upstream
dependence, that rule will be **undecidable on present evidence** for these 15
quantities. Three responses are available, and the choice belongs to the human
reviewer at S7.2, not to this pass:

1. recover the reconstruction lineage from the device archive (resolves it);
2. treat the whole group as carrying `I_p` ancestry (conservative; costs 15
   quantities if the target is `I_p`-related);
3. treat ancestry as unknown and exclude the group from any claim that depends
   on independence (most conservative).

Option 2 is what the Figure 6 audit effectively adopted when it retired q_rec.

## 5. A structural fact recovered in this pass

The equilibrium group is **the coarsest-sampled group in the object** at 20.0 ms
native, roughly 1000× slower than the filterscopes at 0.02 ms. On the
paper-facing analysis grid (median 4.96 ms) these 15 quantities are therefore
**oversampled by ~4×**: four of every five grid points are interpolation, not
measurement.

In 2 of 62 discharges the upstream pipeline had *already* upsampled them
(length ratio up to 4.09), so in those shots the compounded interpolation factor
approaches ~16×.

This does not affect lineage classification, but it bears directly on any
derivative-valued coordinate built from equilibrium quantities: at 4× oversampling,
a finite-difference or spline derivative is dominated by the interpolant rather
than by the reconstruction. It is recorded here so that the ontology stage cannot
adopt such coordinates unaware. See `TEMPORAL_GRID_RECONCILIATION_REPORT.md` §5.

## 6. Graph contents

`equilibrium_lineage_nodes.csv` — 22 nodes: 15 equilibrium outputs
(`LINEAGE_PARTIAL`), one reconstruction node (`LINEAGE_UNRESOLVED`, identity
unknown), six presumed-input nodes (`LINEAGE_UNRESOLVED`, external convention
only, two of which — measured `I_p` and toroidal field — may correspond to
archived `ip` and `bt` but are not verified to).

`equilibrium_lineage_edges.csv` — 18 edges. The 15 reconstruction→output edges
carry `STRONGLY_INFERRED` (group docstring). The 3 input→reconstruction edges
carry `UNRESOLVED` and are explicitly annotated *"NOT verified for this
pipeline"*.

No edge in this graph is `CODE_VERIFIED`, because no code exists locally to
verify against.
