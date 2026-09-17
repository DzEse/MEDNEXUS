# MEDNEXUS Scope Preservation Policy

## Authority

The canonical requirements source is:

`docs/specification/MEDNEXUS_MASTER_BUILD_SPECIFICATION.md`

The implementation status authority is:

`docs/specification/REQUIREMENTS_TRACEABILITY_MATRIX.md`

This policy governs all future MEDNEXUS changes.

## Non-dropping rule

No future implementation step may silently delete, weaken, narrow, or supersede a canonical requirement.

If a requirement is not appropriate to the available data or business question, it must be handled explicitly as one of:

- **Implemented** — executed and validated;
- **Conditional-gated / not justified** — assessed and intentionally not executed, with methodological reason;
- **Deferred** — still required but dependent on an unmet prerequisite;
- **Replaced by stronger method** — original intent preserved and replacement rationale documented.

Silence is not a valid disposition.

## Additive preservation

Validated existing assets are retained unless a stronger implementation replaces them. Replacement requires:

1. explicit reason;
2. preserved business intent;
3. preserved or improved data/grain validity;
4. tests/reconciliation;
5. documentation and lineage update;
6. no loss of disclosure, assumptions or limitations.

The following completed work is therefore preserved:

- deterministic synthetic enterprise generator;
- cross-process reproducibility hardening;
- data-quality gate and current Data Trust Score implementation;
- SQLite analytical database and SQL views;
- OEE/OLI baseline;
- Logistic Regression predictive-maintenance baseline;
- demand-forecast baseline;
- MORI baseline;
- scenario baseline;
- decision queue;
- 29-file Power BI export contract;
- semantic-model blueprint;
- Page 1 Enterprise Command Center shell/design;
- fictional/synthetic/simulated/model-derived disclosures;
- GitHub/VS Code build workflow.

These are baselines, not proof that every canonical requirement is finished.

## Priority hierarchy

Every design decision must follow:

**ACCURACY → BUSINESS LOGIC → DATA INTEGRITY → ANALYTICAL VALIDITY → REPRODUCIBILITY → DECISION VALUE → TECHNICAL DEPTH → VISUAL POLISH**

When two requirements appear to conflict, select the implementation that best preserves this hierarchy and document the decision.

## Evidence discipline

For every major analytical component, record:

- purpose;
- business question;
- unit of analysis;
- grain;
- required data;
- data availability;
- assumptions;
- methodology;
- formula where applicable;
- bias/leakage risks;
- validation;
- what the result supports;
- what it does not prove;
- limitations;
- expected output;
- decision supported.

## Anti-fabrication labels

Use these exact concepts consistently:

- **To be calculated during implementation** — requested but not yet calculated;
- **Simulated** — produced by a scenario/simulation rather than observed outcome;
- **Illustrative assumption** — project-defined assumption not observed as company fact;
- **Model-derived** — output produced by a statistical/ML model;
- **Conceptual framework** — architecture or relationship not empirically established.

Never convert association, feature importance, scenario response, synthetic-generation logic, or a project-defined index into a causal or real-company claim.

## Conditional-technique gate

The following techniques are never automatically required merely because they appear in the specification:

- Cp/Cpk/Pp/Ppk;
- specification-limit analysis;
- X-bar/R, I-MR, p or np charts;
- RTY;
- DPMO;
- Gradient Boosting/XGBoost;
- SHAP;
- partial dependence;
- optimization;
- process mining;
- formal experimentation.

Each must have a documented suitability decision. If the data does not support the technique, the correct output is the gate decision and the strongest valid alternative—not fabricated inputs.

## Phase integrity

Power BI design may proceed as a report shell, but final BI acceptance cannot precede the analytical layers that feed it. Any report visual depending on an unresolved requirement must be marked provisional until its source method passes validation.

## Change-control checklist

Before every future commit that changes analytical logic:

- [ ] identify canonical requirement(s) affected;
- [ ] preserve valid existing functionality;
- [ ] document grain and assumptions;
- [ ] update tests/reconciliation;
- [ ] update lineage and traceability status;
- [ ] regenerate canonical outputs if logic changed;
- [ ] verify disclosures remain accurate;
- [ ] verify no unsupported causal or business claim was introduced;
- [ ] verify storage/computational impact remains reasonable;
- [ ] verify Power BI contract if BI-facing tables/measures changed.

## Completion rule

MEDNEXUS is not complete because a dashboard exists. It is complete only when the traceability matrix, Definition of Done and final quality-control checklist show that every canonical requirement is either:

1. implemented and evidenced, or
2. explicitly condition-gated with a defensible methodological reason.
