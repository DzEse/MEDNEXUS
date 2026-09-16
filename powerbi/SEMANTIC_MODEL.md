# Power BI Semantic Model

Use `EnterpriseMonthly` as the executive monthly fact/mart. Use detailed exports for drill-through pages.

Recommended relationships after importing detailed dimensions from the SQLite database or generated synthetic CSVs:
- Plant 1:* Workforce
- Plant 1:* Recruitment
- Plant 1:* ProductionKPI
- Machine 1:* ProductionKPI
- Machine 1:* Reliability / PredictiveMaintenanceScores
- Product 1:* ProductionKPI
- Supplier 1:* Supply
- Customer 1:* Shipments

Keep filter direction single wherever possible. Avoid many-to-many relationships and do not join facts directly at incompatible grains.
