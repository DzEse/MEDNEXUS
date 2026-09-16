from pathlib import Path
import json
import hashlib
import pandas as pd


def ensure_dirs(paths):
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


def write_json(obj, path):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, default=str), encoding='utf-8')


def file_sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def save_frame(df: pd.DataFrame, path):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)
