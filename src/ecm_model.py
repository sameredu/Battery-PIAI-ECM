import numpy as np
import math

def ecm_model(params, I, t):
    """
    Simplified baseline model as requested in the template.
    Uses R0, R1, C1, R2, C2 (first 5 parameters) and returns voltage V = I * R0.
    """
    R0, R1, C1, R2, C2 = params[:5]
    V = I * R0  # simplified baseline
    return V

def simulate_ecm_2rc(x, I, dt, Qnom):
    """
    Full 2-RC Equivalent Circuit Model simulation as implemented in the Colab code.
    Parameters x: [R0, R1, C1, R2, C2, Voc_slope, Voc_intercept]
    I: Measured current array (A) - negative values denote discharge.
    dt: Array of time steps (s).
    Qnom: Nominal capacity of the cell (Ah).
    
    Returns: Simulated terminal voltage array (V).
    """
    if len(x) != 7:
        return np.zeros(len(I))
        
    R0, R1, C1, R2, C2, a, b = x
    V = np.zeros(len(I))
    v1 = 0.0
    v2 = 0.0
    q = 0.0
    Qc = max(1e-6, Qnom * 3600.0)  # capacity in Ampere-seconds
    
    if len(dt) == 0:
        dt = np.array([0.1])
        
    for k in range(len(I)):
        dtk = dt[k] if k < len(dt) else dt[-1]
        ik = I[k]
        
        # q accumulates discharged capacity (as current is negative for discharge)
        q += -ik * dtk
        soc = min(max(q / Qc, 0.0), 1.0)
        
        tau1 = max(1e-12, R1 * C1)
        tau2 = max(1e-12, R2 * C2)
        
        dt_tau1 = -dtk / tau1 if tau1 > 1e-9 else -1000.0
        dt_tau2 = -dtk / tau2 if tau2 > 1e-9 else -1000.0
        
        # Exponential discretization of the RC transient equations
        a1 = math.exp(max(dt_tau1, -700.0))
        a2 = math.exp(max(dt_tau2, -700.0))
        
        v1 = a1 * v1 + (1.0 - a1) * (R1 * ik)
        v2 = a2 * v2 + (1.0 - a2) * (R2 * ik)
        
        # Voc is approximated as a linear function of depth-of-discharge (soc)
        Voc = a * soc + b
        
        V[k] = Voc - ik * R0 - v1 - v2
        
    return V
