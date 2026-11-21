# Pre-registration 21_attack_drift: Q1 wave 2 Task 6: ATT&CK version drift of the label space (descriptive)

| field | content |
|---|---|
| Hypothesis | Q (no hypothesis test): which share of the 737 label ids (ATT&CK v12.1) and of the train / test label occurrences is deprecated, revoked or missing in the current Enterprise ATT&CK release? |
| Split | train, dev and test labels; no predictions are used |
| Metric | shares of active / deprecated / revoked / missing ids; share of test sentences with at least one non-active gold label; count of current techniques absent from v12.1 |
| Comparison | Latest bundle: mitre-attack/attack-stix-data, enterprise-attack/enterprise-attack.json (collection x_mitre_version and SHA-256 recorded). Revocations followed through revoked-by relationships to the final id (cycle-safe). |
| Seeds | n/a |
| Dev-only tuning | nothing tuned |
| Decision rule | No decision rule (descriptive). The result states for which ATT&CK release the reported numbers are valid. |
| What counts as failure / prior exposure | Descriptions changed between releases are measured by text similarity only; the effect of new descriptions on the matcher is not measured (matcher weights not saved). |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
