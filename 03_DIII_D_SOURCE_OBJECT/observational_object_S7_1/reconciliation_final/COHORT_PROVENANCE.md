# S7.1R-FINAL — 62-discharge cohort

Machine-readable: `FINAL_SHOT_INVENTORY.csv`, `availability_by_shot.csv`,
`availability_matrix.csv`, `signal_quality_summary.csv`.

## Confirmed

- **62 discharges**, shot numbers 155537 – 195659.
- **All 95 signals present and loadable in all 62.** The signal set is identical
  in every archive; 5890/5890 signal × discharge pairs load.
- **Finite fraction = 1.0 for every one of the 5890 pairs.** No NaNs anywhere.

## Was "all 95 on a common grid" the cohort criterion?

The documented inclusion criterion is that the archival pipeline could build a
common temporal grid across all 95 signals for that discharge. The census is
**consistent** with that — every discharge does carry all 95 — but consistency
is not proof: an artifact recording the selection *algorithm*, or the parent
population it drew from, does not exist. The criterion is `LOCAL_DOCUMENTED`;
the algorithm is `UNRESOLVED` (U005).

No evidence of manual QC was found, and no shot-level exclusion record exists.
Absence of a record is not evidence that none occurred.

## The cohort is not homogeneous

Two upstream processing eras are present, splitting cleanly with no overlap:

| Era | Shots | n | `ip` upstream method |
|---|---|---|---|
| earlier | <= 187024 | **35** | `cubic_spline` (~2:1 downsample, no anti-alias) |
| later | >= 189646 | **27** | `decimate_with_antialiasing` (~20:1) |

`bt`, `prmtan_neped` and `prmtan_teped` vary likewise.

**Independently corroborated by different metadata.** The units registry records
upstream unit-string variants splitting **35/62 and 27/62** — `bt` (`t` vs
blank), `ip` (`a` vs `amps`), and the filterscopes (`ph/(sr cm2 s)` vs
`ph/cm2/sr/s`). The same partition, reached from a different source. (Shot-level
membership of the registry's split could not be verified because its source tree
is absent; the count agreement is what is recorded.)

This is issue **U009**.

## Ordering without dates

No calendar date or campaign identifier is recorded for any discharge. But
DIII-D shot numbers increase monotonically with time, so contiguous shot-number
families order the cohort into **7 operational periods**:

`155537` · `159310–161414` (10) · `165017–165965` (13) · `170394–170411` (3) ·
`186997–187024` (8) · `189646–189652` (6) · `195261–195659` (21)

This partially resolves U008 — ordering only. **Operating-regime labels are not
assigned**; inferring them from the signal traces would be interpretation, not
provenance.

## Data quality

Descriptive only. No task-dependent screening was performed and no signal was
ranked by usefulness, because usefulness is task-conditioned and no task exists.

| Property | Value |
|---|---|
| signal × discharge pairs | 5890 |
| finite fraction | **1.0** for all |
| near-constant pairs (<=2 unique values) | 89 (1.5%) |
| identically-zero pairs | 84 |
| high-repeat-value pairs (possible clipping) | 147 |
| median repeat ratio | 0.243 |

The identically-zero pairs are entirely beam channels that never fired:
`pinj_21r` (38 discharges), `pinj_21l` (34), `pinj_15r` (7), `pinj_33l` (3),
`pinj_30r` (2). That is an operational fact about the discharges, not a data
defect, and it is retained rather than screened.

The median repeat ratio of 0.243 is consistent with upstream resampling of
coarse signals onto denser grids.

## The scope statement that matters

**These 62 discharges are the complete finite object available to this study.
They are not a random or representative sample of DIII-D operations.** The
parent population is unknown, the selection algorithm is unrecorded, and the
cohort spans seven operational periods with two distinct upstream processing
regimes.

O is well defined over them. Generalisation beyond them is not supported by
anything in this record, and any later claim of cross-discharge generality must
contend with the U009 discontinuity.
