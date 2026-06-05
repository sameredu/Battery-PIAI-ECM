import os
import numpy as np
import pandas as pd
import scipy.io

def load_nasa_data(path):
    """
    Loads raw NASA .mat files and returns a dictionary mapping cell names to mat objects.
    Matches the requested data_loader template.
    """
    data = {}
    files = ["B0005.mat", "B0006.mat", "B0007.mat", "B0018.mat"]

    for f in files:
        full_path = os.path.join(path, f)
        if os.path.exists(full_path):
            data[f.replace(".mat", "")] = scipy.io.loadmat(full_path)
        else:
            print(f"Warning: File {full_path} not found.")

    return data

def get_field(obj, *names):
    """
    Helper to robustly extract fields from nested structures or dictionaries.
    """
    for n in names:
        try:
            if hasattr(obj, n):
                return getattr(obj, n)
            if isinstance(obj, dict) and n in obj:
                return obj[n]
        except Exception:
            pass
    return None

def load_cycles(file_path):
    """
    Loads raw cycles array from a NASA mat file.
    """
    m = scipy.io.loadmat(file_path, squeeze_me=True, struct_as_record=False)
    keys = [k for k in m.keys() if not k.startswith("__")]
    if not keys:
        return []
    
    # Try to find the key matching the filename or containing 'cycle'
    main_key = None
    file_basename = os.path.basename(file_path).replace('.mat', '')
    if file_basename in keys:
        main_key = file_basename
    else:
        for k in keys:
            if hasattr(m[k], 'cycle'):
                main_key = k
                break
    
    if main_key is None:
        main_key = keys[0]
        
    obj = m[main_key]
    cycles = get_field(obj, 'cycle')
    
    if cycles is None:
        for k in keys:
            v = m[k]
            cycles = get_field(v, 'cycle')
            if cycles is not None:
                break
                
    if cycles is None:
        print(f"Warning: Could not find 'cycle' structure in {file_path}")
        return []
        
    return cycles if hasattr(cycles, "__len__") else [cycles]

def cycle_to_df(cycle):
    """
    Converts a single cycle structure's data field to a Pandas DataFrame.
    """
    data = get_field(cycle, 'data')
    if data is None:
        return pd.DataFrame()
        
    def to_np(x):
        try:
            return np.asarray(x).flatten()
        except Exception:
            return np.array([])
            
    t = to_np(get_field(data, 'Time', 'time', 'timestamp'))
    v = to_np(get_field(data, 'Voltage_measured', 'Voltage', 'voltage'))
    i = to_np(get_field(data, 'Current_measured', 'Current', 'current'))
    
    m = min(len(t), len(v), len(i)) if len(t) > 0 else 0
    if m == 0:
        return pd.DataFrame()
        
    return pd.DataFrame({'Time (s)': t[:m], 'Voltage (V)': v[:m], 'Current (A)': i[:m]})

def is_discharge(cycle):
    """
    Checks if a cycle is a discharge cycle based on the type metadata or current values.
    """
    typ = get_field(cycle, 'type')
    if typ is not None:
        try:
            return 'discharge' in str(typ).lower()
        except Exception:
            pass
    
    df = cycle_to_df(cycle)
    return (not df.empty) and (np.mean(df['Current (A)']) < 0)

def compute_capacity_Ah(df):
    """
    Integrates current over time to compute discharge capacity in Ah.
    """
    t = df['Time (s)'].values
    i = df['Current (A)'].values
    if len(t) < 2:
        return np.nan
    dt = np.diff(t, prepend=t[0])
    return np.sum(np.abs(i) * dt) / 3600.0

def load_full_capacity(file_path, battery_key):
    """
    Loads EOL-tracking capacity values directly from raw .mat file
    cycles for discharge type cycles.
    """
    try:
        mat_file = scipy.io.loadmat(file_path, squeeze_me=True, struct_as_record=False)
        keys = [k for k in mat_file.keys() if not k.startswith("__")]
        
        main_key = None
        if battery_key in keys:
            main_key = battery_key
        else:
            for k in keys:
                if hasattr(mat_file[k], 'cycle'):
                    main_key = k
                    break
        if main_key is None:
            main_key = keys[0]
            
        cycles = mat_file[main_key].cycle
        capacity_data = []
        discharge_cycle_index = 0
        
        for cycle_struct in cycles:
            typ = get_field(cycle_struct, 'type')
            if typ is not None and 'discharge' in str(typ).lower():
                discharge_cycle_index += 1
                data = get_field(cycle_struct, 'data')
                if data is not None:
                    # In python-scipy struct_as_record=False, fields are attributes
                    capacity = np.nan
                    if hasattr(data, 'Capacity'):
                        cap_val = getattr(data, 'Capacity')
                        try:
                            capacity = float(np.asarray(cap_val).flatten()[0])
                        except Exception:
                            pass
                    
                    if not np.isnan(capacity):
                        capacity_data.append({
                            'Battery_ID': battery_key,
                            'CycleIndex': discharge_cycle_index,
                            'Capacity_Ah_Full': capacity
                        })
        return pd.DataFrame(capacity_data)
    except Exception as e:
        print(f"Error loading full capacity for {battery_key} from {file_path}: {e}")
        return pd.DataFrame()
