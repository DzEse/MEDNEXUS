from __future__ import annotations

import pandas as pd

from .enhanced_twin_prototype import (
    _geo_dimensions,
    _warehouses_and_materials,
    _workforce_prototype,
)


PHASE12G_STATUS = "CANONICAL_PROMOTION_APPLIED"
GEOGRAPHY_LABEL = "SIMULATED_ENTERPRISE_FOOTPRINT"


def _merge_geo_attributes(
    base: pd.DataFrame,
    geo: pd.DataFrame,
    key: str,
) -> pd.DataFrame:
    attrs = geo[
        [key, "country", "region", "city", "latitude", "longitude", "geography_status"]
    ].rename(columns={"region": "geography_region"})
    return base.merge(attrs, on=key, how="left", validate="one_to_one")


def promote_approved_structures(
    frames: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """
    Apply only the Phase 12F-approved structures to the canonical source package.

    Deliberately excluded:
    - shared DimRegion relationship;
    - material/product bridge;
    - vacancy/candidate event facts;
    - split production/inspection events;
    - reverse-disaggregated purchase/receipt/inventory facts;
    - duplicate order-fulfillment event log.
    """
    promoted = {name: df.copy() for name, df in frames.items()}

    geo = _geo_dimensions(promoted)
    promoted["dim_plant"] = _merge_geo_attributes(
        promoted["dim_plant"], geo["dim_plant_geo"], "plant_id"
    )
    promoted["dim_supplier"] = _merge_geo_attributes(
        promoted["dim_supplier"], geo["dim_supplier_geo"], "supplier_id"
    )
    promoted["dim_customer"] = _merge_geo_attributes(
        promoted["dim_customer"], geo["dim_customer_geo"], "customer_id"
    )

    warehouse_bundle = _warehouses_and_materials(promoted, geo)
    dim_warehouse = warehouse_bundle["dim_warehouse"].drop(
        columns=["region_id"], errors="ignore"
    ).copy()
    dim_warehouse["canonical_status"] = PHASE12G_STATUS
    promoted["dim_warehouse"] = dim_warehouse

    workforce = _workforce_prototype(promoted)
    promoted["dim_shift"] = workforce["dim_shift"].copy()
    promoted["dim_department"] = workforce["dim_department"].copy()
    promoted["dim_job_role"] = workforce["dim_job_role"].copy()

    assignment = workforce["fact_employee_assignment"].copy()
    assignment["assignment_status"] = "CURRENT_SYNTHETIC_CANONICAL"
    promoted["fact_employee_assignment"] = assignment

    return promoted


def validate_phase12g_source_package(
    frames: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows: list[dict] = []

    def add(check: str, passed: bool, detail: str = "") -> None:
        rows.append(
            {
                "check": check,
                "passed": bool(passed),
                "status": "PASS" if passed else "FAIL",
                "detail": detail,
            }
        )

    expected_new = {
        "dim_warehouse",
        "dim_shift",
        "dim_department",
        "dim_job_role",
        "fact_employee_assignment",
    }
    add(
        "approved_source_tables_present",
        expected_new.issubset(frames),
        "|".join(sorted(expected_new)),
    )

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
    add(
        "nonapproved_prototype_tables_absent",
        not prohibited.intersection(frames),
        "|".join(sorted(prohibited.intersection(frames))),
    )

    geo_fields = {
        "country",
        "geography_region",
        "city",
        "latitude",
        "longitude",
        "geography_status",
    }
    for table in ("dim_plant", "dim_supplier", "dim_customer"):
        df = frames[table]
        add(
            f"{table}_geography_columns_present",
            geo_fields.issubset(df.columns),
        )
        if geo_fields.issubset(df.columns):
            add(
                f"{table}_geography_valid",
                df["latitude"].between(-90, 90).all()
                and df["longitude"].between(-180, 180).all()
                and df["geography_status"].eq(GEOGRAPHY_LABEL).all(),
            )

    warehouse = frames["dim_warehouse"]
    add(
        "warehouse_geography_valid",
        warehouse["latitude"].between(-90, 90).all()
        and warehouse["longitude"].between(-180, 180).all()
        and warehouse["geography_status"].eq(GEOGRAPHY_LABEL).all(),
    )
    add(
        "warehouse_has_no_global_region_fk",
        "region_id" not in warehouse.columns,
    )

    assignment = frames["fact_employee_assignment"]
    add(
        "one_current_assignment_per_employee",
        assignment["employee_id"].notna().all()
        and not assignment["employee_id"].duplicated().any()
        and len(assignment) == len(frames["dim_employee"]),
    )
    add(
        "assignment_status_is_canonical",
        assignment["assignment_status"].eq("CURRENT_SYNTHETIC_CANONICAL").all(),
    )

    line_nonblank = assignment[assignment["line_id"].astype(str) != ""]
    if len(line_nonblank):
        line_to_plant = frames["dim_line"].set_index("line_id")["plant_id"]
        expected_plant = line_nonblank["line_id"].map(line_to_plant)
        add(
            "assignment_line_matches_assignment_plant",
            expected_plant.notna().all()
            and expected_plant.astype(str).eq(
                line_nonblank["plant_id"].astype(str)
            ).all(),
        )
    else:
        add("assignment_line_matches_assignment_plant", True, "no line-scoped assignments")

    return pd.DataFrame(rows)
