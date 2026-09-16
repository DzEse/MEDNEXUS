from pathlib import Path
import sqlite3
import pandas as pd


def connect(db_path):
    con = sqlite3.connect(db_path)
    con.execute('PRAGMA foreign_keys = ON;')
    return con


def load_frames(con, frames: dict[str, pd.DataFrame]):
    for name, df in frames.items():
        df.to_sql(name, con, if_exists='replace', index=False)
    con.commit()


def execute_sql_file(con, path):
    sql = Path(path).read_text(encoding='utf-8')
    con.executescript(sql)
    con.commit()


def query(con, sql, params=None):
    return pd.read_sql_query(sql, con, params=params)
