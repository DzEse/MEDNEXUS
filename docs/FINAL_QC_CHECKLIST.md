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
