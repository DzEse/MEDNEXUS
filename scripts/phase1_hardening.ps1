$ErrorActionPreference = "Stop"

function Write-Utf8NoBom {
    param([Parameter(Mandatory=$true)][string]$Path,[Parameter(Mandatory=$true)][string]$Content)
    $encoding = New-Object System.Text.UTF8Encoding($false)
    $fullPath = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Path))
    [System.IO.File]::WriteAllText($fullPath, $Content, $encoding)
}

function Invoke-NativeChecked {
    param([Parameter(Mandatory=$true)][string]$Step,[Parameter(Mandatory=$true)][scriptblock]$Command)
    & $Command
    if ($LASTEXITCODE -ne 0) { throw "$Step failed with exit code $LASTEXITCODE." }
}

Write-Host "=== MEDNEXUS PHASE 1 HARDENING V2 ==="

if (-not (Test-Path "mednexus\synthetic.py")) {
    throw "Run this script from the MEDNEXUS repository root."
}

# --- 1. Patch synthetic.py with line-based edits (Windows CRLF/LF safe) ---
$syntheticPath = "mednexus\synthetic.py"
$lines = New-Object 'System.Collections.Generic.List[string]'
Get-Content $syntheticPath | ForEach-Object { [void]$lines.Add($_) }

$futureIndex = $lines.IndexOf("from __future__ import annotations")
if ($futureIndex -lt 0) { throw "Could not locate future import in synthetic.py." }

if (-not $lines.Contains("from datetime import timedelta")) {
    $lines.Insert($futureIndex + 1, "from datetime import timedelta")
}
if (-not $lines.Contains("import zlib")) {
    $futureIndex = $lines.IndexOf("from __future__ import annotations")
    $lines.Insert($futureIndex + 2, "import zlib")
}

$stableExists = $false
foreach ($line in $lines) {
    if ($line -like "def _stable_index*") { $stableExists = $true; break }
}

if (-not $stableExists) {
    $returnLine = "    return [f'{prefix}{i:04d}' for i in range(1, n + 1)]"
    $returnIndex = $lines.IndexOf($returnLine)
    if ($returnIndex -lt 0) {
        throw "Could not locate the _ids return line in synthetic.py; refusing to patch ambiguously."
    }
    $insert = @(
        "",
        "",
        "def _stable_index(*parts, n: int) -> int:",
        '    """Return a deterministic bucket index independent of PYTHONHASHSEED."""',
        "    if n <= 0:",
        "        raise ValueError('n must be positive')",
        "    payload = '|'.join(str(part) for part in parts).encode('utf-8')",
        "    return zlib.crc32(payload) % n"
    )
    for ($i = $insert.Count - 1; $i -ge 0; $i--) {
        $lines.Insert($returnIndex + 1, $insert[$i])
    }
}

$oldProduct = "            product = products.iloc[(hash(machine.machine_id + str(d.date())) % len(products))]"
$newProduct = "            product = products.iloc[_stable_index(machine.machine_id, d.date(), n=len(products))]"
$productIndex = $lines.IndexOf($oldProduct)
if ($productIndex -ge 0) {
    $lines[$productIndex] = $newProduct
} elseif (-not $lines.Contains($newProduct)) {
    throw "Could not locate product assignment in synthetic.py."
}

for ($i = 0; $i -lt $lines.Count; $i++) {
    $lines[$i] = $lines[$i].Replace(
        "promised = d + pd.Timedelta(days=int(rng.integers(3,9)))",
        "promised = d + timedelta(days=int(rng.integers(3,9)))"
    )
    $lines[$i] = $lines[$i].Replace(
        "shipped = d + pd.Timedelta(days=int(rng.integers(1,4)))",
        "shipped = d + timedelta(days=int(rng.integers(1,4)))"
    )
    $lines[$i] = $lines[$i].Replace(
        "delivered = promised + pd.Timedelta(days=delay)",
        "delivered = promised + timedelta(days=delay)"
    )
}
Write-Utf8NoBom $syntheticPath (($lines -join "`r`n") + "`r`n")

# --- 2. Strengthen reproducibility tests ---
$testContent = @'
import os
import subprocess
import sys

from mednexus.synthetic import generate


def test_seed_reproducibility():
    a = generate(seed=7)["fact_finance"]
    b = generate(seed=7)["fact_finance"]
    assert a.equals(b)


def test_stable_selection_is_independent_of_python_hash_seed():
    code = (
        "from mednexus.synthetic import _stable_index; "
        "print(_stable_index('PL0001-L1-M1', '2026-08-31', n=6))"
    )
    outputs = []
    for hash_seed in ("1", "999"):
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = hash_seed
        outputs.append(
            subprocess.check_output(
                [sys.executable, "-c", code], env=env, text=True
            ).strip()
        )
    assert outputs[0] == outputs[1]
'@
Write-Utf8NoBom "tests\test_reproducibility.py" $testContent

# --- 3. Replace Windows bootstrap with fail-closed native-command handling ---
$bootstrapContent = @'
$ErrorActionPreference = "Stop"

function Invoke-NativeChecked {
    param([Parameter(Mandatory=$true)][string]$Step,[Parameter(Mandatory=$true)][scriptblock]$Command)
    & $Command
    if ($LASTEXITCODE -ne 0) { throw "$Step failed with exit code $LASTEXITCODE." }
}

Write-Host "=== MEDNEXUS ONE-GO BUILD ==="

if (-not (Get-Command py -ErrorAction SilentlyContinue) -and -not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.11+ is required. Install Python and reopen VS Code."
}
$PythonLauncher = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "python" }

if (-not (Test-Path ".venv")) {
    Invoke-NativeChecked "Virtual environment creation" { & $PythonLauncher -m venv .venv }
}
$VenvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) { throw "Virtual environment Python was not created correctly." }

Invoke-NativeChecked "pip upgrade" { & $VenvPython -m pip install --upgrade pip }
Invoke-NativeChecked "dependency installation" { & $VenvPython -m pip install -r requirements.txt }
Invoke-NativeChecked "project setup" { & $VenvPython setup_project.py }
Invoke-NativeChecked "MEDNEXUS pipeline" { & $VenvPython run_pipeline.py --clean }
Invoke-NativeChecked "pytest" { & $VenvPython -m pytest -q }
Write-Host "=== BUILD AND TESTS PASSED ==="

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is not installed. Build is complete; GitHub publishing was skipped."
    exit 0
}
if (-not (Test-Path ".git")) { Invoke-NativeChecked "git init" { git init } }
Invoke-NativeChecked "git add" { git add . }
$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) { throw "git status failed with exit code $LASTEXITCODE." }
if ($changes) { Invoke-NativeChecked "git commit" { git commit -m "Build MEDNEXUS enterprise analytics platform" } }
Invoke-NativeChecked "git branch normalization" { git branch -M main }

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Warning "GitHub CLI is not installed. Repository is committed locally."
    exit 0
}
gh auth status | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Warning "GitHub CLI is not authenticated. Run 'gh auth login'."
    exit 0
}
$remoteNames = @(git remote)
if ($LASTEXITCODE -ne 0) { throw "git remote failed with exit code $LASTEXITCODE." }
if (-not ($remoteNames -contains "origin")) {
    Invoke-NativeChecked "GitHub repository creation/push" { gh repo create MEDNEXUS --public --source=. --remote=origin --push }
} else {
    Invoke-NativeChecked "GitHub push" { git push -u origin main }
}
Write-Host "=== MEDNEXUS BUILT, TESTED, COMMITTED AND PUSHED ==="
'@
Write-Utf8NoBom "scripts\bootstrap_build_and_publish.ps1" $bootstrapContent

# --- 4. Explicit line-ending policy ---
$attributes = @'
* text=auto eol=lf
*.ps1 text eol=crlf
*.bat text eol=crlf
*.cmd text eol=crlf
'@
Write-Utf8NoBom ".gitattributes" $attributes

# --- 5. Verify tests and cross-process reproducibility ---
$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { throw ".venv was not found. Run the normal bootstrap once before hardening." }

Invoke-NativeChecked "pytest" { & $Python -m pytest -q }

$env:PYTHONHASHSEED = "1"
Invoke-NativeChecked "determinism run 1" { & $Python run_pipeline.py --clean }
$manifest1 = (Get-FileHash "artifacts\validation\manifest.json" -Algorithm SHA256).Hash
$summary1 = (Get-FileHash "artifacts\reports\management_summary.md" -Algorithm SHA256).Hash

$env:PYTHONHASHSEED = "999"
Invoke-NativeChecked "determinism run 2" { & $Python run_pipeline.py --clean }
$manifest2 = (Get-FileHash "artifacts\validation\manifest.json" -Algorithm SHA256).Hash
$summary2 = (Get-FileHash "artifacts\reports\management_summary.md" -Algorithm SHA256).Hash
Remove-Item Env:PYTHONHASHSEED -ErrorAction SilentlyContinue

if (($manifest1 -ne $manifest2) -or ($summary1 -ne $summary2)) {
    throw "Cross-process reproducibility check failed: canonical output hashes changed with PYTHONHASHSEED."
}
Write-Host "CROSS_PROCESS_REPRODUCIBILITY=PASS"

# --- 6. Commit and push canonical hardened state ---
Invoke-NativeChecked "git add" { git add . }
$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) { throw "git status failed with exit code $LASTEXITCODE." }
if ($changes) {
    Invoke-NativeChecked "git commit" { git commit -m "Harden MEDNEXUS reproducibility and Windows publishing" }
    Invoke-NativeChecked "git push" { git push origin main }
}

Write-Host "=== MEDNEXUS PHASE 1 HARDENING PASSED AND PUSHED ==="
