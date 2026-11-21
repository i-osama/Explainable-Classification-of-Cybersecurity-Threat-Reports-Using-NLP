# Chapter 3: Method: numbers, tables, figures, caveats

Every number below comes from `thesis_numbers.json` (do not retype; quote the id). Status meanings: RECOMPUTED = recomputed from saved predictions by a showcase script; VERIFIED = read from a file or code; NOTES-ONLY = a copied constant; TODO-COLAB = not yet run; NOT-FOUND = searched, absent.

## Numbers

| id | value | 95% CI | definition | source file | status |
|---|---|---|---|---|---|
| `A1` | 4,797 |  | Total sentences. train + dev + test rows | `Dataset/combined_train.csv[tram], tram_dev.tsv, tram_test.tsv -> results/tables/sentences.parquet` | RECOMPUTED |
| `A2` | 3,468 / 604 / 725 |  | Train / dev / test sentences. rows per split; train after exact-text de-duplication | `Dataset/combined_train.csv[tram], tram_dev.tsv, tram_test.tsv -> results/tables/sentences.parquet` | RECOMPUTED |
| `A2.train` | 3,468 |  | train sentences. rows in the train split | `Dataset/combined_train.csv[tram], tram_dev.tsv, tram_test.tsv -> results/tables/sentences.parquet` | RECOMPUTED |
| `A2.dev` | 604 |  | dev sentences. rows in the dev split | `Dataset/combined_train.csv[tram], tram_dev.tsv, tram_test.tsv -> results/tables/sentences.parquet` | RECOMPUTED |
| `A2.test` | 725 |  | test sentences. rows in the test split | `Dataset/combined_train.csv[tram], tram_dev.tsv, tram_test.tsv -> results/tables/sentences.parquet` | RECOMPUTED |
| `A2.labels_all` | 193 |  | Distinct labels, all splits. distinct technique ids in train + dev + test | `results/tables/techniques.parquet` | RECOMPUTED |
| `A2.labels_per_text` | 1.16 |  | Labels per sentence, all splits. mean number of technique ids per sentence, train + dev + test | `Dataset/combined_train.csv[tram], tram_dev.tsv, tram_test.tsv -> results/tables/sentences.parquet` | RECOMPUTED |
| `A2.words_mean` | 21.0 |  | Words per sentence (whitespace), all splits. mean whitespace-separated words per sentence, train + dev + test | `Dataset/combined_train.csv[tram], tram_dev.tsv, tram_test.tsv -> results/tables/sentences.parquet` | RECOMPUTED |
| `A3` | 180 |  | Train labels. distinct technique ids with at least one training sentence | `results/tables/techniques.parquet` | RECOMPUTED |
| `A4` | 127 |  | Test labels. distinct technique ids in the test split | `results/tables/techniques.parquet` | RECOMPUTED |
| `A5` | 117 + 10 |  | Seen + unseen test labels. test labels with / without a training sentence | `results/tables/techniques.parquet` | RECOMPUTED |
| `A5.seen` | 117 |  | Seen test labels. test labels that occur in training | `results/tables/techniques.parquet` | RECOMPUTED |
| `A5.unseen` | 10 |  | Unseen test labels. test labels that never occur in training | `results/tables/techniques.parquet` | RECOMPUTED |
| `A6` | exact 1 / 0; near-duplicate +1 / +3 |  | Test / dev sentences also in train. exact = equal after lower-casing and whitespace collapse; near = token-set Jaccard >= 0.90, not exact | `_evidence_pack/01_duplicates.csv, 01_near_duplicates.csv` | RECOMPUTED |
| `A6.exact_test` | 1 |  | exact test rows overlapping train. see A6 | `_evidence_pack/01_duplicates.csv, 01_near_duplicates.csv` | RECOMPUTED |
| `A6.exact_dev` | 0 |  | exact dev rows overlapping train. see A6 | `_evidence_pack/01_duplicates.csv, 01_near_duplicates.csv` | RECOMPUTED |
| `A6.near_test` | 1 |  | near test rows overlapping train. see A6 | `_evidence_pack/01_duplicates.csv, 01_near_duplicates.csv` | RECOMPUTED |
| `A6.near_dev` | 3 |  | near dev rows overlapping train. see A6 | `_evidence_pack/01_duplicates.csv, 01_near_duplicates.csv` | RECOMPUTED |
| `A7` | 34 (RoBERTa tokenizer); 24 (SecBERT tokenizer) |  | Test sentences longer than 128 tokens. token count including special tokens > 128 | `_evidence_pack/01_truncated_test_ids.csv` | RECOMPUTED |
| `A7.roberta` | 34 |  | Truncated test sentences, RoBERTa. see A7 | `_evidence_pack/01_truncated_test_ids.csv` | RECOMPUTED |
| `A7.secbert` | 24 |  | Truncated test sentences, SecBERT. see A7 | `_evidence_pack/01_truncated_test_ids.csv` | RECOMPUTED |
| `A8` | 737 in the file; 733 used |  | ATT&CK description entries. rows of ttp-desc-mappings.csv; matching space after removing 4 revoked ids | `Dataset/ttp-desc-mappings.csv` | RECOMPUTED |
| `A8.file` | 737 |  | Description file entries. rows in ttp-desc-mappings.csv (tab-separated) | `Dataset/ttp-desc-mappings.csv` | RECOMPUTED |
| `A8.space` | 733 |  | Labels in the matching space. description entries minus 4 revoked duplicate ids | `results/tables/techniques.parquet` | RECOMPUTED |
| `A9.multi_test` | 90 |  | Multi-label test sentences. test sentences with 2 or more distinct gold labels | `results/tables/sentences.parquet` | RECOMPUTED |
| `A9.pairs_test` | 851 |  | Gold (sentence, label) pairs in test. sum of distinct gold labels over test sentences | `results/tables/sentences.parquet` | RECOMPUTED |
| `A9.sub_share` | 74 |  | Sub-technique labels among train labels. train labels whose id contains a dot | `results/tables/techniques.parquet` | RECOMPUTED |
| `A9.rare_train` | 79 |  | Train labels with fewer than 5 sentences. labels with train support 1-4 | `results/tables/techniques.parquet` | RECOMPUTED |
| `A9.median_support` | 7 |  | Median train support per label. median training sentences per train label | `results/tables/techniques.parquet` | RECOMPUTED |
| `B3.thr` | -0.45 |  | SVM decision threshold. arg max of dev micro-F1 over np.arange(-0.6, 0.31, 0.05) | `refit -> results/per_seed.csv` | RECOMPUTED |
| `B14` | (3,1,1,1) = dev winner of the 255-setting grid; the 1,711-setting grid selects (4,1,1,1) |  | Fusion weights and the grid they come from. selection by dev MRR@3 then dev P@1, matcher seed 42, order (matcher, SVM, RoBERTa, SecBERT) | `results/weight_surface.csv; Exp_2.1 CELL 8, 9, 11` | RECOMPUTED |
| `B14.coarse_n` | 255 |  | Settings in the coarse grid. {0,1,2,3}^4 minus all-zero | `results/weight_surface.csv` | RECOMPUTED |
| `B14.wide_n` | 1,711 |  | Settings in the wide grid. {0,1,2,3,4,6,8}^4 reduced by gcd | `results/weight_surface.csv` | RECOMPUTED |
| `B14.rank3111` | 28 |  | Dev rank of (3,1,1,1) on the wide grid. rank by dev MRR@3 then dev P@1 | `results/weight_surface.csv` | RECOMPUTED |
| `B14.test3111` | 0.800 |  | Test P@1 of (3,1,1,1), matcher seed 42. reported, never used for selection | `results/weight_surface.csv` | RECOMPUTED |
| `B14.test4111` | 0.804 |  | Test P@1 of (4,1,1,1), matcher seed 42. reported, never used for selection | `results/weight_surface.csv` | RECOMPUTED |
| `B14.top10_coarse` | 0.781 to 0.800 |  | Test P@1 range over the 10 best dev settings, coarse_255. min and max test P@1 among the 10 best dev settings (matcher seed 42) | `results/weight_surface.csv` | RECOMPUTED |
| `B14.top10_coarse.spread` | 0.019 |  | Test P@1 spread over the 10 best dev settings, coarse_255. max minus min | `results/weight_surface.csv` | RECOMPUTED |
| `B14.top10_wide` | 0.797 to 0.806 |  | Test P@1 range over the 10 best dev settings, wide_1711. min and max test P@1 among the 10 best dev settings (matcher seed 42) | `results/weight_surface.csv` | RECOMPUTED |
| `B14.top10_wide.spread` | 0.008 |  | Test P@1 spread over the 10 best dev settings, wide_1711. max minus min | `results/weight_surface.csv` | RECOMPUTED |
| `E1` | permutation SHAP, 40 permutations, model roberta_pw_s42, 725 sentences |  | SHAP settings. method block stored with every record: {"unit": "whitespace-delimited word", "masking": "word replaced by <mask>, surrounding whitespace kept", "algorithm": "permutation", "n_perm": 40, "shap_seed": 42, "output": "logit of the top-1 predicted label", "max_length": 128} | `Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl; Exp_3_0b CELL 2` | VERIFIED |
| `E1.n` | 725 |  | Sentences with stored SHAP values. records in the SHAP file | `Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl` | VERIFIED |
| `G12.exact.n` | 1 |  | Test sentences removed (exact overlap with train). test ids 59 | `results/overlap_sensitivity.csv` | RECOMPUTED |
| `G12.exact.maxdelta` | 0.0004 |  | Largest change in any system's P@1 after removing the exact overlap. max over 6 systems of /P@1 without overlap - P@1 with all 725/ | `results/overlap_sensitivity.csv` | RECOMPUTED |
| `G12.exact_near.n` | 2 |  | Test sentences removed (exact+near overlap with train). test ids 59;124 | `results/overlap_sensitivity.csv` | RECOMPUTED |
| `G12.exact_near.maxdelta` | 0.0007 |  | Largest change in any system's P@1 after removing the exact+near overlap. max over 6 systems of /P@1 without overlap - P@1 with all 725/ | `results/overlap_sensitivity.csv` | RECOMPUTED |
| `G12.p1.fusion` | 0.8028 vs 0.8022 |  | P@1 Fusion (3,1,1,1): all 725 test sentences vs without the exact+near overlap. P@1 on 725 sentences vs on 723 (test ids 59 and 124 removed) | `results/overlap_sensitivity.csv` | RECOMPUTED |
| `G12.p1.roberta` | 0.7559 vs 0.7552 |  | P@1 RoBERTa (3-seed avg): all 725 test sentences vs without the exact+near overlap. P@1 on 725 sentences vs on 723 (test ids 59 and 124 removed) | `results/overlap_sensitivity.csv` | RECOMPUTED |
| `G12.p1.secbert` | 0.7545 vs 0.7538 |  | P@1 SecBERT (3-seed avg): all 725 test sentences vs without the exact+near overlap. P@1 on 725 sentences vs on 723 (test ids 59 and 124 removed) | `results/overlap_sensitivity.csv` | RECOMPUTED |
| `G12.p1.svm` | 0.7421 vs 0.7414 |  | P@1 TF-IDF + SVM: all 725 test sentences vs without the exact+near overlap. P@1 on 725 sentences vs on 723 (test ids 59 and 124 removed) | `results/overlap_sensitivity.csv` | RECOMPUTED |
| `G12.p1.matcher` | 0.7766 vs 0.7759 |  | P@1 Matcher (3-seed ens.): all 725 test sentences vs without the exact+near overlap. P@1 on 725 sentences vs on 723 (test ids 59 and 124 removed) | `results/overlap_sensitivity.csv` | RECOMPUTED |
| `A7.roberta_pct` | 4.7% |  | Share of test sentences truncated at 128 tokens (RoBERTa). A7.roberta / test sentences | `_evidence_pack/01_truncated_test_ids.csv` | RECOMPUTED |
| `A10.combined_rows` | 14,465 |  | Rows in the combined training collection. rows of combined_train.csv (three sources) | `Dataset/combined_train.csv` | RECOMPUTED |
| `A10.combined_labels` | 478 |  | Distinct labels in the combined training collection. distinct technique ids over all rows | `Dataset/combined_train.csv` | RECOMPUTED |
| `A10.rows.procedure` | 8,487 |  | Rows from source 'procedure'. value counts of source_dataset | `Dataset/combined_train.csv` | RECOMPUTED |
| `A10.rows.tram` | 3,468 |  | Rows from source 'tram'. value counts of source_dataset | `Dataset/combined_train.csv` | RECOMPUTED |
| `A10.rows.derived_procedure` | 2,510 |  | Rows from source 'derived_procedure'. value counts of source_dataset | `Dataset/combined_train.csv` | RECOMPUTED |
| `B14.avg_coarse` | (3,1,1,1) |  | Dev-selected weights, seed-averaged matcher, coarse_255. selection by dev MRR@3 then dev P@1; matcher = mean of seeds 42-44 | `results/weight_surface.csv` | RECOMPUTED |
| `B14.avg_coarse.test` | 0.803 |  | Test P@1 of the dev-selected weights, seed-averaged matcher, coarse_255. reported, never used for selection | `results/weight_surface.csv` | RECOMPUTED |
| `B14.avg_wide` | (8,3,2,2) |  | Dev-selected weights, seed-averaged matcher, wide_1711. selection by dev MRR@3 then dev P@1; matcher = mean of seeds 42-44 | `results/weight_surface.csv` | RECOMPUTED |
| `B14.avg_wide.test` | 0.810 |  | Test P@1 of the dev-selected weights, seed-averaged matcher, wide_1711. reported, never used for selection | `results/weight_surface.csv` | RECOMPUTED |

## Tables (CSV for editing, markdown for reading)

- `tables/t_dataset.csv` / `.md`
- `tables/t_overlap_sensitivity.csv` / `.md`

## Figures (in `../figures/`, PNG 300 dpi and SVG; alt text in `../figures/FIGURES.md`)

- `fig01_architecture.png`
- `fig02_protocol.png`
- `fig04_data_long_tail.png`

## Caveats to state

- Train is the tram slice of combined_train.csv after exact-text de-duplication; the raw tram_train.tsv is not in the folder.
- Overlap with train: exact 1 / 0; near-duplicate +1 / +3. State exact and near-duplicate counts separately.
- 34 (RoBERTa tokenizer); 24 (SecBERT tokenizer): the 34 is RoBERTa-specific.
