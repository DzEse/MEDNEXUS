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

Write-Host "=== MEDNEXUS PHASE 12H POWER BI DESKTOP HANDOFF PREP ==="

if (-not (Test-Path "mednexus\powerbi_handoff.py")) {
    throw "Run this script from the MEDNEXUS repository root after pulling Phase 12H."
}

$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Use the existing repository virtual environment."
}

Invoke-NativeChecked "Phase 12H handoff generation" {
    & $Python -c "from mednexus.powerbi_handoff import prepare_handoff; print(prepare_handoff())"
}

Invoke-NativeChecked "Phase 12H targeted tests" {
    & $Python -m pytest -q tests\test_powerbi_handoff.py tests\test_semantic_model.py
}

$required = @(
    "powerbi\handoff\import_plan.csv",
    "powerbi\handoff\relationship_build_order.csv",
    "powerbi\handoff\headline_reconciliation_checklist.csv",
    "powerbi\handoff\pbix_acceptance_checklist.csv",
    "powerbi\handoff\handoff_summary.json"
)

$missing = @()
foreach ($file in $required) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}
if ($missing.Count -gt 0) {
    throw "Phase 12H handoff contract failed. Missing: $($missing -join ', ')"
}

$summary = Get-Content "powerbi\handoff\handoff_summary.json" -Raw | ConvertFrom-Json

if ($summary.status -ne "PASS") { throw "Phase 12H repository handoff is not PASS." }
if ($summary.handoff_status -ne "POWER_BI_DESKTOP_HANDOFF_PREPARED_NOT_PBIX_VALIDATED") {
    throw "Unexpected Phase 12H handoff status."
}
if ([int]$summary.canonical_export_count -ne 58) { throw "Expected 58 canonical exports." }
if ([int]$summary.missing_export_count -ne 0) { throw "One or more canonical exports are missing." }
if ([int]$summary.connected_table_count -ne 35) { throw "Expected 35 connected tables." }
if ([int]$summary.disconnected_table_count -ne 23) { throw "Expected 23 disconnected tables." }
if ([int]$summary.active_relationship_count -ne 45) { throw "Expected 45 active relationships." }
if ([int]$summary.inactive_relationship_count -ne 2) { throw "Expected 2 inactive relationships." }
if ([int]$summary.headline_reconciliation_target_count -ne 19) { throw "Expected 19 headline reconciliation targets." }
if ([int]$summary.pbix_acceptance_check_count -ne 30) { throw "Expected 30 PBIX acceptance checks." }
if ($summary.pbix_built -ne $false) { throw "Phase 12H must not claim PBIX build completion." }
if ($summary.pbix_validated -ne $false) { throw "Phase 12H must not claim PBIX validation." }
if ($summary.evidence_status -ne "TEMPLATE_ONLY_NO_PBIX_EVIDENCE_YET") {
    throw "Phase 12H must not fabricate PBIX evidence."
}

$relationships = Import-Csv "powerbi\handoff\relationship_build_order.csv"
if ($relationships.Count -ne 47) { throw "Expected 47 total relationships." }
if (@($relationships | Where-Object { $_.pbix_creation_status -ne "NOT_YET_CREATED_IN_PBIX" }).Count -gt 0) {
    throw "Relationship handoff contains fabricated PBIX creation status."
}
if (@($relationships | Where-Object { $_.pbix_validation_status -ne "NOT_YET_VALIDATED_IN_PBIX" }).Count -gt 0) {
    throw "Relationship handoff contains fabricated PBIX validation status."
}

$acceptance = Import-Csv "powerbi\handoff\pbix_acceptance_checklist.csv"
if (@($acceptance | Where-Object { $_.status -ne "NOT_YET_VALIDATED_IN_PBIX" }).Count -gt 0) {
    throw "PBIX acceptance checklist contains fabricated PASS status."
}

$recon = Import-Csv "powerbi\handoff\headline_reconciliation_checklist.csv"
if (@($recon | Where-Object { $_.validation_status -ne "NOT_YET_VALIDATED_IN_PBIX" }).Count -gt 0) {
    throw "Headline reconciliation checklist contains fabricated PBIX status."
}

Write-Host "PHASE12H_REPOSITORY_STATUS=PASS"
Write-Host "CANONICAL_EXPORTS=$($summary.canonical_export_count)"
Write-Host "CONNECTED_TABLES=$($summary.connected_table_count)"
Write-Host "DISCONNECTED_TABLES=$($summary.disconnected_table_count)"
Write-Host "ACTIVE_RELATIONSHIPS=$($summary.active_relationship_count)"
Write-Host "INACTIVE_RELATIONSHIPS=$($summary.inactive_relationship_count)"
Write-Host "HEADLINE_TARGETS=$($summary.headline_reconciliation_target_count)"
Write-Host "PBIX_ACCEPTANCE_CHECKS=$($summary.pbix_acceptance_check_count)"
Write-Host "PBIX_BUILT=$($summary.pbix_built)"
Write-Host "PBIX_VALIDATED=$($summary.pbix_validated)"
Write-Host "EVIDENCE_STATUS=$($summary.evidence_status)"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is unavailable. Handoff generation passed, but generated handoff files were not committed."
    exit 0
}

$handoffFiles = @(
    "powerbi/handoff/import_plan.csv",
    "powerbi/handoff/relationship_build_order.csv",
    "powerbi/handoff/headline_reconciliation_checklist.csv",
    "powerbi/handoff/pbix_acceptance_checklist.csv",
    "powerbi/handoff/handoff_summary.json"
)

Invoke-NativeChecked "git add Phase 12H handoff" {
    git -c gc.auto=0 -c maintenance.auto=false add -- $handoffFiles
}

$staged = git diff --cached --name-only
if ($LASTEXITCODE -ne 0) {
    throw "git diff --cached failed with exit code $LASTEXITCODE."
}

if ($staged) {
    Invoke-NativeChecked "git commit Phase 12H handoff" {
        git -c gc.auto=0 -c maintenance.auto=false commit -m "Prepare MEDNEXUS Phase 12H Power BI Desktop handoff"
    }
    Invoke-NativeChecked "git push Phase 12H handoff" {
        git -c gc.auto=0 -c maintenance.auto=false push origin main
    }
}

Write-Host "=== MEDNEXUS PHASE 12H HANDOFF PREPARED ==="
Write-Host "NEXT: Open Power BI Desktop and follow powerbi\PHASE_12H_DESKTOP_HANDOFF.md"
