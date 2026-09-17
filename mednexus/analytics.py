from __future__ import annotations
import numpy as np
import pandas as pd


def production_kpis(production: pd.DataFrame):
    p=production.copy()
    p['availability']=p['run_time_min']/(p['planned_production_min']-p['planned_downtime_min']).clip(lower=1)
    p['performance']=(p['ideal_cycle_min']*p['total_count']/p['run_time_min'].clip(lower=1)).clip(0,1.2)
    p['quality_rate']=p['good_count']/p['total_count'].clip(lower=1)
    p['oee']=(p['availability']*p['performance']*p['quality_rate']).clip(0,1)
    p['fpy']=(p['total_count']-p['defect_units'])/p['total_count'].clip(lower=1)
    # Backward-compatible alias retained for earlier artifacts; canonical KPI name is now FPY.
    p['fpy_proxy']=p['fpy']
    p['defect_rate']=p['defect_units']/p['total_count'].clip(lower=1)
    theoretical=p['planned_production_min']/p['ideal_cycle_min'].clip(lower=.01)
    p['oli']=(1-p['good_count']/theoretical.clip(lower=1)).clip(0,1)
    return p


def monthly_enterprise_mart(frames):
    p=production_kpis(frames['fact_production'])
    p['month']=pd.to_datetime(p['date']).dt.to_period('M').astype(str)
    p['net_planned_min']=(p['planned_production_min']-p['planned_downtime_min']).clip(lower=0)
    p['ideal_time_min']=p['ideal_cycle_min']*p['total_count']
    p['theoretical_units']=p['planned_production_min']/p['ideal_cycle_min'].clip(lower=.01)
    pm=p.groupby('month',as_index=False).agg(
        total_units=('total_count','sum'),
        good_units=('good_count','sum'),
        defect_units=('defect_units','sum'),
        scrap_units=('scrap_units','sum'),
        unplanned_downtime_min=('unplanned_downtime_min','sum'),
        run_time_min=('run_time_min','sum'),
        net_planned_min=('net_planned_min','sum'),
        ideal_time_min=('ideal_time_min','sum'),
        theoretical_units=('theoretical_units','sum'),
    )
    pm['availability']=pm['run_time_min']/pm['net_planned_min'].replace(0,np.nan)
    pm['performance']=pm['ideal_time_min']/pm['run_time_min'].replace(0,np.nan)
    pm['quality_rate']=pm['good_units']/pm['total_units'].replace(0,np.nan)
    pm['oee']=(pm['availability']*pm['performance']*pm['quality_rate']).clip(0,1)
    pm['fpy']=(pm['total_units']-pm['defect_units'])/pm['total_units'].replace(0,np.nan)
    pm['oli']=(1-pm['good_units']/pm['theoretical_units'].replace(0,np.nan)).clip(0,1)
    f=frames['fact_finance'].copy(); f['month']=pd.to_datetime(f['month']).dt.to_period('M').astype(str)
    wf=frames['fact_workforce'].copy(); wf['month']=pd.to_datetime(wf['month']).dt.to_period('M').astype(str)
    wm=wf.groupby('month',as_index=False).agg(required_headcount=('required_headcount','sum'),actual_headcount=('actual_headcount','sum'),vacancies=('vacancies','sum'),absence_rate=('absence_rate','mean'),overtime_hours=('overtime_hours_per_employee','mean'),capacity_gap_pct=('capacity_gap_pct','mean'))
    s=frames['fact_supply'].copy(); s['month']=pd.to_datetime(s['month']).dt.to_period('M').astype(str)
    sm=s.groupby('month',as_index=False).agg(supplier_reliability=('supplier_reliability','mean'),shortage_hours=('shortage_hours','sum'))
    sh=frames['fact_shipment'].copy(); sh['month']=pd.to_datetime(sh['ship_date']).dt.to_period('M').astype(str)
    shm=sh.groupby('month',as_index=False).agg(on_time_delivery=('on_time_flag','mean'),avg_delay_days=('delay_days','mean'),logistics_cost=('logistics_cost','sum'))
    t=frames['fact_technology_incident'].copy(); t['month']=pd.to_datetime(t['date']).dt.to_period('M').astype(str)
    tm=t.groupby('month',as_index=False).agg(technology_downtime_min=('duration_min','sum'),major_incidents=('major_incident_flag','sum'))
    out=pm.merge(f,on='month',how='left').merge(wm,on='month',how='left').merge(sm,on='month',how='left').merge(shm,on='month',how='left').merge(tm,on='month',how='left')
    out['gross_margin_pct_proxy']=(out['gross_margin_proxy']/out['revenue'].replace(0,np.nan)).fillna(0)
    return out


def quality_pareto(frames):
    q=frames['fact_quality']
    out=q.groupby('defect_category',as_index=False)['defect_units'].sum().sort_values('defect_units',ascending=False)
    out['share']=out['defect_units']/out['defect_units'].sum()
    out['cumulative_share']=out['share'].cumsum()
    return out


def reliability_mart(frames):
    down=frames['fact_downtime']; maint=frames['fact_maintenance']
    d=down.groupby('machine_id',as_index=False).agg(failure_downtime_min=('duration_min','sum'),downtime_events=('downtime_event_id','count'))
    m=maint.groupby('machine_id',as_index=False).agg(maintenance_events=('maintenance_event_id','count'),mttr_min=('duration_min','mean'),corrective_events=('maintenance_type',lambda x:(x=='Corrective').sum()))
    out=frames['dim_machine'].merge(d,on='machine_id',how='left').merge(m,on='machine_id',how='left').fillna(0)
    days=(pd.to_datetime(frames['fact_production']['date']).max()-pd.to_datetime(frames['fact_production']['date']).min()).days+1
    out['mtbf_days_proxy']=days/out['downtime_events'].replace(0,np.nan)
    return out
