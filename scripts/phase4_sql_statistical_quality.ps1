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

Write-Host "=== MEDNEXUS PHASE 4 SQL + STATISTICAL QUALITY ==="

if (-not (Test-Path "mednexus\statistical_quality.py")) {
    throw "Run this script from the MEDNEXUS repository root after pulling the Phase 4 files."
}

$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Complete the earlier MEDNEXUS bootstrap first."
}

Invoke-NativeChecked "MEDNEXUS clean pipeline" { & $Python run_pipeline.py --clean }

Invoke-NativeChecked "Phase 4 tests" {
    & $Python -m pytest -q tests\test_kpis.py tests\test_statistical_quality.py tests\test_sql_reconciliation.py tests\test_data_governance.py tests\test_master_spec_traceability.py
}

$required = @(
    "artifacts\validation\quality_methodology_gates.csv",
    "data\curated\quality_p_chart.csv",
    "data\curated\quality_p_chart_summary.csv",
    "data\curated\six_big_losses.csv",
    "data\curated\capacity_waterfall.csv",
    "data\curated\value_leakage.csv",
    "powerbi\exports\QualityPChart.csv",
    "powerbi\exports\SixBigLosses.csv",
    "powerbi\exports\CapacityWaterfall.csv",
    "powerbi\exports\ValueLeakage.csv"
)

$missing = @()
foreach ($file in $required) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}
if ($missing.Count -gt 0) {
    throw "Phase 4 artifact contract failed. Missing: $($missing -join ', ')"
}

$gates = Import-Csv "artifacts\validation\quality_methodology_gates.csv"

function Assert-Gate {
    param(
        [string]$Method,
        [string]$Expected
    )
    $row = $gates | Where-Object { $_.method -eq $Method }
    if ($null -eq $row) {
        throw "Methodology gate missing: $Method"
    }
    if ($row.status -ne $Expected) {
        throw "Unexpected gate for $Method. Expected $Expected, found $($row.status)."
    }
}

Assert-Gate "First Pass Yield (FPY)" "IMPLEMENTED"
Assert-Gate "p chart" "IMPLEMENTED"
Assert-Gate "Rolled Throughput Yield (RTY)" "NOT_CALCULABLE"
Assert-Gate "DPMO" "NOT_CALCULABLE"
Assert-Gate "Cp/Cpk/Pp/Ppk" "NOT_CALCULABLE"
Assert-Gate "Startup Reject loss" "NOT_CALCULABLE"
Assert-Gate "Full COPQ" "NOT_CALCULABLE"

$losses = Import-Csv "data\curated\six_big_losses.csv"
$startup = @($losses | Where-Object { $_.loss_category -eq "Startup Rejects" })
if ($startup.Count -eq 0 -or ($startup | Where-Object { $_.status -ne "NOT_CALCULABLE" }).Count -gt 0) {
    throw "Startup Rejects gate was not preserved."
}

$trust = Get-Content "artifacts\validation\data_trust.json" -Raw | ConvertFrom-Json
if ([double]$trust.data_trust_score -ne 100.0) {
    throw "Data Trust regression detected: $($trust.data_trust_score)"
}

Write-Host "FPY_SEMANTICS=PASS"
Write-Host "P_CHART_CONTROL_LAYER=PASS"
Write-Host "SIX_BIG_LOSSES_LAYER=PASS_WITH_STARTUP_GATE"
Write-Host "CAPACITY_WATERFALL=PASS"
Write-Host "VALUE_LEAKAGE=PASS_WITH_FULL_COPQ_GATE"
Write-Host "SQL_RECONCILIATION=PASS"
Write-Host "DATA_TRUST_SCORE=$($trust.data_trust_score)"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is unavailable. Phase 4 validation passed, but evidence was not committed."
    exit 0
}

Invoke-NativeChecked "git add" { git add . }
$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE."
}
if ($changes) {
    Invoke-NativeChecked "git commit" { git commit -m "Validate MEDNEXUS SQL and statistical quality intelligence" }
    Invoke-NativeChecked "git push" { git push origin main }
}

Write-Host "=== MEDNEXUS PHASE 4 SQL + STATISTICAL QUALITY PASSED AND PUSHED ==="
