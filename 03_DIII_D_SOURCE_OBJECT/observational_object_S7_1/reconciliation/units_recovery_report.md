# S7.1R Issue 2 — Units recovery

**Scope:** all 95 quantities. **Data:** `units_recovery.csv`.
**Sources and method:** `units_sources.md`.

## 1. Headline

| Evidence class | n | Meaning |
|---|---|---|
| `CODE_VERIFIED` / `LOCAL_DOCUMENTED` | **0** | no local artifact records a unit for any signal |
| `AUTHORITATIVE_EXTERNAL` | 8 | device convention; no magnitude test applicable |
| `STRONGLY_INFERRED` | 86 | device convention, 74 of them magnitude-corroborated |
| `UNRESOLVED` | 1 | `pcdiamag3` — hypothesis refuted by magnitude |

**Not one of the 95 units is locally verified.** S7.1 recorded units as
"unknown"; that was correct as a statement about the project's own record and
S7.1R does not overturn it. What S7.1R adds is that the units are *recoverable
by external convention* and that 74 of those recoveries survive a falsification
test against the project's own data.

The distinction matters for the ontology stage. U002 was classified CRITICAL on
the grounds that dimensional typing was impossible. It is not impossible — it is
possible at `STRONGLY_INFERRED` confidence, provided the resulting typing is
labelled as resting on external convention rather than on project record.

## 2. Confidence is bounded by the absence of a local record

The one function in the project whose responsibility is to report units,
`_units_for()`, returns `{"data": "", "times": "ms"}` — a blank data unit, by
deliberate choice, because the exported columns are already z-scored. There is
no unit table anywhere else: not in the 190 array keys per shot, not in the 62
metadata sidecars, not in either provider, not in the 449-line canonical
provenance ledger, and there is no local MDSplus or OMFIT metadata to fall back
on.

Consequently **no unit in this table may be cited as project-verified**, and
none has been promoted. Magnitude agreement is corroboration; it constrains the
scale but cannot establish a convention.

## 3. The magnitude test earned its place

Testing was not ceremonial — it changed three answers.

### 3.1 `pinj_*` is in W while `pinj` is in kW

The eight per-beam channels read ~1.4–2.2 × 10⁶; the aggregate reads
~9.25 × 10³. Under a shared unit the eight parts would exceed their own sum by
~1000×. Assigning W to the parts and kW to the aggregate reconciles them:
Σ per-beam ≈ 10.5 MW against an aggregate of 9.25 MW.

This is the strongest unit result in the pass, because it rests on **additivity
inside the project's own data** rather than on external convention.

### 3.2 `pcdiamag3` is not joules — `UNRESOLVED`

Diamagnetic stored energy on DIII-D is O(10⁵–10⁶) J. Observed: median 9.69,
range −28 to +33. Refuted by four to five orders of magnitude. No rescaled
alternative is offered; the honest output is that the quantity behind this tag
is not established.

This is not a minor entry. `pcdiamag3` was one of the **eight signals used by
every prior analysis in this project**, including the canonical q_desc run. Its
physical identity is now formally open.

### 3.3 `tinj` is torque (N·m), not angular impulse

Observed median 5.9 matches injected torque directly.

## 4. Unit systems are inconsistent within the object

| Physical quantity | Signals | Stored as | Ratio |
|---|---|---|---|
| Number density | `density` / `prmtan_neped` | cm⁻³ / m⁻³ | 10⁶ |
| Temperature | `ece*` / `cerqtit*`, `prmtan_teped` | keV / eV | 10³ |
| Power | `pinj` / `pinj_*` | kW / W | 10³ |

Within-discharge z-scoring makes these differences invisible downstream, which
is why they persisted. They become live again the moment any stage forms a ratio,
a sum, or a dimensional type across members of these pairs.

## 5. Value anomalies (not unit failures)

`ece33` (median 33.9 keV) and `ece34` (21.5 keV) fall outside the expected ECE
band while 38 of 40 ECE channels pass. Group coherence carries the unit; these
two are flagged as **value anomalies** for the data-quality record. Plausible
causes — cutoff, non-thermal contamination, a miscalibrated channel — are not
adjudicated here.

`pinj_21l` and `pinj_21r` are identically zero across the cohort: beam 21 never
fired in any of the 62 discharges. Recorded as `NOT_TESTED_INACTIVE`. These are
two of the 88 near-constant pairs S7.1 flagged.

## 6. Effect on U002

**Recommend `CRITICAL` → `MAJOR`.** Dimensional typing is available at
`STRONGLY_INFERRED` confidence for 94 of 95 signals, with one genuinely
unresolved (`pcdiamag3`) and three cross-system inconsistencies now explicit and
correctable. What remains blocked is any claim that the object's units are
*known from its own record*, which no downstream stage should assert.
