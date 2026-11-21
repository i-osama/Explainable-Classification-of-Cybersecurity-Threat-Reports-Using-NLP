# 02 Settings truth table

Citation format: `notebook : CELL n` refers to the cell index in `nb_src/<notebook>.txt` (a text dump of the notebook made by
`scripts/nb_dump.py`; cell index = position in the .ipynb). `metrics.json` = the `config` block stored with each run.
Every value below is **VERIFIED** (read from code or a stored config) unless tagged otherwise.

## TF-IDF + SVM

| item | value | source |
|---|---|---|
| vectoriser | `TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)`, fit on train text only | Exp_1_4 : CELL 6; Exp_2.1 : CELL 8 |
| n-gram range | word 1-2 grams | same |
| min_df / max_df / max_features | not set -> scikit-learn defaults (min_df=1, max_df=1.0, no cap); lowercase=True default | same (absence of argument) |
| classifier | `LinearSVC(C=1.0, random_state=42)` | same |
| regularisation constant | C = 1.0 | same |
| class_weight | not set -> None | same (absence of argument) |
| multi-label wrapper | `OneVsRestClassifier` over the 180 train labels | same |
| threshold | global threshold on `decision_function`, grid `np.arange(-0.6, 0.31, 0.05)`, chosen on DEV micro-F1: **-0.45**; rows with no label above it get their arg-max label | Exp_1_4 : CELL 6 code + output; CELL 4 `apply_thresholds` |
| SVM results | micro-F1 0.6961, macro-F1 (117 present labels) **0.5427**, P@1 0.7421, MRR@3 0.8138 | Exp_1_4 : CELL 6 output; RECOMPUTED identical (`03_results.md`); macro-F1 over 127 = 0.5000 (RECOMPUTED) |
| saved predictions | none; SVM is refit (deterministic) | - |

## RoBERTa / SecBERT classifiers

| item | value | source |
|---|---|---|
| checkpoints | `roberta-base`, `jackaduma/SecBERT` | Exp_1_4 : CELL 2 `MODELS`; `metrics.json` `model_name` |
| head | `AutoModelForSequenceClassification(num_labels=180, problem_type="multi_label_classification")` | Exp_1_4 : CELL 8 |
| max length | 128 tokens, truncation, dynamic padding | CELL 8 `train_model(max_length=128)`; `metrics.json` config |
| batch size | 16 train, 32 eval | CELL 8; config |
| learning rate | encoder 2e-5, classification head 1e-3 (two parameter groups) | CELL 8, CELL 10, CELL 14; config `lr`, `head_lr` |
| epochs / patience | max 30, early stop after 5 epochs without dev micro-F1 gain; best epoch restored | CELL 8, 10, 14; config |
| best epochs | RoBERTa 25 / 13 / 23, SecBERT 18 / 18 / 23 (seeds 42 / 43 / 44) | `metrics.json` `best_epoch` |
| loss | `BCEWithLogitsLoss(pos_weight=pw)`, `pw = min((N - pos)/pos, 20)` per label | CELL 8 |
| pos_weight cap | 20.0 | CELL 8; config |
| optimizer | `torch.optim.AdamW`, weight decay not set (PyTorch default 0.01) | CELL 8 |
| scheduler | linear warmup (10% of total steps) then linear decay, `get_linear_schedule_with_warmup` | CELL 8 (`warmup_ratio=0.1`) |
| gradient clipping | max-norm 1.0 | CELL 8 `run_epoch` |
| precision | fp32 (no autocast in the classifier loop) | CELL 8 |
| threshold grid | `PROB_GRID = np.arange(0.1, 0.9, 0.05)` (0.10 ... 0.85), chosen on DEV micro-F1 | CELL 8 |
| chosen thresholds | RoBERTa 0.85 / 0.85 / 0.85, SecBERT 0.75 / 0.65 / 0.70 | `metrics.json` `threshold` |
| seeds | 42, 43, 44 (`random`, `numpy`, `torch`, `torch.cuda`) | CELL 4 `set_seed`; CELL 10, 14 |
| pw vs nopw | both trained for seed 42; `pw` kept, "choose pw vs nopw by DEV, never by test" | CELL 12 |
| model selection | epoch by DEV micro-F1; threshold by DEV | CELL 8 |
| train dedup | `train.drop_duplicates(subset=["text"])`, `assert len(train) == 3468` | CELL 4 |
| hardware | Colab GPU (`device=cuda`); GPU model NOT-FOUND in outputs (markdown says T4) | CELL 10 output; CELL 0 |

Note: all three RoBERTa thresholds sit on the upper edge of the grid (0.85), so the grid may be cutting off the optimum.

## bge matcher (bi-encoder retrieval)

| item | value | source |
|---|---|---|
| checkpoint | `BAAI/bge-base-en-v1.5` (HF revision hash NOT-FOUND) | Exp_2.1 : CELL 1 `BASE_MODEL`; `run_match_1/ft20_s*/metrics.json` `model_name` |
| architecture | one shared encoder for sentences and label descriptions | CELL 3 `Matcher` |
| pooling | [CLS] token (`pooling="cls"`) | CELL 3; config |
| normalisation | L2 (`F.normalize`), score = cosine similarity | CELL 3 |
| loss | per positive (sentence, label): `softplus(logsumexp(negatives) - s_pos)`, i.e. -log softmax of the positive against the negatives only (InfoNCE-style, multi-positive) | CELL 3 `train_matcher` |
| temperature | scale 30.0 on cosine (temperature 1/30) | CELL 3; config `scale` |
| negative sampling | per batch: 64 labels drawn uniformly without replacement from ALL 733 labels minus the batch's gold labels (`neg_pool="all"`); other sentences' gold labels in the batch also act as negatives | CELL 3; config `n_neg`, `neg_pool` |
| epochs / patience | max 20, patience 4, epoch chosen by DEV MRR@3; best epochs 17 / 14 / 8 | CELL 7; `metrics.json`; CELL 11 output |
| batch / lr / wd | 16 / 2e-5 / AdamW weight_decay 0.01, linear warmup 10% | CELL 3 |
| max length | sentences 128; descriptions 128 in training, 256 at evaluation | CELL 3 defaults; config |
| precision | AMP fp16 on GPU (`torch.autocast`, `GradScaler`), clip 1.0 | CELL 3 |
| seeds | 42, 43, 44 | CELL 7 |
| text format | raw sentence vs. raw ATT&CK description (whitespace collapsed, literal `citation:` markers removed); no instruction prefix, no technique name prepended | CELL 2 |
| label space | 737 ids in `ttp-desc-mappings.csv` minus 4 revoked duplicates (t1060, t1107, t1151, t1188) = 733 | CELL 2 code + output |
| earlier variant | `ft_s42`: 8 epochs, patience 3 (test P@1 0.731); ablation `ft20L256_s*`: descriptions 256 in training | CELL 5, CELL 16 |
| saved artefacts | dev/test score matrices only; **model weights were never saved** | CELL 3 (no `save_pretrained`) |

## Fusion

| item | value | source |
|---|---|---|
| component ORDER | `['matcher', 'svm', 'roberta', 'secbert']` -> weights (3,1,1,1) = matcher 3, SVM 1, RoBERTa 1, SecBERT 1 | Exp_2.1 : CELL 8 output `models: [...]`; CELL 9 output |
| component scores | matcher: cosine over 733 labels; SVM: `decision_function` over 180; RoBERTa / SecBERT: sigmoid probabilities, averaged over the 3 seeds, over 180 | CELL 8 |
| score normalisation | per sentence z-score over the labels the component knows; labels it does not know (553 for the classifiers) get 0 after z-scoring | CELL 8 `to_full`, `zrow` |
| fusion rule | weighted sum of z-scores, rank labels by the sum | CELL 8 `fuse` |
| tuning split | DEV only (`fuse(w, 0)`, `Y_dev`) | CELL 8, CELL 9 |
| tuning objective | DEV MRR@3 rounded to 4 d.p., tie-break DEV P@1 | CELL 8 |
| grid 1 (coarse) | weights in {0,1,2,3}^4 minus all-zero = **255** settings; matcher = ft20 **seed 42 only** | CELL 8; RECOMPUTED 255 |
| grid 2 (wide) | {0,1,2,3,4,6,8}^4 reduced by gcd = **1,711** distinct settings | CELL 9 output "1711 different weight settings tried"; RECOMPUTED 1711 |
| WHEN (3,1,1,1) was chosen | **on grid 1 (255 settings)**: CELL 8 output `dev-chosen weights: {'matcher': 3, 'svm': 1, 'roberta': 1, 'secbert': 1}`. Grid 2 chose **(4,1,1,1)** (CELL 9 output `chosen with wide grid`). CELL 11 then says "weights FIXED at (3,1,1,1)". Order evidence = cell order and the variable `w_old = w_best`; the notebook has no execution counts or timestamps (exec=None), so wall-clock order is NOT-FOUND | CELL 8, 9, 11; RECOMPUTED in `03_results.md` ((3,1,1,1) is rank 30 of 1,711 on DEV) |
| test exposure | CELL 9 prints TEST P@1/MRR@3 for the 10 best DEV settings "only to judge stability (NOT used to choose)"; (3,1,1,1) test P@1 0.800 vs (4,1,1,1) 0.804 | CELL 9 output |
| final systems | per matcher seed with 3-seed-averaged classifiers (0.800 +- 0.001), and 3-seed-averaged matcher (0.803) | CELL 11, CELL 12 |
| "seed-paired" 0.796 +- 0.006 | matcher seed s + RoBERTa seed s + SecBERT seed s. **Not in any notebook**; exists only as an earlier audit computation -> RECOMPUTED here | `03_results.md` |

## Bootstrap

| item | value | source |
|---|---|---|
| fusion comparisons (C1, C2) | 1,000 resamples; `np.random.default_rng(0)`; unit = test sentence (paired, n = 725); 95% percentile interval | Exp_2.1 : CELL 8, 11, 13 |
| RoBERTa vs SVM / SecBERT (C3, C4) | **NOT-FOUND in any notebook** (searched `nb_src/*.txt` for "bootstrap", "default_rng", "RandomState"); numbers originate from an earlier audit note | - |
| evidence-pack setting | 10,000 resamples, `default_rng(20261114)`, percentile; plus exact McNemar | `scripts/t4_bootstrap.py` |
| deletion test CI | 1,000 resamples of sentences, `RandomState(42)`, percentile | Exp_3_1_deletion_test : CELL 2-3 |
| kappa CI | 2,000 resamples, `RandomState(42)`, percentile | Exp_3_3_rater_agreement : CELL 1 (`N_BOOT, BOOT_SEED = 2000, 42`) |
| 15-epoch pilot | `runs_tram_1.1_epoch_15/analysis/bootstrap_significance.csv` (older experiment, not the thesis numbers) | Exp_1_1 |

## SHAP and deletion test

| item | value | source |
|---|---|---|
| explainer | `shap.Explainer(f, masker, algorithm="permutation", seed=42)`, shap 0.54.1 | Exp_3_0b : CELL 1 output, CELL 2 `explain_row` |
| masker | `shap.maskers.Independent(np.zeros((1, n)))` over n binary word-presence features; a hidden word becomes `<mask>`, whitespace kept | CELL 2 `build_text` |
| unit | whitespace-delimited word (regex `(\s*)(\S+)(\s*)`), not sub-word tokens | CELL 2 |
| permutations | 40 (`max_evals = 40 * (2n + 1)`) | CELL 2 `N_PERM = 40` |
| output explained | raw logit of the model's top-1 label for that sentence | CELL 2 |
| model and seed | `Exp_1_4_run_tram_2_epoc_30/roberta_pw_s42`; SHAP seed 42 | CELL 2 |
| sample size | all 725 test sentences (stored file has 725 records) | CELL 3 output "stored for the selected rows: 725 of 725"; RECOMPUTED |
| sampling rule | order = `np.random.RandomState(42).permutation(725)`; first 100 = deletion-test and human-rating sample | CELL 3; Exp_3_2 : CELL 0 |
| truncation | max_length 128; 34 sentences longer (flag `truncated`) | CELL 3 output |
| deletion test: what is hidden | the K = 3 words with the highest positive SHAP value | Exp_3_1_deletion_test : CELL 0, CELL 2 (`K_HIDE = 3`) |
| how | *mask*: word -> `<mask>`; *remove*: word and trailing whitespace deleted | CELL 0, CELL 2 |
| comparison | mean over 20 random 3-word subsets, `RandomState(42 + row)` | CELL 2-3 (`N_RANDOM = 20`) |
| eligibility | >= 6 words and >= 3 positive SHAP words; truncated rows reported separately | CELL 0, CELL 3 |
| the 10.19 | mean of [drop(top-3) - mean drop(random-3)] in logits of the top-1 label, mask variant, n = 93: 12.656 - 2.466 = 10.189, CI [9.317, 11.041] | CELL 3 output; RECOMPUTED (`06_shap.md`) |
| the 93/93 | sentences (of the 93 eligible, non-truncated ones among the 100 sampled) where the top-3 drop exceeds the mean random drop | CELL 3 output; RECOMPUTED |
| 93 denominator | 100 sampled - 3 skipped - 4 truncated | CELL 3 output |

## Human rating

| item | value | source |
|---|---|---|
| scale | 2 = makes sense, 1 = partly, 0 = does not make sense | Exp_3_2_hand_check : CELL 0, CELL 2 output |
| sampling | first 100 rows of `RandomState(42).permutation(725)` | CELL 0, CELL 2 |
| shown | sentence with top-3 positive SHAP words marked, predicted technique id / name / status / first description sentence; gold hidden | CELL 0, CELL 2 |

## Review focus

| check | verdict | basis |
|---|---|---|
| LEAKAGE: thresholds | **PASS** | chosen on DEV (Exp_1_4 CELL 6, CELL 8) |
| LEAKAGE: epoch selection | **PASS** | DEV micro-F1 (classifiers), DEV MRR@3 (matcher) |
| LEAKAGE: fusion weights | **PASS with a note** | selected on DEV; RECOMPUTED DEV winner of the coarse grid is (3,1,1,1). Note: test scores of the 10 best wide-grid settings were printed before the weights were "fixed" at (3,1,1,1); the kept setting is the LOWER-scoring one on test (0.800 vs 0.804), so the choice did not inflate the result, but the thesis must say which grid the weights come from |
| LEAKAGE: ensemble members | **PASS with a note** | members = all four model families, `pw` variant by DEV (Exp_1_4 CELL 12). Note: the 8-epoch matcher's TEST score (0.731) was visible before the 20-epoch run was launched (Exp_2.1 CELL 5 -> CELL 7); DEV was still rising at epoch 8, so the change is DEV-justified, but the motive cannot be proven from files |
| LEAKAGE: SHAP model | **PASS** | designated before results (Exp_1_4 CELL 10 comment) |
| LEAKAGE: 128 vs 256 descriptions, gated fusion | **PASS** | "DEV first, test is only a report" (Exp_2.1 CELL 17, 18); neither is a headline number |
| METRIC DEFINITIONS | **PASS with notes** | one implementation for all systems in this pack (`scripts/common.py`), reproduces every stored value (max diff 2e-8). Notes: (1) notebook micro/macro-F1 are computed on the 180 train-label columns only, so the 10 unseen test gold labels are ignored, not counted as misses; (2) macro-F1 is over labels present in test (117), hence the 117 vs 127 pair; (3) ties: notebooks use `np.argsort(-S)` (unstable order), this pack uses a stable sort; at most 2 sentences have a top-1 tie in any system; (4) empty predictions: arg-max label is forced; (5) granularity: exact id, sub-technique != parent |
| SPLIT OVERLAP | **PASS (small)** | exact: 1 test sentence in train, 0 dev; near-duplicates: +1 test, +3 dev rows in train, 1 dev-test pair (`01_dataset.md`) |
| MISSING ARTIFACTS | **FAIL (listed)** | `tram_train.tsv`, matcher weights, SVM scores, Colab pip freeze, paper PDF: see NOT-FOUND list in `EVIDENCE_REPORT.md` |
| SELECTION BIAS | **PASS for the pack; UNKNOWN for the draft** | pack examples follow written rules (lowest ids). The label-rarity buckets in Exp_2.1 CELL 14 (0, 1-5, 6-20, >20) have no stated rule; which examples the draft shows is outside this folder |
