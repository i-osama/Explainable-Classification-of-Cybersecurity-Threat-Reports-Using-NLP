# Notebook run order

**Nothing in this folder has been run on Colab.** Each notebook was validated (nbformat) and smoke-executed locally on CPU with `SMOKE=True`
(20 samples, GPU-only cells guarded); logs are in `results/smoke_logs/`. A smoke run is a code check, not a result.

Runtime: Colab T4 GPU. Drive path: `MyDrive/KDU/Thesis`. Every notebook writes to `MyDrive/KDU/Thesis/showcase_runs/<notebook>/` (new folder) and
notebook 04 to `MyDrive/KDU/Thesis/run_match_2_saved/` (new folder). Nothing existing is overwritten. All long runs checkpoint to Drive and resume.
Runtimes are estimates unless a source is given. Kill-switch: Tue 18 Nov 2026 18:00 Asia/Dhaka; anything not finished becomes future work.

**Hardened variants (Prompt F, 16 Nov 2026):** `_showcase/COLAB_UPLOAD/` holds Drive-optional, fail-fast, resumable copies of 04, 06 and `colab_fusion_shap` (plus Kaggle copies of 04 and 06), the input zips and `COLAB_UPLOAD/RUN_COLAB.md` / `COLAB_UPLOAD/KAGGLE.md`. Same model code; prefer them over the originals. Rebuild with `python scripts/make_colab_hardened.py`.

## Priority order

| step | notebook | what it does | runtime (T4) | needs | fills in `thesis_numbers.json` |
|---|---|---|---|---|---|
| 0 | `00_setup_and_verify` | mount Drive, check files, record environment and GPU | 1 min | Drive folder | `T7.env_colab` |
| 1 | `04_train_matcher_save` (first training cell: seed 42) | retrain the matcher and **save the weights** | 20-30 min (estimate printed in the original notebook) | Dataset files | `T1.matcher_retrained_p1` |
| 2 | `06_explainability` | SHAP of the full fusion on 100 fixed sentences, deletion test on the fused score | 30-60 min | step 1; classifier checkpoints seed 42; stored RoBERTa SHAP file | `T2.full_fusion_shap` |
| 3 | `05_fusion_and_ablation` | fusion, both weight grids, ablation, with the retrained matcher | 1 min for seed 42; complete after step 4 | step 1 (seed 42), better after seeds 43, 44 | `T3.fusion_replication` |
| 4 | `04_train_matcher_save` (second training cell: seeds 43-46) and `03_train_classifiers` (seeds 45, 46) | extra seeds, weights saved | matcher 20-30 min per seed (4 seeds); classifiers about 15-25 min per run (4 runs) | Dataset files | `T4.seeds_45_46` |
| 5 | `09_baseline_same_protocol` | our systems under the published metric definitions; instructions for re-running the published model | 1 min; the published model itself: about 24 h per run on a V100 (stated in the paper) | saved scores | `T5.baseline_same_protocol` |
| 6 | `08_extension_cross_dataset` | objective (b): train the matcher on the sibling sources, test on TRAM test | about 1.5-2 h per configuration and seed (6 runs) | `Dataset/combined_train.csv` (present) | `T6.cross_dataset` |
| 7 | `10_llm_baseline` | protocol only; not run; needs the author's own API client | - | - | none |

Not on the critical path (CPU, minutes, can run anywhere): `01_data_audit`, `02_baselines`, `07_extension_support_aware_fusion`.
Their content is already computed locally (`results/*.csv`); the notebooks re-check it in the Colab environment.

## Already available before the showcase

`_evidence_pack/09_repro/colab_fusion_shap.ipynb` does steps 1 and 2 in one notebook (cells 1-6). If it has been run, notebook 06 finds the matcher
weights in `run_match_2_saved/ft20_s42/` and only the SHAP part remains. Do not run both step 1 variants.

## After a run

1. Download or sync `MyDrive/KDU/Thesis/showcase_runs/` and `run_match_2_saved/*/{metrics.json,test_scores.npy,dev_scores.npy}` to `E:\Osamas Paper\` (weights stay on Drive).
2. Tell Claude Code: "INGEST COLAB OUTPUTS" (Prompt C). Manifests are validated, hashes checked, metrics recomputed with `ttpmap.metrics`, `thesis_numbers.json` updated, figures and report rebuilt, `THESIS_DELTA.md` written.

## Risks

- Free-tier disconnects: every training loop resumes from `ckpt_last.pt` on Drive; re-run the cell.
- GPU nondeterminism: retrained matcher scores will differ slightly from `run_match_1`; the retrained model's own numbers are reported beside the originals.
- `drive.mount` inside the VS Code Colab extension is untested; if it fails, run the notebooks in the browser.
