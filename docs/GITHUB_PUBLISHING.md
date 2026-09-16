# GitHub Publishing

The repository intentionally excludes generated datasets, the SQLite database, model binaries and PBIX files from Git.

## Recommended commands

```bash
git init
git add .
git commit -m "Build MEDNEXUS enterprise analytics platform"
git branch -M main
gh repo create MEDNEXUS --public --source=. --remote=origin --push
```

If the repository already exists:

```bash
git remote add origin https://github.com/<YOUR_USERNAME>/MEDNEXUS.git
git push -u origin main
```

Use `scripts/publish_to_github.ps1` on Windows for a guided one-run publication.
