# fig5data — portable Figure 5 data package

Self-contained. `figure5_lorenz_representation_landscape_prototype.py` reads only
this directory and never touches the benchmark tree.

## Files

| File | Contents | Status |
|---|---|---|
| `canonical_recovery.json` | Lorenz parameters, recovered vs true cubic coefficients, per-term errors, run IDs, support verdict | canonical |
| `canonical_attractor.csv` | `times,x,y,z` for Panel a | regenerated (display-only ×10 downsample) |
| `representation_landscape.csv` | 17 candidates × 2 regimes: complexity, CV RMSE ± SE, conditioning, contract flags, Pareto status | canonical, **development CV** |
| `confirmation_trajectory_rmse.csv` | per-trajectory RMSE, 24 protected trajectories × 7 representations × 2 regimes | canonical, **protected confirmation** |
| `noise_robustness.csv` | canonical noise evidence — only σ ∈ {0, 0.01} exist in the frozen benchmark | canonical |
| `noise_robustness_augmented.csv` | dense sweep, trajectory level, native + common support | **augmentation** |
| `noise_robustness_summary.csv` | bootstrap summary of the dense sweep | **augmentation** |
| `selected_representations.json` | exact coordinate identities per contract, equivalent sets, complexity definitions | canonical |
| `PROVENANCE_MANIFEST.json` | per-file meaning, sources, generating script, hashes, checkpoints | — |
| `SOURCE_INVENTORY.md` | authoritative upstream source for every quantity | — |

## Canonical vs augmentation

Every row of every CSV carries `canonical_or_augmentation`.

**Canonical** — produced by the frozen benchmark, unmodified and not rerun.
**Augmentation** — generated for Figure 5 under
`task_conditioning_benchmark/fig5_augmentation/`, holding the scientific object,
information boundary, coordinate grammar, representations and estimator fixed,
and changing only the noise grid, the replicate count and the support scope.
The augmentation never replaces or masquerades as canonical evidence.

## Evidence levels — do not mix

- `development_grouped_CV` — the 17-candidate landscape. Search evidence over the
  48 exposed development trajectories, 6-fold GroupKFold. Panel b.
- `protected_confirmation` — the 24 independent trajectories, never used for any
  selection. Panels c and d.

Confirmation data were **not** used to choose any representation.

## Metric definitions

- **RMSE** — root-mean-square error reconstructing `z` from `x, y` only.
- **`n_coordinates`** — scientific coordinates in the representation `C`.
- **`n_features`** — columns supplied to the estimator after `R(C)`: equal to
  `n_coordinates` for identity families, **65** for the degree-2 baseline (10
  source coordinates expanded), **285** for degree-3.
- **`n_active_terms`** — non-zero STLSQ coefficients after thresholding.
- **`condition_number`** — 2-norm condition number of the standardised training
  design matrix. Comparable within a regime; **not** directly comparable across
  families with very different feature counts unless `n_features` is stated.
- **Support scope** — `native` uses each representation's own mask, so coverage
  differs (0.874–0.998) and representations are scored on *different rows*;
  `common` uses the intersection across the compared representations. Prefer
  `common` for any cross-representation claim.

## Contracts

| Contract | Utility | Selection |
|---|---|---|
| `q_accuracy` | minimum mean grouped-CV RMSE | `C_all` (38 coordinates) |
| `q_compact` | accuracy-equivalent set, then fewest coordinates → fewest terms → best conditioning → most stable | `C0+Q_pair` (12 coordinates) |
| `q_robust` | minimum worst-case CV RMSE over σ ∈ {0, 0.005, 0.01}, same hierarchy | `C_all` (38 coordinates) |

## Cohorts and noise

- Development: 48 trajectories (exposed; search and fitting).
- Confirmation: 24 trajectories, ensemble seed 20260827904, never used for selection.
- Noise: additive Gaussian on `x, y` at σ × the per-channel standard deviation,
  applied **before** every derivative, quotient, phase and scaling operation.
- Augmentation seeds: 5000+ namespace, disjoint from canonical 11/12/13 (development)
  and 901/902/903 (confirmation).

## Caveats

1. **Controlled ontology only.** The noise sweep holds the coordinate grammar and
   numerical realization fixed. It tests robustness *within* a declared ontology.
   It does **not** demonstrate adaptive-SIR ontology reconstruction, in which a
   new error model would rebuild derivative estimators, smoothers, regularization
   or admissibility.
2. **The clean case is near-degenerate.** `z` is almost exactly linear in the
   selected quotient coordinates, so clean RMSE saturates near 1e−5. Even 0.1%
   noise costs about four orders of magnitude. Clean numbers measure a near-exact
   algebraic identity rather than typical performance.
3. `Q[ẏ|x]` and `Q[y|x]` were exposed by an earlier benchmark; their selection
   here is not a first discovery.
4. Conditioning for the polynomial baseline is computed over 65 features and is
   not directly comparable to a 12-coordinate identity representation.
5. Fold-level per-candidate RMSE was not serialized upstream, so the landscape
   carries `se` and `fold_std` but not individual fold values.

## Regenerate

```powershell
cd D:\SIR_paper
$P = ".venv_lorenz_benchmark\Scripts\python.exe"
& $P Lorenz\task_conditioning_benchmark\fig5_augmentation\run_noise_sweep.py
& $P Lorenz\build_fig5data.py
& $P Lorenz\figure5_lorenz_representation_landscape_prototype.py
```

`build_fig5data.py` aborts if any canonical checkpoint drifts beyond tolerance or
the benchmark freeze is violated.
