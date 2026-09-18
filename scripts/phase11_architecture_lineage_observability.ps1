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

Write-Host "=== MEDNEXUS PHASE 11 ARCHITECTURE + LINEAGE + OBSERVABILITY ==="

if (-not (Test-Path "mednexus\architecture_governance.py")) {
    throw "Run this script from the MEDNEXUS repository root after pulling Phase 11."
}

$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Complete the MEDNEXUS bootstrap first."
}

Invoke-NativeChecked "MEDNEXUS clean pipeline" { & $Python run_pipeline.py --clean }

Invoke-NativeChecked "Phase 11 tests" {
    & $Python -m pytest -q tests\test_architecture_governance.py tests\test_master_spec_traceability.py
}

$required = @(
    "artifacts\validation\enterprise_operations_twin.csv",
    "artifacts\validation\output_lineage_registry.csv",
    "artifacts\validation\analysis_design_checklist.csv",
    "artifacts\validation\observability_current_profile.csv",
    "artifacts\validation\cross_run_drift.csv",
    "artifacts\validation\cross_run_drift_summary.json",
    "artifacts\validation\sql_layer_contract.json",
    "artifacts\runtime\observability_baseline.csv"
)

$missing = @()
foreach ($file in $required) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}
if ($missing.Count -gt 0) {
    throw "Phase 11 artifact contract failed. Missing: $($missing -join ', ')"
}

$twin = Import-Csv "artifacts\validation\enterprise_operations_twin.csv"
if ($twin.Count -lt 15) {
    throw "Enterprise Operations Twin catalog is unexpectedly small."
}
if (@($twin | Where-Object { $_.twin_type -ne "CONCEPTUAL_ENTERPRISE_OPERATIONS_TWIN" }).Count -gt 0) {
    throw "Twin conceptual-type guard failed."
}
if (@($twin | Where-Object { $_.three_dimensional_model -ne "False" }).Count -gt 0) {
    throw "Twin incorrectly claims a 3D model."
}

$lineage = Import-Csv "artifacts\validation\output_lineage_registry.csv"
if ($lineage.Count -lt 10) {
    throw "Output lineage registry does not cover enough headline outputs."
}
foreach ($column in @("source","transformation","analytical_table_or_artifact","method_or_metric","bi_surface","decision_supported")) {
    if (@($lineage | Where-Object { [string]::IsNullOrWhiteSpace($_.$column) }).Count -gt 0) {
        throw "Output lineage has missing values in $column."
    }
}

$checklist = Import-Csv "artifacts\validation\analysis_design_checklist.csv"
if ($checklist.Count -ne 10) {
    throw "Expected exactly 10 analysis-design gates."
}
if (@($checklist | Where-Object { $_.mandatory -ne "True" }).Count -gt 0) {
    throw "Analysis-design checklist contains non-mandatory canonical gates."
}

$driftSummary = Get-Content "artifacts\validation\cross_run_drift_summary.json" -Raw | ConvertFrom-Json
if ([int]$driftSummary.alert_count -ne 0) {
    throw "Canonical rebuild produced unexpected drift alerts: $($driftSummary.alert_count)"
}

$drift = Import-Csv "artifacts\validation\cross_run_drift.csv"
$invalidDrift = @(
    $drift | Where-Object {
        $_.status -ne "PASS" -and $_.status -ne "BASELINE_INITIALIZED"
    }
)
if ($invalidDrift.Count -gt 0) {
    throw "Cross-run drift contains unexpected alert states."
}

$sql = Get-Content "artifacts\validation\sql_layer_contract.json" -Raw | ConvertFrom-Json
if ($sql.status -ne "PASS") {
    throw "Layered SQL contract did not pass."
}
if ([int]$sql.order_fulfillment_grain.duplicate_order_rows -ne 0) {
    throw "Order-fulfillment SQL layer duplicates order grain."
}
if ([int]$sql.machine_hierarchy_grain.duplicate_machine_rows -ne 0) {
    throw "Machine-hierarchy SQL layer duplicates machine grain."
}

$trust = Get-Content "artifacts\validation\data_trust.json" -Raw | ConvertFrom-Json
if ([double]$trust.data_trust_score -ne 100.0) {
    throw "Data Trust regression detected: $($trust.data_trust_score)"
}

Write-Host "ENTERPRISE_OPERATIONS_TWIN=PASS"
Write-Host "TWIN_3D_CLAIM_GUARD=PASS"
Write-Host "OUTPUT_LEVEL_LINEAGE=PASS"
Write-Host "ANALYSIS_DESIGN_GATE=PASS"
Write-Host "PERSISTENT_DRIFT_BASELINE=PASS"
Write-Host "ROW_MISSINGNESS_SCHEMA_CATEGORY_MODEL_KPI_DRIFT=PASS"
Write-Host "LAYERED_SQL_ARCHITECTURE=PASS"
Write-Host "SQL_GRAIN_RECONCILIATION=PASS"
Write-Host "DRIFT_ALERT_COUNT=$($driftSummary.alert_count)"
Write-Host "DATA_TRUST_SCORE=$($trust.data_trust_score)"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is unavailable. Phase 11 validation passed, but evidence was not committed."
    exit 0
}

Invoke-NativeChecked "git add" { git add . }
$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE."
}
if ($changes) {
    Invoke-NativeChecked "git commit" { git commit -m "Validate MEDNEXUS architecture lineage and observability" }
    Invoke-NativeChecked "git push" { git push origin main }
}

Write-Host "=== MEDNEXUS PHASE 11 ARCHITECTURE + LINEAGE + OBSERVABILITY PASSED AND PUSHED ==="
