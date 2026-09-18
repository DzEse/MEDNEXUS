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

Write-Host "=== MEDNEXUS PHASE 12 POWER BI SEMANTIC-MODEL AUDIT ==="

if (-not (Test-Path "mednexus\semantic_model.py")) {
    throw "Run this script from the MEDNEXUS repository root after pulling Phase 12."
}

$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Complete the MEDNEXUS bootstrap first."
}

Invoke-NativeChecked "MEDNEXUS clean pipeline" { & $Python run_pipeline.py --clean }

Invoke-NativeChecked "Phase 12 tests" {
    & $Python -m pytest -q tests\test_semantic_model.py tests\test_master_spec_traceability.py
}

$required = @(
    "artifacts\validation\powerbi_semantic_relationships.csv",
    "artifacts\validation\powerbi_table_roles.csv",
    "artifacts\validation\powerbi_semantic_audit.json",
    "artifacts\validation\powerbi_semantic_issues.csv",
    "artifacts\validation\powerbi_headline_reconciliation_targets.csv",
    "artifacts\validation\manifest.json"
)

$missing = @()
foreach ($file in $required) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}
if ($missing.Count -gt 0) {
    throw "Phase 12 artifact contract failed. Missing: $($missing -join ', ')"
}

$audit = Get-Content "artifacts\validation\powerbi_semantic_audit.json" -Raw | ConvertFrom-Json
if ($audit.status -ne "PASS") {
    throw "Power BI semantic-model audit failed."
}
if ([int]$audit.issue_count -ne 0) {
    throw "Power BI semantic-model audit contains issues: $($audit.issue_count)"
}
if ($audit.model_rules.cardinality -ne "1:* only") {
    throw "Power BI cardinality contract changed unexpectedly."
}
if ($audit.model_rules.cross_filter -ne "single direction only") {
    throw "Power BI cross-filter contract changed unexpectedly."
}

$relationships = Import-Csv "artifacts\validation\powerbi_semantic_relationships.csv"
$directPlantProduction = @(
    $relationships | Where-Object {
        $_.active -eq "True" -and
        $_.one_table -eq "DimPlant" -and
        $_.many_table -eq "ProductionKPI"
    }
)
if ($directPlantProduction.Count -gt 0) {
    throw "Ambiguous direct DimPlant -> ProductionKPI active path detected."
}

$directLineProduction = @(
    $relationships | Where-Object {
        $_.active -eq "True" -and
        $_.one_table -eq "DimLine" -and
        $_.many_table -eq "ProductionKPI"
    }
)
if ($directLineProduction.Count -gt 0) {
    throw "Ambiguous direct DimLine -> ProductionKPI active path detected."
}

$inactiveShipmentRoles = @(
    $relationships | Where-Object {
        $_.active -eq "False" -and
        $_.many_table -eq "Shipments" -and
        $_.many_column -in @("promised_date", "actual_delivery_date")
    }
)
if ($inactiveShipmentRoles.Count -ne 2) {
    throw "Expected exactly two optional inactive Shipment date roles."
}

$issues = Import-Csv "artifacts\validation\powerbi_semantic_issues.csv"
if ($issues.Count -gt 0) {
    throw "Semantic issue CSV is not empty."
}

$targets = Import-Csv "artifacts\validation\powerbi_headline_reconciliation_targets.csv"
if ($targets.Count -lt 15) {
    throw "Headline reconciliation target coverage is incomplete."
}
$invalidTargetStatus = @(
    $targets | Where-Object {
        $_.pbix_status -ne "TO_BE_RECONCILED_AFTER_USER_BUILDS_REPORT"
    }
)
if ($invalidTargetStatus.Count -gt 0) {
    throw "Headline targets incorrectly claim PBIX reconciliation."
}

$trust = Get-Content "artifacts\validation\data_trust.json" -Raw | ConvertFrom-Json
if ([double]$trust.data_trust_score -ne 100.0) {
    throw "Data Trust regression detected: $($trust.data_trust_score)"
}

Write-Host "POWER_BI_EXPORT_CONTRACT=PASS"
Write-Host "SEMANTIC_RELATIONSHIP_CONTRACT=PASS"
Write-Host "ONE_TO_MANY_CARDINALITY=PASS"
Write-Host "SINGLE_DIRECTION_FILTERING=PASS"
Write-Host "AMBIGUOUS_ACTIVE_PATH_GUARD=PASS"
Write-Host "DISCONNECTED_EVIDENCE_MARTS=PASS"
Write-Host "SHIPMENT_INACTIVE_DATE_ROLES=PASS"
Write-Host "HEADLINE_RECONCILIATION_TARGETS=PASS"
Write-Host "SEMANTIC_MODEL_ISSUES=$($audit.issue_count)"
Write-Host "EXPECTED_EXPORTS=$($audit.expected_export_count)"
Write-Host "ACTIVE_RELATIONSHIPS=$($audit.active_relationship_count)"
Write-Host "DISCONNECTED_TABLES=$($audit.disconnected_table_count)"
Write-Host "DATA_TRUST_SCORE=$($trust.data_trust_score)"
Write-Host "PBIX_BUILD_STATUS=NOT_YET_BUILT_BY_USER"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is unavailable. Phase 12 validation passed, but evidence was not committed."
    exit 0
}

Invoke-NativeChecked "git add" { git add . }
$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE."
}
if ($changes) {
    Invoke-NativeChecked "git commit" { git commit -m "Validate MEDNEXUS Power BI semantic-model contract" }
    Invoke-NativeChecked "git push" { git push origin main }
}

Write-Host "=== MEDNEXUS PHASE 12 POWER BI SEMANTIC-MODEL AUDIT PASSED AND PUSHED ==="
