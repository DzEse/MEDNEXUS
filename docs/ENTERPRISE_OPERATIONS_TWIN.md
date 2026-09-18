# Enterprise Operations Twin

## Purpose

The MEDNEXUS Enterprise Operations Twin is a **conceptual analytical twin**, not a 3D factory model.

It represents how enterprise entities, operational facts, analytical marts, risk outputs, scenarios and management decisions relate across the business.

## Canonical hierarchy

**Enterprise → Plant → Line → Machine**

Operational evidence attaches to that hierarchy through:

- production;
- downtime;
- quality;
- maintenance;
- sensor observations.

Cross-domain structures include:

- Plant → Workforce / Recruitment;
- Supplier → Supply;
- Customer → Order → Shipment → Customer Service;
- Enterprise → Finance;
- Enterprise → Technology incidents / SaaS usage;
- Enterprise → Enterprise Monthly Mart → MORI / scenarios / decisions.

## Governance

The machine-readable representation is:

`artifacts/validation/enterprise_operations_twin.csv`

Every edge records:

- source entity;
- target entity;
- relationship type;
- link key;
- target grain;
- evidence status.

The twin is used to explain cross-domain structure and decision flow. It does not imply a real-time cyber-physical digital twin, a 3D simulation, or causal relationships.
