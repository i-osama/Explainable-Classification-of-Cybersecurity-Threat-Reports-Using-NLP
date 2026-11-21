@echo off
rem Puts a "ATT&CK explainer" shortcut on this PC's desktop that starts START_DEMO.bat from this folder.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$d=[Environment]::GetFolderPath('Desktop'); $s=(New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $d 'ATT&CK explainer.lnk')); $s.TargetPath='%~dp0START_DEMO.bat'; $s.WorkingDirectory='%~dp0'; $s.IconLocation='%~dp0launcher\icon.ico'; $s.Description='ATT&CK threat-report explainer (offline demo)'; $s.Save(); Write-Host ('Shortcut created: ' + (Join-Path $d 'ATT&CK explainer.lnk'))"
pause
