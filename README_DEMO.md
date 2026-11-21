# ATT&CK threat-report explainer: demo folder

This folder runs the thesis explainer on a Windows 10 or 11 PC (64-bit). No admin rights are needed.
It reads one sentence of a cyber-attack report and names the attacker technique (MITRE ATT&CK). It shows which words led to the answer and how sure it is.

There are two versions of this folder:
- **Full folder** (about 10 GB): Python, all libraries, the models and the thesis data are inside. It needs **no internet**. Use it for USB sticks.
- **Lite folder** (about 1.4 GB): no Python inside. At the first start it downloads Python and the libraries (about 400 MB) from the fastest server for your network. After that it also works offline.

## Start

1. Copy the whole folder to the laptop, for example to `C:\TTP_DEMO`. A short path is best.
2. Double-click `START_DEMO.bat`. A black window opens and does this by itself:
   1. **Checks the PC and the folder**: Windows version, processor, memory, disk space, the folder's Python and libraries, the model files, and the Microsoft C++ runtime. It only checks what the demo needs. It does not read your files.
   2. **Shows what is missing**, with the size and where it would come from.
   3. **Finds the fastest server** for this network: it asks 5 Python package servers at the same time and uses the quickest one.
   4. **Downloads and repairs**. Every file is checked with its SHA-256 fingerprint. A wrong file is thrown away and the next server is used. Libraries go only into this folder, never into Windows.
   5. **Checks again**, then **starts the app** and opens the browser.
3. Keep the black window open during the demo. Close it to stop the app.

Windows-wide installs are never done without asking. If the Microsoft C++ runtime is missing, the window asks first (type `Y`).
The thesis model and data files are never downloaded: if one is damaged, the window says "copy the whole folder again".

Optional:
- `SETUP_LOCAL_AI.bat` installs Ollama and the qwen2.5:7b model (about 5 GB, asks first). Only the "Compare" page needs it.
- `MAKE_DESKTOP_SHORTCUT.bat` puts an icon on the desktop.
- `CHECK_DEMO.bat` (3-5 minutes) checks every file fingerprint, the numbers against the thesis registry, the app tests and the live-vs-stored model check. It ends with `ALL CHECKS PASSED`.

## What to show (about 10 minutes)

| step | page | what it shows |
|---|---|---|
| 1 | **Start here** | What the project is, how it works in three steps, how good it is (numbers from the thesis registry), and a glossary. |
| 2 | **Try a sentence**: click an example, then **Analyse** | The answer, a one-line explanation in plain words, the coloured words, and the confidence level. The first run loads the models (about 1 minute). |
| 3 | **Train and check**: **Load a ready-made example**, then **Train and check** | The tool learns a technique from 4 examples. It is then tested on 4 *different* sentences: before vs after, and a check that the 604 thesis sentences did not get worse. |
| 4 | **Try a sentence** again with a similar sentence | A blue box shows the custom-trained answer. **Undo** in "Train and check" returns to the thesis model. |
| 5 | **Compare: GPU, CPU, local AI** | The same models on GPU or CPU give the same answer, only the speed differs. A general local AI is much less accurate. |
| 6 | **Browse test sentences**, tick "Only sentences where fusion top-1 is not gold" | Honest errors, with warnings. |

## If something goes wrong

- **"No server answered: this PC seems to be offline"**: connect to the internet once (only needed when something is missing), or use the full folder.
- **"The folder is read-only"** (USB stick or DVD): copy the folder to the laptop first.
- **"copy the whole folder again"**: a thesis file is missing or damaged. Copy the complete folder again.
- **Windows SmartScreen warns about the .bat file**: click "More info", then "Run anyway".
- **The browser does not open**: open the address shown in the black window by hand (`http://127.0.0.1:8501` or the next port).
- **The page turns grey with "Connection error"**: the black window was closed. Start `START_DEMO.bat` again, then reload the page.
- **A company network blocks the download**: the window lists every server it tried and why it failed. Try another network (for example a phone hotspot).

The app listens only on 127.0.0.1 and works offline. Only START_DEMO.bat downloads missing parts, and only from public servers
(Python package servers, Hugging Face, Microsoft, ollama.com). No personal data is sent. Do not put this app online.
