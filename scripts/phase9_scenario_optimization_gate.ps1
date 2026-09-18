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

Write-Host "=== MEDNEXUS PHASE 9 SCENARIO + OPTIMIZATION GATE ==="

if (-not (Test-Path "mednexus\scenarios.py")) {
    throw "Run this script from the MEDNEXUS repository root after pulling Phase 9."
}

$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Complete the MEDNEXUS bootstrap first."
}

Invoke-NativeChecked "MEDNEXUS clean pipeline" { & $Python run_pipeline.py --clean }

Invoke-NativeChecked "Phase 9 tests" {
    & $Python -m pytest -q tests\test_scenarios.py tests\test_master_spec_traceability.py
}

$required = @(
    "artifacts\validation\scenario_methodology.json",
    "artifacts\validation\optimization_gate.json",
    "data\curated\scenario_outputs.csv",
    "data\curated\scenario_assumptions.csv",
    "data\curated\scenario_monitoring_plan.csv",
    "powerbi\exports\ScenarioOutputs.csv",
    "powerbi\exports\ScenarioAssumptions.csv",
    "powerbi\exports\ScenarioMonitoringPlan.csv"
)

$missing = @()
foreach ($file in $required) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}
if ($missing.Count -gt 0) {
    throw "Phase 9 artifact contract failed. Missing: $($missing -join ', ')"
}

$methodology = Get-Content "artifacts\validation\scenario_methodology.json" -Raw | ConvertFrom-Json
$gate = Get-Content "artifacts\validation\optimization_gate.json" -Raw | ConvertFrom-Json
$scenarios = Import-Csv "data\curated\scenario_outputs.csv"
$monitoring = Import-Csv "data\curated\scenario_monitoring_plan.csv"

if ($methodology.scenario_status -ne "SIMULATED") {
    throw "Scenario methodology labeling gate failed."
}
if ($methodology.causal_claim -ne $false) {
    throw "Scenario methodology incorrectly claims causation."
}
if ($gate.solver_executed -ne $false) {
    throw "Optimization solver executed despite an unmet admission gate."
}
if ($gate.optimization_status -ne "NOT_ADMITTED_INSUFFICIENT_DECISION_MODEL_EVIDENCE") {
    throw "Unexpected optimization-gate status."
}
if ($gate.recommendation_type -ne "SCENARIO_PRIORITIZATION_ONLY") {
    throw "Optimization recommendation type is invalid."
}

$baseline = @($scenarios | Where-Object { $_.scenario -eq "Baseline" })
if ($baseline.Count -ne 1) {
    throw "Expected exactly one Baseline scenario."
}
if ([math]::Abs([double]$baseline[0].difference_good_units) -gt 0.0000001) {
    throw "Baseline scenario does not reconcile to zero difference."
}
if ([math]::Abs([double]$baseline[0].simulated_opportunity_value) -gt 0.0000001) {
    throw "Baseline simulated opportunity value is not zero."
}

$rankOne = @($scenarios | Where-Object { [int]$_.decision_priority_rank -eq 1 })
if ($rankOne.Count -ne 1) {
    throw "Expected exactly one rank-1 intervention scenario."
}

$invalidMonitoring = @($monitoring | Where-Object { $_.status -ne "MONITORING_PLAN_ONLY_NOT_EXECUTED" })
if ($invalidMonitoring.Count -gt 0) {
    throw "Scenario monitoring plan contains executed/observed status that is not supported."
}

$trust = Get-Content "artifacts\validation\data_trust.json" -Raw | ConvertFrom-Json
if ([double]$trust.data_trust_score -ne 100.0) {
    throw "Data Trust regression detected: $($trust.data_trust_score)"
}

Write-Host "SCENARIO_BASELINE_RECONCILIATION=PASS"
Write-Host "SCENARIO_ASSUMPTION_CONTRACT=PASS"
Write-Host "SCENARIO_RESULT_DIFFERENCES=PASS"
Write-Host "SIMULATED_VALUE_RECONCILIATION=PASS"
Write-Host "SCENARIO_PRIORITY_HEURISTIC=PASS"
Write-Host "SCENARIO_MONITORING_PLAN=PASS"
Write-Host "OPTIMIZATION_ADMISSION_GATE=PASS"
Write-Host "OPTIMIZATION_SOLVER_EXECUTED=$($gate.solver_executed)"
Write-Host "OPTIMIZATION_STATUS=$($gate.optimization_status)"
Write-Host "TOP_SCENARIO=$($rankOne[0].scenario)"
Write-Host "TOP_SCENARIO_SIMULATED_OPPORTUNITY=$($rankOne[0].simulated_opportunity_value)"
Write-Host "DATA_TRUST_SCORE=$($trust.data_trust_score)"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is unavailable. Phase 9 validation passed, but evidence was not committed."
    exit 0
}

Invoke-NativeChecked "git add" { git add . }
$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE."
}
if ($changes) {
    Invoke-NativeChecked "git commit" { git commit -m "Validate MEDNEXUS scenario engine and optimization gate" }
    Invoke-NativeChecked "git push" { git push origin main }
}

Write-Host "=== MEDNEXUS PHASE 9 SCENARIO + OPTIMIZATION GATE PASSED AND PUSHED ==="
