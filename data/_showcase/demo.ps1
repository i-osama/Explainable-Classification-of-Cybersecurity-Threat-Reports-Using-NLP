# One-command demo: recompute the headline numbers from the saved prediction files and compare them with thesis_numbers.json.
# Usage (from _showcase):  powershell -File demo.ps1        Takes under a minute on a laptop CPU. Prints VERIFY: PASS or FAIL.
$py = "E:\Osamas Paper\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
Set-Location $PSScriptRoot
& $py -X utf8 scripts\verify_claims.py
exit $LASTEXITCODE
