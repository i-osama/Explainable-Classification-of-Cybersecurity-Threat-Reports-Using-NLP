@echo off
rem Double-click to start the ATT&CK explainer on this PC only (http://127.0.0.1:8501). Close this window to stop it.
rem Uses the thesis folder one level up (..\Dataset, ..\_showcase\results) and its .venv if present.
cd /d "%~dp0"
set "TTPMAP_ROOT=%~dp0.."
set "PY=%~dp0..\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
"%PY%" -c "import streamlit" 2>nul || (echo streamlit is missing: run  "%PY%" -m pip install -r requirements.txt & pause & exit /b 1)
echo Starting the explainer... the browser opens at http://127.0.0.1:8501  (first load about 10 s)
rem headless: no first-run e-mail prompt; the browser is opened below after the server has had time to start
start "" /b cmd /c "ping -n 9 127.0.0.1 >nul & start "" http://127.0.0.1:8501"
"%PY%" -m streamlit run app.py --server.headless true --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
pause
