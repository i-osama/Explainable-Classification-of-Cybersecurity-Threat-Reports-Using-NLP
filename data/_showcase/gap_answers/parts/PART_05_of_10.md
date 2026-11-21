THESIS GAP ANSWERS - PART 5/10 - 2026-11-21
=== G15 | VERIFIED ===
PART STATUS: matcher retrain s42 and full-fusion SHAP VERIFIED; retrain s43/s44 and fusion with the retrained matcher NOT-RUN
FACTS:
matcher retrain: only seed 42 exists, _colab_returned\run_match_2_saved\ft20_s42 (Kaggle, 16 Nov): BAAI/bge-base-en-v1.5, best epoch 14, test P@1 0.7462, MRR@3 0.8138; weights matcher_state.pt (437,994,623 B). Original run_match_1 ft20_s42: P@1 0.7559 (best epoch 17); s43 0.7710; s44 0.7407. Retrain of s43, s44: NOT-RUN
full-fusion SHAP: _colab_returned\showcase_runs\06_explainability\fusion_shap_full_s42.jsonl, 100 rows (= first 100 of the permutation), 40 permutations, system "fusion (3,1,1,1) seed-paired, retrained matcher, seed 42"
z-score statistics constant under masking: False (summary z_statistics_constant 0.0). No rescaling shortcut: nb 06 explains each component's z-scored output in one multi-output permutation SHAP and sums with the weights
identity shap_fused = 3*matcher + svm + roberta_s42 + secbert_s42: holds, max |diff| 3.6e-15 (by construction, shared permutations); additivity error max 4.1e-05
disagreement RoBERTa s42 top-1 vs seed-avg fusion top-1: 108 of 725 = 14.9% (registry E4, E4.share). Vs seed-paired s42 fusion: 97 of 725. In the 100 SHAP rows: same label 89 of 100; in the 97 deletion rows 86 of 97 (summary same_label_share 0.887)
deletion test on the fused score (Remove variant, 97 sentences): drop fused-SHAP top-3 35.417, RoBERTa-SHAP top-3 32.510, random-3 7.069 (units: fused z-score sum); fused minus RoBERTa 2.907 [1.104, 4.936]; fused top-1 correct 0.80
SOURCE: _colab_returned\...\fusion_shap_summary.json; metrics.json; _showcase\notebooks\06_explainability.ipynb CELL 7 L7-9, CELL 8 L18-23, CELL 9; registry T1.*, T2.*
EVIDENCE: fusion_shap_summary.json "system": "fusion (3,1,1,1) seed-paired, retrained matcher, seed 42"; "z_statistics_constant": 0.0; "max_additivity_error": 4.143e-05
"fused_minus_roberta": 2.9068, "fused_minus_roberta_lo": 1.1039, "fused_minus_roberta_hi": 4.9358; "n_deletion": 97; "same_label_share": 0.8866
CAVEAT: explained system = seed-paired with the retrained matcher s42, not the seed-averaged headline. Fusion with the retrained matcher (T3.fusion_replication): NOT-RUN. Missing-run order (RUN_COLAB.md:10): 04 smoke 5 min > 04 per seed 25-35 min > 06 smoke 5 > 06 real 30-60 (T4).

=== G16 | NOT-FOUND ===
PART STATUS: local analysis env and 16 Nov cloud envs VERIFIED; Hugging Face revision hashes and original Colab training env NOT-FOUND
FACTS:
LOCAL analysis environment: Python 3.13.18; datasets==5.2.0, krippendorff==0.9.0, numpy==2.5.4, openpyxl==3.1.5, pandas==3.1.1, scikit-learn==1.9.1, scipy==1.18.1, sentence-transformers==6.3.0, shap==0.54.1, statsmodels==0.15.0, tokenizers==0.23.3, torch==2.15.0+cpu, transformers==5.23.0
full freeze (173 packages): _showcase\gap_answers\requirements_local.txt (venv has no pip; exported with importlib.metadata)
model ids: RoBERTa "roberta-base", SecBERT "jackaduma/SecBERT" (Exp_1_4 CELL 2 L16); matcher "BAAI/bge-base-en-v1.5" (run_match_1\ft20_s*\metrics.json model_name)
revision hashes: NOT-FOUND (config.json has no _commit_hash; THESIS_PLACEHOLDERS.md:25); checkpoints record transformers_version 5.22.1
cloud envs that exist: Colab nb 00 on 16 Nov, _showcase\results\colab\env_00\env_colab.json (Python 3.13.16, torch 2.14.1+cu130, Tesla T4, 722 packages); Kaggle runs 16 Nov, run_manifest_04/06 (torch 2.11.0+cu130, transformers 5.22.1, sentence-transformers 5.7.0, shap 0.54.1, scikit-learn 1.6.1, numpy 2.1.3, pandas 2.3.3, 937 packages)
original Colab training environment: NOT-FOUND (registry N4.colab_env); partial pins in _evidence_pack\09_repro\requirements_colab_training.txt (transformers 5.22.1, torch 2.14.1, shap 0.54.1)
SOURCE: importlib.metadata of E:\Osamas Paper\.venv; Exp_1_4_tram_30ep_3seeds.ipynb CELL 2 L16; run_match_1\ft20_s*\metrics.json; _showcase\results\colab\env_00\env_colab.json; _colab_returned\showcase_runs\*\run_manifest_*.json; _evidence_pack\09_repro\requirements_colab_training.txt
EVIDENCE: Exp_1_4 CELL 2 L16 `MODELS = {"secbert": "jackaduma/SecBERT", "roberta": "roberta-base"}`
CAVEAT: requirements_local.txt is the local analysis env, not the training env.

=== G17 | NEEDS-AUTHOR ===
PART STATUS: rebuild VERIFIED (3,468 rows, 180 labels, sha256 below); original Drive file hash NOT-FOUND; public file name/revision NEEDS-AUTHOR
FACTS:
rebuild script: _evidence_pack\09_repro\make_tram_train.py:9-13 (rows of Dataset\combined_train.csv with source_dataset == "tram", columns text1, labels, tab-separated)
rows 3,468; distinct labels 180; duplicate texts 0
sha256 of the rebuilt file: a53b9d467b751de7eb22496167b01515a61de942b694d6c7575899b19512c777 (LF line ends, 546,153 B); 82ac83d8c9647c13f474901c8321f813535187ab1099b7f581aa9cce0b7130d0 (CRLF, Windows pandas default, 549,622 B)
original tram_train.tsv (Drive) sha256: NOT-FOUND (not in any input-hash manifest; registry N1 NOT-FOUND)
combined_train.csv: source_dataset counts procedure 8,487 / tram 3,468 / derived_procedure 2,510; sha256 24301c7156ff39ef...
public source: Hugging Face tumeteor/Security-TTP-Mapping, DOI 10.57967/hf/1811 (_showcase\docs\DATA_CARD.md:15); file paths inside that dataset: NOT-FOUND locally
regeneration steps (derivable part): (1) obtain combined_train.csv from the public dataset (file name/revision NEEDS-AUTHOR) and place it as Dataset\combined_train.csv; (2) run `python _evidence_pack\09_repro\make_tram_train.py Dataset\tram_train.tsv` (argument = output path; default = next to the script); (3) check 3,468 rows, 180 labels, SVM P@1 0.742 with _evidence_pack\09_repro\smoke_test.py
SOURCE: make_tram_train.py; 09_repro\README_tram_train.md
EVIDENCE: `t = df[df["source_dataset"] == "tram"][["text1", "labels"]]` / `assert len(t) == 3468` / `t.to_csv(out, sep="\t", index=False)`
CAVEAT: .gitignore excludes tram_train.* and combined_train.* (not in the repo).
QUESTIONS: Which file of tumeteor/Security-TTP-Mapping is Dataset\combined_train.csv (name/revision)?

=== G19 | VERIFIED ===
FACTS:
sampling: first 100 rows of numpy.random.RandomState(42).permutation(725); no stratification; no hand selection; prefix-stable (same order as the SHAP run)
eligibility filter: applied after sampling and only in the deletion test; the rater sheets keep all 100 rows
order: sheet order = permutation order, same for all raters (no per-rater shuffling); control items: none in study 1 (top-3 SHAP words only; gold hidden, SHOW_GOLD = False)
rows per rater: A 100, B 100, C 3
SOURCE: Exp_3_2_hand_check.ipynb CELL 0 L6-11, CELL 1 L17-18, CELL 2 L44; 07_human.md:10, 15-19
EVIDENCE: `SEED, N_TOTAL, N_CHECK, K_SHOW = 42, 725, 100, 3`; `order = [int(r) for r in np.random.RandomState(SEED).permutation(N_TOTAL)[:N_CHECK]]`
CAVEAT: Rater C rated only 3 of the 100 rows (326, 518, 554).
