"""
visualisation.py
----------------
Generate publication-quality figures (Fig 2–5) from processed battery data.
Fig 6 (RUL prediction) is generated inside rul_model.py.

Figures produced:
  fig2_capacity_fade.png     — capacity vs. cycle + regression fits
  fig3_Re_trend.png          — Re trend vs. cycle + regression fits
  fig4_coupling_heatmap.png  — Re–Rct coupling scatter + correlation matrix
  fig5_radar.png             — normalised degradation radar signatures
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import os

from src.config import FIGURES_DIR, EOL_THRESHOLD

COLORS  = {'B0005': '#2166AC', 'B0006': '#D6604D',
           'B0007': '#4DAC26', 'B0018': '#8073AC'}
MARKERS = {'B0005': 'o', 'B0006': 's', 'B0007': '^', 'B0018': 'D'}
BATS    = ['B0005', 'B0006', 'B0007', 'B0018']

RCPARAMS = {
    'font.family'      : 'DejaVu Serif',
    'font.size'        : 12,
    'axes.labelsize'   : 13,
    'axes.titlesize'   : 13,
    'legend.fontsize'  : 10,
    'axes.spines.top'  : False,
    'axes.spines.right': False,
    'savefig.dpi'      : 200,
    'savefig.bbox'     : 'tight',
}


def _save(fig, name):
    os.makedirs(FIGURES_DIR, exist_ok=True)
    path = os.path.join(FIGURES_DIR, name)
    fig.savefig(path)
    plt.close(fig)
    print(f"  Saved → {path}")


def plot_capacity_fade(df: pd.DataFrame):
    """Fig 2 — Capacity fade with linear regression fits."""
    plt.rcParams.update(RCPARAMS)
    fig, ax = plt.subplots(figsize=(8, 5))

    for bat in BATS:
        g = df[df['Battery'] == bat].sort_values('CycleIndex')
        ax.scatter(g['CycleIndex'], g['Capacity_Ah'],
                   s=8, alpha=0.4, color=COLORS[bat])
        sl, ic, rv, *_ = stats.linregress(g['CycleIndex'], g['Capacity_Ah'])
        x = np.array([g['CycleIndex'].min(), g['CycleIndex'].max()])
        ax.plot(x, sl * x + ic, color=COLORS[bat], lw=2,
                label=f'{bat}: {sl*1000:.2f}×10⁻³ Ah/cyc, R²={rv**2:.3f}')

    ax.axhline(EOL_THRESHOLD, color='#B22222', ls='--', lw=1.5,
               label=f'EOL threshold ({EOL_THRESHOLD} Ah)')
    ax.set_xlabel('Cycle Index')
    ax.set_ylabel('Discharge Capacity (Ah)')
    ax.set_title('Fig. 2  Capacity Fade with Linear Regression Fits')
    ax.legend(framealpha=0.9)
    ax.set_ylim([1.0, 2.15])
    fig.tight_layout()
    _save(fig, 'fig2_capacity_fade.png')


def plot_re_trend(df: pd.DataFrame):
    """Fig 3 — Electrolyte resistance Re trend."""
    plt.rcParams.update(RCPARAMS)
    fig, ax = plt.subplots(figsize=(8, 5))

    for bat in BATS:
        g = df[df['Battery'] == bat].dropna(subset=['Re']).sort_values('CycleIndex')
        ax.scatter(g['CycleIndex'], g['Re'] * 1000,
                   s=8, alpha=0.4, color=COLORS[bat])
        sl, ic, rv, *_ = stats.linregress(g['CycleIndex'], g['Re'])
        x = np.array([g['CycleIndex'].min(), g['CycleIndex'].max()])
        ax.plot(x, (sl * x + ic) * 1000, color=COLORS[bat], lw=2,
                label=f'{bat}: {sl*1e6:.2f}×10⁻⁶ Ω/cyc, R²={rv**2:.3f}')

    ax.set_xlabel('Cycle Index')
    ax.set_ylabel('Electrolyte Resistance Re (mΩ)')
    ax.set_title('Fig. 3  Re Trend over Cycling')
    ax.legend(framealpha=0.9)
    fig.tight_layout()
    _save(fig, 'fig3_Re_trend.png')


def plot_coupling_heatmap(df: pd.DataFrame):
    """Fig 4 — Re–Rct coupling scatter and Pearson correlation matrix."""
    plt.rcParams.update(RCPARAMS)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Re vs Rct scatter
    ax = axes[0]
    for bat in BATS:
        g = df[df['Battery'] == bat].dropna(subset=['Re', 'Rct'])
        ax.scatter(g['Re'] * 1000, g['Rct'] * 1000,
                   s=12, alpha=0.6, color=COLORS[bat],
                   marker=MARKERS[bat], label=bat)

    valid = df.dropna(subset=['Re', 'Rct'])
    sl, ic, rv, *_ = stats.linregress(valid['Re'], valid['Rct'])
    x_fit = np.linspace(valid['Re'].min(), valid['Re'].max(), 100)
    ax.plot(x_fit * 1000, (sl * x_fit + ic) * 1000,
            'k--', lw=2, label=f'Fit: R²={rv**2:.3f}')
    ax.set_xlabel('Re (mΩ)')
    ax.set_ylabel('Rct (mΩ)')
    ax.set_title(f'Re–Rct Coupling  (R² = {rv**2:.3f})')
    ax.legend(fontsize=10)

    # Right: correlation heatmap
    ax2 = axes[1]
    feats  = ['Re', 'Rct', 'Capacity_Ah', 'CycleIndex']
    labels = ['Re', 'Rct', 'Capacity', 'Cycle']
    corr   = df[feats].dropna().rename(
        columns=dict(zip(feats, labels))).corr().values

    im = ax2.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
    ax2.set_xticks(range(len(labels)))
    ax2.set_yticks(range(len(labels)))
    ax2.set_xticklabels(labels, rotation=45, ha='right')
    ax2.set_yticklabels(labels)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax2.text(j, i, f'{corr[i, j]:.2f}', ha='center', va='center',
                     fontsize=12, color='white' if abs(corr[i, j]) > 0.5 else 'black')
    plt.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)
    ax2.set_title('Pearson Correlation Matrix')

    fig.suptitle('Fig. 4  Impedance Coupling and Correlation', fontsize=13, y=1.01)
    fig.tight_layout()
    _save(fig, 'fig4_coupling_heatmap.png')


def plot_radar(df: pd.DataFrame):
    """Fig 5 — Normalised degradation radar signatures."""
    plt.rcParams.update(RCPARAMS)
    fig, ax = plt.subplots(figsize=(7, 5), subplot_kw=dict(polar=True))

    categories = ['Re inc\n(%)', 'Rct inc\n(%)', 'Cap\nfade (%)',
                  'EOL\n(norm.)', 'Re–Cap\nR²×100']
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)] + [0]

    bat_metrics = {}
    for bat in BATS:
        g   = df[df['Battery'] == bat].sort_values('CycleIndex')
        imp = g.dropna(subset=['Re', 'Rct'])
        if len(imp) < 2:
            continue
        re_pct  = (imp.iloc[-1]['Re']  - imp.iloc[0]['Re'])  / imp.iloc[0]['Re']  * 100
        rct_pct = (imp.iloc[-1]['Rct'] - imp.iloc[0]['Rct']) / imp.iloc[0]['Rct'] * 100
        cap_f   = (g.iloc[0]['Capacity_Ah'] - g.iloc[-1]['Capacity_Ah']) / g.iloc[0]['Capacity_Ah'] * 100
        below   = g[g['Capacity_Ah'] <= EOL_THRESHOLD]
        eol_n   = below['CycleIndex'].min() / 168 * 100 if len(below) else 100
        sl, _, rv, *_ = stats.linregress(imp['Re'], imp['Capacity_Ah'])
        bat_metrics[bat] = [re_pct, rct_pct, cap_f, eol_n, rv**2 * 100]

    all_v = np.array(list(bat_metrics.values()))
    mn, mx = all_v.min(0), all_v.max(0)

    for bat, raw in bat_metrics.items():
        norm = (np.array(raw) - mn) / (mx - mn + 1e-9) * 100
        vals = list(norm) + [norm[0]]
        ax.plot(angles, vals, color=COLORS[bat], lw=2, label=bat)
        ax.fill(angles, vals, color=COLORS[bat], alpha=0.15)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=10)
    ax.set_ylim(0, 110)
    ax.set_title('Fig. 5  Battery Degradation Radar Signatures', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    fig.tight_layout()
    _save(fig, 'fig5_radar.png')


def generate_all_figures(df: pd.DataFrame):
    """Generate Figures 2–5 from processed DataFrame."""
    print("\n[FIGURES] Generating publication figures...")
    plot_capacity_fade(df)
    plot_re_trend(df)
    plot_coupling_heatmap(df)
    plot_radar(df)
    print("[FIGURES] Done — Figs 2–5 saved.")
