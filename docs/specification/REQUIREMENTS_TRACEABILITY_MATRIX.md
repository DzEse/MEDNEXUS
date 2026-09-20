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
| 22 | Data quality & governance / observability | IMPLEMENTED | Structural/business checks, RI hierarchy, schema/freshness/timeliness, model-input profile, Data Trust, and persistent cross-run row-count/missingness/schema/category/model-target/KPI drift comparison with local runtime baseline | Production alert delivery/incident routing remains environment-specific and is not simulated |
| 23 | Forecasting | IMPLEMENTED/PARTIAL | 3-month moving-average baseline preserved; naive last-value, seasonal-naive and linear-trend comparators; common expanding-window rolling-origin backtest; MAE/RMSE/sMAPE/bias; residual autocorrelation diagnostics; explicit adequacy status versus naive; 3-month model-derived future forecast | Real-world generalization and richer time-series models remain unsupported by the current 24-month synthetic history; add other forecast targets only when independently justified |
| 24 | Optimization | CONDITIONAL-GATED / FORMALLY ASSESSED | Formal optimization admission gate implemented; no solver runs without defensible objective, intervention costs, resource/budget constraints and validated response functions; scenario prioritization remains heuristic | Reassess only when required decision-model evidence exists; do not convert simulated scenario ranking into an optimal recommendation |
| 25 | Process analytics / process mining | CONDITIONAL-GATED / FORMALLY ASSESSED | Source-backed order-fulfillment event log and cycle-time/transition analytics implemented for Order Created→Shipped→Delivered→optional Service Issue; full manufacturing mining gate explicitly closed because order→production→inspection/rework/release case linkage is absent | Add full process mining only if defensible end-to-end case linkage is introduced; never fabricate missing events |
| 26 | Root-cause intelligence | IMPLEMENTED/PARTIAL | Pareto/trend plus Wilson-interval segmentation, FDR-adjusted Spearman/quartile contrasts, Kruskal-Wallis effect tests, grouped-binomial robust GLM/VIF, shallow diagnostic tree and investigation-priority outputs | Business/prospective validation remains required; outputs are association/investigation evidence, never causal attribution |
| 27 | COPQ & value leakage | IMPLEMENTED/PARTIAL | Cost per good unit, scrap/downtime/logistics/technology value leakage, known internal quality-cost proxy, explicit full-COPQ gate | Full COPQ and rework cost remain NOT_CALCULABLE until resource/external-failure cost evidence exists |
| 28 | Scenario engine | IMPLEMENTED | Explicit Baseline→Assumption→Expected Change→Result→Difference→Monitoring structure for reliability, quality, workforce and combined interventions; simulated opportunity-value reconciliation, deterministic ranking, assumptions and monitoring marts | Add new levers only when supported by defensible data/assumptions; outputs remain Simulated and non-causal |
| 29 | Decision queue | IMPLEMENTED | `mednexus/decision_queue.py`, DecisionQueue export | Enhance prioritization evidence only after new analytics; preserve confidence/basis/limitations |
| 30 | Enterprise Operations Twin | IMPLEMENTED/DOCUMENTED | Formal conceptual cross-domain twin catalog covers Enterprise→Plant→Line→Machine plus workforce, supply, customer/order/shipment, finance, technology, MORI and scenario links; machine-readable twin artifact generated | Preserve conceptual analytical-twin semantics; no 3D/cyber-physical claim |
| 31 | Layered data architecture | IMPLEMENTED | Explicit Raw/Synthetic→Staging/Validation→Curated→Analytical SQL/Python→BI→Governance architecture; logical staging SQL avoids unnecessary duplicate persisted copies | Public-source staging expands only if public data is actually activated |
| 32 | Public data sources | PARTIAL | UCI AI4I, UCI SECOM, NASA C-MAPSS provenance entries | Verify current source/license details and add reproducible acquisition adapters only where used; do not misrepresent as MEDNEXUS proprietary |
| 33 | Synthetic data | IMPLEMENTED/PARTIAL | Deterministic generator with cross-domain logic | Expand only where required by unresolved domains; document every relationship and assumption |
| 34 | Storage/computational efficiency | IMPLEMENTED/PARTIAL | Compact generated data, ignored regenerable artifacts/PBIX | Evaluate Parquet where it materially improves storage; retain personal-machine feasibility |
| 35 | Data model | IMPLEMENTED/PARTIAL | Generated table register plus machine-readable Power BI table-role/relationship contract, one-side key/orphan audit, ambiguity guard and headline reconciliation targets | Build the validated contract physically in Power BI Desktop and reconcile the actual PBIX model before final acceptance |
| 36 | SQL requirements | IMPLEMENTED | SQLite analytical/reconciliation views plus explicit staging, dimensional hierarchy, enriched fact, KPI, validation, CASE, CTE, window/LAG/rolling and ranking views with grain tests | Extend SQL only for future valid business requirements; do not duplicate Python logic without decision value |
| 37 | Python architecture | IMPLEMENTED/PARTIAL | Modular `mednexus/` package now includes governance/observability, statistical quality, root-cause statistics, forecast validation and model explainability layers | Add dedicated feature-engineering/scenario-optimization modules only where later requirements justify them; notebooks remain exploratory |
| 38 | Power BI requirements | IMPLEMENTED/PARTIAL | Ambiguity-safe semantic-model contract, table-role contract, DAX library, theme, build guide, page specifications and automated export/relationship audit are complete | Build the actual PBIX and add drill-through/tooltips/bookmarks/field parameters/what-if/dynamic titles only where page decisions justify them |
| 39 | Power BI story structure | DOCUMENTED/READY FOR BUILD | 13 canonical business questions are specified in PAGE_SPECIFICATIONS.md and Build Guide; semantic contract now validated | Actual page construction, interactions and visual reconciliation in Power BI Desktop remain |
| 40 | Executive narrative | IMPLEMENTED/PARTIAL | Business health→loss→risk→scenario→action now includes explicit expected-result differences and scenario monitoring/learning plans | Final Power BI narrative implementation and post-intervention observed learning remain open |
| 41 | Experimentation | CONDITIONAL-GATED / FORMALLY ASSESSED | Prospective experiment-design hierarchy and minimum future fields documented; gate explicitly closed because no executed treatment assignment, comparison group, or observed post-intervention outcomes exist | Estimate treatment effects only after intervention execution, comparison design, pre/post evidence and assumption checks exist |
| 42 | Testing & validation | IMPLEMENTED/PARTIAL | 103-test suite covering prior analytical gates plus Power BI export synchronization, relationship cardinality/direction, disconnected-table enforcement, ambiguity guards, inactive date roles and headline reconciliation-target generation | Actual PBIX relationship/headline reconciliation and portfolio closeout remain |
| 43 | Data lineage | IMPLEMENTED | Expanded LINEAGE.md plus generated output lineage registry covering Source→Transformation→Artifact/Table→Method/KPI/Model→BI Surface→Decision for headline outputs | Final Power BI reconciliation will validate displayed measures against this lineage |
| 44 | Documentation | IMPLEMENTED/PARTIAL | Named core docs plus generated field-level Data Dictionary and table register | Continue updating canonical docs as later analytics close; keep interview defense outside repo |
| 45 | Repository structure | IMPLEMENTED/PARTIAL | Professional compact structure | Add substructure only when real artifacts exist; do not create empty appearance folders |
| 46 | User professional story | DOCUMENTED | Portfolio strategy / positioning docs | Preserve truthful transferable-skill framing; no invented analytics employment |
| 47 | Professional positioning | DOCUMENTED | Portfolio strategy | Preserve simulated-engagement vs analyst-demonstration distinction |
| 48 | Analytical discipline | IMPLEMENTED AS GATE | Reusable 10-part analysis-design checklist and machine-readable gate require business question, grain, data, assumptions, bias/leakage, method suitability, proof boundary, validation, decision and monitoring | Apply the gate to any future major analytical extension |
| 49 | Anti-fabrication | IMPLEMENTED AS POLICY | Disclosures, assumptions/limitations | Add automated/text QC where practical; preserve labels: To be calculated / Simulated / Illustrative / Model-derived / Conceptual |
| 50 | Quality-control standard | IMPLEMENTED/PARTIAL | Formal cross-functional final QC checklist now covers analytical integrity, engineering, Power BI and portfolio integrity | Execute and record final pass/fail only after Power BI build/reconciliation and documentation closeout |
| 51 | 60-part master blueprint output | IMPLEMENTED | `docs/MASTER_IMPLEMENTATION_BLUEPRINT.md` is the single indexed 60-section implementation blueprint tied to the canonical specification/traceability matrix | Keep links/status language synchronized through final closeout |
| 52 | Phases 0–17 | IMPLEMENTED AS PLAN / PARTIAL IN EXECUTION | Backend/analytical predecessors and Phase-12 semantic baseline are closed; Phase 12E.1 enhanced-data structural prototype is CI-validated and remains unpromoted | Complete local Phase 12E evidence/filter-behavior gates, then promote accepted structures before final PBIX construction |
| 53 | Judgment over superficial complexity | IMPLEMENTED AS POLICY | Methodology and repository approach | Continue conditional gating instead of forced techniques |
| 54 | Final success chain | IMPLEMENTED/PARTIAL | Problem→validated data→diagnostics→statistics→prediction/forecast→risk→scenario/decision→monitoring framework is implemented; optimization/process mining/experimentation are condition-gated where evidence is insufficient | Actual Power BI communication/reconciliation and observed post-intervention learning remain final-stage work |
| 55 | Non-negotiable professional standard | ACTIVE GOVERNANCE | Canonical specification + this matrix | Use as final acceptance gate across analytics, engineering, BI, finance and operations |
| 56 | Enterprise Dataset & Digital Twin Enhancement | PARTIAL / PROTOTYPE VALIDATED | Canonical 32-requirement enhancement plus Phase 12E.1: 20 prototype tables, 6,450 rows, 62 checks, 0 failures in full CI; canonical semantic and 53-export contracts unchanged | Run local evidence/storage and Power BI filter-behavior gates, then promote only justified tables/entities/events |
| 57 | Flagship Executive Command Center Enhancement | PARTIAL / DESIGN-READY, BUILD DEFERRED | Canonical 28-requirement Command Center spec plus B01–B28 traceability; existing Page 1 shell and Phase-12 semantic contract preserved | Complete enhanced data/twin predecessor work, regenerate semantic contract, then build/reconcile actual flagship PBIX, navigation, map, scenarios, commentary and evidence pack |

## Enhancement sequencing correction

The September 2026 enhancement adds new inventory, geospatial, event, workforce, recruitment, logistics, technology and cross-domain requirements that can change Power BI grains and relationships. Therefore:

1. preserve the Phase-12 53-export / ambiguity-safe semantic-model contract as a validated baseline;
2. define enhanced business questions, grains, KPI dependencies and required fields;
3. build a small deterministic prototype rather than immediately scaling row counts — **completed in Phase 12E.1**;
4. validate referential integrity, event chronology, inventory balance logic and calculations — **completed in CI with 62/62 checks**;
5. complete local evidence/storage benchmarking and validate Power BI filter behavior against the prototype;
6. promote only justified entities/tables/fields;
7. regenerate the semantic-model audit and reconciliation targets;
8. then resume final PBIX construction and flagship Command Center implementation.

The existing Power BI shell is not discarded. Final PBIX construction is simply moved behind the richer-data validation gate to avoid deliberate rework.

## Immediate sequencing correction

The project had begun Power BI Page 1 preparation before all predecessor analytical requirements were closed. The Power BI handoff already created remains valid and is preserved, but **final report development is paused as the next major workstream** until the following predecessor gaps are closed or explicitly condition-gated:

1. statistical/quality-analysis layer and capability/control gate;
2. predictive-maintenance model comparison, calibration/threshold evidence and explainability — **resolved in Phase 5**; advanced boosting/SHAP remain condition-gated;
3. expanded data quality, referential-integrity and observability controls;
4. diagnostic/root-cause statistical layer;
5. forecast comparator/validation expansion — **resolved in Phase 7** with rolling-origin common-window comparison, sMAPE/bias/residual diagnostics and explicit naive-benchmark adequacy gate;
6. OEE Six Big Losses / COPQ / value-leakage decomposition;
7. scenario engine expansion and optimization decision gate;
8. process-mining event-log feasibility gate — **resolved in Phase 10** with supported order-fulfillment analytics and full manufacturing-mining fail-closed gate;
9. deeper SQL staging/quality/dimensional/KPI/reconciliation layer — **resolved in Phase 11** with explicit layered SQL and grain validation;
10. table-level grain/PK/FK/cardinality/refresh dictionary and output-level lineage — **resolved through governance/data-dictionary work and Phase 11 output-lineage registry**.

Power BI predecessor analytics are now closed or explicitly gated. Page 1 artifacts remain preserved, and final Power BI development may now resume against the validated semantic-model contract and reconciliation targets.

## Acceptance rule

A requirement can move to **IMPLEMENTED** only when there is:

1. an artifact or executable implementation;
2. a documented business purpose and grain;
3. validation evidence appropriate to the method;
4. limitations/assumptions documented;
5. traceability to the decision or report output it supports.

No status may be upgraded based only on intent or documentation describing work that has not been executed.
