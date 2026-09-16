from __future__ import annotations
import numpy as np
import pandas as pd


def _norm(series, inverse=False):
    s=series.astype(float)
    lo,hi=s.min(),s.max()
    if hi==lo: out=pd.Series(0.0,index=s.index)
    else: out=(s-lo)/(hi-lo)
    return 1-out if inverse else out


def build_mori(mart: pd.DataFrame, weights: dict):
    m=mart.copy()
    components=pd.DataFrame({'month':m['month']})
    components['quality']=_norm(m['defect_units']/m['total_units'].clip(lower=1))
    components['equipment']=_norm(m['unplanned_downtime_min'])
    components['downtime']=_norm(m['downtime_cost'])
    components['capacity']=_norm(m['capacity_gap_pct'])
    components['supply']=_norm(m['shortage_hours'])
    components['logistics']=_norm(m['on_time_delivery'],inverse=True)
    components['workforce']=_norm(m['overtime_hours'])
    components['technology']=_norm(m['technology_downtime_min'])
    score=np.zeros(len(m))
    for c,w in weights.items(): score += components[c].to_numpy()*float(w)
    components['mori_score']=(score*100).clip(0,100)
    components['mori_band']=pd.cut(components['mori_score'],[-1,24,49,74,100],labels=['Stable','Watch','Elevated','Critical'])
    return components
