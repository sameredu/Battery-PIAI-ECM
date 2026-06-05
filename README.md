[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0001--0268--7163-brightgreen)](https://orcid.org/0009-0001-0268-7163)
[![ResearchGate](https://img.shields.io/badge/ResearchGate-Samer--Yaghi-00CCBB)](https://www.researchgate.net/profile/Samer-Yaghi-2)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20556874.svg)](https://doi.org/10.5281/zenodo.20556874)
[![GitHub Stars](https://img.shields.io/github/stars/sameredu/Battery-PIAI-ECM?style=social)](https://github.com/sameredu/Battery-PIAI-ECM)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20556874.svg)](https://doi.org/10.5281/zenodo.20556874)

# ⚡ Cycle-Resolved Physics-Informed AI for Lithium-Ion Battery Degradation

This repository contains the implementation of a physics-informed experimental and machine learning framework for lithium-ion battery degradation analysis using equivalent circuit modeling (ECM) and NASA prognostics datasets.

## 📌 Key Idea

We extract cycle-resolved ECM parameters (R0, R1, C1, R2, C2) from NASA battery datasets and integrate them with statistical analysis and machine learning to build an interpretable Remaining Useful Life (RUL) prediction framework.

---

## 📂 Repository Structure

```
Battery-PIAI-ECM-Degradation/
│
├── README.md
├── LICENSE
├── requirements.txt
├── citation.bib
│
│
├── notebooks/
│   ├── 01_data_loading.ipynb
│   ├── 02_ecm_identification.ipynb
│   ├── 03_statistical_analysis.ipynb
│   └── 04_rul_prediction.ipynb
│
├── src/
│   ├── config.py             # Global constants and file paths
│   ├── data_loader.py        # Loading MAT files and discharge cycles
│   ├── ecm_model.py          # 2-RC circuit simulation equations
│   ├── parameter_estimation.py # Nonlinear least squares parameter optimizer
│   ├── feature_engineering.py  # Feature derivation (tau constants) and scaling
│   ├── statistics.py         # ANOVA, Kruskal-Wallis, linear regressions
│   ├── rul_model.py          # Random Forest training and LOBO evaluation
│   └── pipeline.py           # End-to-end execution pipeline
│
├── results/
│   ├── figures/              # Generated plots and visualizations
│   ├── tables/               # Statistical tables and regression logs

```

---

## 📊 Dataset

We utilize the **NASA Prognostics Center of Excellence Battery Dataset** for evaluation.
- Cells: B0005, B0006, B0007, B0018
- Data contains over 800 discharge cycles under constant current discharge at 2A.
- EOL defined at capacity drop to **1.4 Ah** (approx. 30% capacity loss).

---

## 🧠 Methodology

1. **Cycle-resolved ECM Parameter Extraction**: We model the cell with a 2-RC circuit:
   $$V_{sim} = V_{oc}(SOC) - I R_0 - V_1 - V_2$$
   Parameters $x = [R_0, R_1, C_1, R_2, C_2, a, b]$ are identified cycle-by-cycle using Nonlinear Least Squares Optimization.
2. **Statistical Validation**: We apply ANOVA and Kruskal-Wallis tests across cells to verify physical distinguishability, alongside correlation analysis.
3. **Physics-Informed Feature Selection**: Derivation of time constants $\tau_1 = R_1 \times C_1$ and $\tau_2 = R_2 \times C_2$.
4. **Random Forest RUL Prediction**: Model trained via Leave-One-Battery-Out (LOBO) validation strategy, evaluating generalized performance.

---

## 🚀 How to Run

1. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Execute the end-to-end pipeline**:
   ```bash
   python src/pipeline.py
   ```

3. **Explore Jupyter Notebooks**:
   Open notebooks inside the `notebooks/` folder to run step-by-step visualizations and analysis.

---

## 📈 Key Results

- Strong coupling between $R_0$ and $C_1$ (R² = 0.88).
- RUL prediction on test battery B0018: **RMSE = 20.42 cycles, R² = 0.662**.
- Consistent and clear degradation trends across all cells.

---

## 📜 Citation

If you use this code in your work, please cite it as:

### BibTeX
```bibtex
@article{yaghi2025ecm,
  author  = {Samer Yaghi and Mohammed Alhanjouri},
  title   = {Cycle-Resolved Physics-Based Analysis of Lithium-Ion Battery Degradation Using Equivalent Circuit Modeling},
  year    = {2026},
  journal = {Preprint (Under Review)},
  keywords = {Lithium-ion battery, ECM, Physics-Informed AI, RUL, NASA dataset}
}
```

## Citation

@software{yaghi2026ucasedml,
  author = {Yaghi, Samer and Alhanjouri, Mohammed},
  title = {Cycle-Resolved Physics-Informed AI for Lithium-Ion Battery Degradation Prediction},
  year = {2026},
  url = {[(https://github.com/sameredu/Battery-PIAI-ECM)](https://github.com/sameredu/Battery-PIAI-ECM)]}
}

---
## Related Links

- 📄 ResearchGate: [researchgate.net/profile/Samer-Yaghi-2](https://www.researchgate.net/profile/Samer-Yaghi-2)
- 🔬 ORCID: [orcid.org/0009-0001-0268-7163](https://orcid.org/0009-0001-0268-7163)
- 🏛️ UCAS: [ucas.edu.ps](https://www.ucas.edu.ps)
- 🏛️ IUG: [iugaza.edu.ps](https://www.iugaza.edu.ps)

---

## License

This code is released under the [MIT License](LICENSE).

---

*Faculty of Information Technology · University College of Applied Sciences (UCAS) · Islamic University of Gaza · Palestine · © 2026*





