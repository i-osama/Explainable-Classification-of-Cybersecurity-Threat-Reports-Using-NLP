THESIS GAP ANSWERS - PART 8/10 - 2026-11-21
=== X7 | VERIFIED ===
FACTS (_showcase\THESIS_PLACEHOLDERS.md lines still NOT-FOUND or NOTES-ONLY; -> gap):
:25 Hugging Face revision hash NOT-FOUND -> G16 | :37 matcher saved weights NOT-FOUND -> G15 (s42 retrain now exists, original still missing)
:45 grid timestamps NOT-FOUND -> G01 | :47 why (3,1,1,1) kept NOTES-ONLY -> G01
:72 setting for RoBERTa vs SVM / SecBERT in the draft NOT-FOUND -> G09 (C3 = nb 1k setting; C4 unknown)
:114 background of raters B and C NOT-FOUND -> G04 | :121 pre-dedup train size NOT-FOUND -> G17
:161-166 baseline comparability (test split, granularity, ATT&CK version, metrics, training data, baseline numbers) NOTES-ONLY -> G13
:173 full Colab environment NOT-FOUND -> G16 (16 Nov env files exist; original training env still missing)
:174 repository URL NOT-FOUND -> G21 | :175 git history of original experiments NOT-FOUND -> G21 | :176 tram_train.tsv VERIFIED rebuild / NOT-FOUND original -> G17
SOURCE: _showcase\THESIS_PLACEHOLDERS.md (217 lines, 16 Nov 14:53), 17 open lines as listed
EVIDENCE: THESIS_PLACEHOLDERS.md:47 "| why (3,1,1,1) was kept | no written reason. CELL 11 only says "weights FIXED at (3,1,1,1)". ..."
CAVEAT: the ledger is dated 16 Nov; later results (G15 Kaggle s42, G16 cloud envs) are noted after the arrows.

=== Y1 | CONFLICT ===
FACTS (local %USERPROFILE%\Downloads\Thesis_Final-v4.docx):
(a) highlighted runs: 0 (yellow, green, cyan). The 21 bracket texts are absent; the gap sentences remain cut, e.g. "...removing three random words Plausibility is assessed...", "The raters took part voluntarily rated sentences..."
(b) trigger sentences outside the references: 25; covered by G-blocks: p899 (G13), p942 (G22), Table 5.4 p731-744 and p873 (G09); content wording, not gaps: p275, p642, p884, p952, p953; TOC lines p91, p104, p127
UNCOVERED: front matter p39 | "Signature, _____________________________" (signature line empty)
UNCOVERED: whole file | 0 colons, 0 semicolons, 0 hyphens inside words (v3_Corrected: 177, 140, 374). Effects: all 16 URLs read "https,//...", "CRISP DM", "TF IDF", "top 3", "seed averaged", "Student ID, ..." (references p956 onward)
UNCOVERED: whole file | v4 has 102,096 text characters vs 123,803 in v3_Corrected
SOURCE: docx_scan.py (run-level highlight + full text scan) on %USERPROFILE%\Downloads\Thesis_Final-v4.docx and Thesis_Final-v3_Corrected.docx, 2026-11-21
EVIDENCE: v4 p39 "Signature, _____________________________"
CAVEAT: Y1 ran on the local v4, not the chat's 21-gap v4. To check the chat version: copy it to _showcase\gap_answers\ and rerun only Y1.

=== Z1 KAGGLE RUNS (asked 21 Nov: trained final data not yet shown to Claude web) | VERIFIED ===
FACTS:
folder: E:\Osamas Paper\_colab_returned\ (runner "kaggle", Tesla T4, Python 3.13.16, torch 2.11.0+cu130)
run 1: notebook 04_train_matcher_save, 16 Nov 02:46-03:23 (manifest time): run_match_2_saved\ft20_s42\{matcher_state.pt 437,994,623 B; dev_scores.npy; test_scores.npy; metrics.json} + showcase_runs\04_train_matcher_save\{manifest_matcher_ft20_s42.json, run_manifest_04_train_matcher_save.json}; result: test P@1 0.7462, MRR@3 0.8138, R@5 0.8660, dev P@1 0.7699, best epoch 14
run 2: notebook 06_explainability, 16 Nov 07:38-08:10: showcase_runs\06_explainability\{fusion_shap_full_s42.jsonl 100 rows, fusion_shap_summary.json, manifest_fusion_shap.json, run_manifest_06_explainability.json}; results in G15
integrity: all 6 output sha256 values in the two manifests match the local files
already ingested: copies in _showcase\results\colab\{matcher_ft20_s42, fusion_shap}; registry ids T1.matcher_retrained_p1 / _mrr3 / _r5, T2.full_fusion_shap, T2.n_sentences, T2.max_additivity_error, T2.fused_top1_correct, T2.same_label_share (thesis_numbers.json, same copy in WEB_SYNC_2026-11-17)
not yet in the thesis: Thesis_Final-v4 still says full-fusion explanations are pending (G15 sentence); no v4 sentence uses T1/T2
Google Drive (metadata only, folder-by-folder listing of KDU/Thesis, 21 Nov): one run output not on this PC: My Drive/KDU/Thesis/showcase_runs/03_train_classifiers/roberta_pw_s45/ = best_state.pt 499,202,586 B and ckpt_last.pt 231,708,159 B (both 15 Nov ~19:55); no metrics.json, no probs/labels .npy, no manifest -> partial run, results NOT-RUN; seed 46 NOT-FOUND
Drive has no folders for runs 04-10 and no run_match_2_saved (Kaggle 04/06 outputs exist only locally); Drive COLAB_UPLOAD/kaggle/ holds the 2 source notebooks only
Kaggle account listing (kaggle kernels list --mine): NOT-RUN (not checked from this PC)
still missing (registry TODO-COLAB): T3 fusion with the retrained matcher, T4 seeds 45-46, T5 baseline same protocol, T6 cross-dataset, T8 human study v2, T9 usability
SOURCE: _colab_returned\showcase_runs\*\run_manifest_*.json and manifest_*.json (sha256 compared 2026-11-21); Google Drive metadata listing of My Drive/KDU/Thesis (21 Nov)
EVIDENCE: fusion_shap_summary.json "system": "fusion (3,1,1,1) seed-paired, retrained matcher, seed 42"
CAVEAT: fusion_shap_full_s42.jsonl contains the words of 100 test sentences (G03). Upload the summary/manifest JSON, not the jsonl, if dataset text must stay out of shared copies.
