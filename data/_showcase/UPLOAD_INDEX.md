# UPLOAD INDEX

Contents of `UPLOAD_TO_CLAUDE_AI.zip`. No dataset text, no model weights, no rater data. Every number comes from `thesis_numbers.json`.

| file | what it is |
|---|---|
| `thesis_numbers.json` | single source of truth: every number (id, value, CI, definition, source file, script, status) |
| `THESIS_PLACEHOLDERS.md` | answers to the draft's open items, with sources; section 14 = number audit of draft v2 |
| `STATUS.yaml` | status board: done, partial, negative result, to do on Colab, to do by the author, not found |
| `GAP_REGISTER.md` | 17 research dimensions rated covered, partial or missing |
| `DECISIONS.md` | every non-obvious choice and its reason |
| `AUDIT_TODO.md` | unregistered numbers of the draft with the nearest registry key and likely cause |
| `report/index.html` | self-contained report: story, results with intervals, error analysis, explainability, limits, status (open in a browser) |
| `docs/THREATS_TO_VALIDITY.md` | internal, construct, external and conclusion threats with status |
| `docs/RELATED_WORK_VERIFIED.md` | reference check by web search: VERIFIED, PARTLY or UNVERIFIED, with URLs |
| `notebooks/RUN_ORDER.md` | Colab run order, runtimes, what each notebook fills |
| `notebooks/COLAB_RUNBOOK.md` | click-by-click Colab guide and fixes |
| `figures/FIGURES.md` | figure list with claim ids, sources and alt text |
| `docs/superpowers/plans/2026-11-15-q1-upgrade.md` | Q1 upgrade plan: gap table, tasks, what runs where |
| `docs/superpowers/plans/2026-11-15-q1-wave2.md` | Q1 wave 2 plan: conformal sets, triage, label noise, ATT&CK drift, REFORMS, 2026 references |
| `docs/REFORMS_CHECKLIST.md` | REFORMS reporting checklist (32 items) with evidence paths and open holes; use as an appendix |
| `experiments/prereg/14_robustness_shortcuts.md` |  |
| `experiments/prereg/15_stacked_fusion.md` |  |
| `experiments/prereg/16_cross_dataset_svm.md` |  |
| `experiments/prereg/17_llm_local.md` |  |
| `experiments/prereg/18_conformal_sets.md` |  |
| `experiments/prereg/19_selective_prediction.md` |  |
| `experiments/prereg/20_label_noise_audit.md` |  |
| `experiments/prereg/21_attack_drift.md` |  |
| `thesis_feed/appendices.md` | numbers, tables, figures and caveats for this thesis part |
| `thesis_feed/ch1_intro.md` | numbers, tables, figures and caveats for this thesis part |
| `thesis_feed/ch2_related.md` | numbers, tables, figures and caveats for this thesis part |
| `thesis_feed/ch3_method.md` | numbers, tables, figures and caveats for this thesis part |
| `thesis_feed/ch4_implementation.md` | numbers, tables, figures and caveats for this thesis part |
| `thesis_feed/ch4b_system_design.md` | numbers, tables, figures and caveats for this thesis part |
| `thesis_feed/ch5_results.md` | numbers, tables, figures and caveats for this thesis part |
| `thesis_feed/ch6_discussion_conclusion.md` | numbers, tables, figures and caveats for this thesis part |
| `thesis_feed/DIFFERENCES.md` | numbers and statements where draft v2 differs from the files |
| `thesis_feed/DO_NOT_CLAIM.md` | claims the evidence does not support |
| `thesis_feed/EXPLAINER_MATCHER_FUSION.md` | plain-language explainer of the matcher and the fusion (corrected 15 Nov), with method lines |
| `thesis_feed/figures_app/architecture.png` | numbers, tables, figures and caveats for this thesis part |
| `thesis_feed/FUSION_DEFINITIONS.md` | the three fusion definitions and where each appears in draft v2 |
| `thesis_feed/NEW_FINDINGS.md` | results added after draft v2 (Holm, support-aware fusion, faithfulness, 256 tokens, unseen labels) |
| `thesis_feed/Q1_FINDINGS.md` | results of 15 Nov: robustness/shortcuts, stacked fusion, sibling sources, minimum detectable effects, LLM baseline; wave 2: conformal sets, triage (AURC), label-noise candidates, ATT&CK drift |
| `thesis_feed/Q1_MANUSCRIPT_BRIEF.md` | article brief: story, contributions with evidence ids, research questions, section map, open items |
| `thesis_feed/tables/t_ablation.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_ablation.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_calibration.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_calibration.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_comparisons_holm.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_comparisons_holm.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_dataset.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_dataset.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_efficiency.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_efficiency.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_f1_variants.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_f1_variants.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_faithfulness.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_faithfulness.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_fixed_broken.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_fixed_broken.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_fusion_definitions.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_fusion_definitions.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_human_agreement.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_human_agreement.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_maxlen_128_vs_256.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_maxlen_128_vs_256.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_overlap_sensitivity.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_overlap_sensitivity.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_parent_sub.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_parent_sub.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_per_seed.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_per_seed.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_support_aware_family.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_support_aware_family.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_support_buckets.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_support_buckets.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_systems.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_systems.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_tactics.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_tactics.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_threshold_grid.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_threshold_grid.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_top_confusions.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_top_confusions.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_weight_top10.csv` | table for the thesis (CSV for editing), built by scripts/build_thesis_feed.py |
| `thesis_feed/tables/t_weight_top10.md` | table for the thesis (markdown for reading), built by scripts/build_thesis_feed.py |
| `thesis_feed/WEB_CLAUDE_PROMPT.md` | START HERE: paste into the claude.ai Project instructions (number, claim and pending-work rules) |
| `results/ablation.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/app_grounding.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/app_grounding_causes_posthoc.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/app_live_timing.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/app_tests.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/app_verify.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/attack_drift.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/attack_drift_ids.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/attack_version.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/calibration.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/comparisons.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/conformal.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/conformal_buckets.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/conformal_family.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/conformal_posthoc_raw.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/confusions.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/cross_dataset_family.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/cross_dataset_svm.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/efficiency.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/explained_vs_fusion.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/f1_variants.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/faithfulness.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/faithfulness_curves.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/faithfulness_summary.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/fixed_broken.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/human_power_simulation.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/label_noise_candidates.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/label_noise_summary.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/llm_baseline.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/llm_family.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/matcher_variants.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/maxlen.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/overlap_sensitivity.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/parent_sub.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/per_seed.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/power_mde.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/process_timeline.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/reliability_bins.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/risk_coverage.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/robustness.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/robustness_family.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/selective.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/selective_family.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/selective_posthoc_raw.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/stacking.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/stacking_buckets.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/stacking_family.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/support_aware_dev_grid.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/support_aware_family.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/support_aware_fusion.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/support_aware_v2.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/support_aware_v2_dev_grid.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/support_buckets.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/systems.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/tactics.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/threshold_grid.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `results/weight_surface.csv` | derived metrics (no sentence text), written by scripts/run_*.py or build_timeline.py |
| `figures/fig01_architecture.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig02_protocol.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig03_er_diagram.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig04_data_long_tail.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig05_all_systems.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig06_support_buckets.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig07_forest_deltas.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig08_weight_sensitivity.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig09_ablation.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig10_fixed_broken.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig11_tactic_heatmap.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig12_top_confusions.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig13_reliability.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig14_shap_examples.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig15_faithfulness_curves.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig16_latency_accuracy.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig17_process_timeline.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig18_status_board.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
| `figures/fig19_human_agreement.png` | figure, 300 dpi PNG (SVG in the repository); caption and alt text in figures/FIGURES.md |
