from __future__ import annotations
from pathlib import Path
import shutil
import sqlite3
import pandas as pd
from .config import load_config, path
from .synthetic import generate
from .database import connect, load_frames, execute_sql_file
from .quality import (
    evaluate,
    evaluate_referential_integrity,
    build_observability,
    model_input_profile,
    data_trust_score,
)
from .data_dictionary import build_data_dictionary, build_table_register
from .analytics import production_kpis, monthly_enterprise_mart, quality_pareto, reliability_mart
from .statistical_quality import (
    methodology_gates,
    p_chart_by_plant,
    p_chart_summary,
    six_big_losses,
    capacity_waterfall,
    value_leakage,
)
from .models import train_predictive_maintenance
from .root_cause import run_root_cause_analysis
from .forecasting import forecast_demand
from .risk import run_mori_validation
from .scenarios import run_scenarios
from .process_analytics import run_process_and_experiment_gates
from .architecture_governance import (
    build_operations_twin_catalog,
    build_output_lineage_registry,
    build_analysis_design_checklist,
    run_persistent_drift_monitor,
)
from .decision_queue import build as build_decision_queue
from .reporting import write_management_summary
from .utils import save_frame, write_json, file_sha256


def _clean():
    for d in [path('data','synthetic'),path('data','curated'),path('powerbi','exports'),path('artifacts','reports'),path('artifacts','validation'),path('artifacts','models')]:
        if d.exists():
            for p in d.glob('*'):
                if p.name=='.gitkeep':
                    continue
                if p.is_file():
                    p.unlink()
                elif p.is_dir():
                    shutil.rmtree(p)
    db=path('mednexus.db')
    if db.exists():
        db.unlink()


def _build_date_dimension(frames, forecast_future):
    start=pd.to_datetime(frames['fact_production']['date']).min()
    end_candidates=[
        pd.to_datetime(frames['fact_production']['date']).max(),
        pd.to_datetime(frames['fact_shipment']['actual_delivery_date']).max(),
        pd.to_datetime(forecast_future['month']).max(),
    ]
    end=max(x for x in end_candidates if pd.notna(x))
    d=pd.DataFrame({'date':pd.date_range(start.normalize(),end.normalize(),freq='D')})
    d['year']=d['date'].dt.year
    d['quarter']='Q'+d['date'].dt.quarter.astype(str)
    d['month_number']=d['date'].dt.month
    d['month_name']=d['date'].dt.month_name()
    d['year_month']=d['date'].dt.strftime('%Y-%m')
    d['month_start']=d['date'].dt.to_period('M').dt.to_timestamp()
    d['day_of_week']=d['date'].dt.day_name()
    d['is_weekend']=d['date'].dt.dayofweek.ge(5).astype(int)
    return d


def _with_month_date(df):
    out=df.copy()
    if 'month' in out.columns:
        out['month_date']=pd.to_datetime(out['month'].astype(str).str.slice(0,7)+'-01')
    return out


def run(clean=False, seed=None):
    cfg=load_config()
    if clean:
        _clean()
    for d in [path('data','synthetic'),path('data','curated'),path('powerbi','exports'),path('artifacts','reports'),path('artifacts','validation'),path('artifacts','models')]:
        d.mkdir(parents=True,exist_ok=True)

    print('[1/9] Generating synthetic enterprise data...')
    frames=generate(seed=seed)
    for name,df in frames.items():
        save_frame(df,path('data','synthetic',f'{name}.csv'))

    print('[2/9] Running data-quality, integrity and observability controls...')
    table_q,business_q=evaluate(frames)
    referential_q=evaluate_referential_integrity(frames)
    observability=build_observability(frames)
    model_profile=model_input_profile(frames)
    data_dictionary=build_data_dictionary(frames)
    table_register=build_table_register(frames)

    trust,trust_components=data_trust_score(
        table_q,
        business_q,
        referential_checks=referential_q,
        observability=observability,
    )

    save_frame(table_q,path('artifacts','validation','data_quality_tables.csv'))
    save_frame(business_q,path('artifacts','validation','data_quality_business_checks.csv'))
    save_frame(referential_q,path('artifacts','validation','referential_integrity.csv'))
    save_frame(observability,path('artifacts','validation','data_observability.csv'))
    save_frame(model_profile,path('artifacts','validation','model_input_profile.csv'))
    save_frame(data_dictionary,path('artifacts','validation','data_dictionary.csv'))
    save_frame(table_register,path('artifacts','validation','table_register.csv'))
    write_json({
        'data_trust_score':trust,
        'methodology':'MEDNEXUS project-defined Data Trust Score v2',
        'industry_standard':False,
        'component_weighting':'equal across eight dimensions',
        'components':trust_components,
        'dimensions':[
            'completeness','validity','consistency','uniqueness',
            'timeliness','referential_integrity','schema_consistency','freshness'
        ],
    },path('artifacts','validation','data_trust.json'))

    quality_failed = (
        (business_q['status']=='FAIL').any()
        or (table_q['status']=='FAIL').any()
        or (referential_q['status']=='FAIL').any()
        or (observability['status']=='FAIL').any()
    )
    if quality_failed:
        raise RuntimeError('Data quality/integrity/observability gate failed. See artifacts/validation/.')

    print('[3/9] Building analytical marts...')
    production_enriched=production_kpis(frames['fact_production'])
    mart=monthly_enterprise_mart(frames)
    qp=quality_pareto(frames)
    rel=reliability_mart(frames)
    quality_gates=methodology_gates()
    p_chart=p_chart_by_plant(frames['fact_production'])
    p_chart_overview=p_chart_summary(p_chart)
    loss_decomposition=six_big_losses(frames)
    capacity_flow=capacity_waterfall(frames['fact_production'])
    leakage=value_leakage(frames)
    save_frame(production_enriched,path('data','curated','production_kpis.csv'))
    save_frame(mart,path('data','curated','enterprise_monthly_mart.csv'))
    save_frame(qp,path('data','curated','quality_pareto.csv'))
    save_frame(rel,path('data','curated','reliability_mart.csv'))
    save_frame(p_chart,path('data','curated','quality_p_chart.csv'))
    save_frame(p_chart_overview,path('data','curated','quality_p_chart_summary.csv'))
    save_frame(loss_decomposition,path('data','curated','six_big_losses.csv'))
    save_frame(capacity_flow,path('data','curated','capacity_waterfall.csv'))
    save_frame(leakage,path('data','curated','value_leakage.csv'))
    save_frame(quality_gates,path('artifacts','validation','quality_methodology_gates.csv'))

    twin_catalog=build_operations_twin_catalog()
    output_lineage=build_output_lineage_registry()
    analysis_checklist=build_analysis_design_checklist()
    drift_profile,drift_comparison,drift_summary=run_persistent_drift_monitor(
        table_q,
        model_profile,
        mart,
        path('artifacts','runtime','observability_baseline.csv'),
        frames=frames,
    )
    save_frame(twin_catalog,path('artifacts','validation','enterprise_operations_twin.csv'))
    save_frame(output_lineage,path('artifacts','validation','output_lineage_registry.csv'))
    save_frame(analysis_checklist,path('artifacts','validation','analysis_design_checklist.csv'))
    save_frame(drift_profile,path('artifacts','validation','observability_current_profile.csv'))
    save_frame(drift_comparison,path('artifacts','validation','cross_run_drift.csv'))
    write_json(drift_summary,path('artifacts','validation','cross_run_drift_summary.json'))

    root_cause=run_root_cause_analysis(frames)
    save_frame(root_cause['segments'],path('data','curated','root_cause_segments.csv'))
    save_frame(root_cause['associations'],path('data','curated','root_cause_associations.csv'))
    save_frame(root_cause['group_tests'],path('data','curated','root_cause_group_tests.csv'))
    save_frame(root_cause['regression'],path('data','curated','root_cause_regression.csv'))
    save_frame(root_cause['vif'],path('data','curated','root_cause_vif.csv'))
    save_frame(root_cause['tree_importance'],path('data','curated','root_cause_tree_importance.csv'))
    save_frame(root_cause['priorities'],path('data','curated','root_cause_investigation_priorities.csv'))
    write_json(root_cause['methodology'],path('artifacts','validation','root_cause_methodology.json'))
    path('artifacts','validation','root_cause_tree_rules.txt').write_text(
        root_cause['tree_rules'],
        encoding='utf-8',
    )

    print('[4/9] Training and validating predictive-maintenance candidates...')
    (
        model_metrics,
        scored,
        model_comparison,
        threshold_analysis,
        calibration,
        feature_importance,
    )=train_predictive_maintenance(
        frames['fact_sensor'],
        path('artifacts','models','predictive_maintenance_selected.joblib'),
    )
    save_frame(scored,path('data','curated','predictive_maintenance_scores.csv'))
    save_frame(model_comparison,path('artifacts','validation','predictive_maintenance_model_comparison.csv'))
    save_frame(threshold_analysis,path('artifacts','validation','predictive_maintenance_threshold_analysis.csv'))
    save_frame(calibration,path('artifacts','validation','predictive_maintenance_calibration.csv'))
    save_frame(feature_importance,path('artifacts','validation','predictive_maintenance_feature_importance.csv'))
    write_json(model_metrics,path('artifacts','validation','predictive_maintenance_metrics.json'))

    print('[5/9] Building demand forecast...')
    (
        forecast_metrics,
        forecast_history,
        forecast_future,
        forecast_comparison,
        forecast_diagnostics,
    )=forecast_demand(frames['fact_orders'])
    save_frame(forecast_history,path('data','curated','demand_forecast_backtest.csv'))
    save_frame(forecast_future,path('data','curated','demand_forecast_future.csv'))
    save_frame(forecast_comparison,path('artifacts','validation','forecast_model_comparison.csv'))
    save_frame(forecast_diagnostics,path('artifacts','validation','forecast_diagnostics.csv'))
    write_json(forecast_metrics,path('artifacts','validation','forecast_metrics.json'))

    print('[6/9] Building risk, scenarios and decision queue...')
    mori_validation=run_mori_validation(mart,cfg['risk']['mori_weights'])
    risk=mori_validation['mori']
    save_frame(mori_validation['contributions'],path('artifacts','validation','mori_component_contributions.csv'))
    save_frame(mori_validation['weight_sensitivity'],path('artifacts','validation','mori_weight_sensitivity.csv'))
    save_frame(mori_validation['threshold_sensitivity'],path('artifacts','validation','mori_threshold_sensitivity.csv'))
    write_json(mori_validation['sensitivity_summary'],path('artifacts','validation','mori_sensitivity_summary.json'))
    write_json(mori_validation['methodology'],path('artifacts','validation','mori_methodology.json'))
    scenario_validation=run_scenarios(mart)
    scenarios=scenario_validation['scenarios']
    scenario_assumptions=scenario_validation['assumptions']
    scenario_monitoring=scenario_validation['monitoring_plan']
    optimization=scenario_validation['optimization_gate']
    dq=build_decision_queue(mart,risk,rel,qp,forecast_metrics)
    save_frame(risk,path('data','curated','mori.csv'))
    save_frame(scenarios,path('data','curated','scenario_outputs.csv'))
    save_frame(scenario_assumptions,path('data','curated','scenario_assumptions.csv'))
    save_frame(scenario_monitoring,path('data','curated','scenario_monitoring_plan.csv'))
    write_json(scenario_validation['methodology'],path('artifacts','validation','scenario_methodology.json'))
    write_json(optimization,path('artifacts','validation','optimization_gate.json'))
    save_frame(dq,path('data','curated','decision_queue.csv'))

    process_validation=run_process_and_experiment_gates(frames)
    process_event_log=process_validation['event_log']
    process_cases=process_validation['cases']
    process_transitions=process_validation['transition_summary']
    write_json(process_validation['process_gate'],path('artifacts','validation','process_mining_gate.json'))
    write_json(process_validation['experiment_gate'],path('artifacts','validation','experimentation_gate.json'))
    write_json(process_validation['methodology'],path('artifacts','validation','process_analytics_methodology.json'))
    save_frame(process_event_log,path('data','curated','process_order_fulfillment_event_log.csv'))
    save_frame(process_cases,path('data','curated','process_order_fulfillment_cases.csv'))
    save_frame(process_transitions,path('data','curated','process_transition_summary.csv'))

    print('[7/9] Loading SQLite analytical database and SQL views...')
    con=connect(path('mednexus.db'))
    load_frames(con,frames)
    production_enriched.to_sql('mart_production_kpi',con,if_exists='replace',index=False)
    mart.to_sql('mart_enterprise_monthly',con,if_exists='replace',index=False)
    risk.to_sql('mart_mori',con,if_exists='replace',index=False)
    scenarios.to_sql('mart_scenarios',con,if_exists='replace',index=False)
    scenario_assumptions.to_sql('mart_scenario_assumptions',con,if_exists='replace',index=False)
    scenario_monitoring.to_sql('mart_scenario_monitoring',con,if_exists='replace',index=False)
    process_event_log.to_sql('mart_process_event_log',con,if_exists='replace',index=False)
    process_cases.to_sql('mart_order_fulfillment_cases',con,if_exists='replace',index=False)
    process_transitions.to_sql('mart_process_transition_summary',con,if_exists='replace',index=False)
    dq.to_sql('mart_decision_queue',con,if_exists='replace',index=False)
    p_chart.to_sql('mart_quality_p_chart',con,if_exists='replace',index=False)
    loss_decomposition.to_sql('mart_six_big_losses',con,if_exists='replace',index=False)
    capacity_flow.to_sql('mart_capacity_waterfall',con,if_exists='replace',index=False)
    leakage.to_sql('mart_value_leakage',con,if_exists='replace',index=False)
    root_cause['segments'].to_sql('mart_root_cause_segments',con,if_exists='replace',index=False)
    root_cause['associations'].to_sql('mart_root_cause_associations',con,if_exists='replace',index=False)
    root_cause['regression'].to_sql('mart_root_cause_regression',con,if_exists='replace',index=False)
    root_cause['priorities'].to_sql('mart_root_cause_priorities',con,if_exists='replace',index=False)
    forecast_comparison.to_sql('mart_forecast_model_comparison',con,if_exists='replace',index=False)
    forecast_diagnostics.to_sql('mart_forecast_diagnostics',con,if_exists='replace',index=False)
    execute_sql_file(con,path('sql','analytical_views.sql'))
    execute_sql_file(con,path('sql','layered_architecture.sql'))
    sql_views = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name",
        con,
    )['name'].tolist()
    expected_layered_views = [
        'stg_production_validated',
        'dim_machine_hierarchy',
        'fact_order_fulfillment_enriched',
        'kpi_monthly_operations',
        'val_order_fulfillment_grain',
        'val_machine_hierarchy_grain',
        'kpi_supplier_risk_ranked',
    ]
    missing_layered_views = [name for name in expected_layered_views if name not in sql_views]
    if missing_layered_views:
        raise RuntimeError(f'Layered SQL contract failed: {missing_layered_views}')
    order_grain = pd.read_sql_query('SELECT * FROM val_order_fulfillment_grain', con).iloc[0].to_dict()
    machine_grain = pd.read_sql_query('SELECT * FROM val_machine_hierarchy_grain', con).iloc[0].to_dict()
    write_json({
        'expected_views': expected_layered_views,
        'missing_views': missing_layered_views,
        'order_fulfillment_grain': order_grain,
        'machine_hierarchy_grain': machine_grain,
        'status': 'PASS',
    },path('artifacts','validation','sql_layer_contract.json'))
    con.close()

    print('[8/9] Exporting Power BI-ready datasets and reports...')
    dim_date=_build_date_dimension(frames,forecast_future)
    exports={
        'DimDate':dim_date,
        'DimPlant':frames['dim_plant'],
        'DimLine':frames['dim_line'],
        'DimMachine':frames['dim_machine'],
        'DimProduct':frames['dim_product'],
        'DimSupplier':frames['dim_supplier'],
        'DimCustomer':frames['dim_customer'],
        'DimEmployee':frames['dim_employee'],
        'EnterpriseMonthly':_with_month_date(mart),
        'ProductionKPI':production_enriched,
        'Downtime':frames['fact_downtime'],
        'QualityEvents':frames['fact_quality'],
        'Maintenance':frames['fact_maintenance'],
        'MORI':_with_month_date(risk),
        'MORIComponentContributions':_with_month_date(mori_validation['contributions']),
        'MORIWeightSensitivity':_with_month_date(mori_validation['weight_sensitivity']),
        'MORIThresholdSensitivity':_with_month_date(mori_validation['threshold_sensitivity']),
        'ScenarioOutputs':scenarios,
        'ScenarioAssumptions':scenario_assumptions,
        'ScenarioMonitoringPlan':scenario_monitoring,
        'ProcessEventLog':process_event_log,
        'ProcessCases':process_cases,
        'ProcessTransitions':process_transitions,
        'DecisionQueue':dq,
        'QualityPareto':qp,
        'QualityPChart':p_chart,
        'SixBigLosses':_with_month_date(loss_decomposition),
        'CapacityWaterfall':_with_month_date(capacity_flow),
        'ValueLeakage':_with_month_date(leakage),
        'Reliability':rel,
        'PredictiveMaintenanceScores':scored,
        'PredictiveMaintenanceModelComparison':model_comparison,
        'PredictiveMaintenanceCalibration':calibration,
        'PredictiveMaintenanceFeatureImportance':feature_importance,
        'RootCauseSegments':root_cause['segments'],
        'RootCauseAssociations':root_cause['associations'],
        'RootCauseGroupTests':root_cause['group_tests'],
        'RootCauseRegression':root_cause['regression'],
        'RootCauseTreeImportance':root_cause['tree_importance'],
        'RootCausePriorities':root_cause['priorities'],
        'DemandForecast':forecast_future,
        'DemandForecastBacktest':forecast_history,
        'DemandForecastModelComparison':forecast_comparison,
        'DemandForecastDiagnostics':forecast_diagnostics,
        'Finance':frames['fact_finance'],
        'Workforce':frames['fact_workforce'],
        'Recruitment':frames['fact_recruitment'],
        'Supply':frames['fact_supply'],
        'Orders':frames['fact_orders'],
        'Shipments':frames['fact_shipment'],
        'CustomerService':frames['fact_customer_service'],
        'TechnologyIncidents':frames['fact_technology_incident'],
        'SaaSUsage':frames['fact_saas_usage'],
    }
    for name,df in exports.items():
        save_frame(df,path('powerbi','exports',f'{name}.csv'))
    write_management_summary(path('artifacts','reports','management_summary.md'),mart,risk,qp,model_metrics,forecast_metrics,trust)

    print('[9/9] Writing reproducibility manifest...')
    manifest=[]
    for p in sorted(path('powerbi','exports').glob('*.csv')):
        manifest.append({'file':str(p.relative_to(path())), 'sha256':file_sha256(p), 'bytes':p.stat().st_size})
    write_json({
        'project':'MEDNEXUS',
        'seed':seed if seed is not None else cfg['simulation']['seed'],
        'data_trust_score':trust,
        'generated_files':manifest
    },path('artifacts','validation','manifest.json'))
    print('MEDNEXUS pipeline completed successfully.')
    print(f'Data Trust Score: {trust}/100')
    print('Open artifacts/reports/management_summary.md for the executive summary.')
