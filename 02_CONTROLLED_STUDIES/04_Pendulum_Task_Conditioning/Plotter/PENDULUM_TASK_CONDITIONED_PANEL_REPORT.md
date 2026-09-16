# Task-conditioned pendulum panel

Standalone publication panel for the Nature Computational Science manuscript
(intended as one panel of a two-panel main-text figure with heat degeneracy).

## Message

Same observational ensemble + different task contracts → different qualified models.

- **Compression:** \(\omega^2 = -3.645(1-\cos\theta)+2E_i\)
- **Prediction:** \(\dot\theta=\omega\), \(\dot\omega=-1.82245149\sin\theta\),
  autonomous holdout rollout from \(t=0\) only

## Design judgment

The prediction branch does **not** treat visual overlap of true vs predicted
phase portraits as the accuracy claim. A representative protected holdout
orbit is shown only to establish that the rollout stays on the correct
nonlinear libration orbit. Pooled RMSE vs horizon (log scale) is the
quantitative evidence.

## Representative trajectories

Compression: eight energy-spaced **discovery** realizations

`pendulum_000, 004, 008, 012, 016, 020, 024, 028`

(not the protected holdouts). Sorted by mechanical energy; color from
pale blue (low \(E\)) to dark green (high \(E\)).

Prediction inset: `pendulum_015` (mid-energy protected holdout). RMSE
curves are **pooled across all 8 holdouts** from the frozen
`Prediction_model/prediction_summary.json`.

## Frozen sources

- Raw parquet under `Pendulum/data/`
- `Prediction_model/trajectories/*.parquet`
- `Prediction_model/prediction_summary.json`
- Coefficients \(A=-3.645\), \(a=-1.82245149\), \(b=1.0\) are not refit

## Outputs

`D:\SIR_paper\Figures\figs\pendulum_task_conditioned_panel.{pdf,svg,png}`

Run:

```
python make_pendulum_task_conditioned_panel.py
```
