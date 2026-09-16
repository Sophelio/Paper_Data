# Partial maps under the unchanged denominator rule

Machine-readable: `partial_map_admissibility.json`,
`denominator_conditioning_audit.csv`,
`manifests/DENOMINATOR_RULE_VERIFICATION.json`

---

## The rule was verified, not reopened

```
DENOMINATOR_ADMISSIBILITY_PRIMARY_V1
sha256 6d4004eb3ae95067b2a01dddeb90226748cfee7097217d68ab5377ac50ed716d
hash_verified_unchanged : true      reopened : false      threshold_changed : false
```

On each **required development calibration block**, for denominator `d`:

```
scale(d) = RMS(d)              eta(d) = min(|d|) / RMS(d)
require: finite throughout · RMS(d) != 0 · no sign change · eta(d) >= 0.05
```

Fail on **any** required block ⇒ every coordinate using that denominator is
rejected under class E.

**No epsilon · no shift · no clipping · no masking rescue · no bounded
reciprocal · no regularisation · no branch repair.** The 0.01 and 0.10
sensitivity values stay sensitivity-only, for S7.11.

### Scope, not content

The frozen rule text names C3 and C4, because those were the only partial maps
in the superseded five-family grammar. The hardened grammar has five. The rule
is **unchanged**; only the set of families it is applied to grows with the
catalogue. Two reusable tables were built so the families cannot disagree:

| table | denominator | used by |
|---|---|---|
| `LEVEL_DENOMINATOR_STATUS` | `d = x_j` (level, canonical units) | C3, C5, C7 |
| `RATE_DENOMINATOR_STATUS` | `d = dx_j/dt` (FD2_PHYSICAL_TIME_V1) | C4, C8 |

C0, C1, C2 and **C6** have no denominator and no gate. C5's denominator is its
own operand.

---

## Level denominators — 39 of 68 survive

4 080 evaluations (68 signals × 20 discharges × 3 blocks).

Cell-level first failures: sign change 521 · zero value 231 · RMS zero 96 ·
margin below η 84.

**Survivors (39):** 33 ECE channels · `bt` · `ip` · `prmtan_neped` ·
`cerqtit3` · `cerqtit10` · `cerqtit11`

**Failures (29):** all 10 beam signals · all 4 gas valves · 3 filterscopes ·
11 CER chords · `prmtan_teped`

The split is physical. Electron temperature is strictly positive and smooth
across a calibration block. Rotation crosses zero. Beams and gas valves switch
off. Filterscopes fall to the noise floor.

## Rate denominators — 0 of 63 survive

3 780 evaluations. **Every** derivative fails.

| first failure | signals |
|---|---|
| `E_DENOM_SIGN_CHANGE` | 61 |
| `E_DENOM_RMS_ZERO` | 2 (`pinj_21l`, `pinj_21r` — beamlines that never fired) |

3 684 of the 3 780 individual cells show a sign change. A time derivative of a
physically fluctuating signal crosses zero inside every calibration interval, so
the no-sign-change condition fails before the magnitude margin is even reached.

**This was recomputed from scratch on the hardened basis.** The historical V1
outcome was not consulted, not assumed, and not used to skip an evaluation. The
two stages agreeing is corroboration, not inheritance.

---

## Consequences

| family | denominator | admissible |
|---|---|---|
| C3 `RATIO(i,j)` | level | 2 457 of 4 556 |
| C5 `RECIP(i)` | level (own operand) | 39 of 68 |
| C7 `RATE_OVER_LEVEL(i\|j)` | level | 2 301 of 4 284 |
| C4 `PHASE(i\|j)` | rate | **0 of 3 906** |
| C8 `LEVEL_OVER_RATE(i\|j)` | rate | **0 of 4 284** |

### `ZERO_SURVIVING_PRIMARY_C4` and `ZERO_SURVIVING_PRIMARY_C8`

The required reading, stated exactly:

> `G_rec^H` admitted the constructor family conceptually; the observational
> object failed to support stable primary instances under `K_rec`'s
> numerical-domain condition.

What this is **not**:

- not a claim that the phase derivative or the level-over-rate relation is
  mathematically invalid — both are well-defined maps wherever their denominator
  is non-zero;
- not an ontology error, and not a reason to revise `G_rec^H`;
- not a reason to weaken, relax or re-tune the gate;
- not a reason to remove either family from the catalogue. Both remain declared,
  enumerated, and audited, with 8 190 symbolic instances between them.

Shifted, bounded or local-domain alternatives are **different constructors**.
They would need their own prospective declaration and are available to S7.11
sensitivity study, never as a repair on the primary path.

### Why C6 matters here

`LEVEL_RATE(i|j) = x_i · dx_j/dt` is the one new family with no denominator. It
relates a level to a rate without a singularity, and it survives at **3 776 of
4 284 (88%)** — the largest family in the admissible universe. The level–rate
gap the hardened grammar set out to fill is filled, just not by the two
quotient-form families.

---

## The external rule, frozen without opening a value

Any finally selected support containing a partial-map coordinate must satisfy
the **same** rule on each external local-calibration block. On failure there:

```
do NOT shift or regularise · do NOT replace the coordinate
do NOT refit the support   · record that discharge/block as NOT_APPLICABLE
```

The surviving `Ω_rec` is decided by downstream qualification, not by S7.6R. **No
external value was inspected in this stage.**
