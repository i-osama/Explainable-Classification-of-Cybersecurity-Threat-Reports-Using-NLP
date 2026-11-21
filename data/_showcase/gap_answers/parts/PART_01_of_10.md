THESIS GAP ANSWERS - PART 1/10 - 2026-11-21
# THESIS GAP ANSWERS (Prompt F, run 2026-11-21, Asia/Dhaka)
Facts only. Status words: VERIFIED | NOTES-ONLY | CONFLICT | NOT-FOUND | NOT-RUN | NEEDS-AUTHOR | DECISION.
Privacy: raters = roles A/B/C; no dataset sentences; no names, IDs, keys. Paths under the user profile are written as %USERPROFILE%.
Times are local (Asia/Dhaka, UTC+6). "nb" = notebook. Scratch scripts were run read-only; new files only in _showcase\gap_answers\.

=== STEP0 | VERIFIED ===
FACTS:
thesis root: E:\Osamas Paper | Python 3.13.18 (E:\Osamas Paper\.venv)
_evidence_pack: E:\Osamas Paper\_evidence_pack (04_bootstrap.csv; 05_ece, 05_fixed_broken_all, 05_fixed_broken_by_bucket, 05_fixed_broken_examples, 05_parent_sub_confusions, 05_per_tactic, 05_rarity_buckets, 05_top20_confusions, 05_truncation_multilabel .csv; 07_human.md; 08_baseline.md; 09_repro\ with 8 files)
_showcase: E:\Osamas Paper\_showcase | thesis_numbers.json: E:\Osamas Paper\_showcase\thesis_numbers.json (649 claims; same sha256 2910c286a218138e as E:\Osamas Paper\WEB_SYNC_2026-11-17\thesis_numbers.json)
THESIS_PLACEHOLDERS.md: E:\Osamas Paper\_showcase\THESIS_PLACEHOLDERS.md (217 lines, 16 Nov 14:53) | audit_numbers.py: E:\Osamas Paper\_showcase\scripts\audit_numbers.py
deletion_test_v2_roberta_pw_s42.csv: E:\Osamas Paper\Exp_3_0_shap\
notebooks (E:\Osamas Paper\Experiments\): Exp_1_4_tram_30ep_3seeds, Exp_2.1_matcher_ (fusion grids), Exp_3_0_shap, Exp_3_0b_shap_all_725, Exp_3_1_deletion_test, Exp_3_1_shap, Exp_3_2_hand_check, Exp_3_3_rater_agreement (.ipynb)
colab_fusion_shap.ipynb: E:\Osamas Paper\_evidence_pack\09_repro\colab_fusion_shap.ipynb ; hardened copy E:\Osamas Paper\_showcase\COLAB_UPLOAD\colab\colab_fusion_shap_HARDENED.ipynb ; the version that ran = E:\Osamas Paper\_showcase\notebooks\06_explainability.ipynb (Kaggle, see Z1)
final_results_table.csv: E:\Osamas Paper\run_match_1\ | combined_train.csv: E:\Osamas Paper\Dataset\ (copy in _showcase\drive_upload\KDU\Thesis\Dataset\)
rater sheets: study 1 = E:\Osamas Paper\Exp_3_0_shap\hand_check_v2_roberta_pw_s42*.xlsx (3 files); study 2 = E:\Osamas Paper\_showcase\human_study\{sheets,TO_SEND,returned}
.git: E:\Osamas Paper\.git (only repo; tracks _showcase + _evidence_pack, 376 files) | RUN_COLAB.md: E:\Osamas Paper\_showcase\COLAB_UPLOAD\RUN_COLAB.md
Kaggle outputs: E:\Osamas Paper\_colab_returned\ (Z1) | Thesis_Final-v4.docx: NOT in thesis root; found at %USERPROFILE%\Downloads\Thesis_Final-v4.docx (20 Nov 15:43, 3,342,152 B)
SOURCE: file-system listing, sha256 and `git ls-files` run 2026-11-21 (the paths above are the sources)
EVIDENCE: sha256(thesis_numbers.json) begins 2910c286a218138e in both copies
CAVEAT: this local v4 has 0 highlighted runs and none of the 21 bracket texts (Y1). It is not the 21-gap v4 of the chat. Older v3 (%USERPROFILE%\Downloads\Thesis_Final-v3_Corrected.docx) has 20 highlighted runs.

=== K1-K5 CHECK | CONFLICT ===
PART STATUS: K1, K2, K3 VERIFIED; K4 values VERIFIED, 14 Nov supervisor note NOT-FOUND; K5 "0.0 -> 0.5" CONFLICT (G10)
FACTS:
K1: 255 settings, dev MRR@3 then P@1, (3,1,1,1) first: VERIFIED (Exp_2.1 CELL 8 code L45-51 + output). 1,711 grid -> (4,1,1,1) with matcher s42: VERIFIED (CELL 9 output); -> (8,3,2,2) with seed-averaged matcher: VERIFIED (_showcase\results\weight_surface.csv). Rank 28 and 30: both VERIFIED, tie of 3 settings (G01). Top-10 test scores printed: VERIFIED (CELL 9). Test P@1 0.800 / 0.804: VERIFIED.
K2: all 13 values VERIFIED (recomputed from deletion_test_v2_roberta_pw_s42.csv, one RandomState(42) shared by both variants as in nb).
K3: Cohen 0.062 / 0.133 / 0.236, exact 49 of 100: VERIFIED (Exp_3_3 CELL output). alpha -0.057 / 0.031, Fleiss -0.062: VERIFIED (07_human.md, recomputed by _evidence_pack\scripts\t7_human.py).
K4: 0.796 +/- 0.006, 0.800 +/- 0.001, 0.803: VERIFIED (G08). 14 Nov supervisor note: NOT-FOUND.
K5: fusion 0/10, matcher 2/10 (3-seed ens.), 0.294 vs 0.559: VERIFIED. "unseen R@5 0.0 -> 0.5": VERIFIED only against the classifiers; matcher 3-seed ens. = 0.6 (G10).
SOURCE: per K line; full sources in G01 (K1), X4 (K2), G08 (K4), G10 (K5); K3 = Experiments\Exp_3_3_rater_agreement.ipynb outputs + _evidence_pack\07_human.md
EVIDENCE: see the EVIDENCE lines of G01, X4, G08, G10
CAVEAT: K5 "unseen R@5 0.0 -> 0.5" holds only against the classifiers; the matcher 3-seed ensemble reaches 0.6.

=== G01 | NEEDS-AUTHOR ===
FACTS:
(a) both grids are in one file, Experiments\Exp_2.1_matcher_.ipynb (mtime 2026-11-06 13:15:00): grid 1 = CELL 8 (code comment "Cell 7"), grid 2 = CELL 9 ("Cell 8"). Execution counts are None (no timestamps). Order shown by code: CELL 9 uses `w_old = w_best` from CELL 8, so CELL 8 ran first. CELL 11 comment: weights "FIXED at (3,1,1,1)".
(a) recompute files: _evidence_pack\03_fusion_grid_dev.csv (14 Nov 08:19), _showcase\results\weight_surface.csv (14 Nov 13:45).
(b) 1,711 grid, matcher s42: (3,1,1,1) rank 28 (27 settings strictly better). 3 settings tie at dev (0.8698, 0.8179) = positions 28-30; the nb sort order (reverse tuple sort) puts (3,1,1,1) at 30. Registry B14.rank3111 = 28.
(b) 1,711 grid, seed-averaged matcher: (3,1,1,1) rank 16. (Both grids, both matchers: (3,1,1,1) rank 1 on the 255 grid.)
(c) matcher s42, dev MRR@3 / P@1: (3,1,1,1) 0.8698 / 0.8179; (4,1,1,1) 0.8744 / 0.8262; (8,3,2,2) 0.8733 / 0.8228 (rank 4)
(c) seed-avg matcher: (3,1,1,1) 0.8733 / 0.8228; (4,1,1,1) 0.8764 / 0.8278 (rank 2); (8,3,2,2) 0.8775 / 0.8295 (rank 1)
(d) test P@1, matcher s42: (3,1,1,1) 0.800 (recomputed 0.8000); (4,1,1,1) 0.804 (0.8041). Seed-avg: 0.8028 vs 0.8083.
(e) no written reason in any notebook, note or commit.
SOURCE: Exp_2.1_matcher_.ipynb CELL 8 L45-51, CELL 9 L5-25 + outputs, CELL 11; weight_surface.csv rows (matcher_s42|matcher_avg, wide_1711); 03_fusion_grid_dev.csv row 30; _showcase\THESIS_PLACEHOLDERS.md:47
EVIDENCE: "dev-chosen weights: {'matcher': 3, 'svm': 1, 'roberta': 1, 'secbert': 1} | dev MRR@3/P@1: (0.8698, 0.8179)"
"chosen with wide grid: {'matcher': 4, 'svm': 1, 'roberta': 1, 'secbert': 1} | old (Cell 7): {'matcher': 3, ...}"
"wide minus old: P@1 +0.004 [+0.000, +0.010] | MRR@3 +0.004 [+0.000, +0.008]" (CELL 9, test, 1,000 resamples)
CAVEAT: the CELL 9 printout showed test scores of the top-10 dev settings before CELL 11 fixed (3,1,1,1); the kept setting scores lower on test (0.800 vs 0.804).
QUESTIONS: Why was (3,1,1,1) kept after the finer grid? (fixed in advance / difference within noise / simpler integers / other)
