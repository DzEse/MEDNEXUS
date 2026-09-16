from pathlib import Path

DIRS = [
    'data/raw', 'data/staging', 'data/curated', 'data/synthetic', 'data/samples',
    'artifacts/runtime', 'artifacts/models', 'artifacts/reports', 'artifacts/validation',
    'powerbi/exports', 'powerbi/screenshots'
]

for d in DIRS:
    Path(d).mkdir(parents=True, exist_ok=True)
    keep = Path(d) / '.gitkeep'
    if not keep.exists():
        keep.write_text('', encoding='utf-8')

print('MEDNEXUS project directories are ready.')
