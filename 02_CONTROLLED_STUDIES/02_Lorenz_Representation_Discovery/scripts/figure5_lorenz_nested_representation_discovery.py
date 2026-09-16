# Regenerate Figure 5 with text layers explicitly above all rounded cards.
from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib import font_manager
from scipy.integrate import solve_ivp

OUTDIR = Path('/mnt/data')
STEM = 'figure5_lorenz_nested_representation_discovery'
PNG = OUTDIR / f'{STEM}.png'
PDF = OUTDIR / f'{STEM}.pdf'
SVG = OUTDIR / f'{STEM}.svg'

installed = {f.name for f in font_manager.fontManager.ttflist}
SERIF = next(
    (f for f in ['Times New Roman', 'Tinos', 'Nimbus Roman', 'Liberation Serif', 'DejaVu Serif']
     if f in installed),
    'DejaVu Serif'
)
mpl.rcParams.update({
    'font.family': 'serif',
    'font.serif': [SERIF],
    'mathtext.fontset': 'stix',
    'axes.unicode_minus': False,
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'svg.fonttype': 'none',
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.035,
})

NAVY = '#234E70'
BLUE = '#3E78A8'
TEAL = '#2C8C82'
SAGE = '#78A99A'
PALE_TEAL = '#EAF4F1'
PALE_BLUE = '#EDF3F8'
INK = '#263238'
MID = '#64727A'
LIGHT = '#D9E1E5'
VERY_LIGHT = '#F7F9FA'
WHITE = '#FFFFFF'

def lorenz(t, s, sigma=10.0, rho=28.0, beta=8.0/3.0):
    x, y, z = s
    return [sigma*(y-x), x*(rho-z)-y, x*y-beta*z]

t_eval = np.linspace(0, 28, 7500)
sol = solve_ivp(
    lorenz, (t_eval[0], t_eval[-1]), [1.0, 1.0, 1.0],
    t_eval=t_eval, rtol=1e-10, atol=1e-12
)
x, y, z = sol.y
mask = t_eval > 5.0
xa, za = x[mask], z[mask]

fig = plt.figure(figsize=(7.25, 3.72), facecolor=WHITE)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

PANEL_Y0, PANEL_Y1 = 0.055, 0.955
panels = {'a': (0.018, 0.320), 'b': (0.342, 0.678), 'c': (0.700, 0.982)}

for key, (x0, x1) in panels.items():
    bg = PALE_BLUE if key == 'a' else (PALE_TEAL if key == 'b' else VERY_LIGHT)
    ax.add_patch(FancyBboxPatch(
        (x0, PANEL_Y0), x1-x0, PANEL_Y1-PANEL_Y0,
        boxstyle='round,pad=0.004,rounding_size=0.012',
        facecolor=bg, edgecolor=LIGHT, linewidth=0.7, zorder=0
    ))

def txt(xp, yp, s, size=7.5, color=INK, weight='normal',
        ha='left', va='center', zorder=10, **kw):
    ax.text(
        xp, yp, s, fontsize=size, color=color, fontweight=weight,
        ha=ha, va=va, zorder=zorder, **kw
    )

def box(xp, yp, w, h, text='', fc=WHITE, ec=LIGHT, tc=INK,
        size=7.1, weight='normal', lw=0.8, radius=0.012, zorder=5):
    ax.add_patch(FancyBboxPatch(
        (xp, yp), w, h,
        boxstyle=f'round,pad=0.004,rounding_size={radius}',
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=zorder
    ))
    if text:
        txt(
            xp+w/2, yp+h/2, text, size=size, color=tc, weight=weight,
            ha='center', va='center', zorder=zorder+2
        )

def arrow(xa0, ya0, xa1, ya1, color=MID, lw=1.0, ms=8, rad=0.0, zorder=4):
    ax.add_patch(FancyArrowPatch(
        (xa0, ya0), (xa1, ya1), arrowstyle='-|>', mutation_scale=ms,
        linewidth=lw, color=color,
        connectionstyle=f'arc3,rad={rad}', shrinkA=2, shrinkB=2, zorder=zorder
    ))

def map_to_region(v, vmin, vmax, a, b):
    return a + (np.asarray(v)-vmin)/(vmax-vmin)*(b-a)

# --- a: fixed representation -------------------------------------------------
x0, x1 = panels['a']
txt(x0+0.016, 0.918, 'a', size=10.5, weight='bold')
txt(x0+0.046, 0.918, 'Fixed Representation', size=10.2, weight='bold', color=NAVY)
txt(x0+0.046, 0.878, 'Conventional model identification is a restricted SIR case',
    size=6.5, color=MID)

rx0, rx1 = x0+0.027, x1-0.026
ry0, ry1 = 0.505, 0.825
X = map_to_region(xa, np.percentile(xa, 0.3), np.percentile(xa, 99.7), rx0, rx1)
Z = map_to_region(za, np.percentile(za, 0.3), np.percentile(za, 99.7), ry0, ry1)
keep = (X>=rx0)&(X<=rx1)&(Z>=ry0)&(Z<=ry1)
ax.plot(X[keep], Z[keep], color=BLUE, lw=0.36, alpha=0.58, zorder=2)
txt(rx0, ry1+0.018, r'Full state $(x,y,z)$', size=7.4, weight='bold')
txt(rx1, ry0-0.018, 'same trajectory / fixed coordinates', size=6.0, color=MID, ha='right')

box(x0+0.050, 0.382, x1-x0-0.100, 0.073,
    'Cubic library  +  PySINDy', fc=WHITE, ec=BLUE, tc=NAVY,
    size=7.5, weight='bold', lw=1.0)
arrow((x0+x1)/2, 0.505, (x0+x1)/2, 0.458, color=BLUE, lw=1.1, ms=9)

box(x0+0.034, 0.135, x1-x0-0.068, 0.188, fc=WHITE, ec=LIGHT, lw=0.8)
txt((x0+x1)/2, 0.291, 'Canonical Support Recovered',
    size=7.1, weight='bold', color=TEAL, ha='center')
txt((x0+x1)/2, 0.247, r'$\dot{x}=-10x+10y$', size=7.0, ha='center')
txt((x0+x1)/2, 0.211, r'$\dot{y}=28x-y-xz$', size=7.0, ha='center')
txt((x0+x1)/2, 0.175, r'$\dot{z}=-2.667z+xy$', size=7.0, ha='center')
txt((x0+x1)/2, 0.105, r'max. coefficient deviation $\sim 2\times10^{-3}$',
    size=6.2, color=MID, ha='center')
arrow((x0+x1)/2, 0.382, (x0+x1)/2, 0.326, color=TEAL, lw=1.0, ms=8)

# --- b: representation discovery --------------------------------------------
x0, x1 = panels['b']
txt(x0+0.016, 0.918, 'b', size=10.5, weight='bold')
txt(x0+0.046, 0.918, 'Representation Enters Discovery',
    size=10.2, weight='bold', color=TEAL)
txt(x0+0.046, 0.878, r'Observe $x,y$; reconstruct $z$ with the estimator unchanged',
    size=6.5, color=MID)

tr_x0, tr_x1 = x0+0.022, x0+0.126
tr_y0, tr_y1 = 0.650, 0.814
sel = (t_eval > 8.0) & (t_eval < 10.8)
tsel = t_eval[sel]
xx, yy = x[sel], y[sel]
T = map_to_region(tsel, tsel.min(), tsel.max(), tr_x0, tr_x1)
vlo, vhi = min(xx.min(), yy.min()), max(xx.max(), yy.max())
XX = map_to_region(xx, vlo, vhi, tr_y0, tr_y1)
YY = map_to_region(yy, vlo, vhi, tr_y0, tr_y1)
ax.plot(T, XX, color=BLUE, lw=1.0, zorder=4)
ax.plot(T, YY, color=TEAL, lw=1.0, zorder=4)
txt(tr_x0, 0.832, r'Observed $x(t),y(t)$', size=6.8, weight='bold')

cx0 = x0 + 0.151
chip_w, chip_h = 0.057, 0.046
chips = [
    (cx0, 0.756, r'$x,y$'),
    (cx0+0.064, 0.756, r'$\dot x,\dot y$'),
    (cx0, 0.697, r'$xy,x^2$'),
    (cx0+0.064, 0.697, r'$D_yx$'),
    (cx0, 0.638, r'$\Delta,\int$'),
    (cx0+0.064, 0.638, r'$\cdots$'),
]
for i, (cx, cy, label) in enumerate(chips):
    box(cx, cy, chip_w, chip_h, label,
        fc=WHITE, ec=SAGE if i<5 else LIGHT, tc=INK,
        size=6.7, lw=0.7, radius=0.009)
txt(cx0+0.060, 0.831, 'Finite Coordinate Ontology',
    size=6.8, weight='bold', ha='center')
txt(cx0+0.060, 0.603, '17 families  •  38 coordinates',
    size=6.1, color=MID, ha='center')
arrow(tr_x1+0.004, 0.728, cx0-0.005, 0.728, color=SAGE, lw=1.0, ms=8)

box(x0+0.082, 0.500, x1-x0-0.164, 0.071,
    'PySINDy  —  unchanged relation estimator',
    fc=WHITE, ec=TEAL, tc=TEAL, size=7.15, weight='bold', lw=1.0)
arrow((x0+x1)/2, 0.615, (x0+x1)/2, 0.574, color=TEAL, lw=1.0, ms=8)

arrow((x0+x1)/2, 0.498, x0+0.102, 0.432,
      color=BLUE, lw=1.0, ms=8, rad=0.08)
arrow((x0+x1)/2, 0.498, x1-0.102, 0.432,
      color=TEAL, lw=1.0, ms=8, rad=-0.08)

box(x0+0.025, 0.235, 0.132, 0.188, fc=PALE_BLUE, ec=BLUE, lw=1.0)
txt(x0+0.091, 0.391, r'$q_{\rm acc}$', size=8.5, weight='bold', color=NAVY, ha='center')
txt(x0+0.091, 0.352, 'Accuracy', size=6.6, color=MID, ha='center')
txt(x0+0.091, 0.309, '38 coordinates', size=7.2, weight='bold', ha='center')
txt(x0+0.091, 0.267, r'RMSE  $1.35\times10^{-5}$',
    size=6.5, color=NAVY, ha='center')

box(x1-0.157, 0.235, 0.132, 0.188, fc=PALE_TEAL, ec=TEAL, lw=1.0)
txt(x1-0.091, 0.391, r'$q_{\rm comp}$', size=8.5, weight='bold', color=TEAL, ha='center')
txt(x1-0.091, 0.352, 'Compactness', size=6.6, color=MID, ha='center')
txt(x1-0.091, 0.309, '12 coordinates', size=7.2, weight='bold', ha='center')
txt(x1-0.091, 0.267, r'RMSE  $3.26\times10^{-5}$',
    size=6.5, color=TEAL, ha='center')

box(x0+0.044, 0.101, x1-x0-0.088, 0.080,
    '48 development trajectories   →   freeze   →   24 confirmation trajectories',
    fc=WHITE, ec=LIGHT, tc=MID, size=6.15, lw=0.7)

# --- c: observation conditions ----------------------------------------------
x0, x1 = panels['c']
txt(x0+0.016, 0.918, 'c', size=10.5, weight='bold')
txt(x0+0.046, 0.918, 'Observation Conditions Matter',
    size=10.0, weight='bold', color=NAVY)
txt(x0+0.046, 0.878, 'Held-out reconstruction error; lower is better',
    size=6.5, color=MID)

labels = ['Quadratic', 'Compact 12', 'Full 38']
clean = np.array([2.27, 3.26e-5, 1.35e-5])
noise = np.array([3.00, 5.12, 2.25])
ys = np.array([0.704, 0.557, 0.410])

plot_x0, plot_x1 = x0+0.076, x1-0.025
log_min, log_max = -5.15, 0.85
def xlog(val):
    lv = np.log10(val)
    return plot_x0 + (lv-log_min)/(log_max-log_min)*(plot_x1-plot_x0)

for val, lab in [(1e-5, r'$10^{-5}$'), (1e-3, r'$10^{-3}$'),
                 (1e-1, r'$10^{-1}$'), (1, r'$10^{0}$')]:
    gx = xlog(val)
    ax.plot([gx, gx], [0.338, 0.782], color=LIGHT, lw=0.6, zorder=1)
    txt(gx, 0.310, lab, size=5.9, color=MID, ha='center')
txt((plot_x0+plot_x1)/2, 0.270, 'RMSE  (log scale)', size=6.4, color=MID, ha='center')

for i, lab in enumerate(labels):
    yrow = ys[i]
    txt(x0+0.020, yrow, lab, size=6.4, color=INK)
    xc, xn = xlog(clean[i]), xlog(noise[i])
    ax.plot([xc, xn], [yrow, yrow], color='#B7C1C6', lw=1.1, zorder=2)
    # Slight y-offset on the quadratic pair prevents near-overlap.
    clean_y = yrow + (0.009 if i == 0 else 0.0)
    noise_y = yrow - (0.009 if i == 0 else 0.0)
    ax.scatter([xc], [clean_y], s=31, marker='o',
               facecolor=TEAL, edgecolor=WHITE, linewidth=0.7, zorder=6)
    ax.scatter([xn], [noise_y], s=35, marker='D',
               facecolor=WHITE, edgecolor=NAVY, linewidth=1.05, zorder=6)

ax.scatter([x0+0.072], [0.822], s=28, marker='o',
           facecolor=TEAL, edgecolor=WHITE, linewidth=0.7, zorder=6)
txt(x0+0.086, 0.822, 'Clean', size=6.2)
ax.scatter([x0+0.152], [0.822], s=31, marker='D',
           facecolor=WHITE, edgecolor=NAVY, linewidth=1.0, zorder=6)
txt(x0+0.168, 0.822, '1% noise', size=6.2)

box(x0+0.030, 0.110, x1-x0-0.060, 0.111, fc=WHITE, ec=LIGHT, lw=0.75)
txt((x0+x1)/2, 0.193,
    r'Clean:  $q_{\rm acc}\to$ Full 38   •   $q_{\rm comp}\to$ Compact 12',
    size=6.25, color=INK, ha='center')
txt((x0+x1)/2, 0.151,
    r'1% noise:  $q_{\rm robust}\to$ Full 38',
    size=6.35, color=NAVY, weight='bold', ha='center')

txt(0.5, 0.018,
    'Same Lorenz dynamics  •  same downstream estimator  •  different representational commitments',
    size=6.45, color=MID, ha='center')

fig.savefig(PNG, dpi=600, facecolor=WHITE)
fig.savefig(PDF, facecolor=WHITE)
fig.savefig(SVG, facecolor=WHITE)
plt.close(fig)

print(f'Updated: {PNG}')
print(f'Updated: {PDF}')
print(f'Updated: {SVG}')
print(f'Font: {SERIF}')