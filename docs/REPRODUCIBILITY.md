# Reproducibility

1. Create a Python virtual environment.
2. Install `requirements.txt`.
3. Run `python setup_project.py`.
4. Run `python run_pipeline.py --clean`.
5. Run `pytest -q`.
6. Inspect `artifacts/validation/manifest.json` for hashes of BI exports.

The synthetic generator is deterministic for a fixed seed. Override with `python run_pipeline.py --clean --seed 123` for a new synthetic world.
