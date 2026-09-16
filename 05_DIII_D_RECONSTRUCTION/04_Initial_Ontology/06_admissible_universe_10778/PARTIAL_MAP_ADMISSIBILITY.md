# Partial-map admissibility — ratios and phase derivatives

Machine-readable: `denominator_admissibility_rule.json` (frozen **before** any
coordinate value was read), `denominator_conditioning_audit.csv`

---

## The frozen rule

S7.2's `P_rec` class E froze the *principle*: a denominator whose
calibration-interval sign changes, or whose minimum absolute magnitude falls
below a fixed fraction of its calibration scale, is inadmissible unless a
declared regularisation is used. The primary ontology declares **no**
regularisation. The fraction and the scale had never been numerically
instantiated.

That specification was completed **before stage B opened a single coordinate
value**, and hashed (`PRE_ENUMERATION_CONTRACT_COMPLETION`, not an empirical
correction):

```
DENOMINATOR_MARGIN_PRIMARY = 0.05
scale(d)  = RMS(d) = sqrt(mean(d^2))        on one calibration block
eta(d)    = min(|d|) / RMS(d)               on one calibration block

admissible iff, on EVERY required development calibration block:
    d is finite
    d does not change sign
    eta(d) >= 0.05                          and RMS(d) != 0
```

The denominator must stay at least **5% of its RMS calibration scale away from
zero**, in all 60 required blocks (20 development discharges × A/B/C).

**No** shifts, epsilons, clipping, bounded reciprocals or piecewise branch
repair — those would be *different coordinate constructions*, and none was
frozen as a primary constructor.

Predeclared for S7.11 sensitivity only: `eta = 0.01` and `eta = 0.10`. Neither
may replace the primary 0.05 result.

## C3 ratios — denominator is the level `x_j`

**46 of 76** level denominators pass.

| Passing (46) | |
|---|---|
| all 40 ECE channels | electron temperature, strictly positive with margin |
| `cerqtit3`, `cerqtit10`, `cerqtit11` | ion temperature |
| `bt`, `ip` | toroidal field, plasma current |
| `prmtan_neped` | pedestal density |

| Failing (30) | Reason |
|---|---|
| 7 `cerqrott*` | sign change — toroidal rotation reverses |
| `cerqtit12`, `cerqtit13` | sign change |
| `cerqtit6`, `cerqtit8` | `eta` below 0.05 |
| `fs03da`, `fs04`, `fs04da` | sign change |
| `fs05da` | `eta` below 0.05 |
| `gasb`, `gasc`, `gasd` | sign change |
| `gasa` | `eta` below 0.05 |
| `pinj`, `pinj_30r`, `pinj_33r`, `tinj` | sign change |
| `pinj_15l`, `pinj_15r`, `pinj_30l`, `pinj_33l` | exact zero value (`eta = 0`) |
| `pinj_21l`, `pinj_21r` | `RMS = 0` — beams never fired |
| `prmtan_teped` | sign change |

**C3 admissible: 3 266 of 5 700.** Rejections: 1 350 sign change, 450 margin,
300 zero value, 150 RMS zero (all class E) and 184 class D constant on the
constructed ratio.

Every rejection is physically legible. Rotation reverses direction. Filterscope
and gas-valve signals sit near zero between events. Beams switch off, and two
never fired at all.

## C4 phase derivatives — denominator is `dx_j/dt`

**0 of 70** derivative denominators pass.

```
C4 admissible: 0 of 4 830
```

97.7% of the 4 200 denominator checks fail by **sign change**; the remainder by
`RMS = 0`.

This is not a surprising result once stated plainly: `dx/dt` changes sign at
every local extremum of `x`. Over a calibration interval spanning 40–80% of a
discharge, essentially every plasma quantity rises and falls at least once, so
its time derivative crosses zero. A phase derivative `(df/dt)/(dg/dt)` is then
undefined or unbounded somewhere inside every required block.

**No reaction is taken to this result**, as the stage instruction requires.

What it means, precisely:

- the **constructor** remains in `G_rec` — the grammar permits it;
- **no instance** satisfies the task's frozen instance-level domain requirement
  on this observational object;
- this is **not** a search failure and **not** evidence about predictive value.
  Nothing was fitted, and no coordinate was compared to the target.

It is exactly the distinction the stage exists to draw: *ontology* versus
*task-specific admissible universe*. A construction can be mathematically legal
and scientifically meaningful, and still have no instance whose denominator
stays away from zero on the frozen calibration domain.

Anything that would rescue the family — a shifted, bounded or
sensitivity-centered phase derivative — is a **different construction**, already
`PRIMARY_ONTOLOGY_EXCLUDES` in S7.5, and would need separate explicit
qualification.

## External application rule — frozen prospectively

Frozen here **without opening any external value**.

For a selected representation containing C3 or C4 coordinates, external local
calibration must apply the **same** rule: finite denominator, no sign change,
`eta ≥ 0.05`.

If a frozen selected coordinate fails its domain predicate on an external
discharge or block:

- **do not** shift or regularize it;
- **do not** replace the coordinate;
- **do not** refit the support;
- record the representation as **`NOT_APPLICABLE`** on that discharge/block.

Whether the claimed `Omega_rec` survives that is a question for the downstream
qualification stage. **S7.6 does not decide the external outcome.**
