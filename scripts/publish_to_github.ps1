$ErrorActionPreference = "Stop"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is not installed or not available on PATH."
}
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI (gh) is required. Install it, then run 'gh auth login'."
}

gh auth status | Out-Null

if (-not (Test-Path ".git")) {
    git init
}

git add .
$changes = git status --porcelain
if ($changes) {
    git commit -m "Build MEDNEXUS enterprise analytics platform"
}

git branch -M main

$remote = git remote 2>$null
if (-not ($remote -contains "origin")) {
    gh repo create MEDNEXUS --public --source=. --remote=origin --push
} else {
    git push -u origin main
}

Write-Host "MEDNEXUS has been pushed to GitHub."
