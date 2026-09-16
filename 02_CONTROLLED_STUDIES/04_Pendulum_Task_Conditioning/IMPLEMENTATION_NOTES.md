# Pendulum — implementation notes (conventions inspected 2026-08-20)

This file records the **existing** Dalia / SIR paper-example pattern that
Pendulum mirrors. It is not a new registration mechanism.

## Layout of existing numerical examples

Under `D:\SIR_paper` the synthetic examples are:

| Folder | Records | On-disk format | Dalia entry | SIR-web entry |
|---|---|---|---|---|
| `Heat Equation Degeneracy/` | `realization_00.parquet` | **Parquet** | `data_provider.py` | `heat_equation_degeneracy_data_provider.py` |
| `Lorenz/` | `lorenz_dt001.parquet` | **Parquet** | `data_provider.py` | `lorenz_data_provider.py` |
| `Stochastic oscillator/` | `realization_00` … `_39.parquet` | **Parquet** | `data_provider.py` | `stochastic_oscillator_data_provider.py` |

There is **no NetCDF** in these paper examples. The user brief preferred
NetCDF only if it matched neighbours; it does not. Pendulum therefore
stores one **Parquet file per realization** (columns `times`, `theta`,
`omega`) plus a `manifest.csv`. Realization metadata lives in Parquet
schema metadata and in the manifest, **not** as searchable columns.

## Two provider contracts (both required)

### 1. Dalia / Modalia (`data_provider.py`) — what Home actually loads

Documented in `D:\dalia\docs\provider_authoring.md`. Required keys:

- `fetch_data(folder, dataset_id, record_id, signals, params, data_trim_1, data_trim_2)`
  → `{id, signals: [{data, data_name, times, errored}], errored_signals}`
  (or `[]` if `record_id is None`)
- `fetch_record_ids_for_dataset_id(folder, _)` → `list[str]` (parquet **stems**)
- `all_possible_signals` → `list[str]`
- `dataset_id` → `str`
- `data_folder` (alias `data_source`)

Optional SIR hooks used by the Dalia SIR module
(`D:\dalia\worker\worker\modules\sir.py`):

- `fetch_sir_record_ids(folder, _)`
- `fetch_data_sir(folder, record_id, variables=None)` → `{times, <var>: ndarray, ...}`

Path convention: prefer `Path(__file__).resolve().parent / "data"`, with
an absolute `DEFAULT_DATA_FOLDER` fallback (Heat/Lorenz/SHO).

Virtual / synthesized coordinates (Lorenz `dx,dy,dz`; Heat derivatives)
are **not stored** when they can be recomputed; `_ensure_requested_columns`
adds them at fetch time. Pendulum follows that for `sin_theta`,
`cos_theta`, `one_minus_cos_theta`, `omega_squared`.

### 2. Legacy SIR-web (`*_data_provider.py`)

Used by sir-web copies into `.providers/current_provider.py`. Keys:

- `fetch_data(identifier, knames)` → `(data, xflags, timing_data, freq, smooth_rate)`
- `fetch_identifier_variables(identifier, key)`
- `fetch_identifiers_from_url(directory)` — full paths, sorted
- `fetch_dataset_variables(directory)`
- `dataset_url`

`timing_data` shape is `(1, n_samples)`; `freq` is a Python `float`
(`dt`); `xflags` is a boolean vector of length `len(knames)`; `data` is
`float64` with shape `(n_vars, n_samples)`.

Pendulum ships **both** files, like Heat / Lorenz / SHO.

## Dalia project registration

Projects are JSON documents in the shared store

```
D:\SIR_paper\.dalia\projects\<uuid>.json
```

pointed at by `DALIA_PROJECTS_DIR` (see the paper-root `README.md`).
Each example also keeps a copy under `<example>\.dalia\projects\`.
`DIIID_example\.dalia\projects\` currently mirrors the same UUIDs.

The document contains:

- `id`, `name`, `version`
- `files`: in-document Python (`data_provider.py`, siblings)
- `data_root`: absolute path to the example `data/` folder
- `active_file`, `user_layout`, `labels`, `pipelines`, `derived_signals`
- optional `module_settings.sir`

There is **no separate registry file**. Selecting/opening the project on
Dalia Home is sufficient. `create_project` on a live Dalia instance
writes the same kind of JSON; dropping a document into
`DALIA_PROJECTS_DIR` is the offline equivalent used for the existing
paper examples.

On this machine the **running** Dalia Home store is
`D:\dalia\.dalia\projects\` (it already held Heat / Lorenz / SHO / DIII-D
with the same UUIDs as the paper copies, plus Fusion Energy). Pendulum
was copied there as well so Home lists it without changing
`DALIA_PROJECTS_DIR`. The paper-root README still documents
`D:\SIR_paper\.dalia\projects` as the portable shared store.

## Derived-coordinate route chosen

Dalia Data Maker derived signals are **one source + a pipeline**. Built-in
blocks (`D:\dalia\worker\worker\dfl\blocks.py`) are fill / resample /
normalize / smooth / differentiate — **not** `sin`, `cos`, or `x^2`.

A custom `blocks/*.py` transform could implement `sin(theta)`, but:

1. SIR selectable variables come from `all_possible_signals` /
   `fetch_data_sir`, not from Data Maker derived names (unless the user
   also graphs them).
2. Lorenz already synthesizes virtual columns inside the provider.

Pendulum therefore exposes virtual coordinates **in the provider**,
computed from raw `theta`/`omega`, in both `fetch_data` /
`fetch_identifier_variables` / `fetch_data_sir` and in
`all_possible_signals` / `fetch_dataset_variables`. They are **not**
written to the Parquet files.

`energy_true` and analytic `dtheta/dt`, `domega/dt` are **not** exposed.

## SIR target-type strings

Confirmed in `D:\dalia\worker\worker\modules\sir.py` and
`sir_lib/consumer.py` (case-sensitive):

```
"Variable", "Derivative", "Double Derivative",
"Triple Derivative", "Quadruple Derivative"
```

Default in the SIR module is `"Derivative"`. Future prediction tasks
should use that exact string.

## Compression contract / realization-dependent \(E_i\)

SIR prepends a `CONST` column of ones when `constant=True`
(`sir_lib/data.py` `_add_constant`, `sir_lib/model.py`). Coefficients
are fit **per realization** (`eq["x"]` has shape
`(n_realizations, n_terms)`), which is how the stochastic oscillator
recovers a shared form with a realization-dependent ratio.

A compression relation equivalent to

\[
\tfrac12\omega^2 + \omega_0^2(1-\cos\theta) = E_i
\]

can therefore be expressed as a **shared support** with a
realization-dependent intercept, e.g.

\[
[\omega^2] + a_i\,[1-\cos\theta] + c_i = 0
\]

or, targeting `omega_squared` as a `"Variable"`,

\[
\omega^2 = A_i\,(1-\cos\theta) + B_i
\]

with \(A_i \approx -2\omega_0^2\) (shared) and \(B_i \approx 2 E_i\)
(per realization). **No change to SIR/Dalia math is required**, and
\(E_i\) is **not** leaked into the data. Whether a given search recovers
that support is a later experiment; this dataset is not tuned for it.

Caveat: a run with `constant=False` cannot represent \(E_i\) as an
intercept. The Heat example document sets `"constant": true`; Pendulum
should do the same when the compression task is configured.

## Tests

`D:\SIR_paper` itself has **no** pytest tree. Tests live in Dalia
(`D:\dalia\worker\tests\`, `ProviderRuntime`). Pendulum adds focused
pytest files under `Pendulum/tests/` that cover both provider contracts
and, when Dalia's worker is importable, a `ProviderRuntime` smoke fetch.
