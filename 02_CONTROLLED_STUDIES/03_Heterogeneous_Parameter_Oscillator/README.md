# Stochastic oscillator

Dalia project for the random-coefficient harmonic-oscillator ensemble.

- `data/realization_00.parquet` … `realization_39.parquet` — `times`, `h`, `dh`, `d2h`, `alpha` (10,000 points on \([0,\pi]\); same \(\alpha\) draws as the 100-point ensemble, `SEED = 0`)
- `data_provider.py` / `custom_graphs.py` — Dalia provider, ensemble overlay, true-α histogram

`times` is the spatial coordinate x. `alpha` is metadata, not a graphable signal.

Open **Stochastic oscillator** from Dalia Home, then reload the provider if needed.
