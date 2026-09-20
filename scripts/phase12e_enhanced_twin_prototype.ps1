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

Write-Host "=== MEDNEXUS PHASE 12E ENHANCED ENTERPRISE DATASET + DIGITAL TWIN PROTOTYPE ==="

if (-not (Test-Path "mednexus\enhanced_twin_prototype.py")) {
    throw "Run this script from the MEDNEXUS repository root after pulling Phase 12E."
}

$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Complete the MEDNEXUS bootstrap first."
}

Invoke-NativeChecked "Phase 12E prototype build" {
    & $Python -c "from mednexus.enhanced_twin_prototype import run_phase12e; print(run_phase12e())"
}

Invoke-NativeChecked "Phase 12E targeted tests" {
    & $Python -m pytest -q tests\test_enhanced_twin_prototype.py tests\test_master_spec_traceability.py
}

$required = @(
    "artifacts\validation\phase12e_table_contract.csv",
    "artifacts\validation\phase12e_relationship_contract.csv",
    "artifacts\validation\phase12e_validation_checks.csv",
    "artifacts\validation\phase12e_volume_profile.csv",
    "artifacts\validation\phase12e_generation_assumptions.json",
    "artifacts\validation\phase12e_summary.json"
)

$missing = @()
foreach ($file in $required) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}
if ($missing.Count -gt 0) {
    throw "Phase 12E artifact contract failed. Missing: $($missing -join ', ')"
}

$summary = Get-Content "artifacts\validation\phase12e_summary.json" -Raw | ConvertFrom-Json
if ($summary.status -ne "PASS") {
    throw "Phase 12E summary is not PASS."
}
if ([int]$summary.validation_failure_count -ne 0) {
    throw "Phase 12E validation failures detected: $($summary.validation_failure_count)"
}
if ($summary.canonical_semantic_model_changed -ne $false) {
    throw "Phase 12E must not silently alter the canonical semantic model."
}
if ($summary.canonical_powerbi_export_contract_changed -ne $false) {
    throw "Phase 12E must not silently alter the canonical Power BI export contract."
}
if ($summary.full_process_mining_status -ne "NOT_ADMITTED_NO_EXPLICIT_ORDER_PRODUCTION_LINK") {
    throw "Full process-mining gate changed unexpectedly."
}

$checks = Import-Csv "artifacts\validation\phase12e_validation_checks.csv"
$failed = @($checks | Where-Object { $_.status -ne "PASS" })
if ($failed.Count -gt 0) {
    throw "Phase 12E validation check CSV contains failures."
}

$contracts = Import-Csv "artifacts\validation\phase12e_table_contract.csv"
if ($contracts.Count -ne 20) {
    throw "Expected 20 Phase 12E prototype table contracts; found $($contracts.Count)."
}
$badPromotion = @($contracts | Where-Object { $_.promotion_status -ne "PROTOTYPE_NOT_CANONICAL" })
if ($badPromotion.Count -gt 0) {
    throw "A prototype table was incorrectly marked as canonical/promoted."
}

$relationships = Import-Csv "artifacts\validation\phase12e_relationship_contract.csv"
$badRelationship = @($relationships | Where-Object { $_.relationship_status -ne "PROTOTYPE_ONLY_NOT_POWER_BI_PROMOTED" })
if ($badRelationship.Count -gt 0) {
    throw "A Phase 12E relationship was incorrectly promoted into the Power BI model."
}

Write-Host "PHASE12E_PROTOTYPE_STATUS=PASS"
Write-Host "PROTOTYPE_TABLES=$($summary.prototype_table_count)"
Write-Host "PROTOTYPE_ROWS=$($summary.prototype_row_count)"
Write-Host "VALIDATION_CHECKS=$($summary.validation_check_count)"
Write-Host "VALIDATION_FAILURES=$($summary.validation_failure_count)"
Write-Host "CANONICAL_SEMANTIC_MODEL_CHANGED=$($summary.canonical_semantic_model_changed)"
Write-Host "CANONICAL_POWERBI_EXPORT_CONTRACT_CHANGED=$($summary.canonical_powerbi_export_contract_changed)"
Write-Host "FULL_PROCESS_MINING_STATUS=$($summary.full_process_mining_status)"
Write-Host "PROMOTION_STATUS=PROTOTYPE_NOT_CANONICAL"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is unavailable. Phase 12E validation passed, but evidence was not committed."
    exit 0
}

Invoke-NativeChecked "git add" {
    git add artifacts/validation/phase12e_table_contract.csv artifacts/validation/phase12e_relationship_contract.csv artifacts/validation/phase12e_validation_checks.csv artifacts/validation/phase12e_volume_profile.csv artifacts/validation/phase12e_generation_assumptions.json artifacts/validation/phase12e_summary.json
}

$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE."
}

if ($changes) {
    Invoke-NativeChecked "git commit" { git commit -m "Validate MEDNEXUS Phase 12E enhanced twin prototype" }
    Invoke-NativeChecked "git push" { git push origin main }
}

Write-Host "=== MEDNEXUS PHASE 12E ENHANCED TWIN PROTOTYPE PASSED AND PUSHED ==="
