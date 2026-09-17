$ErrorActionPreference = "Stop"

function Invoke-NativeChecked {
    param(
        [Parameter(Mandatory=$true)][string]$Step,
        [Parameter(Mandatory=$true)][scriptblock]$Command
    )
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Step failed with exit code $LASTEXITCODE."
    }
}

Write-Host "=== MEDNEXUS PHASE 3 DATA GOVERNANCE ==="

if (-not (Test-Path "mednexus\quality.py")) {
    throw "Run this script from the MEDNEXUS repository root."
}

$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Complete the earlier MEDNEXUS bootstrap first."
}

Invoke-NativeChecked "MEDNEXUS clean pipeline" { & $Python run_pipeline.py --clean }
Invoke-NativeChecked "governance tests" { & $Python -m pytest -q tests\test_data_governance.py tests\test_quality.py tests\test_master_spec_traceability.py }

$required = @(
    "artifacts\validation\data_quality_tables.csv",
    "artifacts\validation\data_quality_business_checks.csv",
    "artifacts\validation\referential_integrity.csv",
    "artifacts\validation\data_observability.csv",
    "artifacts\validation\model_input_profile.csv",
    "artifacts\validation\data_dictionary.csv",
    "artifacts\validation\table_register.csv",
    "artifacts\validation\data_trust.json"
)

$missing = @()
foreach ($file in $required) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}
if ($missing.Count -gt 0) {
    throw "Governance artifact contract failed. Missing: $($missing -join ', ')"
}

$trust = Get-Content "artifacts\validation\data_trust.json" -Raw | ConvertFrom-Json
if ([double]$trust.data_trust_score -ne 100.0) {
    throw "Canonical synthetic build expected Data Trust Score 100.0; found $($trust.data_trust_score)."
}

$expectedDimensions = @(
    "completeness",
    "validity",
    "consistency",
    "uniqueness",
    "timeliness",
    "referential_integrity",
    "schema_consistency",
    "freshness"
)

foreach ($dimension in $expectedDimensions) {
    if ($null -eq $trust.components.$dimension) {
        throw "Data Trust component missing: $dimension"
    }
    if ([double]$trust.components.$dimension -ne 1.0) {
        throw "Data Trust component did not fully pass: $dimension=$($trust.components.$dimension)"
    }
}

$ri = Import-Csv "artifacts\validation\referential_integrity.csv"
$riFailures = @($ri | Where-Object { $_.status -ne "PASS" })
if ($riFailures.Count -gt 0) {
    throw "Referential-integrity gate failed for $($riFailures.Count) checks."
}

$obs = Import-Csv "artifacts\validation\data_observability.csv"
$obsFailures = @($obs | Where-Object { $_.status -ne "PASS" })
if ($obsFailures.Count -gt 0) {
    throw "Observability gate failed for $($obsFailures.Count) tables."
}

$dictionary = Import-Csv "artifacts\validation\data_dictionary.csv"
$register = Import-Csv "artifacts\validation\table_register.csv"
if ($dictionary.Count -lt 100) {
    throw "Data dictionary appears incomplete: only $($dictionary.Count) field rows."
}
if ($register.Count -lt 20) {
    throw "Table register appears incomplete: only $($register.Count) table rows."
}

Write-Host "DATA_GOVERNANCE_GATE=PASS"
Write-Host "REFERENTIAL_INTEGRITY=PASS"
Write-Host "OBSERVABILITY=PASS"
Write-Host "DATA_DICTIONARY_FIELDS=$($dictionary.Count)"
Write-Host "TABLE_REGISTER_ROWS=$($register.Count)"
Write-Host "DATA_TRUST_SCORE=$($trust.data_trust_score)"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is unavailable. Governance validation passed, but evidence was not committed."
    exit 0
}

Invoke-NativeChecked "git add" { git add . }
$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE."
}
if ($changes) {
    Invoke-NativeChecked "git commit" { git commit -m "Validate MEDNEXUS data governance and observability" }
    Invoke-NativeChecked "git push" { git push origin main }
}

Write-Host "=== MEDNEXUS PHASE 3 DATA GOVERNANCE PASSED AND PUSHED ==="
