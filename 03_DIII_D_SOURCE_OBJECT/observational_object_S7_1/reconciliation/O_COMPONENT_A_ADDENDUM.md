# S7.1R Issue 1 — Addendum: the meaning of `A` in `O = (D, Ω_obs, S, E, Π, A)`

**Addendum semantics.** This document *corrects* S7.1 without rewriting it. The
S7.1 artifacts retain their original text and now carry a correction pointer to
this file, so the audit trail shows both what was concluded and why it changed.

## 1. What S7.1 concluded

S7.1 read `A` as **admissibility**, and recorded it `NOT_INSTANTIATED` on the
grounds that admissibility is task-conditioned and no task exists at Stage 1.
It flagged the reading as ungrounded, noting that the manuscript definition of
`O` could not be located.

## 2. Search for an authoritative definition

Searched, at S7.1 and again with a wider net at S7.1R:

- every `.md`, `.tex`, `.txt` and `.py` under `D:\SIR_paper\`;
- `Lorenz/SIR_paper_orig.pdf` (22 pp) — **zero** occurrences of "observational
  object", "scientific object" or "information boundary"; it predates the
  Section 1.1 architecture;
- the `sir-web` Paper Examples tree;
- the Lorenz benchmark audit corpus.

**No prose artifact states the 6-tuple.** That finding from S7.1 stands.

## 3. But an authoritative local artifact *was* found

`D:\SIR_paper\General\sir_representational_prism.py` — the manuscript's own
visual-abstract figure generator, and its v9 sibling — draws the architecture
directly. Two elements are decisive:

- `draw_observational_object()`, docstring *"Draw the provenance-bearing
  scientific object at the top"*, renders `𝒪` as a box labelled
  **"Provenance-Bearing"** spanning three modality tiles: **Trajectory**,
  **Field**, **Events**.
- The **task contract `q`** is drawn as a *separate* box, and its attributes are
  listed as exactly three lines (L1456–1466):

  > **Admissibility · Information · Intended Use**

**In the manuscript's own figure, admissibility is an attribute of the task
contract `q`, not a component of the scientific object `𝒪`.**

This is `LOCAL_DOCUMENTED` evidence — figure-generating source that produces a
published manuscript figure — and it is the most authoritative statement of the
architecture available locally. It contradicts the S7.1 reading directly.

## 4. Corrected reading

Adopted, consistent both with the figure and with the working semantics supplied
in the S7.1R specification:

> **`A` — ancillary observational information: annotations and metadata carried
> by the scientific object, but not itself a task-conditioned admissibility
> rule.**

Admissibility is relocated to `q`, where the figure places it, and will be
instantiated at whatever stage a task contract is defined — not before.

The reading is recorded as `LOCAL_DOCUMENTED (figure source)`, not
`CODE_VERIFIED`: the figure asserts the architecture pictorially and does not
enumerate the 6-tuple in symbols. A prose definition in the current manuscript
would supersede it and should still be sought before S7.2.

## 5. Reassessment: `A` is `PARTIALLY_INSTANTIATED`

Under the corrected reading, `A` is **not** empty. The object carries a
substantial and previously uncatalogued body of ancillary information.

### Present

| Ancillary information | Extent | Evidence |
|---|---|---|
| Per-signal upstream resampling **method** | 5890 records (62 × 95) | `shot_*_metadata.json` |
| Per-signal upstream resampling **category** | 5890 records | same |
| **Original** sample count before resampling | 5890 records | same |
| **Resampled** sample count | 5890 records | same |
| Signal **group membership** | all 95 assigned to 8 groups | full provider docstring |
| Cohort **provenance flags** (q_desc member; retired q_rec dev/external) | 62 discharges | S7.1, boolean flags only |
| **Shot identifiers**, and the ordering they induce | 62 discharges | archive filenames |

Inventoried in `ancillary_metadata_inventory.csv` (5890 rows) and summarised in
`upstream_resampling_characterization.csv`.

The `method`/`category` fields are the most consequential. They are not inert
labels: they record, per signal per discharge, **which numerical operation was
applied upstream** — `cubic_spline`, `cubic_spline_simple`, `pchip_careful`,
`pchip_no_smoothing`, or `decimate_with_antialiasing` — against a stated signal
character of `smooth_high_snr`, `slow_varying`, `fast_transient`, or `noisy`.
This is exactly the ancillary observational information `A` is meant to hold, and
S7.1 walked past it because it was looking for an admissibility rule.

### Absent

Units; measurement uncertainty; calendar dates or campaign identifiers; operating
regime labels; ELM or other event annotations; operator commentary.

The absence of event annotations is worth stating plainly: the archive is
described as an *ELM dataset*, yet **no ELM event labels are present** in any
archive or sidecar. The 190 keys per shot are exactly `<signal>_data` and
`<signal>_times` — nothing else.

### Status

| Component | S7.1 | S7.1R |
|---|---|---|
| `A` | `NOT_INSTANTIATED` (read as admissibility) | **`PARTIALLY_INSTANTIATED`** (read as ancillary information) |

## 6. What the ancillary information immediately revealed

Cataloguing `A` was not bookkeeping — it produced three findings the S7.1 census
could not have reached, because they live in the metadata rather than the data:

1. **The cohort is stratified.** Contiguous shot-number families partition the
   62 discharges into **7 operational periods** spanning 155537–195659. Since
   DIII-D shot numbers increase monotonically with time, this orders the cohort
   without inventing dates, and partially resolves U008.

2. **Upstream processing differs by period.** `ip` was resampled by
   `cubic_spline` in all 35 discharges up to shot 187024 and by
   `decimate_with_antialiasing` in all 27 from shot 189646 onward — a clean
   split with no overlap. `bt`, `prmtan_neped` and `prmtan_teped` vary likewise.
   **The object is not homogeneous**, and the inhomogeneity aligns with campaign.

3. **14 of 15 equilibrium quantities were upsampled upstream**, and 18 signals
   were downsampled by interpolation with no anti-alias stage.

See §5 of the main S7.1R report.

## 7. Files changed

- `O_DIIID.json` — `A_admissibility` → `A_ancillary_information`, status
  `PARTIALLY_INSTANTIATED`; original block preserved under
  `_s7_1_original_A_admissibility`; `manuscript_definition_source` updated.
- `O_DIIID.md` — correction block appended.
- `S7_1_OBSERVATIONAL_OBJECT_AND_PROVENANCE.md` — correction block appended.
- `S7_1_OBSERVATIONAL_OBJECT_AUDIT_REPORT.md` — correction block appended.

No S7.1 conclusion was deleted or silently edited.
