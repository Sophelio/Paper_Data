# O_DIIID_FINAL — the frozen observational object

Machine-readable: `O_DIIID_FINAL.json` · Freeze record: `S7_1_FINAL_FREEZE.json`
Freeze ID: **`D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1`**

```
O_DIIID = (D, Omega_obs, S, E, Pi, A)
```

## On the definition itself

No prose artifact in the project states the 6-tuple. The architecture is
established from `D:\SIR_paper\General\sir_representational_prism.py`, the
manuscript's own visual-abstract figure generator, which draws the scientific
object and the task contract as **separate boxes** and lists the contract's
attributes as *"Admissibility · Information · Intended Use"*.

Evidence class: `LOCAL_DOCUMENTED (figure source)`. A prose definition in the
current manuscript would supersede it and should still be sought.

The consequence is structural, not cosmetic: **admissibility belongs to `q`, not
to `O`**. The original S7.1 audit read the sixth component as admissibility and
recorded it not-instantiated; that reading is retired (ledger R-2).

---

## D — scientific data · `INSTANTIATED`

95 scalar time-series quantities, all present in all 62 discharges.

| Family | n |
|---|---|
| ECE electron temperature | 40 |
| equilibrium / shape | 15 |
| CER rotation / ion temperature | 14 |
| neutral beams | 10 |
| magnetics | 5 |
| filterscope D-alpha | 4 |
| gas injection | 4 |
| density | 3 |

Identity is **one-to-one at every level**: archive keys `<signal>_data` /
`<signal>_times`, canonical name, provider identity and backend identity are the
same string. There are no aliases and no many-to-one mappings.

`FINAL_SIGNAL_INVENTORY.csv` · sha256 `60c6245d…6eb39d`

## Ω_obs — observational support · `INSTANTIATED`

DIII-D. 62 discharges, shots 155537–195659, ordered into 7 operational periods.
Per-signal native time axes in milliseconds. Median common window over all 95
signals: 4590 ms.

Documented inclusion criterion: the archival pipeline could build a common grid
across all 95 signals. Selection **algorithm** unresolved; **parent population**
unresolved; calendar dates unresolved; operating regimes **not assigned**
(assignment would be inference, not record).

`FINAL_SHOT_INVENTORY.csv` · sha256 `7d3c3ab1…15cd8c`

## S — sampling structure · `INSTANTIATED`

Discharge is the primary realization and grouping unit. Native spacings span
**0.02 – 20.0 ms**, three orders of magnitude. The common grid is a
`TARGET_N = 1000` linspace on the intersection window, so **Δt is
discharge-specific**: 4.595 ms median over all 95, 4.965 ms median over the
historical eight.

Channel identity is retained: ECE 1–40, CER channels 3/6/8/10–13, beamlines
15L–33R, filterscopes fs03da/fs04/fs04da/fs05da, gas manifolds A–D.

`FINAL_TEMPORAL_LINEAGE.csv` · sha256 `9bb6d09e…e05a67`

## E — uncertainty · `NOT_INSTANTIATED`

No measurement-error metadata exists anywhere in the observational record, and
none was invented.

The spline and RTS variants are **numerical realizations of the same
quantities** and must not be described retroactively as observational
uncertainty. What would instantiate E: per-signal measurement uncertainty from
the diagnostic archive.

## Π — provenance · `PARTIALLY_INSTANTIATED`

| Layer | Status |
|---|---|
| analysis-side chain | `CODE_VERIFIED` end to end |
| upstream resample | operation documented per signal per discharge; **generator code absent** |
| equilibrium reconstruction | **EFIT** family identified; settings, inputs, constraints unresolved |
| native acquisition | `UNRESOLVED` |

`provenance_graph.json` · sha256 `aec053f8…d1b24c`

## A — ancillary observational information · `PARTIALLY_INSTANTIATED`

Ancillary information and metadata carried with the object — **not** a
task-conditioned admissibility rule.

**Present:** 5890 per-signal-per-discharge resampling records (`method`,
`category`, `original_length`, `resampled_length`); family membership for all
95; a 95-entry units registry; channel identity; cohort provenance flags for all
62; shot identifiers and the ordering they induce.

**Absent:** measurement uncertainty; calendar dates; campaign identifiers;
operating-regime labels; **any ELM or other event annotation** — notable in an
archive described as an ELM dataset; operator commentary.

The resampling records are the most consequential element. They are not inert
labels: they record which numerical operation was applied upstream, per signal
per discharge, and they are what made the U009 cohort discontinuity visible.

---

## Frozen hashes

| Artifact | sha256 |
|---|---|
| signal inventory | `60c6245da695bd897d62c82dd138c4c10cb8fb2387beeb71e5d547262d6eb39d` |
| shot inventory | `7d3c3ab1ab289ea2c7c038397ffb2524ae6dfd00813551dfe3efccf0a415cd8c` |
| units registry | `b8b3cead0d1d23d8fc42a54824421472847c0744fb293b6fd2196ac93e598e72` |
| provenance graph | `aec053f80d951d37f2c1096158799b14112e84ca6db695e1a8fbdf2433d1b24c` |
| backend parity | `405856b6f1220a782dffac6202b1a91396e939a6a1db2991517a2f15a6706506` |
| temporal lineage | `9bb6d09e365688ac8438376986f00009aa735af0cdfb6283c95ade7359e05a67` |
| equilibrium lineage | `e7f6f8049ed4a214e8a60069cfe3fc68fc42bd06f604da968add207171573b56` |
| source inventory | `aa913025890d632ebab82ef65a5583e432c9eab0b6b7058ada0fe07471910754` |
| quality summary | `bd6953095c3ca67ab47451380d16f0c5f08259fba159c77aa9c721707412168e` |

## Stage gate

No target selected. No `K_rec`, no `I_rec`. No admissibility classification. No
coordinates, no `G_rec`, no `A_rec`. No SIR run, no regression, no performance
inspected. No cohorts selected. S7.2 not started.

**No reconstruction target is encoded anywhere in this object.**
