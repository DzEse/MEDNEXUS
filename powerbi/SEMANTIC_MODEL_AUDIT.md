# Power BI Semantic-Model Audit

## Status

The repository can validate the **intended semantic model contract**, but it does not pretend a PBIX file has been created or inspected.

Phase 12 generates:

- `powerbi_semantic_relationships.csv` — canonical relationship list;
- `powerbi_table_roles.csv` — connected vs disconnected table roles;
- `powerbi_semantic_audit.json` — machine-readable audit result;
- `powerbi_semantic_issues.csv` — issue list, empty on a passing canonical build;
- `powerbi_headline_reconciliation_targets.csv` — expected executive values for later PBIX reconciliation.

## Automated checks

The audit fails on:

- missing required exports;
- unexpected export-contract drift;
- one-side null keys;
- one-side duplicate keys;
- relationship orphans;
- non-1:* cardinality;
- non-single-direction filtering;
- relationships touching a table declared disconnected;
- multiple active filter paths from the same source dimension to the same target.

## Operations-hierarchy decision

The validated hierarchy is:

**DimPlant → DimLine → DimMachine → machine-grain operational fact**

Direct active Plant/Line relationships to machine-grain facts are intentionally excluded because they create parallel filter paths.

## Date-role decision

Every connected fact has one canonical active date role.

Shipment promised date and actual-delivery date are optional **inactive** roles and must only be activated by an explicit measure.

## Reconciliation targets

`powerbi_headline_reconciliation_targets.csv` records the exact latest-month analytical values that the eventual PBIX must display for executive measures including:

- Revenue;
- Operating Cost;
- Operating Margin Proxy;
- OEE;
- OLI;
- FPY;
- Defect Rate;
- On-Time Delivery;
- Capacity Gap;
- Supplier Reliability;
- Technology Downtime;
- MORI.

The file is a target contract, not evidence that Power BI has already matched it.

## Acceptance boundary

Phase 12 can establish:

**SEMANTIC MODEL CONTRACT VALIDATED**

It cannot establish:

**PBIX MODEL BUILT / REPORT RECONCILED**

Those require the user to create/open the model in Power BI Desktop and verify the actual relationships and displayed values.
