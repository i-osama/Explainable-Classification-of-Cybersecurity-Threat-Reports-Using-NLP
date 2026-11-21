# RUN_ORDER: from raw data to every table and figure

Repository URL: **NOT-FOUND** (`E:\Osamas Paper` is not a git repository; no remote).

## A. Training (Google Colab, GPU). NOT re-run for this pack

Paths in the notebooks are `/content/drive/MyDrive/KDU/Thesis/...`. Run cells top to bottom.

| step | notebook | produces | runtime (from logs) |
|---|---|---|---|
| A1 | `Experiments/Exp_1_4_tram_30ep_3seeds.ipynb` CELL 2-10 | SVM reference; `Exp_1_4_run_tram_2_epoc_30/{roberta,secbert}_{pw,nopw}_s42/` | NOT-FOUND per run (no timing printed) |
| A2 | same, CELL 14 | `..._pw_s43`, `..._pw_s44` | NOT-FOUND |
| A3 | `Experiments/Exp_2.1_matcher_.ipynb` CELL 1-4 | `run_match_1/zeroshot/` | minutes |
| A4 | same, CELL 7 | `run_match_1/ft20_s42,43,44/` (scores only) | "about 20-30 min" per seed (notebook CELL 0) |
| A5 | same, CELL 8-13 | fusion weights, `final_results_table.csv`, ablation | seconds, CPU |
| A6 | `Experiments/Exp_3_0b_shap_all_725.ipynb` | `Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl` | 3,504 s for 625 rows on GPU (CELL 3 output) |
| A7 | `Experiments/Exp_3_1_deletion_test.ipynb` | `deletion_test_v2_roberta_pw_s42.csv` | seconds |
| A8 | `Experiments/Exp_3_2_hand_check.ipynb`, `Exp_3_3_rater_agreement.ipynb` | rating sheet, `rater_agreement_v2_roberta_pw_s42.csv` | seconds |

Input not on E: for A1-A4: `Dataset/tram_train.tsv`. Rebuild it with `09_repro/make_tram_train.py`.

## B. Evidence pack (this PC, CPU, read-only on project files)

```
cd "E:\Osamas Paper\_evidence_pack\scripts"
"E:\Osamas Paper\.venv\Scripts\python.exe" run_all.py          # everything (about 1 h with the SHAP extra)
"E:\Osamas Paper\.venv\Scripts\python.exe" run_all.py --fast   # about 3 min, skips model inference
```

| thesis item | script | output |
|---|---|---|
| dataset table, overlap, truncation | `t1_dataset.py` | `01_dataset.md`, `01_label_counts.csv`, `01_duplicates.csv`, `01_near_duplicates.csv` |
| main results table, per-seed tables, fusion grids | `t3_results.py` | `03_results_recomputed.csv`, `03_results.md`, `03_fusion_grid_dev.csv` |
| significance (bootstrap, McNemar) | `t4_bootstrap.py` | `04_bootstrap.csv`, `04_statistics.md` |
| rarity, tactics, confusions, fixed/broken, truncation, ECE | `t5_errors.py` | `05_*.csv`, `05_errors.md`, `fig_rarity.png`, `fig_fusion_delta.png` |
| SHAP examples, deletion test | `t6_shap.py` | `06_shap.md`, `06_deletion_test_725.csv`, `fig_shap_ex1..3.png` |
| rater agreement | `t7_human.py` | `07_human.md`, `07_agreement.csv` |
| fusion vs explained model | `x0_fusion_vs_roberta.py` | `10_fusion_vs_roberta.md/.csv` |
| SHAP of the fused score | `x1_fusion_shap.py`, `x2_fusion_shap_summary.py` | `11_fusion_shap_partial.jsonl`, `11_fusion_shap.md` |
| smoke test | `09_repro/smoke_test.py` | console |

External file used by `t5_errors.py` only: `external/enterprise-attack-12.1.json`
(`https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack-12.1.json`, 38 MB, not in the zip).

## C. Environment

- `requirements_local_analysis.txt`: exact pins of the venv that produced this pack (pip freeze).
- `requirements_colab_training.txt`: the only training-side versions that can be read from files. The Colab pip freeze was never saved.
