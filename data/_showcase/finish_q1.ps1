# Q1 plan close-out after the local LLM run has finished (results\llm_raw\*_test.jsonl complete, 725 rows each).
# Scores the LLM baseline, re-renders every number-bearing document, repackages, re-hashes, runs the QA gates.
# Usage:  powershell -File finish_q1.ps1        (safe to re-run)
$ErrorActionPreference = "Stop"
$py = "E:\Osamas Paper\.venv\Scripts\python.exe"
Set-Location $PSScriptRoot
# 15 Nov: app checks (..\ttp_app, skipped if absent) before the registry; draft audit (newest Thesis_Draft*.docx) after it.
$steps = @(@("scripts\run_llm_baseline.py", "--score"), @("scripts\ingest_app_checks.py"), @("scripts\build_numbers.py"), @("scripts\audit_loop.py"),
           @("scripts\build_thesis_feed.py"), @("scripts\build_placeholders.py"),
           @("scripts\build_docs.py"), @("scripts\build_report.py"), @("scripts\make_upload.py"), @("scripts\package.py"),
           @("scripts\check_hashes.py", "--record"), @("scripts\verify_claims.py"), @("scripts\qa_gates.py"))
foreach ($s in $steps) {
    & $py -X utf8 -W ignore @s *> "$env:TEMP\ttpmap_q1.log"
    $ok = $LASTEXITCODE -eq 0
    "{0}  {1}" -f ($(if ($ok) { "OK  " } else { "FAIL" }), ($s -join " "))
    if (-not $ok) { Get-Content "$env:TEMP\ttpmap_q1.log" -Tail 15; exit 1 }
}
"Done. Upload UPLOAD_TO_CLAUDE_AI.zip to the claude.ai Project; paste thesis_feed\WEB_CLAUDE_PROMPT.md into its instructions."
