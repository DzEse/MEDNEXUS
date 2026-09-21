import os

import pytest

from mednexus.enhanced_twin_prototype import build_prototype
from mednexus.promotion_filter_validation import (
    APPROVED_NEW_EXPORTS,
    MERGE_ENRICHMENTS,
    PROMOTION_DECISIONS,
    build_promotion_decisions,
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


def test_phase12f_approved_plan_is_now_realized_by_phase12g_contract():
    assert len(EXPECTED_EXPORTS) == 58
    assert set(APPROVED_NEW_EXPORTS).issubset(EXPECTED_EXPORTS)



def test_phase12f_role_specific_geography_decision_remains_preserved():
    assert MERGE_ENRICHMENTS == {
        "dim_plant_geo": "DimPlant",
        "dim_supplier_geo": "DimSupplier",
        "dim_customer_geo": "DimCustomer",
    }
