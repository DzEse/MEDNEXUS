# KPI Dictionary

| KPI | Formula | Interpretation / limitations |
|---|---|---|
| Availability | Run Time / (Planned Production Time − Planned Downtime) | Equipment availability during scheduled production window |
| Performance | Ideal Cycle Time × Total Count / Run Time | Capped for reporting sanity; investigate values >100% in real data |
| Quality | Good Count / Total Count | Output yield component of OEE; good output includes recovered rework in the canonical synthetic process |
| OEE | Availability × Performance × Quality | Composite effectiveness measure |
| FPY | (Total Count − Defect Units) / Total Count | Valid single-stage first-pass yield in the canonical synthetic process because defect_units are units failing the first pass before rework |
| RTY | Not calculated | Sequential stage yields do not exist; RTY is gated rather than fabricated |
| Defect Rate | Defect Units / Total Count | Unit defect/nonconformance proportion; not DPMO |
| DPMO | Not calculated | Opportunities per unit are not defined |
| OLI | 1 − Good Units / Theoretical Units | Project-defined productive-capacity loss indicator; not the same as OEE |
| p-chart center line | Total defective units / Total inspected units within plant | Statistical process-control center line for daily plant subgroups |
| p-chart limits | p-bar ± 3 × sqrt(p-bar(1-p-bar)/n) | Binomial proportion limits, clipped to 0–1; signals require investigation and are not causal proof |
| Cost per Good Unit | Operating Cost / Good Units | Synthetic enterprise cost-efficiency indicator |
| Known Internal Quality Cost Proxy | Scrap Cost | Partial internal quality-cost proxy only; full COPQ is not calculated |
| OTIF proxy | On-time delivery flag mean | Default data models complete quantity fulfillment at shipment level |
| Capacity Gap % | max(Required HC − Actual HC, 0) / Required HC | Workforce capacity pressure proxy |
| MORI | Weighted normalized risk components × 100 | Project-defined index, not industry standard |
| Data Trust Score | Mean of eight normalized trust dimensions × 100 | Project-defined composite covering completeness, validity, consistency, uniqueness, timeliness, referential integrity, schema consistency and freshness |
| Simulated Opportunity Value | Scenario reduction applied to observed cost proxies | Simulation, not realized savings |
