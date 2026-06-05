"""
eis_features.py
---------------
Validate and summarise EIS-derived impedance features (Re, Rct).
Re  = electrolyte resistance  (series resistance, SEI layer proxy)
Rct = charge-transfer resistance (kinetic degradation proxy)

Both values are read directly from the NASA MAT file impedance fields —
no circuit fitting is performed.
"""

import numpy as np
import pandas as pd
from scipy import stats

from src.config import RE_MIN_OHM, RE_MAX_OHM, RCT_MIN_OHM, RCT_MAX_OHM


def validate_eis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flag and optionally remove EIS readings outside plausible physical bounds.

    Parameters
    ----------
    df : DataFrame with 'Re' and 'Rct' columns (in Ohms)

    Returns
    -------
    DataFrame with added boolean columns 'Re_valid' and 'Rct_valid'
    """
    df = df.copy()
    df['Re_valid']  = df['Re'].between(RE_MIN_OHM,  RE_MAX_OHM)
    df['Rct_valid'] = df['Rct'].between(RCT_MIN_OHM, RCT_MAX_OHM)

    n_bad_re  = (~df['Re_valid']).sum()
    n_bad_rct = (~df['Rct_valid']).sum()
    if n_bad_re:
        print(f"  [EIS] {n_bad_re} Re values outside [{RE_MIN_OHM*1000:.0f}, {RE_MAX_OHM*1000:.0f}] mΩ")
    if n_bad_rct:
        print(f"  [EIS] {n_bad_rct} Rct values outside [{RCT_MIN_OHM*1000:.0f}, {RCT_MAX_OHM*1000:.0f}] mΩ")
    return df


def eis_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-cell summary of EIS parameter evolution.

    Returns a DataFrame with columns:
        Battery, Re_initial_mΩ, Re_final_mΩ, Re_change_pct,
        Rct_initial_mΩ, Rct_final_mΩ, Rct_change_pct,
        Re_slope_mΩ_per_cycle, Rct_slope_mΩ_per_cycle
    """
    rows = []
    for bat, grp in df.groupby('Battery'):
        g = grp.dropna(subset=['Re', 'Rct']).sort_values('CycleIndex')
        if len(g) < 2:
            continue

        re_i  = g.iloc[0]['Re']  * 1000
        re_f  = g.iloc[-1]['Re'] * 1000
        rct_i = g.iloc[0]['Rct']  * 1000
        rct_f = g.iloc[-1]['Rct'] * 1000

        sl_re,  *_ = stats.linregress(g['CycleIndex'], g['Re'])
        sl_rct, *_ = stats.linregress(g['CycleIndex'], g['Rct'])

        rows.append({
            'Battery'             : bat,
            'Re_initial_mΩ'       : round(re_i, 2),
            'Re_final_mΩ'         : round(re_f, 2),
            'Re_change_pct'       : round((re_f - re_i) / re_i * 100, 1),
            'Rct_initial_mΩ'      : round(rct_i, 2),
            'Rct_final_mΩ'        : round(rct_f, 2),
            'Rct_change_pct'      : round((rct_f - rct_i) / rct_i * 100, 1),
            'Re_slope_mΩ_per_cyc' : round(sl_re  * 1000, 5),
            'Rct_slope_mΩ_per_cyc': round(sl_rct * 1000, 5),
        })
    return pd.DataFrame(rows)


def re_rct_coupling(df: pd.DataFrame) -> dict:
    """
    Linear regression of Rct on Re across all cells.

    Returns dict with keys: slope, intercept, R2, pval, n
    """
    valid = df.dropna(subset=['Re', 'Rct'])
    sl, ic, rv, pv, _ = stats.linregress(valid['Re'], valid['Rct'])
    return {
        'slope'    : round(sl, 4),
        'intercept': round(ic, 4),
        'R2'       : round(rv**2, 4),
        'pval'     : float(pv),
        'n'        : len(valid),
    }
