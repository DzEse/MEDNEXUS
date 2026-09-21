import pandas as pd

from mednexus.powerbi_handoff import (
    build_acceptance_checklist,
    build_import_plan,
    build_relationship_build_order,
    build_reconciliation_checklist,
)
from mednexus.semantic_model import (
    CONNECTED_TABLES,
    DISCONNECTED_TABLES,
    EXPECTED_EXPORTS,
)


def test_import_plan_covers_exactly_58_canonical_exports():
    plan = build_import_plan()
    assert len(plan) == 58
    assert set(plan["table"]) == set(EXPECTED_EXPORTS)
    assert plan["pbix_validation_status"].eq("NOT_YET_VALIDATED_IN_PBIX").all()


def test_connected_and_disconnected_counts_are_preserved():
    plan = build_import_plan()
    assert (plan["model_status"] == "CONNECTED").sum() == len(CONNECTED_TABLES)
    assert (plan["model_status"] == "DISCONNECTED").sum() == len(DISCONNECTED_TABLES)
    disconnected = plan[plan["model_status"] == "DISCONNECTED"]
    assert disconnected["relationship_instruction"].eq("KEEP_DISCONNECTED").all()


def test_relationship_build_order_matches_phase12g_contract():
    rel = build_relationship_build_order()
    assert len(rel) == 47
    assert int(rel["active"].sum()) == 45
    assert int((~rel["active"]).sum()) == 2
    assert rel["cardinality"].eq("1:*").all()
    assert rel["cross_filter_direction"].eq("single").all()
    assert rel["pbix_creation_status"].eq("NOT_YET_CREATED_IN_PBIX").all()
    assert rel["pbix_validation_status"].eq("NOT_YET_VALIDATED_IN_PBIX").all()


def test_relationship_build_order_preserves_semantic_exclusions():
    rel = build_relationship_build_order()
    active = rel[rel["active"]]
    observed = set(zip(active["one_table"], active["many_table"]))
    assert ("DimPlant", "ProductionKPI") not in observed
    assert ("DimLine", "ProductionKPI") not in observed
    assert ("DimLine", "EmployeeAssignment") not in observed
    assert ("DimDepartment", "EmployeeAssignment") not in observed
    assert "DimRegion" not in set(active["one_table"]).union(active["many_table"])


def test_reconciliation_checklist_never_claims_pbix_evidence():
    targets = pd.DataFrame(
        [
            {
                "measure": "Latest Revenue",
                "expected_numeric_value": 1.0,
                "tolerance": 0.01,
            }
        ]
    )
    checklist = build_reconciliation_checklist(targets)
    assert checklist["validation_status"].eq("NOT_YET_VALIDATED_IN_PBIX").all()
    assert checklist["actual_pbix_value"].eq("").all()
    assert checklist["evidence_reference"].eq("").all()


def test_acceptance_checklist_is_blank_evidence_template():
    checklist = build_acceptance_checklist()
    assert len(checklist) == 30
    assert checklist["status"].eq("NOT_YET_VALIDATED_IN_PBIX").all()
    assert checklist["evidence_reference"].eq("").all()
    assert checklist["check_id"].is_unique
