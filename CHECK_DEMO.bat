@echo off
rem Full self-check (about 3-5 minutes): file hashes, app numbers vs the thesis registry, app tests, live full fusion vs stored scores.
title ATT^&CK explainer - full self-check
cd /d "%~dp0"
set "PY=%~dp0runtime\python\python.exe"
if not exist "%PY%" goto nopy
echo Running the full self-check. This takes a few minutes...
"%PY%" -E -s -X utf8 "%~dp0launcher\check.py" --deep
pause
exit /b
:nopy
echo The portable Python is missing: "%PY%"
echo Copy the whole TTP_DEMO folder again.
pause
exit /b 1
