import os

import numpy as np
import pandas as pd
import pytest

from mednexus.enhanced_twin_prototype import (
    TABLE_CONTRACTS,
    build_prototype,
    build_relationship_contract,
    validate_prototype,
)
from mednexus.synthetic import generate


@pytest.fixture(scope="module")
def compact_frames():
    old = os.environ.get("MEDNEXUS_MONTHS")
    os.environ["MEDNEXUS_MONTHS"] = "2"
    try:
        frames = generate(seed=123)
    finally:
        if old is None:
            os.environ.pop("MEDNEXUS_MONTHS", None)
        else:
            os.environ["MEDNEXUS_MONTHS"] = old
    return frames


@pytest.fixture(scope="module")
def prototype(compact_frames):
    return build_prototype(compact_frames, lookback_days=14)


def test_phase12e_contract_covers_every_prototype_table(prototype):
    assert set(prototype) == set(TABLE_CONTRACTS)
    assert len(prototype) == 20


def test_phase12e_validation_gate_passes(compact_frames, prototype):
    checks = validate_prototype(compact_frames, prototype)
    assert not checks.empty
    assert (checks["status"] == "PASS").all()


def test_geospatial_entities_are_explicitly_simulated_and_valid(prototype):
    for table in ("dim_plant_geo", "dim_supplier_geo", "dim_customer_geo", "dim_warehouse"):
        df = prototype[table]
        assert df["geography_status"].eq("SIMULATED_ENTERPRISE_FOOTPRINT").all()
        assert df["latitude"].between(-90, 90).all()
        assert df["longitude"].between(-180, 180).all()


def test_inventory_balance_and_movement_reconciliation(prototype):
    snap = prototype["fact_inventory_snapshot"].copy()
    expected = (
        snap["opening_balance"]
        + snap["receipt_qty"]
        - snap["consumption_qty"]
        + snap["adjustment_qty"]
    )
    assert (expected == snap["closing_balance"]).all()
    assert (snap["closing_balance"] >= 0).all()

    movements = prototype["fact_inventory_movement"].copy()
    movements["month"] = pd.to_datetime(movements["movement_date"]).dt.to_period("M").dt.to_timestamp()
    movement_delta = movements.groupby(["warehouse_id", "material_id", "month"])["signed_quantity"].sum()

    snap["month"] = pd.to_datetime(snap["month"]).dt.to_period("M").dt.to_timestamp()
    snap = snap.set_index(["warehouse_id", "material_id", "month"])
    expected_delta = snap["closing_balance"] - snap["opening_balance"]
    assert movement_delta.reindex(expected_delta.index, fill_value=0).equals(expected_delta)


def test_shift_events_are_internally_consistent_and_reconcile(compact_frames, prototype):
    events = prototype["fact_production_event"]
    assert (events["good_count"] + events["scrap_units"] == events["total_count"]).all()
    assert (events["rework_units"] + events["scrap_units"] == events["defect_units"]).all()
    assert (pd.to_datetime(events["event_end"]) > pd.to_datetime(events["event_start"])).all()

    canonical = compact_frames["fact_production"].set_index("production_order_id")
    agg = events.groupby("production_order_id")[
        ["total_count", "good_count", "defect_units", "rework_units", "scrap_units"]
    ].sum()
    for column in agg.columns:
        assert np.array_equal(
            agg[column].sort_index().to_numpy(),
            canonical.loc[agg.index, column].to_numpy(),
        )


def test_inspections_are_independent_events_without_fabricated_spec_limits(prototype):
    inspections = prototype["fact_inspection_event"]
    production = prototype["fact_production_event"].set_index("production_event_id")
    assert inspections["production_event_id"].is_unique
    assert inspections["production_event_id"].isin(production.index).all()
    assert inspections["specification_status"].eq("NO_SPEC_LIMITS_IN_PROTOTYPE").all()
    aligned = inspections.set_index("production_event_id")
    assert (pd.to_datetime(aligned["inspection_timestamp"]) > pd.to_datetime(production["event_end"])).all()


def test_purchase_order_disaggregation_reconciles_to_supply(compact_frames, prototype):
    po = prototype["fact_purchase_order"]
    grouped = po.groupby("source_supply_key")[
        ["ordered_qty", "expected_received_qty", "expected_material_defects"]
    ].sum()

    supply = compact_frames["fact_supply"].copy()
    supply["month"] = pd.to_datetime(supply["month"])
    supply["source_supply_key"] = supply["month"].dt.strftime("%Y-%m") + "|" + supply["supplier_id"]
    supply = supply[supply["source_supply_key"].isin(grouped.index)].set_index("source_supply_key")

    assert (grouped["ordered_qty"] == supply.loc[grouped.index, "ordered_qty"]).all()
    assert (grouped["expected_received_qty"] == supply.loc[grouped.index, "received_qty"]).all()
    assert (grouped["expected_material_defects"] == supply.loc[grouped.index, "material_defects"]).all()


def test_recruitment_event_chronology_is_monotonic(prototype):
    events = prototype["fact_candidate_event"].sort_values(["candidate_id", "event_timestamp"])
    stage_rank = {
        "Application": 1,
        "Screening": 2,
        "Interview": 3,
        "Assessment": 4,
        "Offer": 5,
        "Acceptance": 6,
        "Onboarding": 7,
    }
    for _, group in events.groupby("candidate_id"):
        ranks = group["stage"].map(stage_rank).to_numpy()
        assert np.all(np.diff(ranks) > 0)
        times = pd.to_datetime(group["event_timestamp"]).to_numpy()
        assert np.all(np.diff(times) > np.timedelta64(0, "ns"))


def test_order_fulfillment_event_log_is_valid_but_scope_limited(prototype):
    events = prototype["fact_order_fulfillment_event"].sort_values(["case_id", "event_timestamp"])
    assert events["scope"].eq("ORDER_FULFILLMENT_ONLY").all()
    sequences = events.groupby("case_id")["event_type"].apply(list)
    assert sequences.map(lambda x: x == ["Order Created", "Shipped", "Delivered"]).all()


def test_prototype_relationship_contract_never_claims_powerbi_promotion(prototype):
    relationships = build_relationship_contract()
    assert not relationships.empty
    assert relationships["relationship_status"].eq("PROTOTYPE_ONLY_NOT_POWER_BI_PROMOTED").all()
    assert set(relationships["child_table"]).issubset(prototype)
    assert set(relationships["parent_table"]).issubset(prototype)
