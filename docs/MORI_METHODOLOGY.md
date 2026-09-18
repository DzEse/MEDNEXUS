# MORI Methodology

## Purpose

The **MEDNEXUS Operational Risk Index (MORI)** is a project-defined composite risk index used to summarize cross-domain operational pressure for executive decision support.

It is **not an industry-standard risk scale**, externally calibrated score, regulatory metric, or causal model.

## Components and canonical weights

| Component | Weight |
|---|---:|
| Quality | 0.16 |
| Equipment | 0.16 |
| Downtime | 0.12 |
| Capacity | 0.12 |
| Supply | 0.12 |
| Logistics | 0.10 |
| Workforce | 0.10 |
| Technology | 0.12 |

Weights must be finite, nonnegative, include every canonical component and sum to exactly 1.0.

## Component construction

Each monthly component is normalized to 0–1 using min-max normalization across the full available canonical history.

- Quality: defect-rate pressure.
- Equipment: unplanned-downtime pressure.
- Downtime: downtime-cost pressure.
- Capacity: workforce-capacity-gap pressure.
- Supply: shortage-hours pressure.
- Logistics: inverse on-time-delivery pressure.
- Workforce: overtime pressure.
- Technology: technology-downtime pressure.

The resulting score is:

`MORI = Sum(normalized component risk × configured weight) × 100`

## Bands

- Stable: 0 ≤ score < 25
- Watch: 25 ≤ score < 50
- Elevated: 50 ≤ score < 75
- Critical: 75 ≤ score ≤ 100

These thresholds are governance choices for this simulated engagement. They are not externally validated risk cutoffs.

## Missing-data policy

MORI fails closed by month.

If any required component is missing:

- the remaining weights are **not** renormalized;
- no partial composite score is produced;
- `mori_score` is unavailable;
- `mori_band` is unavailable;
- the row is labeled `UNAVAILABLE_MISSING_COMPONENTS`.

This prevents a deceptively complete executive risk score from being created from incomplete evidence.

## Sensitivity analysis

Two design-choice sensitivities are tested.

### Weight sensitivity

Each configured component weight is perturbed one at a time by **±25%**. The full weight vector is then renormalized to sum to 1.0.

Evidence retained:

- scenario weight vector;
- perturbed component;
- score delta from baseline;
- absolute score delta;
- band change vs baseline.

### Threshold sensitivity

All band thresholds are shifted by **−5 points** and **+5 points**.

Evidence retained:

- resulting score band;
- baseline band;
- whether the band changes.

## Interpretation

Sensitivity analysis evaluates robustness to configured design choices. It does not validate MORI against real operational outcomes.

A stable sensitivity result means the current classification is less dependent on small weight/threshold changes. An unstable result means management interpretation should place less emphasis on the exact score/band.

## Limitations

- Full-history min-max normalization makes scores relative to the current dataset and can change as history expands.
- Weights are analytical design choices, not empirically estimated causal weights.
- Correlated components can double-count related operational pressure.
- Bands are project governance thresholds rather than validated external cutoffs.
- Synthetic data cannot establish real-world predictive validity.
- MORI supports prioritization and investigation; it does not establish causation.
