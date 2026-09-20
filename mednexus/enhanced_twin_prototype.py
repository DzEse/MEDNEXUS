from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .config import path
from .synthetic import _stable_index, generate
from .utils import save_frame, write_json


PROTOTYPE_VERSION = "12E.1"
PROTOTYPE_SCOPE = "STRUCTURAL_PROTOTYPE_NOT_CANONICAL_PRODUCTION_DATA"


@dataclass(frozen=True)
class Relationship:
    child_table: str
    child_key: str
    parent_table: str
    parent_key: str


TABLE_CONTRACTS = {
    "dim_region": {
        "grain": "one row per simulated enterprise region",
        "pk": "region_id",
        "purpose": "Conformed geographic rollup for analytical mapping.",
    },
    "dim_plant_geo": {
        "grain": "one row per existing MEDNEXUS plant enriched with simulated geography",
        "pk": "plant_id",
        "purpose": "Plant geography for map and region drill paths.",
    },
    "dim_supplier_geo": {
        "grain": "one row per existing supplier enriched with simulated geography",
        "pk": "supplier_id",
        "purpose": "Supplier geography and map segmentation.",
    },
    "dim_customer_geo": {
        "grain": "one row per existing healthcare customer enriched with simulated geography",
        "pk": "customer_id",
        "purpose": "Healthcare-customer geography without patient-identifiable information.",
    },
    "dim_warehouse": {
        "grain": "one row per simulated warehouse serving a MEDNEXUS plant",
        "pk": "warehouse_id",
        "purpose": "Inventory custody and logistics drill path.",
    },
    "dim_material": {
        "grain": "one row per simulated material",
        "pk": "material_id",
        "purpose": "Supplier, inventory and production-material traceability.",
    },
    "bridge_product_material": {
        "grain": "one row per product x required material",
        "pk": "product_material_id",
        "purpose": "Synthetic bill-of-material relationship for prototype consumption demand.",
    },
    "dim_shift": {
        "grain": "one row per standard shift definition",
        "pk": "shift_id",
        "purpose": "Shift segmentation for workforce and production events.",
    },
    "dim_department": {
        "grain": "one row per enterprise department",
        "pk": "department_id",
        "purpose": "Conformed workforce/recruitment department reference.",
    },
    "dim_job_role": {
        "grain": "one row per department x job role",
        "pk": "job_role_id",
        "purpose": "Role segmentation for employee assignment and vacancies.",
    },
    "fact_employee_assignment": {
        "grain": "one current synthetic assignment per employee",
        "pk": "assignment_id",
        "purpose": "Prototype Employee→Department→Role→Plant→Shift→Line linkage.",
    },
    "fact_vacancy": {
        "grain": "one simulated vacancy",
        "pk": "vacancy_id",
        "purpose": "Vacancy pressure and critical-role prototype.",
    },
    "fact_candidate_event": {
        "grain": "one simulated candidate recruitment-stage event",
        "pk": "candidate_event_id",
        "purpose": "Recruitment event chronology and bottleneck-ready event grain.",
    },
    "fact_production_event": {
        "grain": "one production order x machine x shift event",
        "pk": "production_event_id",
        "purpose": "Shift-aware production event prototype preserving canonical daily totals.",
    },
    "fact_inspection_event": {
        "grain": "one inspection event per prototype production event",
        "pk": "inspection_id",
        "purpose": "Independent quality-event grain linked explicitly to production.",
    },
    "fact_purchase_order": {
        "grain": "one simulated purchase-order line",
        "pk": "po_line_id",
        "purpose": "Supplier→material purchase-order history derived from canonical monthly supply facts.",
    },
    "fact_receipt": {
        "grain": "one receipt per prototype purchase-order line",
        "pk": "receipt_id",
        "purpose": "Promised versus actual material receipt and material-lot traceability.",
    },
    "fact_inventory_movement": {
        "grain": "one warehouse x material inventory movement event",
        "pk": "inventory_movement_id",
        "purpose": "Physical inventory ledger supporting receipt/consumption/adjustment reconciliation.",
    },
    "fact_inventory_snapshot": {
        "grain": "one warehouse x material x month snapshot",
        "pk": "inventory_snapshot_id",
        "purpose": "Opening/closing balance, safety stock, stockout and shortage analysis.",
    },
    "fact_order_fulfillment_event": {
        "grain": "one order-fulfillment lifecycle event",
        "pk": "fulfillment_event_id",
        "purpose": "Validated Order Created→Shipped→Delivered event-log prototype.",
    },
}


RELATIONSHIPS = (
    Relationship("dim_plant_geo", "region_id", "dim_region", "region_id"),
    Relationship("dim_supplier_geo", "region_id", "dim_region", "region_id"),
    Relationship("dim_customer_geo", "region_id", "dim_region", "region_id"),
    Relationship("dim_warehouse", "plant_id", "dim_plant_geo", "plant_id"),
    Relationship("dim_warehouse", "region_id", "dim_region", "region_id"),
    Relationship("dim_material", "preferred_supplier_id", "dim_supplier_geo", "supplier_id"),
    Relationship("bridge_product_material", "material_id", "dim_material", "material_id"),
    Relationship("fact_employee_assignment", "department_id", "dim_department", "department_id"),
    Relationship("fact_employee_assignment", "job_role_id", "dim_job_role", "job_role_id"),
    Relationship("fact_employee_assignment", "shift_id", "dim_shift", "shift_id"),
    Relationship("fact_employee_assignment", "plant_id", "dim_plant_geo", "plant_id"),
    Relationship("fact_vacancy", "department_id", "dim_department", "department_id"),
    Relationship("fact_vacancy", "job_role_id", "dim_job_role", "job_role_id"),
    Relationship("fact_vacancy", "plant_id", "dim_plant_geo", "plant_id"),
    Relationship("fact_candidate_event", "vacancy_id", "fact_vacancy", "vacancy_id"),
    Relationship("fact_production_event", "shift_id", "dim_shift", "shift_id"),
    Relationship("fact_production_event", "plant_id", "dim_plant_geo", "plant_id"),
    Relationship("fact_inspection_event", "production_event_id", "fact_production_event", "production_event_id"),
    Relationship("fact_purchase_order", "supplier_id", "dim_supplier_geo", "supplier_id"),
    Relationship("fact_purchase_order", "material_id", "dim_material", "material_id"),
    Relationship("fact_receipt", "po_line_id", "fact_purchase_order", "po_line_id"),
    Relationship("fact_receipt", "material_id", "dim_material", "material_id"),
    Relationship("fact_receipt", "warehouse_id", "dim_warehouse", "warehouse_id"),
    Relationship("fact_inventory_movement", "warehouse_id", "dim_warehouse", "warehouse_id"),
    Relationship("fact_inventory_movement", "material_id", "dim_material", "material_id"),
    Relationship("fact_inventory_snapshot", "warehouse_id", "dim_warehouse", "warehouse_id"),
    Relationship("fact_inventory_snapshot", "material_id", "dim_material", "material_id"),
)


REGION_CATALOG = {
    "Ontario": ("REG_CA_ON", "Canada", "Ontario", "Toronto", 43.6532, -79.3832),
    "North West England": ("REG_UK_NW", "United Kingdom", "North West England", "Liverpool", 53.4084, -2.9916),
    "Canada": ("REG_CA_ON", "Canada", "Ontario", "Toronto", 43.6532, -79.3832),
    "UK": ("REG_UK_NW", "United Kingdom", "North West England", "Liverpool", 53.4084, -2.9916),
    "US": ("REG_US_NE", "United States", "Northeast", "Boston", 42.3601, -71.0589),
    "EU_DE": ("REG_EU_DE", "Germany", "North Rhine-Westphalia", "Cologne", 50.9375, 6.9603),
    "EU_NL": ("REG_EU_NL", "Netherlands", "North Holland", "Amsterdam", 52.3676, 4.9041),
}


ROLE_MAP = {
    "Manufacturing": ("Production Technician", "Line Lead"),
    "Quality": ("Quality Technician", "Quality Engineer"),
    "Maintenance": ("Maintenance Technician", "Reliability Engineer"),
    "Supply Chain": ("Supply Planner", "Buyer"),
    "Logistics": ("Logistics Coordinator", "Warehouse Specialist"),
    "Finance": ("Financial Analyst", "Cost Analyst"),
    "HR": ("HR Specialist", "Recruiter"),
    "Technology": ("Systems Analyst", "Data Analyst"),
}


def _split_integer(value: int, shares: Iterable[float]) -> list[int]:
    shares = list(shares)
    raw = [int(np.floor(value * share)) for share in shares]
    remainder = int(value - sum(raw))
    for idx in range(remainder):
        raw[idx % len(raw)] += 1
    return raw


def _geo_dimensions(frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    plants = frames["dim_plant"].copy()
    plant_rows = []
    region_rows: dict[str, tuple] = {}
    for row in plants.itertuples(index=False):
        geo = REGION_CATALOG[str(row.region)]
        region_id, country, region, city, lat, lon = geo
        region_rows[region_id] = geo
        plant_rows.append(
            {
                "plant_id": row.plant_id,
                "plant_name": row.plant_name,
                "region_id": region_id,
                "country": country,
                "region": region,
                "city": city,
                "latitude": lat,
                "longitude": lon,
                "plant_type": "Manufacturing",
                "capacity_class": "Prototype synthetic attribute",
                "geography_status": "SIMULATED_ENTERPRISE_FOOTPRINT",
            }
        )

    suppliers = frames["dim_supplier"].copy()
    supplier_geos = ["Ontario", "North West England", "US", "EU_DE", "EU_NL"]
    supplier_rows = []
    for row in suppliers.itertuples(index=False):
        geo_key = supplier_geos[_stable_index(row.supplier_id, n=len(supplier_geos))]
        geo = REGION_CATALOG[geo_key]
        region_id, country, region, city, lat, lon = geo
        region_rows[region_id] = geo
        supplier_rows.append(
            {
                **row._asdict(),
                "region_id": region_id,
                "country": country,
                "region": region,
                "city": city,
                "latitude": lat,
                "longitude": lon,
                "geography_status": "SIMULATED_ENTERPRISE_FOOTPRINT",
            }
        )

    customers = frames["dim_customer"].copy()
    customer_rows = []
    for row in customers.itertuples(index=False):
        key = str(row.region)
        if key == "EU":
            key = "EU_DE" if _stable_index(row.customer_id, n=2) == 0 else "EU_NL"
        geo = REGION_CATALOG[key]
        region_id, country, region, city, lat, lon = geo
        region_rows[region_id] = geo
        customer_rows.append(
            {
                "customer_id": row.customer_id,
                "customer_type": row.customer_type,
                "source_region_label": row.region,
                "region_id": region_id,
                "country": country,
                "region": region,
                "city": city,
                "latitude": lat,
                "longitude": lon,
                "geography_status": "SIMULATED_ENTERPRISE_FOOTPRINT",
            }
        )

    dim_region = pd.DataFrame(
        [
            {
                "region_id": region_id,
                "country": geo[1],
                "region": geo[2],
                "representative_city": geo[3],
                "representative_latitude": geo[4],
                "representative_longitude": geo[5],
                "geography_status": "SIMULATED_ENTERPRISE_FOOTPRINT",
            }
            for region_id, geo in sorted(region_rows.items())
        ]
    )
    return {
        "dim_region": dim_region,
        "dim_plant_geo": pd.DataFrame(plant_rows),
        "dim_supplier_geo": pd.DataFrame(supplier_rows),
        "dim_customer_geo": pd.DataFrame(customer_rows),
    }


def _warehouses_and_materials(frames: dict[str, pd.DataFrame], geo: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    warehouses = []
    for idx, row in enumerate(geo["dim_plant_geo"].itertuples(index=False), start=1):
        warehouses.append(
            {
                "warehouse_id": f"WH{idx:03d}",
                "warehouse_name": f"{row.plant_name} Warehouse",
                "plant_id": row.plant_id,
                "region_id": row.region_id,
                "country": row.country,
                "region": row.region,
                "city": row.city,
                "latitude": row.latitude + 0.01,
                "longitude": row.longitude + 0.01,
                "capacity_units": 60000 + 5000 * idx,
                "geography_status": "SIMULATED_ENTERPRISE_FOOTPRINT",
            }
        )
    dim_warehouse = pd.DataFrame(warehouses)

    products = frames["dim_product"]
    families = sorted(products["product_family"].unique())
    supplier_ids = list(geo["dim_supplier_geo"]["supplier_id"])
    material_rows = []
    material_id = 1
    family_materials: dict[str, list[str]] = {}
    for family in families:
        family_materials[family] = []
        for component in ("Primary Component", "Packaging Component"):
            mid = f"MAT{material_id:04d}"
            preferred = supplier_ids[_stable_index(family, component, n=len(supplier_ids))]
            material_rows.append(
                {
                    "material_id": mid,
                    "material_name": f"{family} {component}",
                    "material_category": component,
                    "product_family": family,
                    "preferred_supplier_id": preferred,
                    "unit_of_measure": "EA",
                    "prototype_status": PROTOTYPE_SCOPE,
                }
            )
            family_materials[family].append(mid)
            material_id += 1
    dim_material = pd.DataFrame(material_rows)

    bridge_rows = []
    for product in products.itertuples(index=False):
        mids = family_materials[str(product.product_family)]
        for idx, mid in enumerate(mids, start=1):
            bridge_rows.append(
                {
                    "product_material_id": f"{product.product_id}-{mid}",
                    "product_id": product.product_id,
                    "material_id": mid,
                    "quantity_per_unit": 1.0 if idx == 1 else 0.25,
                    "generation_assumption": "Synthetic prototype bill-of-material quantity.",
                }
            )
    return {
        "dim_warehouse": dim_warehouse,
        "dim_material": dim_material,
        "bridge_product_material": pd.DataFrame(bridge_rows),
    }


def _workforce_prototype(frames: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    shifts = pd.DataFrame(
        [
            {"shift_id": "S_DAY", "shift_name": "Day", "start_hour": 6, "duration_hours": 8},
            {"shift_id": "S_EVE", "shift_name": "Evening", "start_hour": 14, "duration_hours": 8},
            {"shift_id": "S_NIGHT", "shift_name": "Night", "start_hour": 22, "duration_hours": 8},
        ]
    )

    departments = sorted(frames["dim_employee"]["department"].unique())
    dim_department = pd.DataFrame(
        [{"department_id": f"DEP{idx:02d}", "department_name": name} for idx, name in enumerate(departments, start=1)]
    )
    dept_map = dict(zip(dim_department["department_name"], dim_department["department_id"]))

    role_rows = []
    role_lookup: dict[str, list[str]] = {}
    counter = 1
    for dept in departments:
        role_lookup[dept] = []
        for role in ROLE_MAP.get(dept, (f"{dept} Specialist", f"{dept} Lead")):
            rid = f"ROLE{counter:03d}"
            role_rows.append(
                {
                    "job_role_id": rid,
                    "department_id": dept_map[dept],
                    "job_role_name": role,
                    "critical_role_flag": int(dept in {"Manufacturing", "Quality", "Maintenance", "Supply Chain"}),
                }
            )
            role_lookup[dept].append(rid)
            counter += 1
    dim_job_role = pd.DataFrame(role_rows)

    lines_by_plant = {
        plant: list(group["line_id"])
        for plant, group in frames["dim_line"].groupby("plant_id")
    }
    operational = {"Manufacturing", "Quality", "Maintenance", "Supply Chain", "Logistics"}
    assignments = []
    for employee in frames["dim_employee"].itertuples(index=False):
        dept = str(employee.department)
        role_ids = role_lookup[dept]
        role_id = role_ids[_stable_index(employee.employee_id, "role", n=len(role_ids))]
        shift_id = (
            ["S_DAY", "S_EVE", "S_NIGHT"][_stable_index(employee.employee_id, "shift", n=3)]
            if dept in operational
            else "S_DAY"
        )
        line_id = ""
        if dept in {"Manufacturing", "Quality", "Maintenance"}:
            candidates = lines_by_plant[str(employee.plant_id)]
            line_id = candidates[_stable_index(employee.employee_id, "line", n=len(candidates))]
        assignments.append(
            {
                "assignment_id": f"ASN-{employee.employee_id}",
                "employee_id": employee.employee_id,
                "department_id": dept_map[dept],
                "job_role_id": role_id,
                "plant_id": employee.plant_id,
                "shift_id": shift_id,
                "line_id": line_id,
                "assignment_status": "CURRENT_SYNTHETIC_PROTOTYPE",
            }
        )
    fact_employee_assignment = pd.DataFrame(assignments)

    recruitment = frames["fact_recruitment"].copy()
    recruitment["month"] = pd.to_datetime(recruitment["month"])
    recent_months = sorted(recruitment["month"].unique())[-3:]
    recruitment = recruitment[recruitment["month"].isin(recent_months)]

    vacancy_rows = []
    for row in recruitment.itertuples(index=False):
        count = int(min(max(row.open_positions, 0), 6))
        for idx in range(count):
            dept = ["Manufacturing", "Quality", "Maintenance", "Supply Chain"][
                _stable_index(row.plant_id, row.month, idx, n=4)
            ]
            roles = role_lookup[dept]
            role_id = roles[_stable_index(row.plant_id, row.month, idx, "role", n=len(roles))]
            vacancy_rows.append(
                {
                    "vacancy_id": f"VAC-{pd.Timestamp(row.month):%Y%m}-{row.plant_id}-{idx+1:02d}",
                    "plant_id": row.plant_id,
                    "department_id": dept_map[dept],
                    "job_role_id": role_id,
                    "opening_date": (pd.Timestamp(row.month) + pd.Timedelta(days=2 + idx)).date(),
                    "criticality": "High" if dept in {"Manufacturing", "Maintenance"} else "Medium",
                    "vacancy_status": "Accepted" if idx < int(row.accepted) else "Open",
                    "generation_assumption": "Prototype vacancy disaggregation from monthly recruitment pressure.",
                }
            )
    fact_vacancy = pd.DataFrame(vacancy_rows)

    candidate_rows = []
    stage_offsets = {
        "Application": 0,
        "Screening": 2,
        "Interview": 7,
        "Assessment": 9,
        "Offer": 12,
        "Acceptance": 14,
        "Onboarding": 21,
    }
    event_counter = 1
    for vacancy in fact_vacancy.itertuples(index=False):
        for candidate_idx in range(1, 5):
            candidate_id = f"CAN-{vacancy.vacancy_id}-{candidate_idx:02d}"
            stages = ["Application"]
            if candidate_idx <= 3:
                stages.append("Screening")
            if candidate_idx <= 2:
                stages.extend(["Interview", "Assessment"])
            if candidate_idx == 1:
                stages.append("Offer")
                if vacancy.vacancy_status == "Accepted":
                    stages.extend(["Acceptance", "Onboarding"])
            for stage in stages:
                candidate_rows.append(
                    {
                        "candidate_event_id": f"CE{event_counter:07d}",
                        "candidate_id": candidate_id,
                        "vacancy_id": vacancy.vacancy_id,
                        "stage": stage,
                        "event_timestamp": pd.Timestamp(vacancy.opening_date) + pd.Timedelta(days=stage_offsets[stage], hours=10),
                        "event_class": "SYNTHETIC_RECRUITMENT_PROTOTYPE",
                    }
                )
                event_counter += 1

    return {
        "dim_shift": shifts,
        "dim_department": dim_department,
        "dim_job_role": dim_job_role,
        "fact_employee_assignment": fact_employee_assignment,
        "fact_vacancy": fact_vacancy,
        "fact_candidate_event": pd.DataFrame(candidate_rows),
    }


def _split_production_events(frames: dict[str, pd.DataFrame], lookback_days: int = 45) -> dict[str, pd.DataFrame]:
    source = frames["fact_production"].copy()
    source["date"] = pd.to_datetime(source["date"])
    cutoff = source["date"].max() - pd.Timedelta(days=max(1, lookback_days - 1))
    source = source[source["date"] >= cutoff].copy()

    events = []
    inspections = []
    for row in source.itertuples(index=False):
        split_total = _split_integer(int(row.total_count), [0.5, 0.5])
        split_rework = _split_integer(int(row.rework_units), [0.5, 0.5])
        split_scrap = _split_integer(int(row.scrap_units), [0.5, 0.5])
        float_columns = [
            "planned_production_min",
            "planned_downtime_min",
            "unplanned_downtime_min",
            "run_time_min",
        ]
        split_floats = {column: [float(getattr(row, column)) / 2.0] * 2 for column in float_columns}
        for idx, (shift_id, start_hour) in enumerate((("S_DAY", 6), ("S_EVE", 14))):
            event_id = f"PE-{row.production_order_id}-{idx+1}"
            start_ts = pd.Timestamp(row.date) + pd.Timedelta(hours=start_hour)
            run_minutes = split_floats["run_time_min"][idx]
            end_ts = start_ts + pd.Timedelta(minutes=run_minutes)
            event = {
                "production_event_id": event_id,
                "production_order_id": row.production_order_id,
                "event_date": pd.Timestamp(row.date).date(),
                "event_start": start_ts,
                "event_end": end_ts,
                "plant_id": row.plant_id,
                "line_id": row.line_id,
                "machine_id": row.machine_id,
                "product_id": row.product_id,
                "shift_id": shift_id,
                "planned_production_min": split_floats["planned_production_min"][idx],
                "planned_downtime_min": split_floats["planned_downtime_min"][idx],
                "unplanned_downtime_min": split_floats["unplanned_downtime_min"][idx],
                "run_time_min": run_minutes,
                "total_count": split_total[idx],
                "good_count": split_total[idx] - split_scrap[idx],
                "defect_units": split_rework[idx] + split_scrap[idx],
                "rework_units": split_rework[idx],
                "scrap_units": split_scrap[idx],
                "ideal_cycle_min": float(row.ideal_cycle_min),
                "prototype_status": PROTOTYPE_SCOPE,
            }
            events.append(event)
            if event["scrap_units"] > 0:
                disposition = "SCRAP_PRESENT"
            elif event["rework_units"] > 0:
                disposition = "REWORK_PRESENT"
            else:
                disposition = "PASS"
            inspections.append(
                {
                    "inspection_id": f"INSP-{event_id}",
                    "production_event_id": event_id,
                    "production_order_id": row.production_order_id,
                    "inspection_timestamp": end_ts + pd.Timedelta(minutes=10),
                    "plant_id": row.plant_id,
                    "line_id": row.line_id,
                    "machine_id": row.machine_id,
                    "product_id": row.product_id,
                    "shift_id": shift_id,
                    "inspection_result": "PASS" if event["defect_units"] == 0 else "DEFECT_DETECTED",
                    "defect_units": event["defect_units"],
                    "rework_units": event["rework_units"],
                    "scrap_units": event["scrap_units"],
                    "disposition": disposition,
                    "specification_status": "NO_SPEC_LIMITS_IN_PROTOTYPE",
                }
            )
    return {
        "fact_production_event": pd.DataFrame(events),
        "fact_inspection_event": pd.DataFrame(inspections),
    }


def _supply_inventory_prototype(
    frames: dict[str, pd.DataFrame],
    structural: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    supply = frames["fact_supply"].copy()
    supply["month"] = pd.to_datetime(supply["month"])
    recent_months = sorted(supply["month"].unique())[-3:]
    supply = supply[supply["month"].isin(recent_months)].copy()

    suppliers = frames["dim_supplier"].set_index("supplier_id")
    materials = structural["dim_material"]
    warehouses = structural["dim_warehouse"]
    material_ids = list(materials["material_id"])
    warehouse_ids = list(warehouses["warehouse_id"])

    po_rows = []
    receipt_rows = []
    po_counter = 1
    receipt_counter = 1
    for row in supply.itertuples(index=False):
        selected = [
            material_ids[_stable_index(row.supplier_id, row.month, "m1", n=len(material_ids))],
            material_ids[_stable_index(row.supplier_id, row.month, "m2", n=len(material_ids))],
        ]
        ordered_split = _split_integer(int(row.ordered_qty), [0.6, 0.4])
        received_split = _split_integer(int(row.received_qty), [0.6, 0.4])
        defect_split = _split_integer(int(row.material_defects), [0.6, 0.4])
        source_key = f"{pd.Timestamp(row.month):%Y-%m}|{row.supplier_id}"
        base_lead = int(suppliers.loc[row.supplier_id, "base_lead_time_days"])
        for idx, material_id in enumerate(selected):
            po_line_id = f"POL{po_counter:07d}"
            order_date = pd.Timestamp(row.month) + pd.Timedelta(days=2 + idx * 8)
            promised_date = order_date + pd.Timedelta(days=base_lead)
            actual_receipt = promised_date + pd.Timedelta(days=int(round(float(row.avg_late_days))))
            warehouse_id = warehouse_ids[_stable_index(row.supplier_id, material_id, n=len(warehouse_ids))]
            po_rows.append(
                {
                    "po_line_id": po_line_id,
                    "source_supply_key": source_key,
                    "supplier_id": row.supplier_id,
                    "material_id": material_id,
                    "order_date": order_date.date(),
                    "promised_date": promised_date.date(),
                    "ordered_qty": ordered_split[idx],
                    "expected_received_qty": received_split[idx],
                    "expected_material_defects": defect_split[idx],
                    "source_supplier_reliability": float(row.supplier_reliability),
                    "generation_assumption": "Two prototype PO lines deterministically split from canonical monthly supplier fact.",
                }
            )
            receipt_rows.append(
                {
                    "receipt_id": f"RCV{receipt_counter:07d}",
                    "po_line_id": po_line_id,
                    "material_lot_id": f"LOT-{po_line_id}",
                    "supplier_id": row.supplier_id,
                    "material_id": material_id,
                    "warehouse_id": warehouse_id,
                    "actual_receipt_date": actual_receipt.date(),
                    "received_qty": received_split[idx],
                    "material_defects": defect_split[idx],
                    "quality_result": "HOLD_REVIEW" if defect_split[idx] > 0 else "PASS",
                    "prototype_status": PROTOTYPE_SCOPE,
                }
            )
            po_counter += 1
            receipt_counter += 1

    purchase_orders = pd.DataFrame(po_rows)
    receipts = pd.DataFrame(receipt_rows)

    production_events = structural["fact_production_event"].copy()
    production_events["event_date"] = pd.to_datetime(production_events["event_date"])
    product_material = structural["bridge_product_material"]
    warehouse_by_plant = structural["dim_warehouse"].set_index("plant_id")["warehouse_id"].to_dict()

    prod_material = production_events[
        ["production_event_id", "event_date", "plant_id", "product_id", "total_count"]
    ].merge(product_material[["product_id", "material_id", "quantity_per_unit"]], on="product_id", how="left")
    prod_material["warehouse_id"] = prod_material["plant_id"].map(warehouse_by_plant)
    prod_material["month"] = prod_material["event_date"].dt.to_period("M").dt.to_timestamp()
    prod_material["raw_material_demand"] = prod_material["total_count"] * prod_material["quantity_per_unit"]
    demand = (
        prod_material.groupby(["warehouse_id", "material_id", "month"], as_index=False)["raw_material_demand"]
        .sum()
    )
    # Prototype scaling keeps the ledger compact while retaining cross-domain production-pressure behavior.
    demand["demand_proxy_qty"] = np.ceil(demand["raw_material_demand"] * 0.02).astype(int)

    receipts_work = receipts.copy()
    receipts_work["month"] = pd.to_datetime(receipts_work["actual_receipt_date"]).dt.to_period("M").dt.to_timestamp()
    receipt_agg = (
        receipts_work.groupby(["warehouse_id", "material_id", "month"], as_index=False)["received_qty"].sum()
    )

    months = sorted(set(recent_months) | set(receipt_agg["month"].unique()) | set(demand["month"].unique()))
    movement_rows = []
    snapshot_rows = []
    movement_counter = 1

    demand_lookup = demand.set_index(["warehouse_id", "material_id", "month"])["demand_proxy_qty"].to_dict()
    receipt_lookup = receipt_agg.set_index(["warehouse_id", "material_id", "month"])["received_qty"].to_dict()

    for warehouse_id in warehouse_ids:
        for material_id in material_ids:
            opening = 800 + 25 * _stable_index(warehouse_id, material_id, "opening", n=9)
            for month in months:
                month = pd.Timestamp(month)
                receipt_qty = int(receipt_lookup.get((warehouse_id, material_id, month), 0))
                demand_qty = int(demand_lookup.get((warehouse_id, material_id, month), 0))
                adjustment = [-5, 0, 5][_stable_index(warehouse_id, material_id, month, "adj", n=3)]
                pre_consumption = max(0, opening + receipt_qty + adjustment)
                consumption_qty = int(min(demand_qty, pre_consumption))
                closing = int(opening + receipt_qty - consumption_qty + adjustment)
                if closing < 0:
                    adjustment += -closing
                    closing = 0
                shortage_qty = max(demand_qty - consumption_qty, 0)
                safety_stock = 300 + 20 * _stable_index(material_id, "safety", n=8)
                reorder_point = int(safety_stock * 1.5)

                event_date = month + pd.offsets.MonthEnd(0)
                for movement_type, quantity in (
                    ("RECEIPT", receipt_qty),
                    ("CONSUMPTION", -consumption_qty),
                    ("ADJUSTMENT", adjustment),
                ):
                    if quantity == 0:
                        continue
                    movement_rows.append(
                        {
                            "inventory_movement_id": f"IM{movement_counter:08d}",
                            "warehouse_id": warehouse_id,
                            "material_id": material_id,
                            "movement_date": event_date.date(),
                            "movement_type": movement_type,
                            "signed_quantity": int(quantity),
                            "prototype_status": PROTOTYPE_SCOPE,
                        }
                    )
                    movement_counter += 1

                snapshot_rows.append(
                    {
                        "inventory_snapshot_id": f"IS-{warehouse_id}-{material_id}-{month:%Y%m}",
                        "warehouse_id": warehouse_id,
                        "material_id": material_id,
                        "month": month.date(),
                        "opening_balance": int(opening),
                        "receipt_qty": receipt_qty,
                        "consumption_qty": consumption_qty,
                        "adjustment_qty": int(adjustment),
                        "closing_balance": closing,
                        "demand_proxy_qty": demand_qty,
                        "shortage_qty": shortage_qty,
                        "safety_stock": safety_stock,
                        "reorder_point": reorder_point,
                        "stockout_flag": int(shortage_qty > 0),
                        "below_safety_stock_flag": int(closing < safety_stock),
                        "excess_inventory_flag": int(closing > reorder_point * 2),
                        "generation_assumption": "Prototype demand proxy is production-linked and scaled; not observed enterprise inventory.",
                    }
                )
                opening = closing

    return {
        "fact_purchase_order": purchase_orders,
        "fact_receipt": receipts,
        "fact_inventory_movement": pd.DataFrame(movement_rows),
        "fact_inventory_snapshot": pd.DataFrame(snapshot_rows),
    }


def _fulfillment_events(frames: dict[str, pd.DataFrame], lookback_days: int = 60) -> pd.DataFrame:
    orders = frames["fact_orders"].copy()
    shipments = frames["fact_shipment"].copy()
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    shipments["ship_date"] = pd.to_datetime(shipments["ship_date"])
    shipments["actual_delivery_date"] = pd.to_datetime(shipments["actual_delivery_date"])
    cutoff = orders["order_date"].max() - pd.Timedelta(days=max(1, lookback_days - 1))
    joined = orders[orders["order_date"] >= cutoff].merge(
        shipments[
            [
                "shipment_id",
                "order_id",
                "customer_id",
                "ship_date",
                "actual_delivery_date",
            ]
        ],
        on=["order_id", "customer_id"],
        how="inner",
    )

    rows = []
    counter = 1
    for row in joined.itertuples(index=False):
        for event_type, timestamp in (
            ("Order Created", pd.Timestamp(row.order_date) + pd.Timedelta(hours=9)),
            ("Shipped", pd.Timestamp(row.ship_date) + pd.Timedelta(hours=12)),
            ("Delivered", pd.Timestamp(row.actual_delivery_date) + pd.Timedelta(hours=16)),
        ):
            rows.append(
                {
                    "fulfillment_event_id": f"FE{counter:08d}",
                    "case_id": row.order_id,
                    "order_id": row.order_id,
                    "shipment_id": row.shipment_id,
                    "customer_id": row.customer_id,
                    "product_id": row.product_id,
                    "event_type": event_type,
                    "event_timestamp": timestamp,
                    "scope": "ORDER_FULFILLMENT_ONLY",
                }
            )
            counter += 1
    return pd.DataFrame(rows)


def build_prototype(
    frames: dict[str, pd.DataFrame],
    *,
    lookback_days: int = 45,
) -> dict[str, pd.DataFrame]:
    """Build a compact structural prototype without changing canonical source/BI tables."""
    geo = _geo_dimensions(frames)
    structural = {}
    structural.update(geo)
    structural.update(_warehouses_and_materials(frames, geo))
    structural.update(_workforce_prototype(frames))
    structural.update(_split_production_events(frames, lookback_days=lookback_days))
    structural.update(_supply_inventory_prototype(frames, structural))
    structural["fact_order_fulfillment_event"] = _fulfillment_events(frames, lookback_days=max(lookback_days, 60))
    return structural


def build_relationship_contract() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "child_table": rel.child_table,
                "child_key": rel.child_key,
                "parent_table": rel.parent_table,
                "parent_key": rel.parent_key,
                "relationship_status": "PROTOTYPE_ONLY_NOT_POWER_BI_PROMOTED",
            }
            for rel in RELATIONSHIPS
        ]
    )


def build_table_contract(prototype: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for table, meta in TABLE_CONTRACTS.items():
        rows.append(
            {
                "table": table,
                "business_purpose": meta["purpose"],
                "grain": meta["grain"],
                "primary_key": meta["pk"],
                "row_count": int(len(prototype[table])),
                "source": "synthetic prototype derived from validated MEDNEXUS baseline",
                "refresh_frequency": "prototype on demand",
                "transformation_logic": "rule-driven deterministic Phase 12E prototype",
                "promotion_status": "PROTOTYPE_NOT_CANONICAL",
            }
        )
    return pd.DataFrame(rows)


def _add_check(rows: list[dict], check: str, passed: bool, category: str, detail: str = "") -> None:
    rows.append(
        {
            "check": check,
            "category": category,
            "passed": bool(passed),
            "status": "PASS" if passed else "FAIL",
            "detail": detail,
        }
    )


def validate_prototype(
    canonical_frames: dict[str, pd.DataFrame],
    prototype: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    checks: list[dict] = []

    _add_check(
        checks,
        "table_contract_complete",
        set(TABLE_CONTRACTS) == set(prototype),
        "contract",
        f"expected={len(TABLE_CONTRACTS)} actual={len(prototype)}",
    )

    for table, meta in TABLE_CONTRACTS.items():
        df = prototype[table]
        pk = meta["pk"]
        valid = pk in df.columns and df[pk].notna().all() and not df[pk].duplicated().any()
        _add_check(checks, f"{table}_primary_key", valid, "integrity", pk)

    for rel in RELATIONSHIPS:
        child = prototype[rel.child_table]
        parent = prototype[rel.parent_table]
        nonblank = child[rel.child_key].dropna()
        nonblank = nonblank[nonblank.astype(str) != ""]
        passed = nonblank.isin(parent[rel.parent_key].dropna()).all()
        _add_check(
            checks,
            f"fk_{rel.child_table}_{rel.child_key}",
            bool(passed),
            "referential_integrity",
            f"{rel.parent_table}.{rel.parent_key}",
        )

    for table in ("dim_plant_geo", "dim_supplier_geo", "dim_customer_geo", "dim_warehouse"):
        df = prototype[table]
        passed = (
            df["latitude"].between(-90, 90).all()
            and df["longitude"].between(-180, 180).all()
            and df["geography_status"].eq("SIMULATED_ENTERPRISE_FOOTPRINT").all()
        )
        _add_check(checks, f"{table}_geography_valid", bool(passed), "geospatial")

    # Production shift events must reconcile exactly back to the selected canonical daily production rows.
    prod_event = prototype["fact_production_event"]
    canonical_prod = canonical_frames["fact_production"].copy()
    selected_orders = set(prod_event["production_order_id"])
    canonical_prod = canonical_prod[canonical_prod["production_order_id"].isin(selected_orders)].set_index("production_order_id")
    event_agg = prod_event.groupby("production_order_id")[
        [
            "planned_production_min",
            "planned_downtime_min",
            "unplanned_downtime_min",
            "run_time_min",
            "total_count",
            "good_count",
            "defect_units",
            "rework_units",
            "scrap_units",
        ]
    ].sum()
    numeric_reconciles = True
    for column in event_agg.columns:
        numeric_reconciles = numeric_reconciles and np.allclose(
            event_agg[column].sort_index().to_numpy(),
            canonical_prod.loc[event_agg.index, column].to_numpy(),
        )
    _add_check(checks, "production_event_reconciles_to_canonical", bool(numeric_reconciles), "reconciliation")

    inspections = prototype["fact_inspection_event"].set_index("production_event_id")
    production_indexed = prod_event.set_index("production_event_id")
    inspection_ok = (
        inspections.index.equals(production_indexed.index)
        and (inspections["inspection_timestamp"] > production_indexed["event_end"]).all()
        and (inspections["defect_units"] == production_indexed["defect_units"]).all()
        and (inspections["rework_units"] == production_indexed["rework_units"]).all()
        and (inspections["scrap_units"] == production_indexed["scrap_units"]).all()
    )
    _add_check(checks, "inspection_linkage_and_chronology", bool(inspection_ok), "chronology")

    # PO prototype must reconcile to the monthly supplier quantities it disaggregates.
    po = prototype["fact_purchase_order"]
    po_group = po.groupby("source_supply_key")[["ordered_qty", "expected_received_qty", "expected_material_defects"]].sum()
    supply = canonical_frames["fact_supply"].copy()
    supply["month"] = pd.to_datetime(supply["month"])
    supply["source_supply_key"] = supply["month"].dt.strftime("%Y-%m") + "|" + supply["supplier_id"]
    source = supply[supply["source_supply_key"].isin(po_group.index)].set_index("source_supply_key")
    po_ok = (
        (po_group["ordered_qty"] == source.loc[po_group.index, "ordered_qty"]).all()
        and (po_group["expected_received_qty"] == source.loc[po_group.index, "received_qty"]).all()
        and (po_group["expected_material_defects"] == source.loc[po_group.index, "material_defects"]).all()
    )
    _add_check(checks, "purchase_orders_reconcile_to_supply_source", bool(po_ok), "reconciliation")

    snapshots = prototype["fact_inventory_snapshot"]
    balance = (
        snapshots["opening_balance"]
        + snapshots["receipt_qty"]
        - snapshots["consumption_qty"]
        + snapshots["adjustment_qty"]
    )
    _add_check(
        checks,
        "inventory_balance_equation",
        bool((balance == snapshots["closing_balance"]).all()),
        "inventory",
        "opening + receipts - consumption +/- adjustments = closing",
    )
    _add_check(
        checks,
        "inventory_nonnegative_closing",
        bool((snapshots["closing_balance"] >= 0).all()),
        "inventory",
    )

    movements = prototype["fact_inventory_movement"].copy()
    movements["month"] = pd.to_datetime(movements["movement_date"]).dt.to_period("M").dt.to_timestamp()
    move_agg = movements.groupby(["warehouse_id", "material_id", "month"])["signed_quantity"].sum()
    snapshots_keyed = snapshots.copy()
    snapshots_keyed["month"] = pd.to_datetime(snapshots_keyed["month"]).dt.to_period("M").dt.to_timestamp()
    snapshots_keyed = snapshots_keyed.set_index(["warehouse_id", "material_id", "month"])
    delta = snapshots_keyed["closing_balance"] - snapshots_keyed["opening_balance"]
    aligned_movements = move_agg.reindex(delta.index, fill_value=0)
    _add_check(
        checks,
        "inventory_movement_reconciles_to_snapshot_delta",
        bool((aligned_movements == delta).all()),
        "inventory",
    )

    candidates = prototype["fact_candidate_event"].sort_values(["candidate_id", "event_timestamp"])
    stage_rank = {"Application": 1, "Screening": 2, "Interview": 3, "Assessment": 4, "Offer": 5, "Acceptance": 6, "Onboarding": 7}
    candidate_ok = True
    for _, group in candidates.groupby("candidate_id"):
        ranks = group["stage"].map(stage_rank).to_numpy()
        times = pd.to_datetime(group["event_timestamp"]).to_numpy()
        candidate_ok = candidate_ok and bool(np.all(np.diff(ranks) > 0))
        candidate_ok = candidate_ok and bool(np.all(np.diff(times) > np.timedelta64(0, "ns")))
    _add_check(checks, "candidate_event_ordering", candidate_ok, "chronology")

    fulfillment = prototype["fact_order_fulfillment_event"].sort_values(["case_id", "event_timestamp"])
    expected_sequence = ["Order Created", "Shipped", "Delivered"]
    fulfillment_ok = fulfillment.groupby("case_id")["event_type"].apply(list).map(lambda x: x == expected_sequence).all()
    _add_check(checks, "order_fulfillment_event_ordering", bool(fulfillment_ok), "chronology")

    # The full manufacturing process case remains fail-closed until the generator creates explicit order→production linkage.
    _add_check(
        checks,
        "full_process_mining_gate_fail_closed",
        True,
        "methodology_gate",
        "NOT_ADMITTED: no explicit customer_order_id on canonical production orders.",
    )

    total_rows = sum(len(df) for df in prototype.values())
    _add_check(
        checks,
        "prototype_volume_manageable",
        total_rows < 100_000,
        "performance",
        f"prototype_rows={total_rows}",
    )

    return pd.DataFrame(checks)


def assumptions() -> dict:
    return {
        "prototype_version": PROTOTYPE_VERSION,
        "status": PROTOTYPE_SCOPE,
        "causal_status": "Synthetic generation assumptions are not empirical causal findings.",
        "geography": "Coordinates are simulated representative enterprise locations for analytical map testing.",
        "workforce": "Roles, shifts and line assignments are deterministic synthetic prototype enrichments.",
        "recruitment": "Vacancies/candidate stages are prototype disaggregation rules, not observed applicant histories.",
        "production": "Canonical daily production orders are split into two shift events and must reaggregate exactly.",
        "quality": "One inspection event is created per prototype production event; no specification limits are invented.",
        "supply": "Canonical monthly supplier quantities are deterministically split into two prototype PO lines and reconcile exactly.",
        "inventory": "Inventory demand is a scaled production-linked proxy constrained by physical availability; balances must reconcile and never become negative.",
        "process": "Order fulfillment only is admitted. Full Order→Production→Inspection→Rework→Release→Shipment→Delivery process mining remains gated until explicit order-production linkage exists.",
        "power_bi": "No prototype relationship is promoted to the canonical Power BI model in Phase 12E.",
    }


def run_phase12e(seed: int | None = None) -> dict:
    frames = generate(seed=seed)
    prototype = build_prototype(frames)
    validations = validate_prototype(frames, prototype)
    contract = build_table_contract(prototype)
    relationships = build_relationship_contract()

    prototype_dir = path("data", "prototype")
    validation_dir = path("artifacts", "validation")
    prototype_dir.mkdir(parents=True, exist_ok=True)
    validation_dir.mkdir(parents=True, exist_ok=True)

    for name, df in prototype.items():
        save_frame(df, prototype_dir / f"{name}.csv")

    save_frame(contract, validation_dir / "phase12e_table_contract.csv")
    save_frame(relationships, validation_dir / "phase12e_relationship_contract.csv")
    save_frame(validations, validation_dir / "phase12e_validation_checks.csv")

    volume = pd.DataFrame(
        [
            {
                "table": name,
                "row_count": int(len(df)),
                "column_count": int(df.shape[1]),
                "approx_memory_bytes": int(df.memory_usage(index=True, deep=True).sum()),
                "promotion_status": "PROTOTYPE_NOT_CANONICAL",
            }
            for name, df in prototype.items()
        ]
    )
    save_frame(volume, validation_dir / "phase12e_volume_profile.csv")
    write_json(assumptions(), validation_dir / "phase12e_generation_assumptions.json")

    failed = validations[validations["status"] != "PASS"]
    summary = {
        "phase": "12E",
        "prototype_version": PROTOTYPE_VERSION,
        "status": "PASS" if failed.empty else "FAIL",
        "canonical_semantic_model_changed": False,
        "canonical_powerbi_export_contract_changed": False,
        "prototype_table_count": len(prototype),
        "prototype_row_count": int(volume["row_count"].sum()),
        "validation_check_count": int(len(validations)),
        "validation_failure_count": int(len(failed)),
        "full_process_mining_status": "NOT_ADMITTED_NO_EXPLICIT_ORDER_PRODUCTION_LINK",
        "next_gate": "Review prototype evidence before promotion into canonical generator/semantic model.",
    }
    write_json(summary, validation_dir / "phase12e_summary.json")
    if not failed.empty:
        raise RuntimeError(
            "Phase 12E prototype validation failed: "
            + ", ".join(failed["check"].astype(str).tolist())
        )
    return summary


if __name__ == "__main__":
    result = run_phase12e()
    print(result)
