# Core DAX Measures

```DAX
Revenue = SUM(EnterpriseMonthly[revenue])
Operating Cost = SUM(EnterpriseMonthly[operating_cost])
Operating Margin Proxy = [Revenue] - [Operating Cost]
Gross Margin Proxy = SUM(EnterpriseMonthly[gross_margin_proxy])

Total Units = SUM(ProductionKPI[total_count])
Good Units = SUM(ProductionKPI[good_count])
Defect Units = SUM(ProductionKPI[defect_units])
Scrap Units = SUM(ProductionKPI[scrap_units])

Availability =
DIVIDE(SUM(ProductionKPI[run_time_min]),
       SUM(ProductionKPI[planned_production_min]) - SUM(ProductionKPI[planned_downtime_min]))

Performance =
DIVIDE(SUMX(ProductionKPI, ProductionKPI[ideal_cycle_min] * ProductionKPI[total_count]),
       SUM(ProductionKPI[run_time_min]))

Quality Rate = DIVIDE([Good Units], [Total Units])
OEE = [Availability] * [Performance] * [Quality Rate]
Defect Rate = DIVIDE([Defect Units], [Total Units])

Average OLI = AVERAGE(EnterpriseMonthly[oli])
Latest MORI = MAXX(TOPN(1, MORI, MORI[month], DESC), MORI[mori_score])
On-Time Delivery = AVERAGE(EnterpriseMonthly[on_time_delivery])
Capacity Gap % = AVERAGE(EnterpriseMonthly[capacity_gap_pct])
```

Do not sum percentage KPIs that are defined as rates; use weighted or context-appropriate aggregation.
