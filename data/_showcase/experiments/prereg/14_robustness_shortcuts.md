# Pre-registration 14_robustness_shortcuts: Q1 plan Task 3: robustness and shortcut test (local CPU)

| field | content |
|---|---|
| Hypothesis | H1: the classifiers rely on threat-group names (shortcut): masking intrusion-set names lowers P@1. H2: the systems are robust to surface noise: |delta P@1| < 0.02 for typos and for lower-casing without punctuation. |
| Split | TEST only, scored once per perturbation; clean scores must reproduce the saved test_probs.npy within 1e-3 (max abs) before any perturbation is scored |
| Metric | P@1 (primary), MRR@3; delta vs clean with paired bootstrap CI; share of sentences the perturbation changed |
| Comparison | Perturbations (fixed): mask_groups = ATT&CK v12.1 intrusion-set names and aliases -> [ENT]; mask_software = malware and tool names and aliases -> [ENT]; mask_iocs = IPv4, URL, domain, MD5/SHA1/SHA256, Windows/Unix path, registry key, CVE id -> [IOC]; typo_5pct = adjacent-letter swap in 5% of words longer than 3 letters, default_rng(20261114) per sentence index; lower_nopunct = lower-case, punctuation to space. Names shorter than 4 characters and names occurring (word boundary, case-insensitive) in any technique name are never masked. Systems: SVM (refit), RoBERTa ens., SecBERT ens., zero-shot bge (public weights), classifiers-only ens. (z-sum of the three). Fusion with the fine-tuned matcher: TODO-COLAB (weights not saved). |
| Seeds | 42-44 (local weights Exp_1_4_run_tram_2_epoc_30/*_pw_s*) |
| Dev-only tuning | none (no parameter is tuned) |
| Decision rule | Family = classifiers-only ens. clean vs each of the 5 perturbations (5 tests, Holm). H1 supported if mask_groups delta < 0 with Holm p < 0.05. H2 'robust' if |delta| < 0.02 and the CI lies inside [-0.04, 0.04]. Other systems are reported descriptively with CIs. |
| What counts as failure / prior exposure | No perturbation number has been computed before sealing. Masking software names also removes legitimate evidence (tools are often the technique), so mask_software is reported as an upper bound on name reliance, not as a pure shortcut measure. |

Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.
