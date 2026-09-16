# S7.11 — `prmtan_neped` sensitivity

Two predeclared diagnostics, executed exactly as frozen. Neither can repair the
canonical model, and neither alters V1 or V3.

Machine-readable: `prmtan_sensitivity_metrics.csv`.

---

## Why these were predeclared

`prmtan_neped` — pedestal electron density from a tanh fit — belongs to the
`density` scientific family, the same family as the target. Under the frozen
information boundary it is **provenance-certified independent of the target
signal**: it carries no target-signal ancestry, and V1 passes on that basis.

> That certification establishes no target-signal ancestry. It does **not**
> establish physical independence, nor statistical independence, from
> line-averaged density.

That semantic proximity — not any boundary defect — is why these two ablations
were written into the S7.11 predeclaration **before** the external cohort was
opened.

`prmtan_neped` is structurally central to `C_dev_star`: it appears in five of
the twelve coordinates.

## Construction — verified, not assumed

The predeclared removal set was re-derived independently from the recorded
primitive ancestry of each coordinate and agrees exactly:

**Removed (5):** `ID(prmtan_neped)` · `PROD(prmtan_neped,prmtan_neped)` ·
`RATIO(ece21,prmtan_neped)` · `RATIO(fs03da,prmtan_neped)` ·
`RECIP(prmtan_neped)`

**`PRIMARY_MINUS_PRMTAN_NEPED_ANCESTRY` (7 retained):** `ID(cerqtit6)` ·
`ID(pcdiamag3)` · `PROD(ece37,ece39)` · `PROD(gasa,gasa)` ·
`PROD(pinj,cerqrott6)` · `RATIO(ip,ece22)` · `RECIP(cerqtit10)`

No replacement coordinates, no re-search, no support refill, no re-selection.

**`PRMTAN_NEPED_ONLY`:** `ID(prmtan_neped)` alone, same affine local OLS
estimator, no target history, no additional density-family coordinate.

## Results

Both are full-domain: 42/42 discharges, 126/126 blocks.

| | `C_dev_star` | minus-prmtan (7) | prmtan-only (1) |
|---|---|---|---|
| **mean NRMSE** | 0.7424 | **0.8351** | **0.4632** |
| **median NRMSE** | 0.1699 | 0.1764 | **0.4660** |
| `Δ₀` | −0.1801 | −0.0873 | −0.4593 |
| `Δ₁` | +0.5321 | +0.6248 | +0.2529 |
| **V3-style** | FAIL | **FAIL** | **FAIL** |
| earlier mean | 1.1643 | 1.3146 | 0.5692 |
| later mean | 0.1798 | 0.1958 | 0.3219 |
| earlier median | 0.1821 | 0.1835 | 0.5725 |
| later median | 0.1696 | 0.1684 | 0.3086 |
| max single-discharge NRMSE | 11.95 | 13.78 | **0.96** |

Paired mean differences (negative = lower error than the reference):

| | vs `C_dev_star` | vs the other sensitivity |
|---|---|---|
| minus-prmtan | **+0.0928** | +0.3719 vs prmtan-only |
| prmtan-only | **−0.2792** | −0.3719 vs minus-prmtan |

## Reading

**Neither sensitivity passes.** Nothing here rescues anything.

**Removing the same-family density diagnostic makes the external result
worse, not better.** The seven-coordinate support has a higher mean (0.835 vs
0.742), a higher median (0.176 vs 0.170), a worse `Δ₁`, and a *larger* worst
discharge (13.8 vs 12.0). The catastrophic tail survives removal because it was
never a `prmtan_neped` phenomenon — `PROD(gasa,gasa)` is retained in the
minus-prmtan support, and the two catastrophic discharges remain catastrophic.

**The reconstruction is not reducible to the same-family observable.**
`ID(prmtan_neped)` alone achieves a *better mean* (0.463) than the full
twelve-coordinate support, but a **2.7× worse median** (0.466 vs 0.170). Its
advantage is entirely tail behaviour: a single level coordinate cannot
extrapolate catastrophically, so its worst discharge is 0.96 rather than 11.95.
On the typical discharge it is a much poorer reconstructor.

So the relational construction does add substantial typical-case accuracy over
the semantically close pedestal-density diagnostic on its own — and it also
adds the tail exposure that fails the gate. Both statements are true, and
neither yields a qualified claim: all three objects fail the V3-style
criterion, and `prmtan_neped` alone is nowhere near nontrivial skill either
(`Δ₁ = +0.253`).

## What this does not establish

- It does **not** test physical independence between pedestal and line-averaged
  density.
- It does **not** alter V1, which passed on provenance grounds and remains
  passed.
- It does **not** license adding, removing or substituting any coordinate in
  `C_dev_star`, which is unchanged.
