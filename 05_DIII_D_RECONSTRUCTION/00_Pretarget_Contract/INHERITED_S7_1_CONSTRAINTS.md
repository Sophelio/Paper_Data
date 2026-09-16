# S7.2 — Constraints inherited from the frozen S7.1 object

Parent freeze: **`D3D-SIR-S7.1-OBSERVATIONAL-OBJECT-FINAL-V1`**
(`FROZEN_WITH_QUALIFICATIONS`, 32/32 acceptance tests)
Verification: `manifests/S7_1_INPUT_VERIFICATION.json` — 9/9 hashes verified.

These are not optional. Every one binds a downstream policy in this contract.

---

## 1. O is the 95-signal object

The historical eight-signal Paper provider does **not** define O. The
target-conditioned dFL export does **not** define O. O contains the **95**
archived quantities across **62** discharges, complete and finite in all 5890
pairs.

**No eight-signal restriction may re-enter K_rec by inheritance.** If S7.3
narrows the admitted set it must do so by an explicit, documented rule applied
to all 95 — never by starting from the historical subset.

→ binds `TARGET_ELIGIBILITY_POLICY.md`, `KNOWLEDGE_POLICY.md`

## 2. Units must be respected before relational construction

Three scale traps, all invisible under within-discharge z-scoring:

| Quantity | Signals | Stored as | Ratio |
|---|---|---|---|
| Power | `pinj` / `pinj_*` | kW / W | 10³ |
| Number density | `density` / `prmtan_neped` | cm⁻³ / m⁻³ | 10⁶ |
| Temperature | `ece*` / `cerqtit*`, `prmtan_teped` | keV / eV | 10³ |

Any construction forming sums, ratios, products, dimensionless groups, or
requiring dimensional typing **must** operate on a canonical-unit representation
or explicitly carry units. Standardisation must never be relied on to hide a
unit mismatch.

→ binds `UNIT_AND_TYPE_POLICY.md`

## 3. Equilibrium provenance is partial

All 15 equilibrium/shape quantities — `aminor`, `area`, `betan`, `drsep`,
`kappa`, `li`, `q95`, `rmaxis`, `rsurf`, `tribot`, `tritop`, `volume`, `zcur`,
`zmaxis`, `zsurf` — are **`LINEAGE_PARTIAL`**. The family is EFIT; its settings,
inputs and constraints are not locally available.

**No one may infer target-independence for these 15 merely because dependence
cannot be proven.** Absence of evidence is not evidence of independence.

→ binds `INFORMATION_BOUNDARY_POLICY.md` (fail-closed rule)

## 4. Sampling is genuinely multirate

Native cadences span **0.02 ms → 20 ms**. The fixed-20-ms analysis-grid claim is
retired. The historical Paper 8-signal grid was 4.08–6.03 ms; a 95-signal
fixed-N grid would be 3.75–5.37 ms.

Equilibrium quantities are natively 20 ms and are therefore **~4× interpolated**
on a ~5 ms fixed-N grid. **Derivative-valued coordinates over interpolated
equilibrium signals must not be treated as though the interpolated points were
new observations.**

→ binds `NUMERICAL_RESOLUTION_POLICY.md`

## 5. Upstream resampling is partially unresolved

The operation is documented for all 5890 pairs; the generator code is absent.
**18 quantities were downsampled by interpolation with no anti-aliasing:** all 14
CER channels, plus `bt`, `ip`, `prmtan_neped`, `prmtan_teped`. Aliased content
is not separable from signal in those.

Claims about native high-frequency physics or diagnostic bandwidth are **outside
scope**.

→ binds `NUMERICAL_RESOLUTION_POLICY.md`, `DOMAIN_AND_CLAIM_BOUNDARY.md`

## 6. There are two processing eras

**35 earlier** discharges and **27 later**, with a clean upstream processing
discontinuity beginning at shot **189646**. Independently corroborated by the
units registry's 35/62–27/62 unit-string variant split.

This must appear explicitly in the cohort partition and in validation reporting.

→ binds `COHORT_PARTITION_POLICY.md`, gate **V6**

## 7. E is not instantiated

No measurement-error model exists.

- No fabricated measurement-error weights.
- Numerical perturbations are **not** observational uncertainty.
- Bootstrap and sensitivity analyses are permitted later but must be labelled
  **analyst-defined qualification procedures**.

→ binds `UTILITY_AND_QUALIFICATION_POLICY.md`

## 8. The cohort is finite, not representative

The 62 discharges are the complete finite object available to this study. The
parent population and selection algorithm are unresolved, and the cohort spans
seven operational periods.

**No claim may silently generalise to all DIII-D operations.**

→ binds `DOMAIN_AND_CLAIM_BOUNDARY.md`

---

## Additional inherited facts used by this contract

- **`pcdiamag3` and `pcbcoil` are uncalibrated raw digitiser output** with no
  physical unit. `pcdiamag3` is one of the historical eight — its physical
  identity is open. → `TARGET_ELIGIBILITY_POLICY.md`, `UNIT_AND_TYPE_POLICY.md`
- **Origin classification:** 57 diagnostic reconstruction, 15 equilibrium
  derived, 14 control/actuation, 9 direct measurement, 0 unknown. →
  `TARGET_ELIGIBILITY_POLICY.md`
- **Δt is discharge-specific and depends on the requested signal set.** A run
  over all 95 is not on the canonical q_desc grid. →
  `NUMERICAL_RESOLUTION_POLICY.md`
- **Statistical correlation is not provenance.** Binding downstream. →
  `INFORMATION_BOUNDARY_POLICY.md`
- **84 identically-zero pairs** are beam channels that never fired — an
  operational fact, not a defect. → `ADMISSIBILITY_POLICY.md` (numerical support)
- **No ELM or event annotations exist** anywhere in the archive. →
  `RECONSTRUCTION_TASK_DEFINITION.md`

## One defect found in the parent freeze

The S7.1 freeze recorded artifact hashes under **two different rules** —
in-memory for most, post-`read_csv` round trip for `FINAL_SIGNAL_INVENTORY.csv`
and `signal_quality_summary.csv`. Both are reproducible; they are simply
different. A verifier applying either uniformly reports false drift on the other
subset.

**Data integrity impact: none.** All nine artifacts verify. S7.2 records a
uniform `canonical_raw_byte_hashes` set in
`manifests/S7_1_INPUT_VERIFICATION.json` so later stages have one rule. The S7.1
freeze file was not modified.
