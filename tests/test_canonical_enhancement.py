import os

import pytest

from mednexus.canonical_enhancement import (
    GEOGRAPHY_LABEL,
    promote_approved_structures,
    validate_phase12g_source_package,
)
from mednexus.data_dictionary import build_data_dictionary, build_table_register
from mednexus.quality import (
    evaluate,
    evaluate_referential_integrity,
)
from mednexus.synthetic import generate


@pytest.fixture(scope="module")
def frames():
    old = os.environ.get("MEDNEXUS_MONTHS")
    os.environ["MEDNEXUS_MONTHS"] = "2"
    try:
        result = promote_approved_structures(generate(seed=512))
    finally:
        if old is None:
            os.environ.pop("MEDNEXUS_MONTHS", None)
        else:
            os.environ["MEDNEXUS_MONTHS"] = old
    return result


def test_phase12g_source_gate_passes(frames):
    checks = validate_phase12g_source_package(frames)
    assert not checks.empty
    assert checks["status"].eq("PASS").all()


def test_only_approved_new_source_tables_are_added(frames):
    expected = {
        "dim_warehouse",
        "dim_shift",
        "dim_department",
        "dim_job_role",
        "fact_employee_assignment",
    }
    assert expected.issubset(frames)

    prohibited = {
        "dim_region",
        "dim_material",
        "bridge_product_material",
        "fact_vacancy",
        "fact_candidate_event",
        "fact_production_event",
        "fact_inspection_event",
        "fact_purchase_order",
        "fact_receipt",
        "fact_inventory_movement",
        "fact_inventory_snapshot",
        "fact_order_fulfillment_event",
    }
    assert not prohibited.intersection(frames)


def test_role_specific_geography_is_canonical_and_complete(frames):
    for table in ("dim_plant", "dim_supplier", "dim_customer", "dim_warehouse"):
        df = frames[table]
        assert df["geography_status"].eq(GEOGRAPHY_LABEL).all()
        assert df["latitude"].between(-90, 90).all()
        assert df["longitude"].between(-180, 180).all()

    assert "geography_region" in frames["dim_plant"].columns
    assert "geography_region" in frames["dim_supplier"].columns
    assert "geography_region" in frames["dim_customer"].columns
    assert "region_id" not in frames["dim_warehouse"].columns


def test_employee_assignment_is_one_current_row_per_employee(frames):
    assignment = frames["fact_employee_assignment"]
    assert len(assignment) == len(frames["dim_employee"])
    assert assignment["employee_id"].is_unique
    assert assignment["assignment_status"].eq("CURRENT_SYNTHETIC_CANONICAL").all()


def test_department_role_assignment_hierarchy_is_consistent(frames):
    assignment = frames["fact_employee_assignment"]
    roles = frames["dim_job_role"][["job_role_id", "department_id"]]
    joined = assignment.merge(
        roles,
        on="job_role_id",
        how="left",
        suffixes=("_assignment", "_role"),
        validate="many_to_one",
    )
    assert joined["department_id_role"].notna().all()
    assert joined["department_id_assignment"].eq(joined["department_id_role"]).all()


def test_optional_assignment_line_always_belongs_to_assignment_plant(frames):
    assignment = frames["fact_employee_assignment"]
    scoped = assignment[assignment["line_id"].astype(str) != ""].copy()
    line_map = frames["dim_line"].set_index("line_id")["plant_id"]
    expected = scoped["line_id"].map(line_map)
    assert expected.notna().all()
    assert expected.astype(str).eq(scoped["plant_id"].astype(str)).all()


def test_promoted_source_quality_and_referential_integrity_pass(frames):
    table_q, business_q = evaluate(frames)
    referential_q = evaluate_referential_integrity(frames)
    assert table_q["status"].eq("PASS").all()
    assert business_q["status"].eq("PASS").all()
    assert referential_q["status"].eq("PASS").all()


def test_governance_artifacts_include_all_promoted_tables_and_fields(frames):
    register = build_table_register(frames)
    dictionary = build_data_dictionary(frames)
    for table in (
        "dim_warehouse",
        "dim_shift",
        "dim_department",
        "dim_job_role",
        "fact_employee_assignment",
    ):
        assert table in set(register["table"])
        assert table in set(dictionary["table"])
