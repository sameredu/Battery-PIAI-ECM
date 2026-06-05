import numpy as np
import pandas as pd
from scipy.optimize import least_squares
from tqdm import tqdm
import os
import warnings

from src.config import LB, UB, X0, LEAST_SQUARES_MAX_NFEV, SAMPLING_INTERVAL, COMBINED_PARAMS_CSV
from src.ecm_model import ecm_model, simulate_ecm_2rc
from src.data_loader import load_cycles, cycle_to_df, is_discharge, compute_capacity_Ah

# Ignore runtime optimization warnings (e.g. division by zero, overflow)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

def residuals(params, I, V_meas, t):
    """
    Residuals calculation for the simplified template ecm_model.
    """
    V_sim = ecm_model(params, I, t)
    return V_meas - V_sim

def fit_ecm(I, V, t):
    """
    Fits the simplified baseline model as requested in the template.
    """
    x0 = [0.01, 0.01, 1000, 0.01, 1000]
    result = least_squares(residuals, x0, args=(I, V, t))
    return result.x

def resid_2rc(x, I, t, V_meas, Qnom):
    """
    Calculates residuals for the 2-RC model optimization.
    """
    dt = np.diff(t, prepend=t[0])
    V_sim = simulate_ecm_2rc(x, I, dt, Qnom)
    m = min(len(V_sim), len(V_meas))
    if m == 0:
        return np.zeros(len(V_meas))
    return V_sim[:m] - V_meas[:m]

def fit_cycle_2rc(I, V_meas, t, Qnom):
    """
    Optimizes the 7 parameters of the 2-RC model for a single cycle.
    """
    res = least_squares(
        resid_2rc,
        X0,
        bounds=(LB, UB),
        args=(I, t, V_meas, Qnom),
        method='trf',
        max_nfev=LEAST_SQUARES_MAX_NFEV
    )
    return res.x, res.success

def estimate_all_parameters(mat_files_dict, sampling_interval=SAMPLING_INTERVAL):
    """
    Iterates through batteries, processes discharge cycles, fits parameters,
    and returns a combined DataFrame.
    """
    all_batteries_params = []
    
    for battery_id, mat_path in mat_files_dict.items():
        if not os.path.exists(mat_path):
            print(f"Skipping {battery_id}: mat file not found at {mat_path}")
            continue
            
        print(f"Processing {battery_id} parameter estimation...")
        cycles = load_cycles(mat_path)
        discharge_cycles = [c for c in cycles if is_discharge(c)]
        n_dis = len(discharge_cycles)
        print(f"Found {n_dis} discharge cycles.")
        
        # Sample periodically to keep execution time reasonable
        sampled_indices = list(range(0, n_dis, sampling_interval))
        # Ensure we always keep the last cycle to see full degradation
        if (n_dis - 1) not in sampled_indices and n_dis > 0:
            sampled_indices.append(n_dis - 1)
            
        print(f"Optimizing 2-RC parameters for {len(sampled_indices)} cycles...")
        caps = []
        params_list = []
        cycle_indices = []
        
        # Pre-calculate capacities to determine max capacity (nominal)
        temp_caps = []
        for c in discharge_cycles:
            df = cycle_to_df(c)
            if not df.empty:
                temp_caps.append(compute_capacity_Ah(df))
            else:
                temp_caps.append(np.nan)
                
        max_cap = np.nanmax(temp_caps) if np.nanmax(temp_caps) > 0 else 1.5
        
        for idx in tqdm(sampled_indices):
            c = discharge_cycles[idx]
            df = cycle_to_df(c)
            if df.empty or len(df) < 10:
                continue
                
            t = df['Time (s)'].values
            Vm = df['Voltage (V)'].values
            I = df['Current (A)'].values
            
            cap_ah = compute_capacity_Ah(df)
            Qnom = max_cap
            
            try:
                fitted_params, success = fit_cycle_2rc(I, Vm, t, Qnom)
                if success:
                    params_list.append(fitted_params)
                    caps.append(cap_ah)
                    cycle_indices.append(idx + 1)
            except Exception as e:
                print(f"Error optimizing cycle {idx+1}: {e}")
                
        if params_list:
            df_params = pd.DataFrame(params_list, columns=['R0', 'R1', 'C1', 'R2', 'C2', 'Voc_slope', 'Voc_intercept'])
            df_params['Capacity_Ah'] = caps
            df_params['CycleIndex'] = cycle_indices
            df_params['Battery'] = battery_id
            all_batteries_params.append(df_params)
            
    if all_batteries_params:
        df_combined = pd.concat(all_batteries_params, ignore_index=True)
        # Sort and clean
        df_combined = df_combined.dropna().reset_index(drop=True)
        # Save to processed folder
        os.makedirs(os.path.dirname(COMBINED_PARAMS_CSV), exist_ok=True)
        df_combined.to_csv(COMBINED_PARAMS_CSV, index=False)
        print(f"Saved estimated parameters to {COMBINED_PARAMS_CSV}")
        return df_combined
    else:
        print("No parameter estimation results generated.")
        return pd.DataFrame()
