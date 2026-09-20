# Definition of Done

MEDNEXUS is **not** implementation-complete merely because the pipeline runs or a Power BI report exists.

The project is complete only when the canonical master specification is fully resolved through evidence or an explicit methodological gate.

Canonical governance:

- `docs/specification/MEDNEXUS_MASTER_BUILD_SPECIFICATION.md`
- `docs/specification/REQUIREMENTS_TRACEABILITY_MATRIX.md`
- `docs/specification/SCOPE_PRESERVATION_POLICY.md`
- `docs/MASTER_IMPLEMENTATION_BLUEPRINT.md`

## 1. Specification closure

- every one of the 57 canonical specification sections is represented in the traceability matrix;
- every one of the 60 original master-blueprint areas is present;
- every A01–A32 dataset/twin enhancement requirement and B01–B28 Command Center enhancement requirement is preserved in the enhancement traceability matrix and blueprint annexes;
- no canonical requirement is silently dropped, weakened or renamed away;
- every requirement is either implemented/evidenced or explicitly condition-gated with a defensible methodological reason;
- automated specification-preservation tests pass.

## 2. Data and architecture

- clean setup runs from a documented environment;
- synthetic data generation is deterministic across Python processes;
- public-source provenance/license/usage is verified for every public dataset actually used;
- raw/staging/curated/analytical/BI responsibilities are clear;
- dimensional grains, keys, cardinalities and refresh logic are documented;
- fact-to-fact/many-to-many ambiguity and duplicate multiplication are prevented;
- new table grains, keys, cross-domain links, event chronology and geospatial semantics are documented before promotion;
- inventory movement data reconciles opening balance + receipts − consumption ± adjustments = closing balance where applicable;
- enhanced dataset scale is justified by analytical/decision value rather than row-count optics;
- a small deterministic enhanced-data prototype passes relationship/calculation/Power BI-behavior validation before full scale-up;
- data-quality and referential-integrity gates pass;
- observability records freshness, row counts, schema, quality failures and pipeline status.

## 3. Business/KPI correctness

- core KPI formulas are tested and reconciled;
- OEE is mathematically correct and supported by an explicit loss decomposition;
- OLI is clearly distinguished from OEE;
- FPY/RTY/DPMO are used only when their required process/grain inputs exist;
- financial observed/derived values are separated from illustrative assumptions;
- COPQ/value-leakage metrics have transparent definitions and reconciliation;
- MORI methodology, weighting, normalization, sensitivity, missing-data handling and limitations are documented;
- Data Trust Score components are transparent and not presented as an industry standard.

## 4. Statistical and diagnostic validity

- statistical methods state assumptions, sample adequacy and limitations;
- process-control/capability methods are applied only when valid data/specification conditions exist;
- specification limits are never fabricated;
- root-cause outputs distinguish association from causation;
- diagnostic analyses identify evidence for investigation rather than unsupported causal conclusions.

## 5. Predictive analytics

- predictive baseline is temporally validated;
- a nonlinear comparator is evaluated where justified;
- advanced boosting is used only if evidence justifies the additional complexity;
- precision, recall, F1, ROC-AUC, PR-AUC and confusion matrix are reported where applicable;
- calibration is assessed when probability quality matters;
- threshold and false-negative/false-positive operational consequences are documented;
- leakage and train/test separation checks pass;
- explainability is used to understand model behavior, not infer causality.

## 6. Forecasting

- forecast baseline is backtested;
- at least one meaningful comparison is evaluated where the time series supports it;
- MAE/RMSE/bias and sMAPE or another safe percentage metric are used appropriately;
- zeros/near-zero denominators are handled correctly;
- forecast limitations and horizon are explicit.

## 7. Scenario, optimization and process analytics

- scenarios are explicitly labeled **Simulated**;
- scenario outputs show Baseline → Assumption → Expected Change → Result → Difference;
- optimization is implemented only if a defensible objective, variables and constraints exist, otherwise a documented gate decision exists;
- process mining is implemented only if a valid linked event log exists, otherwise a documented gate decision exists;
- experimentation is not fabricated; simulated/pre-post frameworks are labeled appropriately.

## 8. Decision intelligence

- decision queue includes evidence, risk, estimated impact, recommended action, owner, urgency, confidence, analytical basis and limitations;
- recommendations trace back to validated evidence;
- confidence does not hide uncertainty;
- monitoring/learning design explains how management would validate intervention results.

## 9. SQL/Python engineering

- SQL demonstrates controlled staging/quality/dimension/fact/KPI/analytical-view logic with documented grain;
- SQL validation protects against join/aggregation errors;
- Python production logic is modular;
- notebooks are used only for exploration/experimentation;
- reproducibility, validation and quality tests pass in CI/local build;
- no secrets or unnecessary regenerable artifacts are committed.

## 10. Power BI

- Power BI exports reconcile to analytical outputs;
- semantic relationships are valid and unambiguous;
- rate measures aggregate correctly;
- all canonical business questions are covered even if pages are consolidated;
- the flagship Command Center supports the governed Observe → Diagnose → Quantify → Predict → Prioritize → Simulate → Decide → Monitor → Learn lifecycle;
- global navigation, drill-through, map/twin behavior, filter persistence and back navigation are tested;
- map entities are synthetic/public as labeled and provide analytical value rather than decoration;
- analytical mode states distinguish Actual/Observed, Baseline, Simulated Scenario, Model-Derived and Forecast;
- drill-through/tooltips/bookmarks/field parameters/what-if parameters/dynamic titles/conditional formatting are used only where analytically useful;
- decomposition tree/Key Influencers are used only where their data/model semantics are defensible;
- synthetic/simulated/model-derived disclosures are visible;
- no PBIX file or screenshot is fabricated by the repository;
- real Command Center reconciliation/evidence is stored only after it exists, including KPI/DAX/map/navigation/scenario/reconciliation evidence and final screenshots/walkthrough.

## 11. Documentation, lineage and portfolio credibility

- Project Charter, Statement of Work, Business/Analytical Requirements, Data Architecture, Data Dictionary, KPI Dictionary, Provenance, Data Quality/Observability, Methodologies, Assumptions/Limitations, Validation, Lineage, Technical Documentation, Power BI guides and Repository/Reproducibility guides are complete;
- lineage can answer **“Where did this number come from?”** for important outputs;
- README accurately distinguishes implemented work from planned/conditional work;
- the final portfolio identifies the Executive Command Center, Enterprise Operations Twin, Enterprise Value-Loss Map, MORI, OLI, Data Trust Score, Decision Queue, Scenario Engine, Raw Data → Decision Trace and Analytics Assurance Report as signature artifacts only when their actual completion status supports it;
- no fabricated employment, client, customer outcome, savings, source, license, model performance or causal claim exists;
- user positioning demonstrates capability without exaggerating professional analytics experience;
- repository remains lightweight and feasible on a personal development machine.

## Final completion gate

All automated tests and reconciliation checks must pass, and every canonical requirement must have an evidence-backed final disposition in `REQUIREMENTS_TRACEABILITY_MATRIX.md`.
