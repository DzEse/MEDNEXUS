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

Write-Host "=== MEDNEXUS PHASE 7 FORECAST VALIDATION ==="

if (-not (Test-Path "mednexus\forecasting.py")) {
    throw "Run this script from the MEDNEXUS repository root after pulling Phase 7."
}

$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Complete the MEDNEXUS bootstrap first."
}

Invoke-NativeChecked "MEDNEXUS clean pipeline" { & $Python run_pipeline.py --clean }

Invoke-NativeChecked "Phase 7 tests" {
    & $Python -m pytest -q tests\test_forecasting.py tests\test_master_spec_traceability.py
}

$required = @(
    "artifacts\validation\forecast_metrics.json",
    "artifacts\validation\forecast_model_comparison.csv",
    "artifacts\validation\forecast_diagnostics.csv",
    "data\curated\demand_forecast_backtest.csv",
    "data\curated\demand_forecast_future.csv",
    "powerbi\exports\DemandForecast.csv",
    "powerbi\exports\DemandForecastBacktest.csv",
    "powerbi\exports\DemandForecastModelComparison.csv",
    "powerbi\exports\DemandForecastDiagnostics.csv"
)

$missing = @()
foreach ($file in $required) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}
if ($missing.Count -gt 0) {
    throw "Phase 7 artifact contract failed. Missing: $($missing -join ', ')"
}

$metrics = Get-Content "artifacts\validation\forecast_metrics.json" -Raw | ConvertFrom-Json

if ([int]$metrics.backtest_periods -lt [int]$metrics.minimum_backtest_periods) {
    throw "Forecast sample-adequacy gate failed."
}
if ($metrics.sample_adequacy_pass -ne $true) {
    throw "Forecast sample_adequacy_pass is not true."
}
if ($metrics.selected_mae_not_worse_than_naive -ne $true) {
    throw "Selected forecast is worse than naive on MAE."
}
if ([double]$metrics.mae -lt 0 -or [double]$metrics.rmse -lt 0) {
    throw "Forecast error metrics must be nonnegative."
}
if ([double]$metrics.smape_pct -lt 0 -or [double]$metrics.smape_pct -gt 200) {
    throw "Forecast sMAPE is outside the valid 0-200 range."
}
if ($metrics.forecast_semantics -ne "model_derived_synthetic_demand_forecast") {
    throw "Forecast semantics label is invalid."
}

$comparison = Import-Csv "artifacts\validation\forecast_model_comparison.csv"
$models = @($comparison.model)
foreach ($requiredModel in @("naive_last", "moving_average_3", "seasonal_naive_12", "linear_trend")) {
    if ($requiredModel -notin $models) {
        throw "Forecast comparator missing: $requiredModel"
    }
}

$rankOne = @($comparison | Where-Object { [int]$_.selection_rank -eq 1 })
if ($rankOne.Count -ne 1) {
    throw "Expected exactly one rank-1 forecast model."
}
if ($rankOne[0].model -ne $metrics.selected_model) {
    throw "Forecast selected-model mismatch between JSON and comparison CSV."
}

$future = Import-Csv "data\curated\demand_forecast_future.csv"
if ($future.Count -ne 3) {
    throw "Expected exactly three future monthly forecasts."
}
$invalidFuture = @($future | Where-Object { [double]$_.forecast_demand -lt 0 })
if ($invalidFuture.Count -gt 0) {
    throw "Future forecast contains negative demand."
}

$trust = Get-Content "artifacts\validation\data_trust.json" -Raw | ConvertFrom-Json
if ([double]$trust.data_trust_score -ne 100.0) {
    throw "Data Trust regression detected: $($trust.data_trust_score)"
}

Write-Host "ROLLING_ORIGIN_BACKTEST=PASS"
Write-Host "FORECAST_MODEL_COMPARISON=PASS"
Write-Host "SMAPE_BIAS_DIAGNOSTICS=PASS"
Write-Host "RESIDUAL_DIAGNOSTICS=PASS"
Write-Host "FORECAST_ADEQUACY_GATE=PASS"
Write-Host "SELECTED_FORECAST_MODEL=$($metrics.selected_model)"
Write-Host "FORECAST_ADEQUACY_STATUS=$($metrics.adequacy_status)"
Write-Host "FORECAST_MAE=$($metrics.mae)"
Write-Host "FORECAST_RMSE=$($metrics.rmse)"
Write-Host "FORECAST_SMAPE_PCT=$($metrics.smape_pct)"
Write-Host "DATA_TRUST_SCORE=$($trust.data_trust_score)"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is unavailable. Phase 7 validation passed, but evidence was not committed."
    exit 0
}

Invoke-NativeChecked "git add" { git add . }
$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE."
}
if ($changes) {
    Invoke-NativeChecked "git commit" { git commit -m "Validate MEDNEXUS demand forecasting comparators" }
    Invoke-NativeChecked "git push" { git push origin main }
}

Write-Host "=== MEDNEXUS PHASE 7 FORECAST VALIDATION PASSED AND PUSHED ==="
