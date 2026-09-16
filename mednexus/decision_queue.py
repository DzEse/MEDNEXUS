from __future__ import annotations
import pandas as pd


def build(mart, risk, reliability, quality_pareto, forecast_metrics):
    latest=mart.iloc[-1]; latest_risk=risk.iloc[-1]
    rows=[]
    top_machine=reliability.sort_values('failure_downtime_min',ascending=False).iloc[0]
    top_defect=quality_pareto.iloc[0]
    rows.append({'priority':'High','issue':'Repeated equipment downtime','domain':'Maintenance','affected_entity':top_machine['machine_id'],'evidence':f"Highest accumulated downtime: {top_machine['failure_downtime_min']:.0f} min",'risk':'Production capacity pressure','estimated_impact':'Simulated opportunity only','recommended_action':'Investigate targeted preventive-maintenance intervention','owner':'Maintenance Manager','urgency':'30 days','confidence':'Medium','analytical_basis':'Historical downtime concentration + predictive-risk layer','data_limitations':'Synthetic operating history; no causal proof'})
    rows.append({'priority':'High','issue':'Quality loss concentration','domain':'Quality','affected_entity':top_defect['defect_category'],'evidence':f"Top defect category share: {top_defect['share']:.1%}",'risk':'Scrap, rework and throughput loss','estimated_impact':'Simulated opportunity only','recommended_action':'Run process-stage investigation and corrective-action validation','owner':'Quality Manager','urgency':'30 days','confidence':'Medium','analytical_basis':'Pareto + defect-rate trend','data_limitations':'Synthetic defect taxonomy; stage-level root cause not proven'})
    rows.append({'priority':'Medium','issue':'Workforce capacity gap','domain':'HR / Operations','affected_entity':'Enterprise','evidence':f"Latest capacity gap: {latest['capacity_gap_pct']:.1%}; overtime: {latest['overtime_hours']:.1f}h/employee",'risk':'Overtime and operating strain','estimated_impact':'Scenario-based','recommended_action':'Prioritize hard-to-fill roles and test staffing scenario','owner':'HR & Operations','urgency':'60 days','confidence':'Medium','analytical_basis':'Workforce demand vs actual staffing','data_limitations':'Association/scenario; hiring impact not causal'})
    rows.append({'priority':'Medium','issue':'Enterprise risk elevation','domain':'Executive','affected_entity':'Enterprise','evidence':f"Latest MORI: {latest_risk['mori_score']:.1f} ({latest_risk['mori_band']})",'risk':'Cross-domain operational pressure','estimated_impact':'Composite risk indicator','recommended_action':'Review top component drivers before allocating intervention budget','owner':'Executive Operations','urgency':'Monthly review','confidence':'Medium','analytical_basis':'Project-defined MORI composite index','data_limitations':'MORI is project-defined, not an industry standard'})
    return pd.DataFrame(rows)
