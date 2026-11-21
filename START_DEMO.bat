@echo off
rem Double-click: checks this PC and folder, fixes what is missing (downloads from the fastest server), then starts the explainer.
rem Close this window to stop the app.
title ATT^&CK explainer - keep this window open during the demo
cd /d "%~dp0"
set "PY=%~dp0runtime\python\python.exe"
if not exist "%PY%" (
  echo.
  echo   This folder has no Python yet. Getting it from the fastest server (about 50 MB^)...
  set "PSModulePath="
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0launcher\bootstrap.ps1" -Bundle "%~dp0."
  if errorlevel 1 goto failed
)
"%PY%" -E -s -X utf8 "%~dp0launcher\doctor.py" "%~dp0."
if errorlevel 1 pause
exit /b
:failed
echo.
echo   Setup could not finish. Read the lines above, check the internet connection, then start again.
pause
exit /b 1
