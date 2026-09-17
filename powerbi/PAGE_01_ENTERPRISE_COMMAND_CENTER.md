# Page 1 — Enterprise Command Center

## Purpose

Executive question: **Where is MEDNEXUS losing operational value, how severe is the current risk, and what requires management attention now?**

This page is an executive summary. It should use the latest visible monthly period for headline cards and use historical months only for trend visuals.

**Disclosure to show on the page:**

> Synthetic enterprise data. Scenario outputs are simulated. Predictive outputs are model-derived.

## 1. Required tables for Page 1

Import these CSVs from `powerbi/exports/`:

- `DimDate.csv`
- `EnterpriseMonthly.csv`
- `MORI.csv`
- `DecisionQueue.csv`

The full report will later use the other exported dimensions/facts, but these four tables are sufficient for the first executive page.

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

### MORI

- `month_date` → Date
- `mori_score` → Decimal number
- component fields → Decimal number

## 3. Relationships

Create these active relationships with single-direction filtering from `DimDate` to the fact/mart table:

1. `DimDate[date]` **1 → \*** `EnterpriseMonthly[month_date]`
2. `DimDate[date]` **1 → \*** `MORI[month_date]`

Leave `DecisionQueue` disconnected.

Then select `DimDate` and mark it as the Date table using `DimDate[date]`.

## 4. Measures

Create the measures from `powerbi/DAX_MEASURES.md`.

For this page, the required measures are:

- `Latest Visible Month`
- `Latest Revenue`
- `Latest Operating Cost`
- `Latest Operating Margin Proxy`
- `Latest OEE`
- `Latest OLI`
- `Latest On-Time Delivery`
- `Latest MORI`
- `Latest MORI Band`
- `Revenue`
- `Operating Cost`
- `MORI Score`

## 5. Optional loss-driver calculated table

Create a calculated table:

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

Keep `Loss Driver` disconnected.

## 6. Canvas layout

Use a 16:9 report page.

### Header

Title: **MEDNEXUS | Enterprise Command Center**

Subtitle: **Operational Intelligence & Decision Analytics**

Place the disclosure beneath the subtitle in smaller text.

Add a month/date slicer in the upper-right using `DimDate[year_month]`. It may be left unfiltered; headline cards will then show the latest visible month automatically.

### Row 1 — Executive KPI cards

Use six cards in this order:

1. `Latest Revenue`
2. `Latest Operating Cost`
3. `Latest OEE`
4. `Latest OLI`
5. `Latest On-Time Delivery`
6. `Latest MORI`

Add `Latest MORI Band` as a small text card directly under or next to the MORI card.

Formatting:

- Revenue / cost: currency, display units Millions, 1 decimal place.
- OEE / OLI / delivery: percentage, 1 decimal place.
- MORI: number, 1 decimal place.
- Do not display MORI as a percentage.

### Row 2 — Business-health trend

**Visual:** Line chart

- X-axis: `DimDate[month_start]`
- Values: `Revenue`, `Operating Cost`
- Title: **Revenue vs Operating Cost**

Use a continuous monthly axis. Do not use the headline `Latest ...` measures here.

### Row 2 — Risk trend

**Visual:** Line chart

- X-axis: `DimDate[month_start]`
- Y-axis: `MORI Score`
- Title: **MEDNEXUS Operational Risk Index (MORI)**

Add a subtitle or footnote: **Project-defined composite risk index, 0–100.**

### Row 3 — Current value-loss drivers

**Visual:** Horizontal bar chart

- Y-axis: `'Loss Driver'[Driver]`
- X-axis: `Latest Loss Driver Value`
- Sort descending by value.
- Title: **Current Value-Loss Drivers**

Label the financial values as illustrative where they depend on project-defined synthetic financial assumptions.

### Row 3 — Management decision queue

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

Do not hide `data_limitations`; include it in the tooltip or make it available in a drill-through/detail page later.

## 7. Conditional formatting

### MORI

Use the documented bands, without changing their definitions:

- Stable: 0–24
- Watch: 25–49
- Elevated: 50–74
- Critical: 75–100

### Decision queue

Use conditional formatting on `priority`, but do not convert the textual analytical priority into a new scoring system.

## 8. Canonical validation targets

With no date filter applied, the hardened canonical build should show approximately:

- Latest period: August 2026
- Revenue: **$79,962,619**
- Operating cost: **$31,046,396**
- OEE: **78.7%**
- OLI: **23.3%**
- On-time delivery: **57.9%**
- MORI: **70.1**
- MORI band: **Elevated**

Small display-rounding differences are acceptable. Material differences mean the model, data type, filter context, or measure needs investigation.

## 9. Validation checklist

Before considering Page 1 complete:

- [ ] `DimDate` is marked as the Date table.
- [ ] Both active date relationships are one-to-many and single direction.
- [ ] DecisionQueue remains disconnected.
- [ ] Headline cards use `Latest ...` measures, not raw column sums.
- [ ] Trend visuals use historical measures, not `Latest ...` measures.
- [ ] Revenue and operating-cost cards reconcile to the canonical latest-period values.
- [ ] OEE, OLI, delivery, and MORI reconcile to the management summary.
- [ ] MORI is clearly labeled as project-defined.
- [ ] Synthetic/simulated/model-derived disclosure is visible.
- [ ] The page contains no unsupported causal claim.

## 10. Save convention

Save the working Power BI report locally as:

`MEDNEXUS_Enterprise_Operational_Intelligence.pbix`

The repository currently ignores `*.pbix` by design. For the GitHub portfolio, export a clean screenshot of Page 1 to `powerbi/screenshots/` after validation.