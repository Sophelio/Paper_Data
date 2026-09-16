# S7.2 — Numerical resolution policy

S7.1 established that fixed-N interpolation manufactures apparent temporal
resolution: equilibrium quantities natively sampled at 20.0 ms are placed on a
~5 ms grid, so **four of every five grid points are interpolated, not
observed**, reaching ~16× in 2 discharges.

## The governing principle

> **NO SUPER-RESOLUTION AS PRIMARY OBSERVATIONAL EVIDENCE.**
>
> Interpolation-created samples are not observations and may not be treated as
> independent evidence in the primary ontology.

## The primary grid rule — FROZEN

> **Construct the analysis grid no finer than the coarsest native cadence among
> the quantities admitted to the task, subject to common temporal support.**

This is exactly the rule the full 95-signal provider already implements
(`sir-web/providers/diiid_elm_data_provider.py`, L140–143), which sets the grid
to the coarsest requested signal's native cadence and states the reasoning in
its own source. **Prefer that implementation** rather than writing a new one.

Signals **denser** than the grid are block-averaged (anti-aliased) before
placement; signals **sparser** than the grid do not arise under this rule,
because the grid is by construction no finer than the coarsest admitted.

That last clause is the whole point: it removes the interpolation asymmetry that
made the paper grid problematic.

### What this costs

The grid is set by the **worst** admitted signal. Admitting any equilibrium
quantity forces a ~20 ms grid on the whole task, discarding the fast channels'
resolution. This cost is accepted; the alternative is manufacturing evidence.

Where a task admits only fast families, the grid is correspondingly fine.

### Implications by family

| Family | Native Δt | Effect if admitted |
|---|---|---|
| filterscope D-alpha | 0.02 ms | finest; never forces coarsening |
| neutral beams | 0.1 ms | rarely binding |
| ECE | 0.2 ms | rarely binding |
| magnetics | 1 ms | mildly binding |
| gas injection | 2 ms | mildly binding |
| CER, density | 10 ms | strongly binding |
| **equilibrium / shape** | **20 ms** | **binding — forces the coarsest grid** |

**Mixed-family coordinates** inherit the coarsest cadence of their inputs. A
coordinate combining an ECE channel with `q95` is a 20 ms coordinate, and must be
typed as such.

Validation geometry was audited at **every** cadence above and is feasible at
all of them — worst case (20 ms) still yields ≥18 protected and ≥75 calibration
samples per block per discharge. The rule therefore never breaks the protocol.

---

## Derivative policy — FROZEN

| # | Rule |
|---|---|
| D1 | **No derivative may claim resolution finer than its source observation.** A derivative inherits its source's native cadence, and is typed with it. |
| D2 | Derivatives of signals known to have been **interpolation-upsampled** upstream are either **excluded** from the primary ontology or explicitly marked **`NUMERICAL_SENSITIVITY_ONLY`**. |
| D3 | **Equilibrium derivatives are restricted.** With a 20 ms source cadence they are admissible in the primary ontology only if the analysis grid is itself no finer than 20 ms — i.e. only when the grid rule has already coarsened to their cadence. |
| D4 | **Second and higher temporal derivatives are presumed inadmissible** in the primary ontology. Promotion requires explicit human review recorded in the decision ledger, and may not be justified by performance. |
| D5 | Trajectory-relational derivatives (ratios of rates) inherit the **coarser** of numerator and denominator cadence. |

D2 has concrete bite: S7.1 found **16 signals upsampled upstream** — 14 of the
15 equilibrium quantities plus `vsurf`, at ratios up to 4.09 in the worst
discharges.

### Aliasing restriction

S7.1 found **18 signals downsampled by interpolation with no anti-alias stage**:
all 14 CER channels plus `bt`, `ip`, `prmtan_neped`, `prmtan_teped`. Aliased
content in these is not separable from signal.

- They remain **admissible as levels**.
- Their **derivatives** carry a mandatory `ALIASING_RISK` type flag.
- **No high-frequency claim** may rest on them. This is a claim restriction, not
  an exclusion.

---

## The fixed-N grid is not the primary grid

The historical `TARGET_N = 1000` linspace is **not** the primary rule here. It
produces a discharge-specific Δt that is *finer* than the coarsest admitted
cadence — precisely the super-resolution this policy forbids.

It may be used only for **explicit comparability runs** against historical
results, always labelled as such, and never as the primary evidential grid.

## Deferred

- **S7.5:** the instantiated grid cadence for the selected admitted set;
  per-coordinate resolution typing; the `NUMERICAL_SENSITIVITY_ONLY` list.
- **S7.11:** the numerical-realization sensitivity study (unsmoothed / spline /
  RTS), which is an **analyst-defined qualification procedure** and explicitly
  **not** observational uncertainty, since `E` is not instantiated.
