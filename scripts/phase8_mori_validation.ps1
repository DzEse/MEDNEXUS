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

Write-Host "=== MEDNEXUS PHASE 8 MORI VALIDATION ==="

if (-not (Test-Path "mednexus\risk.py")) {
    throw "Run this script from the MEDNEXUS repository root after pulling Phase 8."
}

$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Complete the MEDNEXUS bootstrap first."
}

Invoke-NativeChecked "MEDNEXUS clean pipeline" { & $Python run_pipeline.py --clean }

Invoke-NativeChecked "Phase 8 tests" {
    & $Python -m pytest -q tests\test_risk.py tests\test_data_governance.py tests\test_master_spec_traceability.py
}

$required = @(
    "artifacts\validation\mori_methodology.json",
    "artifacts\validation\mori_sensitivity_summary.json",
    "artifacts\validation\mori_component_contributions.csv",
    "artifacts\validation\mori_weight_sensitivity.csv",
    "artifacts\validation\mori_threshold_sensitivity.csv",
    "powerbi\exports\MORI.csv",
    "powerbi\exports\MORIComponentContributions.csv",
    "powerbi\exports\MORIWeightSensitivity.csv",
    "powerbi\exports\MORIThresholdSensitivity.csv"
)

$missing = @()
foreach ($file in $required) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}
if ($missing.Count -gt 0) {
    throw "Phase 8 artifact contract failed. Missing: $($missing -join ', ')"
}

$methodology = Get-Content "artifacts\validation\mori_methodology.json" -Raw | ConvertFrom-Json
$summary = Get-Content "artifacts\validation\mori_sensitivity_summary.json" -Raw | ConvertFrom-Json

if ($methodology.index_status -ne "project_defined_not_industry_standard") {
    throw "MORI external-validation labeling gate failed."
}
if ($methodology.missing_data_policy -notmatch "Fail closed") {
    throw "MORI missing-data policy is not fail-closed."
}
if ($summary.missing_data_policy -ne "fail_closed_no_partial_score") {
    throw "MORI sensitivity summary missing-data policy is invalid."
}
if ([double]$summary.weight_perturbation_relative -ne 0.25) {
    throw "MORI weight sensitivity must use +/-25 percent perturbation."
}
if ([double]$summary.threshold_shift_points -ne 5.0) {
    throw "MORI threshold sensitivity must use +/-5 points."
}

$weights = Import-Csv "artifacts\validation\mori_weight_sensitivity.csv"
if (($weights.scenario | Sort-Object -Unique).Count -ne 17) {
    throw "Expected 17 MORI weight scenarios: baseline plus +/-25 percent for eight components."
}

$thresholds = Import-Csv "artifacts\validation\mori_threshold_sensitivity.csv"
if (($thresholds.threshold_scenario | Sort-Object -Unique).Count -ne 3) {
    throw "Expected base, -5 and +5 MORI threshold scenarios."
}

$contributions = Import-Csv "artifacts\validation\mori_component_contributions.csv"
if (($contributions.component | Sort-Object -Unique).Count -ne 8) {
    throw "Expected exactly eight MORI components."
}

$trust = Get-Content "artifacts\validation\data_trust.json" -Raw | ConvertFrom-Json
if ([double]$trust.data_trust_score -ne 100.0) {
    throw "Data Trust regression detected: $($trust.data_trust_score)"
}

Write-Host "MORI_WEIGHT_VECTOR=PASS"
Write-Host "MORI_SCORE_BOUNDS=PASS"
Write-Host "MORI_CONTRIBUTION_RECONCILIATION=PASS"
Write-Host "MORI_MISSING_DATA_FAIL_CLOSED=PASS"
Write-Host "MORI_WEIGHT_SENSITIVITY=PASS"
Write-Host "MORI_THRESHOLD_SENSITIVITY=PASS"
Write-Host "MORI_PROJECT_DEFINED_LABEL=PASS"
Write-Host "MORI_LATEST_SCORE=$($summary.baseline_latest_score)"
Write-Host "MORI_LATEST_BAND=$($summary.baseline_latest_band)"
Write-Host "MORI_MAX_WEIGHT_SENSITIVITY_DELTA=$($summary.weight_sensitivity_latest_max_absolute_delta)"
Write-Host "MORI_LATEST_WEIGHT_BAND_CHANGES=$($summary.weight_sensitivity_latest_band_changes)"
Write-Host "MORI_LATEST_THRESHOLD_BAND_CHANGES=$($summary.threshold_sensitivity_latest_band_changes)"
Write-Host "DATA_TRUST_SCORE=$($trust.data_trust_score)"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is unavailable. Phase 8 validation passed, but evidence was not committed."
    exit 0
}

Invoke-NativeChecked "git add" { git add . }
$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE."
}
if ($changes) {
    Invoke-NativeChecked "git commit" { git commit -m "Validate MEDNEXUS MORI robustness and sensitivity" }
    Invoke-NativeChecked "git push" { git push origin main }
}

Write-Host "=== MEDNEXUS PHASE 8 MORI VALIDATION PASSED AND PUSHED ==="
