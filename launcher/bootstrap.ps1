# Gets Python for this folder when it has none (lite folder, or a broken copy).
# Fastest Python package server -> uv (SHA-256 checked) -> uv installs CPython into runtime\python.
# The doctor (launcher\doctor.py) then installs the libraries. Windows PowerShell 5.1, no admin rights needed.
param([Parameter(Mandatory = $true)][string]$Bundle)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'   # no progress bars (they slow PowerShell down)
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
Add-Type -AssemblyName System.Net.Http

$Bundle = (Resolve-Path -LiteralPath $Bundle).Path
$boot = Get-Content -Raw -LiteralPath (Join-Path $Bundle 'launcher\bootstrap.json') | ConvertFrom-Json
$mirrors = @('https://pypi.org/simple', 'https://pypi.tuna.tsinghua.edu.cn/simple', 'https://mirrors.aliyun.com/pypi/simple',
             'https://mirrors.cloud.tencent.com/pypi/simple', 'https://mirror.kakao.com/pypi/simple')   # same list as mirrors.py
$env:UV_NO_CACHE = '1'
$rt = Join-Path $Bundle 'runtime'
New-Item -ItemType Directory -Force -Path $rt | Out-Null

# 1. race: ask every server for the uv page at the same time; the first complete answer wins
Write-Host '  Finding the fastest Python package server for this network...'
$client = New-Object System.Net.Http.HttpClient
$client.Timeout = [TimeSpan]::FromSeconds(10)
$client.DefaultRequestHeaders.UserAgent.ParseAdd('ttp-demo-bootstrap/1.0')
$tasks = @{}; $done = @{}
$sw = [Diagnostics.Stopwatch]::StartNew()
foreach ($m in $mirrors) { $tasks[$m] = $client.GetStringAsync("$m/uv/") }
while ($done.Count -lt $mirrors.Count -and $sw.Elapsed.TotalSeconds -lt 10) {
    foreach ($m in $mirrors) {
        if (-not $done.ContainsKey($m) -and $tasks[$m].IsCompleted) { $done[$m] = [int]$sw.Elapsed.TotalMilliseconds }
    }
    Start-Sleep -Milliseconds 20
}
$ranked = @()
foreach ($m in $mirrors) {
    $t = $tasks[$m]
    if ($done.ContainsKey($m) -and $t.Status -eq 'RanToCompletion' -and $t.Result.Contains($boot.uv_wheel)) {
        $ranked += [pscustomobject]@{ Mirror = $m; Ms = $done[$m]; Page = $t.Result }
    }
}
$ranked = @($ranked | Sort-Object Ms)
foreach ($r in $ranked) { Write-Host ('    {0,6} ms  {1}' -f $r.Ms, $r.Mirror) }
if ($ranked.Count -eq 0) { Write-Host '  No server answered: connect this PC to the internet and start again.'; exit 1 }

# 2. uv wheel from the fastest server that serves the right file (SHA-256 from bootstrap.json).
#    Plain .NET only: the hash, unzip and web-download cmdlets need modules that Windows PowerShell 5.1
#    cannot load when it inherits PowerShell 7's module path.
Add-Type -AssemblyName System.IO.Compression.FileSystem
function Save-Url([string]$Url, [string]$Path) {
    $dl = New-Object System.Net.Http.HttpClient
    $dl.Timeout = [TimeSpan]::FromMinutes(10)
    $dl.DefaultRequestHeaders.UserAgent.ParseAdd('ttp-demo-bootstrap/1.0')
    $resp = $dl.GetAsync($Url, [System.Net.Http.HttpCompletionOption]::ResponseHeadersRead).GetAwaiter().GetResult()
    [void]$resp.EnsureSuccessStatusCode()
    $in = $resp.Content.ReadAsStreamAsync().GetAwaiter().GetResult()
    $out = [System.IO.File]::Create($Path)
    try { $in.CopyTo($out) } finally { $out.Dispose(); $in.Dispose(); $dl.Dispose() }
}
function Get-Sha256([string]$Path) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $fs = [System.IO.File]::OpenRead($Path)
    try { return -join ($sha.ComputeHash($fs) | ForEach-Object { $_.ToString('x2') }) } finally { $fs.Dispose(); $sha.Dispose() }
}
$whl = Join-Path $rt $boot.uv_wheel
$got = $false
foreach ($r in $ranked) {
    $m = [regex]::Match($r.Page, 'href="([^"]*' + [regex]::Escape($boot.uv_wheel) + '[^"]*)"')
    if (-not $m.Success) { continue }
    $href = [System.Net.WebUtility]::HtmlDecode($m.Groups[1].Value)
    $url = (New-Object System.Uri((New-Object System.Uri("$($r.Mirror)/uv/")), $href)).AbsoluteUri.Split('#')[0]
    Write-Host ('  Downloading uv ({0} MB) from {1} ...' -f [int]($boot.uv_size / 1MB), $r.Mirror)
    try {
        Save-Url $url $whl
    } catch {
        Write-Host "    failed: $($_.Exception.Message)"
        if (Test-Path -LiteralPath $whl) { Remove-Item -LiteralPath $whl -Force }
        continue
    }
    if ((Get-Sha256 $whl) -eq $boot.uv_sha256.ToLower()) { $got = $true; break }
    Write-Host '    wrong file (hash mismatch): trying the next server'
    Remove-Item -LiteralPath $whl -Force
}
if (-not $got) { Write-Host '  Could not download uv from any server.'; exit 1 }
$tmp = Join-Path $rt '_uv'
if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Recurse -Force }
[System.IO.Compression.ZipFile]::ExtractToDirectory($whl, $tmp)
$exe = Get-ChildItem -LiteralPath $tmp -Recurse -Filter 'uv.exe' | Select-Object -First 1
New-Item -ItemType Directory -Force -Path (Join-Path $rt 'uv') | Out-Null
Copy-Item -LiteralPath $exe.FullName -Destination (Join-Path $rt 'uv\uv.exe') -Force
Remove-Item -LiteralPath $tmp -Recurse -Force
Remove-Item -LiteralPath $whl -Force

# 3. CPython for this folder
$uv = Join-Path $rt 'uv\uv.exe'
$pyTmp = Join-Path $rt '_py'
Write-Host "  Installing Python $($boot.python) for this folder (about 30 MB, from GitHub)..."
& $uv python install $boot.python --install-dir $pyTmp --no-bin
if ($LASTEXITCODE -ne 0) { Write-Host '  Python download failed.'; exit 1 }
# uv adds a cpython-3.13-... junction next to the real cpython-3.13.18-... folder: take the real folder, never the link
$all = @(Get-ChildItem -LiteralPath $pyTmp -Directory -Filter 'cpython-*')
$dir = $all | Where-Object { -not ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) -and (Test-Path -LiteralPath (Join-Path $_.FullName 'python.exe')) } |
    Select-Object -First 1
if (-not $dir) { Write-Host '  Python was downloaded but its folder was not found.'; exit 1 }
foreach ($l in $all) { if ($l.Attributes -band [IO.FileAttributes]::ReparsePoint) { [System.IO.Directory]::Delete($l.FullName) } }  # the link only
Move-Item -LiteralPath $dir.FullName -Destination (Join-Path $rt 'python')
Remove-Item -LiteralPath $pyTmp -Recurse -Force
$em = Join-Path $rt 'python\Lib\EXTERNALLY-MANAGED'
if (Test-Path -LiteralPath $em) { Remove-Item -LiteralPath $em -Force }   # this Python belongs to the folder: the doctor adds the libraries
Write-Host '  Python ready. Next: the libraries.'
exit 0
