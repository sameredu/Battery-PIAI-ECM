"""
data_loader.py
--------------
Load NASA battery MAT files and extract discharge cycle records.
Returns a clean DataFrame with per-cycle capacity, voltage, current,
temperature statistics, and impedance (Re, Rct) from adjacent EIS sweeps.
"""

import numpy as np
import pandas as pd
import scipy.io
import os

from src.config import BATTERY_KEYS, BATTERY_FILES, RE_MIN_OHM, RE_MAX_OHM, RCT_MIN_OHM, RCT_MAX_OHM


def _safe_float(val):
    """Safely convert a value to a scalar float."""
    arr = np.atleast_1d(val).flatten()
    return float(arr[0]) if len(arr) > 0 else np.nan


def extract_battery_cycles(mat_file: str, battery_name: str) -> pd.DataFrame:
    """
    Parse a NASA battery MAT file and return a DataFrame of discharge cycles.

    Each row corresponds to one discharge cycle and contains:
        - CycleIndex   : sequential discharge count (1-based)
        - Capacity_Ah  : measured discharge capacity (Ah)
        - Re           : electrolyte resistance from preceding EIS sweep (Ω)
        - Rct          : charge-transfer resistance from preceding EIS sweep (Ω)
        - V_min/V_max/V_mean : voltage statistics during discharge
        - T_mean/T_max : temperature statistics during discharge
        - I_mean       : mean absolute current during discharge (A)
        - Duration_s   : total discharge duration (s)

    Parameters
    ----------
    mat_file     : path to the .mat file
    battery_name : e.g. "B0005"

    Returns
    -------
    pd.DataFrame
    """
    d = scipy.io.loadmat(mat_file, squeeze_me=True, struct_as_record=False)
    cycles = d[battery_name].cycle

    records = []
    discharge_idx = 0
    last_re  = np.nan
    last_rct = np.nan

    for cyc in cycles:
        ctype = cyc.type

        # ── EIS sweep: update last known Re / Rct ─────────────────────────
        if ctype == 'impedance':
            data = cyc.data
            re_val  = _safe_float(data.Re)
            rct_val = _safe_float(data.Rct)
            if RE_MIN_OHM < re_val < RE_MAX_OHM:
                last_re = re_val
            if RCT_MIN_OHM < rct_val < RCT_MAX_OHM:
                last_rct = rct_val

        # ── Discharge cycle: record features ──────────────────────────────
        elif ctype == 'discharge':
            discharge_idx += 1
            data = cyc.data

            cap = _safe_float(data.Capacity) if hasattr(data, 'Capacity') else np.nan
            v   = np.atleast_1d(data.Voltage_measured).flatten()
            i   = np.atleast_1d(data.Current_measured).flatten()
            t   = np.atleast_1d(data.Temperature_measured).flatten()
            tm  = np.atleast_1d(data.Time).flatten()

            records.append({
                'Battery'    : battery_name,
                'CycleIndex' : discharge_idx,
                'Capacity_Ah': cap,
                'Re'         : last_re,
                'Rct'        : last_rct,
                'V_min'      : float(v.min()),
                'V_max'      : float(v.max()),
                'V_mean'     : float(v.mean()),
                'T_mean'     : float(t.mean()),
                'T_max'      : float(t.max()),
                'I_mean'     : float(np.abs(i).mean()),
                'Duration_s' : float(tm[-1] - tm[0]) if len(tm) > 1 else np.nan,
            })

    return pd.DataFrame(records)


def load_all_batteries(battery_files: dict = None) -> pd.DataFrame:
    """
    Load and concatenate discharge cycles for all four NASA cells.

    Parameters
    ----------
    battery_files : dict mapping battery name -> MAT file path.
                    Defaults to BATTERY_FILES from config.

    Returns
    -------
    pd.DataFrame with 636 rows (168+168+168+132)
    """
    if battery_files is None:
        battery_files = BATTERY_FILES

    dfs = []
    for name, path in battery_files.items():
        if not os.path.exists(path):
            print(f"  [WARNING] {path} not found — skipping {name}")
            continue
        df = extract_battery_cycles(path, name)
        print(f"  {name}: {len(df)} discharge cycles  "
              f"Cap {df['Capacity_Ah'].min():.3f}–{df['Capacity_Ah'].max():.3f} Ah  "
              f"Re {df['Re'].min()*1000:.1f}–{df['Re'].max()*1000:.1f} mΩ")
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    print(f"\n  Total: {len(combined)} cycles across {combined['Battery'].nunique()} cells")
    return combined
