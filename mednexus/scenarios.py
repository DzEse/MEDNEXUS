from __future__ import annotations
import pandas as pd


def run_scenarios(mart: pd.DataFrame):
    base=mart.iloc[-1]
    scenarios=[
        ('Baseline',0,0,0),
        ('Targeted reliability',15,0,0),
        ('Quality improvement',0,12,0),
        ('Workforce recovery',0,0,5),
        ('Combined intervention',15,12,5),
    ]
    rows=[]
    for name,dt_red,def_red,wf_change in scenarios:
        downtime=base['unplanned_downtime_min']*(1-dt_red/100)
        defects=base['defect_units']*(1-def_red/100)
        capacity_gap=max(0,base['capacity_gap_pct']-wf_change/100)
        # Transparent scenario relationships, not causal claims.
        throughput_gain=(dt_red*0.20 + def_red*0.08 + wf_change*0.35)/100
        good_units=base['good_units']*(1+throughput_gain)
        simulated_value=(base['downtime_cost']*(dt_red/100)) + (base['scrap_cost']*(def_red/100))
        rows.append((name,dt_red,def_red,wf_change,downtime,defects,capacity_gap,good_units,simulated_value))
    return pd.DataFrame(rows,columns=['scenario','downtime_reduction_pct','defect_reduction_pct','workforce_capacity_change_pct','simulated_downtime_min','simulated_defect_units','simulated_capacity_gap_pct','simulated_good_units','simulated_opportunity_value'])
