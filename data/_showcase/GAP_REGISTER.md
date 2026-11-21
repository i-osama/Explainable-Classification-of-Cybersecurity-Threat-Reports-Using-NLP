# GAP REGISTER

Audit of the research against 17 dimensions an examiner can ask about. State at the start of the showcase build
(before T1-T9). "Evidence" points into `_evidence_pack\` (read-only base). "Closes" names the showcase task.
Live state after the build is in `STATUS.yaml` and on the status board of `report\index.html`.

Legend: COVERED = evidence exists and reproduces; PARTIAL = exists with a stated hole; MISSING = nothing usable.

| # | Dimension | State | Evidence | Hole | Severity | Closes |
|---|---|---|---|---|---|---|
| 1 | Task formalisation, metric definitions | PARTIAL | `02_settings.md` (review focus), `scripts/common.py` | three F1 variants not reported side by side; R@1 definition differs from the baseline paper | High | T2, T3 |
| 2 | Datasets, splits, data card, licence, ATT&CK version | PARTIAL | `01_dataset.md`, `01_*.csv` | licence, source commit, version string inside data: NOT-FOUND; no data card | High | T1, T7 |
| 3 | Baselines | PARTIAL | `03_results.md` (SVM, zero-shot bge); `08_baseline.md` | no frequency-prior baseline; published baseline not re-run; no LLM baseline | High | T3 (prior), T5 nb 02/09/10 |
| 4 | Ablations | PARTIAL | `03_results_recomputed.csv` rows "Ablation" | no CIs or tests per ablation | High | T3 |
| 5 | Sensitivity (weights, threshold, max length) | PARTIAL | `03_fusion_grid_dev.csv` (dev only) | no dev+test surface; threshold grid stops at 0.85; no 256-token check | High | T3, T5 nb 03 |
| 6 | Statistics | PARTIAL | `04_bootstrap.csv` | no multiplicity correction; seed variance only as mean +/- sd over 3 seeds | High | T3 |
| 7 | Robustness | MISSING | - | no perturbation or cross-dataset test | Recommended | T3 (masking), T5 nb 08 |
| 8 | Error analysis | COVERED | `05_errors.md`, `05_*.csv` | bucket values lack CIs | Recommended | T3 |
| 9 | Calibration | PARTIAL | `05_ece.csv` | no reliability diagram; classifiers only | Recommended | T3, T4 |
| 10 | Explainability faithfulness | PARTIAL | `06_shap.md`, `06_deletion_test_725.csv`, `11_fusion_shap.md` | deletion only; no insertion, comprehensiveness, sufficiency; full-fusion SHAP never run | High | T3, T5 nb 06 |
| 11 | Human evaluation | PARTIAL (negative) | `07_human.md` | agreement at chance; third rater 3 rows; no protocol document | Critical | T6 (protocol only) |
| 12 | Efficiency | MISSING | - | no parameter counts, latency, memory | Recommended | T3 |
| 13 | Reproducibility | PARTIAL | `00_hashes.csv`, `09_repro\` | no package, no tests, Colab environment NOT-FOUND, matcher weights never saved | Critical | T2, T5 nb 00/04 |
| 14 | Ethics and dual-use | MISSING | - | no statement | High | T7 |
| 15 | Threats to validity | MISSING | scattered caveats in `EVIDENCE_REPORT.md` | not organised | High | T7 |
| 16 | Related work with verified references | MISSING | `08_baseline.md` (one paper, arXiv only) | no verified reference list | High | T6 |
| 17 | Open release | MISSING | - | no licence note, citation file, model cards; not a git repository | Recommended | T7, T9 |

## Negative or uncomfortable results that must stay visible

These are findings, not gaps. They are reported as measured.

1. RoBERTa and SecBERT do not beat TF-IDF + SVM with statistical support (`04_statistics.md` C3, C4).
2. The fusion does not help the tail: 0 of 10 unseen-label sentences correct at rank 1, and worse than the matcher alone on labels with 1-4 training sentences (`05_errors.md`).
3. Fusion vs matcher ensemble is borderline (`04_statistics.md` C2).
4. Human plausibility study is at chance agreement (`07_human.md`).
5. The explained model (one RoBERTa seed) is not the system that produces the headline number; top-1 labels differ on a measurable share of test sentences (`10_fusion_vs_roberta.md`).
6. The published baseline was not re-run; split and training-mode comparability unknown (`08_baseline.md`).

## NOT-FOUND (never claimed anywhere in the showcase)

`tram_train.tsv` (rebuilt from `combined_train.csv`), matcher weights, SVM scores, Colab environment and GPU model, git repository,
dataset licence and source commit, ATT&CK version string inside data files, pre-deduplication train size, roles of raters B and C, training times.

## Q1 upgrade (15 Nov 2026)

Reviewer questions a Q1 journal will ask, state after the local work of 15 Nov. Plan: `docs/superpowers/plans/2026-11-15-q1-upgrade.md`; results: `thesis_feed/Q1_FINDINGS.md`.

| # | Reviewer question | State | Evidence |
|---|---|---|---|
| Q1 | Are the explainer and draft numbers correct? | COVERED | `thesis_feed/EXPLAINER_MATCHER_FUSION.md` (8 errors fixed) |
| Q2 | Shortcut learning on names / IOCs? Robust to noise? | COVERED for classifiers; fusion TODO-COLAB | `results/robustness.csv` (prereg 14) |
| Q3 | Why not a learned fusion? | COVERED (negative) | `results/stacking.csv` (prereg 15) |
| Q4 | More training sources? | PARTIAL (SVM done) | `results/cross_dataset_svm.csv` (prereg 16); notebook 08 |
| Q5 | Are the nulls underpowered? | COVERED | `results/power_mde.csv` |
| Q6 | LLM baseline? | COVERED (negative; open 7B only) | `results/llm_baseline.csv` (prereg 17, D26) |
| Q7 | Published baseline under the same protocol | TODO-COLAB | notebook 09 |
| Q8 | More seeds | TODO-COLAB | notebooks 03, 04 |
| Q9 | Explanations of the deployed system | TODO-COLAB | notebooks 04, 06 |
| Q10 | Adequate human evaluation | TODO-AUTHOR | `docs/HUMAN_STUDY_PROTOCOL.md` |
| Q11 | Can an analyst get a candidate set with a coverage guarantee? | COVERED | `results/conformal.csv` (prereg 18) |
| Q12 | When should the system abstain? | COVERED | `results/selective.csv` (prereg 19) |
| Q13 | How much of the error is label noise? | PARTIAL (candidates; human check TODO-AUTHOR) | `results/label_noise_summary.csv` (prereg 20) |
| Q14 | Is the v12.1 label space still valid? | COVERED | `results/attack_drift.csv` (prereg 21) |
| Q15 | Reporting standard followed? | COVERED | `docs/REFORMS_CHECKLIST.md` |
| Q16 | Related work current to 2026? | COVERED | `docs/RELATED_WORK_VERIFIED.md` section F |
| Q17 | Does the demonstration tool (objective c) show the thesis' own numbers, and is its text grounded? | COVERED (replay verified; explanation usefulness not studied) | `results/app_verify.csv`, `app_live_timing.csv`, `app_grounding.csv` (ids `APP1`-`APP3`, D29) |
| Q18 | Do the draft's numbers match the registry? | COVERED for draft v2.2 (author fixes open) | `AUDIT_TODO.md`, `results/number_audit_v2_2/` (D30) |
