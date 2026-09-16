# Exact coordinate lineage

Status: **D3D-EXACT-COORDINATE-LINEAGE-RESOLVED**
Shift recovery: **EXACT_FROM_SERIALIZED_STATE**

## Construction summary

For Derivative targets, historical sir v1 builds Y-phaseders as `(dy + shiftval)/(dx_i + shiftval)` then z-scores each channel. `shiftval = abs(min(vstack(x, dx))) + nmin` on already z-scored primitives/derivatives. Exact per-discharge `shiftval` values are stored in the historical `.psir`.

## Features
- `d[pcdiamag3]/d[kappa]` (D_kappa W_dia): d[pcdiamag3]/d[t] + shiftval / d[kappa]/d[t] + shiftval; target_containing=True
- `d[kappa]/d[t]` (dot kappa): d[kappa]/d[t] / dt; target_containing=False
- `r[q95]/r[kappa]` (q95 / kappa): r[q95] / r[kappa]; target_containing=False
- `d[pcdiamag3]/d[betan]` (D_betaN W_dia): d[pcdiamag3]/d[t] + shiftval / d[betan]/d[t] + shiftval; target_containing=True
- `d[kappa]/d[betan]` (D_betaN kappa): d[kappa]/d[t] + shiftval / d[betan]/d[t] + shiftval; target_containing=False
- `d[betan]/d[t]` (dot beta_N): d[betan]/d[t] / dt; target_containing=False
- `d[li]/d[betan]` (D_betaN l_i): d[li]/d[t] + shiftval / d[betan]/d[t] + shiftval; target_containing=False

## Code snapshots
- `code_snapshots/get_shiftval_Derivative.py.txt` ← `submodules/Archaieus/src/Archaieus/sir/consumer_function.py` L[114, 126]
- `code_snapshots/yPhaseder_and_quotients.py.txt` ← `submodules/Archaieus/src/Archaieus/sir/consumer_function.py` L[394, 432]
- `code_snapshots/make_Quotients.py.txt` ← `submodules/Archaieus/src/Archaieus/sir/utils/transforms.py` L[218, 240]
- `code_snapshots/finite_difference_derivative.py.txt` ← `submodules/Archaieus/src/Archaieus/sir/utils/transforms.py` L[305, 313]
