# Pre-registration 11_cross_dataset: Extension: objective (b), sibling datasets to TRAM test (Colab)

| field | content |
|---|---|
| Hypothesis | H: adding the 'procedure' and 'derived_procedure' rows of combined_train.csv to TRAM train raises test P@1 on rare labels. |
| Split | TRAM dev for all selection; TRAM test once per configuration |
| Metric | P@1, MRR@3 overall and by support bucket |
| Comparison | train on (a) TRAM only [existing], (b) siblings only, (c) TRAM + siblings; classifiers' label space widens to the labels in the training set |
| Seeds | 42, 43, 44 |
| Dev-only tuning | epoch and threshold on TRAM dev |
| Decision rule | Report all three; success = (c) beats (a) on overall P@1 with the rule of prereg 01. |
| What counts as failure / prior exposure | Sibling rows that duplicate TRAM dev/test sentences (exact, normalised) are removed before training and the count is reported. TODO-COLAB. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
