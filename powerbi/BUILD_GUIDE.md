# Power BI Build Guide

1. Run `python run_pipeline.py --clean`.
2. In Power BI Desktop, choose **Get data → Text/CSV** and import the files in `powerbi/exports/`.
3. Set month/date columns to Date where appropriate and numeric metrics to suitable numeric types.
4. Build the relationships described in `SEMANTIC_MODEL.md`. Keep relationships single-direction unless a documented requirement proves otherwise.
5. Create measures from `DAX_MEASURES.md`.
6. Build pages in the order documented in `PAGE_SPECIFICATIONS.md`.
7. Add a visible disclosure on scenario/model pages: **Synthetic enterprise data / Simulated scenario / Model-derived prediction** as applicable.
8. Validate Power BI totals against `data/curated/enterprise_monthly_mart.csv` and SQLite analytical views before publishing screenshots.
9. Do not commit the PBIX file if it is unnecessarily large; screenshots and build documentation are sufficient for GitHub portfolio review.
