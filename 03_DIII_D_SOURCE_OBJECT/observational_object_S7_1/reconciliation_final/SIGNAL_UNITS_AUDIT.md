# S7.1R-FINAL — Units registry audit

Machine-readable form: `SIGNAL_UNITS_AUDIT.csv` (95 rows).
Registry: `S7/SIGNAL_UNITS.json`.

## Result

```
units_resolved   = 95 / 95      (every signal has a determination)
  with a physical unit          93
  documented as uncalibrated     2   pcbcoil, pcdiamag3
units_unresolved =  0 / 95
ECE channels assigned keV = 40 / 40
```

`pcbcoil` and `pcdiamag3` are **resolved as unit-less**, not missing. Upstream
reports `raw`: uncalibrated digitiser output for which no physical unit exists.
Recording a unit for them would be fabrication.

## The ECE correction

**40** channels, identified from the registry rather than assumed. The
description-based set (`"ECE radiometer"`) and the name-based set (`ece*`) were
computed independently and required to be identical before anything was written.

All 40 previously had `units: null`, status `unresolved`, with the registry
noting they were *"Left null deliberately: NOT inferred."* **No ECE entry
carried a conflicting unit**, so the STOP condition did not trigger.

Applied: `units = "keV"`, `status = "domain_authorized"`,
`evidence_class = "DOMAIN_AUTHORIZED"`, and a note recording that this is expert
assignment rather than recovered metadata.

Safety: the 55 non-ECE entries were compared against a pre-change snapshot after
the write and are **byte-identical**. The file was re-parsed and re-validated.

| | sha256 |
|---|---|
| pre | `bbebdc234b35eccb9682b7a38dc26137c721fe960642972d40c34a14a1d6d4f6` |
| post | `b8b3cead0d1d23d8fc42a54824421472847c0744fb293b6fd2196ac93e598e72` |

Snapshot preserved at `SIGNAL_UNITS.pre_S7_1R.json`.

## Evidence classes

| Status | n | Meaning |
|---|---|---|
| `documented` | 38 | one non-blank unit string, identical on all 62 shots |
| `domain_authorized` | 40 | **new** — expert assignment, no upstream string exists |
| `dimensionless` | 6 | upstream reports `' '` (explicit), not `''` (unset) |
| `resolved_spelling` | 5 | several spellings of one unit, canonicalised |
| `resolved_partial` | 4 | reported on some shots, blank on others |
| `uncalibrated` | 2 | upstream reports `raw`; no physical unit exists |

The registry's distinction between `' '` and `''` matters: it separates *"MDSplus
says this is dimensionless"* from *"the attribute was never set"*. Six signals
(`betan`, `q95`, `li`, `kappa`, `tritop`, `tribot`) are dimensionless on that
basis, not by assumption.

## Provenance of the registry itself

The registry cites `smallELM_freq_v6_ZL_data/{shot}_metadata.json` as its source
and `build_signal_units.py` as its generator. **Neither is present in any local
tree.** The units are therefore `LOCAL_DOCUMENTED`, not `CODE_VERIFIED`: strong
evidence, but not re-derivable here.

Its internal evidence is nonetheless substantial — it records per-shot unit
variant counts across all 62 discharges, which is the signature of a real audit.

## Three scale inconsistencies inside the object

Carried from the registry's own `scale_warnings`, all confirmed independently
against observed magnitudes:

| Quantity | Signals | Stored as | Ratio |
|---|---|---|---|
| Power | `pinj` / `pinj_*` | kW / W | 10³ |
| Number density | `density` / `prmtan_neped` | cm⁻³ / m⁻³ | 10⁶ |
| Temperature | `ece*` / `cerqtit*`, `prmtan_teped` | keV / eV | 10³ |

Within-discharge z-scoring hides all three. They become live the moment any
stage forms a ratio, a sum, or a dimensional type across a pair — which is
exactly what a relational ontology does.

## A note on unit knowledge versus provenance knowledge

They are not the same, and this pass keeps them apart. The 15 equilibrium
quantities now have well-documented units and remain `LINEAGE_PARTIAL`. Knowing
that `q95` is dimensionless says nothing about what produced it.
