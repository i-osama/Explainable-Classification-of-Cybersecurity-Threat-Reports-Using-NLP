THESIS GAP ANSWERS - PART 2/10 - 2026-11-21
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
