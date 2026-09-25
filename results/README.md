# Contents of `results/`

## Produced by v3.0.0 (`src/analysis.py`, `src/export_tables.py`, `src/figs.py`)

| File | What it holds |
|---|---|
| `metrics.json` | Headline numbers for this release |
| `tables/lobo_folds.csv` | All four leave-one-battery-out folds |
| `tables/ablation_baselines.csv` | Feature ablation, alternative learners, training-free baseline |
| `tables/b0007_eol_sensitivity.csv` | Results under three end-of-life labels for the censored cell |
| `tables/between_cell_summary.csv` | One-way tests, effect sizes, mixed-model slopes and ICC |
| `tables/autocorrelation_diagnostics.csv` | Durbin-Watson and lag-1 ACF per cell |
| `tables/pairwise_holm_cliffs.csv` | Holm-corrected pairwise tests with Cliff's delta |
| `tables/coupling_per_cell.csv` | Re-Rct coupling pooled, per cell, centred, de-duplicated, range-corrected |
| `figures/fig1…fig8` | Figures 1 to 8 of the manuscript |

## Input, unchanged since v2.0.0

`tables/battery_processed.csv` — extracted features. Every script here reads it.

## Carried over from v2.0.0, kept for provenance

| File | Why it is still here |
|---|---|
| `tables/stat_tests_summary.csv` | The file a reviewer compared against Table 1 of the submitted manuscript. Retained unchanged so that comparison stays reproducible. |
| `tables/feature_importance.csv` | Importances from the single B0018 fold. Superseded by the ablation. |
| `tables/regression_results.csv` | Per-cell regressions from v2.0.0. |

These three describe the v2.0.0 analysis. Where they disagree with the v3.0.0 outputs, the
v3.0.0 outputs are the ones reported in the manuscript. See `CHANGELOG.md`.
