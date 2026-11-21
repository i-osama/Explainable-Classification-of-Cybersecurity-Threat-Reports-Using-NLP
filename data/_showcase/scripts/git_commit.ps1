# Guarded commit + push.  Usage:  powershell -File _showcase\scripts\git_commit.ps1 "T3: analyses"
# Refuses to commit: files over 25 MB, weights, dataset text files, rater data, or files containing rater-sheet names.
param([Parameter(Mandatory = $true)][string]$Message)
$ErrorActionPreference = "Stop"
Set-Location (Resolve-Path "$PSScriptRoot\..\..")
git add -A
$staged = git diff --cached --name-only
$bad = @()
foreach ($f in $staged) {
    if (-not (Test-Path -LiteralPath $f)) { continue }
    $len = (Get-Item -LiteralPath $f).Length
    if ($len -gt 25MB) { $bad += "$f (over 25 MB)" }
    if ($f -match '\.(pt|bin|safetensors|ckpt|pth|npy|npz|jsonl|xlsx)$') { $bad += "$f (weights / raw rows / rating sheet)" }
    if ($f -match '(tram_(train|dev|test)|combined_train|ttp-desc-mappings)\.') { $bad += "$f (dataset text)" }
    if ($f -match 'human_study[\\/]returned') { $bad += "$f (rater data)" }
    if ($len -lt 5MB -and $f -match '\.(md|csv|json|txt|py|yaml|yml|html|ipynb|ps1|cff)$') {
        if (Select-String -LiteralPath $f -Pattern 'hand_check_v2_roberta_pw_s42_', 'C:\\Users\\' -SimpleMatch -Quiet) { $bad += "$f (rater file name or user path inside)" }
    }
}
if ($bad.Count -gt 0) {
    git reset -q
    Write-Output "COMMIT REFUSED:"; $bad | ForEach-Object { Write-Output "  $_" }
    exit 1
}
if (-not $staged) { Write-Output "nothing to commit"; exit 0 }
git commit -q -m $Message
git push -q
Write-Output ("committed " + (git rev-parse --short HEAD) + " : " + $Message + " (" + @($staged).Count + " files)")
