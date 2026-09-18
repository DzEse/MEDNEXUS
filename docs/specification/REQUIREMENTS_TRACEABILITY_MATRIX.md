# MEDNEXUS Requirements Traceability Matrix

## Purpose

This document makes the canonical MEDNEXUS master specification enforceable in implementation. No requirement may be silently dropped, narrowed, renamed away, or treated as complete merely because a simpler baseline exists.

Canonical source: `docs/specification/MEDNEXUS_MASTER_BUILD_SPECIFICATION.md`.

## Status definitions

- **IMPLEMENTED** — working code/documentation exists and is exercised by the current pipeline or build package.
- **PARTIAL** — a defensible baseline exists, but the canonical requirement contains additional required depth.
- **PLANNED** — required by the canonical specification and not yet implemented.
- **CONDITIONAL-GATED** — the specification requires the technique to be considered, but it must only be implemented if the data/methodological assumptions support it. A documented gate decision is required; silence is not acceptable.
- **DOCUMENTED** — the architecture/method is documented, but implementation evidence is still required where applicable.

## Preservation rule

Existing validated work remains authoritative unless superseded by a stronger, tested implementation. New work is additive. A later phase may refine an earlier artifact, but it must preserve the original requirement, rationale, disclosures, validation controls, and evidence trail.

## Master traceability

| Spec section | Requirement area | Current state | Evidence / current artifact | Remaining canonical work |
|---|---|---|---|---|
| 1 | Project identity | IMPLEMENTED | README, Project Charter | Preserve naming and central executive question |
| 2 | Fictional enterprise disclosure | IMPLEMENTED | README, management summary, assumptions docs | Keep disclosure visible in every portfolio/report surface |
| 3 | Enterprise story / finance entry point | PARTIAL | EnterpriseMonthly, Finance, management summary | Add fuller cost-center/value-leakage analysis and executive narrative chain |
| 4 | HR / people / workforce | PARTIAL | Workforce synthetic fact, capacity-gap/overtime/absence metrics | Add turnover, roles, onboarding/training, utilization and workforce-risk structure where supportable |
| 5 | Recruitment & talent | PARTIAL | Recruitment funnel, time-to-fill, cost-per-hire | Add critical roles, skills shortages, bottleneck diagnostics and capacity linkage |
| 6 | Manufacturing | PARTIAL | Production, lines, machines, products, OEE inputs | Add shift/changeover/schedule-adherence/production-attainment treatment where justified |
| 7 | Quality intelligence | IMPLEMENTED/PARTIAL | Validated single-stage FPY, defect rate, Pareto, scrap/rework facts, explicit RTY/DPMO gates | Sequential-stage, supplier/material, shift and process-location analysis remain conditional on adding valid grain |
| 8 | Process capability & statistical quality | IMPLEMENTED/PARTIAL + CONDITIONAL GATE | Plant-day p-chart control layer implemented and tested; Cp/Cpk/Pp/Ppk explicitly NOT_CALCULABLE | Add other control-chart forms only when data structure supports them; capability remains gated until valid specification limits exist |
| 9 | OEE & loss intelligence | IMPLEMENTED/PARTIAL | Aggregate-grain OEE/OLI, Five calculable Big Loss categories, explicit Startup Reject gate, theoretical-capacity waterfall | Startup Rejects remain NOT_CALCULABLE until startup-period reject evidence exists |
| 10 | Maintenance & reliability | PARTIAL | Preventive/corrective maintenance, downtime, MTTR, MTBF proxy, machine age | Add utilization, backlog concept if supported, failure trends and stronger risk diagnostics |
| 11 | Predictive maintenance | IMPLEMENTED/PARTIAL | Logistic Regression vs Random Forest, strict train/validation/test temporal split, validation-only model/threshold selection, holdout precision/recall/F1/ROC-AUC/PR-AUC/Brier/confusion matrix, weighted error-cost analysis | Gradient boosting and recalibration remain conditional; persistent model-drift monitoring remains a later observability extension |
| 12 | Model explainability | IMPLEMENTED/PARTIAL | Holdout permutation importance with anti-causal interpretation labels | SHAP/PDP remain conditional and should be added only if stable and decision-useful beyond permutation importance |
| 13 | Supply chain | PARTIAL | Supplier reliability, lead-time proxy, shortages, material defects | Add material/inventory/purchase-order/stockout/excess-inventory structure if needed to support decisions |
| 14 | Logistics | PARTIAL | Orders, shipments, promised/actual dates, delays, on-time delivery | Add warehouse/carrier/route/exception/OTIF analysis where justified |
| 15 | Healthcare customer environment | PARTIAL | Customer types, orders, shipment reliability, service events | Add service-level/fulfillment/customer-pattern analytics while retaining no-PII rule |
| 16 | Technology / SaaS operations | PARTIAL | Incidents, severity, downtime, usage/adoption | Add availability/uptime/response/deployment/support/data-availability linkage and technology-risk diagnostics |
| 17 | Central enterprise value-loss chains | PARTIAL | Synthetic cross-domain relationships and decision queue | Quantify supported chains; label unsupported links conceptual/simulated/hypothesis |
| 18 | Five-level decision intelligence | IMPLEMENTED/PARTIAL | Descriptive KPIs, validated statistical/root-cause diagnostics, predictive maintenance, scenarios and decision queue | Prescriptive/optimization gate and monitor/learn intervention evidence remain open |
| 19 | MORI | IMPLEMENTED | Project-defined 8-component index with validated weight vector, fail-closed missing-data policy, exact contribution reconciliation, ±25% weight sensitivity, ±5-point threshold sensitivity, methodology/limitations evidence and Power BI sensitivity marts | Preserve project-defined/not-industry-standard labeling; external calibration and real-world predictive validity are explicitly not claimed |
| 20 | OLI | IMPLEMENTED | Aggregate-grain OLI plus capacity-waterfall/Six Big Losses interpretation | Preserve distinction from OEE and avoid treating gated startup loss as observed |
| 21 | Data Trust Score | IMPLEMENTED | Data Trust Score v2 with completeness, validity, consistency, uniqueness, timeliness, referential integrity, schema consistency and freshness | Preserve project-defined labeling; production alert thresholds remain environment-specific |
| 22 | Data quality & governance / observability | IMPLEMENTED/PARTIAL | Structural/business checks, orphan/RI hierarchy checks, schema signatures, freshness/timeliness, model-input sparsity/class balance, observability artifacts | Persistent cross-run row-count/missingness/category/model/KPI drift alerting remains a production-style extension |
| 23 | Forecasting | IMPLEMENTED/PARTIAL | 3-month moving-average baseline preserved; naive last-value, seasonal-naive and linear-trend comparators; common expanding-window rolling-origin backtest; MAE/RMSE/sMAPE/bias; residual autocorrelation diagnostics; explicit adequacy status versus naive; 3-month model-derived future forecast | Real-world generalization and richer time-series models remain unsupported by the current 24-month synthetic history; add other forecast targets only when independently justified |
| 24 | Optimization | CONDITIONAL-GATED / FORMALLY ASSESSED | Formal optimization admission gate implemented; no solver runs without defensible objective, intervention costs, resource/budget constraints and validated response functions; scenario prioritization remains heuristic | Reassess only when required decision-model evidence exists; do not convert simulated scenario ranking into an optimal recommendation |
| 25 | Process analytics / process mining | CONDITIONAL-GATED | No valid full event log yet | Build/gate event-log design for Order→Production→Inspection→Rework→Release→Shipment; do not fabricate events |
| 26 | Root-cause intelligence | IMPLEMENTED/PARTIAL | Pareto/trend plus Wilson-interval segmentation, FDR-adjusted Spearman/quartile contrasts, Kruskal-Wallis effect tests, grouped-binomial robust GLM/VIF, shallow diagnostic tree and investigation-priority outputs | Business/prospective validation remains required; outputs are association/investigation evidence, never causal attribution |
| 27 | COPQ & value leakage | IMPLEMENTED/PARTIAL | Cost per good unit, scrap/downtime/logistics/technology value leakage, known internal quality-cost proxy, explicit full-COPQ gate | Full COPQ and rework cost remain NOT_CALCULABLE until resource/external-failure cost evidence exists |
| 28 | Scenario engine | IMPLEMENTED | Explicit Baseline→Assumption→Expected Change→Result→Difference→Monitoring structure for reliability, quality, workforce and combined interventions; simulated opportunity-value reconciliation, deterministic ranking, assumptions and monitoring marts | Add new levers only when supported by defensible data/assumptions; outputs remain Simulated and non-causal |
| 29 | Decision queue | IMPLEMENTED | `mednexus/decision_queue.py`, DecisionQueue export | Enhance prioritization evidence only after new analytics; preserve confidence/basis/limitations |
| 30 | Enterprise Operations Twin | PLANNED/DOCUMENTED | Concept represented by dimensional hierarchy | Create formal conceptual twin artifact and cross-domain hierarchy; no 3D factory |
| 31 | Layered data architecture | PARTIAL | raw/staging/curated/BI folders, SQLite analytical layer | Make staging/analytical transformations more explicit and minimize duplicate CSV layers |
| 32 | Public data sources | PARTIAL | UCI AI4I, UCI SECOM, NASA C-MAPSS provenance entries | Verify current source/license details and add reproducible acquisition adapters only where used; do not misrepresent as MEDNEXUS proprietary |
| 33 | Synthetic data | IMPLEMENTED/PARTIAL | Deterministic generator with cross-domain logic | Expand only where required by unresolved domains; document every relationship and assumption |
| 34 | Storage/computational efficiency | IMPLEMENTED/PARTIAL | Compact generated data, ignored regenerable artifacts/PBIX | Evaluate Parquet where it materially improves storage; retain personal-machine feasibility |
| 35 | Data model | IMPLEMENTED/PARTIAL | Generated 21-table grain/PK/FK/cardinality/refresh/business register plus expanded Power BI exports | Add only dimensions/facts required by unresolved domains; keep semantic model synchronized |
| 36 | SQL requirements | IMPLEMENTED/PARTIAL | SQLite analytical views plus production, quality, finance and value-loss reconciliation views/tests | Deeper modular staging/dimension/fact SQL remains an extension where it adds real analytical value |
| 37 | Python architecture | IMPLEMENTED/PARTIAL | Modular `mednexus/` package now includes governance/observability, statistical quality, root-cause statistics, forecast validation and model explainability layers | Add dedicated feature-engineering/scenario-optimization modules only where later requirements justify them; notebooks remain exploratory |
| 38 | Power BI requirements | PARTIAL | Semantic model, DAX, build guide, theme, Page 1 spec | Add drill-through, bookmarks, tooltips, field parameters, what-if parameters, dynamic titles, decomposition tree, Key Influencers, commentary design where justified |
| 39 | Power BI story structure | PARTIAL | Current 10-page architecture + Page 1 detailed spec | Reconcile all 13 canonical business questions. Pages may be consolidated only if every question/requirement remains explicitly covered |
| 40 | Executive narrative | IMPLEMENTED/PARTIAL | Business health→loss→risk→scenario→action now includes explicit expected-result differences and scenario monitoring/learning plans | Final Power BI narrative implementation and post-intervention observed learning remain open |
| 41 | Experimentation | CONDITIONAL-GATED | No fabricated experiment | Define pre/post or treatment/control framework for future interventions; only calculate when valid evidence exists |
| 42 | Testing & validation | IMPLEMENTED/PARTIAL | 63-test suite covering reproducibility, governance, KPI/statistical quality, SQL reconciliation, ML, root-cause, forecast, MORI, and scenario baseline/reconciliation/ranking/monitoring/optimization-gate validation | Process-mining/experimentation gates and final BI/reconciliation closeout still require dedicated tests |
| 43 | Data lineage | PARTIAL | LINEAGE.md and manifests | Expand output-level Source→Transformation→Table→Method→KPI/Model→BI→Decision lineage |
| 44 | Documentation | IMPLEMENTED/PARTIAL | Named core docs plus generated field-level Data Dictionary and table register | Continue updating canonical docs as later analytics close; keep interview defense outside repo |
| 45 | Repository structure | IMPLEMENTED/PARTIAL | Professional compact structure | Add substructure only when real artifacts exist; do not create empty appearance folders |
| 46 | User professional story | DOCUMENTED | Portfolio strategy / positioning docs | Preserve truthful transferable-skill framing; no invented analytics employment |
| 47 | Professional positioning | DOCUMENTED | Portfolio strategy | Preserve simulated-engagement vs analyst-demonstration distinction |
| 48 | Analytical discipline | PLANNED AS GATE | Methodology docs | Add reusable analysis-design checklist requiring business question/grain/data/assumptions/bias/proof/decision/validation |
| 49 | Anti-fabrication | IMPLEMENTED AS POLICY | Disclosures, assumptions/limitations | Add automated/text QC where practical; preserve labels: To be calculated / Simulated / Illustrative / Model-derived / Conceptual |
| 50 | Quality-control standard | PARTIAL | Tests, docs, reproducibility | Formalize final cross-functional QC checklist with pass/fail evidence |
| 51 | 60-part master blueprint output | PARTIAL | Multiple docs cover many areas | Create one indexed master implementation blueprint linking all 60 required areas |
| 52 | Phases 0–17 | IMPLEMENTED AS PLAN / PARTIAL IN EXECUTION | `docs/IMPLEMENTATION_PHASES.md` | Rebaseline actual status; do not call Phase 13/14 complete until predecessor gaps are resolved/gated |
| 53 | Judgment over superficial complexity | IMPLEMENTED AS POLICY | Methodology and repository approach | Continue conditional gating instead of forced techniques |
| 54 | Final success chain | PARTIAL | Core chain exists | Add stronger statistical diagnostics, optimization/prescription where valid, and post-intervention monitoring framework |
| 55 | Non-negotiable professional standard | ACTIVE GOVERNANCE | Canonical specification + this matrix | Use as final acceptance gate across analytics, engineering, BI, finance and operations |

## Immediate sequencing correction

The project had begun Power BI Page 1 preparation before all predecessor analytical requirements were closed. The Power BI handoff already created remains valid and is preserved, but **final report development is paused as the next major workstream** until the following predecessor gaps are closed or explicitly condition-gated:

1. statistical/quality-analysis layer and capability/control gate;
2. predictive-maintenance model comparison, calibration/threshold evidence and explainability — **resolved in Phase 5**; advanced boosting/SHAP remain condition-gated;
3. expanded data quality, referential-integrity and observability controls;
4. diagnostic/root-cause statistical layer;
5. forecast comparator/validation expansion — **resolved in Phase 7** with rolling-origin common-window comparison, sMAPE/bias/residual diagnostics and explicit naive-benchmark adequacy gate;
6. OEE Six Big Losses / COPQ / value-leakage decomposition;
7. scenario engine expansion and optimization decision gate;
8. process-mining event-log feasibility gate;
9. deeper SQL staging/quality/dimensional/KPI/reconciliation layer;
10. table-level grain/PK/FK/cardinality/refresh dictionary and output-level lineage.

Power BI Page 1 artifacts are **not discarded**. They become the validated report shell to be refreshed after these analytical layers produce final canonical measures.

## Acceptance rule

A requirement can move to **IMPLEMENTED** only when there is:

1. an artifact or executable implementation;
2. a documented business purpose and grain;
3. validation evidence appropriate to the method;
4. limitations/assumptions documented;
5. traceability to the decision or report output it supports.

No status may be upgraded based only on intent or documentation describing work that has not been executed.
