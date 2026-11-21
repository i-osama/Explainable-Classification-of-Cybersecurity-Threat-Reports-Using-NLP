"""T7: render README.md, INVIGILATOR_GUIDE.md, PROCESS_LOG.md, docs/*, CITATION.cff, LICENSE-NOTE.md, requirements.txt, run_all.ps1.
Every result number is a {{claim id}} resolved from thesis_numbers.json (scripts/_tpl.py); an unknown id aborts the build."""
import importlib.metadata as md, json, sys
from pathlib import Path
import pandas as pd, yaml
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _tpl import render, numbers, SHOW

N = numbers(); D = SHOW / "docs"; (D / "MODEL_CARDS").mkdir(parents=True, exist_ok=True)
def W(path, text): Path(path).write_text(render(text.strip() + "\n", N), encoding="utf-8")
st = yaml.safe_load((SHOW / "STATUS.yaml").read_text(encoding="utf-8"))["items"]
board = "\n".join(f"| {i['id']} | {i['area']} | {i['item']} | **{i['state']}** | {i['evidence']} |" for i in st)
tl = pd.read_csv(SHOW / "results" / "process_timeline.csv")
tlrows = "\n".join(f"| {str(r.first_timestamp)[:10]} | {str(r.last_timestamp)[:10]} | {r.track} | {r.event} | {r.evidence_files} | {r.basis} |" for _, r in tl.iterrows())
cnt = {}
for c in N.values(): cnt[c["status"]] = cnt.get(c["status"], 0) + 1
tests = json.loads((SHOW / "results" / "test_report.json").read_text())["counts"] if (SHOW / "results" / "test_report.json").exists() else {}

STORY = r"""
**Task.** Given one sentence from a cyber-threat-intelligence report, rank the MITRE ATT&CK techniques it describes, and show which words drove the top prediction,
so that an analyst can check the prediction instead of trusting it. Data: TRAM, {{A1}} sentences ({{A2}} train / dev / test), {{A3}} labels in training, {{A4}} in test of which {{A5.unseen}} never occur in training.

**What was built.** Four components (TF-IDF + linear SVM, RoBERTa, SecBERT, a fine-tuned bge bi-encoder that matches sentences to technique descriptions) and a late fusion of their
per-sentence z-scores with weights chosen on the development set only.

**What the evidence supports.**
- Fusion (3,1,1,1) reaches P@1 {{B13a}} {{B13a|ci}} with all components seed-averaged; {{B12a}} seed-paired; {{B12nb}} in the notebook's definition. It beats the classifiers-only ensemble ({{C1}}, Holm p {{C1.holm}}).
- Word-level SHAP explanations of the RoBERTa classifier are faithful to that model: masking the three top words lowers the predicted logit by {{E2.all}} more than masking three random words ({{E3.all}} sentences), and deletion, insertion, comprehensiveness and sufficiency all favour SHAP order.

**What the evidence does not support (reported as findings).**
- Transformers are not better than the SVM here: RoBERTa minus SVM is {{C3}} {{C3|ci}}, Holm p {{C3.holm}}.
- The fusion's gain over the matcher ensemble is not robust: {{C2}} {{C2|ci}}, exact McNemar p {{C2.p}}, Holm p {{C2.holm}}.
- The fusion does not help rare or unseen techniques: P@1 {{G4.fusion.unseen}} on the {{G4.n.unseen}} unseen-label sentences (matcher {{G4.matcher.unseen}}) and {{G4.fusion.1_4}} vs {{G4.matcher.1_4}} for labels with 1-4 training sentences. A pre-registered support-aware fusion did not fix this (success rule met: {{G9.v2.success}}).
- The first human plausibility study is at chance agreement (Krippendorff alpha {{D1}}); a second study is designed but not run.
- The explained model is one RoBERTa seed, not the fusion: their top-1 labels differ on {{E4}} test sentences. SHAP of the full fusion is not available (the matcher's weights were never saved).
- The published baseline (P@1 {{F1}}, MRR@3 {{F2}}) was not re-run; the comparison is side by side, not controlled.
"""

W(SHOW / "README.md", r"""
# Explainable classification of cyber-threat reports: research showcase

Sentence-level mapping of CTI text to MITRE ATT&CK techniques on TRAM, with word-level explanations. This folder is the auditable companion of the thesis:
code, data models, results, figures, notebooks, and an honest status board. Every number below is rendered from `thesis_numbers.json`.

## 60-second tour

1. **Task.** One sentence of a threat report in, a ranked list of ATT&CK techniques out, plus the words that drove the top prediction.
2. **Main result.** Fusion P@1 {{B13a}} {{B13a|ci}} (seed-averaged; {{B12a}} seed-paired). It beats the classifiers-only ensemble by {{C1}}. It does not beat the matcher ensemble after correction for 8 tests (Holm p {{C2.holm}}).
3. **Main limits.** No gain on rare or unseen techniques; explanations cover one RoBERTa model, not the fusion; the human study is at chance. Full list: `thesis_feed/DO_NOT_CLAIM.md`.
4. **Check it yourself.** `powershell -File demo.ps1` recomputes the headline numbers from the saved prediction files in under a minute and prints PASS or FAIL.
5. **Read it.** Open `report/index.html` (one offline file). What is still open: the status board below and `STATUS.yaml`.

## One-page story
""" + STORY + r"""

## Verify in 10 minutes

See `INVIGILATOR_GUIDE.md`. Short version, from this folder, with the project's Python:

```
python scripts/run_tests.py        # unit, leakage, determinism and regression tests
python scripts/verify_claims.py    # recomputes the headline numbers from saved predictions
python scripts/check_hashes.py     # SHA-256 of every input and shipped output
start report\index.html            # the whole story, offline
```

## Status board

| id | area | item | state | evidence |
|---|---|---|---|---|
""" + board + r"""

Truth file: """ + f"{len(N)} entries: " + ", ".join(f"{k} {v}" for k, v in sorted(cnt.items())) + r""". Nothing marked TODO-COLAB or NOT-FOUND carries a value.

## Folder map

| path | content |
|---|---|
| `thesis_numbers.json`, `THESIS_MAP.md` | single source of truth for every number; map from thesis item to file and script |
| `THESIS_PLACEHOLDERS.md` | answers to the open items of the draft, plus the number audit of the draft |
| `GAP_REGISTER.md`, `PLAN.md`, `PROGRESS.md`, `DECISIONS.md`, `STATUS.yaml`, `PROCESS_LOG.md` | what was missing, what was planned, what was done, why |
| `src/ttpmap/` | package: data models, loaders, the one metric implementation, fusion with dev-only guards, statistics, explanation utilities, figures, CLI |
| `tests/`, `scripts/` | tests; `verify_claims.py`, `check_hashes.py`, analysis and build scripts |
| `experiments/prereg/` | pre-registrations, sealed with timestamp and SHA-256 before the analysis ran |
| `results/` | CSV per analysis, typed tables (`tables/*.parquet`, no sentence text), hashes, smoke logs |
| `figures/` | 19 figures as PNG and SVG, `FIGURES.md` |
| `notebooks/` | Colab notebooks 00-10 and `RUN_ORDER.md`; none has been run on Colab |
| `docs/` | data card, data dictionary, model cards, ethics, threats to validity, verified references, human-study protocol |
| `report/index.html` | self-contained report |
| `../_evidence_pack/` | the earlier audit of the 40 claims of the draft (read-only base) |

## What is not here

Model weights, the TRAM sentences, rating sheets and the baseline paper are not in this folder or in the repository (size, unknown data licence, privacy).
`docs/DATA_CARD.md` says how to obtain the data; `notebooks/04_train_matcher_save.ipynb` retrains the one model whose weights were never saved.

## AI assistance

Claude Code (Anthropic) was used for engineering and analysis in this folder: refactoring the notebooks' analysis code into a package, writing tests and scripts,
recomputing every number from saved predictions, generating figures, notebooks and this documentation. The experiments' design, the original training runs and the
interpretation are the author's; the author checks and finalises all wording according to the university's AI-use policy and must be able to explain every number and decision.
No text here was written or altered to evade AI-detection tools.
""")

W(SHOW / "INVIGILATOR_GUIDE.md", r"""
# Invigilator guide: verify the work in five steps

Environment: Windows, `E:\Osamas Paper\.venv\Scripts\python.exe -X utf8`, CPU only. Run from `E:\Osamas Paper\_showcase`. Steps 1-3 and 5 need about three minutes together.

| step | command | what it proves | expected |
|---|---|---|---|
| 1 | `python scripts\run_tests.py` | metrics are correct on hand-computed cases; ties and empty predictions are handled; tuning functions refuse test ids (leakage test); results are deterministic; headline numbers reproduce within 0.001 | """ + f"{tests.get('PASS', '?')} passed, {tests.get('FAIL', '?')} failed" + r""" |
| 2 | `python scripts\verify_claims.py` | the 40 claims of the draft are all in the truth file; 13 headline numbers are recomputed from the saved prediction files and compared with it | `VERIFY: PASS` |
| 3 | open `report\index.html` | the story, results with intervals, negative findings, status board, in one offline file | - |
| 4 | open `notebooks\RUN_ORDER.md`, then a notebook on Colab | every training or GPU step is scripted, resumable, and marked NOT RUN where it has not run | header says "NOT RUN ON COLAB" |
| 5 | `python scripts\check_hashes.py` | inputs and shipped outputs match the recorded SHA-256 values | `HASHES: PASS` |

`pytest` is not installed in this environment (installation was not permitted in the build session); the test files are plain `test_*` functions and run unchanged under `pytest` once it is installed.

## One page: from raw data to every table

```
Dataset/tram_dev.tsv, tram_test.tsv            Dataset/combined_train.csv  (rows with source_dataset == "tram" = train)
Dataset/ttp-desc-mappings.csv (733 labels)     saved model outputs: Exp_1_4_run_tram_2_epoc_30/*_pw_s4{2,3,4}/*_probs.npy,
                                               run_match_1/ft20_s4{2,3,4}/*_scores.npy, run_match_1/zeroshot/test_scores.npy
            |                                              |
            +-------------------- src/ttpmap/data.py: build_space() ----------------+   (SVM refit here: deterministic)
                                           |
        src/ttpmap/fusion.py (z-scores, weights, dev-only guards)   src/ttpmap/metrics.py (P@1, MRR@3, F1)   src/ttpmap/stats.py
                                           |
  scripts/run_analyses.py ---------> results/systems, per_seed, f1_variants, comparisons, ablation, weight_surface, threshold_grid,
                                     support_buckets, fixed_broken, tactics, confusions, parent_sub, calibration, overlap_sensitivity,
                                     explained_vs_fusion, support_aware_*.csv ; results/tables/*.parquet
  scripts/run_support_aware_v2.py -> results/support_aware_v2.csv, support_aware_family.csv
  scripts/run_inference.py --------> results/faithfulness*.csv, maxlen.csv, efficiency.csv, hardware.json   (CPU inference, about 7 min)
                                           |
  scripts/build_numbers.py --------> thesis_numbers.json  (one entry per number; id, value, CI, definition, source, status)
                                           |
  scripts/build_thesis_feed.py ----> thesis_feed/tables/t_*.csv + .md, chapter files     scripts/make_figures.py -> figures/fig*.png, .svg
  scripts/build_docs.py, build_report.py -> README.md, docs/*, report/index.html          scripts/verify_claims.py, qa_gates.py -> checks
```

Thesis table to file: every table in `thesis_feed/tables/` names its source in its file name (`t_systems` from `results/systems.csv`, `t_comparisons_holm` from
`results/comparisons.csv`, `t_support_buckets` from `results/support_buckets.csv`, and so on); the builder is `scripts/build_thesis_feed.py`.
Rebuild all of it: `powershell -File run_all.ps1` (about 10 minutes; `-Fast` skips the CPU inference).

## Questions an examiner may ask, and where the answer is

| question | answer in |
|---|---|
| Were weights, thresholds or epochs tuned on the test set? | `src/ttpmap/fusion.py` (guards), `tests/test_project_data.py::test_tuning_never_sees_test_ids`, `_evidence_pack/02_settings.md` (review focus) |
| Which fusion number is the headline, and why are there three? | `THESIS_PLACEHOLDERS.md` section 4; ids B12a, B12nb, B13a in `THESIS_MAP.md` |
| Is the gain significant after correcting for multiple tests? | `results/comparisons.csv`, figure fig07 |
| Does the system work on rare and unseen techniques? | `results/support_buckets.csv`, figures fig06 and fig10 (it does not) |
| Do the explanations explain the reported system? | `results/explained_vs_fusion.csv`; README, last bullet of the story (only partly) |
| Was anything decided after seeing the result? | `experiments/prereg/REGISTRY.csv` (timestamps and hashes), `DECISIONS.md` D08 |
| What is missing? | status board in `README.md`; `GAP_REGISTER.md`; NOT-FOUND entries in `THESIS_MAP.md` |
""")

W(SHOW / "PROCESS_LOG.md", r"""
# Process log

Only events with file evidence. Dates of the experimental phase are **reconstructed from file timestamps** (modification times of result files and notebooks;
`results/process_timeline.csv`, built by `scripts/build_timeline.py`). They show when files were last written, not how long the work took.

## Timeline

| first file | last file | track | event | evidence | basis |
|---|---|---|---|---|---|
""" + tlrows + r"""

## Audit phase (14 November 2026, from `_evidence_pack/PROGRESS.md` and the git log)

1. Evidence pack T0-T10: every claim of the draft recomputed from saved predictions; ledger of 40 claims; the leakage review; the baseline paper read from arXiv.
2. Deletion test re-run on all eligible test sentences; SHAP of the classifier part of the fusion on 40 sentences.
3. A local CPU retraining of the matcher was started and stopped during its first epoch (about two hours per epoch); no weights were produced and nothing from it is used.
4. Showcase: package, tests, pre-registered analyses, figures, notebooks, report. Commits are in the private repository from 14 November 2026 onward.

## The 15 contradictions between the draft and the files, and how each was resolved

| # | contradiction (as found in the evidence pack) | resolution |
|---|---|---|
| 1 | the draft attributed (3,1,1,1) to the 1,711-setting grid | files: {{B14}}. Draft corrected to say so; both grids reported |
| 2 | seed-averaged fusion MRR@3 given as 0.853 | file value {{B13b}}; corrected |
| 3 | "2 test and 1 dev sentence also in train" | {{A6}}; corrected in the text. One table cell still carries the old wording (`THESIS_PLACEHOLDERS.md` section 14) |
| 4 | two fusion headline numbers with different meanings | both kept with definitions: seed-paired {{B12a}}, notebook {{B12nb}}, seed-averaged {{B13a}}; the draft headlines the seed-paired value; author to confirm |
| 5 | P@1 of RoBERTa and SecBERT were 3-seed ensembles presented beside single-seed F1 | both stated: ensembles {{B7}} and {{B8}}, single-seed means {{B1.p1_seedmean}} and {{B2.p1_seedmean}} |
| 6 | equal-weight fusion compared on a different matcher | both stated: {{B11}} (matcher seed 42) and {{B11.avg}} (3-seed matcher) |
| 7 | "34 truncated sentences" for all models | {{A7}} |
| 8 | "733 description entries" | {{A8}} |
| 9 | fusion vs matcher ensemble presented as significant | borderline: {{C2}} {{C2|ci}}, McNemar p {{C2.p}}, Holm p {{C2.holm}}; reported as not robust |
| 10 | SHAP sample believed to be 100 sentences | the stored file covers {{E1.n}} sentences; the deletion test and rating sheet use the first 100 |
| 11 | "fusion helps on unseen techniques" | P@1 {{G4.fusion.unseen}} on unseen labels; unseen R@5 {{G6.unseen_r5_fusion}} vs {{G6.unseen_r5_clsonly}} for the classifiers; reported as a limitation |
| 12 | notebook F1 ignores the unseen test labels | three variants computed; micro-F1 drops by {{G2.roberta.micro_drop}} (RoBERTa) when unseen gold labels count as misses |
| 13 | RoBERTa threshold on the edge of its grid | extended grid checked: thresholds {{G3.roberta.thr_new}}; test micro-F1 changes by {{G3.roberta.delta}} on average |
| 14 | baseline R@1 compared with a different quantity | the paper's per-sample definition implemented in `notebooks/09_baseline_same_protocol.ipynb`; R@1 is not compared in the thesis |
| 15 | description file called CSV; venue of the baseline unconfirmed | file is tab-separated; venue confirmed by web search as Findings of EACL 2024 (`docs/RELATED_WORK_VERIFIED.md`) |
""")

W(D / "DATA_CARD.md", r"""
# Data card

| | |
|---|---|
| Name | TRAM sentence-level ATT&CK technique annotations, in the split distributed with the repository of Nguyen et al. |
| Unit | one sentence (or short passage) of a cyber-threat-intelligence report with one or more ATT&CK technique or sub-technique ids |
| Sizes | {{A1}} sentences: {{A2}} (train / dev / test). Train after exact-text de-duplication |
| Labels | {{A3}} in train, {{A4}} in test ({{A5}} seen + unseen); {{A9.multi_test}} test sentences carry more than one label; {{A9.pairs_test}} gold (sentence, label) pairs in test |
| Long tail | median {{A9.median_support}} training sentences per label; {{A9.rare_train}} labels have fewer than 5 |
| Overlap | {{A6}} |
| Length | {{A7}} test sentences exceed 128 tokens |
| Label descriptions | `ttp-desc-mappings.csv` (tab-separated): {{A8}} |
| Sibling data | `combined_train.csv`: {{A10.combined_rows}} rows from three sources ({{A10.rows.procedure}} procedure, {{A10.rows.tram}} tram, {{A10.rows.derived_procedure}} derived_procedure), {{A10.combined_labels}} labels; used only as the source of the TRAM train rows |
| Source | description file: `github.com/tumeteor/mitre-ttp-mapping` (URL in `Exp_2.1` CELL 1); original annotations: `github.com/center-for-threat-informed-defense/tram` |
| Licence | No licence file in the project. The Hugging Face dataset card lists "cc" without a variant (DOI 10.57967/hf/1811), as reported by the author; variant [FILL]. Because the variant is unknown, this showcase ships no sentence text: only ids, SHA-256 hashes, lengths, labels and derived metrics (`results/tables/sentences.parquet`) |
| ATT&CK version | "version 12" according to notebook comments and the baseline paper; **no version string inside any data file** |
| Known issues | annotation noise is reported in the literature; one normalised test sentence also occurs in train; `tram_train.tsv` itself is not in the folder and is rebuilt from `combined_train.csv` |

## Obtaining the data

1. TRAM dev and test: the files `tram_dev.tsv`, `tram_test.tsv` of the baseline repository. 2. Train: `python ../_evidence_pack/09_repro/make_tram_train.py`.
3. Check: `python scripts/check_hashes.py` compares the files with the recorded hashes.

## Intended and unintended use

Research on mapping CTI text to ATT&CK. Not validated for operational triage: accuracy on rare techniques is low and labels are noisy.
""")

W(D / "DATA_DICTIONARY.md", r"""
# Data dictionary

Models are defined in `src/ttpmap/schema.py` (pydantic); every shipped row is validated against them by `scripts/run_analyses.py`.
ER diagram: `figures/fig03_er_diagram.png`; Mermaid source below.

| table (file) | model | key | fields |
|---|---|---|---|
| `results/tables/sentences.parquet` | Sentence | `id` = `<split>-<4 digits>` (row position in the split) | `split`, `text_sha256` (SHA-256 of the raw text; the text is not shipped), `n_words`, `labels` (sorted unique technique ids) |
| `results/tables/techniques.parquet` | Technique | `id` (`T1234` or `T1234.001`) | `name`, `tactics` (ATT&CK v12.1 STIX), `parent_id`, `is_sub`, `train_support`, `dev_support`, `test_support` |
| `results/tables/score_matrices.parquet` | ScoreMatrix | (`system`, `seed`, `split`) | `n_sentences`, `n_labels`, `score_kind` (probability, cosine, decision_function), `source_file`, `sha256` |
| `results/tables/predictions.parquet` | Prediction | (`sentence_id`, `system`) | `top1`, `top2`, `top3`, `hit_at_1`, `rr_at_3` (test split, 9 systems) |
| notebook manifests (`manifest_*.json`) | RunManifest | `run_id` | `system`, `seed`, `config_hash`, `env`, `input_sha256`, `output_sha256`, `metrics`, `status` |
| `thesis_numbers.json` | Claim | `id` | `label`, `value`, `display`, `ci`, `definition`, `source_file`, `script`, `status`, `thesis_section`, `note` |

Conventions: technique ids are upper-case; a sub-technique is a different label from its parent; ranking ties go to the lower label index; `seed` is an integer, `avg` (mean over seeds 42-44) or `-` (deterministic).

```mermaid
erDiagram
    SENTENCE }o--o{ TECHNIQUE : "labels"
    SENTENCE ||--o{ PREDICTION : "has"
    PREDICTION }o--|| TECHNIQUE : "top1..top3"
    SCOREMATRIX }o--o{ TECHNIQUE : "columns"
    RUNMANIFEST ||--o{ SCOREMATRIX : "produces"
    RUNMANIFEST ||--o{ CLAIM : "feeds"
    SENTENCE { string id PK
               string split
               string text_sha256
               int n_words }
    TECHNIQUE { string id PK
                string name
                string parent_id FK
                bool is_sub
                int train_support }
    PREDICTION { string sentence_id FK
                 string system
                 string top1 FK
                 bool hit_at_1 }
    CLAIM { string id PK
            string display
            string status
            string source_file }
```
""")

CARD = r"""
# Model card: {name}

| | |
|---|---|
| Role | {role} |
| Architecture | {arch} |
| Training data | TRAM train, {{A2.train}} sentences, {{A3}} labels |
| Settings | {settings} |
| Selection | {selection} |
| Seeds | {seeds} |
| Test results | {results} |
| By label frequency | {tail} |
| Efficiency | {eff} |
| Artefacts | {artefacts} |
| Limitations | {limits} |
| Not for | operational use without analyst review; techniques absent from or rare in the training data |
"""
cards = {
 "svm": dict(name="TF-IDF + linear SVM", role="classical baseline and fusion component", arch="word 1-2 gram TF-IDF (sublinear tf), one-vs-rest LinearSVC",
             settings="C = 1.0, no class weights, random_state 42 (`Exp_1_4` CELL 6)", selection="global decision threshold {{B3.thr}} on dev micro-F1; arg-max fallback", seeds="deterministic",
             results="micro-F1 {{B3}}; macro-F1 {{B3.macro117}} (seen test labels) / {{B3.macro127}} (all test labels); P@1 {{B6}} {{B6|ci}}", tail="P@1 {{G4.svm.unseen}} unseen, {{G4.svm.1_4}} for 1-4 training sentences, {{G4.svm.50plus}} for 50+",
             eff="{{G10.params.svm}} weights; {{G10.ms.svm}} ms per sentence (CPU, median)", artefacts="no saved scores; refit is deterministic and reproduces the notebook output", limits="cannot output a label unseen in training"),
 "roberta": dict(name="RoBERTa-base classifier", role="neural classifier, fusion component, and the model explained with SHAP (seed 42)", arch="`roberta-base` with a multi-label classification head over the train labels",
             settings="max length 128, batch 16, lr 2e-5 (encoder) / 1e-3 (head), up to 30 epochs, patience 5, BCE with positive weight capped at 20 (`Exp_1_4` CELL 8)", selection="epoch and threshold on dev micro-F1", seeds="42, 43, 44",
             results="micro-F1 {{B1}}; macro-F1 {{B4}}; P@1 single-seed mean {{B1.p1_seedmean}}, 3-seed average {{B7}} {{B7|ci}}; ECE {{G7.ece.roberta}}", tail="P@1 {{G4.roberta.unseen}} unseen, {{G4.roberta.1_4}} for 1-4, {{G4.roberta.50plus}} for 50+",
             eff="{{G10.params.roberta}} parameters; {{G10.ms.roberta}} ms per sentence (CPU, median, one seed)", artefacts="probabilities and weights saved for all seeds", limits="not better than the SVM with statistical support ({{C3}} {{C3|ci}}); over-confident; dev threshold at the edge of the original grid"),
 "secbert": dict(name="SecBERT classifier", role="domain-specific neural classifier and fusion component", arch="`jackaduma/SecBERT` with a multi-label classification head", settings="as RoBERTa", selection="as RoBERTa", seeds="42, 43, 44",
             results="micro-F1 {{B2}}; macro-F1 {{B5}}; P@1 single-seed mean {{B2.p1_seedmean}}, 3-seed average {{B8}} {{B8|ci}}; ECE {{G7.ece.secbert}}", tail="P@1 {{G4.secbert.unseen}} unseen, {{G4.secbert.1_4}} for 1-4, {{G4.secbert.50plus}} for 50+",
             eff="{{G10.params.secbert}} parameters; {{G10.ms.secbert}} ms per sentence (CPU, median, one seed)", artefacts="probabilities and weights saved for all seeds", limits="no measurable advantage over RoBERTa ({{C4}} {{C4|ci}})"),
 "matcher": dict(name="bge bi-encoder matcher", role="retrieval component: ranks all {{A8.space}} technique descriptions, so it can output techniques unseen in training", arch="`BAAI/bge-base-en-v1.5`, shared encoder for sentences and descriptions, [CLS] pooling, cosine",
             settings="InfoNCE-style loss with 64 random negatives, scale 30, batch 16, lr 2e-5, up to 20 epochs, patience 4 (`Exp_2.1` CELL 3, 7)", selection="epoch on dev MRR@3", seeds="42, 43, 44",
             results="zero-shot P@1 {{B10a}}; fine-tuned {{B10b}}; 3-seed ensemble {{B10c}} {{B10c|ci}}", tail="P@1 {{G4.matcher.unseen}} unseen, {{G4.matcher.1_4}} for 1-4, {{G4.matcher.50plus}} for 50+: the best component on rare labels",
             eff="{{G10.params.matcher}} parameters; {{G10.ms.matcher}} ms per sentence (CPU, median), timed with the public base checkpoint", artefacts="**score files only; the fine-tuned weights were never saved** (notebook 04 retrains with saving)", limits="cannot be re-run, explained or timed exactly until retrained"),
 "fusion": dict(name="Late fusion (3,1,1,1)", role="the reported system", arch="weighted sum of per-sentence z-scores: matcher 3, SVM 1, RoBERTa 1, SecBERT 1", settings="weights from the dev winner of the coarse grid: {{B14}}", selection="dev MRR@3, tie-break dev P@1; guarded against test ids in code",
             seeds="three definitions: seed-averaged, seed-paired, matcher seed varied", results="P@1 {{B13a}} {{B13a|ci}} (seed-averaged), {{B12a}} (seed-paired), {{B12nb}} (notebook); MRR@3 {{B13b}}; vs classifiers-only {{C1}} (Holm p {{C1.holm}}); vs matcher ensemble {{C2}} (Holm p {{C2.holm}})",
             tail="P@1 {{G4.fusion.unseen}} unseen, {{G4.fusion.1_4}} for 1-4, {{G4.fusion.50plus}} for 50+: worse than the matcher on rare labels, better on frequent ones", eff="sum of the components; about ten transformer passes per sentence in the seed-averaged form",
             artefacts="recomputed from saved scores by `scripts/verify_claims.py`", limits="gain over the matcher ensemble is not robust; no gain on rare or unseen techniques; explanations exist for one component only"),
}
for k, c in cards.items(): W(D / "MODEL_CARDS" / f"{k}.md", CARD.replace("{{", "<<").replace("}}", ">>").format(**{a: b.replace("{{", "<<").replace("}}", ">>") for a, b in c.items()}).replace("<<", "{{").replace(">>", "}}"))

W(D / "ETHICS_AND_LIMITATIONS.md", r"""
# Ethics and limitations

## Dual use
The system reads defensive threat reports and names the attack techniques they describe. It produces no exploit, payload or procedure; ATT&CK itself is public.
The realistic misuse is indirect: automated labelling could help an adversary index public reporting about their own tooling. That information is already public and the risk is judged low.

## Risks of use
- **Over-trust.** P@1 is {{B13a}}: about one top prediction in five is wrong, and on rare techniques most are (P@1 {{G4.fusion.1_4}} for labels with 1-4 training sentences, {{G4.fusion.unseen}} for unseen ones). Output is a suggestion for an analyst, never a decision.
- **Over-confidence.** The classifiers' top-1 probability averages {{G7.conf.roberta}} for RoBERTa while its accuracy is lower (ECE {{G7.ece.roberta}}); probabilities must not be shown as certainty.
- **Explanations can mislead.** They are faithful to one RoBERTa model, not to the fused system (different top-1 label on {{E4}} sentences), and human agreement on their plausibility is at chance in the only study run (alpha {{D1}}).
- **Label noise and coverage.** TRAM covers {{A3}} of the ATT&CK techniques in training; a sentence about any other technique cannot be labelled correctly by three of the four components.

## Data and privacy
The data are sentences from published threat reports. No personal data were collected for training. Human raters are recorded by role only; rating sheets stay out of the repository.
The dataset licence is not documented in the project, so no sentence text is redistributed here.

## Limitations of the study
One dataset and one split; three seeds; a baseline taken from its paper; an inconclusive human study; no robustness test under paraphrase or adversarial edits;
efficiency measured on one desktop CPU. `docs/THREATS_TO_VALIDITY.md` treats these in detail.

## AI assistance
See the section "AI assistance" in `README.md`.
""")

W(D / "THREATS_TO_VALIDITY.md", r"""
# Threats to validity

## Internal (is the measured effect real?)
| threat | evidence | mitigation / status |
|---|---|---|
| tuning on test | selection code takes dev only and raises on test ids; the leakage test passes | controlled. Residual: test scores of the ten best wide-grid settings were printed in the original notebook before weights were fixed; the kept setting has the lower test score ({{B14.test3111}} vs {{B14.test4111}}) |
| the test set was looked at repeatedly during development | notebooks print test metrics at many steps | cannot be undone; new analyses are pre-registered and the family of tests is Holm-corrected |
| train-test overlap | {{A6}} | removing the overlap changes P@1 by at most {{G12.exact_near.maxdelta}} |
| threshold grid too narrow | RoBERTa thresholds {{G3.roberta.thr_old}} at the grid edge | extended grid changes test micro-F1 by {{G3.roberta.delta}} on average |
| implementation differences between systems | one metric implementation, unit-tested; stored metrics reproduce | controlled |
| matcher weights lost | score files only | fusion cannot be re-run on new text or explained until notebook 04 is run |

## Construct (do the measures mean what is claimed?)
| threat | status |
|---|---|
| P@1 and MRR@3 against noisy single annotations treat a plausible alternative technique as an error | open; the confusion table shows semantically close pairs |
| F1 as computed in the notebooks ignores the {{A5.unseen}} unseen test labels | three variants reported; micro-F1 drops by {{G2.roberta.micro_drop}} when they count |
| "explainable" is measured as faithfulness to one component | stated; fusion-level explanation is open work |
| plausibility judged by two raters on a three-point scale | agreement at chance (alpha {{D1}}); a five-point protocol with controls is written, not run |
| per-sample vs micro definitions of recall differ between this work and the baseline paper | R@1 is not compared; notebook 09 implements the paper's definitions |

## External (does it generalise?)
| threat | status |
|---|---|
| one dataset, short sentences, {{A3}} of several hundred techniques | open; objective (b) on the sibling datasets is scripted (notebook 08), not run |
| one ATT&CK version, not pinned inside the data | open |
| comparison with the published baseline is not on verified-identical data or training mode | open; reported as side by side |
| latency measured on one desktop CPU | descriptive only (`results/hardware.json`) |

## Conclusion (are the statistics sound?)
| threat | status |
|---|---|
| three seeds give a weak estimate of seed variance | mean and sd reported; seeds 45-46 scripted, not run |
| the bootstrap resamples sentences, not seeds or training data | stated with every interval |
| multiplicity | Holm over a family of 8 fixed in advance; only fusion vs classifiers-only and the matcher and RoBERTa ablations stay supported |
| borderline result reported as a gain | fusion vs matcher ensemble: {{C2}} {{C2|ci}}, Holm p {{C2.holm}}: reported as not robust |
| small buckets | unseen (n = {{G4.n.unseen}}) and 1-4 (n = {{G4.n.1_4}}) have wide intervals; shown with intervals, not interpreted beyond direction |
""")

W(SHOW / "CITATION.cff", r"""
cff-version: 1.2.0
message: "If you use this material, please cite the thesis. Fields marked [FILL] must be completed by the author."
title: "Explainable Classification of Cybersecurity Threat Reports Using Natural Language Processing: Sentence-Level Mapping to MITRE ATT&CK Techniques"
type: software
authors:
  - family-names: "[FILL]"
    given-names: "[FILL]"
date-released: "2026-11-14"
repository-code: "[FILL: public repository URL, if the code is published]"
license: "[FILL]"
""")

W(SHOW / "LICENSE-NOTE.md", r"""
# Licence note

Licence of this repository: [FILL: chosen by the author with the university; not chosen by the build]. Until then, all rights are reserved by the author and the repository is private (status board S25).

Third-party material and what is (not) included:

| material | licence status | included here |
|---|---|---|
| TRAM sentences and labels | the Hugging Face dataset card lists licence "cc" without a variant (DOI 10.57967/hf/1811), as reported by the author; the exact variant is [FILL: author to confirm on the card] | **no text**; ids, hashes, labels, derived metrics only |
| `ttp-desc-mappings.csv` (ATT&CK descriptions, from the baseline repository) | not documented in the project; MITRE ATT&CK content has its own terms of use | not included |
| ATT&CK v12.1 STIX (used for tactic names) | MITRE ATT&CK terms of use | derived id-to-tactic table only |
| `roberta-base`, `jackaduma/SecBERT`, `BAAI/bge-base-en-v1.5` | see the model pages on the Hugging Face hub | not included (weights) |
| baseline paper (arXiv:2401.10337) | publisher / authors | not included; short quotations in `_evidence_pack/08_baseline.md` |
""")

pk = sorted({f"{d.metadata['Name']}=={d.version}" for d in md.distributions() if d.metadata["Name"]}, key=str.lower)
(SHOW / "requirements.txt").write_text("# Exact versions of the analysis environment that produced this showcase (CPU; Python " + sys.version.split()[0] + ").\n"
    "# torch is the CPU build: install from https://download.pytorch.org/whl/cpu . pytest is optional (tests also run with scripts/run_tests.py).\n"
    "# Training environment (Colab): only transformers 5.22.1, torch 2.14.1+cu130 and shap 0.54.1 are known from files; notebook 00 records the rest.\n" + "\n".join(pk) + "\n", encoding="utf-8")
(SHOW / "run_all.ps1").write_text(r"""# Rebuild everything that can be rebuilt on this PC (CPU, no training).  Usage:  powershell -File run_all.ps1 [-Fast]
param([switch]$Fast)
$ErrorActionPreference = "Stop"
$py = "E:\Osamas Paper\.venv\Scripts\python.exe"
Set-Location $PSScriptRoot
$steps = @("scripts\make_prereg.py", "scripts\run_tests.py", "scripts\run_analyses.py", "scripts\run_support_aware_v2.py")
if (-not $Fast) { $steps += "scripts\run_inference.py" }          # about 7 minutes of CPU inference
$steps += @("scripts\build_timeline.py", "scripts\build_numbers.py", "scripts\audit_from_ledger.py", "scripts\build_placeholders.py", "scripts\make_figures.py",
            "scripts\make_notebooks.py", "scripts\build_docs.py", "scripts\build_report.py", "scripts\verify_claims.py", "scripts\qa_gates.py")
foreach ($s in $steps) {
    $t = Get-Date
    & $py -X utf8 $s *> "$env:TEMP\ttpmap_step.log"
    $ok = $LASTEXITCODE -eq 0
    "{0}  {1,-36} {2,5:N0}s" -f ($(if ($ok) { "OK  " } else { "FAIL" }), $s, ((Get-Date) - $t).TotalSeconds)
    if (-not $ok) { Get-Content "$env:TEMP\ttpmap_step.log" -Tail 15; exit 1 }
}
""", encoding="utf-8")
print("docs written: README, INVIGILATOR_GUIDE, PROCESS_LOG, DATA_CARD, DATA_DICTIONARY, 5 model cards, ETHICS, THREATS, CITATION.cff, LICENSE-NOTE, requirements.txt, run_all.ps1")
