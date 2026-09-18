# MEDNEXUS Power BI Page Specifications

## Governance

The report must follow the canonical enterprise story rather than a dashboard-count target. The architecture below uses the 13 canonical business questions because, at the current scope, separating them improves traceability and prevents recruitment, statistical-quality, inventory/supply and healthcare-customer requirements from disappearing inside broader pages.

Pages may be consolidated later only if every business question, measure, interaction, disclosure and decision remains explicitly covered.

Every page must state or imply a clear decision question and must avoid unsupported causal language.

---

## Page 1 — Enterprise Command Center

**Question:** Where is MEDNEXUS losing operational value?

Required evidence groups:

- revenue, operating cost and margin;
- workforce/capacity pressure;
- production/OEE/OLI;
- quality loss;
- supply-chain risk;
- logistics/service risk;
- technology health/Data Trust;
- MORI and top component drivers;
- top value-loss drivers;
- priority decision queue.

Recommended layout:

- compact executive KPI row for financial health, OEE/OLI, delivery and MORI;
- enterprise health strip/matrix for margin, capacity gap, quality, supplier reliability, technology health/Data Trust;
- revenue vs operating-cost trend;
- MORI trend/component indicator;
- current value-loss-driver bar/waterfall;
- priority decision queue;
- month slicer and plant slicer only when filter semantics remain valid across displayed facts.

Detailed build: `PAGE_01_ENTERPRISE_COMMAND_CENTER.md`.

---

## Page 2 — Finance & Business Health

**Question:** Where is financial performance being pressured?

Required analysis:

- revenue, operating cost, gross/operating margin proxy;
- budget vs actual/variance;
- labor/material/scrap/rework/downtime/logistics/technology cost;
- COPQ/value-leakage measures once analytically validated;
- cost per good unit where supported;
- trend and cost-driver decomposition;
- clear labels for illustrative financial assumptions.

Interactions:

- date slicer;
- cost-driver field parameter where useful;
- decomposition tree only after measure semantics are validated;
- tooltip showing assumption/provenance for illustrative cost components.

---

## Page 3 — People, HR & Workforce

**Question:** Do we have the people and capacity required to operate the business?

Required analysis:

- required vs actual headcount;
- vacancies/capacity gap;
- overtime and absenteeism;
- labor cost;
- skills/roles/turnover/onboarding/training/utilization only where the final data model supports them;
- workforce-risk and capacity relationship without causal overclaim.

Recommended visuals:

- required vs actual headcount trend;
- vacancy/capacity-gap trend;
- overtime vs absence scatter/trend;
- workforce pressure segmentation by plant/role where valid;
- diagnostic commentary.

---

## Page 4 — Recruitment & Capacity

**Question:** Where are talent gaps becoming operational constraints?

Required analysis:

- open positions;
- recruitment funnel;
- conversion rates;
- time-to-fill;
- cost-per-hire;
- critical roles/skills shortages if supported;
- recruitment bottleneck diagnostics;
- capacity-impact scenarios rather than unsupported causal claims.

Recommended visuals:

- funnel or staged bar chart;
- time-to-fill trend;
- open positions by plant/role;
- bottleneck conversion matrix;
- scenario callout linking hiring assumptions to capacity change, explicitly Simulated.

---

## Page 5 — Manufacturing Performance

**Question:** Where is productive capacity being lost?

Required analysis:

- Availability, Performance, Quality and OEE;
- OLI;
- throughput/good units;
- production attainment/schedule adherence where supported;
- planned/unplanned downtime;
- Six Big Losses decomposition;
- theoretical-capacity → planned downtime → unplanned downtime → speed loss → quality loss → good production waterfall;
- plant/line/machine/product drill-through.

---

## Page 6 — Quality & Process Intelligence

**Question:** Where are defects and process instability originating?

Required analysis:

- defect rate, true FPY and rework/scrap;
- RTY/DPMO only when valid input structure exists;
- defect category/severity/process stage/location where supported;
- Pareto and trend;
- supplier/material/machine/shift/product segmentation where valid;
- statistical process-control charts selected by data structure;
- capability metrics only with valid specification limits;
- COPQ and quality-related value leakage;
- explicit distinction between process control and process capability.

Advanced visuals:

- Pareto;
- control chart produced from validated analytical output;
- decomposition tree/Key Influencers only for association diagnostics and only after assumptions are documented;
- root-cause evidence panel sourced from disconnected `RootCause...` marts: Wilson-interval segment ranking, FDR-adjusted associations, adjusted GLM evidence, shallow-tree importance and investigation priorities;
- every diagnostic visual must visibly state **Association / investigation priority — not causal attribution**.

---

## Page 7 — Equipment & Reliability

**Question:** Which assets represent the greatest operational risk?

Required analysis:

- planned/preventive/corrective maintenance;
- downtime and failure trends;
- failure modes;
- MTBF/MTTR with proxy labeling where definitions are approximate;
- machine age/utilization/backlog where supported;
- predictive-maintenance risk;
- model threshold, false-positive and false-negative context;
- explainability outputs labeled association/model behavior, not causation.

Recommended drill-through: machine detail page/tooltip with maintenance history, downtime, sensor risk and model score.

---

## Page 8 — Supply Chain & Inventory

**Question:** Are materials and suppliers constraining operations?

Required analysis:

- supplier reliability;
- lead time;
- supplier quality/material defects;
- shortage hours/material availability;
- material/inventory/purchase-order/stockout/excess-inventory measures when implemented;
- supplier-risk segmentation;
- relationship to production interruption/capacity shown only at supported evidence level.

---

## Page 9 — Logistics & Customer Service

**Question:** Where are delivery and service failures occurring?

Required analysis:

- order volume;
- promised vs actual delivery;
- on-time delivery and OTIF where valid;
- delay/lead-time distribution;
- shipment exceptions;
- carrier/warehouse/route performance only if modeled;
- logistics cost;
- customer-service issues associated with delivery performance;
- supported order-fulfillment process cycle times and Order Created → Shipped → Delivered transition bottlenecks;
- visible disclosure that these process analytics do not represent full manufacturing process mining.

---

## Page 10 — Healthcare Customer Operations

**Question:** How does enterprise performance translate into downstream customer service?

Required analysis:

- healthcare customer type/region;
- order/product demand patterns;
- delivery reliability;
- service levels/fulfillment;
- order exceptions;
- customer-service issue patterns;
- internal operational associations with downstream service.

No patient-identifiable information is used or required.

---

## Page 11 — Technology / Data Operations

**Question:** Can MEDNEXUS trust the systems and data supporting its decisions?

Required analysis:

- application/system incidents;
- availability/uptime/response time/failed deployments/support if implemented;
- incident severity and MTTR;
- usage/adoption;
- service degradation;
- Data Trust Score and components;
- data-quality/observability status;
- pipeline freshness/schema/row-count/failure state;
- technology reliability → data availability/trust relationship where supportable.

---

## Page 12 — Prediction, Forecast & Risk

**Question:** What is likely to happen next?

Required analysis:

- predictive-maintenance model comparison;
- precision/recall/F1/ROC-AUC/PR-AUC/confusion matrix;
- calibration/threshold/false-negative context where appropriate;
- explainability outputs;
- demand forecast and baseline/comparator backtest;
- forecast candidate comparison using MAE, RMSE and sMAPE on common rolling-origin periods;
- forecast error/bias and residual-autocorrelation diagnostics;
- explicit adequacy status versus naive forecasting; do not imply improvement when the selected model fails the benchmark gate;
- MORI trend/components/sensitivity;
- clear **Model-derived** disclosure.

---

## Page 13 — Scenario & Decision Intelligence

**Question:** What should management do?

Required analysis:

- scenario selector/what-if parameters;
- Baseline → Assumption → Expected Change → Result → Difference;
- simulated opportunity value;
- OEE/good units/downtime/capacity/cost/risk effects where supported;
- optimization recommendation only if a valid objective/constraint model exists;
- explicit optimization-gate status when a solver is not admitted;
- scenario ranking clearly labeled as heuristic rather than optimal;
- monitoring-plan panel showing metric, owner, frequency and required future validation design;
- priority DecisionQueue;
- owner/urgency/confidence/basis/limitations;
- monitoring plan for validating intervention results;
- experimentation-gate status showing that no treatment effect is estimated until executed intervention/comparison evidence exists.

Every scenario/optimization output must show a visible **Simulated** or decision-support label.

---

# Cross-report interaction requirements

Use only where they improve decision flow:

- synchronized date/plant slicers with valid filter paths;
- drill-through from enterprise → domain → entity detail;
- tooltip pages for metric definition/provenance/limitations;
- bookmarks for executive/detail views rather than decorative navigation;
- field parameters for legitimate measure/dimension switching;
- what-if parameters for scenario assumptions;
- dynamic titles reflecting selected period/entity;
- conditional formatting tied to documented thresholds;
- decomposition tree/Key Influencers for diagnostic association, not causal claims.

# Report-wide disclosure

At minimum, relevant pages must visibly distinguish:

- **Synthetic enterprise data**;
- **Illustrative assumption**;
- **Model-derived**;
- **Simulated**;
- **Project-defined index/metric**.

# Story order

**Business Health → Value Leakage → Workforce/Capacity → Production → Quality/Reliability → Supply/Logistics → Customer Impact → Technology/Data Trust → Prediction/Risk → Scenario/Decision → Monitoring**
