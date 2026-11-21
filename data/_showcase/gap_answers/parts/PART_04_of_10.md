THESIS GAP ANSWERS - PART 4/10 - 2026-11-21
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
