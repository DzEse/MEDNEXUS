from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from joblib import dump
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, confusion_matrix

FEATURES=['temperature_c','torque_nm','vibration_mm_s','tool_wear_index']


def train_predictive_maintenance(sensor: pd.DataFrame, model_path=None):
    df=sensor.copy().sort_values('date')
    df['date']=pd.to_datetime(df['date'])
    split=int(len(df)*0.8)
    train=df.iloc[:split]; test=df.iloc[split:]
    Xtr=train[FEATURES]; ytr=train['failure_next_7d']
    Xte=test[FEATURES]; yte=test['failure_next_7d']
    pipe=Pipeline([('scale',StandardScaler()),('model',LogisticRegression(max_iter=1000,class_weight='balanced',random_state=42))])
    pipe.fit(Xtr,ytr)
    prob=pipe.predict_proba(Xte)[:,1]
    # recall-sensitive threshold because false negatives have higher operational cost in this simulated use case.
    threshold=0.40
    pred=(prob>=threshold).astype(int)
    metrics={
        'model':'LogisticRegression baseline',
        'split':'temporal 80/20',
        'threshold':threshold,
        'precision':float(precision_score(yte,pred,zero_division=0)),
        'recall':float(recall_score(yte,pred,zero_division=0)),
        'f1':float(f1_score(yte,pred,zero_division=0)),
        'roc_auc':float(roc_auc_score(yte,prob)) if yte.nunique()>1 else None,
        'pr_auc':float(average_precision_score(yte,prob)) if yte.nunique()>1 else None,
        'confusion_matrix':confusion_matrix(yte,pred,labels=[0,1]).tolist(),
        'test_rows':int(len(test)),
        'positive_rate_test':float(yte.mean()),
        'note':'Model-derived. Feature importance must not be interpreted as causation.'
    }
    scored=test[['date','machine_id','plant_id','line_id']].copy()
    scored['failure_risk']=prob
    scored['predicted_failure_flag']=pred
    scored['actual_failure_next_7d']=yte.values
    if model_path:
        Path(model_path).parent.mkdir(parents=True,exist_ok=True)
        dump(pipe,model_path)
    return metrics, scored
