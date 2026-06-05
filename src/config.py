import os
import numpy as np

# --- Paths Configuration ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
FIGURES_DIR = os.path.join(RESULTS_DIR, "figures")
TABLES_DIR = os.path.join(RESULTS_DIR, "tables")
MODELS_DIR = os.path.join(BASE_DIR, "models")

COMBINED_PARAMS_CSV = os.path.join(PROCESSED_DATA_DIR, "all_batteries_params_combined.csv")
COMBINED_CLEANED_CSV = os.path.join(TABLES_DIR, "all_batteries_params_combined_cleaned.csv")
REGRESSION_RESULTS_CSV = os.path.join(TABLES_DIR, "regression_results.csv")
STAT_TESTS_CSV = os.path.join(TABLES_DIR, "stat_tests_summary.csv")
METRICS_PATH = os.path.join(RESULTS_DIR, "metrics.json")
WORD_DOC_PATH = os.path.join(RESULTS_DIR, "IV_Results_and_Discussion_ECM_LiIon_IEEE.docx")
MODEL_PATH = os.path.join(MODELS_DIR, "random_forest_rul.pkl")

# --- Battery Datasets Map ---
BATTERY_KEYS = ["B0005", "B0006", "B0007", "B0018"]
BATTERY_FILES = {
    key: os.path.join(RAW_DATA_DIR, f"{key}.mat") for key in BATTERY_KEYS
}

# --- EOL and Model Constants ---
EOL_THRESHOLD = 1.40  # End-of-Life capacity threshold (Ah)
TEST_BATTERY = "B0018"  # Battery to evaluate on (Leave-One-Battery-Out validation)
RANDOM_STATE = 42

# --- Optimization Settings (2-RC ECM) ---
# Parameters format: [R0, R1, C1, R2, C2, Voc_slope, Voc_intercept]
LB = np.array([1e-4, 1e-4, 1e-1, 1e-4, 1e-1, -0.5, 3.0])
UB = np.array([0.5,  5.0,  1e4,  5.0,  1e4,  0.5,  4.2])
X0 = (LB + UB) / 2.0

# Sampling configuration to avoid slow runtime (set to 1 to run on all cycles)
SAMPLING_INTERVAL = 20
LEAST_SQUARES_MAX_NFEV = 500
