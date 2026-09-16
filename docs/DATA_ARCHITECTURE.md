# Data Architecture

## Layers
1. **Raw** — reserved for downloaded public data; excluded from Git by default.
2. **Synthetic** — reproducible fictional enterprise data generated from documented business relationships.
3. **Staging** — optional temporary cleaning layer.
4. **Curated** — analytical marts and model outputs.
5. **Relational SQL** — `mednexus.db` SQLite database for professional SQL analysis.
6. **BI exports** — compact CSV extracts for Power BI.

## Why SQLite + CSV in the baseline build
SQLite is embedded, reproducible and requires no database server. CSV exports keep the Power BI handoff universal. The repository can later swap the storage engine for DuckDB, PostgreSQL, Fabric or a warehouse without changing the business logic.

## Controlled multi-source strategy
Public engineering datasets should remain separate from synthetic enterprise domains. A public predictive-maintenance dataset must not be misrepresented as proprietary MEDNEXUS data.
