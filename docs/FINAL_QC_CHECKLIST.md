# Final Quality-Control Checklist

This checklist is the final cross-functional acceptance framework. It is not considered fully passed until the Power BI report, final reconciliation, documentation closeout and portfolio package are complete.

## Analytical integrity

- [ ] Business questions map to validated outputs.
- [ ] Table grains and joins are valid.
- [ ] KPI formulas and aggregation behavior reconcile.
- [ ] Statistical methods match assumptions and sample structure.
- [ ] Predictive models preserve temporal separation and leakage controls.
- [ ] Forecasts retain comparator, bias and adequacy evidence.
- [ ] Scenario outputs remain visibly Simulated.
- [ ] Optimization/process-mining/experimentation gates remain fail-closed where evidence is insufficient.
- [ ] Causal claims are absent unless a valid causal design exists.

## Data and engineering

- [ ] Data Trust and integrity gates pass.
- [ ] Persistent observability drift checks are reviewed.
- [ ] SQL layer grain validations pass.
- [ ] Output-level lineage reaches BI and management decisions.
- [ ] Reproducibility manifest matches the generated BI handoff.
- [ ] Repository remains lightweight and personal-machine feasible.

## Power BI

- [ ] Star-schema relationships are one-to-many/single direction where intended.
- [ ] No ambiguous active filter paths remain.
- [ ] Disconnected evidence/scenario marts stay disconnected.
- [ ] All 13 canonical business questions are covered.
- [ ] Headline Power BI values reconcile to analytical outputs.
- [ ] Simulated, Model-derived, Illustrative and Project-defined labels remain visible.

## Portfolio integrity

- [ ] Fictional/simulated enterprise disclosure is visible.
- [ ] No invented employer/client/proprietary-data claim exists.
- [ ] No realized savings are claimed from simulated scenarios.
- [ ] Public sources actually used have verified provenance/license/usage notes.
- [ ] README and screenshots reflect validated outputs only.
- [ ] Requirements traceability contains no silently unresolved requirement.


## Enhanced dataset / twin acceptance

- [ ] Every promoted new table/field has a documented business/analytical/decision purpose.
- [ ] A01–A32 are resolved through evidence or explicit gate.
- [ ] Enhanced grains, PKs, FKs, cardinalities, refresh logic and transformation rules are documented.
- [ ] Event chronology is valid and optional events are not fabricated.
- [ ] Inventory opening + receipts − consumption ± adjustments = closing within documented tolerance where applicable.
- [ ] Geospatial entities are synthetic/public as labeled and coordinates are plausible.
- [ ] Synthetic dependency rules are documented as generation assumptions rather than empirical causality.
- [ ] Expanded temporal depth supports the intended comparisons without forced seasonality.
- [ ] Prototype runtime/storage remains manageable on a personal development machine.
- [ ] Full scale-up occurred only after prototype relationship/calculation/Power BI-behavior validation.

## Flagship Command Center acceptance

- [ ] B01–B28 are resolved through evidence or explicit gate.
- [ ] Analytical mode visibly distinguishes Actual/Observed, Baseline, Simulated Scenario, Model-Derived and Forecast.
- [ ] Global navigation, bookmarks, drill-through, back buttons and filter persistence have real test evidence.
- [ ] Enterprise map entities/filters are validated and do not introduce ambiguous relationships.
- [ ] Enterprise Operations Twin drill paths expose only evidence-backed contributions.
- [ ] Enterprise Value-Loss Map distinguishes Observed, Derived, Model-Derived, Simulated Opportunity and Conceptual relationships.
- [ ] Forecast/early-warning surfaces expose method, validation, error, bias, assumptions and limitations.
- [ ] Scenario launchpad remains visibly simulated and non-causal.
- [ ] Executive commentary is evidence-class-aware and contains no unsupported causal claims.
- [ ] Evidence pack contains real KPI/DAX/map/MORI/OLI/scenario/navigation/reconciliation evidence and actual screenshots/walkthrough only after creation.
