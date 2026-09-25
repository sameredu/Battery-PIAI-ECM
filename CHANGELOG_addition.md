## v3.0.2 — documentation and determinism

Packaging only. No numerical result changes; the values in the manuscript are unchanged.

- **Root `README.md` restored.** A copy step in v3.0.1 overwrote it with `results/README.md`,
  so the repository landing page showed the contents of the results folder instead of the
  project description. The restored README also lists the actual file tree, which the earlier
  version did not.
- **`LICENSE` added.** The MIT badge and `.zenodo.json` both declared MIT but no licence file
  had ever been committed.
- **`src/figs2.py` removed.** It was merged into `src/figs.py` in v3.0.1 but the file itself
  was not deleted.
- **Figure 4 is now deterministic.** The jitter in the strip overlay used an unseeded random
  draw, so reruns produced a visually different image from the published one. The seed is now
  fixed and reruns are byte-identical.
- **`results/results_summary.json` ignored.** It duplicated `results/metrics.json`.

This is the tag to cite and to archive.
