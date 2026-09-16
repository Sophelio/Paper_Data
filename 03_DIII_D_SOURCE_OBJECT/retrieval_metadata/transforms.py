"""Human-readable reference implementation of the DIIID_SIR_Paper transform family.

This file is the human-readable reference implementation for the
DIIID_SIR_Paper transform family. The runtime Dalia implementations are
embedded in the Dalia project document. These functions are kept
synchronized with the canonical Archaieus implementations and are intended
to make the exact mathematics auditable outside the Dalia project
serialization.

===========================================================================
NOTATION
===========================================================================

The manuscript phase-derivative convention is

    D_g f = (df/dt) / (dg/dt)

so the SUBSCRIPT is the *reference* (denominator) coordinate and the operand
written after it is the numerator.  For example

    D_{x2} x1 = (dx1/dt) / (dx2/dt)

There is no two-subscript form: writing ``D_{x1 x2}`` is ambiguous and is not
used anywhere in this family.  A superscript marks the variant, e.g.
``D^{sc}_{x2} x1`` is the sensitivity-centered coordinate.

===========================================================================
THE TWO-STAGE PIPELINE
===========================================================================

Every relational coordinate here is built in the same two stages:

    stage 1   operand scaling      u = raw / S        (S fitted on a cohort)
    stage 2   relational operator  C = f(u_n, u_d)    (the coordinate)

Archaieus then applies a THIRD stage — a shared Z-score over the completed
coordinate, fitted on the training cohort and frozen
(``conditioning_consumer._complete_one`` -> ``apply_channel_stat``).  In this
file and in the Dalia blocks, the functions return the **pre-Z coordinate**
(what Archaieus stores as ``C_pre_z``), because that is the quantity whose
mathematics is being audited.  In Dalia the shared Z is available separately
as the SIR prep step ``sir_feature_zscore``.

The single exception is `conditioning_aware`, which historically carried its
own Z-score; it is cohort-fitted and frozen here (see its docstring).

===========================================================================
FIT vs APPLY
===========================================================================

`FittedScales`, `ClearanceFit` and `ChannelStat` are the FIT products.  They
are computed once on a training cohort and then FROZEN: applying a transform
to a held-out record must reuse the training values, never re-estimate them.
The only intentionally record-local transform is `per_realization_zscore`,
which is documented as such.

Getting this wrong is not academic.  The original Dalia port re-estimated the
sensitivity-centering constant per record, which silently made training and
held-out records pass through different functions.

===========================================================================
CANONICAL SOURCES
===========================================================================

    Archaieus/sir/utils/conditioning_aware.py     scales, ratios, gains
    Archaieus/sir/utils/channel_normalization.py  channel Z statistics
    Archaieus/sir/conditioning_consumer.py        drivers / operand choice
    Archaieus/sir/consumer_function.py            per-realization Z

Per-transform line references appear in each docstring.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence

import numpy as np

__all__ = [
    "MIN_SCALE",
    "MIN_STD",
    "FittedScales",
    "ChannelStat",
    "finite",
    "pooled_rms",
    "robust_zero_mad",
    "fit_operand_scale",
    "fit_channel_stat",
    "apply_channel_stat",
    "fit_denominator_clearance",
    "regularized_denominator_gain",
    "fit_training_mean_gain",
    "regularized_ratio",
    "clearance_shifted_regularized_ratio",
    "sensitivity_centered_clearance_ratio",
    "tangent_direction_components",
    "per_realization_zscore",
    "per_channel_zscore",
    "conditioning_aware",
    "level_rate_relational",
    "reference_shifted_phase",
    "sensitivity_centered_phase",
    "tangent_direction",
]

# Floor keeping exact-zero operands from producing a zero divisor.
# Archaieus: conditioning_aware.MIN_SCALE.
MIN_SCALE = 1e-15
# Below this a channel is treated as constant rather than Z-scored.
# Archaieus: channel_normalization.fit_channel_stat(min_std=1e-12).
MIN_STD = 1e-12


# ===========================================================================
# Fit containers
# ===========================================================================
@dataclass(frozen=True)
class FittedScales:
    """Operand scales + reference shift, fitted on the training cohort.

    Attributes
    ----------
    S_n, S_d
        Operand scales for the numerator and denominator (pooled RMS or
        robust zero-MAD).  These divide the RAW operands.
    s_0
        Denominator clearance, ``max(0, -min_fit(u_d))``, fitted on the
        **normalized** denominator ``u_d = d / S_d``.
    kappa
        User reference-shift margin.
    rho
        Regularizer half-width.
    g_bar
        Mean denominator gain, only used by the sensitivity-centered
        coordinate; ``None`` for the others.
    """

    S_n: float
    S_d: float
    s_0: float
    kappa: float
    rho: float
    g_bar: Optional[float] = None

    @property
    def s_eff(self) -> float:
        """Effective reference shift ``s_eff = s_0 + kappa``."""
        return float(self.s_0) + float(self.kappa)


@dataclass(frozen=True)
class ChannelStat:
    """Frozen (mean, std) for one channel, pooled over the training cohort."""

    name: str
    mean: float
    std: float
    n_finite: int
    n_realizations: int


# ===========================================================================
# Primitives
# ===========================================================================
def finite(a) -> np.ndarray:
    """Flatten and keep only finite entries. Drops both NaN and +/-Inf."""
    arr = np.asarray(a, dtype=np.float64).reshape(-1)
    return arr[np.isfinite(arr)]


def pooled_rms(samples: Sequence, min_scale: float = MIN_SCALE) -> float:
    """Zero-preserving pooled scale ``sqrt(mean(x^2))`` over all realizations.

    RMS about ZERO, not about the mean.  That is the whole point: a relational
    coordinate divides by this operand, so the scale must preserve the location
    of zero.  Subtracting a mean first would move the denominator's zero and
    change where the regularizer bites.

    Archaieus: ``conditioning_aware.fit_pooled_rms``.
    """
    chunks = [finite(s) for s in samples]
    chunks = [c for c in chunks if c.size]
    if not chunks:
        return float(min_scale)
    pooled = np.concatenate(chunks)
    rms = float(np.sqrt(np.mean(pooled * pooled)))
    if not np.isfinite(rms) or abs(rms) < min_scale:
        return float(min_scale)
    return rms


def robust_zero_mad(samples: Sequence, min_scale: float = MIN_SCALE) -> float:
    """Robust zero-centred scale ``1.4826 * median(|x|)``.

    Same zero-preserving intent as `pooled_rms` but insensitive to heavy tails
    and to a few large excursions.  1.4826 makes it consistent with the
    standard deviation for Gaussian data.

    Falls back to `pooled_rms` when the MAD itself degenerates (a signal that
    is zero more than half the time has median|x| = 0).

    Archaieus: ``conditioning_aware.fit_robust_zero_mad``.
    """
    chunks = [finite(s) for s in samples]
    chunks = [c for c in chunks if c.size]
    if not chunks:
        return float(min_scale)
    pooled = np.concatenate(chunks)
    scale = float(1.4826 * np.median(np.abs(pooled)))
    if not np.isfinite(scale) or abs(scale) < min_scale:
        return pooled_rms(samples, min_scale=min_scale)
    return scale


def fit_operand_scale(samples: Sequence, method: str = "pooled_rms") -> float:
    """Dispatch to `pooled_rms` or `robust_zero_mad`.

    Archaieus: ``conditioning_aware.fit_operand_scale``.
    """
    m = str(method or "pooled_rms").strip().lower()
    if m == "robust_zero_mad":
        return robust_zero_mad(samples)
    if m == "pooled_rms":
        return pooled_rms(samples)
    raise ValueError(f"Unknown scale method {method!r}")


def fit_channel_stat(
    name: str, samples: Sequence, *, ddof: int = 0, min_std: float = MIN_STD
) -> ChannelStat:
    """Pooled (mean, std) for one channel over all training realizations.

    Raises on a constant channel rather than emitting inf/NaN, matching
    Archaieus.  (The Dalia runtime block substitutes std=1.0 instead so a GUI
    plot degrades gracefully; that divergence is recorded in the audit.)

    Archaieus: ``channel_normalization.fit_channel_stat``.
    """
    chunks = [finite(s) for s in samples]
    chunks = [c for c in chunks if c.size]
    if not chunks:
        raise ValueError(f"No finite samples for channel {name!r}")
    pooled = np.concatenate(chunks)
    mean = float(np.mean(pooled))
    std = float(np.std(pooled, ddof=ddof))
    if not np.isfinite(std) or abs(std) < min_std:
        raise ValueError(
            f"Per-channel Z-score failed for {name!r}: std is zero or "
            f"non-finite (std={std!r}, n={pooled.size})."
        )
    return ChannelStat(
        name=str(name),
        mean=mean,
        std=std,
        n_finite=int(pooled.size),
        n_realizations=len(chunks),
    )


def apply_channel_stat(a, stat: ChannelStat) -> np.ndarray:
    """Apply frozen channel statistics: ``(x - mu) / sigma``."""
    return (np.asarray(a, dtype=np.float64) - stat.mean) / stat.std


# ===========================================================================
# Reference-shift machinery
# ===========================================================================
def fit_denominator_clearance(u_d_samples: Sequence) -> float:
    """Training clearance ``s_0 = max(0, -min_fit(u_d))``.

    The argument must be the **already-normalized** denominator ``u_d = d/S_d``.
    Computing the clearance from the raw rate and then adding it to a
    normalized quantity mixes coordinate systems: the shift is then larger than
    ``u_d`` by the scale factor, the gain ``g`` saturates to a constant, and the
    coordinate silently degenerates into a rescaled numerator.  That was the
    original defect in the Dalia port (see the audit report).

    ``s_0`` is the smallest non-negative shift that lifts the most negative
    training denominator up to zero, so that ``w = u_d + s_eff`` clears the sign
    region and the regularizer acts symmetrically.

    Archaieus: ``conditioning_aware.fit_denominator_clearance`` (line 210),
    called at ``conditioning_consumer._clearance_for`` (line 314).
    """
    chunks = [finite(s) for s in u_d_samples]
    chunks = [c for c in chunks if c.size]
    if not chunks:
        return 0.0
    return float(max(0.0, -np.min(np.concatenate(chunks))))


def regularized_denominator_gain(u_d, rho: float, s_eff: float) -> np.ndarray:
    """Regularized denominator gain ``g(w) = w / (w^2 + rho^2)``, ``w = u_d + s_eff``.

    This is the factor common to the whole reference-shifted family.  It is a
    smooth stand-in for ``1/w``: away from zero ``g -> 1/w``, but instead of
    diverging it peaks at ``w = rho`` with value ``1/(2*rho)`` and returns to
    zero.  ``rho`` therefore sets both the largest attainable gain and the width
    of the neighbourhood of the denominator's turning point over which the
    coordinate stays bounded.

    Archaieus: ``conditioning_aware.regularized_denominator_gain`` (line 246).
    """
    w = np.asarray(u_d, dtype=np.float64) + float(s_eff)
    return w / (w * w + float(rho) ** 2)


def fit_training_mean_gain(g_samples: Sequence) -> float:
    """Frozen training mean gain ``g_bar = mean_fit[g]``.

    Only the sensitivity-centered coordinate uses this.  Pooled over every
    training realization and then frozen, so held-out records are centered by
    the SAME constant.

    Archaieus: ``conditioning_aware.fit_training_mean_gain`` (line 277),
    called at ``conditioning_consumer._mean_gain_for`` (line 330).
    """
    chunks = [finite(s) for s in g_samples]
    chunks = [c for c in chunks if c.size]
    if not chunks:
        raise ValueError("No finite gain samples to fit g_bar")
    return float(np.mean(np.concatenate(chunks)))


# ===========================================================================
# Relational operators (pure math core)
# ===========================================================================
def regularized_ratio(u_n, u_d, rho: float) -> np.ndarray:
    """Unshifted regularized quotient ``C = u_n * u_d / (u_d^2 + rho^2)``.

    The plain regularized stand-in for ``u_n / u_d``.  No reference shift, so
    it changes sign with the denominator and passes through zero where the
    denominator does.  Use it when the denominator is not expected to change
    sign, or when sign changes are themselves the signal.

    Archaieus: ``conditioning_aware.regularized_ratio`` (line 202).
    """
    u_n = np.asarray(u_n, dtype=np.float64)
    u_d = np.asarray(u_d, dtype=np.float64)
    return u_n * u_d / (u_d * u_d + float(rho) ** 2)


def clearance_shifted_regularized_ratio(u_n, u_d, rho: float, s_eff: float) -> np.ndarray:
    """Reference-shifted regularized quotient ``C_RS = (u_n + s_eff) * g(w)``.

    Equivalently ``(u_n + s) * (u_d + s) / ((u_d + s)^2 + rho^2)`` with
    ``s = s_eff``.  With ``s_eff = 0`` it reduces to `regularized_ratio`.

    BOTH operands receive the shift.  The denominator shift is what the
    clearance is for — it moves the whole training denominator to one side of
    zero so the quotient stops flipping sign.  The numerator shift keeps the
    pair on a common origin, so the coordinate remains a quotient of two
    comparably-shifted quantities rather than a shifted denominator dividing an
    unshifted numerator.  Dropping the numerator shift (as the original Dalia
    port did) does not merely rescale the result; it removes the ``s_eff * g``
    term, which is precisely the part that survives where ``u_n -> 0``.

    Archaieus: ``conditioning_aware.clearance_shifted_regularized_ratio`` (226).
    """
    s_eff = float(s_eff)
    if not np.isfinite(s_eff) or s_eff < 0:
        raise ValueError(f"s_eff must be >= 0; got {s_eff!r}")
    u_n = np.asarray(u_n, dtype=np.float64)
    return (u_n + s_eff) * regularized_denominator_gain(u_d, rho, s_eff)


def sensitivity_centered_clearance_ratio(
    u_n, u_d, rho: float, s_eff: float, g_bar: float
) -> np.ndarray:
    """Sensitivity-centered coordinate ``C_SC = C_RS - g_bar * u_n``.

    Equivalently::

        C_SC = u_n * (g - g_bar) + s_eff * g

    WHAT "SENSITIVITY-CENTERED" MEANS.  The derivative of ``C_RS`` with respect
    to the numerator is ``dC_RS/du_n = g``.  Subtracting ``g_bar * u_n`` removes
    the *mean* of that sensitivity, leaving ``dC_SC/du_n = g - g_bar``, which by
    construction averages to zero over the training cohort::

        mean_fit(g - g_bar) = 0

    So the coordinate responds to the numerator only where the denominator gain
    departs from its typical value — i.e. near denominator turning points, which
    is exactly where relational information lives.

    THIS IS NOT MEAN-CENTERING.  ``C_RS - mean(C_RS)`` would merely force the
    OUTPUT to have zero mean, which removes no sensitivity at all and leaves
    ``dC/du_n = g`` unchanged.  The two are different functions.  Do not call a
    coordinate "sensitivity centered" because its output mean is zero.

    ``g_bar = 0`` recovers `clearance_shifted_regularized_ratio`.

    Archaieus: ``conditioning_aware.sensitivity_centered_clearance_ratio`` (257);
    driver ``conditioning_consumer`` lines 1013-1032 (target phase) and
    758-774 (feature phase).
    """
    u_n = np.asarray(u_n, dtype=np.float64)
    g = regularized_denominator_gain(u_d, rho, s_eff)
    return (u_n + float(s_eff)) * g - float(g_bar) * u_n


def tangent_direction_components(u_n, u_d, rho: float):
    """Regularized unit tangent ``(T_n, T_d) = (u_n, u_d) / R``.

    with ``R = sqrt(u_n^2 + u_d^2 + rho^2)``.

    NOT a quotient and NOT an angle.  This is the direction of the operand pair
    with its magnitude divided out, kept as two Cartesian components rather than
    ``atan2``.  That choice matters: an angle wraps at +/-pi, so a trajectory
    passing through that branch produces a spurious jump; the component pair is
    continuous everywhere.

    ``rho`` regularizes the zero-speed point.  Without it the direction is
    undefined where both operands vanish; with it ``R >= rho`` and the pair
    smoothly shrinks toward ``(0, 0)`` instead of becoming ill-conditioned.
    Consequently ``T_n^2 + T_d^2 = (u_n^2 + u_d^2) / R^2 <= 1``, approaching 1
    when the operands are large compared with ``rho`` and 0 at a stagnation
    point — so the pair encodes direction while remaining well defined.

    There are no fitted quantities beyond the operand scales.

    HOW IT DIFFERS from the phase coordinates: a phase derivative
    ``D_g f = (df/dt)/(dg/dt)`` is a RATIO and therefore diverges where the
    reference rate vanishes; the reference-shifted family tames that with a
    shift and a regularizer.  The tangent-direction coordinate never forms the
    ratio at all, so it has nothing to diverge — at the cost of not being a
    derivative: it is scale-free in the pair jointly but is NOT invariant to
    rescaling one operand alone.

    Archaieus: ``conditioning_aware.tangent_direction_components`` (line 331).
    """
    u_n = np.asarray(u_n, dtype=np.float64)
    u_d = np.asarray(u_d, dtype=np.float64)
    R = np.sqrt(u_n * u_n + u_d * u_d + float(rho) ** 2)
    return u_n / R, u_d / R


# ===========================================================================
# Transform-level entry points
# ===========================================================================
def per_realization_zscore(values) -> np.ndarray:
    """Per-Realization Z-score — INTENTIONALLY record-local.

    ``z_r(t) = (x_r(t) - mu_r) / sigma_r`` with ``mu_r``, ``sigma_r`` computed
    from realization ``r`` ALONE.

    This is the one transform in the family whose statistics are deliberately
    not cohort-fitted and not frozen.  Applying it to a new realization
    computes NEW local statistics, and that is the design: it removes each
    record's own offset and amplitude so that shot-to-shot gain and calibration
    differences do not dominate, leaving only within-shot shape.

    The trade-off is that it destroys cross-record comparability of absolute
    level — two shots that genuinely differ in magnitude become identical after
    it.  When you need that comparability, use `per_channel_zscore`, whose
    statistics are pooled and frozen.

    Degenerate handling: a constant record has ``sigma_r = 0``; this returns
    zeros rather than NaN/Inf.  (Archaieus' ``scipy.stats.zscore`` yields
    NaN/Inf there; the difference only shows on constant records.)  NaNs are
    ignored when estimating ``mu_r``/``sigma_r`` and remain NaN in the output.

    Archaieus: ``consumer_function`` line 309, ``zscore(x, axis=-1)`` under
    ``total_normalization`` (mode ``per_realization``).
    """
    v = np.asarray(values, dtype=np.float64)
    if v.size == 0:
        return v.copy()
    mean = np.nanmean(v)
    std = np.nanstd(v)
    if not np.isfinite(std) or std == 0:
        return np.zeros_like(v)
    return (v - mean) / std


def per_channel_zscore(values, stat: ChannelStat) -> np.ndarray:
    """Per-Channel Z-score — cohort-fitted and FROZEN.

    ``z = (x - mu_channel) / sigma_channel`` where "channel" is one *semantic
    signal* (``ip``, ``q95``, ...), and ``mu``/``sigma`` are pooled over BOTH
    time and every training realization — one number per signal for the whole
    cohort, not one per record.

    Because the statistics are frozen, a held-out record is mapped through
    exactly the same affine function as the training records, so absolute
    levels stay comparable across shots.  That is the precise opposite of
    `per_realization_zscore`, and the two must not be substituted for each
    other.

    Fit with `fit_channel_stat`, which raises on a constant channel.

    Archaieus: ``channel_normalization.fit_channel_stat`` /
    ``apply_channel_stat`` (lines 134, 182).
    """
    return apply_channel_stat(values, stat)


def conditioning_aware(
    u_n, u_d=None, *, rho: float = 0.1, stat: Optional[ChannelStat] = None
) -> np.ndarray:
    """Conditioning-aware standardization.

    Two forms, selected by whether a denominator operand is supplied.

    SCALE-ONLY (``u_d is None``).  The operand is divided by a zero-preserving
    pooled scale and then shared-Z-scored.  WHY NOT PLAIN Z-SCORING: an
    ordinary Z-score subtracts the mean first, which moves the signal's zero.
    For a quantity that will later be used as a denominator, or whose sign is
    physically meaningful, that is destructive — "zero current" must stay at
    zero.  The pooled-RMS scale normalizes magnitude *about zero*, and only
    afterwards is a frozen shared Z applied for conditioning.

    RATIO (``u_d`` supplied).  ``C = regularized_ratio(u_n, u_d, rho)``, then
    the frozen shared Z.  Both operands are LEVELS, each divided by its own
    cohort operand scale.

    The Z statistics are fitted on the training cohort and frozen; pass them in
    via ``stat``.  Omitting ``stat`` returns the pre-Z coordinate.

    RELATION TO NEIGHBOURS: this is the unshifted member of the family.  It has
    no clearance and no ``kappa``, so it changes sign wherever the denominator
    does.  `level_rate_relational` and `reference_shifted_phase` add the shift
    to prevent exactly that.

    Archaieus: ``conditioning_consumer._build_physical_quotients`` (line 566,
    level/level, ``get_scale("level", ...)``) and ``_build_x_phase`` default
    branch (line 868, rate/rate).  Shared Z via ``_complete_one`` (line 472).
    """
    if u_d is None:
        out = np.asarray(u_n, dtype=np.float64)
    else:
        out = regularized_ratio(u_n, u_d, rho)
    if stat is not None:
        out = apply_channel_stat(out, stat)
    return out


def level_rate_relational(u_level, u_d_rate, scales: FittedScales) -> np.ndarray:
    """Level-rate relational coordinate.

    ``C = (u_level + s_eff) * g(w)``, ``w = u_d_rate + s_eff``.

    The numerator is a scaled **LEVEL** ``y``; the denominator is a scaled
    **RATE** ``dx_j/dt``.  It answers "how much of this quantity per unit change
    in that reference" — a level compared against a rate, which is why it is
    NOT a phase derivative and NOT dimensionless in the same way.

    IT SHARES THE FORMULA of `reference_shifted_phase`.  Archaieus builds both
    with the same `clearance_shifted_regularized_ratio`; the ONLY difference is
    the numerator operand — level here, ``dy/dt`` there.  Archaieus flags this
    explicitly as the "CRITICAL SEMANTIC SPLIT of the target-phase numerator"
    (``conditioning_consumer`` lines 1132-1156).  Do not infer from the shared
    helper that they are the same coordinate; they are not, and their units
    differ.

    Fitted and frozen: ``S_n`` (level scale), ``S_d`` (rate scale), ``s_0`` on
    the normalized rate.

    Archaieus: ``conditioning_consumer`` lines 1139-1174 (level numerator) and
    818-831 (feature-feature variant).
    """
    return clearance_shifted_regularized_ratio(
        u_level, u_d_rate, scales.rho, scales.s_eff
    )


def reference_shifted_phase(u_n_rate, u_d_rate, scales: FittedScales) -> np.ndarray:
    """Reference-shifted regularized phase ``D^{rs}_{g} f``.

    ``C_RS = (u_n + s_eff) * g(w)``, ``w = u_d + s_eff``.

    A true phase derivative: BOTH operands are rates, so this is the regularized
    stand-in for ``(df/dt)/(dg/dt)``.  The reference shift ``s_eff = s_0 +
    kappa`` moves the training denominator clear of zero so the quotient does
    not flip sign, and ``rho`` bounds the gain where it still passes close.

    ``kappa`` is the user's margin ON TOP of the fitted clearance: ``s_0`` only
    just reaches zero, so ``kappa > 0`` buys headroom for held-out records whose
    denominator dips below anything seen in training.  ``kappa = 0`` is legal
    and leaves held-out excursions unprotected.

    Fitted and frozen: ``S_n``, ``S_d``, ``s_0`` (on the NORMALIZED denominator).

    RELATION TO NEIGHBOURS: `conditioning_aware` is this without the shift;
    `sensitivity_centered_phase` is this minus ``g_bar * u_n``;
    `level_rate_relational` is this with a level numerator.

    Archaieus: ``conditioning_consumer`` lines 1151-1174 and 818-834.
    """
    return clearance_shifted_regularized_ratio(
        u_n_rate, u_d_rate, scales.rho, scales.s_eff
    )


def sensitivity_centered_phase(u_n_rate, u_d_rate, scales: FittedScales) -> np.ndarray:
    """Sensitivity-centered reference-shifted regularized phase ``D^{sc}_{g} f``.

    ``C_SC = C_RS - g_bar * u_n = u_n * (g - g_bar) + s_eff * g``

    See `sensitivity_centered_clearance_ratio` for what the centering means and
    why it is not mean-centering.  ``g_bar`` must come from `FittedScales` and
    must have been fitted on the training cohort.

    Fitted and frozen: ``S_n``, ``S_d``, ``s_0``, and ``g_bar``.

    Archaieus: ``conditioning_consumer`` lines 1013-1032.
    """
    if scales.g_bar is None:
        raise ValueError(
            "sensitivity_centered_phase requires a fitted g_bar; "
            "FittedScales.g_bar is None"
        )
    return sensitivity_centered_clearance_ratio(
        u_n_rate, u_d_rate, scales.rho, scales.s_eff, scales.g_bar
    )


def tangent_direction(u_n, u_d, rho: float = 0.1, component: str = "numerator"):
    """Tangent-direction coordinate — one component of the regularized unit tangent.

    See `tangent_direction_components` for the geometry, the reason components
    are preferred over an angle, and the role of ``rho``.

    ``component`` selects ``"numerator"`` (``T_n``) or ``"denominator"``
    (``T_d``); ``"both"`` returns the pair.  Archaieus always emits BOTH as two
    separate coordinates (``td_num_*`` and ``td_den_*``): they are not
    redundant, since together they fix the direction and their common shrinkage
    encodes proximity to a stagnation point.  Reporting only ``T_n`` discards
    that.

    No fitted quantities beyond the operand scales.

    Archaieus: ``conditioning_consumer`` lines 712-756 (rate/rate) and 916-939
    (level/rate).
    """
    T_n, T_d = tangent_direction_components(u_n, u_d, rho)
    c = str(component).strip().lower()
    if c in ("numerator", "num", "n"):
        return T_n
    if c in ("denominator", "den", "d"):
        return T_d
    if c == "both":
        return T_n, T_d
    raise ValueError(f"Unknown component {component!r}")


# ===========================================================================
# Convenience: fit the reference-shifted family in one call
# ===========================================================================
def fit_reference_shifted(
    numerator_samples: Iterable,
    denominator_samples: Iterable,
    *,
    rho: float = 0.1,
    kappa: float = 1.0,
    scale_method: str = "pooled_rms",
    with_mean_gain: bool = False,
) -> FittedScales:
    """Fit the whole reference-shifted family on a training cohort.

    ORDER MATTERS and is the point of this helper:

        1. fit ``S_n``, ``S_d`` from the RAW operands;
        2. normalize ``u_d = d / S_d``;
        3. fit ``s_0`` from the NORMALIZED ``u_d``;
        4. only then, if needed, fit ``g_bar`` from ``g(u_d + s_eff)``.

    Steps 2-3 must not be swapped.  Fitting the clearance before normalizing
    produces a shift carrying the denominator's physical units, which is then
    added to a dimensionless quantity.

    Pass ``with_mean_gain=True`` for the sensitivity-centered coordinate.
    """
    num = list(numerator_samples)
    den = list(denominator_samples)
    S_n = fit_operand_scale(num, scale_method)
    S_d = fit_operand_scale(den, scale_method)

    u_d_list = [np.asarray(d, dtype=np.float64) / S_d for d in den]
    s_0 = fit_denominator_clearance(u_d_list)
    s_eff = s_0 + float(kappa)

    g_bar = None
    if with_mean_gain:
        g_bar = fit_training_mean_gain(
            [regularized_denominator_gain(u_d, rho, s_eff) for u_d in u_d_list]
        )

    return FittedScales(
        S_n=S_n, S_d=S_d, s_0=s_0, kappa=float(kappa), rho=float(rho), g_bar=g_bar
    )
