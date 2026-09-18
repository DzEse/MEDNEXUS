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

Write-Host "=== MEDNEXUS PHASE 5 PREDICTIVE MAINTENANCE VALIDATION ==="

if (-not (Test-Path "tests\test_predictive_maintenance.py")) {
    throw "Run this script from the MEDNEXUS repository root after pulling the Phase 5 files."
}

$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Complete the MEDNEXUS bootstrap first."
}

Invoke-NativeChecked "MEDNEXUS clean pipeline" { & $Python run_pipeline.py --clean }

Invoke-NativeChecked "Phase 5 tests" {
    & $Python -m pytest -q tests\test_predictive_maintenance.py tests\test_data_governance.py tests\test_master_spec_traceability.py tests\test_reproducibility.py
}

$required = @(
    "artifacts\validation\predictive_maintenance_metrics.json",
    "artifacts\validation\predictive_maintenance_model_comparison.csv",
    "artifacts\validation\predictive_maintenance_threshold_analysis.csv",
    "artifacts\validation\predictive_maintenance_calibration.csv",
    "artifacts\validation\predictive_maintenance_feature_importance.csv",
    "data\curated\predictive_maintenance_scores.csv",
    "powerbi\exports\PredictiveMaintenanceScores.csv",
    "powerbi\exports\PredictiveMaintenanceModelComparison.csv",
    "powerbi\exports\PredictiveMaintenanceCalibration.csv",
    "powerbi\exports\PredictiveMaintenanceFeatureImportance.csv"
)

$missing = @()
foreach ($file in $required) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}
if ($missing.Count -gt 0) {
    throw "Phase 5 artifact contract failed. Missing: $($missing -join ', ')"
}

$metrics = Get-Content "artifacts\validation\predictive_maintenance_metrics.json" -Raw | ConvertFrom-Json
$comparison = Import-Csv "artifacts\validation\predictive_maintenance_model_comparison.csv"
$thresholds = Import-Csv "artifacts\validation\predictive_maintenance_threshold_analysis.csv"
$calibration = Import-Csv "artifacts\validation\predictive_maintenance_calibration.csv"
$importance = Import-Csv "artifacts\validation\predictive_maintenance_feature_importance.csv"

$models = @($comparison.model | Sort-Object -Unique)
if ($models.Count -ne 2 -or -not ($models -contains "LogisticRegression") -or -not ($models -contains "RandomForest")) {
    throw "Model comparison contract failed. Expected LogisticRegression and RandomForest."
}

if ([datetime]$metrics.train_end -ge [datetime]$metrics.validation_start) {
    throw "Temporal leakage gate failed between train and validation."
}
if ([datetime]$metrics.validation_end -ge [datetime]$metrics.test_start) {
    throw "Temporal leakage gate failed between validation and test."
}

$selectedRows = @($thresholds | Where-Object { $_.model -eq $metrics.model })
if ($selectedRows.Count -eq 0) {
    throw "Threshold analysis does not contain the selected model."
}

$minimumCost = ($selectedRows | ForEach-Object { [double]$_.weighted_error_cost } | Measure-Object -Minimum).Minimum
$chosen = @(
    $selectedRows | Where-Object {
        [math]::Abs([double]$_.threshold - [double]$metrics.threshold) -lt 0.0000001
    }
)
if ($chosen.Count -eq 0) {
    throw "Selected threshold is missing from the validation threshold table."
}
if ([double]$chosen[0].recall -lt [double]$metrics.minimum_validation_recall) {
    throw "Selected threshold violates the minimum validation recall floor."
}
$feasibleCosts = @(
    $selectedRows |
    Where-Object { [double]$_.recall -ge [double]$metrics.minimum_validation_recall } |
    ForEach-Object { [double]$_.weighted_error_cost }
)
if ($feasibleCosts.Count -eq 0) {
    throw "No threshold satisfies the minimum validation recall floor."
}
$minimumFeasibleCost = ($feasibleCosts | Measure-Object -Minimum).Minimum
if ([math]::Abs([double]$chosen[0].weighted_error_cost - [double]$minimumFeasibleCost) -gt 0.0000001) {
    throw "Selected threshold does not minimize cost among recall-feasible thresholds."
}

if ($calibration.Count -eq 0) {
    throw "Calibration evidence is empty."
}
if ($importance.Count -ne 4) {
    throw "Permutation-importance contract failed. Expected exactly four canonical features."
}

$trust = Get-Content "artifacts\validation\data_trust.json" -Raw | ConvertFrom-Json
if ([double]$trust.data_trust_score -ne 100.0) {
    throw "Data Trust regression detected: $($trust.data_trust_score)"
}

Write-Host "TEMPORAL_SPLIT_GATE=PASS"
Write-Host "MODEL_COMPARISON=PASS"
Write-Host "THRESHOLD_COST_ANALYSIS=PASS"
Write-Host "CALIBRATION_ASSESSMENT=PASS"
Write-Host "CALIBRATION_STATUS=$($metrics.calibration_status)"
Write-Host "SCORE_SEMANTICS=$($metrics.score_semantics)"
Write-Host "MIN_VALIDATION_RECALL=$($metrics.minimum_validation_recall)"
Write-Host "PERMUTATION_IMPORTANCE=PASS"
Write-Host "SELECTED_MODEL=$($metrics.model)"
Write-Host "SELECTED_THRESHOLD=$($metrics.threshold)"
Write-Host "HOLDOUT_PR_AUC=$($metrics.pr_auc)"
Write-Host "HOLDOUT_RECALL=$($metrics.recall)"
Write-Host "HOLDOUT_BRIER_SCORE=$($metrics.brier_score)"
Write-Host "DATA_TRUST_SCORE=$($trust.data_trust_score)"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is unavailable. Phase 5 validation passed, but evidence was not committed."
    exit 0
}

Invoke-NativeChecked "git add" { git add . }
$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE."
}
if ($changes) {
    Invoke-NativeChecked "git commit" { git commit -m "Validate MEDNEXUS predictive maintenance model selection" }
    Invoke-NativeChecked "git push" { git push origin main }
}

Write-Host "=== MEDNEXUS PHASE 5 PREDICTIVE MAINTENANCE PASSED AND PUSHED ==="
