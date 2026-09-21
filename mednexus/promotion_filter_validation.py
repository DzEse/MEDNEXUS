from __future__ import annotations

from collections import defaultdict
import os
import platform
import sys
import time

import pandas as pd

from .config import path
from .enhanced_twin_prototype import TABLE_CONTRACTS, build_prototype
from .semantic_model import (
    CONNECTED_TABLES,
    DISCONNECTED_TABLES,
    EXPECTED_EXPORTS,
    build_relationship_contract as build_baseline_relationship_contract,
    build_table_role_contract as build_baseline_table_role_contract,
)
from .synthetic import generate
from .utils import save_frame, write_json


PHASE = "12F"
STATUS = "PROMOTION_REVIEW_AND_FILTER_BEHAVIOR_VALIDATION"
CANONICAL_CONTRACT_MUTATED = False

# Phase 12F makes an explicit decision for every Phase 12E prototype table.
# APPROVED means approved for the next physical canonical-implementation phase;
# it does NOT mean the current 53-export contract has already changed.
PROMOTION_DECISIONS = {
    "dim_region": {
        "decision": "DEFERRED",
        "action": "DO_NOT_CONNECT_AS_GLOBAL_DIMENSION",
        "reason": "A single active Region dimension across plant, supplier and customer geography would conflate different business roles and could create misleading cross-domain filtering.",
    },
    "dim_plant_geo": {
        "decision": "APPROVED_FOR_CANONICAL_IMPLEMENTATION",
        "action": "MERGE_ATTRIBUTES_INTO_DIMPLANT",
        "reason": "Plant geography is one-to-one with the existing plant key and enables map/drill behavior without adding a parallel plant relationship path.",
    },
    "dim_supplier_geo": {
        "decision": "APPROVED_FOR_CANONICAL_IMPLEMENTATION",
        "action": "MERGE_ATTRIBUTES_INTO_DIMSUPPLIER",
        "reason": "Supplier geography is one-to-one with the existing supplier key; retain supplier-region semantics on the supplier dimension rather than a shared global Region relationship.",
    },
    "dim_customer_geo": {
        "decision": "APPROVED_FOR_CANONICAL_IMPLEMENTATION",
        "action": "MERGE_ATTRIBUTES_INTO_DIMCUSTOMER",
        "reason": "Customer geography is one-to-one with the existing customer key and preserves customer-location semantics without patient-identifiable information.",
    },
    "dim_warehouse": {
        "decision": "APPROVED_FOR_CANONICAL_IMPLEMENTATION",
        "action": "ADD_DIMWAREHOUSE",
        "reason": "Warehouse is a stable plant-child reference useful for enterprise-map and future inventory drill paths; Plant→Warehouse is unambiguous and one-directional.",
    },
    "dim_material": {
        "decision": "DEFERRED",
        "action": "WAIT_FOR_CANONICAL_INVENTORY_SOURCE_GRAIN",
        "reason": "Material becomes decision-useful when purchase, receipt, consumption and inventory facts are generated directly rather than from prototype reverse-disaggregation.",
    },
    "bridge_product_material": {
        "decision": "DEFERRED",
        "action": "WAIT_FOR_DEFENSIBLE_MATERIAL_FLOW_MODEL",
        "reason": "Do not introduce a product-material bridge until material flows are canonical; premature bridge activation would add model complexity and many-to-many risk.",
    },
    "dim_shift": {
        "decision": "APPROVED_FOR_CANONICAL_IMPLEMENTATION",
        "action": "ADD_DIMSHIFT",
        "reason": "Shift is a compact conformed reference and safely filters the approved current employee-assignment snapshot without changing machine-fact paths.",
    },
    "dim_department": {
        "decision": "APPROVED_FOR_CANONICAL_IMPLEMENTATION",
        "action": "ADD_DIMDEPARTMENT",
        "reason": "Department is a stable workforce hierarchy parent and can filter employee assignment through Job Role with one active path.",
    },
    "dim_job_role": {
        "decision": "APPROVED_FOR_CANONICAL_IMPLEMENTATION",
        "action": "ADD_DIMJOBROLE",
        "reason": "Job Role provides decision-useful workforce segmentation and a safe Department→JobRole→EmployeeAssignment hierarchy.",
    },
    "fact_employee_assignment": {
        "decision": "APPROVED_FOR_CANONICAL_IMPLEMENTATION",
        "action": "ADD_EMPLOYEEASSIGNMENT_SNAPSHOT",
        "reason": "Current one-row-per-employee assignment is deterministic, key-complete and supports Plant/Shift/Department/Role workforce drill without inventing historical employment events.",
    },
    "fact_vacancy": {
        "decision": "REWORK_REQUIRED",
        "action": "GENERATE_DIRECTLY_NOT_FROM_MONTHLY_DISAGGREGATION",
        "reason": "Vacancies are currently deterministic disaggregation of monthly recruitment aggregates; canonical event facts should become source generation, with monthly recruitment derived upward.",
    },
    "fact_candidate_event": {
        "decision": "REWORK_REQUIRED",
        "action": "GENERATE_DIRECTLY_FROM_CANDIDATE_LIFECYCLE",
        "reason": "Candidate events pass chronology checks but are derived from prototype vacancy disaggregation; direct candidate lifecycle generation is required before promotion.",
    },
    "fact_production_event": {
        "decision": "REWORK_REQUIRED",
        "action": "GENERATE_TRUE_SHIFT_EVENTS_THEN_AGGREGATE_DAILY",
        "reason": "The prototype intentionally splits canonical daily production 50/50 to test grain mechanics; that is not sufficient evidence for decision-useful shift variation.",
    },
    "fact_inspection_event": {
        "decision": "REWORK_REQUIRED",
        "action": "GENERATE_INDEPENDENT_INSPECTION_EVENTS",
        "reason": "One inspection per split production event validates linkage but does not yet represent independent inspection sampling/process-stage behavior.",
    },
    "fact_purchase_order": {
        "decision": "REWORK_REQUIRED",
        "action": "GENERATE_PURCHASE_ORDER_LINES_DIRECTLY",
        "reason": "PO lines reconcile to supply totals but are reverse-disaggregated from monthly supplier facts; direct PO generation must become authoritative before promotion.",
    },
    "fact_receipt": {
        "decision": "REWORK_REQUIRED",
        "action": "GENERATE_RECEIPTS_AND_LOTS_FROM_DIRECT_PO_LINES",
        "reason": "Receipt/lot structure is sound, but canonical receipts must flow from directly generated purchase orders.",
    },
    "fact_inventory_movement": {
        "decision": "REWORK_REQUIRED",
        "action": "GENERATE_PHYSICAL_LEDGER_FROM_DIRECT_RECEIPTS_AND_CONSUMPTION",
        "reason": "Ledger equations pass, but prototype consumption uses an explicitly scaled production-demand proxy; canonical inventory requires direct, documented movement generation.",
    },
    "fact_inventory_snapshot": {
        "decision": "REWORK_REQUIRED",
        "action": "DERIVE_SNAPSHOTS_FROM_CANONICAL_MOVEMENT_LEDGER",
        "reason": "Snapshots reconcile mathematically, but must be downstream derivations of a canonical direct-movement ledger rather than prototype assumptions.",
    },
    "fact_order_fulfillment_event": {
        "decision": "NOT_PROMOTED_REDUNDANT",
        "action": "KEEP_EXISTING_PROCESS_EVENT_LOG",
        "reason": "The repository already has a source-backed order-fulfillment process event log; duplicating the same case process would add no decision value.",
    },
}


APPROVED_NEW_EXPORTS = {
    "DimWarehouse": "dimension",
    "DimShift": "dimension",
    "DimDepartment": "dimension",
    "DimJobRole": "dimension",
    "EmployeeAssignment": "workforce_snapshot_fact",
}

MERGE_ENRICHMENTS = {
    "dim_plant_geo": "DimPlant",
    "dim_supplier_geo": "DimSupplier",
    "dim_customer_geo": "DimCustomer",
}


def _rel(one_table: str, one_column: str, many_table: str, many_column: str, rationale: str) -> dict:
    return {
        "one_table": one_table,
        "one_column": one_column,
        "many_table": many_table,
        "many_column": many_column,
        "cardinality": "1:*",
        "cross_filter_direction": "single",
        "active": True,
        "relationship_class": "phase12f_approved_candidate",
        "rationale": rationale,
    }


APPROVED_RELATIONSHIP_ADDITIONS = [
    _rel(
        "DimPlant",
        "plant_id",
        "DimWarehouse",
        "plant_id",
        "Plant filters warehouses for map and future inventory drill; Warehouse does not back-filter Plant.",
    ),
    _rel(
        "DimPlant",
        "plant_id",
        "EmployeeAssignment",
        "plant_id",
        "Current workforce assignment uses Plant directly; no active Line relationship is added, preventing a second Plant→Line→Assignment path.",
    ),
    _rel(
        "DimShift",
        "shift_id",
        "EmployeeAssignment",
        "shift_id",
        "Shift filters the current workforce assignment snapshot only; it does not falsely filter canonical production until true shift production is generated.",
    ),
    _rel(
        "DimEmployee",
        "employee_id",
        "EmployeeAssignment",
        "employee_id",
        "Connecting the previously disconnected employee dimension is justified by the one-current-assignment-per-employee grain.",
    ),
    _rel(
        "DimDepartment",
        "department_id",
        "DimJobRole",
        "department_id",
        "Department filters Job Role as the only workforce hierarchy route into EmployeeAssignment.",
    ),
    _rel(
        "DimJobRole",
        "job_role_id",
        "EmployeeAssignment",
        "job_role_id",
        "Job Role filters employee assignment; no parallel direct Department→EmployeeAssignment relationship is admitted.",
    ),
]


def build_promotion_decisions() -> pd.DataFrame:
    rows = []
    for table in TABLE_CONTRACTS:
        decision = PROMOTION_DECISIONS[table]
        rows.append(
            {
                "prototype_table": table,
                "prototype_grain": TABLE_CONTRACTS[table]["grain"],
                "decision": decision["decision"],
                "canonical_action": decision["action"],
                "reason": decision["reason"],
                "phase12f_status": "REVIEWED",
            }
        )
    return pd.DataFrame(rows)


def build_proposed_table_roles() -> pd.DataFrame:
    baseline = build_baseline_table_role_contract().copy()
    # DimEmployee becomes connected only in the proposed Phase 12F target because
    # EmployeeAssignment gives it a defensible fact-grain relationship.
    employee_mask = baseline["table"].eq("DimEmployee")
    baseline.loc[employee_mask, "model_status"] = "CONNECTED"
    baseline.loc[employee_mask, "role"] = "dimension"
    baseline.loc[employee_mask, "filtering_rule"] = (
        "Proposed Phase 12F target: filters EmployeeAssignment only; not yet canonical."
    )
    rows = baseline.to_dict("records")
    for table, role in APPROVED_NEW_EXPORTS.items():
        rows.append(
            {
                "table": table,
                "model_status": "CONNECTED",
                "role": role,
                "filtering_rule": "Phase 12F approved candidate; becomes canonical only in the next implementation phase.",
            }
        )
    return pd.DataFrame(rows).sort_values("table").reset_index(drop=True)


def build_proposed_relationship_contract() -> pd.DataFrame:
    baseline = build_baseline_relationship_contract().copy()
    additions = pd.DataFrame(APPROVED_RELATIONSHIP_ADDITIONS)
    return pd.concat([baseline, additions], ignore_index=True)


def _active_adjacency(relationships: pd.DataFrame) -> dict[str, list[str]]:
    adjacency: dict[str, list[str]] = defaultdict(list)
    for row in relationships.loc[relationships["active"]].itertuples(index=False):
        adjacency[row.one_table].append(row.many_table)
    return adjacency


def _count_paths(adjacency: dict[str, list[str]], source: str, target: str, visited=None) -> int:
    if source == target:
        return 1
    visited = set() if visited is None else set(visited)
    if source in visited:
        return 0
    visited.add(source)
    total = 0
    for nxt in adjacency.get(source, []):
        total += _count_paths(adjacency, nxt, target, visited)
        if total > 1:
            return total
    return total


def _build_proposed_data(
    canonical_frames: dict[str, pd.DataFrame],
    prototype: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    plant_geo = prototype["dim_plant_geo"][
        ["plant_id", "country", "region", "city", "latitude", "longitude", "geography_status"]
    ].rename(columns={"region": "geography_region"})
    supplier_geo = prototype["dim_supplier_geo"][
        ["supplier_id", "country", "region", "city", "latitude", "longitude", "geography_status"]
    ].rename(columns={"region": "geography_region"})
    customer_geo = prototype["dim_customer_geo"][
        ["customer_id", "country", "region", "city", "latitude", "longitude", "geography_status"]
    ].rename(columns={"region": "geography_region"})

    return {
        "DimPlant": canonical_frames["dim_plant"].merge(plant_geo, on="plant_id", how="left", validate="one_to_one"),
        "DimSupplier": canonical_frames["dim_supplier"].merge(supplier_geo, on="supplier_id", how="left", validate="one_to_one"),
        "DimCustomer": canonical_frames["dim_customer"].merge(customer_geo, on="customer_id", how="left", validate="one_to_one"),
        "DimEmployee": canonical_frames["dim_employee"].copy(),
        "DimWarehouse": prototype["dim_warehouse"].copy(),
        "DimShift": prototype["dim_shift"].copy(),
        "DimDepartment": prototype["dim_department"].copy(),
        "DimJobRole": prototype["dim_job_role"].copy(),
        "EmployeeAssignment": prototype["fact_employee_assignment"].copy(),
    }


def validate_filter_behavior(
    canonical_frames: dict[str, pd.DataFrame],
    prototype: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    proposed = _build_proposed_data(canonical_frames, prototype)
    relationships = build_proposed_relationship_contract()
    rows: list[dict] = []

    def add(check: str, passed: bool, category: str, detail: str = "") -> None:
        rows.append(
            {
                "check": check,
                "category": category,
                "passed": bool(passed),
                "status": "PASS" if passed else "FAIL",
                "detail": detail,
            }
        )

    add(
        "baseline_export_contract_preserved_during_phase12f",
        len(EXPECTED_EXPORTS) == 53
        and not set(APPROVED_NEW_EXPORTS).intersection(EXPECTED_EXPORTS),
        "scope_preservation",
        "Phase 12F validates a proposed target; it does not mutate the current 53-export contract.",
    )
    add(
        "all_relationships_one_to_many",
        relationships["cardinality"].eq("1:*").all(),
        "semantic_model",
    )
    add(
        "all_relationships_single_direction",
        relationships["cross_filter_direction"].eq("single").all(),
        "semantic_model",
    )

    # No relationship may connect one fact-like table directly to another.
    roles = build_proposed_table_roles().set_index("table")["role"].to_dict()
    fact_like = {
        table
        for table, role in roles.items()
        if role in {
            "fact",
            "workforce_snapshot_fact",
            "enterprise_mart",
            "risk_mart",
            "statistical_mart",
            "analytical_mart",
            "model_output",
            "forecast_output",
        }
    }
    active = relationships[relationships["active"]]
    fact_to_fact = active[
        active["one_table"].isin(fact_like) & active["many_table"].isin(fact_like)
    ]
    add("no_fact_to_fact_relationships", fact_to_fact.empty, "semantic_model")

    adjacency = _active_adjacency(relationships)
    proposed_dimensions = sorted(
        table for table, role in roles.items() if role == "dimension"
    )
    targets = sorted(set(active["many_table"]))
    ambiguous = []
    for source in proposed_dimensions:
        for target in targets:
            if source == target:
                continue
            paths = _count_paths(adjacency, source, target)
            if paths > 1:
                ambiguous.append(f"{source}->{target}:{paths}")
    add(
        "no_ambiguous_active_filter_paths",
        not ambiguous,
        "filter_behavior",
        "|".join(ambiguous),
    )

    # Explicit guards around decisions that could otherwise create ambiguity or
    # misleading cross-domain behavior.
    add(
        "no_global_dimregion_relationship",
        "DimRegion" not in set(relationships["one_table"]).union(relationships["many_table"]),
        "filter_behavior",
        "Plant, Supplier and Customer geography remain role-specific attributes.",
    )
    add(
        "no_direct_dimline_employeeassignment_relationship",
        not (
            relationships["one_table"].eq("DimLine")
            & relationships["many_table"].eq("EmployeeAssignment")
            & relationships["active"]
        ).any(),
        "filter_behavior",
        "Nullable line assignment remains informational until a complete workforce-line grain is justified.",
    )
    add(
        "department_filters_assignment_via_jobrole_only",
        _count_paths(adjacency, "DimDepartment", "EmployeeAssignment") == 1,
        "filter_behavior",
        "DimDepartment→DimJobRole→EmployeeAssignment",
    )

    # Proposed one-side keys and relationship orphan checks.
    key_data = {
        "DimPlant": proposed["DimPlant"],
        "DimWarehouse": proposed["DimWarehouse"],
        "DimShift": proposed["DimShift"],
        "DimEmployee": proposed["DimEmployee"],
        "DimDepartment": proposed["DimDepartment"],
        "DimJobRole": proposed["DimJobRole"],
        "EmployeeAssignment": proposed["EmployeeAssignment"],
    }
    for rel in APPROVED_RELATIONSHIP_ADDITIONS:
        one = key_data[rel["one_table"]]
        many = key_data[rel["many_table"]]
        one_key = one[rel["one_column"]]
        many_key = many[rel["many_column"]].dropna()
        if many_key.dtype == object:
            many_key = many_key[many_key.astype(str) != ""]
        add(
            f"one_side_unique_{rel['one_table']}_{rel['one_column']}",
            one_key.notna().all() and not one_key.duplicated().any(),
            "key_integrity",
        )
        add(
            f"no_orphans_{rel['one_table']}_{rel['many_table']}",
            many_key.isin(one_key).all(),
            "referential_integrity",
        )

    # Geo merges must preserve base dimension row counts and provide complete
    # simulated map attributes.
    for name, base_name in (
        ("DimPlant", "dim_plant"),
        ("DimSupplier", "dim_supplier"),
        ("DimCustomer", "dim_customer"),
    ):
        df = proposed[name]
        complete_geo = (
            df["latitude"].between(-90, 90).all()
            and df["longitude"].between(-180, 180).all()
            and df["geography_status"].eq("SIMULATED_ENTERPRISE_FOOTPRINT").all()
        )
        add(
            f"{name.lower()}_geo_merge_preserves_grain",
            len(df) == len(canonical_frames[base_name]) and complete_geo,
            "geospatial",
        )

    assignments = proposed["EmployeeAssignment"]
    plant = proposed["DimPlant"].iloc[0]["plant_id"]
    expected_plant_rows = int(assignments["plant_id"].eq(plant).sum())
    filtered_plant_rows = int(assignments[assignments["plant_id"].isin({plant})].shape[0])
    add(
        "plant_filter_employeeassignment",
        expected_plant_rows == filtered_plant_rows and filtered_plant_rows > 0,
        "filter_behavior",
        f"plant={plant};rows={filtered_plant_rows}",
    )

    shift = proposed["DimShift"].iloc[0]["shift_id"]
    expected_shift_rows = int(assignments["shift_id"].eq(shift).sum())
    filtered_shift_rows = int(assignments[assignments["shift_id"].isin({shift})].shape[0])
    add(
        "shift_filter_employeeassignment",
        expected_shift_rows == filtered_shift_rows and filtered_shift_rows > 0,
        "filter_behavior",
        f"shift={shift};rows={filtered_shift_rows}",
    )

    employee = proposed["DimEmployee"].iloc[0]["employee_id"]
    employee_rows = int(assignments["employee_id"].eq(employee).sum())
    add(
        "employee_filter_one_current_assignment",
        employee_rows == 1,
        "filter_behavior",
        f"employee={employee};rows={employee_rows}",
    )

    department = proposed["DimDepartment"].iloc[0]["department_id"]
    role_ids = set(
        proposed["DimJobRole"].loc[
            proposed["DimJobRole"]["department_id"].eq(department),
            "job_role_id",
        ]
    )
    via_hierarchy = assignments[assignments["job_role_id"].isin(role_ids)]
    direct_reference = assignments[assignments["department_id"].eq(department)]
    add(
        "department_hierarchy_filter_matches_assignment_reference",
        set(via_hierarchy["assignment_id"]) == set(direct_reference["assignment_id"]),
        "filter_behavior",
        f"department={department};rows={len(via_hierarchy)}",
    )

    warehouse_counts = proposed["DimWarehouse"].groupby("plant_id").size()
    add(
        "plant_filter_warehouse_is_nonambiguous",
        warehouse_counts.ge(1).all(),
        "filter_behavior",
        f"warehouses_per_plant={warehouse_counts.to_dict()}",
    )

    # Explicitly confirm that higher-risk structural prototypes are NOT in the
    # proposed Power BI target.
    risky_tables = {
        "fact_vacancy",
        "fact_candidate_event",
        "fact_production_event",
        "fact_inspection_event",
        "fact_purchase_order",
        "fact_receipt",
        "fact_inventory_movement",
        "fact_inventory_snapshot",
        "bridge_product_material",
        "dim_material",
    }
    unready_approved = sorted(
        table
        for table in risky_tables
        if PROMOTION_DECISIONS[table]["decision"] == "APPROVED_FOR_CANONICAL_IMPLEMENTATION"
    )
    add(
        "unready_prototype_facts_not_approved",
        not unready_approved,
        "promotion_gate",
        "Reverse-disaggregated/proxy facts remain outside the approved canonical target."
        + ("" if not unready_approved else " Unexpected approvals: " + "|".join(unready_approved)),
    )

    issues = pd.DataFrame(
        [
            {"issue_type": row["check"], "detail": row["detail"]}
            for row in rows
            if row["status"] != "PASS"
        ],
        columns=["issue_type", "detail"],
    )
    return pd.DataFrame(rows), issues


def build_geo_enrichment_contract() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "prototype_source": source,
                "canonical_target": target,
                "join_key": {
                    "dim_plant_geo": "plant_id",
                    "dim_supplier_geo": "supplier_id",
                    "dim_customer_geo": "customer_id",
                }[source],
                "attributes": "country|geography_region|city|latitude|longitude|geography_status",
                "relationship_change": "NONE_ATTRIBUTE_MERGE_ONLY",
                "label": "SIMULATED_ENTERPRISE_FOOTPRINT",
            }
            for source, target in MERGE_ENRICHMENTS.items()
        ]
    )


def run_phase12f(seed: int | None = None) -> dict:
    start = time.perf_counter()
    canonical_frames = generate(seed=seed)
    prototype = build_prototype(canonical_frames)
    build_seconds = time.perf_counter() - start

    decisions = build_promotion_decisions()
    table_roles = build_proposed_table_roles()
    relationships = build_proposed_relationship_contract()
    filter_checks, issues = validate_filter_behavior(canonical_frames, prototype)
    geo_contract = build_geo_enrichment_contract()

    validation_dir = path("artifacts", "validation")
    validation_dir.mkdir(parents=True, exist_ok=True)

    save_frame(decisions, validation_dir / "phase12f_promotion_decisions.csv")
    save_frame(table_roles, validation_dir / "phase12f_proposed_table_roles.csv")
    save_frame(relationships, validation_dir / "phase12f_proposed_relationships.csv")
    save_frame(filter_checks, validation_dir / "phase12f_filter_behavior_checks.csv")
    save_frame(issues, validation_dir / "phase12f_semantic_issues.csv")
    save_frame(geo_contract, validation_dir / "phase12f_geo_enrichment_contract.csv")

    approved = decisions["decision"].eq("APPROVED_FOR_CANONICAL_IMPLEMENTATION")
    rework = decisions["decision"].eq("REWORK_REQUIRED")
    deferred = decisions["decision"].eq("DEFERRED")
    redundant = decisions["decision"].eq("NOT_PROMOTED_REDUNDANT")

    prototype_memory = int(
        sum(df.memory_usage(index=True, deep=True).sum() for df in prototype.values())
    )
    benchmark = {
        "phase": PHASE,
        "environment": {
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "cpu_count": os.cpu_count(),
        },
        "generation_and_prototype_build_seconds": round(build_seconds, 4),
        "prototype_memory_bytes": prototype_memory,
        "prototype_table_count": len(prototype),
        "prototype_row_count": int(sum(len(df) for df in prototype.values())),
        "note": "Runtime is environment-specific evidence, not a cross-machine performance target.",
    }
    write_json(benchmark, validation_dir / "phase12f_local_benchmark.json")

    summary = {
        "phase": PHASE,
        "status": "PASS" if issues.empty and filter_checks["status"].eq("PASS").all() else "FAIL",
        "input_prototype": "12E.1",
        "promotion_decision_count": int(len(decisions)),
        "approved_structure_count": int(approved.sum()),
        "approved_new_export_count": len(APPROVED_NEW_EXPORTS),
        "approved_geo_merge_count": len(MERGE_ENRICHMENTS),
        "rework_required_count": int(rework.sum()),
        "deferred_count": int(deferred.sum()),
        "redundant_not_promoted_count": int(redundant.sum()),
        "current_canonical_export_count": len(EXPECTED_EXPORTS),
        "proposed_post_promotion_export_count": len(EXPECTED_EXPORTS) + len(APPROVED_NEW_EXPORTS),
        "current_canonical_semantic_model_changed": CANONICAL_CONTRACT_MUTATED,
        "current_canonical_powerbi_export_contract_changed": CANONICAL_CONTRACT_MUTATED,
        "proposed_active_relationship_count": int(relationships["active"].sum()),
        "proposed_inactive_relationship_count": int((~relationships["active"]).sum()),
        "filter_behavior_check_count": int(len(filter_checks)),
        "filter_behavior_failure_count": int((filter_checks["status"] != "PASS").sum()),
        "semantic_issue_count": int(len(issues)),
        "pbix_model_validated": False,
        "powerbi_validation_scope": "CONTRACT_SIMULATION_NOT_ACTUAL_PBIX",
        "promotion_implementation_status": "APPROVED_PLAN_NOT_YET_APPLIED",
        "next_gate": "Physically implement only approved structures, regenerate canonical exports/semantic contract, then reconcile in Power BI Desktop.",
    }
    write_json(summary, validation_dir / "phase12f_summary.json")

    if summary["status"] != "PASS":
        raise RuntimeError("Phase 12F promotion/filter-behavior gate failed. See artifacts/validation/.")
    return summary


if __name__ == "__main__":
    print(run_phase12f())
