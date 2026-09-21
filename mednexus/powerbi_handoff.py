from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import path
from .semantic_model import (
    CONNECTED_TABLES,
    DISCONNECTED_TABLES,
    EXPECTED_EXPORTS,
    build_relationship_contract,
    build_table_role_contract,
)
from .utils import save_frame, write_json


PHASE = "12H"
STATUS = "POWER_BI_DESKTOP_HANDOFF_PREPARED_NOT_PBIX_VALIDATED"


def build_import_plan() -> pd.DataFrame:
    roles = build_table_role_contract().copy()
    role_order = {
        "dimension": 10,
        "enterprise_mart": 20,
        "risk_mart": 21,
        "fact": 30,
        "workforce_snapshot_fact": 31,
        "statistical_mart": 40,
        "analytical_mart": 41,
        "model_output": 42,
        "forecast_output": 43,
        "risk_evidence": 70,
        "simulated_scenario": 71,
        "simulated_scenario_evidence": 72,
        "prospective_monitoring": 73,
        "case_process_evidence": 74,
        "presentation_mart": 75,
        "model_validation": 76,
        "diagnostic_evidence": 77,
        "forecast_validation": 78,
    }
    rows = []
    for row in roles.itertuples(index=False):
        rows.append(
            {
                "import_sequence_group": role_order.get(row.role, 99),
                "table": row.table,
                "file": f"{row.table}.csv",
                "model_status": row.model_status,
                "role": row.role,
                "load_to_model": True,
                "relationship_instruction": (
                    "CREATE_ONLY_CANONICAL_RELATIONSHIPS"
                    if row.model_status == "CONNECTED"
                    else "KEEP_DISCONNECTED"
                ),
                "pbix_validation_status": "NOT_YET_VALIDATED_IN_PBIX",
            }
        )
    return (
        pd.DataFrame(rows)
        .sort_values(["import_sequence_group", "table"])
        .reset_index(drop=True)
    )


def build_relationship_build_order() -> pd.DataFrame:
    rel = build_relationship_contract().copy()

    def _group(row) -> int:
        if row.one_table == "DimPlant" and row.many_table in {"DimLine", "DimWarehouse", "EmployeeAssignment"}:
            return 10
        if row.one_table == "DimLine" and row.many_table == "DimMachine":
            return 11
        if row.one_table in {"DimDepartment", "DimJobRole", "DimShift", "DimEmployee"}:
            return 12
        if row.one_table == "DimDate":
            return 20 if row.active else 90
        if row.one_table in {"DimMachine", "DimProduct", "DimSupplier", "DimCustomer"}:
            return 30
        return 50

    rel.insert(0, "build_group", [_group(row) for row in rel.itertuples(index=False)])
    rel.insert(1, "build_sequence", range(1, len(rel) + 1))
    rel["pbix_creation_status"] = "NOT_YET_CREATED_IN_PBIX"
    rel["pbix_validation_status"] = "NOT_YET_VALIDATED_IN_PBIX"
    return rel.sort_values(
        ["build_group", "active", "one_table", "many_table", "many_column"],
        ascending=[True, False, True, True, True],
    ).reset_index(drop=True).assign(
        build_sequence=lambda df: range(1, len(df) + 1)
    )


def build_reconciliation_checklist(
    targets: pd.DataFrame,
) -> pd.DataFrame:
    checklist = targets.copy()
    checklist["actual_pbix_value"] = ""
    checklist["variance"] = ""
    checklist["within_tolerance"] = ""
    checklist["validation_status"] = "NOT_YET_VALIDATED_IN_PBIX"
    checklist["evidence_reference"] = ""
    return checklist


def build_acceptance_checklist() -> pd.DataFrame:
    checks = [
        ("A01", "Import", "All 58 canonical CSV exports are loaded."),
        ("A02", "Model", "DimDate is marked as the Date table using DimDate[date]."),
        ("A03", "Model", "Exactly 45 active canonical relationships exist."),
        ("A04", "Model", "Exactly 2 inactive shipment date relationships exist."),
        ("A05", "Model", "Every canonical relationship is 1:* and single-direction."),
        ("A06", "Model", "No many-to-many relationship exists."),
        ("A07", "Model", "No bidirectional relationship exists."),
        ("A08", "Model", "No fact-to-fact relationship exists."),
        ("A09", "Model", "No direct active DimPlant→ProductionKPI relationship exists."),
        ("A10", "Model", "No direct active DimLine→ProductionKPI relationship exists."),
        ("A11", "Model", "No direct active DimLine→EmployeeAssignment relationship exists."),
        ("A12", "Model", "No direct active DimDepartment→EmployeeAssignment relationship exists."),
        ("A13", "Model", "No shared active DimRegion relationship exists."),
        ("A14", "Model", "All tables documented as disconnected remain disconnected."),
        ("A15", "Filtering", "Plant filters machine-grain facts only through Plant→Line→Machine."),
        ("A16", "Filtering", "Department filters EmployeeAssignment only through DimJobRole."),
        ("A17", "Filtering", "Date filtering works for each intended connected fact/mart."),
        ("A18", "Filtering", "Slicers do not multiply revenue, production, shipment, or workforce totals."),
        ("A19", "Reconciliation", "All headline measures match generated targets within tolerance."),
        ("A20", "Reconciliation", "Latest MORI Band equals the generated expected text."),
        ("A21", "Disclosure", "Synthetic enterprise data disclosure is visible."),
        ("A22", "Disclosure", "MORI/OLI/Data Trust are labeled project-defined where shown."),
        ("A23", "Disclosure", "Predictive-maintenance output is labeled risk score, not probability."),
        ("A24", "Disclosure", "Scenario outputs are labeled Simulated and not realized savings."),
        ("A25", "Disclosure", "Forecast outputs are labeled Model-derived."),
        ("A26", "Disclosure", "Map surfaces use SIMULATED ENTERPRISE FOOTPRINT labeling."),
        ("A27", "Evidence", "Relationship/model screenshots are captured only after validation."),
        ("A28", "Evidence", "Reconciliation evidence is stored in evidence/powerbi_reconciliation/."),
        ("A29", "Acceptance", "PBIX file name is MEDNEXUS_Enterprise_Operational_Intelligence.pbix."),
        ("A30", "Acceptance", "PBIX acceptance is not claimed until all required checks are PASS."),
    ]
    return pd.DataFrame(
        [
            {
                "check_id": check_id,
                "category": category,
                "requirement": requirement,
                "status": "NOT_YET_VALIDATED_IN_PBIX",
                "evidence_reference": "",
                "notes": "",
            }
            for check_id, category, requirement in checks
        ]
    )


def prepare_handoff() -> dict:
    export_dir = path("powerbi", "exports")
    missing_exports = [
        f"{table}.csv"
        for table in EXPECTED_EXPORTS
        if not (export_dir / f"{table}.csv").exists()
    ]

    target_path = path(
        "artifacts",
        "validation",
        "powerbi_headline_reconciliation_targets.csv",
    )
    if not target_path.exists():
        raise FileNotFoundError(
            "Headline reconciliation targets are missing. Run the canonical pipeline first."
        )

    targets = pd.read_csv(target_path)
    import_plan = build_import_plan()
    relationships = build_relationship_build_order()
    reconciliation = build_reconciliation_checklist(targets)
    acceptance = build_acceptance_checklist()

    handoff_dir = path("powerbi", "handoff")
    handoff_dir.mkdir(parents=True, exist_ok=True)

    save_frame(import_plan, handoff_dir / "import_plan.csv")
    save_frame(relationships, handoff_dir / "relationship_build_order.csv")
    save_frame(reconciliation, handoff_dir / "headline_reconciliation_checklist.csv")
    save_frame(acceptance, handoff_dir / "pbix_acceptance_checklist.csv")

    active_count = int(relationships["active"].sum())
    inactive_count = int((~relationships["active"]).sum())
    disconnected_count = int(
        (import_plan["model_status"] == "DISCONNECTED").sum()
    )

    summary = {
        "phase": PHASE,
        "status": "PASS" if not missing_exports else "FAIL",
        "handoff_status": STATUS,
        "canonical_export_count": len(EXPECTED_EXPORTS),
        "missing_export_count": len(missing_exports),
        "missing_exports": missing_exports,
        "connected_table_count": len(CONNECTED_TABLES),
        "disconnected_table_count": len(DISCONNECTED_TABLES),
        "active_relationship_count": active_count,
        "inactive_relationship_count": inactive_count,
        "headline_reconciliation_target_count": int(len(targets)),
        "pbix_acceptance_check_count": int(len(acceptance)),
        "pbix_built": False,
        "pbix_validated": False,
        "evidence_status": "TEMPLATE_ONLY_NO_PBIX_EVIDENCE_YET",
        "next_gate": (
            "Build the model in Power BI Desktop exactly from the handoff files, "
            "reconcile headline values, then record real PBIX evidence."
        ),
    }
    write_json(summary, handoff_dir / "handoff_summary.json")

    if missing_exports:
        raise RuntimeError(
            f"Phase 12H handoff failed: {len(missing_exports)} canonical export(s) missing."
        )
    if len(EXPECTED_EXPORTS) != 58:
        raise RuntimeError("Phase 12H requires the canonical 58-export Phase 12G contract.")
    if active_count != 45 or inactive_count != 2:
        raise RuntimeError("Phase 12H relationship count differs from the Phase 12G contract.")

    return summary


if __name__ == "__main__":
    print(prepare_handoff())
