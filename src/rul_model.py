"""
rul_model.py
------------
Random Forest RUL prediction using Leave-One-Battery-Out (LOBO) validation.
Train on B0005, B0006, B0007 → test on B0018.

Features: Re, Rct, Capacity_Ah, CycleIndex, V_mean, T_mean, Duration_s
Target  : Remaining Useful Life (cycles to EOL at 1.40 Ah)
"""

import numpy as np
import pandas as pd
import json
import os
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

from src.config import (
    EOL_THRESHOLD, TEST_BATTERY, TRAIN_BATTERIES, FEATURE_COLS,
    RF_N_ESTIMATORS, RF_RANDOM_STATE,
    FIGURES_DIR, TABLES_DIR, METRICS_JSON, MODEL_PKL
)


def compute_rul(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add RUL column to DataFrame.
    RUL = EOL_cycle − CycleIndex  (clipped at 0)
    EOL_cycle = first cycle where Capacity_Ah ≤ EOL_THRESHOLD,
                or max CycleIndex + 1 if threshold never reached.
    """
    df = df.copy()
    result = []
    for bat, grp in df.groupby('Battery'):
        g = grp.sort_values('CycleIndex').copy()
        below = g[g['Capacity_Ah'] <= EOL_THRESHOLD]
        eol   = int(below['CycleIndex'].min()) if len(below) else int(g['CycleIndex'].max()) + 1
        g['RUL']      = (eol - g['CycleIndex']).clip(lower=0)
        g['EOL_cycle'] = eol
        result.append(g)
    return pd.concat(result, ignore_index=True)


def train_rf(X_train: np.ndarray, y_train: np.ndarray) -> RandomForestRegressor:
    """Train a Random Forest regressor."""
    model = RandomForestRegressor(
        n_estimators=RF_N_ESTIMATORS,
        random_state=RF_RANDOM_STATE,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    return model


def evaluate_rf(model, X_test, y_test):
    """Return predictions, RMSE, and R²."""
    y_pred = model.predict(X_test)
    rmse   = float(np.sqrt(mean_squared_error(y_test, y_pred)))
    r2     = float(r2_score(y_test, y_pred))
    return y_pred, rmse, r2


def run_rul_pipeline(df: pd.DataFrame) -> dict:
    """
    Full LOBO RUL pipeline.

    1. Compute RUL labels
    2. Split: train = TRAIN_BATTERIES, test = TEST_BATTERY
    3. Scale features with StandardScaler
    4. Train Random Forest
    5. Evaluate and save results

    Returns
    -------
    dict with keys: RMSE, R2, feature_importance, y_test, y_pred
    """
    print(f"\n[RUL] Computing RUL labels (EOL threshold: {EOL_THRESHOLD} Ah)...")
    df_rul = compute_rul(df)

    # Report EOL per cell
    for bat, grp in df_rul.groupby('Battery'):
        eol = grp['EOL_cycle'].iloc[0]
        print(f"  {bat}: EOL = {eol if eol <= grp['CycleIndex'].max() else 'N/A (>' + str(grp['CycleIndex'].max()) + ')'}")

    # ── Split ──────────────────────────────────────────────────────────────
    clean  = df_rul.dropna(subset=FEATURE_COLS + ['RUL'])
    train  = clean[clean['Battery'].isin(TRAIN_BATTERIES)]
    test   = clean[clean['Battery'] == TEST_BATTERY].sort_values('CycleIndex')

    X_train = train[FEATURE_COLS].values
    y_train = train['RUL'].values
    X_test  = test[FEATURE_COLS].values
    y_test  = test['RUL'].values

    print(f"\n[RUL] Training samples: {len(X_train)}  |  Test samples: {len(X_test)}")

    # ── Scale ──────────────────────────────────────────────────────────────
    scaler    = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    # ── Train ──────────────────────────────────────────────────────────────
    print("[RUL] Training Random Forest regressor...")
    model = train_rf(X_train_s, y_train)

    # ── Evaluate ───────────────────────────────────────────────────────────
    y_pred, rmse, r2 = evaluate_rf(model, X_test_s, y_test)
    print(f"\n[RUL] Results on {TEST_BATTERY}:")
    print(f"  RMSE = {rmse:.2f} cycles")
    print(f"  R²   = {r2:.4f}")

    # ── Feature importance ─────────────────────────────────────────────────
    fi = pd.Series(model.feature_importances_, index=FEATURE_COLS).sort_values(ascending=False)
    print("\n[RUL] Feature importance:")
    for feat, val in fi.items():
        print(f"  {feat:<15}: {val:.4f}")

    fi_df = fi.reset_index()
    fi_df.columns = ['Feature', 'Importance']
    os.makedirs(TABLES_DIR, exist_ok=True)
    fi_df.to_csv(os.path.join(TABLES_DIR, 'feature_importance.csv'), index=False)

    # ── Save model ─────────────────────────────────────────────────────────
    joblib.dump({'model': model, 'scaler': scaler}, MODEL_PKL)
    print(f"[RUL] Model saved → {MODEL_PKL}")

    # ── Save metrics ───────────────────────────────────────────────────────
    metrics = {
        'RMSE_cycles'          : round(rmse, 4),
        'R2'                   : round(r2, 4),
        'test_battery'         : TEST_BATTERY,
        'train_batteries'      : TRAIN_BATTERIES,
        'feature_importance'   : fi.round(4).to_dict(),
        'n_estimators'         : RF_N_ESTIMATORS,
    }
    os.makedirs(os.path.dirname(METRICS_JSON), exist_ok=True)
    with open(METRICS_JSON, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"[RUL] Metrics saved → {METRICS_JSON}")

    # ── Plot Figure 6 ──────────────────────────────────────────────────────
    _plot_rul(test['CycleIndex'].values, y_test, y_pred, rmse, r2, fi)

    return {**metrics, 'y_test': y_test, 'y_pred': y_pred}


def _plot_rul(cycles, y_test, y_pred, rmse, r2, fi):
    """Generate Fig 6: RUL prediction + feature importance."""
    plt.rcParams.update({'font.family': 'DejaVu Serif', 'font.size': 12,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'savefig.dpi': 200, 'savefig.bbox': 'tight'})

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Left: actual vs predicted RUL
    ax = axes[0]
    order = np.argsort(cycles)
    ax.plot(cycles[order], y_test[order],  color='#2166AC', lw=2, label='Actual RUL')
    ax.plot(cycles[order], y_pred[order],  color='#D6604D', lw=2, ls='--',
            label=f'Predicted RUL')
    ax.fill_between(cycles[order],
                    y_test[order] - rmse, y_test[order] + rmse,
                    alpha=0.15, color='#2166AC', label=f'±RMSE ({rmse:.1f} cyc)')
    ax.set_xlabel('Cycle Index')
    ax.set_ylabel('Remaining Useful Life (cycles)')
    ax.set_title(f'{TEST_BATTERY} — RMSE = {rmse:.2f}  R² = {r2:.3f}')
    ax.legend(fontsize=10)

    # Right: feature importance
    ax2 = axes[1]
    colors = ['#2166AC' if i == 0 else '#4A90D9' for i in range(len(fi))]
    bars = ax2.barh(fi.index, fi.values, color=colors, edgecolor='white')
    ax2.set_xlabel('Importance Score')
    ax2.set_title('Random Forest Feature Importance')
    ax2.invert_yaxis()
    for bar, val in zip(bars, fi.values):
        ax2.text(val + 0.002, bar.get_y() + bar.get_height() / 2,
                 f'{val:.3f}', va='center', fontsize=10)

    fig.suptitle(f'Fig. 6  Hybrid PIAI RUL Prediction — Leave-One-Out ({TEST_BATTERY})',
                 fontsize=13)
    fig.tight_layout()
    os.makedirs(FIGURES_DIR, exist_ok=True)
    fig.savefig(os.path.join(FIGURES_DIR, 'fig6_RUL.png'))
    plt.close()
    print(f"[RUL] Fig 6 saved → {FIGURES_DIR}/fig6_RUL.png")
