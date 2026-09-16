from __future__ import annotations
import numpy as np
import pandas as pd
from .config import load_config


def _ids(prefix, n):
    return [f'{prefix}{i:04d}' for i in range(1, n + 1)]


def generate(seed: int | None = None):
    cfg = load_config()
    s = cfg['simulation']
    seed = s['seed'] if seed is None else seed
    rng = np.random.default_rng(seed)

    end = pd.Timestamp('2026-08-31')
    start = end - pd.DateOffset(months=s['months']) + pd.offsets.MonthBegin(0)
    dates = pd.date_range(start, end, freq='D')
    months = pd.date_range(start.to_period('M').to_timestamp(), end.to_period('M').to_timestamp(), freq='MS')

    plants = pd.DataFrame({
        'plant_id': _ids('PL', s['plants']),
        'plant_name': [f'MEDNEXUS Plant {chr(65+i)}' for i in range(s['plants'])],
        'region': ['Ontario', 'North West England'][:s['plants']],
    })

    lines = []
    for plant in plants.itertuples(index=False):
        for j in range(s['lines_per_plant']):
            lines.append((f'{plant.plant_id}-L{j+1}', plant.plant_id, f'Line {j+1}'))
    lines = pd.DataFrame(lines, columns=['line_id', 'plant_id', 'line_name'])

    machines = []
    for line in lines.itertuples(index=False):
        for j in range(s['machines_per_line']):
            machines.append((f'{line.line_id}-M{j+1}', line.line_id, line.plant_id, f'Machine {j+1}', rng.integers(1, 12)))
    machines = pd.DataFrame(machines, columns=['machine_id', 'line_id', 'plant_id', 'machine_name', 'machine_age_years'])

    products = pd.DataFrame({
        'product_id': _ids('PR', s['products']),
        'product_family': np.resize(['Diagnostic', 'Monitoring', 'Surgical'], s['products']),
        'unit_price': rng.uniform(260, 920, s['products']).round(2),
        'ideal_cycle_min': rng.uniform(1.5, 4.8, s['products']).round(2),
        'material_cost_per_unit': rng.uniform(80, 290, s['products']).round(2),
    })

    suppliers = pd.DataFrame({
        'supplier_id': _ids('SUP', s['suppliers']),
        'supplier_name': [f'Supplier {i:02d}' for i in range(1, s['suppliers'] + 1)],
        'base_lead_time_days': rng.integers(4, 24, s['suppliers']),
        'quality_rating': rng.uniform(0.88, 0.995, s['suppliers']).round(4),
    })

    customers = pd.DataFrame({
        'customer_id': _ids('CUS', s['customers']),
        'customer_type': np.resize(['Hospital', 'Clinic', 'Distributor', 'Healthcare Organization'], s['customers']),
        'region': rng.choice(['Canada', 'UK', 'US', 'EU'], s['customers']),
    })

    departments = ['Manufacturing', 'Quality', 'Maintenance', 'Supply Chain', 'Logistics', 'Finance', 'HR', 'Technology']
    employee_ids = _ids('EMP', s['employees'])
    emp_dept = rng.choice(departments, size=s['employees'], p=[0.35,0.11,0.09,0.11,0.08,0.07,0.08,0.11])
    employees = pd.DataFrame({
        'employee_id': employee_ids,
        'department': emp_dept,
        'plant_id': rng.choice(plants['plant_id'], s['employees']),
        'skill_level': rng.choice(['Developing','Qualified','Advanced'], s['employees'], p=[0.25,0.60,0.15]),
        'hourly_cost': rng.uniform(24, 58, s['employees']).round(2),
        'active_flag': 1,
    })

    # Workforce monthly facts: staffing shortage is linked to overtime, absenteeism, and capacity pressure.
    workforce_rows = []
    for m in months:
        for plant in plants['plant_id']:
            demand_growth = 1 + 0.002 * ((m.year - months[0].year) * 12 + m.month - months[0].month)
            req = int(78 * demand_growth + rng.normal(0, 3))
            actual = int(req - max(0, rng.normal(3.5, 2.5)))
            absence = float(np.clip(rng.normal(0.045, 0.012), 0.015, 0.10))
            vacancy = max(req - actual, 0)
            overtime = float(np.clip(6 + vacancy * 1.4 + absence * 60 + rng.normal(0, 2), 2, 30))
            workforce_rows.append((m.date(), plant, req, actual, vacancy, absence, overtime))
    workforce = pd.DataFrame(workforce_rows, columns=['month','plant_id','required_headcount','actual_headcount','vacancies','absence_rate','overtime_hours_per_employee'])
    workforce['capacity_gap_pct'] = ((workforce['required_headcount'] - workforce['actual_headcount']) / workforce['required_headcount']).clip(lower=0)
    workforce['labor_cost'] = workforce['actual_headcount'] * (160 + workforce['overtime_hours_per_employee']) * 36.0

    # Recruitment monthly facts linked to vacancies.
    recruitment_rows = []
    for row in workforce.itertuples(index=False):
        openings = int(max(1, row.vacancies + rng.integers(0, 3)))
        applicants = int(openings * rng.integers(7, 15))
        screened = int(applicants * rng.uniform(0.45, 0.68))
        interviews = int(screened * rng.uniform(0.35, 0.55))
        offers = int(max(openings, interviews * rng.uniform(0.25, 0.45)))
        accepted = int(min(offers, max(0, round(offers * rng.uniform(0.70, 0.93)))))
        recruitment_rows.append((row.month,row.plant_id,openings,applicants,screened,interviews,offers,accepted,float(rng.uniform(22,58)),float(rng.uniform(1800,4200))))
    recruitment = pd.DataFrame(recruitment_rows, columns=['month','plant_id','open_positions','applicants','screened','interviews','offers','accepted','avg_time_to_fill_days','cost_per_hire'])

    # Daily production is driven by planned time, workforce availability, downtime, speed and quality.
    prod_rows=[]; down_rows=[]; qual_rows=[]; maint_rows=[]; sensor_rows=[]
    prod_id = 1; downtime_id=1; quality_id=1; maint_id=1
    workforce_lookup = workforce.set_index([pd.to_datetime(workforce['month']).dt.to_period('M'), 'plant_id'])
    for d in dates:
        wf_period = d.to_period('M')
        for machine in machines.itertuples(index=False):
            product = products.iloc[(hash(machine.machine_id + str(d.date())) % len(products))]
            wf = workforce_lookup.loc[(wf_period, machine.plant_id)]
            staffing = 1 - float(wf['capacity_gap_pct'])
            planned_min = 2 * 8 * 60
            deterioration = min(0.18, machine.machine_age_years * 0.006)
            failure_pressure = np.clip(0.025 + deterioration + rng.normal(0,0.018), 0.005, 0.30)
            unplanned_down = float(np.clip(rng.gamma(1.8, 15) * (1 + failure_pressure*2.4), 0, 240))
            planned_down = float(np.clip(rng.normal(24,6), 8, 50))
            runtime = max(planned_min - planned_down - unplanned_down, 20)
            speed_factor = float(np.clip(rng.normal(0.90 - 0.06*(1-staffing),0.04),0.67,1.0))
            theoretical = runtime / float(product['ideal_cycle_min'])
            total_count = int(max(1, theoretical * speed_factor * staffing))
            base_defect = 0.018 + 0.055*(1-staffing) + 0.00018*unplanned_down + 0.012*failure_pressure
            defect_rate = float(np.clip(base_defect + rng.normal(0,0.006),0.004,0.16))
            defect_units = int(rng.binomial(total_count, defect_rate))
            rework_units = int(rng.binomial(defect_units, 0.52)) if defect_units else 0
            scrap_units = max(defect_units - rework_units, 0)
            good_units = max(total_count - scrap_units, 0)
            prod_rows.append((f'PO{prod_id:07d}',d.date(),machine.plant_id,machine.line_id,machine.machine_id,product['product_id'],planned_min,planned_down,unplanned_down,runtime,total_count,good_units,defect_units,rework_units,scrap_units,float(product['ideal_cycle_min'])))
            prod_id += 1
            if unplanned_down > 8:
                reason = rng.choice(['Equipment Failure','Minor Stop','Setup Adjustment'], p=[0.48,0.32,0.20])
                down_rows.append((f'DT{downtime_id:07d}',d.date(),machine.machine_id,machine.line_id,machine.plant_id,reason,round(unplanned_down,2)))
                downtime_id += 1
            if defect_units > 0:
                defect_cat = rng.choice(['Dimensional','Assembly','Electrical','Surface','Functional'], p=[0.22,0.27,0.18,0.16,0.17])
                severity = rng.choice(['Minor','Major','Critical'], p=[0.62,0.33,0.05])
                qual_rows.append((f'Q{quality_id:07d}',d.date(),machine.machine_id,machine.line_id,machine.plant_id,product['product_id'],defect_cat,severity,defect_units,rework_units,scrap_units))
                quality_id += 1
            # Maintenance events are more likely with age and failure pressure.
            if rng.random() < (0.025 + failure_pressure*0.20):
                mtype = rng.choice(['Preventive','Corrective'], p=[0.62,0.38])
                duration = float(np.clip(rng.gamma(2.2,18) * (1.5 if mtype=='Corrective' else 0.8), 10, 240))
                maint_rows.append((f'MT{maint_id:07d}',d.date(),machine.machine_id,mtype,duration,rng.choice(['Bearing','Drive','Sensor','Calibration','Electrical'])))
                maint_id += 1
            # Aggregate daily sensor snapshot for predictive maintenance.
            temp = 62 + machine.machine_age_years*0.55 + failure_pressure*34 + rng.normal(0,2.8)
            torque = 39 + failure_pressure*16 + rng.normal(0,3.5)
            vibration = 2.1 + machine.machine_age_years*0.04 + failure_pressure*3.2 + rng.normal(0,0.25)
            tool_wear = 25 + (d - dates[0]).days*0.08 + machine.machine_age_years*2 + rng.normal(0,7)
            failure_prob = float(np.clip(0.008 + 0.30*failure_pressure + 0.012*max(temp-68,0) + 0.045*max(vibration-2.8,0) + 0.0007*max(tool_wear-70,0), 0.005, 0.55))
            failure_next_7d = int(rng.random() < failure_prob)
            sensor_rows.append((d.date(),machine.machine_id,machine.plant_id,machine.line_id,temp,torque,vibration,max(tool_wear,0),failure_next_7d))

    production = pd.DataFrame(prod_rows, columns=['production_order_id','date','plant_id','line_id','machine_id','product_id','planned_production_min','planned_downtime_min','unplanned_downtime_min','run_time_min','total_count','good_count','defect_units','rework_units','scrap_units','ideal_cycle_min'])
    downtime = pd.DataFrame(down_rows, columns=['downtime_event_id','date','machine_id','line_id','plant_id','downtime_reason','duration_min'])
    quality = pd.DataFrame(qual_rows, columns=['quality_event_id','date','machine_id','line_id','plant_id','product_id','defect_category','severity','defect_units','rework_units','scrap_units'])
    maintenance = pd.DataFrame(maint_rows, columns=['maintenance_event_id','date','machine_id','maintenance_type','duration_min','failure_mode'])
    sensor = pd.DataFrame(sensor_rows, columns=['date','machine_id','plant_id','line_id','temperature_c','torque_nm','vibration_mm_s','tool_wear_index','failure_next_7d'])

    # Precompute rolling daily downtime pressure for downstream logistics; avoids repeated full-table scans.
    _daily_down = production.copy()
    _daily_down['date'] = pd.to_datetime(_daily_down['date'])
    _daily_down = _daily_down.groupby('date')['unplanned_downtime_min'].mean().sort_index()
    _rolling_pressure = (_daily_down.rolling(3, min_periods=1).mean() / 120.0).to_dict()

    # Supply-chain monthly facts. Late materials are connected to supplier reliability and shortage hours.
    supply_rows=[]
    for m in months:
        for sup in suppliers.itertuples(index=False):
            ordered = int(rng.integers(900, 3200))
            reliability = float(np.clip(0.93 - sup.base_lead_time_days*0.002 + rng.normal(0,0.025),0.70,0.995))
            received = int(ordered * np.clip(reliability + rng.normal(0,0.02),0.72,1.0))
            defect_material = int(received * np.clip(1-sup.quality_rating + rng.normal(0,0.004),0,0.08))
            late_days = float(max(0, rng.normal((1-reliability)*18,2.0)))
            shortage_hours = float(max(0, (ordered-received)/max(ordered,1)*95 + late_days*1.7 + rng.normal(0,2)))
            supply_rows.append((m.date(),sup.supplier_id,ordered,received,defect_material,late_days,reliability,shortage_hours))
    supply = pd.DataFrame(supply_rows, columns=['month','supplier_id','ordered_qty','received_qty','material_defects','avg_late_days','supplier_reliability','shortage_hours'])

    # Orders / shipment / customer service.
    order_rows=[]; ship_rows=[]; service_rows=[]
    order_id=1
    for d in dates:
        daily_n = int(rng.poisson(15.5))
        for _ in range(daily_n):
            product = products.iloc[rng.integers(0,len(products))]
            customer = customers.iloc[rng.integers(0,len(customers))]
            qty = int(rng.integers(80,450))
            promised = d + pd.Timedelta(days=int(rng.integers(3,9)))
            # Shipment delay linked to three-day rolling production downtime pressure.
            pressure = float(_rolling_pressure.get(d, 0.0))
            delay = int(max(0, round(rng.normal(pressure*1.2,0.9))))
            shipped = d + pd.Timedelta(days=int(rng.integers(1,4)))
            delivered = promised + pd.Timedelta(days=delay)
            revenue = qty * float(product['unit_price'])
            oid=f'ORD{order_id:07d}'
            order_rows.append((oid,d.date(),customer['customer_id'],product['product_id'],qty,float(product['unit_price']),revenue,promised.date()))
            ship_rows.append((f'SHP{order_id:07d}',oid,customer['customer_id'],shipped.date(),promised.date(),delivered.date(),delay,int(delay==0),float(rng.uniform(70,280))))
            tickets = int(rng.poisson(0.15 + delay*0.12))
            if tickets:
                service_rows.append((f'CS{order_id:07d}',oid,customer['customer_id'],delivered.date(),tickets,rng.choice(['Delivery','Product','Documentation','Support'])))
            order_id += 1
    orders = pd.DataFrame(order_rows, columns=['order_id','order_date','customer_id','product_id','quantity','unit_price','revenue','promised_date'])
    shipments = pd.DataFrame(ship_rows, columns=['shipment_id','order_id','customer_id','ship_date','promised_date','actual_delivery_date','delay_days','on_time_flag','logistics_cost'])
    customer_service = pd.DataFrame(service_rows, columns=['service_event_id','order_id','customer_id','date','ticket_count','issue_type'])

    # Technology incidents and usage.
    tech_rows=[]; usage_rows=[]
    systems=['ERP','MES','QMS','WMS','Analytics Platform']
    for d in dates:
        for sys in systems:
            incident_n = rng.poisson(0.09 if sys!='MES' else 0.14)
            if incident_n:
                for _ in range(incident_n):
                    duration=float(np.clip(rng.gamma(1.8,32),5,420))
                    sev=rng.choice(['P1','P2','P3'],p=[0.08,0.34,0.58])
                    tech_rows.append((d.date(),sys,sev,duration,int(duration>120),rng.choice(['Deployment','Infrastructure','Data Pipeline','Application'])))
            usage_rows.append((d.date(),sys,int(rng.integers(45,220)),float(np.clip(rng.normal(0.91,0.045),0.72,0.995))))
    technology = pd.DataFrame(tech_rows, columns=['date','system_name','severity','duration_min','major_incident_flag','incident_type'])
    saas_usage = pd.DataFrame(usage_rows, columns=['date','system_name','active_users','adoption_rate'])

    # Finance monthly is reconciled from operational facts plus documented synthetic overhead.
    finance_rows=[]
    for m in months:
        period = pd.Period(m, freq='M')
        o = orders[pd.to_datetime(orders['order_date']).dt.to_period('M')==period]
        p = production[pd.to_datetime(production['date']).dt.to_period('M')==period]
        sh = shipments[pd.to_datetime(shipments['ship_date']).dt.to_period('M')==period]
        wf = workforce[pd.to_datetime(workforce['month']).dt.to_period('M')==period]
        tech = technology[pd.to_datetime(technology['date']).dt.to_period('M')==period]
        revenue = float(o['revenue'].sum())
        material = float((p.merge(products[['product_id','material_cost_per_unit']], on='product_id')['good_count'] * p.merge(products[['product_id','material_cost_per_unit']], on='product_id')['material_cost_per_unit']).sum())
        labor = float(wf['labor_cost'].sum())
        scrap_cost = float((p.merge(products[['product_id','material_cost_per_unit']], on='product_id')['scrap_units'] * p.merge(products[['product_id','material_cost_per_unit']], on='product_id')['material_cost_per_unit']).sum())
        logistics_cost=float(sh['logistics_cost'].sum())
        downtime_cost=float(p['unplanned_downtime_min'].sum()*12.0)  # Illustrative financial assumption: $12/min proxy.
        technology_cost=float(120000 + tech['duration_min'].sum()*18.0)  # Illustrative assumption.
        overhead=float(300000 + rng.normal(0,22000))
        operating_cost=material+labor+scrap_cost+logistics_cost+downtime_cost+technology_cost+overhead
        budget_cost=operating_cost*rng.uniform(0.96,1.03)
        finance_rows.append((m.date(),revenue,material,labor,scrap_cost,logistics_cost,downtime_cost,technology_cost,overhead,operating_cost,budget_cost))
    finance=pd.DataFrame(finance_rows,columns=['month','revenue','material_cost','labor_cost','scrap_cost','logistics_cost','downtime_cost','technology_cost','overhead_cost','operating_cost','budget_operating_cost'])
    finance['gross_margin_proxy']=finance['revenue']-finance['material_cost']-finance['labor_cost']
    finance['operating_margin_proxy']=finance['revenue']-finance['operating_cost']
    finance['budget_variance']=finance['operating_cost']-finance['budget_operating_cost']

    return {
        'dim_plant': plants,
        'dim_line': lines,
        'dim_machine': machines,
        'dim_product': products,
        'dim_supplier': suppliers,
        'dim_customer': customers,
        'dim_employee': employees,
        'fact_workforce': workforce,
        'fact_recruitment': recruitment,
        'fact_production': production,
        'fact_downtime': downtime,
        'fact_quality': quality,
        'fact_maintenance': maintenance,
        'fact_sensor': sensor,
        'fact_supply': supply,
        'fact_orders': orders,
        'fact_shipment': shipments,
        'fact_customer_service': customer_service,
        'fact_technology_incident': technology,
        'fact_saas_usage': saas_usage,
        'fact_finance': finance,
    }
