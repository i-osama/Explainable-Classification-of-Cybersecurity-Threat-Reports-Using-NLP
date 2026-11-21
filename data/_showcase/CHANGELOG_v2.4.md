# Changelog: Thesis_Draft_v2.3.docx -> Thesis_Draft_v2.4.docx (16 Nov 2026)

All changes are Word tracked changes (author "Claude"); review them with Review > Accept / Reject. v2.3 is unchanged.
Every new value comes from `thesis_numbers.json` (id in the last column), the experiment notebooks, or `DECISIONS.md`.

Result: highlighted placeholders 52 -> 13 (all 13 need the author); unregistered numbers 11 -> 10; intervals differing from the registry 0 of 20; QA gates 9/9.

## Corrections beyond the placeholders

- p357, p423: "(3,1,1,1) ranks thirtieth" -> "28th" (`B14.rank3111` = 28, ranked by dev MRR@3 then dev P@1).
- p676, p854: Holm correction is over the pre-registered family of **eight** tests, not four; adjusted p = 0.190 (`C2.holm`).
- p741: unseen-label R@5 "from 0.0 to 0.5" compared the fusion with the classifiers-only ensemble; against the matcher ensemble the fusion is lower (0.60 -> 0.50; `G6.*`).
- p637: headline definition aligned with the abstract and `FUSION_DEFINITIONS.md`: headline = seed-averaged fusion 0.803 (`B13a`); seed-paired values show the variation across seeds.
- p323: "P@1 57.83%" is not in Kumarasinghe et al. (RELATED_WORK_VERIFIED, ref 11); replaced by the confirmed "top-3 recall of 81% over 193 top-level techniques".
- p197 (no change needed): "14 tactics, 193 techniques and 401 sub-techniques" for ATT&CK v12 is correct. Counted from the official v12.1 STIX bundle `_evidence_pack/external/enterprise-attack-12.1.json` (active objects: 14 / 193 / 401). The "196 / 411" in Nguyen et al. does not match v12.

## Every change

| para | removed | inserted | source |
|---|---|---|---|
| 192 |  [confirm upper bound] | (deleted) | C2 CI upper bound 0.051 confirmed |
| 192 | (none) | ; Holm-adjusted p = 0.190 | C2.holm (family of 8, prereg 01) |
| 323 | P@1 57.83% on its own data | Top-3 recall of 81% over 193 top-level techniques | RELATED_WORK_VERIFIED ref 11: 57.83% not found in the paper; top-3 recall 81% over 193 techniques confirmed |
| 334 | (none) |  [8] | RELATED_WORK_VERIFIED: 0.674 confirmed in ref [8] Table 2, keep with citation |
| 357 | thirtieth | 28th | B14.rank3111 = 28 (dev MRR@3 then dev P@1) |
| 357 |  [confirm that the choice was fixed before the finer grid was run and state why it was kept] | ; in the notebook record the 255-vector grid was searched first, the 1,711-vector grid second, and the weights were fixed at (3, 1, 1, 1) in a later cell, so the record does not show that the choice preceded the finer grid. With matcher seed 42 the test P@1 is 0.800 for (3, 1, 1, 1) and 0.804 for (4, 1, 1, 1) [author: state why (3, 1, 1, 1) was kept] | Exp_2.1 cell order (Cell 7 grid 255, Cell 8 wider grid, Cell 10 fixed (3,1,1,1)); B14.test3111, B14.test4111 |
| 392 |  [confirm whether duplicates were removed from the training portion] | ; the training portion was de-duplicated on exact text, and its size before de-duplication is not recorded | A2 (train after exact-text de-duplication); N8.pre_dedup_size NOT-FOUND |
| 395 |  [confirm n-gram range, regularisation constant and one-vs-rest setup] | , with TF-IDF features of word unigrams and bigrams (sublinear term frequency), a regularisation constant C = 1.0 and one binary classifier per technique (one-vs-rest) | Exp_0/Exp_1 notebooks and src/ttpmap/data.py: TfidfVectorizer(ngram_range=(1,2), sublinear_tf=True), OneVsRest(LinearSVC(C=1.0)) |
| 395 |  [confirm exact checkpoint name] |  (checkpoint BAAI/bge-base-en-v1.5) | Exp_2.1 BASE_MODEL |
| 395 |  [confirm number of epochs and negative sampling] | : at most 20 epochs with early stopping after four epochs without improvement on the development set, a contrastive loss, and 64 negative descriptions sampled for each batch of 16 sentences | Exp_2.1 train_matcher(epochs=20, patience=4, batch_size=16, n_neg=64) |
| 395 |  for 20 epochs | (deleted) | duplicate of the ft20 settings sentence |
| 423 | thirtieth | 28th | B14.rank3111 = 28 |
| 423 |  [confirm the order of the two searches] |  (the 255-vector grid was searched first and the 1,711-vector grid second) | Exp_2.1 Cell 7 then Cell 8 |
| 423 |  [weight-sensitivity analysis pending] | : the ten best development settings reach a test P@1 between 0.781 and 0.800 on the 255-vector grid and between 0.797 and 0.806 on the 1,711-vector grid (matcher seed 42; test values are reported and were never used for selection) | B14.top10_coarse, B14.top10_wide |
| 457 | 20 epochs; descriptions of 128 tokens (256 in the ablation) [confirm] | At most 20 epochs (early stopping after four epochs without improvement); descriptions truncated at 128 tokens in training and 256 tokens at scoring (256 in training in the ablation) | Exp_2.1: epochs=20, patience=4, label_max_len_train=128, label_max_len_eval=256; ablation label_max_len_train=256 |
| 502 |  [confirm the seed] |  (NumPy default_rng(20261114)) | C2 definition |
| 528 |  [confirm the exact masking procedure and the number of removed tokens] | . In this test, words are whitespace-delimited, removing a word means replacing it with the tokenizer’s mask token, three words are removed, and the random baseline is the mean drop over 20 random sets of three words | E1 method block; E2 definition |
| 580 |  [confirm loss function and negative sampling] | . The loss is the negative log of the softmax of each gold description’s score against the negative descriptions, with cosine similarities scaled by 30; for each batch of 16 sentences, 64 negative descriptions are sampled without replacement from all descriptions that are not gold for any sentence in the batch | Exp_2.1 lines: loss = softplus(lse_neg - s_pos) (= -log softmax), scale=30.0, negs = rng.choice(cand, 64, replace=False), cand = pool minus batch gold |
| 580 | (none) | ; at scoring time, descriptions are cut at 256 tokens in both variants | Exp_2.1 label_max_len_eval=256 |
| 580 | 20 epochs | at most 20 epochs | Exp_2.1 patience=4 early stopping |
| 584 |  [confirm the sampling rule for the 100 sentences and the eligibility rule that leaves 93] | : the first 100 rows of a fixed random permutation of the 725 test sentences (NumPy RandomState(42)); a sentence is eligible for the deletion test if it has at least six words, at least three words with a positive SHAP value and no truncation, which leaves 93 | DECISIONS D10; E3 / E3.n definitions |
| 584 |  [confirm the rating scale] |  (2 = the highlighted words make sense for the technique, 1 = partly, 0 = they do not make sense) | Exp_3_2_hand_check scale; D1 (scale 0-2) |
| 633 | [add] | 0.543 | B3.macro117 |
| 634 | [add] | 0.500 | B3.macro127 |
| 635 |  Macro-F1 values for the SVM are to be added from the analysis notebook. | (deleted) | values now in the table |
| 637 |  [confirm the second equal-weight figure of 0.782 and its basis] | , and 0.782 (95% interval 0.750 to 0.812) with the same seed-averaged components as the headline fusion | B11, B11.avg |
| 637 | the seed-paired value is used as the headline [author to confirm the headline definition] | the seed-paired values are reported to show the variation across seeds, and the headline is the seed-averaged fusion (P@1 0.803, 95% interval 0.774 to 0.832) | FUSION_DEFINITIONS.md: headline = seed-averaged B13a (as in the abstract) |
| 676 |  [confirm upper bound] | (deleted) | C2 CI |
| 676 |  [confirm] | (deleted) | C2.mrr CI |
| 676 | would not remain significant after a Holm correction for the four comparisons made [confirm with the adjusted p-value] | does not remain significant after a Holm correction over the pre-registered family of eight tests (adjusted p = 0.190) | C2.holm |
| 693 |  [confirm the upper bound and the MRR@3 interval from the recomputation] |  and an upper bound of +0.051, and its MRR@3 interval is +0.003 to +0.036 | C2 CI, C2.mrr CI |
| 697 | one exact match to training and one near-duplicate [confirm the set removed] | test rows 59 and 124: one exact match to training and one near-duplicate with a token-set Jaccard similarity of at least 0.90 | G12.exact_near (ids 59;124), A6 definition |
| 697 | their effect was not re-evaluated at a longer length [optional: re-evaluate at 256 tokens] | re-running inference at 256 tokens on these sentences, with the models still trained at 128, gives no gain (RoBERTa seed 42 ranks a gold label first in 19 of 34 at 128 tokens and 17 at 256; SecBERT seed 42 in 20 and 20); training at 256 tokens was not tested | G11.roberta, G11.secbert (results/maxlen.csv) |
| 703 |  [confirm set] |  (rows 59 and 124) | G12.exact_near |
| 741 | Fusion raises the recall of the unseen labels at rank five from 0.0 to 0.5 only [confirm the reference system for 0.0]. | At rank five, the fusion finds 0.50 of the ten unseen gold pairs, against 0.60 for the matcher ensemble and 0.00 for the classifiers-only ensemble, which cannot output unseen labels. | G6.unseen_r5_fusion / _matcher / _clsonly |
| 757 | [pending] | 0.646 | G4.matcher.5_19 |
| 758 | [pending] | 0.667 | G4.fusion.5_19 |
| 767 | [confirm whether the three-seed ensemble or seed 42] | three-seed ensemble | G4 labels: Matcher (3-seed ens.) |
| 767 | (none) |  (30 and 66 sentences) | G4.n.5_9, G4.n.10_19 |
| 767 |  [insert from the support-bucket results] |  and merged here as sentence-weighted means, without an interval because they were merged after the fact | G4.*.5_19 definition |
| 769 |  [confirm the definition of the 10.19 difference and the eligibility rule behind 93] |  (10.19 is the mean, over eligible sentences, of the logit drop after masking the three highest-SHAP words minus the mean drop over 20 random three-word sets; a sentence is eligible if it has at least six words, at least three words with a positive SHAP value and no truncation, which leaves 93 of the 100) | E2, E3.n definitions |
| 817 | [pending: weight-sensitivity analysis] | 0.804, against 0.800 for (3, 1, 1, 1) with the same matcher seed 42; over the ten best development settings of the finer grid the test P@1 ranges from 0.797 to 0.806 | B14.test4111, B14.test3111, B14.top10_wide |
| 820 |  [confirm that the test split and label granularity are identical to those of the published evaluation] | ; this could not be confirmed, because the published method was not re-run on the present split | DO_NOT_CLAIM (baseline not re-run; split unverified); T5.baseline_same_protocol pending |
| 848 | so a wider grid might select a higher value [extended-grid analysis pending] | but an extended grid (0.10 to 0.99 in steps of 0.01) selects 0.93, 0.83 and 0.88 and changes the mean test micro-F1 by −0.0006, so the grid edge has no material effect | G3.roberta.thr_old/thr_new/delta (results/threshold_grid.csv) |
| 852 | at all [full-fusion explanations pending] | by them. A pre-registered SHAP analysis of the full fusion with the retrained matcher (seed 42) was run on the 100-sentence sample: removing its three highest-attributed words lowers the fused score by 2.907 logit-z units more than removing the three highest RoBERTa-SHAP words (95% interval 1.104 to 4.936, 97 eligible sentences), but it covers one seed and 100 sentences only | T2.full_fusion_shap (prereg 12, Kaggle T4 16 Nov) |
| 854 | Four pairwise comparisons are reported without a correction for multiple testing; | The pairwise comparisons belong to a pre-registered family of eight tests with a Holm correction; | C*.holm definition (prereg 01) |
| 854 | would not remain significant after a Holm correction [confirm with the adjusted p-value] | does not remain significant after the correction (Holm-adjusted p = 0.190) | C2.holm |
| 929 |  [export requirements.txt] |  (_showcase/requirements.txt) | file exists |
| 929 | Copy the training split next to the other data files [copy tram_train.tsv] | Build the training split from the rows of Dataset/combined_train.csv whose source_dataset is "tram"; the original tram_train.tsv file was not found | INVIGILATOR_GUIDE; N1.tram_train_tsv NOT-FOUND |
| 931 |  [state the scale and its labels] |  (2 = makes sense, 1 = partly, 0 = does not make sense) | Exp_3_2_hand_check scale |
| 931 |  [state the sampling procedure] |  (the first 100 rows of a fixed random permutation of the 725 test sentences, NumPy RandomState(42)) | DECISIONS D10 |

## Left for the author (13 highlighted placeholders)

- p3, p9, p40, p188: author full name; p41: student ID; p46: supervisor name.
- p337: additional references recommended by the supervisor.
- p357: why (3, 1, 1, 1) was kept although the finer grid prefers (4, 1, 1, 1) (new, replaces the old "confirm" note).
- p530: repository contents (no repository exists yet, STATUS S25) and the AI-use statement in the university wording. Note: the current sentence says AI assistants were used "for code review and drafting support"; the project record (Q1_FINDINGS Q17) says the explainer application and the analysis code were built with Claude and Claude Code. The statement should say so.
- p769: example SHAP figure (candidate: `figures/fig14_shap_examples.png`).
- p931: final annotation guideline (after human study v2).
- p933: repository URL.

## Not yet in the text

- The full-fusion SHAP result (`T2.full_fusion_shap`) is added to the limitations paragraph (p852) only; the results section (around p769) can report it too.
