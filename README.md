# ⚡ Cycle-Resolved EIS Feature Extraction and Physics-Informed Machine Learning for Lithium-Ion Battery Health and Life Prediction

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0001--0268--7163-brightgreen)](https://orcid.org/0009-0001-0268-7163)
[![ResearchGate](https://img.shields.io/badge/ResearchGate-Samer--Yaghi-00CCBB)](https://www.researchgate.net/profile/Samer-Yaghi-2)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20556874.svg)](https://doi.org/10.5281/zenodo.20556874)
[![GitHub Stars](https://img.shields.io/github/stars/sameredu/Battery-PIAI-ECM?style=social)](https://github.com/sameredu/Battery-PIAI-ECM)

**Authors:** Samer Yaghi¹ · Mohammed Alhanjouri²

¹ University College of Applied Sciences (UCAS), Gaza, Palestine — syaghi@ucas.edu.ps  
² Islamic University of Gaza (IUG), Gaza, Palestine — mhanjouri@iugaza.edu.ps

---

## 📌 Overview

This repository contains the full implementation of a **Physics-Informed AI (PIAI)** framework for lithium-ion battery degradation analysis and Remaining Useful Life (RUL) prediction. The framework extracts impedance features — electrolyte resistance **Re** and charge-transfer resistance **Rct** — directly from Electrochemical Impedance Spectroscopy (EIS) measurements on the NASA battery dataset, applies rigorous statistical cross-cell validation, and feeds physics-grounded features into a Random Forest regressor for interpretable RUL estimation.

> **Key contribution:** Unlike purely data-driven approaches, our pipeline couples EIS-derived physical features with formal ANOVA and Kruskal-Wallis significance testing across four cells, producing a transparent and generalisable prognostic model.

---

## 📊 Key Results

| Metric | Value |
|--------|-------|
| Re–Rct coupling R² | **0.937** (p < .001) |
| Capacity fade R² per cell | **0.940–0.977** |
| ANOVA F (Re) | **287.85** (p < .001) |
| ANOVA F (Rct) | **176.91** (p < .001) |
| RUL RMSE (test: B0018) | **11.42 cycles** |
| RUL R² (test: B0018) | **0.873** |
| Top feature (importance) | Capacity\_Ah = 0.791 |

### EOL Cycles (threshold: 1.40 Ah)

| Cell | Discharge Cycles | Initial Cap. (Ah) | Final Cap. (Ah) | EOL Cycle |
|------|-----------------|-------------------|-----------------|-----------|
| B0005 | 168 | 1.857 | 1.325 | 125 |
| B0006 | 168 | 2.035 | 1.186 | 109 |
| B0007 | 168 | 1.891 | 1.433 | N/A |
| B0018 | 132 | 1.855 | 1.341 | 97 |

---

## 📂 Repository Structure

```
Battery-PIAI-ECM/
│
├── README.md
├── LICENSE
├── requirements.txt
├── citation.bib
├── .zenodo.json
│
├── notebooks/
│   ├── 01_data_loading.ipynb          # MAT file parsing and cycle extraction
│   ├── 02_eis_feature_extraction.ipynb # Re, Rct extraction from EIS sweeps
│   ├── 03_statistical_analysis.ipynb   # ANOVA, Kruskal-Wallis, regression
│   └── 04_rul_prediction.ipynb         # Random Forest LOBO evaluation
│
├── src/
│   ├── config.py                  # Global constants and file paths
│   ├── data_loader.py             # MAT file loader and discharge cycle parser
│   ├── eis_features.py            # Re, Rct extraction from EIS impedance data
│   ├── capacity_tracking.py       # Coulomb counting for cycle capacity
│   ├── statistics.py              # ANOVA, Kruskal-Wallis, linear regression
│   ├── rul_model.py               # Random Forest + LOBO cross-validation
│   └── pipeline.py                # End-to-end execution pipeline
│
├── results/
│   ├── figures/                   # Generated plots (Figs 2–6)
│   └── tables/                    # Statistical tables (ANOVA, regression, RUL)
```

---

## 🧠 Methodology

### 1. EIS Feature Extraction
Re (electrolyte resistance) and Rct (charge-transfer resistance) are read directly from EIS sweeps performed between discharge cycles. No circuit fitting is applied — values come from the `Re` and `Rct` fields in the NASA MAT files.

### 2. Capacity Tracking
Cycle-by-cycle discharge capacity is tracked via Coulomb counting from constant-current (2 A) discharge profiles.

### 3. Statistical Validation
ANOVA and Kruskal-Wallis tests are applied across all four cells to verify that inter-cell differences in Re, Rct, and capacity are statistically significant (all p < .001).

### 4. Re–Rct Coupling Analysis
Linear regression between Re and Rct yields R² = 0.937 across 636 cycles, confirming their joint utility as compact SOH indicators consistent with SEI layer growth and active-material loss mechanisms.

### 5. RUL Prediction
A Random Forest regressor [Breiman 2001] is trained using a **Leave-One-Battery-Out (LOBO)** strategy:
- **Train:** B0005, B0006, B0007
- **Test:** B0018
- **Features:** Re, Rct, Capacity\_Ah, CycleIndex, V\_mean, T\_mean, Duration\_s
- **Result:** RMSE = 11.42 cycles, R² = 0.873

---

## 🚀 How to Run

### 1. Install requirements

```bash
pip install -r requirements.txt
```

### 2. Download NASA battery data

Place `B0005.mat`, `B0006.mat`, `B0007.mat`, `B0018.mat` in a `data/` folder.  
Dataset available at: [NASA Prognostics Center of Excellence](https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/pcoe/pcoe-data-set-repository/)

### 3. Run the full pipeline

```bash
python src/pipeline.py
```

### 4. Explore step-by-step notebooks

Open the `notebooks/` folder in Jupyter Lab or Google Colab for interactive analysis.

---

## 📦 Dataset

**NASA Prognostics Center of Excellence Battery Dataset**

- **Cells:** B0005, B0006, B0007, B0018 (18650 Li-ion, rated 2 Ah)
- **Total discharge cycles:** 636
- **Discharge protocol:** Constant current at 2 A to cut-off voltages (2.7 V / 2.5 V / 2.2 V / 2.5 V)
- **EIS sweeps:** 0.1 Hz – 5 kHz between cycles
- **EOL criterion:** Capacity fade to 1.40 Ah (30% loss from rated 2 Ah)
- **Citation:** Saha & Goebel (2007), NASA Ames Prognostics Data Repository

---

## 📜 Citation

If you use this code or results in your work, please cite:

### BibTeX (paper — under review)

```bibtex
@article{yaghi2026piai,
  author   = {Samer Yaghi and Mohammed Alhanjouri},
  title    = {Cycle-Resolved EIS Feature Extraction and Physics-Informed Machine
              Learning for Lithium-Ion Battery Health and Life Prediction},
  year     = {2026},
  journal  = {Ionics (Under Review)},
  keywords = {lithium-ion battery, EIS, physics-informed AI, RUL, NASA dataset,
              ANOVA, Random Forest}
}
```

### BibTeX (software — this repository)

```bibtex
@software{yaghi2026battery_piai,
  author    = {Yaghi, Samer and Alhanjouri, Mohammed},
  title     = {Cycle-Resolved EIS Feature Extraction and Physics-Informed Machine
               Learning for Lithium-Ion Battery Health and Life Prediction},
  year      = {2026},
  version   = {2.0.0},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.20556874},
  url       = {https://github.com/sameredu/Battery-PIAI-ECM}
}
```

---

## 🔗 Related Links

- 📄 ResearchGate: [researchgate.net/profile/Samer-Yaghi-2](https://www.researchgate.net/profile/Samer-Yaghi-2)
- 🔬 ORCID: [orcid.org/0009-0001-0268-7163](https://orcid.org/0009-0001-0268-7163)
- 🏛️ UCAS: [ucas.edu.ps](https://www.ucas.edu.ps)
- 🏛️ IUG: [iugaza.edu.ps](https://www.iugaza.edu.ps)
- 📦 Zenodo Archive: [doi.org/10.5281/zenodo.20556874](https://doi.org/10.5281/zenodo.20556874)

---

## License

Released under the [MIT License](LICENSE).

---

*Faculty of Information Technology · University College of Applied Sciences (UCAS) · Islamic University of Gaza (IUG) · Palestine · © 2026*
