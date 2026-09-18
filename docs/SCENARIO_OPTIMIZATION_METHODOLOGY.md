# Scenario and Optimization Methodology

## Purpose

Scenario analysis estimates how selected operational levers could change enterprise outcomes under explicit simulated assumptions.

All scenario outputs are **Simulated**. They are not realized savings, forecasts, causal effects, or evidence that an intervention will achieve the stated result.

## Canonical scenario flow

Every scenario follows:

**Baseline → Assumption → Expected Change → Result → Difference → Monitoring**

The current baseline is the latest enterprise monthly period.

## Scenario levers

The current validated levers are:

- unplanned-downtime reduction;
- defect reduction;
- workforce capacity-gap improvement.

The current response relationship for simulated throughput is an illustrative assumption retained from the original transparent scenario baseline. It is not estimated from causal intervention evidence.

## Financial semantics

Simulated opportunity value uses only supported proxies:

- downtime-cost reduction from the documented downtime-cost assumption;
- scrap-cost reduction from the synthetic scrap-cost field.

It excludes rework cost, external-failure cost and any unobserved intervention cost.

Therefore:

**Simulated opportunity value ≠ realized savings.**

## Scenario prioritization

Non-baseline scenarios are ranked by:

1. simulated opportunity value;
2. simulated good-unit improvement as a tie-breaker.

This is a scenario-prioritization heuristic, not mathematical optimization.

## Monitoring

Each intervention scenario produces a monitoring plan for:

- unplanned downtime;
- defect units;
- capacity gap;
- good units.

The plan requires observed post-intervention data and an appropriate pre/post, controlled, or other defensible comparison before causal claims.

## Optimization gate

Formal optimization is currently **not admitted**.

Required evidence that is still missing includes:

- observed intervention implementation costs by lever;
- validated budget/resource constraints;
- validated response functions;
- intervention resource-consumption requirements;
- management objective trade-off weights or utility.

No solver is executed while those requirements are missing.

This preserves the distinction between scenario comparison and an optimization problem.
