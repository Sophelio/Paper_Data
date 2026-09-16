
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from scipy.integrate import solve_ivp

PLOTTER = Path(__file__).resolve().parent
PENDULUM = PLOTTER.parent
PAPER = PENDULUM.parent
MANIFEST = PENDULUM / 'manifest.csv'
OUT_DIR = PAPER / 'Figures' / 'figs'
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PNG = OUT_DIR / 'pendulum_task_conditioned_panel_v5.png'
OUT_PDF = OUT_DIR / 'pendulum_task_conditioned_panel_v5.pdf'
OUT_SVG = OUT_DIR / 'pendulum_task_conditioned_panel_v5.svg'

OMEGA0 = 1.35
A_COMP = -3.64499998
A_PRED = -1.82245149
B_PRED = 1.0
HOLDOUTS = (3, 7, 11, 15, 19, 23, 27, 31)
HORIZONS = np.array([0.5, 1, 2, 5, 10, 20, 30.0])
COMP_REP = (0, 4, 8, 12, 16, 20, 24, 28)

INK = '#17324D'
NAVY = '#274C77'
BLUE = '#4F7FA8'
BLUE_LIGHT = '#AFC4D8'
GREEN = '#2E7D62'
GREEN_MID = '#5E9A82'
GREEN_LIGHT = '#C8DDD3'
SLATE = '#66788B'
GRID = '#DCE3E8'
WHITE = '#FFFFFF'

mpl.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'Tinos', 'Times', 'Nimbus Roman', 'DejaVu Serif'],
    'mathtext.fontset': 'stix',
    'pdf.fonttype': 42,
    'ps.fonttype': 42,
    'axes.unicode_minus': True,
    'font.size': 8.2,
})

manifest = pd.read_csv(MANIFEST)
t_eval = np.linspace(0.0, 30.0, 3001)


def rhs_truth(t, u):
    return (u[1], -(OMEGA0**2) * np.sin(u[0]))


def rhs_sir(t, u):
    return (B_PRED * u[1], A_PRED * np.sin(u[0]))


def integrate(rid, rhs):
    row = manifest.loc[manifest['realization_id'] == rid].iloc[0]
    y0 = (float(row.theta0), float(row.omega_init))
    sol = solve_ivp(rhs, (0.0, 30.0), y0, t_eval=t_eval, method='DOP853', rtol=1e-12, atol=1e-14)
    if not sol.success:
        raise RuntimeError(sol.message)
    return sol.y


truth = {rid: integrate(rid, rhs_truth) for rid in set(COMP_REP).union(HOLDOUTS)}
pred = {rid: integrate(rid, rhs_sir) for rid in HOLDOUTS}

theta_rmse, omega_rmse = [], []
for h in HORIZONS:
    mask = t_eval <= h + 1e-12
    e_th = np.concatenate([(pred[r][0, mask] - truth[r][0, mask]) for r in HOLDOUTS])
    e_om = np.concatenate([(pred[r][1, mask] - truth[r][1, mask]) for r in HOLDOUTS])
    theta_rmse.append(np.sqrt(np.mean(e_th**2)))
    omega_rmse.append(np.sqrt(np.mean(e_om**2)))
theta_rmse = np.asarray(theta_rmse)
omega_rmse = np.asarray(omega_rmse)

fig = plt.figure(figsize=(6.15, 4.85), dpi=180, facecolor='white')

fig.text(0.5, 0.962, 'Same Trajectories, Different Task Contracts',
         ha='center', va='top', color=INK, fontsize=14.4, fontweight='bold')
fig.text(0.5, 0.912, 'Same 32-Realization Observational Ensemble',
         ha='center', va='center', color=SLATE, fontsize=8.3, style='italic')

# Rebalanced axes and separator.
axL = fig.add_axes([0.072, 0.183, 0.348, 0.474])
axR = fig.add_axes([0.612, 0.183, 0.338, 0.474])

fig.text(0.245, 0.825, 'Compression', ha='center', va='center',
         color=GREEN, fontsize=12.0, fontweight='bold')
fig.text(0.245, 0.793, r'$q_{\mathrm{comp}}$', ha='center', va='center',
         color=GREEN_MID, fontsize=9.2)
fig.text(0.775, 0.825, 'Prediction', ha='center', va='center',
         color=NAVY, fontsize=12.0, fontweight='bold')
fig.text(0.775, 0.793, r'$q_{\mathrm{pred}}$', ha='center', va='center',
         color=BLUE, fontsize=9.2)

fig.text(0.245, 0.735,
         r'$\omega^2=-3.645(1-\cos\theta)+2E_i$',
         ha='center', va='center', color=INK, fontsize=9.1,
         bbox=dict(boxstyle='round,pad=0.25', fc='#F2F8F5', ec=GREEN_LIGHT, lw=0.8))
fig.text(0.775, 0.735,
         r'$\dot\theta=\omega,\quad \dot\omega=-1.82245149\sin\theta$',
         ha='center', va='center', color=INK, fontsize=8.8,
         bbox=dict(boxstyle='round,pad=0.25', fc='#F3F6FA', ec=BLUE_LIGHT, lw=0.8))

energies = manifest.set_index('realization_id')['energy_initial']
comp_energy = np.array([float(energies.loc[rid]) for rid in COMP_REP])
norm = Normalize(vmin=comp_energy.min(), vmax=comp_energy.max())
cmap = mpl.cm.get_cmap('BuGn')

for rid in COMP_REP:
    th, om = truth[rid]
    x = 1.0 - np.cos(th)
    y = om**2
    color = cmap(norm(float(energies.loc[rid])))
    axL.plot(x, y, color=color, lw=1.35, alpha=0.95, solid_capstyle='round')

axL.set_xlabel(r'$1-\cos\theta$', fontsize=9.0, color=INK, labelpad=3)
axL.set_ylabel(r'$\omega^2$', fontsize=9.0, color=INK, labelpad=3)
axL.text(0.02, 0.975, '8 Representative Discovery Trajectories', transform=axL.transAxes,
         ha='left', va='top', fontsize=7.0, color=SLATE)
axL.grid(True, color=GRID, lw=0.55, alpha=0.75)
axL.spines[['top', 'right']].set_visible(False)
axL.spines[['left', 'bottom']].set_color('#91A0AD')
axL.tick_params(colors=SLATE, labelsize=7.4, length=3)
axL.set_xlim(left=0)
axL.set_ylim(bottom=0)

# Colorbar moved slightly right and lower label kept clearly above it.
cax = fig.add_axes([0.418, 0.318, 0.012, 0.24])
sm = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
cbar = fig.colorbar(sm, cax=cax)
cbar.ax.tick_params(labelsize=6.8, colors=SLATE, length=2)
cbar.outline.set_edgecolor('#A9B7C3')
cbar.outline.set_linewidth(0.7)
fig.text(0.425, 0.572, r'Initial Energy $E_i$', ha='center', va='bottom', fontsize=6.9, color=INK)

# Stats box moved well below the colorbar and kept inside the left plot.
axL.text(0.42, 0.71,
         r'$\mathrm{median}(A_i)=-3.6450$' + '\n' + r'$R^2(B_i,2E_i)=0.999999986$',
         transform=axL.transAxes, ha='left', va='bottom', fontsize=6.7, color=INK,
         bbox=dict(boxstyle='round,pad=0.23', fc=WHITE, ec=GREEN_LIGHT, lw=0.7, alpha=0.96))

axR.plot(HORIZONS, theta_rmse, marker='o', markersize=3.4, lw=1.5,
         color=GREEN, label=r'$\theta$ RMSE (rad)')
axR.plot(HORIZONS, omega_rmse, marker='s', markersize=3.2, lw=1.5,
         color=NAVY, label=r'$\omega$ RMSE (rad s$^{-1}$)')
axR.set_yscale('log')
axR.set_xlabel('Autonomous Forecast Horizon (s)', fontsize=8.7, color=INK, labelpad=3)
axR.set_ylabel('Pooled RMSE', fontsize=8.7, color=INK, labelpad=1)
axR.text(0.03, 0.97, '8 Protected Holdouts; Initial State Only At $t=0$',
         transform=axR.transAxes, ha='left', va='top', fontsize=6.9, color=SLATE)
axR.grid(True, which='major', color=GRID, lw=0.55, alpha=0.8)
axR.grid(True, which='minor', color=GRID, lw=0.35, alpha=0.35)
axR.spines[['top', 'right']].set_visible(False)
axR.spines[['left', 'bottom']].set_color('#91A0AD')
axR.tick_params(colors=SLATE, labelsize=7.4, length=3)
axR.set_xlim(0, 31)
axR.set_xticks([0, 5, 10, 20, 30])
axR.set_ylim(1e-6, 1.2e-3)
axR.legend(frameon=False, fontsize=6.7, loc='upper left', bbox_to_anchor=(0.0, 0.875), handlelength=1.8)

axR.annotate(
    r'$30\,\mathrm{s}:\ \mathrm{RMSE}_{\theta}=3.28\times10^{-4}$' + '\n' +
    r'$\qquad\ \mathrm{RMSE}_{\omega}=3.38\times10^{-4}$',
    xy=(30, theta_rmse[-1]), xycoords='data',
    xytext=(0.965, 0.085), textcoords='axes fraction',
    ha='right', va='bottom', fontsize=6.8, color=INK,
    bbox=dict(boxstyle='round,pad=0.25', fc=WHITE, ec=BLUE_LIGHT, lw=0.7, alpha=0.96),
    arrowprops=dict(arrowstyle='->', lw=0.7, color=BLUE, shrinkA=3, shrinkB=4)
)

fig.text(0.245, 0.098, 'Shared Invariant + One Scalar Per Realization',
         ha='center', va='center', color=GREEN, fontsize=7.3, fontweight='semibold')
fig.text(0.779, 0.098, 'Frozen Evolution Law + Autonomous Held-Out Rollout',
         ha='center', va='center', color=NAVY, fontsize=7.3, fontweight='semibold')

# Separator moved slightly left so it never interferes with right-axis label.
fig.lines.append(mpl.lines.Line2D([0.548, 0.548], [0.14, 0.84], transform=fig.transFigure,
                                  color='#E2E7EB', lw=0.8))

fig.savefig(OUT_PNG, dpi=400, bbox_inches='tight', pad_inches=0.035, facecolor='white')
fig.savefig(OUT_PDF, bbox_inches='tight', pad_inches=0.035, facecolor='white')
fig.savefig(OUT_SVG, bbox_inches='tight', pad_inches=0.035, facecolor='white')
plt.close(fig)

print(OUT_PNG)
print(OUT_PDF)
print(OUT_SVG)
