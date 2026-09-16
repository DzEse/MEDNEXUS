from __future__ import annotations
import pandas as pd
import numpy as np

PRIMARY_KEYS = {
    'dim_plant':'plant_id','dim_line':'line_id','dim_machine':'machine_id','dim_product':'product_id',
    'dim_supplier':'supplier_id','dim_customer':'customer_id','dim_employee':'employee_id',
    'fact_production':'production_order_id','fact_downtime':'downtime_event_id','fact_quality':'quality_event_id',
    'fact_maintenance':'maintenance_event_id','fact_orders':'order_id','fact_shipment':'shipment_id'
}


def evaluate(frames):
    results=[]
    for name,df in frames.items():
        rows=len(df)
        null_cells=int(df.isna().sum().sum())
        duplicate_rows=int(df.duplicated().sum())
        pk=PRIMARY_KEYS.get(name)
        duplicate_keys=int(df[pk].duplicated().sum()) if pk and pk in df else 0
        results.append({'table':name,'row_count':rows,'null_cells':null_cells,'duplicate_rows':duplicate_rows,'duplicate_keys':duplicate_keys,'status':'PASS' if duplicate_keys==0 else 'FAIL'})
    q=pd.DataFrame(results)
    # Additional business validity checks
    checks=[]
    prod=frames['fact_production']
    checks.append(('production_counts_nonnegative', bool((prod[['total_count','good_count','defect_units','rework_units','scrap_units']]>=0).all().all())))
    checks.append(('good_count_not_above_total', bool((prod['good_count']<=prod['total_count']).all())))
    checks.append(('runtime_positive', bool((prod['run_time_min']>0).all())))
    ship=frames['fact_shipment']
    checks.append(('shipment_delay_nonnegative', bool((ship['delay_days']>=0).all())))
    finance=frames['fact_finance']
    checks.append(('finance_revenue_nonnegative', bool((finance['revenue']>=0).all())))
    business=pd.DataFrame(checks,columns=['check','passed'])
    business['status']=np.where(business['passed'],'PASS','FAIL')
    return q,business


def data_trust_score(table_quality: pd.DataFrame, business_checks: pd.DataFrame):
    # Project-defined composite score. Equal dimension weighting is intentionally simple and transparent.
    tables=len(table_quality)
    no_dup_key=(table_quality['duplicate_keys']==0).mean() if tables else 0
    no_dup_row=(table_quality['duplicate_rows']==0).mean() if tables else 0
    null_score=1-min(1,table_quality['null_cells'].sum()/max(1,table_quality['row_count'].sum()*5))
    validity=business_checks['passed'].mean() if len(business_checks) else 0
    components={'uniqueness':no_dup_key,'row_uniqueness':no_dup_row,'completeness_proxy':null_score,'validity':validity}
    score=100*sum(components.values())/len(components)
    return round(score,2), components
