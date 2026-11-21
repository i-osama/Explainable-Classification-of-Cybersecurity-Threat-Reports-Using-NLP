# Pre-registration 13_support_aware_fusion_v2: Extension: support-aware fusion, four bands (author plan of 14 Nov)

| field | content |
|---|---|
| Hypothesis | H: as prereg 09, with the band layout requested in the author's master plan: unseen, 1-4, 5-19, 20+. |
| Split | dev for tuning; test touched once with the dev-selected setting |
| Metric | overall P@1 and MRR@3; P@1 on sentences whose rarest gold label has train support 0-4 |
| Comparison | fused(l) = w_m(b(l)) * z_matcher(l) + z_svm(l) + z_roberta(l) + z_secbert(l); b(l) in {unseen: 0, rare: 1-4, mid: 5-19, frequent: 20+}; w_m in {1,2,3,4,6,8} per band = 1,296 settings. Seed-averaged components; SVM scores from the deterministic refit. Compared against (3,1,1,1), (4,1,1,1) and equal weights (1,1,1,1) with paired bootstrap and exact McNemar. |
| Seeds | 42-44 (saved) |
| Dev-only tuning | dev MRR@3 (4 d.p.), tie-break dev P@1, first maximum |
| Decision rule | Extension family = 4 tests: v2 vs (3,1,1,1), v2 vs (4,1,1,1), v2 vs equal, and prereg-09 variant vs (3,1,1,1); Holm over the 4. Success = Holm-adjusted p < 0.05 vs (3,1,1,1) with a CI excluding 0, AND rare-bucket (0-4) P@1 rises. Otherwise reported as a failed extension. |
| What counts as failure / prior exposure | Registered AFTER the prereg-09 script had run but BEFORE its output file was opened or any support-aware number was read; the two variants are therefore two test evaluations of one idea and are both reported. Dev has 4 unseen-label and 34 rare-label sentences, so the unseen and rare weights are poorly determined; overfitting dev is the expected failure mode. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
