# PROGRESS (evidence pack)

Resume notes: run scripts with `E:\Osamas Paper\.venv\Scripts\python.exe` from `_evidence_pack\scripts\` (`run_all.py`, `run_all.py --fast`).
Console output is truncated by a plugin: redirect to a file and read it with offset/limit.
Notebook sources are dumped to `nb_src\<notebook>.txt` (cite as notebook : CELL n). The venv has no pip module.

| Task | Status | Files |
|---|---|---|
| T0 inventory | DONE | 00_inventory.md, 00_env.txt, 00_hashes.csv, nb_src/ |
| T1 dataset | DONE | 01_dataset.md, 01_label_counts.csv, 01_duplicates.csv, 01_near_duplicates.csv, 01_truncated_test_ids.csv |
| T2 settings | DONE | 02_settings.md (hand-written citations + review-focus verdicts) |
| T3 recompute | DONE | 03_results_recomputed.csv, 03_results.md, 03_fusion_grid_dev.csv |
| T4 statistics | DONE | 04_bootstrap.csv, 04_statistics.md |
| T5 error/rarity | DONE | 05_*.csv, 05_errors.md, fig_rarity.png, fig_fusion_delta.png |
| T6 SHAP | DONE | 06_shap.md, 06_deletion_test_725.csv, fig_shap_ex1-3.png |
| T7 human study | DONE | 07_human.md, 07_agreement.csv |
| T8 baseline | DONE | 08_baseline.md (paper not in folder; numbers confirmed from arXiv:2401.10337 PDF) |
| T9 repro kit | DONE | 09_repro/ (smoke test passes in 5 s) |
| T10 report + zip | DONE | EVIDENCE_REPORT.md, ..\_evidence_pack.zip |
| X0 fusion vs RoBERTa | DONE | 10_fusion_vs_roberta.md/.csv |
| X1/X2 fusion-score SHAP | DONE for the classifier components (40 sentences, 3,900 s CPU); report and zip rebuilt afterwards | 11_fusion_shap_partial.jsonl, 11_fusion_shap.md |

## IN PROGRESS: local matcher retrain + full-fusion SHAP (user request, 2026-11-14)
- `scripts\x3_train_matcher_cpu.py --seed 42` runs DETACHED (PID in `scripts\_x3_pid.txt`, log `scripts\_x3_train_log.txt`).
  CPU benchmark 32 s/step = about 2 h per epoch, max 20 epochs, patience 4 -> up to about 40 h. Checkpoint after every epoch in
  `matcher_retrain\ft20_s42\ckpt_last.pt`; re-running the same command resumes. Best weights: `matcher_state.pt`.
- Scoring path validated: `x1_fusion_shap.py --selftest` reproduces the saved zero-shot scores (P@1 0.2276, max score diff 2.7e-4).
- When `metrics.json` has `"finished": true`:
  1. `python x1_fusion_shap.py --n 40 --seed 42 --matcher-dir "E:\Osamas Paper\_evidence_pack\matcher_retrain\ft20_s42"` (about 2.5 min per sentence)
  2. `python x2_fusion_shap_summary.py --file 11_fusion_shap_full.jsonl` (rename the earlier partial 11_fusion_shap.md first: it is overwritten)
  3. report the retrained matcher's own test P@1 next to run_match_1 (0.756) and re-run `t10_report.py`.

## Blocked / not run
- Full-fusion SHAP: matcher weights were never saved. Needs `09_repro/colab_train_matcher_with_save.py` on Colab (20-30 min per seed), then `x1_fusion_shap.py --matcher-dir ...`.
- No retraining was done. Only inference with saved checkpoints and a deterministic SVM refit.

## Key findings
- All B, C, D, E numbers reproduce. Mismatches: A6 (overlap), B13b (MRR@3 0.856 not 0.853), B14 ((3,1,1,1) is the 255-grid winner, the 1,711 grid picks (4,1,1,1)).
- B7/B8 P@1 values are 3-seed ensembles, not seed means (0.752 / 0.743).
- Fusion P@1 on unseen labels = 0/10; gains come from labels with >= 10 training sentences.
