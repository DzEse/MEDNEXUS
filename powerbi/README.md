# MEDNEXUS Power BI Build Package

The final PBIX file is intentionally **not fabricated** by this repository. The user builds and validates the report in Power BI Desktop from the generated `powerbi/exports/` datasets and the documented semantic model, DAX and page specifications.

## Canonical report questions

The report architecture currently uses 13 pages so each canonical business question remains explicit:

1. **Enterprise Command Center** — Where is MEDNEXUS losing operational value?
2. **Finance & Business Health** — Where is financial performance being pressured?
3. **People, HR & Workforce** — Do we have the people and capacity required to operate the business?
4. **Recruitment & Capacity** — Where are talent gaps becoming operational constraints?
5. **Manufacturing Performance** — Where is productive capacity being lost?
6. **Quality & Process Intelligence** — Where are defects and process instability originating?
7. **Equipment & Reliability** — Which assets represent the greatest operational risk?
8. **Supply Chain & Inventory** — Are materials and suppliers constraining operations?
9. **Logistics & Customer Service** — Where are delivery and service failures occurring?
10. **Healthcare Customer Operations** — How does enterprise performance translate into downstream customer service?
11. **Technology / Data Operations** — Can MEDNEXUS trust the systems and data supporting its decisions?
12. **Prediction, Forecast & Risk** — What is likely to happen next?
13. **Scenario & Decision Intelligence** — What should management do?

Pages may later be consolidated only if every question, analytical layer, interaction and disclosure remains covered.

## Build artifacts

Use:

- `SEMANTIC_MODEL.md`
- `DAX_MEASURES.md`
- `PAGE_SPECIFICATIONS.md`
- `PAGE_01_ENTERPRISE_COMMAND_CENTER.md`
- `BUILD_GUIDE.md`
- `MEDNEXUS_THEME.json`

## Analytical dependency

The current Power BI work is a **preserved report shell**, not proof that every upstream analytical requirement is final. Review `../docs/specification/REQUIREMENTS_TRACEABILITY_MATRIX.md` before treating visuals as portfolio-final.

Report visuals depending on unresolved statistical-quality, COPQ/Six Big Losses, observability, model comparison/explainability, forecast comparison, optimization/process-mining gates or expanded scenario logic remain provisional until the corresponding analytical layer is validated.

## Required transparency

Use visible terminology where relevant:

- **Synthetic enterprise data**
- **Illustrative assumption**
- **Model-derived**
- **Simulated**
- **Project-defined index/metric**

Do not present MEDNEXUS as a real employer/client or generated outputs as real-company results.
