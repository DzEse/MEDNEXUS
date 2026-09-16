from pathlib import Path
import os
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / 'config' / 'project.yml'


def load_config():
    with CONFIG_PATH.open('r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    cfg['simulation']['seed'] = int(os.getenv('MEDNEXUS_SEED', cfg['simulation']['seed']))
    cfg['simulation']['months'] = int(os.getenv('MEDNEXUS_MONTHS', cfg['simulation']['months']))
    return cfg


def path(*parts):
    return ROOT.joinpath(*parts)
