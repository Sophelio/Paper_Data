# Lorenz

Dalia project for the Lorenz attractor validation example.

- `data/lorenz_dt001.parquet` — times, x, y, z
- `data/lorenz_dt001_exact_derivatives.parquet` — plus dx, dy, dz
- `data_provider.py` / `custom_graphs.py` — Dalia provider + Welch power spectrum

`dx`/`dy`/`dz` are synthesized from the Lorenz vector field when a file does not store them.

Open **Lorenz** from Dalia Home, then reload the provider if needed.
