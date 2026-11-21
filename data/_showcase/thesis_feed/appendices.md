# Appendices: numbers, tables, figures, caveats

Every number below comes from `thesis_numbers.json` (do not retype; quote the id). Status meanings: RECOMPUTED = recomputed from saved predictions by a showcase script; VERIFIED = read from a file or code; NOTES-ONLY = a copied constant; TODO-COLAB = not yet run; NOT-FOUND = searched, absent.

## Numbers

All entries: `../THESIS_MAP.md` (one row per id). Full list of open and missing items:

| id | value | 95% CI | definition | source file | status |
|---|---|---|---|---|---|
| `T3.fusion_replication` | n/a |  | Fusion and ablation with the retrained matcher. replication of B12a/B13a | `notebooks/05_fusion_and_ablation.ipynb` | TODO-COLAB |
| `T4.seeds_45_46` | n/a |  | Five-seed means (seeds 42-46). prereg 10 | `notebooks/03_train_classifiers.ipynb, 04_train_matcher_save.ipynb` | TODO-COLAB |
| `T5.baseline_same_protocol` | n/a |  | Published baseline under our protocol. re-run of Nguyen et al. on the same split and metric code | `notebooks/09_baseline_same_protocol.ipynb` | TODO-COLAB |
| `T6.cross_dataset` | n/a |  | Objective (b): sibling datasets to TRAM test. prereg 11 | `notebooks/08_extension_cross_dataset.ipynb` | TODO-COLAB |
| `T8.human_study_v2` | n/a |  | Second human study (3+ raters, protocol). docs/HUMAN_STUDY_PROTOCOL.md | `scripts/make_rating_sheet.py` | TODO-COLAB |
| `T9.usability_sus` | n/a |  | Usability study of the explainer app (3-5 users, 5 tasks, SUS); author task, not Colab. design-science evaluation of the artefact | `ttp_app/usability/USABILITY_STUDY.md, ttp_app/usability/score_sus.py` | TODO-COLAB |
| `N1.tram_train_tsv` | n/a |  | Original tram_train.tsv. searched Dataset/ and the whole tree; rebuilt from combined_train.csv | `-` | NOT-FOUND |
| `N2.matcher_weights` | n/a |  | Original matcher weights. run_match_1/ holds score files only | `-` | NOT-FOUND |
| `N3.svm_scores` | n/a |  | Saved SVM scores. never written by any notebook; refit | `-` | NOT-FOUND |
| `N4.colab_env` | n/a |  | Colab environment of the original runs. no pip freeze saved | `-` | NOT-FOUND |
| `N5.git_history` | n/a |  | Git history of the original work. no repository existed before 2026-11-14 | `-` | NOT-FOUND |
| `N6.data_licence` | n/a |  | Dataset licence and source commit. no licence text in the folder | `-` | NOT-FOUND |
| `N7.attack_version_in_data` | n/a |  | ATT&CK version string inside a data file. only in notebook comments | `-` | NOT-FOUND |
| `N8.pre_dedup_size` | n/a |  | Train size before de-duplication. raw train file absent | `-` | NOT-FOUND |
| `N9.rater_roles` | n/a |  | Background of raters B and C. not recorded in any file | `-` | NOT-FOUND |
| `N10.training_times` | n/a |  | Classifier training times. not printed by the notebooks | `-` | NOT-FOUND |

## Tables (CSV for editing, markdown for reading)

- `tables/t_per_seed.csv` / `.md`
- `tables/t_f1_variants.csv` / `.md`
- `tables/t_weight_top10.csv` / `.md`
- `tables/t_threshold_grid.csv` / `.md`
- `tables/t_overlap_sensitivity.csv` / `.md`
- `tables/t_tactics.csv` / `.md`
- `tables/t_top_confusions.csv` / `.md`
- `tables/t_efficiency.csv` / `.md`

## Figures (in `../figures/`, PNG 300 dpi and SVG; alt text in `../figures/FIGURES.md`)

- `fig03_er_diagram.png`
- `fig17_process_timeline.png`
- `fig18_status_board.png`
