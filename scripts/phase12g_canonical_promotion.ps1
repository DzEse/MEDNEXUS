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

Write-Host "=== MEDNEXUS PHASE 12G CANONICAL PROMOTION ==="

if (-not (Test-Path "mednexus\canonical_enhancement.py")) {
    throw "Run this script from the MEDNEXUS repository root after pulling Phase 12G."
}

$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Complete the MEDNEXUS bootstrap first."
}

Invoke-NativeChecked "Canonical MEDNEXUS pipeline" {
    & $Python run_pipeline.py --clean
}

Invoke-NativeChecked "Phase 12G targeted tests" {
    & $Python -m pytest -q tests\test_canonical_enhancement.py tests\test_semantic_model.py tests\test_master_spec_traceability.py
}

$required = @(
    "artifacts\validation\phase12g_source_promotion_checks.csv",
    "artifacts\validation\phase12g_summary.json",
    "artifacts\validation\powerbi_semantic_relationships.csv",
    "artifacts\validation\powerbi_table_roles.csv",
    "artifacts\validation\powerbi_semantic_issues.csv",
    "artifacts\validation\powerbi_semantic_audit.json",
    "artifacts\validation\powerbi_headline_reconciliation_targets.csv",
    "artifacts\validation\manifest.json",
    "artifacts\validation\data_dictionary.csv",
    "artifacts\validation\table_register.csv"
)

$missing = @()
foreach ($file in $required) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}
if ($missing.Count -gt 0) {
    throw "Phase 12G evidence contract failed. Missing: $($missing -join ', ')"
}

$summary = Get-Content "artifacts\validation\phase12g_summary.json" -Raw | ConvertFrom-Json
if ($summary.status -ne "PASS") { throw "Phase 12G summary is not PASS." }
if ($summary.canonical_promotion_status -ne "APPLIED") { throw "Canonical promotion is not APPLIED." }
if ([int]$summary.approved_new_source_table_count -ne 5) { throw "Expected 5 promoted source tables." }
if ([int]$summary.approved_geo_merge_count -ne 3) { throw "Expected 3 geography merges." }
if ([int]$summary.canonical_export_count -ne 58) { throw "Expected 58 canonical exports." }
if ([int]$summary.active_relationship_count -ne 45) { throw "Expected 45 active relationships." }
if ([int]$summary.inactive_relationship_count -ne 2) { throw "Expected 2 inactive relationships." }
if ([int]$summary.semantic_issue_count -ne 0) { throw "Semantic issues detected." }
if ([int]$summary.source_promotion_failure_count -ne 0) { throw "Source-promotion failures detected." }
if ([double]$summary.data_trust_score -ne 100.0) { throw "Expected Data Trust Score 100.0." }
if ($summary.pbix_model_validated -ne $false) { throw "Repository must not claim PBIX validation." }
if ($summary.pbix_build_status -ne "NOT_YET_BUILT_BY_USER") { throw "PBIX status changed unexpectedly." }

$audit = Get-Content "artifacts\validation\powerbi_semantic_audit.json" -Raw | ConvertFrom-Json
if ($audit.status -ne "PASS") { throw "Semantic audit is not PASS." }
if ([int]$audit.expected_export_count -ne 58) { throw "Semantic audit expected export count is not 58." }
if ([int]$audit.actual_export_count -ne 58) { throw "Semantic audit actual export count is not 58." }
if ([int]$audit.active_relationship_count -ne 45) { throw "Semantic audit active relationship count is not 45." }
if ([int]$audit.inactive_relationship_count -ne 2) { throw "Semantic audit inactive relationship count is not 2." }
if ([int]$audit.issue_count -ne 0) { throw "Semantic audit contains issues." }

$manifest = Get-Content "artifacts\validation\manifest.json" -Raw | ConvertFrom-Json
if ([double]$manifest.data_trust_score -ne 100.0) { throw "Manifest Data Trust Score is not 100.0." }
if ([int]$manifest.generated_files.Count -ne 58) { throw "Manifest does not contain 58 Power BI exports." }

$sourceChecks = Import-Csv "artifacts\validation\phase12g_source_promotion_checks.csv"
$failedSource = @($sourceChecks | Where-Object { $_.status -ne "PASS" })
if ($failedSource.Count -gt 0) { throw "Phase 12G source promotion checks contain failures." }

$semanticIssues = Import-Csv "artifacts\validation\powerbi_semantic_issues.csv"
if ($semanticIssues.Count -gt 0) { throw "Power BI semantic issues CSV is not empty." }

$relationships = Import-Csv "artifacts\validation\powerbi_semantic_relationships.csv"
if (@($relationships | Where-Object { $_.one_table -eq "DimRegion" -or $_.many_table -eq "DimRegion" }).Count -gt 0) {
    throw "A shared active DimRegion relationship was introduced unexpectedly."
}
if (@($relationships | Where-Object { $_.one_table -eq "DimLine" -and $_.many_table -eq "EmployeeAssignment" -and $_.active -eq "True" }).Count -gt 0) {
    throw "Direct active DimLine->EmployeeAssignment relationship is prohibited."
}
if (@($relationships | Where-Object { $_.one_table -eq "DimDepartment" -and $_.many_table -eq "EmployeeAssignment" -and $_.active -eq "True" }).Count -gt 0) {
    throw "Direct active DimDepartment->EmployeeAssignment relationship is prohibited."
}

$plant = Import-Csv "powerbi\exports\DimPlant.csv"
$supplier = Import-Csv "powerbi\exports\DimSupplier.csv"
$customer = Import-Csv "powerbi\exports\DimCustomer.csv"
$warehouse = Import-Csv "powerbi\exports\DimWarehouse.csv"
foreach ($df in @($plant, $supplier, $customer, $warehouse)) {
    if (@($df | Where-Object { $_.geography_status -ne "SIMULATED_ENTERPRISE_FOOTPRINT" }).Count -gt 0) {
        throw "A promoted geography table is missing the simulated-footprint label."
    }
}

$nonApproved = @(
    "DimRegion.csv",
    "DimMaterial.csv",
    "ProductMaterial.csv",
    "Vacancy.csv",
    "CandidateEvent.csv",
    "ProductionEvent.csv",
    "InspectionEvent.csv",
    "PurchaseOrder.csv",
    "Receipt.csv",
    "InventoryMovement.csv",
    "InventorySnapshot.csv"
)
foreach ($name in $nonApproved) {
    if (Test-Path (Join-Path "powerbi\exports" $name)) {
        throw "Non-approved prototype export found: $name"
    }
}

Write-Host "PHASE12G_STATUS=PASS"
Write-Host "CANONICAL_PROMOTION_STATUS=$($summary.canonical_promotion_status)"
Write-Host "CANONICAL_EXPORTS=$($summary.canonical_export_count)"
Write-Host "ACTIVE_RELATIONSHIPS=$($summary.active_relationship_count)"
Write-Host "INACTIVE_RELATIONSHIPS=$($summary.inactive_relationship_count)"
Write-Host "SEMANTIC_ISSUES=$($summary.semantic_issue_count)"
Write-Host "SOURCE_PROMOTION_FAILURES=$($summary.source_promotion_failure_count)"
Write-Host "DATA_TRUST_SCORE=$($summary.data_trust_score)"
Write-Host "PBIX_MODEL_VALIDATED=$($summary.pbix_model_validated)"
Write-Host "PBIX_BUILD_STATUS=$($summary.pbix_build_status)"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is unavailable. Phase 12G validation passed, but evidence was not committed."
    exit 0
}

$evidence = @(
    "artifacts/validation/phase12g_source_promotion_checks.csv",
    "artifacts/validation/phase12g_summary.json",
    "artifacts/validation/powerbi_semantic_relationships.csv",
    "artifacts/validation/powerbi_table_roles.csv",
    "artifacts/validation/powerbi_semantic_issues.csv",
    "artifacts/validation/powerbi_semantic_audit.json",
    "artifacts/validation/powerbi_headline_reconciliation_targets.csv",
    "artifacts/validation/manifest.json",
    "artifacts/validation/data_dictionary.csv",
    "artifacts/validation/table_register.csv"
)

Invoke-NativeChecked "git add Phase 12G evidence" {
    git -c gc.auto=0 -c maintenance.auto=false add -- $evidence
}

$staged = git diff --cached --name-only
if ($LASTEXITCODE -ne 0) { throw "git diff --cached failed with exit code $LASTEXITCODE." }

if ($staged) {
    Invoke-NativeChecked "git commit Phase 12G evidence" {
        git -c gc.auto=0 -c maintenance.auto=false commit -m "Validate MEDNEXUS Phase 12G canonical promotion"
    }
    Invoke-NativeChecked "git push Phase 12G evidence" {
        git -c gc.auto=0 -c maintenance.auto=false push origin main
    }
}

Write-Host "=== MEDNEXUS PHASE 12G CANONICAL PROMOTION PASSED AND PUSHED ==="
