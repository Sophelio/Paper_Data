from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path as MplPath
from matplotlib.patches import Ellipse, FancyBboxPatch, PathPatch

# This is an intentionally separate rendering variant; v14 and its outputs
# remain untouched.
# Outputs go to the figure folder (the parent of figure_source/).
OUT = Path(__file__).resolve().parents[1]
OUT.mkdir(parents=True, exist_ok=True)
STEM = "admissible_relational_space_hierarchical_v15_metaball"
PNG_PATH = OUT / f"{STEM}.png"
PDF_PATH = OUT / f"{STEM}.pdf"
SVG_PATH = OUT / f"{STEM}.svg"

LM_DESIGN_SIZE_PIN = (
    r"\DeclareFontFamily{T1}{lmr}{}"
    r"\DeclareFontShape{T1}{lmr}{m}{n}{<-> ec-lmr10}{}"
    r"\DeclareFontShape{T1}{lmr}{m}{it}{<-> ec-lmri10}{}"
    r"\DeclareFontShape{T1}{lmr}{bx}{n}{<-> ec-lmbx10}{}"
    r"\DeclareFontShape{T1}{lmr}{bx}{it}{<-> ec-lmbxi10}{}"
    r"\DeclareFontShape{T1}{lmr}{b}{n}{<->ssub * lmr/bx/n}{}"
    r"\DeclareFontFamily{OT1}{lmr}{}"
    r"\DeclareFontShape{OT1}{lmr}{m}{n}{<-> rm-lmr10}{}"
    r"\DeclareFontShape{OT1}{lmr}{m}{it}{<-> rm-lmri10}{}"
    r"\DeclareFontShape{OT1}{lmr}{bx}{n}{<-> rm-lmbx10}{}"
    r"\DeclareFontShape{OT1}{lmr}{b}{n}{<->ssub * lmr/bx/n}{}"
    r"\DeclareFontFamily{OML}{lmm}{\skewchar\font127 }"
    r"\DeclareFontShape{OML}{lmm}{m}{it}{<-> lmmi10}{}"
    r"\DeclareFontShape{OML}{lmm}{b}{it}{<-> lmmib10}{}"
    r"\DeclareFontShape{OML}{lmm}{bx}{it}{<->ssub * lmm/b/it}{}"
    r"\DeclareFontFamily{OMS}{lmsy}{\skewchar\font48 }"
    r"\DeclareFontShape{OMS}{lmsy}{m}{n}{<-> lmsy10}{}"
    r"\DeclareFontShape{OMS}{lmsy}{b}{n}{<-> lmbsy10}{}"
)


# Latin Modern via LaTeX, matching the manuscript. Font sizes are the original
# canvas sizes (the canvas prints at about half size at 183 mm).
mpl.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "text.latex.preamble": (
        r"\usepackage[T1]{fontenc}"
        r"\usepackage{lmodern}"
        r"\usepackage{amsmath,amssymb}"
        + LM_DESIGN_SIZE_PIN
    ),
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "path",
})

DARK = "#0D4B25"
MID = "#5E8F63"
MID2 = "#7FA37C"
FIELD = "#F1F2E8"
FIELD_EDGE = "#9EB89C"
FIELD_HALO = "#DCE6D8"
CAT_A = "#DCE6D0"
CAT_B = "#D3E1C8"
CAT_C = "#E3E8C9"
SUB = "#F1F5EC"
AMBER = "#274C77"
AMBER_FILL = "#DCE6F2"
FAINT = "#B9CCB7"


def closed_path(points):
    """Create an explicitly closed Matplotlib path from an Nx2 array."""
    pts = np.asarray(points, dtype=float)
    verts = np.vstack([pts, pts[0]])
    codes = np.full(len(verts), MplPath.LINETO, dtype=np.uint8)
    codes[0] = MplPath.MOVETO
    codes[-1] = MplPath.CLOSEPOLY
    return MplPath(verts, codes)


def polygon_area(points):
    pts = np.asarray(points, dtype=float)
    x = pts[:, 0]
    y = pts[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def resample_closed_curve(points, n=440):
    """Uniformly resample a closed contour to keep vector exports compact."""
    pts = np.asarray(points, dtype=float)
    if np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]
    ring = np.vstack([pts, pts[0]])
    seg = np.linalg.norm(np.diff(ring, axis=0), axis=1)
    cumulative = np.concatenate([[0.0], np.cumsum(seg)])
    targets = np.linspace(0.0, cumulative[-1], n, endpoint=False)
    x = np.interp(targets, cumulative, ring[:, 0])
    y = np.interp(targets, cumulative, ring[:, 1])
    return np.column_stack([x, y])


def amoeba_points(cx, cy, rx, ry, phase=0.0, amp1=0.070, amp2=0.036,
                  amp3=0.018, n=420):
    th = np.linspace(0, 2 * np.pi, n, endpoint=True)
    r = (
        1
        + amp1 * np.sin(2 * th + phase)
        + amp2 * np.sin(3 * th - 0.73 * phase)
        + amp3 * np.sin(5 * th + 0.37 * phase)
    )
    return th, cx + rx * r * np.cos(th), cy + ry * r * np.sin(th)


def amoeba_patch(cx, cy, rx, ry, phase=0.0, facecolor=CAT_A,
                 edgecolor=MID, lw=0.72, alpha=0.48, zorder=2,
                 amp1=0.070, amp2=0.036, amp3=0.018):
    _, x, y = amoeba_points(cx, cy, rx, ry, phase, amp1, amp2, amp3)
    return PathPatch(
        closed_path(np.column_stack([x, y])),
        facecolor=facecolor,
        edgecolor=edgecolor,
        lw=lw,
        alpha=alpha,
        zorder=zorder,
        joinstyle="round",
    )


CLOUD_LOBES = (
    (-0.66, -0.08, 0.50),
    (-0.22, 0.30, 0.58),
    (0.28, 0.16, 0.54),
    (0.62, -0.18, 0.42),
    (0.02, -0.34, 0.46),
)


def cloud_path(cx, cy, scale, rotation=0.0, level=0.78, nx=190):
    """
    Build a puffy thought-bubble outline as the smooth union of round lobes.

    A metaball union yields one continuous scalloped contour, which reads as an
    organic thought cloud instead of a geometric circle or a wobbly ellipse.
    """
    span = 2.0 * scale
    gx = np.linspace(cx - span, cx + span, nx)
    gy = np.linspace(cy - span, cy + span, nx)
    xx, yy = np.meshgrid(gx, gy)

    cos_a, sin_a = np.cos(rotation), np.sin(rotation)
    field = np.zeros_like(xx)
    for dx, dy, lobe_r in CLOUD_LOBES:
        px = cx + (cos_a * dx - sin_a * dy) * scale
        py = cy + (sin_a * dx + cos_a * dy) * scale
        field += np.exp(
            -0.5 * (((xx - px) ** 2 + (yy - py) ** 2) / (lobe_r * scale) ** 2)
        )

    probe_fig, probe_ax = plt.subplots(figsize=(2, 2))
    contour = probe_ax.contour(xx, yy, field, levels=[level])
    segments = [seg for seg in contour.allsegs[0] if len(seg) >= 12]
    plt.close(probe_fig)
    if not segments:
        raise RuntimeError("Thought-bubble field produced no usable contour.")

    return closed_path(
        resample_closed_curve(max(segments, key=polygon_area), n=220)
    )


def category_points(cx, cy, rx, ry, phase=0.0, top_widen=0.08, n=440):
    """Fluid, title-safe category organelle."""
    th = np.linspace(0, 2 * np.pi, n, endpoint=True)
    # Stronger low-frequency lobes give a cytoplasmic organelle silhouette
    # rather than a near-ellipse. Deviations are biased outward so the boundary
    # bulges organically without eroding the interior room needed by the title
    # and subfamily capsules.
    deviation = (
        0.098 * np.sin(2 * th + phase)
        + 0.054 * np.sin(3 * th - 0.73 * phase)
        + 0.026 * np.sin(5 * th + 0.37 * phase)
    )
    # Outward-biased so the interior stays roomy, and damped vertically so the
    # bulges never close the horizontal channels that carry the row captions.
    signed = np.where(deviation < 0.0, 0.20 * deviation, deviation)
    r_x = 1.0 + signed
    r_y = 1.0 + 0.38 * signed
    upper = np.clip(np.sin(th), 0.0, 1.0)
    xscale = 1.0 + top_widen * upper**2
    yscale = 1.0 + 0.025 * upper**2
    x = cx + rx * r_x * xscale * np.cos(th)
    y = cy + ry * r_y * yscale * np.sin(th)
    return th, x, y


def category_patch(cx, cy, rx, ry, phase=0.0, top_widen=0.08,
                   facecolor=CAT_A, edgecolor=MID,
                   lw=0.76, alpha=0.43, zorder=2):
    _, x, y = category_points(
        cx, cy, rx, ry, phase=phase, top_widen=top_widen
    )
    return PathPatch(
        closed_path(np.column_stack([x, y])),
        facecolor=facecolor,
        edgecolor=edgecolor,
        lw=lw,
        alpha=alpha,
        zorder=zorder,
        joinstyle="round",
    )


def draw_sub(ax, x, y, w, h, text, fs=15.5, fc=SUB, ec=MID2,
             lw=0.55, alpha=0.86, z=5):
    patch = Ellipse(
        (x, y), w, h, facecolor=fc, edgecolor=ec,
        linewidth=lw, alpha=alpha, zorder=z
    )
    ax.add_patch(patch)
    ax.text(
        x, y, text, ha="center", va="center",
        fontsize=fs, color=DARK, zorder=z + 1
    )


def draw_category(ax, spec):
    ax.add_patch(category_patch(
        spec["cx"], spec["cy"], spec["rx"], spec["ry"],
        phase=spec["phase"],
        top_widen=spec.get("top_widen", 0.08),
        facecolor=spec["fill"],
    ))
    ax.text(
        spec["title_x"], spec["title_y"], spec["title"],
        ha="center", va="center",
        fontsize=spec.get("title_fs", 18.4),
        color=DARK,
        linespacing=spec.get("title_linespacing", 0.88),
        zorder=7,
    )
    for sub in spec.get("subs", []):
        draw_sub(ax, **sub)


def metaball_boundary(categories, xlim=(-0.10, 12.20),
                      ylim=(0.41, 9.88), nx=920, ny=710):
    """
    Derive a smooth, connected membrane from the category geometry.

    Each category contributes an anisotropic Gaussian influence. A high-order
    smooth maximum preserves local lobes and concave saddles, unlike a simple
    Gaussian sum that tends toward one rounded rectangle. The contour level is
    the one-sigma boundary of each expanded influence region, so every category
    remains enclosed with a controlled margin.
    """
    gx = np.linspace(*xlim, nx)
    gy = np.linspace(*ylim, ny)
    xx, yy = np.meshgrid(gx, gy)

    # A softer smooth-maximum and larger influence padding keep the membrane
    # organic while preventing it from tracing each category too tightly.
    power = 4.0
    threshold = np.exp(-0.5)
    components = []
    for spec in categories:
        sx = spec["rx"] + 0.42
        if spec["cy"] > 6.5:
            sy_pad = 0.38
        elif spec["cy"] > 3.3:
            sy_pad = 0.34
        else:
            sy_pad = 0.30
        sy = spec["ry"] + sy_pad
        q2 = ((xx - spec["cx"]) / sx) ** 2 + ((yy - spec["cy"]) / sy) ** 2
        components.append(np.exp(-0.5 * q2))

    # A weak anisotropic pull makes the mid-right membrane grow toward the
    # open frontier while staying attached to the Statistical/Stochastic area.
    frontier_pull = 0.72 * np.exp(
        -0.5 * (((xx - 11.08) / 0.86) ** 2 + ((yy - 5.35) / 0.50) ** 2)
    )
    components.append(frontier_pull)

    field = np.sum(np.stack(components) ** power, axis=0) ** (1.0 / power)

    # Use Matplotlib's contour engine only to solve the implicit boundary; the
    # final artwork is a normal PathPatch and remains stable across exports.
    probe_fig, probe_ax = plt.subplots(figsize=(2, 2))
    contour = probe_ax.contour(xx, yy, field, levels=[threshold])
    segments = [segment for segment in contour.allsegs[0] if len(segment) >= 20]
    plt.close(probe_fig)
    if not segments:
        raise RuntimeError("Metaball field did not produce a usable boundary.")

    boundary = max(segments, key=polygon_area)
    return resample_closed_curve(boundary), threshold


# The nine categories and all illustrative subfamilies are retained from v14.
# Horizontal radii are modestly enlarged so adjacent organic regions can
# visually approach/interpenetrate without disturbing their internal labels.
categories = [
    dict(
        title="Algebraic /\nFunctional",
        cx=2.10, cy=7.92, rx=1.58, ry=1.23, phase=0.35, fill=CAT_C,
        title_x=2.10, title_y=8.55, title_fs=18.4, top_widen=0.09,
        subs=[
            dict(x=1.38, y=7.78, w=1.37, h=0.50, text=r"$y=F(x)$"),
            dict(x=2.62, y=7.79, w=0.99, h=0.50, text=r"$F=0$"),
            dict(x=1.68, y=7.16, w=0.96, h=0.47, text=r"$P/Q$"),
            dict(x=2.70, y=7.16, w=1.02, h=0.47,
                 text=r"$\mathcal{R}_{\mathrm{SR}}$", fs=15.8,
                 fc=AMBER_FILL, ec=AMBER, lw=0.85, alpha=0.96),
        ],
    ),
    dict(
        title="Differential /\nEvolution",
        cx=5.78, cy=8.01, rx=1.59, ry=1.23, phase=1.05, fill=CAT_B,
        title_x=5.78, title_y=8.62, title_fs=18.4, top_widen=0.08,
        subs=[
            dict(x=5.07, y=7.88, w=0.94, h=0.50, text=r"$d/dt$"),
            dict(x=6.14, y=7.88, w=0.94, h=0.50, text=r"$\partial_i$", fs=16.0),
            dict(x=5.30, y=7.24, w=1.12, h=0.49, text=r"$D_g^\gamma f$", fs=15.0),
            dict(x=6.39, y=7.24, w=1.00, h=0.49, text=r"$\nabla^2u$"),
        ],
    ),
    dict(
        title="Integral /\nNonlocal / Memory",
        cx=9.44, cy=7.93, rx=1.57, ry=1.23, phase=1.95, fill=CAT_C,
        title_x=9.44, title_y=8.55, title_fs=17.5, top_widen=0.11,
        subs=[
            dict(x=8.76, y=7.79, w=0.85, h=0.51, text=r"$\displaystyle\int$", fs=18.0),
            dict(x=9.88, y=7.79, w=1.16, h=0.51, text=r"$u(t-\tau)$", fs=15.0),
            dict(x=9.30, y=7.15, w=1.08, h=0.48, text=r"$K*u$"),
        ],
    ),
    dict(
        title="Geometric /\nTopological /\nSymmetry",
        cx=2.14, cy=4.95, rx=1.73, ry=1.23, phase=2.65, fill=CAT_B,
        title_x=2.14, title_y=5.68, title_fs=15.9, top_widen=0.15,
        title_linespacing=0.82,
        subs=[
            dict(x=1.43, y=4.83, w=0.99, h=0.49, text=r"$\kappa_\gamma$"),
            dict(x=2.52, y=4.83, w=1.08, h=0.49, text=r"$d_{\mathcal{M}}$", fs=15.1),
            dict(x=1.78, y=4.17, w=1.08, h=0.48, text=r"$g\!\cdot\!x$"),
            dict(x=2.84, y=4.17, w=0.90, h=0.48, text=r"$H_k$"),
        ],
    ),
    dict(
        title="Spectral /\nModal / Multiscale",
        cx=5.82, cy=5.00, rx=1.75, ry=1.23, phase=3.45, fill=CAT_A,
        title_x=5.82, title_y=5.72, title_fs=16.4, top_widen=0.11,
        subs=[
            dict(x=5.08, y=4.85, w=1.28, h=0.50, text=r"$L\phi=\lambda\phi$", fs=14.0),
            dict(x=6.39, y=4.85, w=1.24, h=0.50, text=r"$\sum a_k\phi_k$", fs=14.0),
            dict(x=5.80, y=4.19, w=1.72, h=0.48, text=r"$u_0+\epsilon u_1+\cdots$", fs=13.1),
        ],
    ),
    dict(
        title="Statistical /\nStochastic /\nPopulation",
        cx=9.43, cy=4.94, rx=1.71, ry=1.23, phase=4.15, fill=CAT_B,
        title_x=9.43, title_y=5.68, title_fs=15.9, top_widen=0.14,
        title_linespacing=0.82,
        subs=[
            dict(x=8.78, y=4.80, w=1.01, h=0.49, text=r"$p(y|x)$"),
            dict(x=9.95, y=4.80, w=1.34, h=0.49,
                 text=r"$\theta^{(j)}\!\sim P_\theta$", fs=13.3),
            dict(x=9.35, y=4.16, w=1.26, h=0.48,
                 text=r"$\mathbb{E},\,\mathrm{Cov}$", fs=14.2),
        ],
    ),
    dict(
        title="Constraint /\nConservation /\nVariational",
        cx=2.22, cy=1.98, rx=1.77, ry=1.17, phase=4.90, fill=CAT_C,
        title_x=2.22, title_y=2.67, title_fs=15.5, top_widen=0.16,
        title_linespacing=0.82,
        subs=[
            dict(x=1.43, y=1.87, w=0.92, h=0.46, text=r"$C=0$"),
            dict(x=2.47, y=1.87, w=0.98, h=0.46, text=r"$C\leq0$"),
            dict(x=1.72, y=1.29, w=1.08, h=0.45, text=r"$\nabla\!\cdot J$"),
            dict(x=2.82, y=1.29, w=1.16, h=0.45, text=r"$\delta\mathcal{J}=0$", fs=14.0),
        ],
    ),
    dict(
        title="Discrete /\nGraph / Hybrid",
        cx=5.84, cy=2.04, rx=1.70, ry=1.15, phase=5.65, fill=CAT_B,
        title_x=5.84, title_y=2.68, title_fs=16.2, top_widen=0.10,
        subs=[
            dict(x=5.06, y=1.91, w=1.60, h=0.47, text=r"$x_{n+1}=F(x_n)$", fs=13.0),
            dict(x=6.44, y=1.91, w=0.94, h=0.47, text=r"$L_Gx$"),
            dict(x=5.78, y=1.31, w=1.18, h=0.45, text=r"$R_k|_{\Omega_k}$", fs=13.8),
        ],
    ),
    dict(
        title="Learned /\nNonparametric",
        cx=9.43, cy=1.97, rx=1.65, ry=1.15, phase=0.15, fill=CAT_A,
        title_x=9.43, title_y=2.61, title_fs=17.0, top_widen=0.09,
        subs=[
            dict(x=8.76, y=1.88, w=1.31, h=0.47, text=r"$z=\Phi_\theta(x)$", fs=13.8),
            dict(x=10.03, y=1.88, w=1.09, h=0.47, text=r"$K(x,x')$", fs=14.0),
            dict(x=9.37, y=1.28, w=1.25, h=0.45, text=r"$\widehat{F}_{\mathrm{data}}$", fs=13.6),
        ],
    ),
]


fig = plt.figure(figsize=(14.4, 8.35), dpi=180)
ax = fig.add_axes([0, 0, 1, 1])
fig.patch.set_facecolor("white")
ax.set_xlim(-0.1, 19.20)
ax.set_ylim(-0.05, 11.05)
ax.axis("off")

# Adaptive living membrane. The relational space is deliberately drawn without
# any outline so the admissible region reads as an open, diffuse field rather
# than a bounded container.
smooth_field, field_level = metaball_boundary(categories)
field_path = closed_path(smooth_field)
ax.add_patch(PathPatch(
    field_path, facecolor=FIELD, edgecolor="none",
    alpha=0.985, zorder=0,
))

# Thought-bubble clouds carry the "more categories remain to be discovered"
# message. Their temporary positions are replaced after operator layout by an
# edge-separated sequence centred in the measured inter-panel white gutter.
frontier_cloud_specs = [
    (5.28, 0.270, 0.15, CAT_B, 0.95),
    (5.52, 0.165, 1.15, CAT_A, 0.85),
    (5.68, 0.095, 2.05, SUB, 0.75),
]
frontier_cloud_artists = []
for cy, scale, rotation, facecolor, linewidth in frontier_cloud_specs:
    patch = PathPatch(
        cloud_path(12.45, cy, scale, rotation=rotation),
        facecolor=facecolor, edgecolor="none",
        lw=0.0, alpha=0.95, zorder=1.4,
        joinstyle="round",
    )
    ax.add_patch(patch)
    frontier_cloud_artists.append(patch)

ax.text(
    6.10, 10.43, r"Admissible Relational Space $\mathfrak{R}_q$",
    ha="center", va="center", fontsize=29.6, color=DARK
)

# Temporary label position; after the operator panel is measured, the label and
# cloud sequence share the exact centre of the inter-panel white gutter.
FRONTIER_LABEL_Y = 6.46
frontier_label = ax.text(
    12.45, FRONTIER_LABEL_Y,
    "\\textbf{Open, Expandable}\n\\textbf{Discovery Frontier}",
    ha="center", va="center", fontsize=14.0, color=DARK,
    linespacing=0.92,
)

for category in categories:
    draw_category(ax, category)

def category_by_title(fragment):
    for spec in categories:
        if fragment in spec["title"]:
            return spec
    raise KeyError(fragment)


def row_gap_center(upper_title, lower_title, x_center, half_width=1.30):
    """
    Vertical mid-line of the clear channel between two stacked organelles.

    Measured from the rendered boundaries so the caption stays centred even as
    the organelle silhouettes deform.
    """
    upper = category_by_title(upper_title)
    lower = category_by_title(lower_title)
    _, ux, uy = category_points(
        upper["cx"], upper["cy"], upper["rx"], upper["ry"],
        phase=upper["phase"], top_widen=upper.get("top_widen", 0.08),
    )
    _, lx, ly = category_points(
        lower["cx"], lower["cy"], lower["rx"], lower["ry"],
        phase=lower["phase"], top_widen=lower.get("top_widen", 0.08),
    )
    upper_floor = uy[np.abs(ux - x_center) < half_width].min()
    lower_ceiling = ly[np.abs(lx - x_center) < half_width].max()
    return 0.5 * (upper_floor + lower_ceiling), upper_floor - lower_ceiling


# Both inter-row captions are centred in the channel they occupy.
sr_x = 0.5 * (
    category_by_title("Differential")["cx"] + category_by_title("Spectral")["cx"]
)
sr_y, sr_gap = row_gap_center("Differential", "Spectral", sr_x)
overlap_y, overlap_gap = row_gap_center("Spectral", "Discrete", 6.02)

ax.text(
    6.02, overlap_y,
    "Overlapping categories permit hybrid/composed representations",
    ha="center", va="center", fontsize=11.8,
    color=MID,
)

# Kept as a plain Text artist so its extent can be audited independently of the
# connector; the leader line is attached once the text extent is known.
sr_caption = ax.text(
    sr_x, sr_y, r"Symbolic Regression:\ One Restricted Subfamily",
    ha="center", va="center", fontsize=11.9,
    color=AMBER, zorder=8,
)

ax.text(
    6.10, 0.30,
    "Illustrative, non-exhaustive categories; each SIR run instantiates a finite, auditable grammar.",
    ha="center", va="center", fontsize=11.8,
    color="black",
)

# Coordinate-generation panel: content retained from v14 and shifted as one
# unit to preserve its internal alignment while opening a clear visual gutter.
# Latin Modern at the original sizes is wider than STIX: the panel moves 0.11
# further right so the frontier clouds keep a visible gutter (pre-polish 0.65).
OP_SHIFT = 0.76
SYMBOL_SHIFT = 0.35
# Header and subtitle sit together slightly left of the shifted column centre;
# centred there the header would cross the right canvas edge, and this position
# keeps the right-edge clearance set by the composition box.
HEADER_X = 15.63
ax.text(
    HEADER_X, 10.38, "Coordinate-Generation Operators",
    ha="center", va="center", fontsize=23.3, color=DARK
)
ax.text(
    HEADER_X, 9.98, "Representative groups; recursively composable",
    ha="center", va="center", fontsize=12.5,
    color=MID,
)

op_rows = [
    (r"$\partial,\,d,\,\Delta,\,D^\gamma$", "Local",
     "Derivatives, differences,\ntangent / phase constructions"),
    (r"$\displaystyle\int,\ *,\ \mathcal{L}_\tau$", "Nonlocal / History",
     "Integrals, convolutions,\nlags and memory operators"),
    (r"$\mathcal{T},\ \mathcal{B},\ \Pi$", "Algebraic / Basis",
     "Transforms, ratios, reductions,\nnondimensional groups and bases"),
    (r"$\mathcal{G},\ \mathcal{S}$", "Structural / Statistical",
     "Geometry, symmetry, graph,\nspectral and statistical maps"),
    (r"$\Phi_\theta$", "Learned",
     "Embeddings, kernels,\nneural / surrogate coordinates"),
    (r"$\mathcal{M}$", "Model Primitives",
     "Numerical simulators, pretrained\nmodels, scientific codes, agents"),
]

# Rows are lifted slightly and later centred, as a block, on the composition
# box below them.
row_artists = []
y = 9.18
step = 1.10
for sym, heading, detail in op_rows:
    row_artists.append(ax.text(
        12.93 + OP_SHIFT + SYMBOL_SHIFT, y, sym, ha="center", va="center",
        fontsize=18.8, color=DARK
    ))
    row_artists.append(ax.text(
        14.27 + OP_SHIFT, y + 0.10, rf"\textbf{{{heading}}}", ha="left", va="center",
        fontsize=15.0, color=DARK
    ))
    row_artists.append(ax.text(
        14.27 + OP_SHIFT, y - 0.25, detail, ha="left", va="center",
        fontsize=12.5, color=DARK, linespacing=1.08
    ))
    y -= step

box = FancyBboxPatch(
    (12.82 + OP_SHIFT, 1.26), 5.15, 1.18,
    boxstyle="round,pad=0.18,rounding_size=0.08",
    facecolor="#F7F8F3", edgecolor=MID2,
    linewidth=0.75, alpha=0.96
)
ax.add_patch(box)
ax.text(
    15.40 + OP_SHIFT, 1.97,
    r"$G=G_{i_k}\circ\cdots\circ G_{i_2}\circ G_{i_1}$",
    ha="center", va="center", fontsize=16.8, color=DARK
)
ax.text(
    15.40 + OP_SHIFT, 1.58, "Operators may compose recursively",
    ha="center", va="center", fontsize=12.4,
    color=MID,
)

ax.text(
    12.74 + OP_SHIFT, 0.42, r"\textbf{Key}", fontsize=12.2, color=DARK,
    ha="left", va="center"
)
ax.add_patch(Ellipse(
    (13.45 + OP_SHIFT, 0.42), 0.34, 0.21,
    facecolor=CAT_B, edgecolor=MID, lw=0.60, alpha=0.55
))
ax.text(
    13.69 + OP_SHIFT, 0.42, "Category", fontsize=11.4,
    color=DARK, ha="left", va="center"
)
ax.add_patch(Ellipse(
    (14.75 + OP_SHIFT, 0.42), 0.28, 0.17,
    facecolor=SUB, edgecolor=MID2, lw=0.55, alpha=0.86
))
ax.text(
    14.95 + OP_SHIFT, 0.42, "Illustrative subfamily", fontsize=11.4,
    color=DARK, ha="left", va="center"
)

# ---------------------------------------------------------------------------
# Layout measurement pass: centre the operator rows on the composition box and
# verify that no annotation collides with the field or the operator panel.
# ---------------------------------------------------------------------------
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
to_data = ax.transData.inverted()


def data_bbox(artist):
    return artist.get_window_extent(renderer).transformed(to_data)


box_center_x = 12.82 + OP_SHIFT + 5.15 / 2.0
row_boxes = [data_bbox(artist) for artist in row_artists]
block_x0 = min(bbox.x0 for bbox in row_boxes)
block_x1 = max(bbox.x1 for bbox in row_boxes)
row_dx = box_center_x - 0.5 * (block_x0 + block_x1)
for artist in row_artists:
    artist.set_x(artist.get_position()[0] + row_dx)

fig.canvas.draw()
row_boxes = [data_bbox(artist) for artist in row_artists]

# Centre the thought-cloud sequence in the actual white gutter between the
# membrane and the operator rows. Cloud boundaries are laid out sequentially,
# guaranteeing visible edge-to-edge gaps regardless of their asymmetric lobes.
operator_left = min(bbox.x0 for bbox in row_boxes)
cloud_band = (smooth_field[:, 1] >= 4.85) & (smooth_field[:, 1] <= 5.95)
gutter_left = smooth_field[cloud_band, 0].max() + 0.16
gutter_right = operator_left - 0.18
if gutter_right <= gutter_left:
    raise RuntimeError("No white gutter remains for the frontier thought clouds.")
gutter_center = 0.5 * (gutter_left + gutter_right)


def place_frontier_clouds():
    local_paths = []
    local_extents = []
    for cy, scale, rotation, _, _ in frontier_cloud_specs:
        path = cloud_path(0.0, cy, scale, rotation=rotation)
        x0 = path.vertices[:, 0].min()
        x1 = path.vertices[:, 0].max()
        local_paths.append(path)
        local_extents.append((x0, x1))

    available_width = gutter_right - gutter_left
    cloud_width = sum(x1 - x0 for x0, x1 in local_extents)
    requested_gap = 0.10
    side_margin = 0.04
    cloud_gap = min(
        requested_gap,
        0.5 * (available_width - 2.0 * side_margin - cloud_width),
    )
    if cloud_gap < 0.055:
        raise RuntimeError(
            "The white gutter is too narrow to separate the thought clouds."
        )

    cursor = 0.0
    centre_offsets = []
    for x0, x1 in local_extents:
        centre_offsets.append(cursor - x0)
        cursor += (x1 - x0) + cloud_gap
    group_width = cursor - cloud_gap
    group_left = gutter_center - 0.5 * group_width

    for patch, spec, centre_offset in zip(
        frontier_cloud_artists, frontier_cloud_specs, centre_offsets
    ):
        cy, scale, rotation, _, _ = spec
        patch.set_path(cloud_path(
            group_left + centre_offset, cy, scale, rotation=rotation
        ))

    return cloud_gap


cloud_gap = place_frontier_clouds()
frontier_label.set_x(gutter_center)

fig.canvas.draw()
row_boxes = [data_bbox(artist) for artist in row_artists]
cloud_boxes = [data_bbox(artist) for artist in frontier_cloud_artists]
label_box = data_bbox(frontier_label)
sr_box = data_bbox(sr_caption)

# Attach the leader line now that the caption extent is known, so it starts at
# the caption edge instead of at an assumed offset.
ax.annotate(
    "", xy=(2.70, 7.16), xycoords="data",
    xytext=(sr_box.x0 - 0.08, sr_y), textcoords="data",
    arrowprops=dict(
        arrowstyle="-", lw=0.75, color=AMBER,
        shrinkA=0, shrinkB=3,
        connectionstyle="arc3,rad=-0.20",
    ),
)

print(f"symbolic-regression channel: gap={sr_gap:.3f} centre={sr_y:.3f}")
print(f"overlap-caption channel:     gap={overlap_gap:.3f} centre={overlap_y:.3f}")
print(f"operator block re-centred by dx={row_dx:+.3f}")
print(
    "frontier label x-span: "
    f"[{label_box.x0:.2f}, {label_box.x1:.2f}]  "
    f"operator block left: {min(b.x0 for b in row_boxes):.2f}"
)
print(
    f"sr caption bbox height={sr_box.height:.3f} "
    f"y=[{sr_box.y0:.3f}, {sr_box.y1:.3f}]"
)

if field_path.intersects_bbox(label_box, filled=True):
    raise RuntimeError("Frontier label overlaps the relational field.")

colliding_rows = [
    bbox for bbox in row_boxes
    if label_box.overlaps(bbox)
    or (bbox.x0 - label_box.x1) < 0.12 and not (
        bbox.y1 < label_box.y0 or bbox.y0 > label_box.y1
    )
]
if colliding_rows:
    raise RuntimeError(
        "Frontier label is too close to the coordinate-generation panel."
    )

cloud_x0 = min(bbox.x0 for bbox in cloud_boxes)
cloud_x1 = max(bbox.x1 for bbox in cloud_boxes)
cloud_center_measured = 0.5 * (cloud_x0 + cloud_x1)
ordered_cloud_boxes = sorted(cloud_boxes, key=lambda bbox: bbox.x0)
measured_cloud_gaps = [
    right.x0 - left.x1
    for left, right in zip(ordered_cloud_boxes, ordered_cloud_boxes[1:])
]
label_center_measured = 0.5 * (label_box.x0 + label_box.x1)
if cloud_x0 < gutter_left or cloud_x1 > gutter_right:
    raise RuntimeError(
        "Frontier thought clouds extend outside the inter-panel white gutter."
    )
if abs(cloud_center_measured - gutter_center) > 0.025:
    raise RuntimeError("Frontier thought-cloud group is not centred in the gutter.")
if min(measured_cloud_gaps) < 0.05:
    raise RuntimeError(
        f"Frontier thought clouds are not visibly separated: {measured_cloud_gaps}"
    )
if abs(label_center_measured - gutter_center) > 0.025:
    raise RuntimeError("Frontier label is not centred over the thought clouds.")
if any(
    field_path.intersects_path(patch.get_path(), filled=True)
    for patch in frontier_cloud_artists
):
    raise RuntimeError("Frontier thought clouds overlap the relational field.")

sr_hits = [
    spec["title"].replace("\n", " ")
    for spec in categories
    if closed_path(
        np.column_stack(
            category_points(
                spec["cx"], spec["cy"], spec["rx"], spec["ry"],
                phase=spec["phase"],
                top_widen=spec.get("top_widen", 0.08),
            )[1:]
        )
    ).intersects_bbox(sr_box, filled=True)
]
if sr_hits:
    raise RuntimeError(
        f"Symbolic-regression caption overlaps organelles: {sr_hits}"
    )

# The first-row organelles must remain visibly distinct. Audit both true path
# intersection and minimum contour separation so a later fluidity adjustment
# cannot quietly recreate touching or overlapping boundaries.
top_row_gaps = {}
for left, right in zip(categories[:3], categories[1:3]):
    left_points = np.column_stack(
        category_points(
            left["cx"], left["cy"], left["rx"], left["ry"],
            phase=left["phase"],
            top_widen=left.get("top_widen", 0.08),
        )[1:]
    )
    right_points = np.column_stack(
        category_points(
            right["cx"], right["cy"], right["rx"], right["ry"],
            phase=right["phase"],
            top_widen=right.get("top_widen", 0.08),
        )[1:]
    )
    pair_name = (
        f"{left['title'].replace(chr(10), ' ')} / "
        f"{right['title'].replace(chr(10), ' ')}"
    )
    if closed_path(left_points).intersects_path(
        closed_path(right_points), filled=True
    ):
        raise RuntimeError(f"Top-row organelles overlap: {pair_name}")
    distances = np.linalg.norm(
        left_points[:, None, :] - right_points[None, :, :], axis=2
    )
    top_row_gaps[pair_name] = float(distances.min())

narrow_top_gaps = {
    pair: gap for pair, gap in top_row_gaps.items() if gap < 0.10
}
if narrow_top_gaps:
    raise RuntimeError(
        f"Top-row organelle gaps are visually too narrow: {narrow_top_gaps}"
    )

print(
    "frontier cloud gutter: "
    f"[{gutter_left:.2f}, {gutter_right:.2f}], "
    f"group centre={cloud_center_measured:.2f}"
)
for pair, gap in top_row_gaps.items():
    print(f"top-row boundary gap: {gap:.3f}  {pair}")

# Geometry audit: all organic category boundaries must remain within the
# implicit membrane despite their broader v15 deformations.
outside_counts = {}
for spec in categories:
    _, cxp, cyp = category_points(
        spec["cx"], spec["cy"], spec["rx"], spec["ry"],
        phase=spec["phase"],
        top_widen=spec.get("top_widen", 0.08),
    )
    pts = np.column_stack([cxp, cyp])
    outside_counts[spec["title"].replace("\n", " ")] = int(
        (~field_path.contains_points(pts)).sum()
    )

bad = {name: count for name, count in outside_counts.items() if count}
if bad:
    raise RuntimeError(
        f"Metaball membrane intersects category organelles: {bad}"
    )

# The fluid organelle outlines must still fully contain their own subfamily
# capsules; this is what limits how far the boundary may be deformed.
capsule_escapes = {}
for spec in categories:
    boundary = closed_path(
        np.column_stack(
            category_points(
                spec["cx"], spec["cy"], spec["rx"], spec["ry"],
                phase=spec["phase"],
                top_widen=spec.get("top_widen", 0.08),
            )[1:]
        )
    )
    theta = np.linspace(0.0, 2.0 * np.pi, 96)
    for sub in spec.get("subs", []):
        ring = np.column_stack([
            sub["x"] + 0.5 * sub["w"] * np.cos(theta),
            sub["y"] + 0.5 * sub["h"] * np.sin(theta),
        ])
        escaped = int((~boundary.contains_points(ring)).sum())
        if escaped:
            key = f"{spec['title'].replace(chr(10), ' ')} :: {sub['text']}"
            capsule_escapes[key] = escaped

if capsule_escapes:
    raise RuntimeError(f"Subfamily capsules escape their organelle: {capsule_escapes}")

if smooth_field[:, 0].max() >= 12.35:
    raise RuntimeError("Metaball membrane extends into the operator panel.")
if smooth_field[:, 1].max() >= 9.90:
    raise RuntimeError("Metaball membrane extends too close to the title.")
if smooth_field[:, 1].min() <= 0.40:
    raise RuntimeError("Metaball membrane extends too close to the footer.")

fig.savefig(
    PDF_PATH, bbox_inches="tight", pad_inches=0.04, facecolor="white"
)
fig.savefig(
    SVG_PATH, bbox_inches="tight", pad_inches=0.04, facecolor="white"
)
fig.savefig(
    PNG_PATH, dpi=600, bbox_inches="tight", pad_inches=0.04,
    facecolor="white"
)
plt.close(fig)

print(f"metaball contour level: {field_level:.6f}")
print(PDF_PATH)
print(SVG_PATH)
print(PNG_PATH)
