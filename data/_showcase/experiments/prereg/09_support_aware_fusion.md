# Pre-registration 09_support_aware_fusion: Extension: support-aware fusion weights

| field | content |
|---|---|
| Hypothesis | H: letting the matcher's weight depend on a label's train support (higher for rare labels) raises P@1 on sentences with rare gold labels without lowering overall P@1. |
| Split | dev for tuning; test touched once with the dev-selected setting |
| Metric | overall P@1 and MRR@3; P@1 on sentences whose rarest gold label has train support 0-4 |
| Comparison | fused(l) = w_m(b(l)) * z_matcher(l) + z_svm(l) + z_roberta(l) + z_secbert(l); b(l) in {rare: support 0-4, mid: 5-19, frequent: 20+}; w_m in {1,2,3,4,6,8} per band = 216 settings; baseline = (3,3,3) = the thesis fusion. Seed-averaged components. |
| Seeds | 42-44 (saved); seeds 45-46 in notebook 07 when they exist |
| Dev-only tuning | dev MRR@3 (4 d.p.), tie-break dev P@1, first maximum; if the dev winner is (3,3,3) the extension is reported as 'no change' |
| Decision rule | Success = paired bootstrap CI of (support-aware - baseline) on overall test P@1 does not include a loss larger than 0.005 AND the rare-bucket P@1 rises. Otherwise reported as a failed extension. |
| What counts as failure / prior exposure | Known in advance: the notebook's confidence-gated fusion gained +0.008 on test (Exp_2.1 CELL 18), and the matcher alone is better on rare labels; so a gain is plausible and the dev set has only 38 rare-label sentences (overfitting risk). This exact rule was never run. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
