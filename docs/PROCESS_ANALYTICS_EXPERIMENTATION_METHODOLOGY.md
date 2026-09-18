# Process Analytics and Experimentation Gate Methodology

## Purpose

MEDNEXUS evaluates process-mining and experimentation techniques only when the data contains defensible case linkage and observed intervention evidence.

The governing rule is: **do not fabricate events, treatments, comparison groups, or causal effects.**

## Supported process scope

The current synthetic data supports a linked order-fulfillment process using `order_id` as the case identifier:

**Order Created → Shipped → Delivered → Service Issue (optional)**

These events come directly from:

- `fact_orders`;
- `fact_shipment`;
- `fact_customer_service`.

The supported outputs are:

- event log;
- case-level order-fulfillment cycle times;
- order-to-ship duration;
- ship-to-delivery duration;
- total order-to-delivery duration;
- promised-vs-actual delivery difference;
- transition-duration summary;
- bottleneck ranking based on supported transition durations.

## Full manufacturing process-mining gate

The desired end-to-end manufacturing process is:

**Order → Production → Inspection → Rework → Release → Shipment**

Full process mining is **not admitted** because the current canonical model does not contain:

- customer `order_id` linked to `production_order_id`;
- production-order linkage to inspection/quality events;
- case-linked rework timestamps;
- case-linked release timestamps;
- one end-to-end case identifier across commercial and manufacturing events.

MEDNEXUS therefore does not invent Production, Inspection, Rework, or Release events.

## Process interpretation

The implemented process evidence is **order-fulfillment process analytics**, not a claim of full manufacturing conformance mining.

Transition-duration ranking identifies where elapsed time is concentrated in the supported process. It does not prove causal bottlenecks or process inefficiency mechanisms.

## Experimentation gate

No experiment or causal intervention analysis is currently admitted.

Current scenario outputs provide simulated assumptions and prospective monitoring plans, but MEDNEXUS has no:

- executed treatment assignment;
- observed post-intervention outcomes;
- validated comparison/control group;
- intervention implementation record.

Therefore:

- no treatment effect is calculated;
- no causal lift is reported;
- no A/B or quasi-experimental result is claimed.

## Future design hierarchy

If real intervention evidence becomes available, the preferred hierarchy is:

1. randomized controlled intervention where operationally feasible;
2. matched treatment/control or difference-in-differences when assignment is non-random but defensible;
3. interrupted time series or pre/post analysis only with sufficient history and explicit causal limitations.

The future design must define treatment, comparison logic, pre-period, post-period, primary outcome, assumptions, and intervention timing before effect estimation.
