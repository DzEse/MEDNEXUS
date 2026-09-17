# Assumptions and Limitations

## Assumptions

- Default enterprise data is synthetic and reproducible.
- Unit prices and cost parameters are synthetic.
- $12/min downtime cost is an illustrative financial assumption.
- Technology incident cost mapping is illustrative.
- Scenario response relationships are simplified and explicitly simulated.
- Each shipment fulfills the modeled order quantity; therefore on-time delivery is used as an OTIF proxy.
- In the canonical generator, defect_units are units failing the first pass; rework_units are the recovered subset and scrap_units are unrecovered units.

## Limitations

- Synthetic data cannot demonstrate real-world generalization.
- The predictive-maintenance target is generated from simulated relationships.
- Causal effects are not identified.
- No patient-level data is present.
- No valid engineering specification limits are available, so Cp/Cpk/Pp/Ppk are intentionally omitted.
- No sequential process-stage yield data exists, so RTY is intentionally omitted.
- Opportunities per unit are undefined, so DPMO is intentionally omitted.
- Startup-period rejects are not separately identified, so the sixth Big Loss category cannot be quantified directly.
- Rework resource cost and external failure cost are not separately observed, so full COPQ is intentionally omitted.
- p-chart signals indicate statistical behavior requiring investigation, not causal explanations.
- Power BI is specified but the PBIX file must be built by the user.
