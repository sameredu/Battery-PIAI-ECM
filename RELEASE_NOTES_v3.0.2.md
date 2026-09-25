# Cross Cell Evaluation of Electrochemical Impedance Features for Lithium Ion Battery Remaining Useful Life Prediction

Release accompanying the revised manuscript submitted to *Discover Electrochemistry*.
**This is the release to cite.** Tags v3.0.0 and v3.0.1 are superseded: v3.0.1 predates the
restoration of the root README, the addition of the licence file, and the determinism fix.

## What this release contains

A complete re-analysis of the four NASA cells (B0005, B0006, B0007, B0018), replacing the
single-fold evaluation reported in v2.0.0.

### Two findings, in opposite directions

Impedance features **discriminate** strongly between nominally identical cells:

| Parameter | n | η² | ICC | Battery-level CV |
|---|---|---|---|---|
| Re | 579 | 0.600 | 0.899 | 13.6 % |
| Rct | 579 | 0.480 | 0.854 | 9.6 % |
| Capacity | 636 | 0.038 | 0.646 | 2.8 % |

The same features **do not transfer** to an unseen cell. Complete four-fold
leave-one-battery-out:

| Held-out cell | RMSE (cycles) | R² |
|---|---|---|
| B0005 | 27.41 | 0.390 |
| B0006 | 5.13 | 0.970 |
| B0007 | 32.24 | 0.438 |
| B0018 | 11.42 | 0.873 |
| **Mean** | **19.05** | **0.668** |

And the ablation shows the capacity trajectory carries the prediction:

| Feature set | Mean RMSE | Mean R² |
|---|---|---|
| Full feature set | 19.05 | 0.668 |
| Capacity only | 20.46 | 0.630 |
| Linear capacity extrapolation (no training at all) | 22.19 | 0.467 |
| Re and Rct only | 33.20 | −0.020 |

## Corrections to earlier releases

- The capacity row of Table 1 in the submitted manuscript (F = 10.39, H = 36.72) originated
  in **v1.0.0**, which computed capacity by integrating the discharge current. From v2.0.0
  capacity is read from the NASA `Capacity` field, giving **F = 8.34, H = 30.66**.
- Impedance statistics use **n = 579**, not the 636 discharge cycles stated previously.
- B0007's minimum capacity is **1.4005 Ah at cycle 166**, not the 1.433 Ah reported; that
  figure is its final capacity. The cell is right-censored and is now treated as such.
- The Re range is **35.9–79.1 mΩ**, not 43.6–79.1 mΩ.
- The "physics-informed AI" designation is dropped: the model embeds no physical constraints.
- The claim that between-cell variance is 288 times within-cell variance is withdrawn. F is a
  ratio of mean squares; the intraclass correlation for Re is 0.899.

## Disclosure

Impedance sweeps are not recorded once per discharge cycle. B0005, B0006 and B0007 each hold
278 sweeps against 168 discharge cycles; **B0018 holds 53 sweeps against 132 discharge
cycles**, so its 132 rows are built from 49 distinct measurements. This mapping step was not
described in earlier releases. Affected analyses are reported on both the full and the
de-duplicated series.

## Reproducing

```bash
pip install -r requirements.txt
python src/analysis.py
python src/export_tables.py
python src/figs.py
```

All paths resolve relative to the repository root. A clean clone reproduces every value above
and all eight figures.

Full detail in `CHANGELOG.md`.
