# Coordinate audit

**Date:** 2026-08-27

## Grammar — 38 candidates, finite and declared

| Family | n | Members |
|---|---|---|
| raw | 10 | x, y at k−2 … k+2 (the declared information boundary) |
| rate | 2 | dx, dy — 4th-order centered 5-point |
| curvature | 2 | d2x, d2y — 4th-order centered 5-point |
| product | 8 | x·y, x², y², x·dy, y·dx, dx·dy, x·dx, y·dy |
| quotient | 4 | masked `Q[num|den]`; includes the classical phase derivatives `Q[ẏ|ẋ] = D_x y` and `Q[ẋ|ẏ] = D_y x` |
| ca_ratio | 4 | `CA = u_n·u_d/(u_d² + ρ²)`, unshifted |
| reference_shifted | 4 | `RS = (u_n + s_eff)·g(w)` |
| sensitivity_centered | 4 | `SC = RS − ḡ·u_n` |

Numerator/denominator pairs: (ẏ|x), (y|x), (ẏ|ẋ), (ẋ|ẏ).

Denominators include **levels** (x) as well as **rates**, because in this system
the z-information lives in quotients with a level denominator. The grammar admits
both and lets the search choose; neither is weighted or forced.

Notation: `D_g f = (df/dt)/(dg/dt)` — the subscript is the reference.

## Canonical implementations

RS and SC are imported from `D:/SIR_paper/DIIID_example/transforms.py`, verified
elementwise (rtol=0, atol=1e-12) against Archaieus in
`AUDIT_dalia_transform_family.md`. No ad hoc formula was substituted.

Fitted on **train only**, then frozen:

| Pair | s_0 | s_eff | ḡ |
|---|---|---|---|
| ẏ \| x | 2.37710 | 3.37710 | 0.323787 |
| y \| x | 2.37710 | 3.37710 | 0.323787 |
| ẏ \| ẋ | 2.97362 | 3.97362 | 0.271020 |
| ẋ \| ẏ | 4.23232 | 5.23232 | 0.199743 |

ρ = 0.1, κ = 1.0, `pooled_rms` — canonical defaults, **not tuned** against any
split.

## Conditioning and coverage

Masked quotients drop samples where |denominator| falls below the 5th train
percentile. Combined with the stencil interior this retains **88.5%** of test
samples; every method is scored on that same support.

Condition numbers of the standardised train matrix:

| Representation | cond |
|---|---|
| C0 (10) | 2.6×10¹² |
| C_all (38) | **7.5×10¹⁶** — effectively rank-deficient |
| C* (12) | 2.6×10¹² |

C_all is numerically the worst-conditioned representation. C* is four orders
better while achieving comparable accuracy — a substantive parsimony argument
independent of RMSE.

## What the search selected, reported as found

    C* = C0 + { Q[ẏ|x], Q[y|x] }

The **plain masked quotients** — not the phase derivative `D_x y`, and not the
reference-shifted or sensitivity-centered variants, all of which were available
and were not chosen.

This is reported without massaging. On noiseless data the shift and
regularisation that RS/SC provide are unnecessary, and the plain quotient is the
more direct coordinate; the search preferred it. That outcome is consistent with
the SIR thesis — the procedure determines the construction rather than the
analyst asserting it — and it is deliberately *not* presented as a win for the
phase-derivative family.

The two selected coordinates are exactly those appearing in the analytic identity
`z = ρ − (ẏ + y)/x`, which was used only for auditing and was never supplied to
the search.
