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

Write-Host "=== MEDNEXUS PHASE 12F PROTOTYPE PROMOTION + POWER BI FILTER-BEHAVIOR VALIDATION ==="

if (-not (Test-Path "mednexus\promotion_filter_validation.py")) {
    throw "Run this script from the MEDNEXUS repository root after pulling Phase 12F."
}

$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Complete the MEDNEXUS bootstrap first."
}

Invoke-NativeChecked "Phase 12F validation build" {
    & $Python -c "from mednexus.promotion_filter_validation import run_phase12f; print(run_phase12f())"
}

Invoke-NativeChecked "Phase 12F targeted tests" {
    & $Python -m pytest -q tests\test_promotion_filter_validation.py tests\test_semantic_model.py tests\test_master_spec_traceability.py
}

$required = @(
    "artifacts\validation\phase12f_promotion_decisions.csv",
    "artifacts\validation\phase12f_proposed_table_roles.csv",
    "artifacts\validation\phase12f_proposed_relationships.csv",
    "artifacts\validation\phase12f_filter_behavior_checks.csv",
    "artifacts\validation\phase12f_semantic_issues.csv",
    "artifacts\validation\phase12f_geo_enrichment_contract.csv",
    "artifacts\validation\phase12f_local_benchmark.json",
    "artifacts\validation\phase12f_summary.json"
)

$missing = @()
foreach ($file in $required) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}
if ($missing.Count -gt 0) {
    throw "Phase 12F artifact contract failed. Missing: $($missing -join ', ')"
}

$summary = Get-Content "artifacts\validation\phase12f_summary.json" -Raw | ConvertFrom-Json
if ($summary.status -ne "PASS") {
    throw "Phase 12F summary is not PASS."
}
if ([int]$summary.promotion_decision_count -ne 20) {
    throw "Expected 20 explicit prototype promotion decisions."
}
if ([int]$summary.approved_structure_count -ne 8) {
    throw "Expected 8 approved structures."
}
if ([int]$summary.approved_new_export_count -ne 5) {
    throw "Expected 5 proposed new exports."
}
if ([int]$summary.approved_geo_merge_count -ne 3) {
    throw "Expected 3 geography attribute merges."
}
if ([int]$summary.rework_required_count -ne 8) {
    throw "Expected 8 structures to remain rework-required."
}
if ([int]$summary.deferred_count -ne 3) {
    throw "Expected 3 structures to remain deferred."
}
if ([int]$summary.redundant_not_promoted_count -ne 1) {
    throw "Expected 1 redundant structure to remain not promoted."
}
if ([int]$summary.current_canonical_export_count -ne 53) {
    throw "Current canonical export count changed unexpectedly."
}
if ([int]$summary.proposed_post_promotion_export_count -ne 58) {
    throw "Proposed post-promotion export count is not 58."
}
if ($summary.current_canonical_semantic_model_changed -ne $false) {
    throw "Phase 12F must not mutate the canonical semantic model."
}
if ($summary.current_canonical_powerbi_export_contract_changed -ne $false) {
    throw "Phase 12F must not mutate the canonical Power BI export contract."
}
if ([int]$summary.filter_behavior_failure_count -ne 0) {
    throw "Phase 12F filter-behavior failures detected."
}
if ([int]$summary.semantic_issue_count -ne 0) {
    throw "Phase 12F semantic issues detected."
}
if ($summary.pbix_model_validated -ne $false) {
    throw "Phase 12F must not claim an actual PBIX was validated."
}
if ($summary.powerbi_validation_scope -ne "CONTRACT_SIMULATION_NOT_ACTUAL_PBIX") {
    throw "Power BI validation scope changed unexpectedly."
}
if ($summary.promotion_implementation_status -ne "APPROVED_PLAN_NOT_YET_APPLIED") {
    throw "Promotion implementation status changed unexpectedly."
}

$issues = Import-Csv "artifacts\validation\phase12f_semantic_issues.csv"
if ($issues.Count -gt 0) {
    throw "Phase 12F semantic issue CSV is not empty."
}

$checks = Import-Csv "artifacts\validation\phase12f_filter_behavior_checks.csv"
$failed = @($checks | Where-Object { $_.status -ne "PASS" })
if ($failed.Count -gt 0) {
    throw "Phase 12F filter-behavior CSV contains failures."
}

Write-Host "PHASE12F_STATUS=PASS"
Write-Host "PROMOTION_DECISIONS=$($summary.promotion_decision_count)"
Write-Host "APPROVED_STRUCTURES=$($summary.approved_structure_count)"
Write-Host "APPROVED_NEW_EXPORTS=$($summary.approved_new_export_count)"
Write-Host "APPROVED_GEO_MERGES=$($summary.approved_geo_merge_count)"
Write-Host "REWORK_REQUIRED=$($summary.rework_required_count)"
Write-Host "DEFERRED=$($summary.deferred_count)"
Write-Host "REDUNDANT_NOT_PROMOTED=$($summary.redundant_not_promoted_count)"
Write-Host "CURRENT_CANONICAL_EXPORTS=$($summary.current_canonical_export_count)"
Write-Host "PROPOSED_POST_PROMOTION_EXPORTS=$($summary.proposed_post_promotion_export_count)"
Write-Host "FILTER_BEHAVIOR_FAILURES=$($summary.filter_behavior_failure_count)"
Write-Host "SEMANTIC_ISSUES=$($summary.semantic_issue_count)"
Write-Host "PBIX_MODEL_VALIDATED=$($summary.pbix_model_validated)"
Write-Host "PROMOTION_IMPLEMENTATION_STATUS=$($summary.promotion_implementation_status)"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is unavailable. Phase 12F validation passed, but evidence was not committed."
    exit 0
}

Invoke-NativeChecked "git add" {
    git add artifacts/validation/phase12f_promotion_decisions.csv artifacts/validation/phase12f_proposed_table_roles.csv artifacts/validation/phase12f_proposed_relationships.csv artifacts/validation/phase12f_filter_behavior_checks.csv artifacts/validation/phase12f_semantic_issues.csv artifacts/validation/phase12f_geo_enrichment_contract.csv artifacts/validation/phase12f_local_benchmark.json artifacts/validation/phase12f_summary.json
}

$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE."
}

if ($changes) {
    Invoke-NativeChecked "git commit" { git commit -m "Validate MEDNEXUS Phase 12F promotion and filter behavior" }
    Invoke-NativeChecked "git push" { git push origin main }
}

Write-Host "=== MEDNEXUS PHASE 12F PROMOTION + FILTER-BEHAVIOR VALIDATION PASSED AND PUSHED ==="
