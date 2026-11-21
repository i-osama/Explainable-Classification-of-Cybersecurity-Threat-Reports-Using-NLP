# Rebuild everything that can be rebuilt on this PC (CPU, no training).  Usage:  powershell -File run_all.ps1 [-Fast]
param([switch]$Fast)
$ErrorActionPreference = "Stop"
$py = "E:\Osamas Paper\.venv\Scripts\python.exe"
Set-Location $PSScriptRoot
$steps = @("scripts\make_prereg.py", "scripts\run_tests.py", "scripts\run_analyses.py", "scripts\run_support_aware_v2.py")
if (-not $Fast) { $steps += "scripts\run_inference.py" }          # about 7 minutes of CPU inference
$steps += @("scripts\build_timeline.py", "scripts\build_numbers.py", "scripts\audit_from_ledger.py", "scripts\build_placeholders.py", "scripts\make_figures.py",
            "scripts\make_notebooks.py", "scripts\build_docs.py", "scripts\build_report.py", "scripts\verify_claims.py", "scripts\qa_gates.py")
foreach ($s in $steps) {
    $t = Get-Date
    & $py -X utf8 $s *> "$env:TEMP\ttpmap_step.log"
    $ok = $LASTEXITCODE -eq 0
    "{0}  {1,-36} {2,5:N0}s" -f ($(if ($ok) { "OK  " } else { "FAIL" }), $s, ((Get-Date) - $t).TotalSeconds)
    if (-not $ok) { Get-Content "$env:TEMP\ttpmap_step.log" -Tail 15; exit 1 }
}
