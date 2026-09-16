$ErrorActionPreference = "Stop"

Write-Host "=== MEDNEXUS ONE-GO BUILD ==="

if (-not (Get-Command py -ErrorAction SilentlyContinue) -and -not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.11+ is required. Install Python and reopen VS Code."
}

$PythonLauncher = if (Get-Command py -ErrorAction SilentlyContinue) { "py" } else { "python" }

if (-not (Test-Path ".venv")) {
    & $PythonLauncher -m venv .venv
}

$VenvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    throw "Virtual environment Python was not created correctly."
}

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r requirements.txt
& $VenvPython setup_project.py
& $VenvPython run_pipeline.py --clean
& $VenvPython -m pytest -q

Write-Host "=== BUILD AND TESTS PASSED ==="

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is not installed. Build is complete, but GitHub publishing was skipped."
    exit 0
}

if (-not (Test-Path ".git")) {
    git init
}

git add .
$changes = git status --porcelain
if ($changes) {
    git commit -m "Build MEDNEXUS enterprise analytics platform"
}

git branch -M main

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Warning "GitHub CLI (gh) is not installed. Repository is committed locally. Install gh, run 'gh auth login', then run scripts/publish_to_github.ps1."
    exit 0
}

try {
    gh auth status | Out-Null
} catch {
    Write-Warning "GitHub CLI is not authenticated. Repository is committed locally. Run 'gh auth login', then run scripts/publish_to_github.ps1."
    exit 0
}

$remoteNames = @(git remote)
if (-not ($remoteNames -contains "origin")) {
    gh repo create MEDNEXUS --public --source=. --remote=origin --push
} else {
    git push -u origin main
}

Write-Host "=== MEDNEXUS BUILT, TESTED, COMMITTED AND PUSHED ==="
