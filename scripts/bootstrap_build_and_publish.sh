#!/usr/bin/env bash
set -euo pipefail

echo "=== MEDNEXUS ONE-GO BUILD ==="
PYTHON_BIN="${PYTHON_BIN:-python3}"
command -v "$PYTHON_BIN" >/dev/null || { echo "Python 3.11+ is required."; exit 1; }

[ -d .venv ] || "$PYTHON_BIN" -m venv .venv
VENV_PY=".venv/bin/python"
"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install -r requirements.txt
"$VENV_PY" setup_project.py
"$VENV_PY" run_pipeline.py --clean
"$VENV_PY" -m pytest -q

echo "=== BUILD AND TESTS PASSED ==="

if ! command -v git >/dev/null; then
  echo "Git not installed; GitHub publishing skipped."
  exit 0
fi

[ -d .git ] || git init
git add .
if [ -n "$(git status --porcelain)" ]; then
  git commit -m "Build MEDNEXUS enterprise analytics platform"
fi
git branch -M main

if ! command -v gh >/dev/null; then
  echo "GitHub CLI not installed. Local Git commit is complete."
  exit 0
fi
if ! gh auth status >/dev/null 2>&1; then
  echo "GitHub CLI is not authenticated. Run: gh auth login"
  exit 0
fi

if ! git remote | grep -qx origin; then
  gh repo create MEDNEXUS --public --source=. --remote=origin --push
else
  git push -u origin main
fi

echo "=== MEDNEXUS BUILT, TESTED, COMMITTED AND PUSHED ==="
