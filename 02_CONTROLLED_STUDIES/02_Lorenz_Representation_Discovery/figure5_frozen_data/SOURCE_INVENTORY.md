# Source inventory — Figure 5 data package

Authoritative upstream source for every quantity used in Figure 5.
`B/` = `D:\SIR_paper\Lorenz\task_conditioning_benchmark\`

## Canonical (frozen benchmark, read-only)

| Quantity | Upstream source | Notes |
|---|---|---|
| Lorenz parameters σ=10, ρ=28, β=8/3 | `B/benchmark_config.yaml` → `system:` | also asserted in the benchmark test suite |
| Recovered cubic coefficients, run IDs, final errors | `B/sir_mcp/containment/mcp_containment.json` | SIR MCP native runs `20260827-1722*` |
| Max coefficient deviation 2.000e−3 | computed from the above | from `dy/dt`: 27.998 vs 28 |
| 17-candidate landscape (CV RMSE, SE, fold std, conditioning, complexity) | `B/tables/selection_stability.csv` | 34 rows = 17 candidates × 2 regimes |
| Contract selections, equivalent sets, coordinate identities | `B/contracts/contract_selections.json` | frozen pre-confirmation |
| Per-trajectory confirmation RMSE | `B/tables/confirmation_per_trajectory.csv` | 336 rows = 24 traj × 7 reps × 2 regimes |
| Native coverage per representation | `B/tables/confirmation_results.csv` | 0.874–0.998, **not** common |
| 48 development trajectory hashes | `B/prior_benchmark_reference/imported_hashes.json` | referenced, never copied |
| 24 confirmation trajectory hashes, seeds | `B/shared/manifests/confirmation_lineage.json` | ensemble seed 20260827904 |
| Freeze integrity | `B/PRECONFIRMATION_FREEZE.json` | 12 files, verified at build time |

## Regenerated (deterministic, documented)

| Quantity | How | Why |
|---|---|---|
| Lorenz attractor for Panel a | `Lorenz_attractor.generate_lorenz(dt=0.001, tmax=40, x0=(1,1,1))`, DOP853, rtol=atol=1e−12 | no serialized attractor exists upstream; regeneration is bit-deterministic. Downsampled ×10 **for display only** |

## Augmentation (Figure-5 specific — NOT the frozen benchmark)

| Quantity | Source | Notes |
|---|---|---|
| Dense noise sweep, trajectory level | `B/fig5_augmentation/noise_sweep_trajectory_level.csv` | 4464 rows: 11 σ levels × up to 3 replicates × 3 representations × 24 trajectories × 2 support scopes |
| Augmentation design, seeds, held-fixed list | `B/fig5_augmentation/AUGMENTATION_MANIFEST.json` | seed namespace 5000+, disjoint from canonical |
| Common-support evaluation | same | added because canonical scoring used **native** per-representation masks |

## Quantities deliberately NOT used

| Quantity | Why |
|---|---|
| MLP results (`B/tables/mlp_comparators.csv`) | secondary sensitivity; kept out of the main figure per the design brief |
| `coverage` column of `selection_stability.csv` | stride-8 selection-subsample artifact (~1/8 of native); exported under a renamed column and not plotted |
| Fold-level per-candidate RMSE | not serialized upstream — only `fold_std` survives |

## Discrepancies found against the benchmark report

1. **Coverage is not common, and the report overstates it.**
   `TASK_CONDITIONING_BENCHMARK_REPORT.md` §16 states 88.5% coverage for all four
   representations. Actual confirmation coverage is 0.874 (`C_all`), 0.941
   (compact), 0.998 (poly2 / raw / cubic). The 88.5% value is development-level
   coverage for `C_all`, not a common support. Consequence: `C_all` is scored
   after discarding 12.6% of samples while the quadratic baseline discards 0.17%,
   so it could benefit from dropping difficult samples. The augmentation adds a
   **common-support** scope, and the figure uses it for cross-representation
   claims.

2. **Strided coverage column.** `selection_stability.csv::coverage` ≈ 0.11–0.12
   is the stride-8 CV subsample, not a retained fraction. Exported as
   `coverage_selection_strided` so it cannot be misread.

3. **Complexity is ambiguous across families.** The quadratic baseline has 10
   scientific coordinates but 65 estimator features; plotting it as "10" against
   `C_all`'s 38 would misstate the comparison. Three distinct notions are
   exported (`n_coordinates`, `n_features`, `n_active_terms`) and the figure
   states which axis it uses.
