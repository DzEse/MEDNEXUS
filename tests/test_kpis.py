import pandas as pd

from mednexus.analytics import production_kpis, monthly_enterprise_mart
from mednexus.synthetic import generate


def test_oee_formula():
    df=pd.DataFrame([{'planned_production_min':100,'planned_downtime_min':0,'run_time_min':80,'ideal_cycle_min':1,'total_count':72,'good_count':68,'defect_units':4,'rework_units':2,'scrap_units':2}])
    out=production_kpis(df).iloc[0]
    expected=(80/100)*(72/80)*(68/72)
    assert abs(out['oee']-expected)<1e-9


def test_oli_is_bounded():
    df=pd.DataFrame([{'planned_production_min':100,'planned_downtime_min':5,'run_time_min':80,'ideal_cycle_min':2,'total_count':35,'good_count':34,'defect_units':1,'rework_units':0,'scrap_units':1}])
    out=production_kpis(df).iloc[0]
    assert 0 <= out['oli'] <= 1


def test_monthly_kpis_recompute_from_aggregate_components():
    frames = generate(seed=42)
    mart = monthly_enterprise_mart(frames)

    production = frames['fact_production'].copy()
    production['month'] = pd.to_datetime(production['date']).dt.to_period('M').astype(str)
    first_month = mart.iloc[0]['month']
    p = production[production['month'] == first_month]

    expected_fpy = (p['total_count'].sum() - p['defect_units'].sum()) / p['total_count'].sum()
    net_planned = (p['planned_production_min'] - p['planned_downtime_min']).sum()
    availability = p['run_time_min'].sum() / net_planned
    performance = (p['ideal_cycle_min'] * p['total_count']).sum() / p['run_time_min'].sum()
    quality = p['good_count'].sum() / p['total_count'].sum()
    expected_oee = availability * performance * quality
    expected_oli = 1 - p['good_count'].sum() / (p['planned_production_min'] / p['ideal_cycle_min']).sum()

    row = mart[mart['month'] == first_month].iloc[0]
    assert abs(row['fpy'] - expected_fpy) < 1e-12
    assert abs(row['oee'] - expected_oee) < 1e-12
    assert abs(row['oli'] - expected_oli) < 1e-12
