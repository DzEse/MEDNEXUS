import pandas as pd
from mednexus.analytics import production_kpis


def test_oee_formula():
    df=pd.DataFrame([{'planned_production_min':100,'planned_downtime_min':0,'run_time_min':80,'ideal_cycle_min':1,'total_count':72,'good_count':68,'defect_units':4,'rework_units':2,'scrap_units':2}])
    out=production_kpis(df).iloc[0]
    expected=(80/100)*(72/80)*(68/72)
    assert abs(out['oee']-expected)<1e-9


def test_oli_is_bounded():
    df=pd.DataFrame([{'planned_production_min':100,'planned_downtime_min':5,'run_time_min':80,'ideal_cycle_min':2,'total_count':35,'good_count':34,'defect_units':1,'rework_units':0,'scrap_units':1}])
    out=production_kpis(df).iloc[0]
    assert 0 <= out['oli'] <= 1
