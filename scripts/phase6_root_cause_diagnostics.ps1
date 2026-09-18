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

Write-Host "=== MEDNEXUS PHASE 6 ROOT-CAUSE DIAGNOSTICS ==="

if (-not (Test-Path "mednexus\root_cause.py")) {
    throw "Run this script from the MEDNEXUS repository root after pulling Phase 6."
}

$Python = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw ".venv was not found. Complete the MEDNEXUS bootstrap first."
}

Invoke-NativeChecked "MEDNEXUS clean pipeline" { & $Python run_pipeline.py --clean }

Invoke-NativeChecked "Phase 6 tests" {
    & $Python -m pytest -q tests\test_root_cause.py tests\test_statistical_quality.py tests\test_data_governance.py tests\test_master_spec_traceability.py
}

$required = @(
    "artifacts\validation\root_cause_methodology.json",
    "artifacts\validation\root_cause_tree_rules.txt",
    "data\curated\root_cause_segments.csv",
    "data\curated\root_cause_associations.csv",
    "data\curated\root_cause_group_tests.csv",
    "data\curated\root_cause_regression.csv",
    "data\curated\root_cause_vif.csv",
    "data\curated\root_cause_tree_importance.csv",
    "data\curated\root_cause_investigation_priorities.csv",
    "powerbi\exports\RootCauseSegments.csv",
    "powerbi\exports\RootCauseAssociations.csv",
    "powerbi\exports\RootCauseGroupTests.csv",
    "powerbi\exports\RootCauseRegression.csv",
    "powerbi\exports\RootCauseTreeImportance.csv",
    "powerbi\exports\RootCausePriorities.csv"
)

$missing = @()
foreach ($file in $required) {
    if (-not (Test-Path $file)) {
        $missing += $file
    }
}
if ($missing.Count -gt 0) {
    throw "Phase 6 artifact contract failed. Missing: $($missing -join ', ')"
}

$methodology = Get-Content "artifacts\validation\root_cause_methodology.json" -Raw | ConvertFrom-Json
if ($methodology.causal_claim -ne $false) {
    throw "Root-cause methodology incorrectly claims causation."
}
if ($methodology.regression_diagnostics.converged -ne $true) {
    throw "Root-cause regression did not converge."
}
if ([double]$methodology.regression_diagnostics.max_vif -le 0) {
    throw "Root-cause VIF diagnostic is invalid."
}
if ($methodology.tree_diagnostics.causal_status -ne "NOT_CAUSAL") {
    throw "Diagnostic tree causal-status gate failed."
}

$associations = Import-Csv "data\curated\root_cause_associations.csv"
foreach ($feature in @("unplanned_downtime_min", "capacity_gap_pct")) {
    $row = $associations | Where-Object { $_.feature -eq $feature }
    if ($null -eq $row) {
        throw "Required diagnostic association missing: $feature"
    }
    if ([double]$row.spearman_rho -le 0) {
        throw "Expected positive synthetic association was not recovered for $feature."
    }
    if ([double]$row.p_value_fdr_bh -ge 0.05) {
        throw "Expected synthetic association was not statistically detected for $feature."
    }
}

$priorities = Import-Csv "data\curated\root_cause_investigation_priorities.csv"
$invalidCausal = @(
    $priorities | Where-Object {
        $_.causal_status -notin @("ASSOCIATION_ONLY", "DESCRIPTIVE_ONLY", "EXPLORATORY_ONLY")
    }
)
if ($invalidCausal.Count -gt 0) {
    throw "Root-cause priority output contains an invalid causal-status label."
}

$trust = Get-Content "artifacts\validation\data_trust.json" -Raw | ConvertFrom-Json
if ([double]$trust.data_trust_score -ne 100.0) {
    throw "Data Trust regression detected: $($trust.data_trust_score)"
}

Write-Host "SEGMENT_CONFIDENCE_INTERVALS=PASS"
Write-Host "SPEARMAN_FDR_ASSOCIATIONS=PASS"
Write-Host "GROUP_EFFECT_TESTS=PASS"
Write-Host "BINOMIAL_REGRESSION=PASS"
Write-Host "MULTICOLLINEARITY_DIAGNOSTIC=PASS"
Write-Host "DIAGNOSTIC_TREE=PASS"
Write-Host "NON_CAUSAL_INTERPRETATION_GATE=PASS"
Write-Host "ROOT_CAUSE_PRIORITIES=$($priorities.Count)"
Write-Host "DATA_TRUST_SCORE=$($trust.data_trust_score)"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warning "Git is unavailable. Phase 6 validation passed, but evidence was not committed."
    exit 0
}

Invoke-NativeChecked "git add" { git add . }
$changes = git status --porcelain
if ($LASTEXITCODE -ne 0) {
    throw "git status failed with exit code $LASTEXITCODE."
}
if ($changes) {
    Invoke-NativeChecked "git commit" { git commit -m "Validate MEDNEXUS root-cause diagnostic intelligence" }
    Invoke-NativeChecked "git push" { git push origin main }
}

Write-Host "=== MEDNEXUS PHASE 6 ROOT-CAUSE DIAGNOSTICS PASSED AND PUSHED ==="
