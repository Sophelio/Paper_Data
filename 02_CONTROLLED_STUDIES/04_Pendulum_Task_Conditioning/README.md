# Autonomous nonlinear pendulum

Controlled numerical example for the SIR paper. **One canonical observational
dataset** is used for two later task contracts (compression / description vs
prediction / evolution). This folder is data + Dalia integration only; SIR
searches are not run here.

## Equations

\[
\frac{\mathrm{d}\theta}{\mathrm{d}t}=\omega,\qquad
\frac{\mathrm{d}\omega}{\mathrm{d}t}=-\omega_0^2\sin\theta
\]

with \(\theta\) = angular displacement (rad, **not** wrapped to \([0,2\pi]\)),
\(\omega=\mathrm{d}\theta/\mathrm{d}t\) (rad/s), and fixed

\[
\omega_0=1.35\,\mathrm{s}^{-1},\qquad \omega_0^2=1.8225\,\mathrm{s}^{-2}.
\]

Conserved energy (audit / ground truth only):

\[
E=\tfrac12\omega^2+\omega_0^2\bigl(1-\cos\theta\bigr).
\]

The separatrix is \(E=2\omega_0^2\). Realizations are librations with

\[
0.08 < E_i/(2\omega_0^2) < 0.90.
\]

## Numerical integration

| | |
|---|---|
| Solver | `scipy.integrate.solve_ivp`, method **DOP853** |
| `rtol` | `1e-12` |
| `atol` | `1e-14` |
| Grid | \(t\in[0,30]\) s, \(\Delta t=0.01\) s (3001 samples, identical for every file) |
| dtype | float64 |
| Seed | `20260820` |
| IC design | Latin hypercube in \((\theta_0,\omega(0))\in[-2.4,2.4]\times[-1.2,1.2]\), 2048 draws, then 8 energy-spaced points in each sign quadrant (32 total) |

## Files

```
Pendulum/
  generate_pendulum_data.py
  pendulum_coordinates.py      shared raw/virtual coordinate helpers
  pendulum_data_provider.py    SIR-web get_provider() contract
  data_provider.py             Dalia get_provider() contract
  custom_graphs.py
  manifest.csv
  data/pendulum_000.parquet … pendulum_031.parquet
  qc/pendulum_dataset_qc.png
  qc/pendulum_qc_report.json
  tests/test_pendulum_provider.py
```

Format is **Parquet**, matching Heat / Lorenz / Stochastic oscillator (not NetCDF).
See `IMPLEMENTATION_NOTES.md`.

### RAW OBSERVATIONS (on disk)

`times`, `theta`, `omega`

Realization metadata (`realization_id`, `theta0`, `omega_init`, `omega0`,
`energy_initial`, `dt`, solver settings, `generator_version`) is stored as
Parquet schema metadata and in `manifest.csv`, **not** as searchable channels.

### DETERMINISTIC DERIVED COORDINATES (provider virtual, not on disk)

| Name | Definition |
|---|---|
| `sin_theta` | \(\sin\theta\) |
| `cos_theta` | \(\cos\theta\) |
| `one_minus_cos_theta` | \(1-\cos\theta\) |
| `omega_squared` | \(\omega^2\) |

These are synthesized in both providers (`fetch_data` /
`fetch_identifier_variables` / `fetch_data_sir` and the selectable-variable
lists). Dalia Data Maker is **not** used for them: built-in transform blocks
have no `sin`/`cos`/`x^2`, and SIR variables come from the provider.

### GROUND TRUTH USED ONLY FOR AUDIT (not selectable)

\(\omega_0\), analytic ODE RHS, \(E_i\) / energy drift. `energy_true` is
**refused** if requested.

## Dalia-visible / SIR-selectable variables

`theta`, `omega`, `sin_theta`, `cos_theta`, `one_minus_cos_theta`, `omega_squared`

`times` is the time axis, not a model variable.

## Load in Dalia

1. Dalia Home should list **Pendulum** from the shared store
   `D:\SIR_paper\.dalia\projects\` (`DALIA_PROJECTS_DIR`).
2. Open **Pendulum**, confirm the data source is `D:\SIR_paper\Pendulum\data`.
3. Reload the provider if the catalog is stale.
4. Record ids are `pendulum_000` … `pendulum_031`.

If Dalia is not pointed at that store:

```powershell
$env:DALIA_PROJECTS_DIR = "D:\SIR_paper\.dalia\projects"
powershell -ExecutionPolicy Bypass -File D:\dalia\scripts\run.ps1
```

There is no extra registry beyond those JSON documents.

## Future SIR tasks (not run here)

Prediction / evolution (`output_type` must be the exact string **`Derivative`**):

- target \(\theta\) → expect \(\mathrm{d}\theta/\mathrm{d}t=\omega\)
- target \(\omega\) → expect \(\mathrm{d}\omega/\mathrm{d}t=-\omega_0^2\sin\theta\)

Compression / description: shared support with realization-dependent intercept
\(E_i\) via SIR `CONST` (`constant=True`) and per-realization coefficients.
Do **not** add \(E_i\) to the files. Details in `IMPLEMENTATION_NOTES.md`.

## Regenerate data

```powershell
python D:\SIR_paper\Pendulum\generate_pendulum_data.py
```

## Tests

```powershell
python -m pytest D:\SIR_paper\Pendulum\tests -q
```

## QC

See `qc/pendulum_qc_report.json` and `qc/pendulum_dataset_qc.png` after
generation. Energy-drift limits enforced at write time:
max relative \(<10^{-7}\), max absolute \(<10^{-8}\).

This ensemble (seed `20260820`):

| | min | median | max |
|---|---|---|---|
| \(\theta_0\) (rad) | −2.119 | 0.238 | 2.393 |
| \(\omega(0)\) (rad/s) | −1.089 | 0.017 | 1.041 |
| \(E_i\) | 0.292 | 1.543 | 3.280 |
| \(E_i/(2\omega_0^2)\) | 0.080 | 0.423 | 0.900 |

16/16 split on the sign of \(\theta_0\) and of \(\omega(0)\).

Max / median absolute energy drift: \(2.12\times10^{-11}\) / \(4.85\times10^{-12}\).
Max / median relative energy drift: \(6.45\times10^{-12}\) / \(3.54\times10^{-12}\).

Finite-difference \(\mathrm{d}\theta/\mathrm{d}t-\omega\) residuals on the
0.01 s grid are \(O(10^{-2})\) (second-order \(\nabla\) truncation), not
an ODE defect; energy conservation is the tight integrator check.
