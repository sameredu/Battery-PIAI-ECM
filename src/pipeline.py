"""
pipeline.py
-----------
End-to-end execution pipeline for Battery-PIAI-ECM v2.0.0.

Steps:
  1. Load NASA MAT files and extract discharge + EIS cycles
  2. Save processed DataFrame to CSV
  3. Run ANOVA, Kruskal-Wallis, and regression analysis
  4. Generate Figures 2–5
  5. Train Random Forest RUL model (LOBO) and generate Fig 6
  6. Print summary report

Usage:
    python src/pipeline.py
"""

import os
import pandas as pd

from src.config import PROCESSED_CSV, TABLES_DIR, FIGURES_DIR
from src.data_loader import load_all_batteries
from src.eis_features import eis_summary, re_rct_coupling, validate_eis
from src.statistics import run_statistical_pipeline
from src.visualisation import generate_all_figures
from src.rul_model import run_rul_pipeline


def run_pipeline():
    print("=" * 60)
    print("Battery-PIAI-ECM  v2.0.0  —  Full Pipeline")
    print("=" * 60)

    # ── Step 1: Load data ────────────────────────────────────────────────
    print("\n[1/5] Loading NASA battery data...")
    df = load_all_batteries()

    # Validate EIS bounds
    df = validate_eis(df)

    # Save processed data
    os.makedirs(TABLES_DIR, exist_ok=True)
    df.to_csv(PROCESSED_CSV, index=False)
    print(f"  Processed data saved → {PROCESSED_CSV}")

    # ── Step 2: EIS feature summary ──────────────────────────────────────
    print("\n[2/5] EIS feature summary...")
    summary = eis_summary(df)
    print(summary[['Battery', 'Re_initial_mΩ', 'Re_final_mΩ',
                    'Re_change_pct', 'Rct_initial_mΩ', 'Rct_final_mΩ']].to_string(index=False))

    coupling = re_rct_coupling(df)
    print(f"\n  Re–Rct coupling: slope={coupling['slope']}, "
          f"R²={coupling['R2']}, p={coupling['pval']:.2e}, n={coupling['n']}")

    # ── Step 3: Statistical analysis ─────────────────────────────────────
    print("\n[3/5] Statistical analysis...")
    df_anova, df_reg, df_corr = run_statistical_pipeline(df)

    # ── Step 4: Figures 2–5 ──────────────────────────────────────────────
    print("\n[4/5] Generating figures...")
    generate_all_figures(df)

    # ── Step 5: RUL prediction (Fig 6) ───────────────────────────────────
    print("\n[5/5] RUL prediction (Leave-One-Battery-Out)...")
    rul_results = run_rul_pipeline(df)

    # ── Summary ───────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"  Total cycles loaded    : {len(df)}")
    print(f"  Re–Rct coupling R²     : {coupling['R2']}")
    print(f"  ANOVA F (Re)           : {df_anova[df_anova['Parameter']=='Re']['ANOVA_F'].values[0]}")
    print(f"  ANOVA F (Rct)          : {df_anova[df_anova['Parameter']=='Rct']['ANOVA_F'].values[0]}")
    print(f"  RUL RMSE (B0018)       : {rul_results['RMSE_cycles']} cycles")
    print(f"  RUL R²   (B0018)       : {rul_results['R2']}")
    print(f"\n  Figures saved to  → {FIGURES_DIR}")
    print(f"  Tables  saved to  → {TABLES_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
