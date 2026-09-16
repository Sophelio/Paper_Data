# Access, licensing and redistribution

Presence of a file on the authoring machine does not establish the right to
redistribute it. Categories are separated below.

## Freely redistributable

| Category | Where |
|---|---|
| Generated synthetic data | Lorenz, pendulum, heat-equation, oscillator trajectories in `02_CONTROLLED_STUDIES/` |
| Analysis and figure source code | throughout; authored for this work |
| Derived numerical results | all frozen JSON/CSV/parquet outputs |
| Manuscript-generated tables and indexes | `07_TABLES_AND_REPORTED_NUMBERS/`, `00_START_HERE/` |
| Audit, manifest and provenance records | `08_...`, `18_Machine_Readable_Lineage`, `90_AUDIT_REPORTS/` |

## Restricted: DIII-D source archive — NOT BUNDLED

The 62 resampled discharge archives
(`DIIID_example/data/resampled_data_v6/*_resampled.npz`, 1.1 GB) are **deliberately
excluded**. Redistribution rights for the underlying DIII-D measurements have not
been established here.

This is a deliberate exclusion, **not a missing artifact**.

The strongest legally safe reproducibility path is provided instead:

1. **Discharge identifiers** — the complete 62-shot list, in
   `03_DIII_D_SOURCE_OBJECT/observational_object_S7_1/`.
2. **SHA-256 of every excluded file** —
   `source_access_notes/RESTRICTED_SOURCE_INDEX.csv`, so a reader who obtains the
   archive independently can confirm they hold the identical bytes.
3. **Per-shot resampling metadata** — method, category, units and provenance for
   every admitted signal, in `retrieval_metadata/shot_metadata/` (bundled;
   derived and redistributable).
4. **The units registry** — `SIGNAL_UNITS.json`. Units are read from here, never
   inferred from signal names.
5. **Every derived artifact** — aligned exports, coordinates, coefficients,
   metrics and audits are all bundled.
6. **The data provider** — `retrieval_metadata/diiid_sir_data_provider.py`, the
   exact code that reads the archive.

Anyone with authorised access to the DIII-D archive can reconstruct the
observational object from these materials and verify byte identity.

## Third-party assets

Fonts under `General/fonts` are **not** bundled. Figure scripts request Times New
Roman and fall back to available serif faces; no third-party font is
redistributed here.

## Before public release

- Assign a DOI or archive identifier and record it here.
- Confirm the DIII-D data-use agreement covers the derived artifacts that *are*
  bundled.
- Choose and add a licence file (code and data may warrant different terms).
