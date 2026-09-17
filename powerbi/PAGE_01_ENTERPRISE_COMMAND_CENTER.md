# Page 1 — Enterprise Command Center

## Purpose

Executive question:

> **Where is MEDNEXUS losing operational value, how severe is the current risk, what is driving the pressure, and what requires management attention now?**

This page is an executive summary. It must represent the enterprise rather than a single factory function. It therefore covers financial health, workforce/capacity, production, quality, supply, logistics/service, technology health, MORI/OLI, value-loss drivers and priority actions without turning the page into a wall of KPI cards.

**Disclosure to show on the page:**

> Synthetic enterprise data. Scenario outputs are simulated. Predictive outputs are model-derived. Project-defined indices/financial assumptions are labeled where applicable.

## 1. Required tables for Page 1

Import these CSVs from `powerbi/exports/`:

- `DimDate.csv`
- `EnterpriseMonthly.csv`
- `MORI.csv`
- `DecisionQueue.csv`

The full report later uses the detailed dimensions/facts. These four tables are sufficient for the executive shell because `EnterpriseMonthly` contains the cross-domain monthly health indicators needed at Page 1 grain.

## 2. Data types

### DimDate

- `date` → Date
- `month_start` → Date
- `year` → Whole number
- `month_number` → Whole number
- `is_weekend` → Whole number

Sort `month_name` by `month_number`.

### EnterpriseMonthly

- `month_date` → Date
- `revenue`, `operating_cost`, `gross_margin_proxy`, `downtime_cost`, `scrap_cost`, `logistics_cost`, `technology_cost`, `budget_operating_cost` → Decimal / Fixed decimal as appropriate
- `oee`, `oli`, `fpy`, `on_time_delivery`, `capacity_gap_pct`, `absence_rate`, `supplier_reliability` → Decimal number, formatted as percentage where appropriate
- counts/minutes/shortage hours → numeric, with units shown in titles/tooltips

### MORI

- `month_date` → Date
- `mori_score` → Decimal number
- component fields → Decimal number

## 3. Relationships

Create these active relationships with single-direction filtering from `DimDate` to the mart:

1. `DimDate[date]` **1 → \*** `EnterpriseMonthly[month_date]`
2. `DimDate[date]` **1 → \*** `MORI[month_date]`

Leave `DecisionQueue` disconnected.

Then mark `DimDate` as the Date table using `DimDate[date]`.

## 4. Required measures

Create the measures from `powerbi/DAX_MEASURES.md`.

For this page, required measures include:

### Headline health

- `Latest Visible Month`
- `Latest Revenue`
- `Latest Operating Cost`
- `Latest Operating Margin Proxy`
- `Latest Operating Margin % Proxy`
- `Latest OEE`
- `Latest OLI`
- `Latest On-Time Delivery`
- `Latest MORI`
- `Latest MORI Band`

### Enterprise health strip

- `Latest Capacity Gap %`
- `Latest Vacancies`
- `Latest Total Units`
- `Latest Defect Rate`
- `Latest Supplier Reliability`
- `Latest Shortage Hours`
- `Latest Technology Downtime Minutes`
- `Latest Major Technology Incidents`

### Historical trends

- `Revenue`
- `Operating Cost`
- `Operating Margin Proxy`
- `MORI Score`

`Latest FPY Proxy` may be displayed only with the word **Proxy** until the canonical FPY definition is fully validated from pass-without-rework semantics.

## 5. Loss-driver calculated table

Create a disconnected calculated table:

```DAX
Loss Driver =
DATATABLE(
    "Driver", STRING,
    {
        {"Downtime"},
        {"Scrap"},
        {"Logistics"},
        {"Technology"}
    }
)
```

Then create:

```DAX
Latest Loss Driver Value =
VAR _period = [Latest Visible Month]
VAR _driver = SELECTEDVALUE('Loss Driver'[Driver])
RETURN
    SWITCH(
        _driver,
        "Downtime",
            CALCULATE(
                SUM(EnterpriseMonthly[downtime_cost]),
                KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
            ),
        "Scrap",
            CALCULATE(
                SUM(EnterpriseMonthly[scrap_cost]),
                KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
            ),
        "Logistics",
            CALCULATE(
                SUM(EnterpriseMonthly[logistics_cost]),
                KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
            ),
        "Technology",
            CALCULATE(
                SUM(EnterpriseMonthly[technology_cost]),
                KEEPFILTERS(EnterpriseMonthly[month_date] = _period)
            )
    )
```

Keep `Loss Driver` disconnected. These costs include project-defined assumptions where documented; the visual must show an **Illustrative financial assumptions apply** note/tool-tip.

The loss-driver visual will be expanded after COPQ/Six Big Losses work is validated; do not invent missing components in the meantime.

## 6. Canvas layout

Use a 16:9 report page.

### Header

Title: **MEDNEXUS | Enterprise Command Center**

Subtitle: **Operational Intelligence & Decision Analytics**

Place the disclosure beneath the subtitle in smaller text.

Upper-right slicer: `DimDate[year_month]`. It may be unfiltered; latest-period measures then show the latest visible month automatically.

A plant slicer is added only when the executive marts genuinely support plant-level filtering for every affected visual. Do not create a slicer that falsely appears to filter enterprise-only monthly facts.

### Row 1 — Executive KPI cards

Use six primary cards, not a larger wall of cards:

1. `Latest Revenue`
2. `Latest Operating Margin % Proxy`
3. `Latest OEE`
4. `Latest OLI`
5. `Latest On-Time Delivery`
6. `Latest MORI`

Add `Latest MORI Band` as a small text label beside/under the MORI card.

Place `Latest Operating Cost` in the financial trend/tooltip or as a compact secondary value associated with Revenue/Margin; it remains a required executive measure even though it is not a seventh hero card.

Formatting:

- Revenue / cost: currency, display units Millions, 1 decimal place.
- Margin/OEE/OLI/delivery: percentage, 1 decimal place.
- MORI: number, 1 decimal place, never formatted as percentage.

### Row 2 — Enterprise health strip

Use a **matrix / multi-row card / compact KPI strip** rather than eight more large cards.

Represent these business areas explicitly:

| Domain | Indicator | Measure |
|---|---|---|
| Workforce / capacity | Capacity gap | `Latest Capacity Gap %` |
| Workforce | Vacancies | `Latest Vacancies` |
| Production | Total units | `Latest Total Units` |
| Quality | Defect rate | `Latest Defect Rate` |
| Supply | Supplier reliability | `Latest Supplier Reliability` |
| Supply | Shortage hours | `Latest Shortage Hours` |
| Technology | Technology downtime | `Latest Technology Downtime Minutes` |
| Technology | Major incidents | `Latest Major Technology Incidents` |

This strip exists to satisfy executive cross-domain awareness while keeping the hero KPI row focused.

Do not imply green/red thresholds for metrics unless the threshold is explicitly defined in the KPI dictionary or risk methodology. Neutral formatting is safer until threshold governance is complete.

### Row 3 — Business-health trend

**Visual:** Line chart

- X-axis: `DimDate[month_start]`
- Values: `Revenue`, `Operating Cost`
- Optional secondary/tooltip: `Operating Margin Proxy`
- Title: **Revenue vs Operating Cost**

Use a continuous monthly axis. Do not use `Latest ...` measures on trend visuals.

### Row 3 — Risk trend

**Visual:** Line chart

- X-axis: `DimDate[month_start]`
- Y-axis: `MORI Score`
- Title: **MEDNEXUS Operational Risk Index (MORI)**

Footnote:

> Project-defined composite risk index, 0–100. Association/risk prioritization, not causal proof.

Where space permits, show the top MORI component(s) in a tooltip rather than adding more permanent visuals.

### Row 4 — Current value-loss drivers

**Visual:** Horizontal bar chart or waterfall

- Category: `'Loss Driver'[Driver]`
- Value: `Latest Loss Driver Value`
- Sort descending by value.
- Title: **Current Value-Loss Drivers**

The validated future version should incorporate Six Big Losses/COPQ outputs after those analytical layers are complete.

### Row 4 — Priority Decision Queue

**Visual:** Table

Columns, in this order:

1. `DecisionQueue[priority]`
2. `DecisionQueue[domain]`
3. `DecisionQueue[issue]`
4. `DecisionQueue[affected_entity]`
5. `DecisionQueue[evidence]`
6. `DecisionQueue[recommended_action]`
7. `DecisionQueue[owner]`
8. `DecisionQueue[urgency]`
9. `DecisionQueue[confidence]`

Title: **Priority Decision Queue**

`data_limitations` must remain available via tooltip/detail page and must never be deleted from the analytical output merely to simplify the visual.

## 7. Conditional formatting

### MORI

Use only the documented MORI bands:

- Stable: 0–24
- Watch: 25–49
- Elevated: 50–74
- Critical: 75–100

### Decision queue

Conditional formatting may highlight the existing textual `priority`, but must not invent a new numerical priority score.

### Enterprise health strip

Do not apply arbitrary good/bad colors. Only metrics with documented thresholds may receive threshold-based formatting.

## 8. Canonical validation targets for the current baseline

With no date filter applied, the hardened canonical baseline should show approximately:

- Latest period: August 2026
- Revenue: **$79,962,619**
- Operating cost: **$31,046,396**
- OEE: **78.7%**
- OLI: **23.3%**
- On-time delivery: **57.9%**
- MORI: **70.1**
- MORI band: **Elevated**

These are current baseline reconciliation values, not permanent business targets. Analytical logic may intentionally change as unresolved canonical requirements are implemented; any change must be regenerated, validated and documented.

## 9. Validation checklist

Before considering the executive page technically valid:

- [ ] `DimDate` is marked as the Date table.
- [ ] Both active date relationships are one-to-many and single direction.
- [ ] `DecisionQueue` remains disconnected.
- [ ] headline cards use `Latest ...` measures, not raw column sums.
- [ ] trend visuals use historical measures, not `Latest ...` measures.
- [ ] finance includes revenue, cost and margin context.
- [ ] workforce/capacity is visibly represented.
- [ ] production and quality are visibly represented.
- [ ] supply risk is visibly represented.
- [ ] logistics/service is represented by on-time delivery.
- [ ] technology health is visibly represented.
- [ ] OEE, OLI and MORI are clearly differentiated.
- [ ] MORI is labeled project-defined.
- [ ] loss-driver financial assumptions are labeled illustrative where applicable.
- [ ] synthetic/simulated/model-derived disclosure is visible.
- [ ] no unsupported causal claim appears.
- [ ] no arbitrary thresholds are introduced for executive-health metrics.
- [ ] current headline values reconcile to the latest generated management summary after every analytical regeneration.

## 10. Finalization dependency

This Page 1 design is preserved as the executive shell, but it is **provisional** until the canonical predecessor work is closed/gated, especially:

- Six Big Losses and COPQ/value-leakage decomposition;
- expanded statistical/root-cause analysis;
- expanded Data Trust/observability;
- strengthened predictive/forecast/risk evidence;
- scenario/optimization suitability decisions.

When those layers are validated, refresh the executive measures/driver visuals instead of rebuilding the page concept from scratch.

## 11. Save convention

Save the working Power BI report locally as:

`MEDNEXUS_Enterprise_Operational_Intelligence.pbix`

The repository ignores `*.pbix` by design. For the GitHub portfolio, export validated page screenshots to `powerbi/screenshots/` after final reconciliation.
