# Invigilator guide: verify the work in five steps

Environment: Windows, `E:\Osamas Paper\.venv\Scripts\python.exe -X utf8`, CPU only. Run from `E:\Osamas Paper\_showcase`. Steps 1-3 and 5 need about three minutes together.

| step | command | what it proves | expected |
|---|---|---|---|
| 1 | `python scripts\run_tests.py` | metrics are correct on hand-computed cases; ties and empty predictions are handled; tuning functions refuse test ids (leakage test); results are deterministic; headline numbers reproduce within 0.001 | 80 passed, 0 failed |
| 2 | `python scripts\verify_claims.py` | the 40 claims of the draft are all in the truth file; 13 headline numbers are recomputed from the saved prediction files and compared with it | `VERIFY: PASS` |
| 3 | open `report\index.html` | the story, results with intervals, negative findings, status board, in one offline file | - |
| 4 | open `notebooks\RUN_ORDER.md`, then a notebook on Colab | every training or GPU step is scripted, resumable, and marked NOT RUN where it has not run | header says "NOT RUN ON COLAB" |
| 5 | `python scripts\check_hashes.py` | inputs and shipped outputs match the recorded SHA-256 values | `HASHES: PASS` |

`pytest` is not installed in this environment (installation was not permitted in the build session); the test files are plain `test_*` functions and run unchanged under `pytest` once it is installed.

## One page: from raw data to every table

```
Dataset/tram_dev.tsv, tram_test.tsv            Dataset/combined_train.csv  (rows with source_dataset == "tram" = train)
Dataset/ttp-desc-mappings.csv (733 labels)     saved model outputs: Exp_1_4_run_tram_2_epoc_30/*_pw_s4{2,3,4}/*_probs.npy,
                                               run_match_1/ft20_s4{2,3,4}/*_scores.npy, run_match_1/zeroshot/test_scores.npy
            |                                              |
            +-------------------- src/ttpmap/data.py: build_space() ----------------+   (SVM refit here: deterministic)
                                           |
        src/ttpmap/fusion.py (z-scores, weights, dev-only guards)   src/ttpmap/metrics.py (P@1, MRR@3, F1)   src/ttpmap/stats.py
                                           |
  scripts/run_analyses.py ---------> results/systems, per_seed, f1_variants, comparisons, ablation, weight_surface, threshold_grid,
                                     support_buckets, fixed_broken, tactics, confusions, parent_sub, calibration, overlap_sensitivity,
                                     explained_vs_fusion, support_aware_*.csv ; results/tables/*.parquet
  scripts/run_support_aware_v2.py -> results/support_aware_v2.csv, support_aware_family.csv
  scripts/run_inference.py --------> results/faithfulness*.csv, maxlen.csv, efficiency.csv, hardware.json   (CPU inference, about 7 min)
                                           |
  scripts/build_numbers.py --------> thesis_numbers.json  (one entry per number; id, value, CI, definition, source, status)
                                           |
  scripts/build_thesis_feed.py ----> thesis_feed/tables/t_*.csv + .md, chapter files     scripts/make_figures.py -> figures/fig*.png, .svg
  scripts/build_docs.py, build_report.py -> README.md, docs/*, report/index.html          scripts/verify_claims.py, qa_gates.py -> checks
```

Thesis table to file: every table in `thesis_feed/tables/` names its source in its file name (`t_systems` from `results/systems.csv`, `t_comparisons_holm` from
`results/comparisons.csv`, `t_support_buckets` from `results/support_buckets.csv`, and so on); the builder is `scripts/build_thesis_feed.py`.
Rebuild all of it: `powershell -File run_all.ps1` (about 10 minutes; `-Fast` skips the CPU inference).

## Questions an examiner may ask, and where the answer is

| question | answer in |
|---|---|
| Were weights, thresholds or epochs tuned on the test set? | `src/ttpmap/fusion.py` (guards), `tests/test_project_data.py::test_tuning_never_sees_test_ids`, `_evidence_pack/02_settings.md` (review focus) |
| Which fusion number is the headline, and why are there three? | `THESIS_PLACEHOLDERS.md` section 4; ids B12a, B12nb, B13a in `THESIS_MAP.md` |
| Is the gain significant after correcting for multiple tests? | `results/comparisons.csv`, figure fig07 |
| Does the system work on rare and unseen techniques? | `results/support_buckets.csv`, figures fig06 and fig10 (it does not) |
| Do the explanations explain the reported system? | `results/explained_vs_fusion.csv`; README, last bullet of the story (only partly) |
| Was anything decided after seeing the result? | `experiments/prereg/REGISTRY.csv` (timestamps and hashes), `DECISIONS.md` D08 |
| What is missing? | status board in `README.md`; `GAP_REGISTER.md`; NOT-FOUND entries in `THESIS_MAP.md` |
