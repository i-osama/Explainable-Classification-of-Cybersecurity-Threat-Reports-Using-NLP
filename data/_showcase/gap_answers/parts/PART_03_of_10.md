THESIS GAP ANSWERS - PART 3/10 - 2026-11-21
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
