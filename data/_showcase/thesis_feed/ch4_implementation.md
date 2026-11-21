# Chapter 4: Implementation: numbers, tables, figures, caveats

Every number below comes from `thesis_numbers.json` (do not retype; quote the id). Status meanings: RECOMPUTED = recomputed from saved predictions by a showcase script; VERIFIED = read from a file or code; NOTES-ONLY = a copied constant; TODO-COLAB = not yet run; NOT-FOUND = searched, absent.

## Numbers

| id | value | 95% CI | definition | source file | status |
|---|---|---|---|---|---|
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
| `G10.params.svm` | 7,774,740 |  | Parameters, TF-IDF + SVM. 43193 n-gram features x 180 labels; 2306593 non-zero weights | `results/efficiency.csv` | RECOMPUTED |
| `G10.ms.svm` | 17.9 |  | Median CPU latency per sentence, TF-IDF + SVM (ms). batch size 1, 100 sentences after 5 warm-up; p90 = 19.3 ms; timed with: refit model; hardware in results/hardware.json | `results/efficiency.csv` | RECOMPUTED |
| `G10.params.roberta` | 124,784,052 |  | Parameters, RoBERTa. one seed; the 3-seed average costs 3 forward passes | `results/efficiency.csv` | RECOMPUTED |
| `G10.ms.roberta` | 46.7 |  | Median CPU latency per sentence, RoBERTa (ms). batch size 1, 100 sentences after 5 warm-up; p90 = 86.6 ms; timed with: saved checkpoint seed 42; hardware in results/hardware.json | `results/efficiency.csv` | RECOMPUTED |
| `G10.params.secbert` | 83,589,300 |  | Parameters, SecBERT. one seed; the 3-seed average costs 3 forward passes | `results/efficiency.csv` | RECOMPUTED |
| `G10.ms.secbert` | 22.7 |  | Median CPU latency per sentence, SecBERT (ms). batch size 1, 100 sentences after 5 warm-up; p90 = 35.7 ms; timed with: saved checkpoint seed 42; hardware in results/hardware.json | `results/efficiency.csv` | RECOMPUTED |
| `G10.params.matcher` | 109,482,240 |  | Parameters, Matcher (bge-base). sentence encoding + dot product with 733 pre-computed label vectors; label vectors are a one-off cost | `results/efficiency.csv` | RECOMPUTED |
| `G10.ms.matcher` | 47.6 |  | Median CPU latency per sentence, Matcher (bge-base) (ms). batch size 1, 100 sentences after 5 warm-up; p90 = 83.4 ms; timed with: PUBLIC base checkpoint (fine-tuned weights were never saved; same architecture); hardware in results/hardware.json | `results/efficiency.csv` | RECOMPUTED |
| `H1.roberta_15ep` | 0.624 +/- 0.010 |  | micro-F1 roberta, earlier 15-epoch configuration (3 seeds). stored test micro-F1, mean +/- sd over seeds 42-44 | `runs_tram_1.1_epoch_15/*/metrics.json` | VERIFIED |
| `H1.secbert_15ep` | 0.629 +/- 0.010 |  | micro-F1 secbert, earlier 15-epoch configuration (3 seeds). stored test micro-F1, mean +/- sd over seeds 42-44 | `runs_tram_1.1_epoch_15/*/metrics.json` | VERIFIED |
| `H2.roberta_pw_dev` | 0.736 |  | RoBERTa seed 42, with positive weight: best dev micro-F1. stored dev_best_micro_f1 | `Exp_1_4_run_tram_2_epoc_30/roberta_pw_s42/metrics.json` | VERIFIED |
| `H2.roberta_pw_test` | 0.708 |  | RoBERTa seed 42, with positive weight: test micro-F1. stored test micro_f1 | `Exp_1_4_run_tram_2_epoc_30/roberta_pw_s42/metrics.json` | VERIFIED |
| `H2.roberta_nopw_dev` | 0.736 |  | RoBERTa seed 42, without positive weight: best dev micro-F1. stored dev_best_micro_f1 | `Exp_1_4_run_tram_2_epoc_30/roberta_nopw_s42/metrics.json` | VERIFIED |
| `H2.roberta_nopw_test` | 0.712 |  | RoBERTa seed 42, without positive weight: test micro-F1. stored test micro_f1 | `Exp_1_4_run_tram_2_epoc_30/roberta_nopw_s42/metrics.json` | VERIFIED |
| `B14.avg_coarse` | (3,1,1,1) |  | Dev-selected weights, seed-averaged matcher, coarse_255. selection by dev MRR@3 then dev P@1; matcher = mean of seeds 42-44 | `results/weight_surface.csv` | RECOMPUTED |
| `B14.avg_coarse.test` | 0.803 |  | Test P@1 of the dev-selected weights, seed-averaged matcher, coarse_255. reported, never used for selection | `results/weight_surface.csv` | RECOMPUTED |
| `B14.avg_wide` | (8,3,2,2) |  | Dev-selected weights, seed-averaged matcher, wide_1711. selection by dev MRR@3 then dev P@1; matcher = mean of seeds 42-44 | `results/weight_surface.csv` | RECOMPUTED |
| `B14.avg_wide.test` | 0.810 |  | Test P@1 of the dev-selected weights, seed-averaged matcher, wide_1711. reported, never used for selection | `results/weight_surface.csv` | RECOMPUTED |

## Tables (CSV for editing, markdown for reading)

- `tables/t_efficiency.csv` / `.md`
- `tables/t_weight_top10.csv` / `.md`

## Figures (in `../figures/`, PNG 300 dpi and SVG; alt text in `../figures/FIGURES.md`)

- `fig03_er_diagram.png`
- `fig16_latency_accuracy.png`
- `fig17_process_timeline.png`

## Caveats to state

- Matcher weights were never saved; the matcher can only be re-scored from saved score files until notebook 04 is run.
- Latency was measured on one desktop CPU (`results/hardware.json`); the matcher was timed with the public base checkpoint.
