from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def forecast_demand(orders: pd.DataFrame, horizon=3):
    d=orders.copy(); d['month']=pd.to_datetime(d['order_date']).dt.to_period('M').dt.to_timestamp()
    ts=d.groupby('month',as_index=False)['quantity'].sum().rename(columns={'quantity':'demand'})
    # Transparent baseline: 3-month moving average, backtested one-step ahead.
    ts['forecast']=ts['demand'].rolling(3).mean().shift(1)
    valid=ts.dropna()
    mae=float(mean_absolute_error(valid['demand'],valid['forecast'])) if len(valid) else None
    rmse=float(mean_squared_error(valid['demand'],valid['forecast'])**0.5) if len(valid) else None
    bias=float((valid['forecast']-valid['demand']).mean()) if len(valid) else None
    future=[]
    history=list(ts['demand'].astype(float))
    last=ts['month'].max()
    for i in range(1,horizon+1):
        fc=float(np.mean(history[-3:]))
        future.append((last+pd.offsets.MonthBegin(i),fc))
        history.append(fc)
    f=pd.DataFrame(future,columns=['month','forecast_demand'])
    metrics={'method':'3-month moving-average baseline','mae':mae,'rmse':rmse,'bias':bias,'note':'Model-derived forecast baseline; compare future methods against this baseline.'}
    return metrics,ts,f
