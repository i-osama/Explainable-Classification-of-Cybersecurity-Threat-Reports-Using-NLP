# Demo guide: run, check and present the project yourself

For the author. Everything runs on the thesis PC, offline. Commands are for **PowerShell** (Windows Terminal). Screenshots in `img/` show test sentences: keep them for the thesis and the viva, do not post them online.

## 0 What you can show (research + project)
| part | what it proves | where |
|---|---|---|
| Web app (Streamlit) | a working tool for analysts (objective c) | `ttp_app/`, start with `run_app.bat` |
| App reproduces the thesis | the tool shows the evaluated system, not a mock-up | `verify_artifacts.py`: 16/16 |
| Tests | engineering quality | 29 app tests, 75 research tests |
| Research pipeline | pre-registered experiments, one command rebuilds everything | `_showcase/finish_q1.ps1`, `report/index.html` |
| Architecture | system design | `img/architecture.png` |
| Usability study kit | evaluation with users (design science) | `ttp_app/usability/` |

Say it in one sentence: *"This is design science research: I built an artefact for a real problem and evaluated it, both with pre-registered experiments and as a working tool."*

## 1 One-time setup (already done on this PC)
```powershell
cd "E:\Osamas Paper"
.\.venv\Scripts\python.exe -m pip install -r ttp_app\requirements.txt        # streamlit, pytest
.\.venv\Scripts\python.exe -m pip install -r ttp_app\requirements-live.txt   # only for live mode
```

## 2 Before every demo: prove it works (2 minutes)
```powershell
cd "E:\Osamas Paper\ttp_app"
$env:TTPMAP_ROOT = "E:\Osamas Paper"
..\.venv\Scripts\python.exe verify_artifacts.py      # expect: 16/16 match
..\.venv\Scripts\python.exe -m pytest -q              # expect: 41 passed
```
Optional, full research rebuild (a few minutes): `cd "E:\Osamas Paper\_showcase"; powershell -File finish_q1.ps1` and expect 13 lines starting with `OK`.

## 3 Start the app
Double-click `ttp_app\run_app.bat`. A black window opens; the browser opens `http://127.0.0.1:8501` after about 10 seconds. Keep the black window open; closing it stops the app.
Manual start: `cd "E:\Osamas Paper\ttp_app"; $env:TTPMAP_ROOT="E:\Osamas Paper"; ..\.venv\Scripts\python.exe -m streamlit run app.py`
Sidebar: "Synthetic demo data" OFF, Mode "Replay", alpha 0.10, LLM toggle OFF. Change the sentence with the "Sentence" box (type a number, press Enter).

## 4 Five-minute demo script (what to click, what to say)
**Screen 1, sentence 1** (`img/01_correct_sentence1.jpg`)
Click: nothing. Say: "The tool ranks ATT&CK techniques for one sentence. Here the first rank, T1082, is the gold label. The conformal set has one label, so the tool is sure; the triage tier says high confidence. Red words raised the score (SHAP)."

**Screen 2, sentence 9** (`img/02_wrong_sentence9_conformal_set.jpg`)
Type 9, Enter. Say: "Here the first rank is wrong, but the correct technique T1021.002 is inside the conformal set of four. That is why the tool gives a set with a coverage guarantee, not just one answer. The blue box shows this mistake is a known confusion from my error analysis."

**Screen 3, sentence 84** (`img/03_retired_technique_sentence84.jpg`)
Type 84, Enter. Say: "The label space is ATT&CK v12.1. The tool warns that T1064 is deprecated in the current ATT&CK release. 39 test sentences have such labels; I measured this drift."

**Screen 4, sentence 39** (`img/04_rare_label_low_confidence_sentence39.jpg`)
Type 39, Enter. Say: "Rare label: only 4 training sentences, and the margin is small, so the tool says 'analyst review'. The highlighted words explain RoBERTa, not the fused answer, and the tool says so in the caution box. It hides nothing."

**Screen 5, limits** (`img/05_limits_panel.jpg`)
Scroll down, open "What this tool does not show". Say: "Every number here comes from my results registry by id, for example fusion P@1 0.803. The panel also lists what the tool cannot claim."

**Optional:** tick "Only sentences where fusion top-1 is not gold" to browse the 143 errors; switch alpha to 0.20 to show smaller sets.

## 5 Show the research side (2 minutes)
- Open `_showcase\report\index.html` in the browser: the story, results with intervals, limits, status board.
- Open `_showcase\thesis_numbers.json`: every number, with its source file and script.
- Open `_showcase\experiments\prereg\`: analyses written and sealed before the test numbers were seen.
- Say: "The thesis text is checked against this registry by a script (`audit_loop.py`), so no number is typed by hand."

## 6 Live mode (optional, needs about 2 GB free memory)
Sidebar Mode "Live: full fusion (3,1,1,1)", click an example button or paste a sentence, keep permutations at 10, click Analyse. The first run loads the four models (about 1 minute); then about 11 s for a 16-word sentence at 10 permutations (measured 16 Nov 2026, `check_live_parity.py`). Say: "This is the full fusion running now on this laptop: the matcher retrained on Kaggle, plus SVM, RoBERTa and SecBERT, seed 42. A parity check shows its scores match the stored GPU run to within 0.001."
The older mode "Live: classifiers only" (SVM + RoBERTa + SecBERT, equal weights) is still there. Measured: 7 words 2.4 s, 26 words 17.4 s, 54 words 76.9 s (40 permutations: 8.4 / 67.0 / 300.3 s).
If the teacher brings new text, use Mode "Report: many sentences" (paste or upload; a table of techniques per sentence, CSV download). If the teacher brings labelled data, use Mode "Teach: add labelled sentences" (`T1529: sentence` per line; the SVM is retrained in seconds, with the SVM top-3 before and after; Undo returns to the thesis model). The portable `README_DEMO.md` has a tested example and what to say.
On another PC, use the portable folder (`E:\TTP_DEMO`, `START_DEMO.bat`); its `README_DEMO.md` has a 10-minute script.

## 7 Written explanation with the local LLM (optional)
Start Ollama (it runs qwen2.5:7b locally), tick "Explain with local qwen2.5:7b". About 8 s per sentence. If the model quotes a word that is not a top-5 SHAP word, the tool shows the template instead and says so. Measured: 23 of 100 LLM texts passed this rule.

## 8 Questions the teacher may ask
| question | short answer |
|---|---|
| Is this only research, or a project? | Both: design science. Artefact = the tool; evaluation = pre-registered experiments + tool checks + usability study. |
| Does the tool show real results? | Yes: `verify_artifacts.py` recomputes the thesis numbers from the saved scores, 16 of 16 match. |
| Why not train inside the app? | So the screen shows exactly the evaluated system; retraining would change the numbers. |
| Can analysts trust the explanation? | It shows which words the model used, not that it is right. A human study found no usable agreement; the tool says so. |
| Why a local LLM? | No threat data leaves the PC; a grounding rule blocks invented evidence. |
| Did you use AI? | Yes, disclosed: Claude and Claude Code helped write code and documents; I checked every number with scripts and can explain each part. |

## 9 Problems and fixes
| problem | fix |
|---|---|
| `streamlit is missing` | run the step 1 install line |
| browser does not open | open `http://127.0.0.1:8501` by hand |
| page shows "SYNTHETIC DEMO DATA" | switch "Synthetic demo data" off; check that `E:\Osamas Paper\Dataset` exists |
| live mode is slow or crashes | close other programs; use 10 permutations; short sentences |
| "Ollama not reachable" | start Ollama; the template text is used meanwhile |
| port in use | close the old black window, or add `--server.port 8502` |

## 10 Before submission
- Run the usability study (`ttp_app/usability/USABILITY_STUDY.md`) with 3-5 people and add the SUS result to the thesis (`T9.usability_sus`).
- Do **not** deploy the app online under your name or account. Show it locally.
- Keep the AI-assistance statement in the thesis.
- Demo GIF: Chrome saved `ttp_explainer_demo.gif` to your Downloads folder only after you confirm the download in Chrome; copy it to `ttp_app\docs\img\` if you want it.
