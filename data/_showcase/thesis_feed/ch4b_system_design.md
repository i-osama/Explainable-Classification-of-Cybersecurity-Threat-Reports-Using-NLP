# Chapter 4b (or Chapter 5 of a project-style thesis): the explainer application as a design-science artefact

All numbers are rendered from `thesis_numbers.json`. Screenshots and the demo script are in `ttp_app/docs/DEMO_GUIDE.md` (local; they show test sentences, so they are not in this upload).

## 4b.1 Research approach: design science
The thesis follows design science research: it builds an artefact for a real problem and evaluates it (Hevner et al. 2004; the six activities of Peffers et al. 2007). Mapping of the activities to this work:
| activity (Peffers et al. 2007) | in this thesis |
|---|---|
| 1 problem identification and motivation | analysts must map threat-report sentences to ATT&CK techniques and judge how far to trust a suggestion (ch1) |
| 2 objectives of a solution | (a) accurate technique ranking, (b) more training sources, (c) an explainable tool an analyst can use |
| 3 design and development | classifiers, matcher, fusion (ch3); the explainer application (this chapter) |
| 4 demonstration | replay of the 725 test sentences and a live mode (4b.6) |
| 5 evaluation | experiments with pre-registration (ch5, Q1_FINDINGS); artefact checks (4b.5); usability study `[PENDING: T9.usability_sus]` |
| 6 communication | thesis, report, reproducible package |

## 4b.2 Requirements
| id | requirement | how it is met | evidence |
|---|---|---|---|
| FR1 | rank ATT&CK techniques for a sentence | fused scores (3,1,1,1), top 5 shown | test P@1 0.803 |
| FR2 | give a candidate set with a stated coverage | split-conformal set, alpha 0.10 or 0.20, fitted on dev | coverage 0.894, mean size 2.80 |
| FR3 | say when to pass a sentence to an analyst | triage tier from the top-1 minus top-2 margin, dev thresholds | selective P@1 0.964 at coverage 0.455 |
| FR4 | warn where the model is weak | rare-label, retired-technique (ATT&CK drift) and known-confusion warnings | `G4`, `AD1`, confusions table |
| FR5 | show why | SHAP word highlights; caution when the explained model differs from the fusion | differs on 108 of 725 (14.9%) |
| FR6 | short written explanation that cannot invent evidence | template, or local qwen2.5:7b checked by grounding rule v1 | pass 23 of 100 (23%) |
| FR7 | state the limits next to the result | limits panel filled from the registry by id | `core.LIMITS` |
| FR8 | analyse new text | live mode, classifier-only | timings 4b.5 |
| NFR1 | reproduce the thesis numbers exactly | replay from saved scores, same formulas | 16 of 16 checks match |
| NFR2 | run on a CPU-only PC, no data leaves it | CPU inference; LLM only on localhost | live timings 4b.5 |
| NFR3 | no test-set tuning | thresholds fitted on dev only | prereg 18, 19; D29 |
| NFR4 | testable and maintainable | unit, integration and UI tests; small modules | 29 app tests pass |

## 4b.3 Architecture
Figure: `figures_app/architecture.png`. Data and runs (saved probabilities, matcher scores, stored SHAP) feed both the research pipeline and the app. `core.py` loads and fuses the saved scores and fits the dev thresholds; `live.py` runs the three classifiers and permutation SHAP on new text; `explain.py` writes the explanation and applies the grounding rule; `app.py` is the Streamlit user interface; `verify_artifacts.py` and the tests check the whole chain.

## 4b.4 Design decisions
- Replay from saved scores instead of retraining: the screen shows exactly the evaluated system, and every number can be checked against the thesis.
- Calibration on dev only, as pre-registered; the test set is only read.
- The explanation model is a local open-weights LLM behind a fixed grounding rule, so no text leaves the PC and the text can quote only SHAP evidence.
- Streamlit: a Python-only interface that reuses the research code.
- Honesty by design: limits panel, caution messages, `[PENDING]` for any missing number. Built with AI assistance (Claude, Claude Code), disclosed.

## 4b.5 Verification and validation of the artefact
- Reproduction: 16 of 16 checks match (`verify_artifacts.py`; the first run found one difference in the triage threshold rule, fixed with a test, D29).
- Tests: 29 app tests pass, 0 fail (unit tests, a fake thesis folder of the real shape, Streamlit AppTest of the user interface).
- Live mode on CPU (seconds, one run each): 7 words 2.4 / 8.4, 26 words 17.4 / 67.0, 54 words 76.9 / 300.3 at 10 / 40 permutations; additivity error at most 5.7e-07.
- Grounding of LLM text: 23 of 100 (23%) pass rule v1; 31 failures quote only the explained technique's own id or name (POST-HOC; rule v2 proposed, not applied).

## 4b.6 Demonstration
Five screens (see the demo guide): a correct sentence with a one-label set; a wrong sentence whose gold label is inside the conformal set; a retired technique; a rare label with low confidence and a caution message; the limits panel.

## 4b.7 Evaluation with users
Planned: 3-5 users, five tasks, System Usability Scale (Brooke 1996; benchmarks Bangor et al. 2008), descriptive only. Result: `[PENDING: T9.usability_sus]`. Kit: `ttp_app/usability/`.
