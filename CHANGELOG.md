# Changelog

All notable changes to this repository are documented here.

---

## [v2.0.0] — 2026-06

### 🔄 Major Changes

#### Methodology — EIS-Direct vs ECM Fitting
- **Replaced** cycle-by-cycle 2RC ECM parameter fitting (R0, R1, C1, R2, C2) with **direct EIS feature extraction** (Re, Rct) from NASA MAT impedance fields
- Re and Rct are now read directly from `cycle.data.Re` and `cycle.data.Rct` fields — no nonlinear optimisation required
- This change eliminates optimizer boundary failures that affected ~40% of cycles in v1.0.0

#### Updated Results
| Metric | v1.0.0 | v2.0.0 |
|--------|--------|--------|
| Primary coupling | R0–C1, R² = 0.88 | Re–Rct, R² = **0.937** |
| RUL RMSE (B0018) | 20.42 cycles | **11.42 cycles** |
| RUL R² (B0018) | 0.662 | **0.873** |
| ANOVA F (primary) | F = 36.33 (R0) | F = **287.85** (Re) |
| Top feature | Capacity\_Ah = 0.907 | Capacity\_Ah = **0.791**, Rct = 0.128 |

#### Updated Paper Title
- **Old:** *Cycle-Resolved Physics-Based Analysis of Lithium-Ion Battery Degradation Using Equivalent Circuit Modeling*
- **New:** *From Impedance Spectroscopy to Prognosis: A Physics-Informed AI Approach to Lithium-Ion Battery Degradation and Remaining Useful Life*

#### Updated Figures
- Fig 2: Capacity fade with per-cell linear regression (R² = 0.940–0.977)
- Fig 3: Re trend across cycles (replacing R0 trend)
- Fig 4: Re–Rct coupling scatter + Pearson correlation matrix
- Fig 5: Radar degradation signatures (Re%, Rct%, capacity fade, EOL, R²)
- Fig 6: RUL prediction B0018 + feature importance bar chart

#### Updated Source Files
- `src/eis_features.py` — new module replacing `ecm_model.py` and `parameter_estimation.py`
- `src/capacity_tracking.py` — Coulomb counting from discharge profiles
- Notebooks renamed to reflect EIS-based workflow

### 📚 References
- Added 12 new references [29–40] from 2019–2023 literature
- All new references cited in-text at appropriate sections

---

## [v1.0.0] — 2026-06-05

- Initial release
- 2RC ECM parameter extraction via NLLS (scipy TRF)
- Random Forest RUL prediction (LOBO)
- ANOVA + Kruskal-Wallis statistical validation
- NASA B0005–B0018 dataset
