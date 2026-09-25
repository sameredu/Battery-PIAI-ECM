# Changelog

## v3.0.1 — reproducibility fixes

- **Scripts now run from a clone.** `src/analysis.py`, `src/export_tables.py` and `src/figs.py`
  contained absolute paths from the authoring machine and could not be executed by anyone else.
  All paths are now resolved relative to the repository root.
- **One figure script.** `src/figs2.py` is merged into `src/figs.py`, which now produces exactly
  Figures 1 to 8 under the numbering used in the manuscript. The previous pair wrote four
  additional files under superseded names.
- **`results/metrics.json` updated.** It still carried the v2.0.0 headline values
  (RMSE = 11.42, R² = 0.873 from the B0018 fold alone). It now carries the four-fold results,
  the ablation and the between-cell statistics, with a note recording what the earlier figures were.
- **Superseded files labelled.** `src/pipeline.py`, `src/rul_model.py` and notebooks 03 and 04
  implement the v2.0.0 single-fold analysis. They are retained so v2.0.0 stays reproducible and
  now carry a header saying so. `results/README.md` states which outputs belong to which release.

No numerical result changes in this release. Rerunning the corrected scripts from a clean clone
reproduces every value in the manuscript.


## v3.0.0 — revised analyses for the Discover Electrochemistry major revision

This release accompanies the revised manuscript. It corrects two reporting errors
carried over from earlier versions, discloses a data-preparation step that was not
previously described, and adds the analyses requested by the reviewers.

### Corrected

- **Table 1 capacity row.** The manuscript reported ANOVA F = 10.39 and Kruskal H = 36.72
  for capacity. Those values originate in **v1.0.0**, which obtained capacity by integrating
  the measured discharge current. From v2.0.0 onward capacity is read from the `Capacity`
  field recorded with each discharge cycle, which gives F = 8.34 and H = 30.66. The two
  series differ (B0005 cycle 1: 1.861952 Ah under integration against 1.856487 Ah from the
  recorded field). The manuscript row was not updated when the pipeline changed; the
  `Re` and `Rct` rows were, which is why the discrepancy was confined to one row.

- **Sample sizes.** Impedance statistics are computed over **579** cycles (149 each for
  B0005, B0006 and B0007; 132 for B0018), not the 636 discharge cycles stated previously.
  636 remains correct for capacity.

- **B0007 minimum capacity.** Previously reported as 1.433 Ah. That is the *final*
  capacity. The minimum is **1.4005 Ah at discharge cycle 166**, 0.46 mAh above the
  1.40 Ah threshold, with three cycles at or below 1.41 Ah.

- **Re range.** Previously reported as 43.6–79.1 mΩ. The pooled range is **35.9–79.1 mΩ**.

### Disclosed

- **Impedance-to-cycle mapping.** Impedance sweeps are not recorded once per discharge
  cycle. The raw files contain 278 sweeps for each of B0005, B0006 and B0007 against 168
  discharge cycles, and **53 sweeps for B0018 against 132 discharge cycles**. Each cycle is
  assigned the nearest available sweep, so B0018 carries 132 rows built from only 49
  distinct values. Analyses affected by this are reported both on the full mapping and on
  the de-duplicated series (`results/tables/coupling_per_cell.csv`).

### Added

- Complete four-fold leave-one-battery-out evaluation (`lobo_folds.csv`). The previous
  release reported a single fold (test on B0018).
- Feature ablation and baseline comparison, including a training-free linear capacity
  extrapolation (`ablation_baselines.csv`).
- Sensitivity of all results to the end-of-life label assigned to the censored cell B0007
  (`b0007_eol_sensitivity.csv`).
- Linear mixed-effects models with random intercept per cell, effect sizes and confidence
  intervals (`between_cell_summary.csv`), replacing the one-way tests.
- Autocorrelation diagnostics justifying that replacement (`autocorrelation_diagnostics.csv`).
- Holm-corrected pairwise comparisons with Cliff's delta (`pairwise_holm_cliffs.csv`).
- Per-cell, within-cell-centred and cycle-partialled coupling analysis (`coupling_per_cell.csv`).
- Figures regenerated without embedded titles; new Figure 5 (per-cell coupling) and
  Figure 6 (folds and ablation); Figure 1 redrawn as a vector schematic.

### Authorship

The README and Zenodo record for v1.0.0 and v2.0.0 listed two authors. This release lists all
three authors of the manuscript: Samer Yaghi, Mohammed A. Awadallah and Mohammed Alhanjouri.

### Removed from the manuscript's claims

- The description of the method as "physics-informed AI".
- The claim that between-cell variance is 288 times within-cell variance. F is a ratio of
  mean squares; the intraclass correlation is 0.899 for Re, implying a ratio near 9.
- The claim that the pooled Re–Rct R² of 0.937 demonstrates a single physical process
  holding across four cells. Per-cell R² ranges from 0.146 to 0.966.
- The claim that held-out performance was possible only through physical anchoring. The
  ablation shows a model using Re and Rct alone reaches mean R² = −0.020.

## v2.0.1
Metadata alignment only (README, Zenodo record, citation). The title used in this tag was
written for a submission to *Ionics*. That submission is closed. The work is now under review
at *Discover Electrochemistry* under the title carried by v3.0.0.

## v2.0.0
EIS-direct feature extraction replacing equivalent-circuit fitting.

## v1.0.0
Equivalent-circuit parameter identification by nonlinear least squares; capacity by
current integration. Superseded.
