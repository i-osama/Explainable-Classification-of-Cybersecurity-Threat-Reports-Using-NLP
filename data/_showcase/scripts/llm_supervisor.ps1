# Local supervisor for the Q1 LLM baseline (prereg 17). Needs no Claude: only PowerShell, Python and the local Ollama model.
# - keeps the PC awake while it runs (released automatically when this process ends)
# - restarts the resumable runner if it stops before all 3 variants have 725 rows (max 20 restarts), restarting Ollama if needed
# - when complete: runs finish_q1.ps1 (scores, documents, zip, hashes, QA gates); never commits or pushes
# Status: results\llm_raw\supervisor_status.txt (one line) and supervisor.log (history).
# Start (detached):  Start-Process powershell -WindowStyle Hidden -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','"E:\Osamas Paper\_showcase\scripts\llm_supervisor.ps1"'   (inner quotes needed: the path has a space)
$ErrorActionPreference = "Continue"
Add-Type -Namespace W -Name P -MemberDefinition '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint f);'
[W.P]::SetThreadExecutionState([uint32]"0x80000001") | Out-Null      # ES_CONTINUOUS | ES_SYSTEM_REQUIRED: no sleep while this runs
$env:TTPMAP_OLLAMA_NUM_GPU = "9"   # pinned: the automatic fit Ollama chose for the whole 'closed' variant (server.log: offloaded 9/29 layers); see DECISIONS D23
$show = "E:\Osamas Paper\_showcase"; $raw = "$show\results\llm_raw"; $py = "E:\Osamas Paper\.venv\Scripts\python.exe"
$variants = "closed", "rr_matcher", "rr_zero"

function Say($m) { $l = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')  $m"; Add-Content "$raw\supervisor.log" $l; Set-Content "$raw\supervisor_status.txt" $l }
function Count($v) {
    $f = "$raw\${v}_test.jsonl"; if (-not (Test-Path $f)) { return 0 }
    $ids = foreach ($l in Get-Content $f) { try { ($l | ConvertFrom-Json).i } catch { } }   # half-written last line is skipped
    return @($ids | Sort-Object -Unique).Count
}
function Runner { Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -like "*run_llm_baseline.py*--split test*" } }
function OllamaUp { try { Invoke-RestMethod "http://127.0.0.1:11434/api/tags" -TimeoutSec 10 | Out-Null; $true } catch { $false } }

$restarts = 0
Say "supervisor started (PID $PID)"
while ($true) {
    $n = @($variants | ForEach-Object { Count $_ })
    if (@($n | Where-Object { $_ -ge 725 }).Count -eq 3) { break }
    $state = "closed $($n[0]) / rr_matcher $($n[1]) / rr_zero $($n[2]) of 725; restarts $restarts"
    if (Runner) { Say "running: $state"; Start-Sleep 60; continue }
    if ($restarts -ge 20) { Say "STOPPED after 20 restarts: $state. See results\llm_raw\run_test*.err"; exit 1 }
    if (-not (OllamaUp)) { Say "Ollama not answering; starting 'ollama serve'"; Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden; Start-Sleep 30 }
    $restarts++; Say "runner not running ($state); restart $restarts"
    Start-Process -FilePath $py -ArgumentList "-X", "utf8", "-W", "ignore", "scripts\run_llm_baseline.py", "--split", "test" -WorkingDirectory $show -WindowStyle Hidden `
        -RedirectStandardOutput "$raw\run_test_r$restarts.log" -RedirectStandardError "$raw\run_test_r$restarts.err"
    Start-Sleep 60
}
Say "all 3 variants complete; running finish_q1.ps1"
& powershell -NoProfile -ExecutionPolicy Bypass -File "$show\finish_q1.ps1" *> "$raw\finish_q1.log"
if ($LASTEXITCODE -ne 0) { Say "FINISH FAILED (run results are safe): see results\llm_raw\finish_q1.log"; exit 1 }
Say "DONE: LLM scored, documents rebuilt, QA gates passed (no git commit or push: author's instruction of 15 Nov)"
