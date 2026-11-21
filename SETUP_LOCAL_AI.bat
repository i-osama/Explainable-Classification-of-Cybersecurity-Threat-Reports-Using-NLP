@echo off
rem Optional: installs Ollama and the qwen2.5:7b model (about 5 GB) for the "Compare: GPU, CPU, local AI" page.
rem It asks before installing anything, then starts the demo.
title ATT^&CK explainer - optional local AI setup
cd /d "%~dp0"
"%~dp0runtime\python\python.exe" -E -s -X utf8 "%~dp0launcher\doctor.py" "%~dp0." --optional
pause
