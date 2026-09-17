import numpy as np

from mednexus.database import connect, execute_sql_file, load_frames, query
from mednexus.statistical_quality import value_leakage
from mednexus.synthetic import generate
from mednexus.config import path


def _database_with_views():
    frames = generate(seed=42)
    con = connect(':memory:')
    load_frames(con, frames)
    value_leakage(frames).to_sql('mart_value_leakage', con, if_exists='replace', index=False)
    execute_sql_file(con, path('sql', 'analytical_views.sql'))
    return con


def test_sql_production_reconciliation():
    con = _database_with_views()
    try:
        row = query(con, 'SELECT * FROM vw_production_reconciliation').iloc[0]
        assert row['final_output_identity_difference'] == 0
        assert row['first_pass_identity_difference'] == 0
    finally:
        con.close()


def test_sql_quality_event_reconciliation():
    con = _database_with_views()
    try:
        row = query(con, 'SELECT * FROM vw_quality_reconciliation').iloc[0]
        assert row['defect_difference'] == 0
        assert row['rework_difference'] == 0
        assert row['scrap_difference'] == 0
    finally:
        con.close()


def test_sql_finance_reconciliation():
    con = _database_with_views()
    try:
        df = query(con, 'SELECT * FROM vw_finance_reconciliation')
        assert np.allclose(df['revenue_difference'], 0.0, atol=1e-6)
        assert np.allclose(df['operating_cost_difference'], 0.0, atol=1e-6)
    finally:
        con.close()
