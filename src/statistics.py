"""
statistics.py
-------------
Statistical characterisation of EIS and capacity features across NASA cells.
Implements:
  - One-way ANOVA and Kruskal-Wallis tests (inter-cell significance)
  - Per-cell linear regression (degradation trend fitting)
  - Pearson correlation matrix
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import f_oneway, kruskal

from src.config import BATTERY_KEYS, STAT_TESTS_CSV, REGRESSION_CSV, TABLES_DIR
import os


def run_anova_kruskal(df: pd.DataFrame,
                      features: list = None) -> pd.DataFrame:
    """
    Run one-way ANOVA and Kruskal-Wallis tests for each feature across cells.

    Parameters
    ----------
    df       : DataFrame with 'Battery' column and feature columns
    features : list of column names to test (default: Re, Rct, Capacity_Ah)

    Returns
    -------
    pd.DataFrame with columns: Parameter, ANOVA_F, ANOVA_p, Kruskal_H, Kruskal_p
    """
    if features is None:
        features = ['Re', 'Rct', 'Capacity_Ah']

    rows = []
    for feat in features:
        groups = [
            df[df['Battery'] == b][feat].dropna().values
            for b in BATTERY_KEYS
        ]
        groups = [g for g in groups if len(g) > 0]
        if len(groups) < 2:
            continue

        F, p_anova  = f_oneway(*groups)
        H, p_kruskal = kruskal(*groups)

        rows.append({
            'Parameter' : feat,
            'ANOVA_F'   : round(F, 2),
            'ANOVA_p'   : round(p_anova, 8),
            'Kruskal_H' : round(H, 2),
            'Kruskal_p' : round(p_kruskal, 8),
            'Significant': 'Yes' if p_anova < 0.001 else 'No',
        })

    result = pd.DataFrame(rows)
    os.makedirs(TABLES_DIR, exist_ok=True)
    result.to_csv(STAT_TESTS_CSV, index=False)
    print(f"  ANOVA/KW results saved → {STAT_TESTS_CSV}")
    return result


def run_regression(df: pd.DataFrame,
                   features: list = None) -> pd.DataFrame:
    """
    Fit linear regression of each feature on CycleIndex per cell.

    Returns
    -------
    pd.DataFrame with columns:
        Parameter, Battery, slope, intercept, R2, pval, n
    """
    if features is None:
        features = ['Re', 'Rct', 'Capacity_Ah']

    rows = []
    for feat in features:
        for bat in BATTERY_KEYS:
            g = (df[df['Battery'] == bat]
                 .dropna(subset=[feat, 'CycleIndex'])
                 .sort_values('CycleIndex'))
            if len(g) < 5:
                continue
            sl, ic, rv, pv, _ = stats.linregress(g['CycleIndex'], g[feat])
            rows.append({
                'Parameter' : feat,
                'Battery'   : bat,
                'slope'     : round(sl, 8),
                'intercept' : round(ic, 6),
                'R2'        : round(rv**2, 4),
                'pval'      : round(pv, 8),
                'n'         : len(g),
            })

    result = pd.DataFrame(rows)
    os.makedirs(TABLES_DIR, exist_ok=True)
    result.to_csv(REGRESSION_CSV, index=False)
    print(f"  Regression results saved → {REGRESSION_CSV}")
    return result


def correlation_matrix(df: pd.DataFrame,
                       features: list = None) -> pd.DataFrame:
    """
    Pearson correlation matrix for selected features.
    """
    if features is None:
        features = ['Re', 'Rct', 'Capacity_Ah', 'CycleIndex']
    valid = df[features].dropna()
    return valid.corr(method='pearson').round(4)


def run_statistical_pipeline(df: pd.DataFrame) -> tuple:
    """
    Run the full statistical pipeline:
    1. ANOVA + Kruskal-Wallis
    2. Per-cell regression
    3. Correlation matrix

    Returns
    -------
    (df_anova, df_regression, df_corr)
    """
    print("\n[STATS] Running ANOVA and Kruskal-Wallis tests...")
    df_anova = run_anova_kruskal(df)
    print(df_anova[['Parameter', 'ANOVA_F', 'ANOVA_p', 'Significant']].to_string(index=False))

    print("\n[STATS] Running per-cell linear regression...")
    df_reg = run_regression(df)
    cap_reg = df_reg[df_reg['Parameter'] == 'Capacity_Ah']
    print(cap_reg[['Battery', 'slope', 'R2']].to_string(index=False))

    print("\n[STATS] Pearson correlation matrix:")
    df_corr = correlation_matrix(df)
    print(df_corr)

    return df_anova, df_reg, df_corr
