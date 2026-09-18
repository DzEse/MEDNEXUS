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

Write-Host "=== MEDNEXUS PHASE 10 PROCESS + EXPERIMENTATION GATES ==="

if (-not (Test-Path "mednexus\process_analytics.py")) {
    throw "Run this script from the MEDNEXUS repository root after pulling Phase 10."
}

$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Complete the MEDNEXUS bootstrap first."
}

Invoke-NativeChecked "MEDNEXUS clean pipeline" { & $Python run_pipeline.py --clean }

Invoke-NativeChecked "Phase 10 tests" {
    & $Python -m pytest -q tests\test_process_analytics.py tests\test_master_spec_traceability.py
}

$required = @(
    "artifacts\validation\process_mining_gate.json",
    "artifacts\validation\experimentation_gate.json",
    "artifacts\validation\process_analytics_methodology.json",
    "data\curated\process_order_fulfillment_event_log.csv",
    "data\curated\process_order_fulfillment_cases.csv",
    "data\curated\process_transition_summary.csv",
    "powerbi\exports\ProcessEventLog.csv",
    "powerbi\exports\ProcessCases.csv",
    "powerbi\exports\ProcessTransitions.csv"
)

$missing = @()
foreach ($file in $required) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}
if ($missing.Count -gt 0) {
    throw "Phase 10 artifact contract failed. Missing: $($missing -join ', ')"
}

$processGate = Get-Content "artifacts\validation\process_mining_gate.json" -Raw | ConvertFrom-Json
$experimentGate = Get-Content "artifacts\validation\experimentation_gate.json" -Raw | ConvertFrom-Json
$methodology = Get-Content "artifacts\validation\process_analytics_methodology.json" -Raw | ConvertFrom-Json

if ($processGate.full_process_mining_status -ne "NOT_ADMITTED_MISSING_END_TO_END_CASE_LINKAGE") {
    throw "Unexpected full process-mining gate status."
}
if ($processGate.partial_process_analytics_status -ne "SUPPORTED_ORDER_FULFILLMENT_ONLY") {
    throw "Order-fulfillment process analytics support gate failed."
}
if ($experimentGate.experimentation_status -ne "NOT_ADMITTED_NO_EXECUTED_INTERVENTION_OR_TREATMENT_ASSIGNMENT") {
    throw "Unexpected experimentation gate status."
}
if ($experimentGate.causal_effect_estimated -ne $false) {
    throw "A causal treatment effect was incorrectly estimated."
}
if ($experimentGate.experiment_executed -ne $false) {
    throw "Experiment execution was incorrectly claimed."
}
if ($methodology.full_process_mining_admitted -ne $false) {
    throw "Methodology incorrectly admits full process mining."
}
if ($methodology.experimentation_admitted -ne $false) {
    throw "Methodology incorrectly admits experimentation."
}

$events = Import-Csv "data\curated\process_order_fulfillment_event_log.csv"
$allowedActivities = @("Order Created", "Shipped", "Delivered", "Service Issue")
$invalidActivities = @($events | Where-Object { $_.activity -notin $allowedActivities })
if ($invalidActivities.Count -gt 0) {
    throw "Process event log contains fabricated/unsupported activities."
}

foreach ($prohibited in @("Production", "Inspection", "Rework", "Release")) {
    if (@($events | Where-Object { $_.activity -eq $prohibited }).Count -gt 0) {
        throw "Fabricated process event detected: $prohibited"
    }
}

$cases = Import-Csv "data\curated\process_order_fulfillment_cases.csv"
$invalidCycles = @(
    $cases | Where-Object {
        [double]$_.order_to_ship_days -lt 0 -or
        [double]$_.ship_to_delivery_days -lt 0 -or
        [double]$_.order_to_delivery_days -lt 0
    }
)
if ($invalidCycles.Count -gt 0) {
    throw "Negative process cycle time detected."
}

$transitions = Import-Csv "data\curated\process_transition_summary.csv"
if ($transitions.Count -ne 2) {
    throw "Expected exactly two supported fulfillment transitions."
}

$trust = Get-Content "artifacts\validation\data_trust.json" -Raw | ConvertFrom-Json
if ([double]$trust.data_trust_score -ne 100.0) {
    throw "Data Trust regression detected: $($trust.data_trust_score)"
}

Write-Host "ORDER_FULFILLMENT_EVENT_LOG=PASS"
Write-Host "PROCESS_EVENT_CHRONOLOGY=PASS"
Write-Host "PROCESS_CYCLE_TIME_RECONCILIATION=PASS"
Write-Host "PROCESS_TRANSITION_BOTTLENECKS=PASS"
Write-Host "FULL_PROCESS_MINING_GATE=PASS"
Write-Host "FABRICATED_EVENT_GUARD=PASS"
Write-Host "EXPERIMENTATION_ADMISSION_GATE=PASS"
Write-Host "CAUSAL_EFFECT_ESTIMATED=$($experimentGate.causal_effect_estimated)"
Write-Host "FULL_PROCESS_MINING_STATUS=$($processGate.full_process_mining_status)"
Write-Host "EXPERIMENTATION_STATUS=$($experimentGate.experimentation_status)"
Write-Host "PROCESS_CASES=$($methodology.case_count)"
Write-Host "PROCESS_EVENTS=$($methodology.event_count)"
Write-Host "DATA_TRUST_SCORE=$($trust.data_trust_score)"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is unavailable. Phase 10 validation passed, but evidence was not committed."
    exit 0
}

Invoke-NativeChecked "git add" { git add . }
$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE."
}
if ($changes) {
    Invoke-NativeChecked "git commit" { git commit -m "Validate MEDNEXUS process and experimentation gates" }
    Invoke-NativeChecked "git push" { git push origin main }
}

Write-Host "=== MEDNEXUS PHASE 10 PROCESS + EXPERIMENTATION GATES PASSED AND PUSHED ==="
