# S7.1R-FINAL — Three provider surfaces

These are routinely conflated. They are different objects with different
purposes, and only one of them is O.

| | **A. Full observational-object provider** | **B. Historical Paper / UI provider** | **C. SIR→dFL feature export** |
|---|---|---|---|
| **Purpose** | expose the finite archived object | the 8-signal historical search surface | derived features for downstream modelling |
| **Raw scientific quantities** | **95** | **8** | **0** (none are raw) |
| **Derived features exposed** | none | none | relational coordinates, phase derivatives |
| **Cohort restriction** | none — all 62 | all 62 | admissible ELM shots only |
| **Transformation** | native arrays, or 1000-pt common grid on request | 1000-pt common grid, Δt 4.08–6.03 ms | inherits Paper grid; z-scored; phaseders added |
| **Target conditioning** | none | none | **yes** — export is named for its target (`pcdiamag3_none_…`) |
| **Manuscript role** | **defines O** | historical search subset | results/product surface |
| **Code** | `sir-web/providers/diiid_elm_data_provider.py`; `DIIID_example/diiid_sir_data_provider.py`; backend v164 | `Paper Examples/diiid_elm_data_provider.py` | `SIR_to_dFL_provider_on_ELM_shots_with_phaseders.py` |

## Three statements to hold onto

**The 8-signal provider does not define O.** It defined the historical search
subset. The other 87 quantities were excluded by convention, not by any
documented scientific reasoning. O is the 95.

**The dFL feature list is not the observational signal inventory.** It contains
no raw scientific quantities at all — it holds z-scored derived coordinates, and
it is *target-conditioned*: the export directory is named for the target it was
built against. Treating it as a signal list would import a task decision into
the observational object.

**Surface A's own grid is not the Paper grid.** A grids to the coarsest
requested native dt (~20 ms with equilibrium signals); B lays 1000 points across
the intersection window (4.08–6.03 ms). Both are correct for their purpose. See
`TEMPORAL_GRID_FINAL_VERDICT.md`.

## Why this matters for the ontology stage

The observational object must be fixed before any task-conditioned rule reshapes
it. If S7.2 inherits surface B or surface C as though it were O, the contract
will have silently absorbed decisions made years earlier for other reasons — a
target choice, in surface C's case.
