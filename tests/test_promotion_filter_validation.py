import os

import pytest

from mednexus.enhanced_twin_prototype import build_prototype
from mednexus.promotion_filter_validation import (
    APPROVED_NEW_EXPORTS,
    MERGE_ENRICHMENTS,
    PROMOTION_DECISIONS,
    build_promotion_decisions,
    build_proposed_relationship_contract,
    build_proposed_table_roles,
    validate_filter_behavior,
)
from mednexus.semantic_model import EXPECTED_EXPORTS
from mednexus.synthetic import generate


@pytest.fixture(scope="module")
def compact_frames():
    old = os.environ.get("MEDNEXUS_MONTHS")
    os.environ["MEDNEXUS_MONTHS"] = "2"
    try:
        frames = generate(seed=321)
    finally:
        if old is None:
            os.environ.pop("MEDNEXUS_MONTHS", None)
        else:
            os.environ["MEDNEXUS_MONTHS"] = old
    return frames


@pytest.fixture(scope="module")
def prototype(compact_frames):
    return build_prototype(compact_frames, lookback_days=14)


def test_phase12f_reviews_all_twenty_prototype_tables():
    decisions = build_promotion_decisions()
    assert len(decisions) == 20
    assert set(decisions["prototype_table"]) == set(PROMOTION_DECISIONS)


def test_phase12f_promotion_counts_are_explicit():
    decisions = build_promotion_decisions()
    counts = decisions["decision"].value_counts().to_dict()
    assert counts["APPROVED_FOR_CANONICAL_IMPLEMENTATION"] == 8
    assert counts["REWORK_REQUIRED"] == 8
    assert counts["DEFERRED"] == 3
    assert counts["NOT_PROMOTED_REDUNDANT"] == 1
    assert len(APPROVED_NEW_EXPORTS) == 5
    assert len(MERGE_ENRICHMENTS) == 3


def test_high_risk_reverse_disaggregated_facts_are_not_approved():
    for table in (
        "fact_vacancy",
        "fact_candidate_event",
        "fact_production_event",
        "fact_inspection_event",
        "fact_purchase_order",
        "fact_receipt",
        "fact_inventory_movement",
        "fact_inventory_snapshot",
    ):
        assert PROMOTION_DECISIONS[table]["decision"] == "REWORK_REQUIRED"


def test_product_material_bridge_and_global_region_are_deferred():
    assert PROMOTION_DECISIONS["bridge_product_material"]["decision"] == "DEFERRED"
    assert PROMOTION_DECISIONS["dim_region"]["decision"] == "DEFERRED"


def test_existing_order_fulfillment_process_is_not_duplicated():
    assert PROMOTION_DECISIONS["fact_order_fulfillment_event"]["decision"] == "NOT_PROMOTED_REDUNDANT"


def test_phase12f_does_not_mutate_current_53_export_contract():
    assert len(EXPECTED_EXPORTS) == 53
    assert not set(APPROVED_NEW_EXPORTS).intersection(EXPECTED_EXPORTS)


def test_proposed_post_promotion_table_roles_are_58_and_employee_is_connected():
    roles = build_proposed_table_roles()
    assert len(roles) == 58
    employee = roles[roles["table"] == "DimEmployee"].iloc[0]
    assert employee["model_status"] == "CONNECTED"
    for table in APPROVED_NEW_EXPORTS:
        row = roles[roles["table"] == table]
        assert len(row) == 1
        assert row.iloc[0]["model_status"] == "CONNECTED"


def test_proposed_relationships_preserve_semantic_safety():
    rel = build_proposed_relationship_contract()
    assert rel["cardinality"].eq("1:*").all()
    assert rel["cross_filter_direction"].eq("single").all()

    # New workforce route deliberately omits Line→EmployeeAssignment.
    assert not (
        rel["one_table"].eq("DimLine")
        & rel["many_table"].eq("EmployeeAssignment")
        & rel["active"]
    ).any()

    # Shared global geography must not be connected.
    assert "DimRegion" not in set(rel["one_table"]).union(rel["many_table"])

    # Department reaches assignment through role rather than a parallel direct path.
    assert (
        rel["one_table"].eq("DimDepartment")
        & rel["many_table"].eq("DimJobRole")
        & rel["active"]
    ).any()
    assert (
        rel["one_table"].eq("DimJobRole")
        & rel["many_table"].eq("EmployeeAssignment")
        & rel["active"]
    ).any()
    assert not (
        rel["one_table"].eq("DimDepartment")
        & rel["many_table"].eq("EmployeeAssignment")
        & rel["active"]
    ).any()


def test_filter_behavior_contract_simulation_passes(compact_frames, prototype):
    checks, issues = validate_filter_behavior(compact_frames, prototype)
    assert not checks.empty
    assert (checks["status"] == "PASS").all()
    assert issues.empty


def test_geography_is_role_specific_and_workforce_filtering_is_single_path(compact_frames, prototype):
    checks, _ = validate_filter_behavior(compact_frames, prototype)
    named = checks.set_index("check")["status"].to_dict()
    assert named["no_global_dimregion_relationship"] == "PASS"
    assert named["no_direct_dimline_employeeassignment_relationship"] == "PASS"
    assert named["department_filters_assignment_via_jobrole_only"] == "PASS"
    assert named["department_hierarchy_filter_matches_assignment_reference"] == "PASS"
    assert named["employee_filter_one_current_assignment"] == "PASS"
