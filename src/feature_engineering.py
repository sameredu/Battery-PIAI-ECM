import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

def extract_features(ecm_params):
    """
    Extracts features from ECM parameters.
    Matches the requested feature_extraction template.
    """
    R0, R1, C1, R2, C2 = ecm_params[:5]

    return {
        "R0": R0,
        "R1": R1,
        "C1": C1,
        "R2": R2,
        "C2": C2,
        "tau1": R1 * C1,
        "tau2": R2 * C2
    }

def prepare_features(df):
    """
    Derives physics-informed features (time constants tau1, tau2) from parameters dataframe.
    """
    df_feat = df.copy()
    
    # Calculate RC branch time constants (tau = R * C)
    df_feat['tau1'] = df_feat['R1'] * df_feat['C1']
    df_feat['tau2'] = df_feat['R2'] * df_feat['C2']
    
    return df_feat

def scale_features(df, features_list):
    """
    Applies StandardScaler to numerical features.
    """
    df_scaled = df.copy()
    scaler = StandardScaler()
    df_scaled[features_list] = scaler.fit_transform(df_scaled[features_list])
    return df_scaled, scaler
