THESIS GAP ANSWERS - PART 7/10 - 2026-11-21
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
