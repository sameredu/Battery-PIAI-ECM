import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
import os
import json
import matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.config import MODEL_PATH, METRICS_PATH, FIGURES_DIR, TABLES_DIR, TEST_BATTERY, RANDOM_STATE
from src.feature_engineering import prepare_features

def train_rul(X_train, y_train):
    """
    Trains a RandomForestRegressor model on the training features.
    Matches the requested rul_model template.
    """
    model = RandomForestRegressor(n_estimators=200, random_state=RANDOM_STATE, max_depth=10, min_samples_leaf=1)
    model.fit(X_train, y_train)
    return model

def evaluate(model, X_test, y_test):
    """
    Evaluates the model on test features and returns RMSE and R-squared.
    Matches the requested rul_model template.
    """
    pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    r2 = r2_score(y_test, pred)
    return rmse, r2

def save_model(model, path=MODEL_PATH):
    """
    Saves the trained model to disk.
    Matches the requested rul_model template.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    print(f"Saved model to {path}")

def run_rul_pipeline(df_params, df_full_capacity):
    """
    Runs the RUL training and evaluation pipeline:
    - Calculates actual RUL target based on full capacity and EOL
    - Merges with ECM parameters
    - Splits data by Leave-One-Battery-Out (LOBO) on TEST_BATTERY
    - Train and evaluate Random Forest Regressor
    - Save plots, feature importances, metrics, and trained model
    """
    print("\nRunning RUL prediction pipeline...")
    
    # 1. EOL calculation
    # df_full_capacity has cols: ['Battery_ID', 'CycleIndex', 'Capacity_Ah_Full']
    # EOL defined as Capacity_Ah_Full <= 1.40
    # Group by Battery_ID and find min CycleIndex where capacity <= 1.40
    eol_thresh = 1.40
    eol_df = df_full_capacity[df_full_capacity['Capacity_Ah_Full'] <= eol_thresh]
    eol_cycles = eol_df.groupby('Battery_ID')['CycleIndex'].min()
    
    print("Calculated End-of-Life (EOL) Cycles (at <= 1.4 Ah):")
    for b_id, eol_c in eol_cycles.items():
        print(f"  {b_id}: {eol_c} cycles")
        
    # Map EOL cycle to each battery; if a battery didn't reach EOL, use its max cycle
    max_cycles = df_full_capacity.groupby('Battery_ID')['CycleIndex'].max()
    
    df_full_capacity['EOL_Cycle'] = df_full_capacity['Battery_ID'].map(eol_cycles)
    df_full_capacity['EOL_Cycle'] = df_full_capacity.apply(
        lambda row: row['EOL_Cycle'] if pd.notna(row['EOL_Cycle']) 
        else max_cycles.get(row['Battery_ID'], row['CycleIndex']),
        axis=1
    )
    
    # RUL is EOL_Cycle - CycleIndex (clamped at 0)
    df_full_capacity['RUL'] = (df_full_capacity['EOL_Cycle'] - df_full_capacity['CycleIndex']).clip(lower=0)
    
    # 2. Prepare features (tau constants)
    df_feat = prepare_features(df_params)
    
    # Rename Battery to Battery_ID for merging if needed
    if 'Battery' in df_feat.columns:
        df_feat = df_feat.rename(columns={'Battery': 'Battery_ID'})
        
    # 3. Merge features (X) and actual RUL (Y)
    df_merged = pd.merge(
        df_feat,
        df_full_capacity[['Battery_ID', 'CycleIndex', 'RUL']],
        on=['Battery_ID', 'CycleIndex'],
        how='left'
    )
    
    # Drop rows without RUL target
    df_merged = df_merged.dropna(subset=['RUL']).reset_index(drop=True)
    print(f"Merged features and target. Shape: {df_merged.shape}")
    
    # 4. Standardize features
    FEATURES = ['R0', 'R1', 'C1', 'R2', 'C2', 'Voc_slope', 'Voc_intercept', 'Capacity_Ah']
    TARGET = 'RUL'
    
    X = df_merged[FEATURES].copy()
    y = df_merged[TARGET].copy()
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled_df = pd.DataFrame(X_scaled, columns=FEATURES)
    
    # Add Battery_ID and CycleIndex back
    df_scaled_all = X_scaled_df.copy()
    df_scaled_all['Battery_ID'] = df_merged['Battery_ID']
    df_scaled_all['CycleIndex'] = df_merged['CycleIndex']
    df_scaled_all['RUL'] = y
    
    # 5. Data Split (LOBO)
    train_df = df_scaled_all[df_scaled_all['Battery_ID'] != TEST_BATTERY]
    test_df = df_scaled_all[df_scaled_all['Battery_ID'] == TEST_BATTERY]
    
    print(f"LOBO split: Training on {train_df['Battery_ID'].unique()}, testing on {TEST_BATTERY}")
    
    X_train = train_df[FEATURES]
    y_train = train_df[TARGET]
    X_test = test_df[FEATURES]
    y_test = test_df[TARGET]
    
    if X_train.empty or X_test.empty:
        print("Error: Train or test data is empty. Cannot train RUL model.")
        return
        
    # 6. Train model
    print("Training Random Forest Regressor...")
    model = train_rul(X_train, y_train)
    
    # 7. Evaluate model
    rmse, r2 = evaluate(model, X_test, y_test)
    print(f"\n--- Final PIAI-RUL Results on {TEST_BATTERY} ---")
    print(f"  RMSE: {rmse:.2f} cycles")
    print(f"  R2:   {r2:.3f}")
    
    # Save model and scaler (can bundle together in dict if needed, or just model)
    save_model(model, MODEL_PATH)
    
    # 8. Save metrics to json
    metrics = {
        'test_battery': TEST_BATTERY,
        'rmse_cycles': float(rmse),
        'r2_score': float(r2),
        'features_used': FEATURES
    }
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=4)
    print(f"Saved metrics to {METRICS_PATH}")
    
    # 9. Plot prediction results
    plt.figure(figsize=(12, 6))
    # Retrieve unscaled test cycles
    test_cycles = df_merged[df_merged['Battery_ID'] == TEST_BATTERY]['CycleIndex']
    y_pred = model.predict(X_test)
    
    plt.plot(test_cycles, y_test, label=f'Actual RUL ({TEST_BATTERY})', color='blue', linewidth=2, marker='o')
    plt.plot(test_cycles, y_pred, label=f'Predicted RUL (PIAI-RF) (RMSE: {rmse:.2f})', color='red', linestyle='--', marker='x')
    plt.title(f'RUL Prediction using PIAI Features (Test on {TEST_BATTERY})')
    plt.xlabel('Cycle Index')
    plt.ylabel('Remaining Useful Life (RUL) - Cycles')
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    
    os.makedirs(FIGURES_DIR, exist_ok=True)
    plt.savefig(os.path.join(FIGURES_DIR, "rul_predictions_vs_actual.png"), dpi=300)
    plt.close()
    
    # 10. Feature Importance
    importances = model.feature_importances_
    importance_df = pd.DataFrame({
        'Feature': FEATURES,
        'Importance': importances
    }).sort_values(by='Importance', ascending=False)
    
    os.makedirs(TABLES_DIR, exist_ok=True)
    importance_df.to_csv(os.path.join(TABLES_DIR, "table2_feature_importance.csv"), index=False)
    
    print("\nFeature Importances:")
    print(importance_df.to_string(index=False))
    
    return metrics
