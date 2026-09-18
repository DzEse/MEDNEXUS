# Analysis Design Checklist

Every new major MEDNEXUS analysis must pass this design gate before it is treated as canonical.

1. **Business question** — What decision-relevant question is being answered?
2. **Unit and grain** — What is the unit of analysis and grain?
3. **Required data** — Which source tables/fields are required and linked validly?
4. **Assumptions** — Which inputs are observed, derived, illustrative, simulated or model-derived?
5. **Bias and leakage** — What selection, leakage, confounding or survivorship risks apply?
6. **Method suitability** — Why is the selected method appropriate?
7. **Proof boundary** — What does the result prove and explicitly not prove?
8. **Validation** — Which reconciliation, benchmark, test or gate validates it?
9. **Decision supported** — Which management decision can legitimately use the evidence?
10. **Monitoring** — How will the metric/model/intervention be monitored over time?

Machine-readable gate:

`artifacts/validation/analysis_design_checklist.csv`

A method is not accepted merely because code executes or a p-value/model metric exists.
