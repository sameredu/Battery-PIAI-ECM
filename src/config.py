"""
config.py
---------
Global constants, file paths, and model settings for the Battery-PIAI-ECM v2.0.0 pipeline.
EIS-based approach: Re and Rct extracted directly from NASA MAT impedance fields.
"""

import os

# ── Directory structure ──────────────────────────────────────────────────────
BASE_DIR           = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR       = os.path.join(BASE_DIR, "data", "raw")
RESULTS_DIR        = os.path.join(BASE_DIR, "results")
FIGURES_DIR        = os.path.join(RESULTS_DIR, "figures")
TABLES_DIR         = os.path.join(RESULTS_DIR, "tables")

# ── Output file paths ────────────────────────────────────────────────────────
PROCESSED_CSV      = os.path.join(TABLES_DIR, "battery_processed.csv")
STAT_TESTS_CSV     = os.path.join(TABLES_DIR, "stat_tests_summary.csv")
REGRESSION_CSV     = os.path.join(TABLES_DIR, "regression_results.csv")
FEATURE_IMP_CSV    = os.path.join(TABLES_DIR, "feature_importance.csv")
METRICS_JSON       = os.path.join(RESULTS_DIR, "metrics.json")
MODEL_PKL          = os.path.join(RESULTS_DIR, "rf_rul_model.pkl")

# ── Battery dataset ──────────────────────────────────────────────────────────
BATTERY_KEYS = ["B0005", "B0006", "B0007", "B0018"]
BATTERY_FILES = {
    key: os.path.join(RAW_DATA_DIR, f"{key}.mat") for key in BATTERY_KEYS
}

# ── Experiment constants ─────────────────────────────────────────────────────
EOL_THRESHOLD   = 1.40   # End-of-Life capacity threshold (Ah) — 30% fade from 2 Ah rated
DISCHARGE_CURRENT = 2.0  # Constant discharge current (A)
TEST_BATTERY    = "B0018"
TRAIN_BATTERIES = ["B0005", "B0006", "B0007"]
RANDOM_STATE    = 42

# ── EIS validity bounds ──────────────────────────────────────────────────────
RE_MIN_OHM  = 0.010   # Minimum plausible Re  (10 mΩ)
RE_MAX_OHM  = 0.200   # Maximum plausible Re  (200 mΩ)
RCT_MIN_OHM = 0.010   # Minimum plausible Rct (10 mΩ)
RCT_MAX_OHM = 0.300   # Maximum plausible Rct (300 mΩ)

# ── Random Forest settings ───────────────────────────────────────────────────
RF_N_ESTIMATORS = 200
RF_RANDOM_STATE = RANDOM_STATE

# ── Feature columns used for RUL prediction ──────────────────────────────────
FEATURE_COLS = ["Re", "Rct", "Capacity_Ah", "CycleIndex",
                "V_mean", "T_mean", "Duration_s"]
