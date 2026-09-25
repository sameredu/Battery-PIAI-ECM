# Cross Cell Evaluation of Electrochemical Impedance Features for Lithium Ion Battery Remaining Useful Life Prediction

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0001--0268--7163-brightgreen)](https://orcid.org/0009-0001-0268-7163)

**Authors:** Samer Yaghi¹ · Mohammed A. Awadallah² · Mohammed Alhanjouri³

¹ University College of Applied Sciences (UCAS), Gaza, Palestine — syaghi@ucas.edu.ps
² Al-Aqsa University, Gaza, Palestine
³ Islamic University of Gaza (IUG), Gaza, Palestine — mhanjouri@iugaza.edu.ps

---

## Overview

This repository evaluates whether electrochemical impedance features transfer across
lithium-ion cells. Electrolyte resistance `Re` and charge-transfer resistance `Rct` are read
directly from the recorded impedance fields of the NASA Prognostics Center of Excellence
dataset, with no circuit fitting. Two questions are kept separate:

1. **Discrimination** — do impedance features separate nominally identical cells more
   sharply than capacity does?
2. **Transfer** — do those features predict remaining useful life on a cell the model has
   never seen?

The answer to the first is yes and to the second is no, and this release contains the
analyses that establish both.

> **Note on v1 and v2.** Earlier releases described this work as "Physics-Informed AI". The
> model contains no physical constraints, loss terms or governing equations, so that label
> has been dropped. Earlier releases also validated on a single held-out cell. See
> `CHANGELOG.md` for every correction made in this release.

---

## Key results

### Between-cell variation

| Parameter | n | η² | ε² | ICC | Battery-level CV |
|---|---|---|---|---|---|
| Re | 579 | 0.600 | 0.634 | 0.899 | 13.6 % |
| Rct | 579 | 0.480 | 0.455 | 0.854 | 9.6 % |
| Capacity | 636 | 0.038 | 0.044 | 0.646 | 2.8 % |

Cycle-level measurements within a cell are strongly autocorrelated (lag-1 ACF +0.65 to
+0.90; Durbin–Watson 0.19 to 0.69), so one-way ANOVA and Kruskal–Wallis do not provide
valid inference here. Linear mixed-effects models with a random intercept per cell are used
instead. See `results/tables/autocorrelation_diagnostics.csv`.

### Cross-cell RUL prediction — complete four-fold leave-one-battery-out

| Held-out cell | RMSE (cycles) | MAE | R² |
|---|---|---|---|
| B0005 | 27.41 | 21.39 | 0.390 |
| B0006 | 5.13 | 3.06 | 0.970 |
| B0007 | 32.24 | 29.75 | 0.438 |
| B0018 | 11.42 | 9.02 | 0.873 |
| **Mean** | **19.05** | **15.80** | **0.668** |

v2.0.0 reported only the B0018 fold, which is the second most favourable of the four.

### What the impedance features contribute

| Feature set | Mean RMSE | Mean R² |
|---|---|---|
| Full feature set | 19.05 | 0.668 |
| Capacity + cycle index | 19.66 | 0.642 |
| Capacity only | 20.46 | 0.630 |
| Linear capacity extrapolation (no training at all) | 22.19 | 0.467 |
| No capacity | 25.18 | 0.461 |
| Re and Rct only | 33.20 | −0.020 |

End of life is defined by a capacity threshold, so a model predicting cycles to that
threshold is largely predicting the capacity trajectory. The impedance features add 0.61
cycles over capacity plus cycle index, which is far smaller than the spread across folds.

### Re–Rct coupling

Pooled R² = 0.937 (n = 579). Per cell: 0.894, 0.966, 0.959 and 0.146 for B0005, B0006,
B0007 and B0018, with slopes 1.14, 1.53, 1.10 and 0.53. Centring within cells leaves
R² = 0.900, so the coupling is genuine and not purely an aggregation artefact. Partialling
out cycle index reduces the correlation to +0.783, +0.750, +0.655 and +0.242.

B0018 spans only 7.0 mΩ of Re against 19.5 to 31.4 mΩ for the other cells. Correcting for
that range restriction raises its coefficient from r = 0.381 to r = 0.904, so B0018 appears
to differ mainly in how little it aged rather than in mechanism. See
`results/tables/coupling_per_cell.csv`.

---

## Data caveats

**Impedance sampling is uneven.** Sweeps are not recorded once per discharge cycle:

| Cell | Discharge cycles | Impedance sweeps | Cycles carrying impedance | Distinct values |
|---|---|---|---|---|
| B0005 | 168 | 278 | 149 | 141 |
| B0006 | 168 | 278 | 149 | 141 |
| B0007 | 168 | 278 | 149 | 141 |
| B0018 | 132 | **53** | 132 | **49** |

Each discharge cycle is assigned the values of the nearest available sweep. For B0018 this
means 132 rows built from 49 distinct measurements. Analyses sensitive to this are reported
both on the full mapping and on the de-duplicated series.

**B0007 is right-censored.** It never crosses the 1.40 Ah threshold; its minimum is
1.4005 Ah at discharge cycle 166, 0.46 mAh above it, before recovering to 1.4325 Ah.
Results under three end-of-life labels are in `results/tables/b0007_eol_sensitivity.csv`:

| Assumed EOL for B0007 | Mean RMSE | Mean R² |
|---|---|---|
| 166 (cycle of minimum capacity) | 17.53 | 0.723 |
| 169 (last observed + 1, used throughout) | 19.05 | 0.668 |
| 178 (linear extrapolation) | 23.95 | 0.464 |

---

## Repository structure

```
Battery-PIAI-ECM/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── requirements.txt
├── citation.bib
├── .zenodo.json
│
├── src/
│   ├── analysis.py          # v3: four LOBO folds, ablation, baselines, B0007 sensitivity
│   ├── export_tables.py     # v3: mixed-effects models, effect sizes, pairwise, coupling
│   ├── figs.py              # v3: Figures 1-8
│   │
│   ├── config.py            # v2: thresholds and validity bounds
│   ├── data_loader.py       # v2: MAT parsing, cycle extraction
│   ├── eis_features.py      # v2: Re and Rct extraction
│   ├── statistics.py        # v2: one-way tests and regressions
│   ├── visualisation.py     # v2: earlier figure code
│   ├── pipeline.py          # v2, superseded: end-to-end single-fold run
│   ├── rul_model.py         # v2, superseded: single held-out cell
│   └── __init__.py
│
├── notebooks/               # v2 walkthrough; 03 and 04 superseded, see their header note
│   ├── 01_data_loading.ipynb
│   ├── 02_eis_feature_extraction.ipynb
│   ├── 03_statistical_analysis.ipynb
│   └── 04_rul_prediction.ipynb
│
└── results/
    ├── README.md            # which outputs belong to which release
    ├── metrics.json         # v3 headline numbers
    ├── tables/
    │   ├── battery_processed.csv          # input, unchanged since v2.0.0
    │   ├── between_cell_summary.csv       # v3
    │   ├── autocorrelation_diagnostics.csv# v3
    │   ├── pairwise_holm_cliffs.csv       # v3
    │   ├── coupling_per_cell.csv          # v3
    │   ├── lobo_folds.csv                 # v3
    │   ├── ablation_baselines.csv         # v3
    │   ├── b0007_eol_sensitivity.csv      # v3
    │   ├── stat_tests_summary.csv         # v2, kept for provenance
    │   ├── feature_importance.csv         # v2, kept for provenance
    │   └── regression_results.csv         # v2, kept for provenance
    └── figures/
        └── fig1_pipeline.png … fig8_ablation.png
```

Files marked v2 describe the earlier analysis and are retained so that release stays
reproducible. Where they disagree with the v3 outputs, the v3 outputs are the ones reported
in the manuscript. See `results/README.md`.

## Reproducing

```bash
pip install -r requirements.txt
python src/analysis.py        # folds, ablation, sensitivity
python src/export_tables.py   # statistical tables
python src/figs.py            # Figures 1-8
```

All paths are resolved relative to the repository root, so the scripts run from a clone with
no editing. The input is `results/tables/battery_processed.csv`, itself derived from the NASA
`.mat` files by `src/data_loader.py` and `src/eis_features.py`.

## Citation

See `citation.bib`. Please cite the release you used; results differ between v1, v2 and v3
as recorded in `CHANGELOG.md`.

## License

MIT — see `LICENSE`.
