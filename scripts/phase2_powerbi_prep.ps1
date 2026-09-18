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

Write-Host "=== MEDNEXUS PHASE 2 POWER BI PREP ==="

if (-not (Test-Path "mednexus\pipeline.py")) {
    throw "Run this script from the MEDNEXUS repository root."
}

$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Complete Phase 1 bootstrap/hardening first."
}

Invoke-NativeChecked "MEDNEXUS clean pipeline" { & $Python run_pipeline.py --clean }

$expected = @(
    "DimDate.csv",
    "DimPlant.csv",
    "DimLine.csv",
    "DimMachine.csv",
    "DimProduct.csv",
    "DimSupplier.csv",
    "DimCustomer.csv",
    "DimEmployee.csv",
    "EnterpriseMonthly.csv",
    "ProductionKPI.csv",
    "Downtime.csv",
    "QualityEvents.csv",
    "Maintenance.csv",
    "MORI.csv",
    "ScenarioOutputs.csv",
    "DecisionQueue.csv",
    "QualityPareto.csv",
    "QualityPChart.csv",
    "SixBigLosses.csv",
    "CapacityWaterfall.csv",
    "ValueLeakage.csv",
    "Reliability.csv",
    "PredictiveMaintenanceScores.csv",
    "PredictiveMaintenanceModelComparison.csv",
    "PredictiveMaintenanceCalibration.csv",
    "PredictiveMaintenanceFeatureImportance.csv",
    "DemandForecast.csv",
    "Finance.csv",
    "Workforce.csv",
    "Recruitment.csv",
    "Supply.csv",
    "Orders.csv",
    "Shipments.csv",
    "CustomerService.csv",
    "TechnologyIncidents.csv",
    "SaaSUsage.csv"
)

$missing = @()
foreach ($name in $expected) {
    $file = Join-Path "powerbi\exports" $name
    if (-not (Test-Path $file)) {
        $missing += $name
    }
}

if ($missing.Count -gt 0) {
    throw "Power BI export contract failed. Missing: $($missing -join ', ')"
}

$manifest = Get-Content "artifacts\validation\manifest.json" -Raw | ConvertFrom-Json
if ([double]$manifest.data_trust_score -ne 100.0) {
    throw "Expected Data Trust Score 100.0 for the canonical synthetic build; found $($manifest.data_trust_score)."
}

Write-Host "POWER_BI_EXPORT_CONTRACT=PASS"
Write-Host "POWER_BI_EXPORT_FILES=$($expected.Count)"
Write-Host "DATA_TRUST_SCORE=$($manifest.data_trust_score)"
Write-Host "Open Power BI Desktop and follow powerbi\BUILD_GUIDE.md"
Write-Host "=== MEDNEXUS PHASE 2 POWER BI PREP PASSED ==="
