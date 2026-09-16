# Protected holdout prediction test

Frozen autonomous rollout of the SIR-discovered pendulum evolution law on
the 8 realizations withheld from discovery. SIR is **not** rerun here.

## Frozen primary model

From the 24 training realizations (run `20260820-175024-08c0`), pre-calibration:

```
d(theta_hat)/dt = 1.0 * omega_hat
d(omega_hat)/dt = -1.82245149 * sin(theta_hat)
```

`sin` is evaluated on the **predicted** angle. After `t = 0` the model is
closed: no observed `sin_theta`, no energy, no teacher forcing, no coefficient
refit.

## Audit-only model

Same ICs and solver with the generating coefficient `a = -1.8225`. This is
not the reported SIR result; it isolates phase drift from the ~4.85e-5
discovery bias.

## Holdouts

`pendulum_003, 007, 011, 015, 019, 023, 027, 031`

Each rollout is initialized from the first observed `(theta, omega)` only,
then integrated with DOP853, `rtol=1e-12`, `atol=1e-14` over `t ∈ [0, 30]`,
`dt = 0.01` (same grid as the dataset).

## Run

```
python run_prediction_holdouts.py
```

Writes `prediction_summary.json`, `prediction_metrics.csv`,
`trajectories/*.parquet`, and `audit/*.parquet`.

The reusable integrator is `prediction_model.rollout_from_observed` /
`integrate_frozen_model`. The dFL grapher **Held-out predictive phase portrait**
calls that same module.
