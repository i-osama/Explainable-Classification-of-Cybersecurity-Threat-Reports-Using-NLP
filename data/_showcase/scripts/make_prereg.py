"""Write the pre-registration files and seal them: experiments/prereg/REGISTRY.csv gets one row per file with a UTC
timestamp and the SHA-256 of the file. Run ONCE, before any analysis script. Re-running never rewrites a sealed file;
it only verifies the hashes (exit 1 if a sealed file changed)."""
import csv, hashlib, sys
from datetime import datetime, timezone
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "experiments" / "prereg"; D.mkdir(parents=True, exist_ok=True)
COMMON = ("Split discipline: anything tuned is tuned on DEV only. The test split is evaluated once per configuration listed here. "
          "Uncertainty: paired/percentile bootstrap over test sentences, 10,000 resamples, numpy default_rng(20261114). "
          "Systems (fixed): SVM (refit, deterministic); RoBERTa and SecBERT = mean probability of seeds 42-44; matcher = mean score of seeds 42-44; "
          "fusion = z-score sum with weights (3,1,1,1) in the order matcher, SVM, RoBERTa, SecBERT.")
P = [
 ("01_statistics_family", "Comparison family and multiplicity correction",
  "H: the fusion's P@1 gain over its parts is not explained by chance; RoBERTa does not differ from SVM or SecBERT.",
  "test (725 sentences)", "P@1 (per-sentence hit at rank 1)",
  "Family of 8 two-sided tests: C1 fusion vs classifiers-only; C2 fusion vs matcher ensemble; C3 RoBERTa vs SVM; C4 RoBERTa vs SecBERT; "
  "A1-A4 full fusion vs fusion without matcher / SVM / RoBERTa / SecBERT. Exact McNemar per pair; Holm step-down over the 8 p-values.",
  "none (uses saved predictions of seeds 42-44)", "nothing is tuned",
  "A difference is called supported only if the Holm-adjusted McNemar p < 0.05 AND the bootstrap 95% CI excludes 0.",
  "Any comparison failing either condition is reported as 'not supported'. C1-C4 raw values were already seen in the evidence pack (04_bootstrap.csv); "
  "this registration fixes the family size and the correction, not a first look."),
 ("02_frequency_prior_baseline", "Frequency-prior baseline",
  "H: a model that ignores the sentence and always ranks labels by training frequency is far below every learned system.",
  "test", "P@1, MRR@3, micro/macro-F1 (predict the single most frequent train label)", "prior vs SVM (descriptive; not part of the test family)",
  "none", "nothing tuned; ranking = train label counts, ties by lower label index",
  "Reported as the floor. No decision depends on it.", "If the prior reaches P@1 above 0.20 the task is easier than described and that is stated. Never computed before this registration."),
 ("03_ablation_and_weight_surface", "Fusion ablation and weight-sensitivity surface",
  "H1: removing any component lowers test P@1. H2: test P@1 is flat (within 0.01) across the 10 best dev settings of each grid, i.e. the result does not hinge on (3,1,1,1).",
  "dev for ranking settings; test reported for every setting but never used to rank", "P@1 and MRR@3",
  "Ablation: (3,1,1,1) with one weight set to 0, seed-averaged components. Surface: both dev grids (255 and 1,711 settings), matcher seed 42 as in the notebook, plus the seed-averaged matcher.",
  "none", "selection objective = dev MRR@3 (4 d.p.), tie-break dev P@1 (as in the notebook)",
  "H1 supported for a component only if its ablation contrast passes the rule of prereg 01. H2 supported if max-min test P@1 over the top-10 dev settings <= 0.01 on both grids.",
  "Ablation point values and the top-10 wide-grid test scores were already seen (evidence pack; notebook output). New here: CIs, tests, the full dev+test surface."),
 ("04_threshold_grid_extension", "Decision-threshold grid above 0.85",
  "H: RoBERTa's dev-optimal threshold lies above the original grid's upper edge (0.85), and moving it changes test micro-F1 by less than 0.01.",
  "dev for selection; test micro-F1 reported once at the newly selected threshold", "micro-F1 (notebook variant) and macro-F1",
  "original grid np.arange(0.10, 0.90, 0.05) vs extended grid np.arange(0.10, 0.9951, 0.01); all 6 classifier runs",
  "42, 43, 44 (saved probabilities)", "threshold = arg max dev micro-F1, first maximum",
  "Report old and new threshold and the test delta per run. No headline number is replaced; the extended result is a sensitivity note.",
  "If |delta test micro-F1| >= 0.01 for RoBERTa on average, the thesis must state that the reported F1 is grid-limited. Not computed before."),
 ("05_f1_variants_support_buckets", "F1 variants and performance by train support",
  "H1: counting unseen gold labels as misses lowers micro-F1 by less than 0.01 (only 10 of 851 gold pairs). H2: fusion P@1 is below the matcher's on labels with 1-4 training sentences and above it at 20 or more.",
  "test", "micro/macro-F1 in 3 variants (notebook, seen_test, all_test); P@1 and top-1 label-F1 per bucket with 95% bootstrap CI",
  "Buckets by the train support of the sentence's rarest gold label: 0, 1-4, 5-9, 10-19, 20-49, 50+ (fixed in the evidence-pack brief).",
  "42-44", "nothing tuned",
  "H2 is called supported per bucket only if the paired bootstrap CI of (fusion - matcher) excludes 0.",
  "Bucket point values were already seen (05_rarity_buckets.csv). New: CIs and paired CIs. Small buckets (n=10, 34, 30) are expected to be inconclusive and will be reported so."),
 ("06_faithfulness", "Faithfulness of the stored word-level SHAP explanations",
  "H: masking words in SHAP order lowers the explained logit faster than masking in random order (deletion), and revealing them raises it faster (insertion); "
  "comprehensiveness of the top-3 words exceeds that of 3 random words; sufficiency is lower (better) for top-3 than for random-3.",
  "test, first 100 rows of RandomState(42).permutation(725) (the fixed sample of the existing deletion test)",
  "explained quantity = logit (and sigmoid probability) of roberta_pw_s42's top-1 label; curves for k = 0..10 masked/revealed words; AUC by trapezoid over k normalised by the k=0 value; comprehensiveness and sufficiency at k=3",
  "SHAP order vs mean of 5 random orders (RandomState(1000 + row)); eligibility = at least 6 words, not truncated at 128 tokens",
  "model seed 42 (the explained model)", "nothing tuned; k=3 fixed by the earlier deletion test; curve length 10 fixed here",
  "Each H is supported if the paired bootstrap 95% CI of (SHAP - random) excludes 0 in the stated direction.",
  "The deletion result at k=3 was already seen (10.19 logits). Insertion, comprehensiveness, sufficiency and the curves were never computed. "
  "Limit stated in advance: mask-token perturbation is the same perturbation SHAP used, so this tests consistency of the attribution, not human plausibility."),
 ("07_efficiency_latency", "Model size and CPU latency",
  "Descriptive, no hypothesis.", "100 test sentences = first 100 of the fixed permutation",
  "parameter count; median and p90 wall-clock seconds per sentence, batch size 1, 100 timed runs after 5 warm-up runs; peak resident memory of the process",
  "SVM vs RoBERTa vs SecBERT (single seed) on this PC's CPU; matcher cannot be timed (weights never saved) -> timed with the public base checkpoint and labelled as such",
  "seed 42 checkpoints", "nothing tuned", "Report hardware (CPU model, threads, torch version) with the numbers.",
  "Latency on a shared desktop is noisy; medians only, no claims of significance."),
 ("08_maxlen_128_vs_256", "Maximum length 128 vs 256 at inference",
  "H: reading 256 instead of 128 tokens at inference does not change P@1 on the 34 test sentences longer than 128 RoBERTa tokens by more than 3 sentences.",
  "test, the 34 truncated sentences (ids in _evidence_pack/01_truncated_test_ids.csv)", "P@1 on those sentences",
  "roberta_pw_s42 and secbert_pw_s42 with max_length 128 vs 256 (inference only; the models were TRAINED at 128)",
  "42", "nothing tuned", "Report both; exact McNemar on the 34.",
  "Models were trained at 128, so 256 at inference is out of distribution; a null or negative result does not show that training at 256 would not help (that needs retraining: notebook 03, TODO-COLAB)."),
 ("09_support_aware_fusion", "Extension: support-aware fusion weights",
  "H: letting the matcher's weight depend on a label's train support (higher for rare labels) raises P@1 on sentences with rare gold labels without lowering overall P@1.",
  "dev for tuning; test touched once with the dev-selected setting",
  "overall P@1 and MRR@3; P@1 on sentences whose rarest gold label has train support 0-4",
  "fused(l) = w_m(b(l)) * z_matcher(l) + z_svm(l) + z_roberta(l) + z_secbert(l); b(l) in {rare: support 0-4, mid: 5-19, frequent: 20+}; "
  "w_m in {1,2,3,4,6,8} per band = 216 settings; baseline = (3,3,3) = the thesis fusion. Seed-averaged components.",
  "42-44 (saved); seeds 45-46 in notebook 07 when they exist", "dev MRR@3 (4 d.p.), tie-break dev P@1, first maximum; if the dev winner is (3,3,3) the extension is reported as 'no change'",
  "Success = paired bootstrap CI of (support-aware - baseline) on overall test P@1 does not include a loss larger than 0.005 AND the rare-bucket P@1 rises. Otherwise reported as a failed extension.",
  "Known in advance: the notebook's confidence-gated fusion gained +0.008 on test (Exp_2.1 CELL 18), and the matcher alone is better on rare labels; so a gain is plausible and the dev set has only 38 rare-label sentences (overfitting risk). This exact rule was never run."),
 ("10_new_seeds_45_46", "Additional seeds 45 and 46 (Colab)", "H: adding two seeds does not move any 3-seed mean by more than one standard deviation.",
  "dev for epoch/threshold selection; test once per run", "micro-F1, macro-F1, P@1, MRR@3 per seed; 5-seed mean and sd",
  "RoBERTa, SecBERT, matcher with the unchanged training settings", "45, 46 (new); 42-44 untouched", "as in the original runs",
  "Report 3-seed and 5-seed values side by side. No selection of seeds.", "If a run diverges it is reported, not replaced. TODO-COLAB."),
 ("11_cross_dataset", "Extension: objective (b), sibling datasets to TRAM test (Colab)",
  "H: adding the 'procedure' and 'derived_procedure' rows of combined_train.csv to TRAM train raises test P@1 on rare labels.",
  "TRAM dev for all selection; TRAM test once per configuration", "P@1, MRR@3 overall and by support bucket",
  "train on (a) TRAM only [existing], (b) siblings only, (c) TRAM + siblings; classifiers' label space widens to the labels in the training set",
  "42, 43, 44", "epoch and threshold on TRAM dev", "Report all three; success = (c) beats (a) on overall P@1 with the rule of prereg 01.",
  "Sibling rows that duplicate TRAM dev/test sentences (exact, normalised) are removed before training and the count is reported. TODO-COLAB."),
 ("12_full_fusion_shap", "SHAP of the full fusion (Colab)",
  "H: explanations of the fused score are more faithful TO THE FUSED SCORE than the stored RoBERTa-only explanations, mainly on sentences where the two systems output different top-1 labels.",
  "test, first 100 rows of the fixed permutation", "drop of the fused score after removing the top-3 words (fused-SHAP vs RoBERTa-SHAP vs random-3)",
  "seed-paired fusion (3,1,1,1) with a matcher retrained with saved weights", "42",
  "linearity shortcut is used only if the per-row z-score statistics are verified constant under masking; they are NOT (mean and sd are recomputed per perturbed sentence), so the notebook explains each component's z-scored output directly and sums with the weights (exact by linearity of Shapley values in the OUTPUT, no assumption on the z statistics)",
  "Supported if the paired bootstrap CI of (fused-SHAP drop - RoBERTa-SHAP drop) excludes 0.",
  "Partial result already seen without the matcher (n=40): no difference when labels agree, large difference when they differ. The retrained matcher is not the original one; its own test P@1 is reported next to the result. TODO-COLAB."),
 ("13_support_aware_fusion_v2", "Extension: support-aware fusion, four bands (author plan of 14 Nov)",
  "H: as prereg 09, with the band layout requested in the author's master plan: unseen, 1-4, 5-19, 20+.",
  "dev for tuning; test touched once with the dev-selected setting",
  "overall P@1 and MRR@3; P@1 on sentences whose rarest gold label has train support 0-4",
  "fused(l) = w_m(b(l)) * z_matcher(l) + z_svm(l) + z_roberta(l) + z_secbert(l); b(l) in {unseen: 0, rare: 1-4, mid: 5-19, frequent: 20+}; w_m in {1,2,3,4,6,8} per band = 1,296 settings. "
  "Seed-averaged components; SVM scores from the deterministic refit. Compared against (3,1,1,1), (4,1,1,1) and equal weights (1,1,1,1) with paired bootstrap and exact McNemar.",
  "42-44 (saved)", "dev MRR@3 (4 d.p.), tie-break dev P@1, first maximum",
  "Extension family = 4 tests: v2 vs (3,1,1,1), v2 vs (4,1,1,1), v2 vs equal, and prereg-09 variant vs (3,1,1,1); Holm over the 4. "
  "Success = Holm-adjusted p < 0.05 vs (3,1,1,1) with a CI excluding 0, AND rare-bucket (0-4) P@1 rises. Otherwise reported as a failed extension.",
  "Registered AFTER the prereg-09 script had run but BEFORE its output file was opened or any support-aware number was read; the two variants are therefore two test evaluations of one idea and are both reported. "
  "Dev has 4 unseen-label and 34 rare-label sentences, so the unseen and rare weights are poorly determined; overfitting dev is the expected failure mode."),
 ("14_robustness_shortcuts", "Q1 plan Task 3: robustness and shortcut test (local CPU)",
  "H1: the classifiers rely on threat-group names (shortcut): masking intrusion-set names lowers P@1. H2: the systems are robust to surface noise: "
  "|delta P@1| < 0.02 for typos and for lower-casing without punctuation.",
  "TEST only, scored once per perturbation; clean scores must reproduce the saved test_probs.npy within 1e-3 (max abs) before any perturbation is scored",
  "P@1 (primary), MRR@3; delta vs clean with paired bootstrap CI; share of sentences the perturbation changed",
  "Perturbations (fixed): mask_groups = ATT&CK v12.1 intrusion-set names and aliases -> [ENT]; mask_software = malware and tool names and aliases -> [ENT]; "
  "mask_iocs = IPv4, URL, domain, MD5/SHA1/SHA256, Windows/Unix path, registry key, CVE id -> [IOC]; typo_5pct = adjacent-letter swap in 5% of words longer than 3 letters, "
  "default_rng(20261114) per sentence index; lower_nopunct = lower-case, punctuation to space. Names shorter than 4 characters and names occurring (word boundary, case-insensitive) "
  "in any technique name are never masked. Systems: SVM (refit), RoBERTa ens., SecBERT ens., zero-shot bge (public weights), classifiers-only ens. (z-sum of the three). "
  "Fusion with the fine-tuned matcher: TODO-COLAB (weights not saved).",
  "42-44 (local weights Exp_1_4_run_tram_2_epoc_30/*_pw_s*)", "none (no parameter is tuned)",
  "Family = classifiers-only ens. clean vs each of the 5 perturbations (5 tests, Holm). H1 supported if mask_groups delta < 0 with Holm p < 0.05. "
  "H2 'robust' if |delta| < 0.02 and the CI lies inside [-0.04, 0.04]. Other systems are reported descriptively with CIs.",
  "No perturbation number has been computed before sealing. Masking software names also removes legitimate evidence (tools are often the technique), so mask_software is reported "
  "as an upper bound on name reliance, not as a pure shortcut measure."),
 ("15_stacked_fusion", "Q1 plan Task 4: learned (stacked) fusion (local CPU)",
  "H: a logistic-regression stacker over the four z-scored components plus label-support features beats the hand-set (3,1,1,1) fusion on test P@1.",
  "fit and C selection on DEV only (5-fold CV by sentence, KFold shuffle seed 20261114), final fit on all dev; TEST once",
  "P@1 (primary), MRR@3, R@5, support-bucket P@1",
  "Features per (sentence, label): z_matcher, z_svm, z_roberta, z_secbert (seed-averaged components), log1p(train_count), seen flag, log(matcher rank). "
  "sklearn LogisticRegression (L2, lbfgs, max_iter 2000), C in {0.01, 0.1, 1, 10}, chosen by mean dev-fold MRR@3. Fitting rows: all gold pairs + 50 random negative labels per sentence "
  "(default_rng(20261114)); scoring uses all 733 labels.",
  "42-44 (saved)", "C by dev-fold MRR@3; a LeakageError is raised if the fit is called with any split other than dev",
  "Family = stacker vs (3,1,1,1) and stacker vs (4,1,1,1) (2 tests, Holm). Success = Holm p < 0.05 vs (3,1,1,1) and CI excluding 0. Otherwise a failed extension, reported.",
  "Dev has 604 sentences; overfitting dev is the expected failure mode. The stacker's test number is computed once."),
 ("16_cross_dataset_svm", "Q1 plan Task 5: objective (b), SVM part (local CPU)",
  "H: adding the sibling sources (procedure, derived_procedure) to TRAM train raises TF-IDF + SVM test P@1; siblings alone transfer worse than TRAM alone.",
  "train on (a) TRAM train, (b) siblings only, (c) TRAM + siblings; TEST = TRAM test, once per training set",
  "P@1 (primary), MRR@3, R@5, seen/unseen R@5, support-bucket P@1; removed-duplicate counts",
  "Siblings are de-duplicated against TRAM dev + test before training: exact (normalised text) and near (token-set Jaccard >= 0.90, as A6). Labels outside the 733-label space are dropped and counted. "
  "Same TF-IDF (1,2)-gram sublinear + LinearSVC C=1 one-vs-rest as the refit SVM; ranking metrics need no threshold.",
  "deterministic", "none",
  "Family = (c) vs (a) and (b) vs (a) (2 tests, Holm). The transformer part of objective (b) stays in notebook 08 (prereg 11).",
  "No sibling-trained number has been computed before sealing."),
 ("17_llm_local", "Q1 plan Task 7: LLM baseline with open weights (local Ollama)",
  "H: an open-weights 7B LLM (closed-set or retrieve-then-rank) does not reach the matcher ensemble's test P@1.",
  "DEV pilot: first 50 dev sentences, parse rate only, no prompt change allowed afterwards; TEST once per variant",
  "P@1 (primary), MRR@3, R@5, parse rate; ranking = the LLM's ordered ids first, then the remaining candidates in retriever order (closed-set: then by SVM score)",
  "Model qwen2.5:7b (Ollama digest 845dbda0ea48, Q4_K_M), options temperature 0, seed 0, num_predict 64, num_ctx 8192. Variants: closed = 180 training labels (id: name); "
  "rr_zero = top-20 candidates from zero-shot bge; rr_matcher = top-20 candidates from the fine-tuned matcher ensemble. Candidate descriptions cut to 40 words. "
  "Prompt templates fixed in src/ttpmap/llm.py: CLOSED_TEMPLATE sha256 f0bf94b9ce5c18b2e170f06636568c38bfcf1d65831ee915c0e3584a5219cd9f; "
  "RR_TEMPLATE sha256 42c0c897c7305baaeb3e22c68bbe3819f3519da75ce85295c32213451e25439f.",
  "n/a", "none (prompts fixed before any output was seen)",
  "Family = each variant vs matcher ensemble and vs fusion (3,1,1,1) (6 tests, Holm). H supported if no variant beats the matcher ensemble with Holm p < 0.05.",
  "No test request has been sent before sealing. A 7B local model is a lower bound on LLM performance; notebook 10 keeps the protocol for an API model."),
 ("18_conformal_sets", "Q1 wave 2 Task 3: split-conformal prediction sets (local CPU)",
  "H1: split-conformal sets of the fusion calibrated on DEV reach the nominal coverage on TEST (all gold labels in the set) at alpha 0.10. "
  "H2: at alpha 0.10 the fusion's sets are smaller than the sets of each of its four components.",
  "calibration DEV (604 sentences); TEST (725) once per system, alpha and rule",
  "coverage_all (all gold labels in the set; primary), coverage_any, mean / median / 90th-percentile set size, empty-set rate; coverage per support bucket of the rarest gold label",
  "Systems: fusion (3,1,1,1), matcher, SVM, RoBERTa, SecBERT (seed-averaged components). Rules: (a) score threshold, nonconformity = -min over gold labels of the system score, "
  "set = labels with score >= tau; (b) rank threshold, nonconformity = worst rank of a gold label, set = top-k. alpha in {0.10 (primary), 0.20}. "
  "Quantile = ceil((n+1)(1-alpha))-th smallest nonconformity on dev; above n gives the full label set. NaN scores are treated as -inf.",
  "42-44 (saved)", "tau / k fitted on DEV only; a LeakageError is raised for any other split",
  "H1 supported if the Wilson 95% CI of fusion test coverage_all at alpha 0.10 (rule a) contains 0.90. H2: family = fusion vs each component, per-sentence set size "
  "(rule a, alpha 0.10), two-sided Wilcoxon signed-rank, Holm over 4; supported if Holm p < 0.05 and the paired bootstrap CI of the mean size difference excludes 0 with fusion smaller.",
  "Coverage is marginal, not conditional on the label: low coverage for unseen and rare labels is expected and reported, not tested. Dev and test are assumed exchangeable "
  "(random TRAM split); if dev-test label shift is large the guarantee can fail and that is stated. No conformal set was computed before sealing."),
 ("19_selective_prediction", "Q1 wave 2 Task 4: selective prediction for analyst triage (local CPU)",
  "H: ranking sentences by the fusion's top-1 minus top-2 score margin gives a lower area under the risk-coverage curve (AURC, risk = 1 - hit at rank 1) than each component.",
  "thresholds on DEV; TEST once",
  "AURC (primary), E-AURC, realised test coverage and selective P@1 at dev-chosen thresholds for target coverage 0.5, 0.8, 0.9",
  "Systems: fusion (3,1,1,1), matcher, SVM, RoBERTa, SecBERT. Confidence = top-1 minus top-2 score (NaN as -inf). Stable sort for ties. "
  "Family = fusion AURC vs each component (4 tests): paired bootstrap over test sentences (both AURCs recomputed per resample), two-sided bootstrap p, Holm over 4.",
  "42-44 (saved)", "confidence thresholds for each target coverage fitted on DEV only (LeakageError otherwise)",
  "Supported for a component if Holm p < 0.05 and the 95% CI of AURC(fusion) - AURC(component) is below 0.",
  "Margins of z-score sums and of probabilities are on different scales; only within-system ordering is used, so this is valid. No risk-coverage curve was computed before sealing."),
 ("20_label_noise_audit", "Q1 wave 2 Task 5: label-noise candidates on TEST (EXPLORATORY, descriptive)",
  "Q (no hypothesis test): how many fusion top-1 errors are sentences where all four components and the fusion agree on the same wrong top-1 label (consensus disagreement with the gold label)?",
  "TEST (725)", "count and share of fusion top-1 errors that are consensus candidates; relation of the consensus label to the gold labels "
  "(parent or sub-technique, sibling sub-technique, same tactic, other)",
  "Candidate = fusion top-1 not in gold AND matcher, SVM, RoBERTa and SecBERT top-1 all equal the fusion top-1. Descriptive only.",
  "42-44 (saved)", "nothing tuned",
  "No decision rule: candidates are not label errors until a human checks them. The review sheet goes to the author (human_study/label_noise_review.xlsx).",
  "Consensus can be shared bias (all systems learnt the same shortcut), so the count is neither a lower nor an upper bound on label noise. Never computed before sealing."),
 ("21_attack_drift", "Q1 wave 2 Task 6: ATT&CK version drift of the label space (descriptive)",
  "Q (no hypothesis test): which share of the 737 label ids (ATT&CK v12.1) and of the train / test label occurrences is deprecated, revoked or missing in the current Enterprise ATT&CK release?",
  "train, dev and test labels; no predictions are used",
  "shares of active / deprecated / revoked / missing ids; share of test sentences with at least one non-active gold label; count of current techniques absent from v12.1",
  "Latest bundle: mitre-attack/attack-stix-data, enterprise-attack/enterprise-attack.json (collection x_mitre_version and SHA-256 recorded). "
  "Revocations followed through revoked-by relationships to the final id (cycle-safe).",
  "n/a", "nothing tuned",
  "No decision rule (descriptive). The result states for which ATT&CK release the reported numbers are valid.",
  "Descriptions changed between releases are measured by text similarity only; the effect of new descriptions on the matcher is not measured (matcher weights not saved)."),
]
reg = D / "REGISTRY.csv"
sealed = {}
if reg.exists():
    sealed = {r["file"]: r for r in csv.DictReader(open(reg, encoding="utf-8"))}
changed = []
for fid, title, hyp, split, metric, comp, seeds, tuning, rule, fail in P:
    f = D / f"{fid}.md"
    if f.name in sealed:
        if hashlib.sha256(f.read_bytes()).hexdigest() != sealed[f.name]["sha256"]: changed.append(f.name)
        continue
    f.write_text(f"# Pre-registration {fid}: {title}\n\n| field | content |\n|---|---|\n| Hypothesis | {hyp} |\n| Split | {split} |\n| Metric | {metric} |\n"
                 f"| Comparison | {comp} |\n| Seeds | {seeds} |\n| Dev-only tuning | {tuning} |\n| Decision rule | {rule} |\n| What counts as failure / prior exposure | {fail} |\n"
                 f"\n{COMMON}\n", encoding="utf-8")
    sealed[f.name] = {"file": f.name, "sealed_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
with open(reg, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["file", "sealed_utc", "sha256"]); w.writeheader(); w.writerows(sealed.values())
print(f"prereg files: {len(sealed)} sealed; changed since sealing: {changed or 'none'}")
sys.exit(1 if changed else 0)
