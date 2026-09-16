"""Generate the random-coefficient harmonic-oscillator ensemble (paper Sec. on SHO).

We draw an ensemble of functions

    h_alpha(x) = sin(alpha * pi * x),     alpha ~ U[1, 2],

each of which satisfies the harmonic-oscillator relation

    d^2 h_alpha / dx^2 + (alpha * pi)^2 h_alpha = 0,

with a coefficient (alpha*pi)^2 that varies from realization to realization. The
goal of the SIR example is to recover the *shared relational form*
``a * d2h/dx2 + b * h = 0`` for every realization, and to reconstruct the
distribution of the latent parameter alpha from the recovered ratios
``-b/a ~= (alpha*pi)^2``.

Running this script:
  * generates ``N_REALIZATIONS`` realizations sampled on a uniform grid of
    ``N_POINTS`` points,
  * writes one parquet per realization into ``data/`` with columns
    ``times, h, dh, d2h, alpha`` so it can be ingested by an SIR data provider
    (see ``stochastic_oscillator_data_provider.py``),
  * renders publication-grade figures (the ensemble of curves and the true
    parameter distribution) as high-dpi PNG and vector PDF.

``times`` is the spatial coordinate ``x`` (named ``times`` to match the SIR
provider contract). ``dh``/``d2h`` are the analytic ("exact") derivatives;
``alpha`` is constant per file and is treated as metadata by the provider.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import Normalize


# --------------------------------------------------------------------------
# Ensemble parameters
# --------------------------------------------------------------------------
N_REALIZATIONS = 40
N_POINTS = 10_000
X_MIN = 0.0
X_MAX = float(np.pi)
ALPHA_LOW = 1.0
ALPHA_HIGH = 2.0
SEED = 0

OUTPUT_DIR = Path(__file__).resolve().parent
DATA_DIR = OUTPUT_DIR / "data"


# --------------------------------------------------------------------------
# Ensemble generation
# --------------------------------------------------------------------------
def generate_realization(alpha, n_points=N_POINTS, x_min=X_MIN, x_max=X_MAX):
    """Return a DataFrame for one realization h_alpha(x) = sin(alpha*pi*x).

    Columns ``times, h, dh, d2h, alpha``. ``dh``/``d2h`` are the analytic
    derivatives; note ``d2h == -(alpha*pi)**2 * h`` (the oscillator relation).
    """
    x = np.linspace(x_min, x_max, n_points).astype(np.float64)
    w = alpha * np.pi
    h = np.sin(w * x)
    dh = w * np.cos(w * x)
    d2h = -(w**2) * np.sin(w * x)

    return pd.DataFrame(
        {
            "times": x,
            "h": h.astype(np.float64),
            "dh": dh.astype(np.float64),
            "d2h": d2h.astype(np.float64),
            "alpha": np.full(n_points, float(alpha), dtype=np.float64),
        }
    )


def generate_ensemble(n=N_REALIZATIONS, seed=SEED):
    """Draw ``n`` alphas ~ U[ALPHA_LOW, ALPHA_HIGH] and build their realizations.

    Returns ``(alphas, frames)`` where ``frames[i]`` is the DataFrame for
    ``alphas[i]``.
    """
    rng = np.random.default_rng(seed)
    alphas = rng.uniform(ALPHA_LOW, ALPHA_HIGH, size=n).astype(np.float64)
    frames = [generate_realization(a) for a in alphas]
    return alphas, frames


# --------------------------------------------------------------------------
# Publication-grade plotting
# --------------------------------------------------------------------------
def _set_publication_style():
    """A compact serif style suitable for PRL / Nature single-column figures."""
    mpl.rcParams.update(
        {
            "figure.dpi": 150,
            "savefig.dpi": 800,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.02,
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
            "mathtext.fontset": "cm",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.size": 9,
            "axes.labelsize": 10,
            "axes.titlesize": 10,
            "legend.fontsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "axes.linewidth": 0.8,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.top": True,
            "ytick.right": True,
            "xtick.major.size": 3.5,
            "ytick.major.size": 3.5,
            "xtick.minor.size": 2.0,
            "ytick.minor.size": 2.0,
            "lines.linewidth": 1.0,
            "legend.frameon": False,
            "axes.grid": False,
        }
    )


def plot_ensemble(alphas, frames, out_stem: Path):
    """Overlay all realizations h_alpha(x), colored by alpha."""
    norm = Normalize(vmin=ALPHA_LOW, vmax=ALPHA_HIGH)
    cmap = cm.viridis

    fig, ax = plt.subplots(figsize=(3.5, 2.7))
    for alpha, df in zip(alphas, frames):
        ax.plot(
            df["times"].to_numpy(),
            df["h"].to_numpy(),
            color=cmap(norm(alpha)),
            linewidth=0.7,
            alpha=0.85,
        )

    ax.set_xlabel(r"$x$")
    ax.set_ylabel(r"$h_\alpha(x)=\sin(\alpha\pi x)$")
    ax.set_xlim(X_MIN, X_MAX)
    ax.margins(y=0.05)
    ax.minorticks_on()

    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, pad=0.02, aspect=22)
    cbar.set_label(r"$\alpha$", rotation=0, labelpad=7)
    cbar.outline.set_linewidth(0.6)

    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(out_stem.with_suffix(f".{ext}"))
    plt.close(fig)


def plot_parameter_distribution(alphas, out_stem: Path):
    """True distributions of alpha and of the oscillator coefficient (alpha*pi)^2."""
    coeff = (alphas * np.pi) ** 2

    fig, axes = plt.subplots(1, 2, figsize=(5.2, 2.4))

    axes[0].hist(alphas, bins=10, range=(ALPHA_LOW, ALPHA_HIGH),
                 color="#1b3a6b", edgecolor="white", linewidth=0.6, density=True)
    axes[0].axhline(1.0 / (ALPHA_HIGH - ALPHA_LOW), color="#a6171b",
                    linewidth=1.0, linestyle="--", label=r"$U[1,2]$")
    axes[0].set_xlabel(r"$\alpha$")
    axes[0].set_ylabel("density")
    axes[0].legend(loc="upper right")
    axes[0].minorticks_on()

    axes[1].hist(coeff, bins=12, color="#1f7a3d", edgecolor="white", linewidth=0.6,
                 density=True)
    axes[1].set_xlabel(r"$(\alpha\pi)^2$")
    axes[1].set_ylabel("density")
    axes[1].minorticks_on()

    fig.tight_layout(w_pad=1.5)
    for ext in ("png", "pdf"):
        fig.savefig(out_stem.with_suffix(f".{ext}"))
    plt.close(fig)


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------
def main():
    _set_publication_style()

    alphas, frames = generate_ensemble()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    width = len(str(N_REALIZATIONS - 1))
    for i, df in enumerate(frames):
        path = DATA_DIR / f"realization_{i:0{width}d}.parquet"
        df.to_parquet(path, index=False)
    print(f"Wrote {len(frames)} realizations ({N_POINTS} pts each) -> {DATA_DIR}")
    print(f"Columns: {list(frames[0].columns)}")
    print(f"alpha range: [{alphas.min():.4f}, {alphas.max():.4f}]")

    plot_ensemble(alphas, frames, OUTPUT_DIR / "sho_ensemble")
    plot_parameter_distribution(alphas, OUTPUT_DIR / "sho_parameter_distribution")
    print(f"Saved figures (png + pdf) to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
