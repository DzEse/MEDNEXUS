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