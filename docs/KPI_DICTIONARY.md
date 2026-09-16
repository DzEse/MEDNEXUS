# KPI Dictionary

| KPI | Formula | Interpretation / limitations |
|---|---|---|
| Availability | Run Time / (Planned Production Time − Planned Downtime) | Equipment availability during scheduled production window |
| Performance | Ideal Cycle Time × Total Count / Run Time | Capped for reporting sanity; investigate values >100% in real data |
| Quality | Good Count / Total Count | Output yield component of OEE |
| OEE | Availability × Performance × Quality | Composite effectiveness measure |
| FPY proxy | (Total Count − Defect Units) / Total Count | Proxy because sequential-stage rework routing is not modeled in default synthetic build |
| Defect Rate | Defect Units / Total Count | Not DPMO |
| OLI | 1 − Good Units / Theoretical Units | Project-defined productive-capacity loss indicator; not the same as OEE |
| OTIF proxy | On-time delivery flag mean | Default data models complete quantity fulfillment at shipment level |
| Capacity Gap % | max(Required HC − Actual HC, 0) / Required HC | Workforce capacity pressure proxy |
| MORI | Weighted normalized risk components × 100 | Project-defined index, not industry standard |
| Data Trust Score | Mean of transparent completeness/validity/uniqueness proxies × 100 | Project-defined data-quality composite |
| Simulated Opportunity Value | Scenario reduction applied to observed cost proxies | Simulation, not realized savings |
