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

=== G02 | VERIFIED ===
FACTS:
mask token string: "<mask>" (tokenizer_config.json of Exp_1_4_run_tram_2_epoc_30\roberta_pw_s42; code uses tok.mask_token)
whitespace: kept. Unit = whitespace-delimited word; the whole word becomes one "<mask>" string before tokenisation (no subword-level masking; a word of several subwords becomes one <mask>)
Remove variant: the word and its trailing whitespace are deleted; trailing space stripped if the last word is hidden; no <mask>
both variants: one notebook, Experiments\Exp_3_1_deletion_test.ipynb (CELL 2 helpers, CELL 3 run), one output file Exp_3_0_shap\deletion_test_v2_roberta_pw_s42.csv (columns drop_*_mask, drop_*_remove)
SHAP used the same masking: Exp_3_0b_shap_all_725 CELL 2 L75-77 build_text
SOURCE: Exp_3_1_deletion_test.ipynb CELL 2 L36-53
EVIDENCE: L36 `UNIT_RE = re.compile(r"(\s*)(\S+)(\s*)")`
L44-46 `def masked_text(parts, hide): return "".join(l + (tok.mask_token if i in hide else c) + t for i, (l, c, t) in enumerate(parts))`
L48-53 `def removed_text(parts, hide, original): s = "".join(l + c + t for i, (l, c, t) in enumerate(parts) if i not in hide); if (len(parts) - 1) in hide and not original[-1:].isspace(): s = s.rstrip(); return s`
CAVEAT: score = logit of the top-1 predicted label; drop = logit(original) - logit(edited). K2 all VERIFIED (X4).

=== G03 | CONFLICT ===
FACTS:
scan: 581 files (csv, tsv, json, jsonl, ipynb incl. outputs, txt, md, py) in _showcase, _evidence_pack, Experiments, ttp_app + root *.ipynb; 4,797 TRAM sentences (train 3,468 / dev 604 / test 725), whitespace-normalised, exact case. Second pass: [[marker]]-stripped text, .html, text members of .zip.
git-tracked files with dataset sentences (3 of 376): _evidence_pack/05_errors.md = 14 test sentences (6-15 words); _evidence_pack/06_shap.md = 3 test sentences (10-23 words); _showcase/tests/test_fusion_stats_schema.py = 1 train sentence (4 words)
the 2 _evidence_pack files are also on the remote branch origin/main (git ls-tree)
untracked files with dataset text (not in the repo, but inside _showcase): drive_upload\KDU\Thesis\Dataset\{combined_train.csv 3,957; tram_test.tsv 728; tram_dev.tsv 605}; drive_upload\...\Exp_3_0_shap\shap_v2_roberta_pw_s42.jsonl 728; results\colab\fusion_shap\fusion_shap_full_s42.jsonl 100; COLAB_UPLOAD\thesis_inputs.zip 5,720 (marker pass); human_study\sheets\rating_sheet_R1-R3.csv 77 each; human_study\TO_SEND\rater_R1-R3.zip 79 each; human_study\materials_local 2+2
other untracked: _evidence_pack\05_fixed_broken_all.csv 94, 11_fusion_shap_partial.jsonl 40, 05_fixed_broken_examples.csv 19, 01_near_duplicates.csv 9, 01_duplicates.csv 2, scripts\_t6_log.txt 3; Experiments\Exp_3_1_shap_results.txt 3; combined_3_dataset_exploration.ipynb 2; ttp_app\grounding_report.csv 1; _evidence_pack\external\enterprise-attack-12.1.json 2,088 (public ATT&CK procedure examples, not the TRAM files)
per-file table (paths and counts only): _showcase\gap_answers\g03_dataset_text_counts.csv; publish list = publish_manifest.csv (G21)
SOURCE: scan scripts run 2026-11-21; .gitignore (excludes dataset files, *.jsonl, 05_fixed_broken_*, 01_*duplicates); _showcase\scripts\qa_gates.py:70-90
EVIDENCE: qa_gates.py:73 scans only `git ls-files _showcase`; :89 flags a file only if `n_s > 3` sentences of >= 60 characters
CAVEAT: the QA gate never looked at _evidence_pack, so the v2.5 sentence "an automated check of the code package found no dataset text beyond short quoted examples" holds for _showcase only. Not scanned: xlsx, parquet, docx, pdf, images. Images to check by eye: _evidence_pack\fig_shap_ex1-3.png, _showcase\figures\fig14_shap_examples.png/.svg. Remote repo visibility (public/private): NOT-FOUND locally.

=== G04 | NEEDS-AUTHOR ===
FACTS:
study 1 roles (07_human.md): Rater A sheet sha256 9e83b71a, 100 rows rated; Rater B 0c1fb4a9, 100 rated; Rater C ceb79cdb, 3 rated (rows 326, 518, 554); all sheets match the fixed sample
07_human.md: "Rater A's sheet is the project author's own sheet according to the notebook output order"; background of B and C NOT-FOUND (registry N9.rater_roles NOT-FOUND)
the 3 workbook file names carry personal name tags (withheld); keep them out of any upload or repository
consent text for study 1: NOT-FOUND (workbooks have one sheet `rating`; no information sheet in any folder)
study 2 (not yet returned) consent wording: _showcase\docs\RATER_INSTRUCTIONS.md:45 and human_study\TO_SEND\RETURN_CHECKLIST.md:14; protocol _showcase\docs\HUMAN_STUDY_PROTOCOL.md:94-95
draft v2.5 (_showcase\Thesis_Draft_v2.5.docx, Section 3.7) calls the raters "project colleagues": NOTES-ONLY (no source file)
SOURCE: _evidence_pack\07_human.md:15-21; Exp_3_0_shap\hand_check_v2_roberta_pw_s42*.xlsx (headers only read)
EVIDENCE: RATER_INSTRUCTIONS.md:45 "We store only your role and your answers. We do not store your name. You may withdraw your sheet at any time."
HUMAN_STUDY_PROTOCOL.md:95 "Whether institutional ethics approval is required is a question for the supervisor."
CAVEAT: "Rater A = the author" rests only on the notebook output order (07_human.md), not on a statement by the author.
QUESTIONS: Relationship of Rater A, B, C to the project (project member / peer / external)? | How was consent obtained in study 1 (written / message / stated in the sheet)? | Is any rater the thesis author (yes/no; which role)? | Was ethics approval needed (supervisor answer)?

=== G05 | NEEDS-AUTHOR ===
FACTS:
university AI-use policy or declaration template: NOT-FOUND in E:\Osamas Paper (searched md/txt/py/yaml for generative AI, AI-use, AI declaration, policy)
fallback sentence (agreed 17 Nov), ttp_app\README.md:90: "The demonstration application was developed with the assistance of generative AI tools (Claude, Anthropic); all outputs were checked against the thesis results by the scripts described in Section X, and the author reviewed the code."
README disclosure list, ttp_app\README.md:85-89: Claude (claude.ai) wrote the first app code, tests, grounding rule v1, README; Claude Code ran checks on 15 Nov; qwen2.5:7b (Ollama) writes the optional explanations
_showcase\README.md:119-123: Claude Code used for refactoring, tests, scripts, number recompute, figures, notebooks, docs
draft v2.5 Section 3.7 declaration (NOTES-ONLY, AI-drafted): Claude for analysis code, number re-checks and wording; qwen2.5:7b for prototype explanations
SOURCE: ttp_app\README.md:83-90; _showcase\README.md:119-123; _showcase\CHANGELOG_v2.5.md:25,38
EVIDENCE: ttp_app\README.md:90 "The demonstration application was developed with the assistance of generative AI tools (Claude, Anthropic); ..."
CAVEAT: "Section X" in the fallback sentence is a placeholder.
QUESTIONS: Names of all AI tools used? | Stages used (code review / analysis scripts / drafting / figures)? | Who checked the outputs? | Supervisor: what must the AI-use declaration contain and where does it go?

=== G06 + G12 | VERIFIED ===
FACTS:
sample: rows = numpy.random.RandomState(42).permutation(725)[:100] (deletion CSV rows equal this list in order)
rule 1 (deletion test only): at least 6 whitespace words AND at least 3 words with positive SHAP value -> 97 of 100 used
excluded by rule 1: row 72 (4 words, 7 model tokens), row 81 (6 words, 2 positive, 11 tokens), row 210 (7 words, 2 positive, 12 tokens)
rule 2: main result only on sentences of at most 128 RoBERTa tokens (n_model_tokens <= 128) -> 93; reported separately: row 711 (243 tokens), 721 (335), 697 (274), 669 (147)
eligibility = 100 - 3 - 4 = 93 (registry E3.n = 93; E3 = 93 / 93)
rater study used all 100 rows (filter not applied there)
SOURCE: Exp_3_1_deletion_test.ipynb CELL 2 L7-13, CELL 3 L16-17, L50; shap_v2_roberta_pw_s42.jsonl fields n_model_tokens, truncated (truncated = n_tok > 128, Exp_3_0b CELL 2 L95,102)
EVIDENCE: CELL 2: `MIN_WORDS = 6`, `K_HIDE = 3`, `MAX_LENGTH = 128`
CELL 3: `if len(parts) < MIN_WORDS or (vals > 0).sum() < K_HIDE: rows.append({**row, "used": False}); continue`
output: "sentences: 100 | used: 97 | skipped (...): 3 | used and longer than 128 tokens: 4"
CAVEAT: token count = len(tok(text)["input_ids"]) incl. special tokens. Of all 725 test sentences, 34 exceed 128 tokens.

=== G07 + G18 | NOT-FOUND ===
PART STATUS: scale and coding VERIFIED (notebook); text shown to the raters NOT-FOUND
FACTS:
labels and coding (author's notebook text, verbatim): "`2` = makes sense (the words clearly relate to the technique), `1` = partly (some words relate, some do not), `0` = does not make sense (the words are filler or unrelated)."
question: "do these words make sense as evidence for the predicted technique?"
printed when the sheet was built: "scale: 2 = makes sense | 1 = partly | 0 = does not make sense"
SOURCE: Experiments\Exp_3_2_hand_check.ipynb CELL 0 L8-9; CELL 2 L100 + output
EVIDENCE: Exp_3_2_hand_check CELL 2 output "scale: 2 = makes sense | 1 = partly | 0 = does not make sense"
CAVEAT: the workbooks contain only the `rating` sheet (columns no, row, predicted_technique, technique_name, technique_status, technique_description, top_words, sentence_with_top_words_marked, rating, note); no scale text on the sheet. What the raters were told: NOT-FOUND. Study 2 uses a different 1-5 scale (G20).

=== G08 | DECISION ===
PART STATUS: values A, B, C VERIFIED; headline choice DECISION; 14 Nov note vs D24 CONFLICT
FACTS:
A seed-paired: matcher, RoBERTa, SecBERT all from seed s, SVM fixed, z-scored, (3,1,1,1); P@1 per seed 0.7903 / 0.7959 / 0.8028 -> 0.7963 +/- 0.0062 (sd ddof=1); MRR@3 0.8519 +/- 0.0017; registry B12a, B12b
B notebook: matcher seed s, classifiers 3-seed mean; 0.8000 / 0.7986 / 0.8000 -> 0.7995 +/- 0.0008; MRR@3 0.8530; registry B12nb (Exp_2.1 CELL 8 = seed 42 only: 0.800)
C seed-averaged: matcher = z of mean raw scores of 3 seeds, classifiers = mean probability of 3 seeds; P@1 0.8028 [0.7738, 0.8317], MRR@3 0.8556; registry B13a
code: _showcase\src\ttpmap\fusion.py:47 (avg), :48 (nb_seed), :49 (paired), :54-58; values from _showcase\scripts\run_analyses.py:55
04_bootstrap.csv: all 4 rows use mode "avg" (_evidence_pack\scripts\t4_bootstrap.py:8 `Z = components(S, "test", "avg")`, :10-12). C1 fusion C vs classifiers-only (0,1,1,1) avg; C2 fusion C vs matcher 3-seed ens.; C3 RoBERTa 3-seed avg vs SVM; C4 RoBERTa avg vs SecBERT avg
author decision record: _showcase\DECISIONS.md:30 D24 (15 Nov): headline = B13a (C), B12a (A) reported beside it; STATUS.yaml S04 DONE
14 Nov supervisor note: NOT-FOUND (only _showcase\thesis_feed\FUSION_DEFINITIONS.md:36 "the plan says the draft headlines the seed-paired value 0.796"; the master-plan docx is not on disk, only its Word lock file)
supervisor-signed log paper: NOT-FOUND (no file or scan named log/logbook/signed/supervision/meeting in E:\Osamas Paper or Downloads)
SOURCE: _showcase\src\ttpmap\fusion.py:47-58; _showcase\scripts\run_analyses.py:55; _evidence_pack\scripts\t4_bootstrap.py:8-12; _showcase\DECISIONS.md:30; _showcase\thesis_feed\FUSION_DEFINITIONS.md:36; registry B12a, B12b, B12nb, B13a
EVIDENCE: DECISIONS.md:30 "| D24 | Headline fusion number = `B13a` (seed-averaged components, one system, 95% CI); `B12a` (seed-paired, mean +/- sd over seeds 42-44) is reported beside it ..."
FUSION_DEFINITIONS.md:36 "Finding: the plan says the draft headlines the seed-paired value 0.796, but the abstract (p192) and the conclusion (p859) state 0.803 (seed-averaged)."
t4_bootstrap.py:8 `Z = components(S, "test", "avg")`
CAVEAT: CONFLICT: the 14 Nov note (per prompt) says headline = A; D24 (15 Nov) and Thesis_Final-v4 use C. All comparison intervals (C1, C2) and bucket tables use C.
QUESTIONS: Headline: A) 0.796 +/- 0.006 seed-paired, B) 0.800 +/- 0.001 notebook, C) 0.803 seed-averaged? | Which fusion number is on the signed log paper?

=== G09 | CONFLICT ===
FACTS:
recomputed (04_bootstrap.csv rows C3, C4 = _showcase\results\comparisons.csv = registry C3.mrr, C4.mrr): 10,000 resamples, numpy default_rng(20261114), paired percentile bootstrap over 725 test sentences
C3 RoBERTa avg - SVM, dMRR@3: +0.0021 [-0.0184, +0.0216]; thesis v4 (Table 5.4 p741, text p729): +0.002 [-0.018, +0.020] -> hi differs by 0.0016
C4 RoBERTa avg - SecBERT avg, dMRR@3: +0.0016 [-0.0161, +0.0193]; thesis v4 (p744, p729): +0.003 [-0.015, +0.020] -> delta differs 0.0014, lo 0.0011
origin check: C3 thesis interval = nb setting (1,000 resamples, default_rng(0)): [-0.0177, +0.0202] -> rounds to [-0.018, +0.020]. C4 thesis values match no run found (1k rng0 gives +0.0016 [-0.0166, +0.0184]).
v4 P@1 intervals of all 4 rows match the 10k run (e.g. C2 +0.026 [+0.001, +0.051]).
SOURCE: _evidence_pack\04_bootstrap.csv rows C3, C4 (columns delta_MRR@3, mrr_ci_lo, mrr_ci_hi); t4_bootstrap.py:19-26; v4 paragraphs 729, 741, 744
EVIDENCE: C3 "...,0.0020689655172413746,-0.01839080459770115,0.02160919540229885,..."
C4 "...,0.0016091954022988504,-0.01609195402298851,0.019310344827586208,..."
CAVEAT: the number audit flags exactly these three "+0.020" as unregistered (X5). Correct values (3 d.p., as in the table): C3 +0.002 [-0.018, +0.022]; C4 +0.002 [-0.016, +0.019].

=== G10 | VERIFIED ===
FACTS (unseen = gold labels with 0 train sentences; 10 test sentences, 10 (sentence, label) pairs, 10 distinct labels; R@5 = share of the 10 pairs in the top 5):
SVM 0.0 (0/10) | RoBERTa 3-seed avg 0.0 | SecBERT 3-seed avg 0.0 | RoBERTa s42 0.0 | classifiers-only (0,1,1,1) 0.0
matcher s42 0.5 (5/10) | matcher 3-seed ens. 0.6 (6/10) | matcher zero-shot 0.6
fusion (3,1,1,1) seed-avg 0.5 (5/10) | fusion nb (matcher s42) 0.4 | fusion seed-paired s42 0.4
P@1 on the 10 sentences: classifiers 0/10; matcher s42 1/10; matcher 3-seed ens. 2/10; zero-shot 3/10; every fusion 0/10
the system with 0.0: every classifier and the classifiers-only ensemble (they cannot rank unseen labels)
SOURCE: recompute with _showcase\src\ttpmap (rank_topk stable ties); _showcase\results\systems.csv column unseen_R@5; registry G6.unseen_r5_fusion 0.5, G6.unseen_r5_clsonly 0.0, G6.unseen_r5_matcher 0.6; 05_rarity_buckets.csv row "unseen (0)" (P@1 only)
EVIDENCE: systems.csv unseen_R@5: "Frequency prior 0.0 | TF-IDF + SVM 0.0 | RoBERTa (3-seed avg) 0.0 | SecBERT (3-seed avg) 0.0 | Classifiers-only ens. 0.0"
"Matcher zero-shot 0.6 | Matcher (3-seed ens.) 0.6 | Fusion equal (1,1,1,1) 0.0 | Fusion (3,1,1,1) 0.5"
CAVEAT: 05_*.csv hold P@1, not R@5. Fusion 0.5 is below the matcher ensemble 0.6; "rises from 0.0" holds only against the classifiers. Exp_2.1 CELL 8 (matcher s42): matcher 0.5, fusion 0.4.

=== G11 | VERIFIED ===
FACTS: matcher column = 3-seed ensemble ("Matcher (3-seed ens.)" = z-score of the mean raw scores of seeds 42-44); fusion = seed-averaged (3,1,1,1)
SOURCE: _showcase\scripts\run_analyses.py:19, :23-24 (SYS), :111 (MAIN), :113-120 (buckets); _evidence_pack\scripts\t5_errors.py:3, :17
EVIDENCE: run_analyses.py:19 `Z = components(S, "test", "avg")`; :23 `"Matcher (3-seed ens.)": Z["matcher"]`; :24 `"Fusion (3,1,1,1)": fuse(Z, (3, 1, 1, 1))`
t5_errors.py:3 "matcher 3-seed ensemble; fusion (3,1,1,1) seed-averaged; plus classifiers-only as a reference column."
CAVEAT: bucket 1-4: 34 sentences, fusion 0.294 vs matcher 0.559 (registry G4.fusion.1_4, G4.matcher.1_4).

=== G13 | NOT-FOUND ===
PART STATUS: paper split files, code, predictions NOT-FOUND; comparability verdicts NOTES-ONLY (08_baseline.md, paper read online 14 Nov); ATT&CK id set VERIFIED (attack_version.csv)
FACTS (08_baseline.md:48-55):
test set: UNKNOWN (probably same): 725 = 15.1% of 4,797; totals 4,797 and 193 labels equal the paper; no hash/row comparison possible
ATT&CK version: paper states v12.0; our 737 description ids = v12.1 STIX id set exactly, median text similarity 0.959 (_showcase\results\attack_version.csv) -> SAME major version, minor UNKNOWN
label set: SAME for the 193-label TRAM inventory; candidate set size of the paper UNKNOWN
metric definitions: SAME for P@1 and MRR@3; DIFFERENT for R@1 (paper per sample; notebooks hits / all gold)
also: training data UNKNOWN, possibly DIFFERENT (paper "separate" vs "combined" mode); technique-level 0.903 NOT COMPARABLE
local: paper PDF NOT-FOUND (read online from arXiv:2401.10337 on 14 Nov, WEB); their code, predictions, split files NOT-FOUND
SOURCE: _evidence_pack\08_baseline.md:5-11, 48-55; _showcase\THESIS_PLACEHOLDERS.md:161-166
EVIDENCE: 08_baseline.md:50 "| test set | 725 sentences, `Dataset/tram_test.tsv` | 15% stratified split of 4,797 TRAM texts (15% = 720; our 725 = 15.1%) ..."
CAVEAT: label granularity: both use exact technique/sub-technique ids (NOTES-ONLY, paper Table 2 vs Table 3).

=== G14 | VERIFIED ===
PART STATUS: extended grid = sensitivity run on saved dev probabilities; not used for selection
FACTS:
nb grid: PROB_GRID = np.arange(0.1, 0.9, 0.05) -> 0.10 to 0.85, step 0.05, 16 values; rule = first maximum of dev micro-F1 of (probs >= t)
extended (same step, to 0.99) -> 0.10 to 0.95, 18 values; dev probabilities saved for all seeds
roberta_pw_s42: selected 0.90 (changes); dev micro-F1 0.7311 at 0.85, 0.7315 at 0.90 (0.7289 at 0.95)
roberta_pw_s43: selected 0.85 (no change); dev 0.7234 | roberta_pw_s44: 0.85 (no change); dev 0.7379
sensitivity only, not used for selection: roberta_pw_s42 test micro-F1 0.7077 at 0.85, 0.7074 at 0.90
SecBERT (not on the grid edge): 0.75 / 0.65 / 0.70, unchanged
SOURCE: Exp_1_4_tram_30ep_3seeds.ipynb CELL 8 L7 + L97, CELL 4 L17-23; Exp_1_4_run_tram_2_epoc_30\*_pw_s*\dev_probs.npy, dev_labels.npy, metrics.json "threshold"
EVIDENCE: Exp_1_4_tram_30ep_3seeds CELL 8 L7 `PROB_GRID = np.arange(0.1, 0.9, 0.05)`
CAVEAT: _showcase\results\threshold_grid.csv used step 0.01 (0.10-0.99) and full-space F1: roberta s42 0.93, s43 0.83, s44 0.88; test micro-F1 change <= 0.003.

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

=== G20 | NOT-RUN ===
FACTS:
returned repeat-study sheets: none. _showcase\human_study\returned\ holds only raters_TEMPLATE.csv (14 Nov 18:04, empty rows R1-R2...)
sent kits: _showcase\human_study\TO_SEND\rater_R1.zip, rater_R2.zip, rater_R3.zip (16 Nov 01:19); each = rating_sheet_Rn.csv, READ_FIRST_instructions.md, worked_examples.md, raters.csv
no returned copy anywhere in E:\Osamas Paper or Downloads (search rating_sheet*)
instruction sheet: _showcase\docs\RATER_INSTRUCTIONS.md = READ_FIRST_instructions.md in each zip (sha256 aeee52ee5ad02a9a identical); full text in APPENDIX G20 at the end of this file
SOURCE: directory listing of _showcase\human_study\{returned,TO_SEND}; search for rating_sheet* in E:\Osamas Paper and %USERPROFILE%\Downloads; sha256 of RATER_INSTRUCTIONS.md and the zip members
EVIDENCE: returned\ holds 1 file: raters_TEMPLATE.csv (14 Nov 18:04)
CAVEAT: scale 1-5 (not the 0-2 scale of study 1); some rows mark random words (controls). Agreement statistics: NOT-RUN (no data).

=== G21 | NEEDS-AUTHOR ===
FACTS:
.git roots: one, E:\Osamas Paper\.git; `git remote -v`: origin -> github.com/<personal account, withheld>/ttp-thesis-showcase.git (fetch, push); local main is 17 commits ahead of origin/main
the remote URL and the commit author are the PC user's personal identity: do not use this URL in the thesis
publishable manifest: _showcase\gap_answers\publish_manifest.csv (376 tracked files; 373 kept, 10.48 MB; columns file, bytes, excluded_flag, review_note)
excluded (G03): _evidence_pack/05_errors.md, _evidence_pack/06_shap.md, _showcase/tests/test_fusion_stats_schema.py
excluded (G04 rater data): none tracked (07_human.md and 07_agreement.csv hold only aggregates, roles and hash prefixes)
review by eye: _evidence_pack/fig_shap_ex1-3.png, _showcase/figures/fig14_shap_examples.png/.svg (may show sentence words)
SOURCE: git remote -v; git ls-files; git ls-tree origin/main
EVIDENCE: `git status -sb` -> "## main...origin/main [ahead 17]"
CAVEAT: no commit or push made; the 2 G03 files are already on origin/main, so leaving them out of a new copy does not remove them from the existing remote.
QUESTIONS: Repository URL for Appendix C, or confirm a new public repository will be created (under whose account) and from which folder?

=== G22 | NEEDS-AUTHOR ===
FACTS: supervisor's additional references: NOT-FOUND (no .bib/.ris, reference list, note, mail or message file; only the open item _showcase\CHANGELOG_v2.4.md:76 "p337: additional references recommended by the supervisor")
v4 sentence: paragraph 942 (Achievement and Objectives) "...it should be extended with the supervisor's additional references."
SOURCE: _showcase\CHANGELOG_v2.4.md:76; Thesis_Final-v4.docx p942; search of E:\Osamas Paper and %USERPROFILE%\Downloads for .bib, .ris and reference-list files
EVIDENCE: CHANGELOG_v2.4.md:76 "- p337: additional references recommended by the supervisor."
CAVEAT: none.
QUESTIONS: Paste the supervisor's additional references, or confirm there are none (then the sentence is deleted)?

=== X1 | VERIFIED ===
FACTS:
P@1 / MRR@3 (_showcase\src\ttpmap\metrics.py):
:20-22 `def rank_topk(scores, k): return np.argsort(-scores, axis=1, kind="stable")[:, :k]`  (ties: lower label index first)
:25-28 `def hit_at_1(scores, Y): top = rank_topk(scores, 1)[:, 0]; return Y[np.arange(len(Y)), top].astype(float)`  (hit if top-1 is any gold label)
:36-40 `def rr_at_k(scores, Y, k=3): hits = np.take_along_axis(Y, rank_topk(scores, k), axis=1); first = hits.argmax(1) + 1; return np.where(hits.any(1), 1.0 / first, 0.0)`  (k = 3; 0 if no gold in top 3; multi-label: first gold counts)
z-score and fusion (fusion.py):
:33-36 `def zrow(F): m = np.nanmean(F, axis=1, keepdims=True); s = np.nanstd(F, axis=1, keepdims=True) + 1e-9; return np.nan_to_num((F - m) / s, nan=0.0)`  (per sentence, over the labels the model knows; unknown labels -> 0)
:52 `Z = {"svm": zrow(to_full(S.svm_raw[split], S.seen_idx, L))}`
:57 classifiers avg `zrow(np.mean([to_full(S.cls_raw[tag, s][split], ...) for s in SEEDS], axis=0))`  (seed averaging = mean probability, then z)
:58 matcher `zrow(np.mean([S.matcher_raw[s][split] for s in SEEDS], axis=0)) if mode == "avg" else zrow(S.matcher_raw[seed][split])`
:20 `ORDER = ("matcher", "svm", "roberta", "secbert")`; :62-63 `def fuse(Z, w): return sum(wi * Z[n] for wi, n in zip(w, ORDER))`
bootstrap / McNemar (stats.py):
:9-10 `BOOT_N = 10_000`, `BOOT_SEED = 20261114`
:24-30 `d = a - b; rng = np.random.default_rng(seed); bs = d[rng.integers(0, len(d), (n_boot, len(d)))].mean(1)`; CI = quantiles 0.025 / 0.975 (paired, unit = sentence); p_boot = 2*min(P(bs<=0), P(bs>=0))
:33-38 `b_ = (a & ~b).sum(); c_ = (~a & b).sum(); p = binomtest(b_, b_ + c_, 0.5).pvalue`  (exact two-sided McNemar)
SOURCE: _showcase\src\ttpmap\metrics.py:20-40; fusion.py:20-63; stats.py:9-38
EVIDENCE: the raw code lines are quoted in FACTS
CAVEAT: Exp_2.1 nb used np.argsort default (not stable) and 1,000 resamples default_rng(0); P@1 values are identical (registry), CIs differ slightly.

=== X2 | VERIFIED ===
FACTS: shap 0.54.1; `shap.Explainer(f, shap.maskers.Independent(np.zeros((1, n))), algorithm="permutation", seed=42)` (permutation explainer); max_evals = 40 * (2n + 1) = 40 permutations; background = all-zeros mask vector = every word replaced by <mask>; f = logit of the top-1 label of roberta_pw_s42 (Exp_1_4_run_tram_2_epoc_30\roberta_pw_s42, fine-tuned from roberta-base); unit = whitespace-delimited word, surrounding whitespace kept; max_length 128; output Exp_3_0_shap\shap_v2_roberta_pw_s42.jsonl
SOURCE: Exp_3_0b_shap_all_725.ipynb CELL 0 L2, CELL 1, CELL 2 L8-13, L87-102
EVIDENCE: method block in every record: {'unit': 'whitespace-delimited word', 'masking': 'word replaced by <mask>, surrounding whitespace kept', 'algorithm': 'permutation', 'n_perm': 40, 'shap_seed': 42, 'output': 'logit of the top-1 predicted label', 'max_length': 128}
CAVEAT: explains RoBERTa s42 only; SHAP of the fused score = G15 / Z1.

=== X3 | VERIFIED ===
FACTS: path E:\Osamas Paper\Exp_3_0_shap\shap_v2_roberta_pw_s42.jsonl; 725 rows; mtime 2026-11-12 23:22; sha256 2075dd6a418c0798... (identical copy _showcase\drive_upload\KDU\Thesis\Exp_3_0_shap\)
columns: row, text, units, shap_values, base_value, pred_label, pred_prob, pred_logit, gold_labels, top1_correct, additivity_error, n_model_tokens, truncated, method
written by: Exp_3_0 (first 100 rows, v2 method, 40 permutations) then Exp_3_0b_shap_all_725 (rows 101-725, same method; appends, refuses other settings). All 725 records carry the same v2 method block.
older files (not v2): shap_roberta_pw_s42.jsonl (20 rows, 7 Nov 11:48, no method block), shap_v1_roberta_pw_s42.jsonl (100 rows, 10 permutations, 7 Nov 12:52)
"replaced 5-line script": NOT-FOUND as a file; nothing on disk wrote a 725-row SHAP file except Exp_3_0b
app replay: ttp_app\core.py:414 loads "Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl" (the v2 file) and core.py:431 the Kaggle fusion file results\colab\fusion_shap\fusion_shap_full_s42.jsonl: VERIFIED.
SOURCE: Exp_3_0_shap\*.jsonl (row counts, method field, sha256); Experiments\Exp_3_0_shap.ipynb, Exp_3_0b_shap_all_725.ipynb; ttp_app\core.py:414, :431
EVIDENCE: core.py:414 `shap_p = _find(root, "Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl")`
core.py:431 `fp = res / "colab" / "fusion_shap" / "fusion_shap_full_s42.jsonl" if res else None`
CAVEAT: the jsonl holds the words of the test sentences (G03); keep it out of shared copies.

=== X4 | VERIFIED ===
FACTS: deletion_test_v2_roberta_pw_s42.csv: 100 rows, 100 unique row ids, used 97, used and <= 128 tokens 93 (10 Nov 19:36)
mask: top 12.656, random 2.466, diff 10.189 [9.317, 11.041]; remove: 12.768, 2.643, 10.125 [9.229, 11.004]; top-3 larger 93 of 93 in both
CI: percentile bootstrap of the paired difference, 1,000 resamples, RandomState(42) shared by mask then remove (Exp_3_1 CELL 3 L38-45); 20 random 3-word sets per sentence, RandomState(42 + row)
old-claim search: "645", "644 of 645", "10.13" appear in every draft, all in section "Explanation Faithfulness": v4 p831, v3_Corrected p803, v2.2_identity p768, v2.5 p792, v2.4 p768, v2.3 p768, root Thesis_Draft_v2.2 p768
these are the all-725 run, not errors: _evidence_pack\06_deletion_test_725.csv: 645 eligible (679 used, 34 over 128 tokens), mask diff 10.1315, 644 of 645 (registry E2.all, E3.all); remove 10.094, 642 of 645
SOURCE: Exp_3_0_shap\deletion_test_v2_roberta_pw_s42.csv (recompute); Experiments\Exp_3_1_deletion_test.ipynb CELL 3 L38-45; _evidence_pack\06_deletion_test_725.csv; text scan of 7 draft docx files (2026-11-21)
EVIDENCE: v4 p831 "On all 645 eligible test sentences the difference is 10.13 logits, in the expected direction for 644 of 645."
CAVEAT: the 725 run was computed on CPU on 14 Nov by _evidence_pack\scripts\t6_shap.py from the same SHAP file; it is a separate claim from the 93-sentence result.

=== X5 | VERIFIED ===
FACTS: audit_numbers.py on %USERPROFILE%\Downloads\Thesis_Final-v4.docx, registry thesis_numbers.json + configs\number_whitelist.txt; output _showcase\gap_answers\number_audit_v4\
registry numbers 1,111; checked 885; registered 552, ignored 200, allowed 94, UNREGISTERED 39 (31 decimal, 6 int >= 10, 2 percent); highlighted placeholders 0
unregistered, real problems: +0.020 at p729, p742, p745 (G09 MRR intervals)
unregistered, literature values (not in registry): p352/p374 24.8; p354 39,296; p355 92.42%; p363 6,612; p364 57.83% and 8.9 (E3_REPORT.md: 57.83% unconfirmed); p375 0.674; p226 401 sub-techniques
unregistered, harmless: equation numbers (2.3) (2.5) (3.2) (3.3) (3.4) and section refs 3.6 / 3.4 / 2.3 in the body and Appendix E list; 768 (bge vector size, p322, p1063); 2.5th / 97.5th percentiles (p545, p1146); front matter: student ID (value withheld)
words: body text 9,872; body incl. tables and captions 12,088
SOURCE: _showcase\gap_answers\number_audit_v4\audit_ledger.csv, audit_report.md (audit_numbers.py run 2026-11-21)
EVIDENCE: audit_ledger.csv "+0.020,decimal,UNREGISTERED,body,742,yes,+0.002 [−0.018, +0.020]"
"+0.020,decimal,UNREGISTERED,body,745,yes,+0.003 [−0.015, +0.020]"
CAVEAT: audit_numbers.py numbers table paragraphs one higher than G09 (p742/p745 here = p741/p744 in G09); same cells, same values.

=== X6 | VERIFIED ===
FACTS (number -> thesis_numbers.json id):
K1: 604 A2.dev | 255 B14.coarse_n | 1711 B14.wide_n | 28 B14.rank3111 | 30 NOT-FOUND | 0.800 B14.test3111, B12nb | 0.804 B14.test4111
K2: 93 E3.n (and E3 "93 / 93") | 10.189 E2 | 20, 12.656, 2.466, 9.317, 11.041, 12.768, 2.643, 10.125, 9.229, 11.004: NOT-FOUND
K3: 0.062 D4 | 0.133 D4.lin | 0.236 NOT-FOUND | 0.49 D6 | -0.057 D1 | 0.031 D2 | -0.062 D3
K4: 0.796 B12a | 0.006 sd: NOT-FOUND as its own id | 0.800 B12nb | 0.001 sd: NOT-FOUND | 0.803 B13a
K5: unseen P@1 fusion 0.0 G4.fusion.unseen; matcher 0.2 G4.matcher.unseen; unseen R@5 0.5 G6.unseen_r5_fusion; 0.0 G6.unseen_r5_clsonly; 0.6 G6.unseen_r5_matcher; 0.294 G4.fusion.1_4; 0.559 G4.matcher.1_4
G09: C3.mrr (0.0021 [-0.0184, 0.0216]), C4.mrr (0.0016 [-0.0161, 0.0193]); thesis +0.020 and C4 +0.003 / -0.015: NOT-FOUND
G15: 108 E4; 0.149 E4.share; retrained matcher 0.7462 T1.matcher_retrained_p1; fused deletion 2.907 T2.full_fusion_shap
SOURCE: _showcase\thesis_numbers.json (649 claims; field id)
EVIDENCE: {"id": "B14.rank3111", "label": "Dev rank of (3,1,1,1) on the wide grid", "value": 28, "display": "28", "ci": null, "definition": "rank by dev MRR@3 then dev P@1", ...}
CAVEAT: matching is rounding-aware on value and ci fields, filtered by label keywords.

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

=== APPENDIX G20: full text of _showcase\docs\RATER_INSTRUCTIONS.md (= READ_FIRST_instructions.md) ===
# Instructions for raters (one page)

Thank you for helping. This takes about 45 to 60 minutes. You can stop and continue later.

## What you see

Each row of your sheet shows:
- a sentence from a cyber-threat report;
- a MITRE ATT&CK technique that a computer model predicted for this sentence, with its name and the first sentence of its official description;
- three words in the sentence marked like this: [[word]].

## Your task

For each row, answer one question:

> If you had to justify the predicted technique to a colleague using only the marked words, how well would they serve as evidence?

Write a whole number from 1 to 5 in the column `rating_1_to_5`.

| rating | meaning |
|---|---|
| 5 | All three marked words are direct evidence for the technique. They name the action, tool or object that defines it. |
| 4 | Two marked words are direct evidence. The third is neutral. |
| 3 | One marked word is direct evidence, or the words are only loosely related to the technique. |
| 2 | The marked words are general security words that would fit many techniques. |
| 1 | The marked words are filler (such as "a", "the", "to", names) or point to a different technique. |

## Rules

- Rate the marked words as evidence for the **predicted** technique, even if you think the prediction is wrong. If you think it is wrong, write that in the `note` column.
- Judge only the marked words. Other words in the sentence do not count.
- Some rows mark words chosen at random. This is on purpose. Rate them the same way.
- Work alone. Do not discuss rows with other raters until everyone has sent their sheet.
- Do not change the order of rows, the `item_id` column or any column except `rating_1_to_5` and `note`.
- If a row is unclear, still give your best rating and explain in `note`. Leave a rating empty only if you cannot judge at all.

## Two worked examples

Your sheet comes with a page of two worked examples (one rated 5, one rated 1). Read it before you start.

## When you are done

Save the file as CSV with the same name and send it back. Also fill in one row of the short background form (`raters.csv`): your role, years in security,
whether you work with threat intelligence, how familiar you are with ATT&CK (1 to 5), and how many minutes the rating took.
We store only your role and your answers. We do not store your name. You may withdraw your sheet at any time.

=== SUMMARY TABLE ===
ID | STATUS | answer (max 12 words)
STEP0 | VERIFIED | All found; v4 only in Downloads, without highlighted gaps
K1-K5 | CONFLICT | K1-K3 verified; K4 note not found; K5 matcher ensemble 0.6
G01 | NEEDS-AUTHOR | (3,1,1,1) rank 28 (tie to 30); no written reason found
G02 | VERIFIED | Whole word replaced by "<mask>", whitespace kept; Remove deletes word
G03 | CONFLICT | 3 tracked files hold dataset sentences; 2 already on remote
G04 | NEEDS-AUTHOR | Roles A/B/C, 100/100/3 rows; study-1 consent text not found
G05 | NEEDS-AUTHOR | No university policy file; README fallback sentence found
G06 | VERIFIED | >=6 words, >=3 positive SHAP, <=128 tokens: 100-3-4=93
G07 | NOT-FOUND | Scale 2/1/0 verified; text shown to raters not found
G08 | DECISION | A 0.796, B 0.800, C 0.803; D24 chose C
G09 | CONFLICT | C3 hi 0.022 not 0.020; C4 +0.002 [-0.016, +0.019]
G10 | VERIFIED | 0.0 = classifiers; fusion 0.5; matcher ensemble 0.6
G11 | VERIFIED | Matcher = 3-seed ensemble; fusion = seed-averaged
G12 | VERIFIED | Same rule as G06; 93 of 93
G13 | NOT-FOUND | Paper split files absent; test UNKNOWN, version v12, metrics SAME
G14 | VERIFIED | Extended grid: s42 picks 0.90 (+0.0004 dev F1); s43, s44 stay 0.85
G15 | VERIFIED | Kaggle s42 retrain + fusion SHAP verified; s43/s44 not run
G16 | NOT-FOUND | Local + 16 Nov envs verified; revisions, training env not found
G17 | NEEDS-AUTHOR | Rebuild 3,468 rows, 180 labels; original hash not found
G18 | NOT-FOUND | Same as G07; sheet text not found
G19 | VERIFIED | RandomState(42) permutation, first 100; no strata, no controls
G20 | NOT-RUN | Repeat-study sheets not returned; instructions printed
G21 | NEEDS-AUTHOR | Existing remote is personal; 373 files publishable
G22 | NEEDS-AUTHOR | Supervisor references not found in any file
X1 | VERIFIED | Code lines printed for P@1, MRR@3, z, fusion, bootstrap
X2 | VERIFIED | Permutation SHAP, 40 perms, <mask> background, seed 42
X3 | VERIFIED | 725-row v2 file by Exp_3_0 + Exp_3_0b
X4 | VERIFIED | K2 exact; 645/644/10.13 = 725-run claims, all drafts
X5 | VERIFIED | 39 unregistered; real issue = three +0.020 (G09)
X6 | VERIFIED | Most ids found; deletion detail numbers unregistered
X7 | VERIFIED | 17 open ledger lines mapped to G-blocks
Y1 | CONFLICT | Local v4: 0 gaps; colons/semicolons/hyphens stripped; URLs broken
Z1 | VERIFIED | Kaggle matcher s42 + fusion SHAP verified; Drive s45 partial only

=== QUESTIONS FOR THE AUTHOR (NEEDS-AUTHOR / DECISION) ===
1. Why was (3,1,1,1) kept after the finer grid? (fixed in advance / within noise / simpler integers / other)
2. Headline fusion: A 0.796 +/- 0.006 seed-paired, B 0.800 +/- 0.001 notebook, or C 0.803 seed-averaged?
3. Which fusion number is on the supervisor-signed log paper?
4. Relationship of Rater A, B, C to the project (member / peer / external)?
5. Is any rater the thesis author (yes/no; which role)?
6. How was consent obtained in study 1 (written / message / in the sheet)?
7. AI tools used and stages (code review / scripts / drafting / figures), and who checked outputs?
8. Supervisor: required AI-use declaration wording and its place in the thesis?
9. Repository URL for Appendix C, or confirm a new public repository and the folder?
10. Supervisor's additional references (paste), or confirm none so the sentence is deleted?
11. Which file/revision of tumeteor/Security-TTP-Mapping is Dataset\combined_train.csv?
12. Was ethics approval required for the rater study (supervisor answer yes/no)?

Upload _showcase\gap_answers\GAP_ANSWERS.md instead of pasting if the terminal text is cut off.
