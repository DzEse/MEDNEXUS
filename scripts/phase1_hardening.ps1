$ErrorActionPreference = "Stop"

function Write-Utf8NoBom {
    param([string]$Path, [string]$Content)
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText((Resolve-Path $Path), $Content, $encoding)
}

function Invoke-NativeChecked {
    param(
        [Parameter(Mandatory = $true)][string]$Step,
        [Parameter(Mandatory = $true)][scriptblock]$Command
    )
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE."
    }
}

Write-Host "=== MEDNEXUS PHASE 1 HARDENING ==="

if (-not (Test-Path "mednexus\synthetic.py")) {
    throw "Run this script from the MEDNEXUS repository root."
}

# 1. Make synthetic product assignment independent of Python's randomized hash seed.
$syntheticPath = "mednexus\synthetic.py"
$synthetic = Get-Content $syntheticPath -Raw

if ($synthetic -notmatch "from datetime import timedelta") {
    $synthetic = $synthetic.Replace(
        "from __future__ import annotations`nimport numpy as np",
        "from __future__ import annotations`nfrom datetime import timedelta`nimport zlib`n`nimport numpy as np"
    )
}

if ($synthetic -notmatch "def _stable_index") {
    $marker = @'
def _ids(prefix, n):
    return [f'{prefix}{i:04d}' for i in range(1, n + 1)]


'@
    $replacement = @'
def _ids(prefix, n):
    return [f'{prefix}{i:04d}' for i in range(1, n + 1)]


def _stable_index(*parts, n: int) -> int:
    """Return a deterministic bucket index independent of PYTHONHASHSEED."""
    if n <= 0:
        raise ValueError('n must be positive')
    payload = '|'.join(str(part) for part in parts).encode('utf-8')
    return zlib.crc32(payload) % n


'@
    if (-not $synthetic.Contains($marker)) {
        throw "Could not locate the _ids block in mednexus/synthetic.py; refusing to patch ambiguously."
    }
    $synthetic = $synthetic.Replace($marker, $replacement)
}

$synthetic = $synthetic.Replace(
    "product = products.iloc[(hash(machine.machine_id + str(d.date())) % len(products))]",
    "product = products.iloc[_stable_index(machine.machine_id, d.date(), n=len(products))]"
)
$synthetic = $synthetic.Replace(
    "promised = d + pd.Timedelta(days=int(rng.integers(3,9)))",
    "promised = d + timedelta(days=int(rng.integers(3,9)))"
)
$synthetic = $synthetic.Replace(
    "shipped = d + pd.Timedelta(days=int(rng.integers(1,4)))",
    "shipped = d + timedelta(days=int(rng.integers(1,4)))"
)
$synthetic = $synthetic.Replace(
    "delivered = promised + pd.Timedelta(days=delay)",
    "delivered = promised + timedelta(days=delay)"
)
Write-Utf8NoBom $syntheticPath $synthetic

# 2. Strengthen reproducibility tests across different PYTHONHASHSEED values.
$testPath = "tests\test_reproducibility.py"
$testContent = @'
import os
import subprocess
import sys

from mednexus.synthetic import generate


def test_seed_reproducibility():
    a = generate(seed=7)['fact_finance']
    b = generate(seed=7)['fact_finance']
    assert a.equals(b)


def test_stable_selection_is_independent_of_python_hash_seed():
    code = (
        "from mednexus.synthetic import _stable_index; "
        "print(_stable_index('PL0001-L1-M1', '2026-08-31', n=6))"
    )
    outputs = []
    for hash_seed in ('1', '999'):
        env = os.environ.copy()
        env['PYTHONHASHSEED'] = hash_seed
        outputs.append(
            subprocess.check_output(
                [sys.executable, '-c', code],
                env=env,
                text=True,
            ).strip()
        )
    assert outputs[0] == outputs[1]
'@
Write-Utf8NoBom $testPath $testContent

# 3. Make the one-go Windows launcher fail closed on native command errors.
$bootstrapPath = "scripts\bootstrap_build_and_publish.ps1"
$bootstrapContent = @'
$ErrorActionPreference = "Stop"

function Invoke-NativeChecked {
    param(
        [Parameter(Mandatory = $true)][string]$Step,
        [Parameter(Mandatory = $true)][scriptblock]$Command
    )
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE."
    }
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
if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment Python was not created correctly."
}

Invoke-NativeChecked "pip upgrade" { & $VenvPython -m pip install --upgrade pip }
Invoke-NativeChecked "dependency installation" { & $VenvPython -m pip install -r requirements.txt }
Invoke-NativeChecked "project setup" { & $VenvPython setup_project.py }
Invoke-NativeChecked "MEDNEXUS pipeline" { & $VenvPython run_pipeline.py --clean }
Invoke-NativeChecked "pytest" { & $VenvPython -m pytest -q }

Write-Host "=== BUILD AND TESTS PASSED ==="

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is not installed. Build is complete, but GitHub publishing was skipped."
    exit 0
}

if (-not (Test-Path ".git")) {
    Invoke-NativeChecked "git init" { git init }
}

Invoke-NativeChecked "git add" { git add . }
$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE."
}
if ($changes) {
    Invoke-NativeChecked "git commit" { git commit -m "Build MEDNEXUS enterprise analytics platform" }
}

Invoke-NativeChecked "git branch normalization" { git branch -M main }

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Warning "GitHub CLI (gh) is not installed. Repository is committed locally. Install gh, run 'gh auth login', then run scripts/publish_to_github.ps1."
    exit 0
}

gh auth status | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Warning "GitHub CLI is not authenticated. Repository is committed locally. Run 'gh auth login', then run scripts/publish_to_github.ps1."
    exit 0
}

$remoteNames = @(git remote)
if ($LASTEXITCODE -ne 0) {
    throw "git remote failed with exit code $LASTEXITCODE."
}

if (-not ($remoteNames -contains "origin")) {
    Invoke-NativeChecked "GitHub repository creation/push" { gh repo create MEDNEXUS --public --source=. --remote=origin --push }
} else {
    Invoke-NativeChecked "GitHub push" { git push -u origin main }
}

Write-Host "=== MEDNEXUS BUILT, TESTED, COMMITTED AND PUSHED ==="
'@
Write-Utf8NoBom $bootstrapPath $bootstrapContent

# 4. Normalize repository line endings deliberately.
$attributesPath = ".gitattributes"
$attributes = @'
* text=auto eol=lf
*.ps1 text eol=crlf
*.bat text eol=crlf
*.cmd text eol=crlf
'@
if (Test-Path $attributesPath) {
    Write-Utf8NoBom $attributesPath $attributes
} else {
    $encoding = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText((Join-Path (Get-Location) $attributesPath), $attributes, $encoding)
}

# 5. Verify the hardened project and prove cross-process determinism.
$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Run the normal bootstrap once before hardening."
}

Invoke-NativeChecked "pytest" { & $Python -m pytest -q }

$env:PYTHONHASHSEED = "1"
Invoke-NativeChecked "determinism run 1" { & $Python run_pipeline.py --clean }
$hash1 = (Get-FileHash "artifacts\validation\manifest.json" -Algorithm SHA256).Hash
$summaryHash1 = (Get-FileHash "artifacts\reports\management_summary.md" -Algorithm SHA256).Hash

$env:PYTHONHASHSEED = "999"
Invoke-NativeChecked "determinism run 2" { & $Python run_pipeline.py --clean }
$hash2 = (Get-FileHash "artifacts\validation\manifest.json" -Algorithm SHA256).Hash
$summaryHash2 = (Get-FileHash "artifacts\reports\management_summary.md" -Algorithm SHA256).Hash

if (($hash1 -ne $hash2) -or ($summaryHash1 -ne $summaryHash2)) {
    throw "Cross-process reproducibility check failed. Output hashes changed with PYTHONHASHSEED."
}

Write-Host "CROSS_PROCESS_REPRODUCIBILITY=PASS"

# 6. Commit and push the hardened canonical outputs.
Invoke-NativeChecked "git add" { git add . }
$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE."
}
if ($changes) {
    Invoke-NativeChecked "git commit" { git commit -m "Harden MEDNEXUS reproducibility and Windows publishing" }
    Invoke-NativeChecked "git push" { git push origin main }
}

Write-Host "=== MEDNEXUS PHASE 1 HARDENING PASSED AND PUSHED ==="
