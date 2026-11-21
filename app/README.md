# ATT&CK threat-report explainer (thesis objective c)

Streamlit app for the thesis "Explainable Classification of Cybersecurity Threat Reports Using NLP".
For one threat-report sentence it shows: ranked ATT&CK techniques, a conformal set, a triage tier, warnings (rare label, retired technique, known confusion), SHAP word highlights, and a short written explanation.
CPU only. No data leaves the machine (the optional LLM is local Ollama).

## Run it

| Step | Command (Windows, from this folder) | Needs |
|---|---|---|
| 0. Any PC | copy the portable folder `E:\TTP_DEMO` and double-click `START_DEMO.bat` (own Python, no install, no internet; see `portable/README_DEMO.md`). Built by `_showcase/scripts/build_portable_demo.py` | inside the folder |
| 0b. This PC | double-click `run_app.bat`, then follow `docs/DEMO_GUIDE.md` | the thesis folder one level up |
| 1. Demo, no thesis data | `pip install -r requirements.txt` then `set TTPMAP_DEMO=1` and `streamlit run app.py` | nothing else. Data is synthetic and labelled so on screen. |
| 2. Real replay | `set TTPMAP_ROOT=E:\Osamas Paper` then `streamlit run app.py` | the thesis folder (layout below) |
| 3. Check it matches the thesis | `python verify_artifacts.py` | same folder + `results/*.csv` |
| 4. Live mode | `pip install -r requirements-live.txt`, pick "Live: full fusion (3,1,1,1)" or "Live: classifiers only" in the sidebar | checkpoints seed 42; the full fusion also needs the retrained matcher (`_showcase/results/colab/matcher_ft20_s42/matcher_state.pt`) and the bge-base tokenizer |
| 5. Written explanations | install Ollama, `ollama pull qwen2.5:7b`, tick the sidebar toggle | Ollama running |
| 6. Grounding pass rate | `python grounding_report.py 100` | Ollama running |

**Do step 3 before you show anything.** `verify_artifacts.py` recomputes P@1, conformal tau/coverage/size, triage coverage and selective P@1 from the saved scores and compares them with `results/conformal.csv`, `selective.csv`, `explained_vs_fusion.csv`. Any `DIFF` means the app does not reproduce the thesis. On the thesis PC (15 Nov 2026) all 16 checks match; see "Checks run on the thesis machine".

Thesis folder layout the loader expects (same as notebooks 05 and 06):

```
Dataset/tram_{train,dev,test}.tsv, ttp-desc-mappings.csv
Exp_1_4_run_tram_2_epoc_30/{roberta,secbert}_pw_s{42,43,44}/  mlb_classes.npy dev_probs.npy test_probs.npy (+ checkpoint for live mode)
run_match_1/ft20_s{42,43,44}/  dev_scores.npy test_scores.npy      (or run_match_2_saved/ once notebook 04 has run)
Exp_3_0_shap/shap_v2_roberta_pw_s42.jsonl                          (fields used: row, pred_label, shap_values)
results/*.csv and thesis_numbers.json                               (optional; set TTPMAP_RESULTS / TTPMAP_NUMBERS if elsewhere)
```

## What is real, what is pending

| Part | Status |
|---|---|
| Replay of the 725 test sentences: fusion (3,1,1,1) ranking, from saved scores | built; **run `verify_artifacts.py`** |
| Conformal set (prereg 18 score rule, fitted on dev) and margin triage (prereg 19) | built; same check |
| SHAP words in replay | stored run: **RoBERTa seed 42 only**, not the fusion. On 108 of 725 sentences (E4) its top-1 differs from the fusion's; the app warns on those |
| Live mode | **classifier-only** (SVM + RoBERTa s42 + SecBERT s42, equal weights), live SHAP with a speed knob for permutations (40 = thesis setting). Conformal/triage thresholds are fitted on dev and **not evaluated on test**: no coverage claim. Run on the real seed-42 checkpoints on 15 Nov 2026 (timings below). |
| Live full fusion | Added 16 Nov 2026. Matcher (retrained on Kaggle, notebook 04, seed 42) + SVM + RoBERTa s42 + SecBERT s42, weights (3,1,1,1), same code as notebook 06, live SHAP of the fused score. Thresholds fitted on dev, **not evaluated on test**. `check_live_parity.py` compares it with the stored scores: matcher difference 5.2e-4 on 20 test sentences, same top-1 as notebook 06 on 5 of 5. Build-time test P@1 of this seed-42 system: 0.790 [0.761, 0.819] (`_build/live_parity.json`; not a thesis number). |
| Report mode | Added 16 Nov 2026. Paste a report or upload .txt/.md/.csv: every sentence (up to 300) is scored with the live full fusion (seed 42), tier and conformal-set size; CSV download; SHAP on request for one sentence. Measured: 5 sentences in 0.2 s. |
| Teach mode | Added 16 Nov 2026. Labelled lines (`T1529: sentence`) or a CSV refit the SVM (same recipe as `load_replay`) on train + the new sentences, and refit the dev-only thresholds. Session only: nothing is written to disk, and replay and thesis numbers never change. Shows the SVM top-3 before and after; Live and Report modes then use the new SVM under a banner, with an Undo. Not evaluated on test. |
| Replay fusion SHAP | Added 16 Nov 2026. For the 100 test sentences of notebook 06 (T2.full_fusion_shap), replay shows the SHAP of the full fusion (seed 42); for the other sentences, the RoBERTa seed 42 SHAP. The caption says which. |
| Written explanation | new, **no evaluation**. Template by default; local qwen2.5:7b optional |

## Written explanations and the grounding rule

GROUNDING RULE v1 (in `explain.py`, fixed before any model output was read): the text must quote at least one word in double quotes; every quoted word must be one of the top-5 positive SHAP words; any technique id must equal the explained label. A failed check shows the template text and says so. Do not change the rule after running `grounding_report.py`; if you must, call it v2 and report both.
What a pass means: the quoted words come from SHAP. It does not mean the explanation is correct, and no human study supports that analysts find it useful (Krippendorff alpha -0.057 nominal, +0.031 ordinal).
Report the pass rate for a fixed set of rows (default: the first 100 with stored SHAP), failures included, as a descriptive number.

**Result of rule v1 on the thesis PC (15 Nov 2026):** 23 of 100 passed, 77 failed, 0 without an LLM answer, median 7.55 s per row (`grounding_report.csv`). The app showed the template text for the 77 failures, as designed.
POST-HOC look at the 77 failures (rule unchanged): 31 fail only because the model quotes the explained technique's own id or name (e.g. `"T1547.009 Shortcut Modification"`); 42 quote at least one word that is not in the sentence; 9 quote a sentence word outside the top 5.

**Proposed rule v2 (not applied, author decision):** as v1, plus a quoted span is allowed when it equals the explained technique's id, its ATT&CK name, or "id name". Words that are neither top-5 SHAP words nor part of that name still fail.
To report a v2 number honestly, fix v2 in `explain.py` under a new name (keep `grounded` as v1), then run it on a fresh set of rows, for example rows 100-199 (`run()` takes the first n rows today; give it a start index so it uses `sorted(R.shap)[100:200]`), and report v1 (23 of 100) and v2 side by side.
Applying v2 to the same 100 rows would score a rule chosen after seeing those outputs.

## Sentences you can write in the thesis

- The framework is packaged in a CPU-only Streamlit application that replays the 725 test sentences from saved scores and stored SHAP values (full-fusion SHAP for the 100 notebook-06 sentences), and offers a live mode with the full fusion of seed 42 (retrained matcher) and a classifier-only live mode.
- It shows a conformal set, a margin-based triage tier and warnings taken from the thesis' own error analysis, with numbers read from `thesis_numbers.json`.
- Do not write: that analysts find the explanations plausible; that the replay explanations describe the fusion outside the 100 notebook-06 sentences; that the conformal guarantee holds per technique; that live mode equals the reported seed-averaged fusion B13a (it is seed 42 with the retrained matcher). Write `[PENDING: <id>]` for anything not yet run.
- Disclose AI assistance in building the tool, as your thesis guidelines require.

## Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit UI |
| `core.py` | loading, fusion maths, conformal, triage, flags, limits |
| `explain.py` | template, Ollama call, grounding rule v1 |
| `live.py` | live classifiers + SHAP (lazy torch/transformers/shap) |
| `demo_data.py` | synthetic data for the demo |
| `verify_artifacts.py`, `grounding_report.py` | the two checks to run on your machine |
| `tests/` | 29 tests: `python -m pytest -q` (fake thesis folder, real result-CSV excerpts, a stub-model SHAP additivity test, Streamlit AppTest, the 15 Nov fixes, SUS scoring) |
| `CLAUDE_CODE_PROMPT.md` | prompt to hand to Claude Code on the thesis machine |
| `run_app.bat` | double-click launcher (local only, port 8501) |
| `docs/DEMO_GUIDE.md` | how to check, start and present the app yourself; viva script with screenshots |
| `docs/img/architecture.png`, `docs/make_architecture.py` | architecture figure and the script that draws it |
| `usability/` | usability study kit: protocol, SUS form, response template, `score_sus.py` |

## AI assistance (disclosure)

This tool was built with AI assistance, and the thesis must say so under the university's AI-use rules.
- Claude (claude.ai, Anthropic) wrote the first version of the code, the tests, the grounding rule v1 and this README, from the thesis files and the author's instructions.
- Claude Code (Anthropic) ran the checks on the thesis machine on 15 Nov 2026. It fixed the triage threshold rule, the technique names and the retired-technique warnings, and added tests for each fix (see "Checks run on the thesis machine").
- The optional written explanations are generated by a local open-weights model (qwen2.5:7b via Ollama) and are filtered by the grounding rule; they are machine text, not author text.
- The thesis design, the models, the saved scores and the stored SHAP values are the author's. The author must check, understand and be able to explain every part of the tool before it is used or described in the thesis.
- Suggested thesis sentence: "The demonstration application was developed with the assistance of generative AI tools (Claude, Anthropic); all outputs were checked against the thesis results by the scripts described in Section X, and the author reviewed the code."

## Limits you should know

- Live SHAP cost is about `n_perm x (2 x words + 1)` model passes per sentence: 2.4 s (7 words) to 76.9 s (54 words) at 10 permutations, 8.4 s to 300.3 s at 40 (measured, table below).
- Sentences longer than 128 tokens are truncated by the models, as in training.
- The conformal guarantee is marginal. Unseen labels have coverage 0.00 for the fusion (CP1.b.unseen.fusion).
- Tested on the thesis PC: Windows 11, Python 3.13.18, streamlit 1.67.0, shap 0.54.1, torch 2.15.0+cpu, transformers 5.23.0, Ollama with qwen2.5:7b.

## Checks run on the thesis machine (15 Nov 2026)

| Step | Result | How it was measured |
|---|---|---|
| 1 `verify_artifacts.py` | 16 of 16 match (`verify_artifacts_output.txt`) | first run 15/16: triage coverage at target 0.9 was 0.9117 vs 0.9145, because `Calib.fit` used `np.quantile` (interpolates) instead of the prereg-19 order statistic. Fixed in `core.dev_threshold` with a test. |
| 2 tests | 26 passed | `python -m pytest -q` (20 original + 6 for the fixes: triage threshold, names, drift text, retired labels in the set, STIX names, `TTPMAP_DEMO=0`) |
| 3 replay by hand | no exceptions; top-5 equals the fused scores for all 6 cases (correct: row 0; wrong: row 8; SHAP label differs: row 1; rare top-1: row 38; retired top-1: row 83; retired label in the set: row 293) | Streamlit AppTest on the real folder, plus one look at the running server. Fixed on the way: only 60 of 733 labels had a name (now all, from the ATT&CK v12.1 bundle); a deprecated technique was shown as its own successor (now "no replacement"); retired labels inside the conformal set are now flagged, not only the top-1. |
| 4 live mode | see the table below; additivity error at most 5.7e-07 | `live.analyse()`, wall clock, CPU (6 threads), one run per setting, invented sentences; numbers in `live_timing.json` |
| 5 `grounding_report.py 100` | see `grounding_report.csv` and `thesis_feed/Q1_FINDINGS.md` Q17 | first 100 rows with stored SHAP, rule v1 unchanged, Ollama at 127.0.0.1 (same answers as localhost, about 2 s faster per request on this PC) |

| sentence | words | 10 permutations | 40 permutations |
|---|---|---|---|
| short | 7 | 2.4 s | 8.4 s |
| medium | 26 | 17.4 s | 67.0 s |
| long | 54 | 76.9 s | 300.3 s |

Model loading before the first live sentence: replay 2.6 s, RoBERTa + SecBERT 4.8 s. Scoring one sentence (batch 1): SVM 19-30 ms, RoBERTa 37-88 ms, SecBERT 15-38 ms.
