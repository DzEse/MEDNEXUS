# MEDNEXUS Enterprise Dataset & Digital Twin Enhancement

## Authority and preservation

This document is a binding additive extension to the MEDNEXUS Master Build Specification.

It does **not** replace, weaken, narrow, or silently supersede any previously validated requirement, analytical gate, disclosure, method, artifact, relationship contract, or evidence trail.

Where this enhancement requires a richer dataset than the current implementation, the existing implementation remains the validated baseline until the richer design is prototyped, tested, reconciled, and explicitly promoted.

The governing objective is:

> **Maximum analytical richness per unit of data.**

The target is a **compact synthetic enterprise digital twin** whose additional data earns its place through business value, analytical validity, traceability, decision usefulness, or validation value.

---

# 1. CORE PRINCIPLE

Design MEDNEXUS as a **compact synthetic enterprise digital twin**.

The objective is:

> **Maximum analytical richness per unit of data.**

Do not generate millions of repetitive synthetic records merely to make the project appear large.

Every additional table, field, entity, event, and relationship must support at least one:

- business question
- KPI
- analytical method
- predictive model
- forecast
- risk calculation
- scenario
- decision
- Power BI interaction
- validation requirement

If a field does not contribute meaningfully, do not create it.

---

# 2. TEMPORAL DEPTH

Where appropriate, create approximately **24–36 months of enterprise history**.

The exact period must be determined from analytical requirements and dataset suitability.

The historical data should support:

- trend analysis
- seasonality
- year-over-year comparison
- month-over-month analysis
- workforce changes
- production trends
- quality trends
- equipment deterioration
- supplier variability
- inventory behavior
- logistics performance
- demand forecasting
- maintenance forecasting
- anomaly detection
- scenario analysis

Do not artificially force seasonality into every domain.

Use realistic domain-specific temporal patterns.

Clearly distinguish:

- **Observed/Public Dataset History**
- **Synthetic Enterprise History**
- **Derived Metrics**
- **Model-Derived Outputs**
- **Forecasts**
- **Simulated Scenarios**

---

# 3. ENTERPRISE ENTITY SCALE

Use enough entities to create meaningful segmentation without excessive computational burden.

Initial planning ranges may include:

### Manufacturing

- 3–5 plants
- 8–15 production lines
- 50–150 machines
- 10–30 products/product families
- multiple shifts

### Workforce

- several hundred employees
- multiple departments
- multiple job roles
- multiple skills
- supervisors/managers
- plant and corporate functions

### Recruitment

- multiple open positions
- candidates
- applications
- screening events
- interviews
- offers
- acceptances/rejections
- time-to-fill
- hiring costs

### Supply Chain

- 20–50 suppliers
- multiple materials
- material lots
- purchase orders
- lead-time history

### Inventory

- multiple warehouses
- raw materials
- work-in-progress
- finished goods
- safety stock
- stock movements

### Logistics

- multiple carriers
- routes
- warehouses
- shipment events
- delivery exceptions

### Healthcare Customers

- approximately 50–150 simulated healthcare customers where appropriate
- hospitals
- clinics
- healthcare organizations
- distributors

### Technology

- multiple enterprise systems
- applications
- services
- incidents
- support tickets
- deployments
- usage records

These are planning ranges, NOT fabricated final dataset statistics.

Adjust them after determining the required analytical grain.

---

# 4. FINANCE DATA

Expand Finance to support enterprise value analysis.

Include where appropriate:

- revenue
- operating costs
- labor costs
- production costs
- quality costs
- maintenance costs
- inventory costs
- logistics costs
- technology costs
- budgets
- actuals
- cost centers
- departments
- plants
- product families
- business units
- financial periods

Support:

- budget vs actual
- cost trends
- cost-per-unit
- quality cost
- downtime cost
- labor cost
- logistics cost
- simulated value leakage
- profitability analysis

Clearly distinguish observed/derived financial values from simulated financial assumptions.

---

# 5. WORKFORCE / HR DATA

Create interconnected workforce information.

Potential entities:

**Employee**
→ Department
→ Job Role
→ Plant
→ Shift
→ Manager
→ Skill
→ Training
→ Employment Event

Include:

- employee ID
- department
- role
- plant
- shift
- skills
- start date
- employment status
- overtime
- absenteeism
- training
- utilization/capacity
- labor cost
- turnover events

Do not create unnecessary sensitive personal information.

Do not include real employee identities.

Use synthetic identifiers.

---

# 6. RECRUITMENT DATA

Create a recruitment pipeline connected to workforce capacity.

Potential process:

**Vacancy**
→ Application
→ Screening
→ Interview
→ Assessment
→ Offer
→ Acceptance
→ Onboarding

Include:

- position
- department
- required skills
- location
- opening date
- candidate event history
- stage
- time in stage
- offer status
- time-to-fill
- hiring cost
- criticality

The data must allow analysis of:

- recruitment bottlenecks
- skill shortages
- time-to-fill
- vacancy pressure
- hiring demand
- workforce capacity risk

Connect critical vacancies conceptually or analytically to workforce capacity only where the data supports it.

---

# 7. MANUFACTURING DATA

Create a realistic production-event layer.

Potential grain:

**Production Event / Production Order / Shift-Line-Product-Day**

Do NOT mix grains.

Include:

- production order
- plant
- production line
- machine
- product
- product family
- shift
- planned quantity
- actual quantity
- cycle time
- ideal cycle time
- run time
- planned downtime
- unplanned downtime
- good units
- defective units
- scrap
- rework
- production status
- production date

Support:

- throughput
- production attainment
- utilization
- OEE
- capacity
- schedule adherence
- cycle time
- production loss

---

# 8. QUALITY DATA

Create quality events independently from production where appropriate.

Potential grain:

**Inspection Event / Quality Event**

Include:

- inspection ID
- production order
- product
- plant
- line
- machine
- shift
- process stage
- characteristic
- defect
- defect category
- severity
- inspection result
- rework
- scrap
- disposition

Support:

- FPY
- RTY where process-stage data permits
- defect rate
- DPMO where opportunities are defined
- scrap rate
- rework rate
- Pareto analysis
- quality trends
- process capability
- SPC
- root-cause analysis

Do not invent specification limits.

If specifications are illustrative, label them explicitly.

---

# 9. PROCESS CAPABILITY / SPC DATA

Where appropriate, include quality characteristics that support statistical analysis.

Potential fields:

- characteristic
- measurement
- specification lower limit
- specification upper limit
- target
- timestamp
- machine
- line
- product
- process stage

Support:

- mean
- median
- variance
- standard deviation
- control limits
- Cp
- Cpk
- Pp
- Ppk
- process sigma
- control charts
- drift
- out-of-control events

Do not calculate capability metrics unless specification and sampling assumptions are valid.

Distinguish:

**Process Capability**
from
**Process Stability / Statistical Control**.

---

# 10. EQUIPMENT / MAINTENANCE DATA

Create machine and maintenance relationships.

Potential hierarchy:

**Plant**
→ Line
→ Machine
→ Component
→ Failure Mode
→ Maintenance Event

Include:

- machine ID
- machine type
- age where appropriate
- operating hours
- failure events
- failure mode
- downtime
- maintenance type
- maintenance date
- repair duration
- maintenance cost
- technician/resource where appropriate
- maintenance status

Support:

- MTBF
- MTTR
- downtime analysis
- failure-mode Pareto
- maintenance backlog
- preventive maintenance
- corrective maintenance
- reliability trends

---

# 11. SENSOR / PREDICTIVE MAINTENANCE DATA

Where a public predictive-maintenance dataset is used, preserve its original methodology and provenance.

Do not falsely claim that public NASA/UCI data represents MEDNEXUS's real medical-device machines.

Instead:

**Public Dataset**
→ methodology/model development
→ controlled MEDNEXUS analytical demonstration

Where synthetic sensor data is generated, document:

- generation methodology
- assumptions
- distributions
- correlations
- simulated failure mechanism
- limitations

Prevent:

- target leakage
- temporal leakage
- future information leakage
- duplicate observations

Use appropriate temporal validation.

---

# 12. SUPPLY CHAIN DATA

Create:

**Supplier**
→ Purchase Order
→ Material
→ Material Lot
→ Receipt
→ Inventory

Include:

- supplier
- material
- purchase order
- order date
- promised date
- actual receipt date
- quantity
- lead time
- quality result
- shortage
- late delivery
- supplier performance

Support:

- supplier reliability
- lead-time variability
- shortage risk
- material availability
- supplier quality
- supply risk

---

# 13. INVENTORY DATA

Include:

- warehouse
- material
- product
- stock level
- safety stock
- reorder point
- inventory movement
- receipt
- consumption
- adjustment
- stockout
- excess inventory

Support:

- inventory turnover
- stockouts
- excess inventory
- safety-stock analysis
- inventory risk
- working-capital analysis

Avoid creating physically impossible inventory movements.

Validate opening balance + receipts − consumption ± adjustments = closing balance where appropriate.

---

# 14. LOGISTICS DATA

Create:

**Customer Order**
→ Shipment
→ Carrier
→ Route
→ Delivery Event

Include:

- order
- shipment
- warehouse
- customer
- carrier
- origin
- destination
- promised date
- ship date
- delivery date
- delay
- exception
- delivery status

Support:

- OTIF
- on-time delivery
- lead time
- carrier performance
- logistics exceptions
- customer-service risk

---

# 15. HEALTHCARE CUSTOMER DATA

Create a simulated customer environment without patient-identifiable information.

Potential entities:

- healthcare customer
- customer type
- region
- product demand
- order
- shipment
- service request
- service issue

Analyze:

- demand
- fulfillment
- service reliability
- delivery performance
- order volume
- exceptions
- customer-service trends

Do not introduce unnecessary patient data.

---

# 16. TECHNOLOGY / SAAS DATA

Create technology operations data that supports the enterprise.

Potential entities:

**System**
→ Application
→ Incident
→ Deployment
→ Support Ticket
→ Usage

Include:

- uptime
- downtime
- incident
- severity
- response time
- resolution time
- MTTR
- deployment
- failed deployment
- support ticket
- system usage
- data-quality incident

Technology must remain connected to MEDNEXUS operations.

Example:

Technology incident
→ data interruption
→ reporting uncertainty
→ delayed operational visibility

Do not treat SaaS as an unrelated business project.

---

# 17. GEOSPATIAL DATA

Add geographic information for entities that benefit from mapping.

Potential fields:

### DimPlant

- PlantID
- PlantName
- Country
- Region
- City
- Latitude
- Longitude
- PlantType
- Capacity

### DimSupplier

- SupplierID
- SupplierName
- Country
- Region
- City
- Latitude
- Longitude
- SupplierRisk

### DimWarehouse

- WarehouseID
- Location
- Latitude
- Longitude
- Capacity

### DimCustomer

- CustomerID
- CustomerType
- Country
- Region
- City
- Latitude
- Longitude

Use synthetic locations where MEDNEXUS is fictional.

Clearly label them as simulated.

The map must support actual analysis rather than decoration.

---

# 18. CROSS-DOMAIN RELATIONSHIPS

This is one of the most important requirements.

Design the data so the enterprise can be traced across domains.

Example:

**Employee**
→ Department
→ Plant
→ Shift
→ Production Line

**Machine**
→ Production Line
→ Product
→ Production
→ Downtime
→ Maintenance
→ Quality

**Supplier**
→ Material
→ Purchase Order
→ Inventory
→ Production

**Production**
→ Quality
→ Shipment
→ Customer

**Shipment**
→ Healthcare Customer
→ Logistics
→ Service Performance

**All operational activity**
→ Cost
→ Finance

This is what creates the MEDNEXUS enterprise story.

---

# 19. EVENT-BASED PROCESS LOG

Where practical, create an event-log representation supporting process mining.

Potential lifecycle:

**Order Created**
→ **Production Scheduled**
→ **Production Started**
→ **Inspection**
→ **Rework**
→ **Release**
→ **Shipment**
→ **Delivery**

Use timestamps.

Support analysis of:

- waiting time
- bottlenecks
- cycle time
- process variants
- rework loops
- delays
- throughput

Do not create process mining data unless event ordering is logically valid.

---

# 20. DATA GRAIN REQUIREMENT

Before creating any table, explicitly document:

- table name
- business purpose
- grain
- primary key
- foreign keys
- dimensions
- measures
- cardinality
- source
- refresh frequency
- transformation logic

Examples:

`FactProduction`

> One production record for a defined production order/line/product/shift/time grain.

`FactQuality`

> One inspection event for a defined production/quality event.

`FactDowntime`

> One downtime event.

`FactShipment`

> One shipment/order fulfillment event.

Never combine different grains merely to reduce the number of tables.

---

# 21. SYNTHETIC DATA GENERATION

Synthetic data must be generated from explicit business rules.

Do not generate independent random numbers for every field.

Create realistic dependencies.

Examples:

- higher machine age may increase simulated failure probability
- increased downtime may reduce production output
- quality variation may affect rework
- supplier delays may increase material shortages
- workforce shortages may reduce available capacity
- higher demand may increase production pressure
- maintenance events may reduce subsequent failure probability in the simulation

These relationships must be labelled as **synthetic generation assumptions**, not discovered empirical causality.

Document the generation rules.

Use fixed random seeds where reproducibility is required.

---

# 22. DATA VOLUME STRATEGY

The target is a **manageable enterprise dataset**, not a big-data demonstration.

A planning target may be approximately:

**hundreds of thousands to low millions of records across all fact tables**, depending on the chosen grain.

Do not treat this as a mandatory number.

Determine actual volume based on:

- analytical requirements
- Power BI performance
- local hardware
- GitHub practicality
- model complexity
- reproducibility

Use:

- Parquet where appropriate
- compressed formats
- samples
- generated synthetic data
- reproducible generation scripts

Avoid duplicate copies of the same dataset.

---

# 23. RAW / STAGING / CURATED ARCHITECTURE

Use:

    RAW
     ↓
    STAGING
     ↓
    QUALITY VALIDATION
     ↓
    CURATED
     ↓
    ANALYTICAL DATA MODEL
     ↓
    SQL / PYTHON
     ↓
    POWER BI
     ↓
    DECISION INTELLIGENCE

Raw public datasets should remain identifiable and traceable.

Do not overwrite source data.

---

# 24. DATA PROVENANCE

For every source document:

- Source
- Dataset name
- Publisher
- URL/reference
- License/usage considerations
- Download date
- Version if available
- Original grain
- Fields used
- Transformation
- Intended analytical use
- Limitations

For synthetic data:

- Synthetic
- Generator version
- Generation date
- Seed
- Generation assumptions
- Tables generated
- Relationships
- Limitations

Never invent licensing information.

---

# 25. DATA QUALITY

Implement automated checks for:

- nulls
- duplicates
- invalid ranges
- impossible values
- date anomalies
- duplicate keys
- orphan records
- broken foreign keys
- inconsistent categories
- schema changes
- row-count anomalies
- missingness spikes
- stale data
- category drift
- timestamp problems
- class imbalance
- feature sparsity

Generate evidence for the checks.

---

# 26. ENTERPRISE DATA TRUST SCORE

Use the MEDNEXUS Data Trust Score.

Potential dimensions:

- completeness
- validity
- consistency
- uniqueness
- timeliness
- referential integrity
- freshness
- schema integrity

Create a transparent formula.

Document:

- normalization
- weighting
- thresholds
- missing-data handling
- interpretation
- limitations

Do not present Data Trust Score as an industry-standard metric.

---

# 27. COMMAND CENTER DATA REQUIREMENTS

Ensure the expanded dataset can support the Executive Command Center.

It must be possible to navigate:

**Enterprise**
→ Region
→ Plant
→ Line
→ Machine
→ Product
→ Shift
→ Event

And across:

**Supplier**
→ Material
→ Inventory
→ Production
→ Shipment
→ Customer

And:

**Workforce**
→ Department
→ Role
→ Capacity
→ Recruitment
→ Operations

The Command Center must be able to trace high-level signals to underlying data.

---

# 28. ANALYTICAL RICHNESS OVER ROW COUNT

Before increasing dataset volume, ask:

> What new decision can this additional data support?

Good reasons to increase data:

- enables forecasting
- enables segmentation
- enables drill-through
- enables statistical testing
- enables model training
- enables process mining
- enables map analysis
- enables scenario analysis
- enables cross-domain root-cause analysis
- enables reconciliation

Bad reasons:

- “more rows looks impressive”
- “large dataset sounds more advanced”
- “millions of rows proves data engineering”
- “more columns automatically makes the project better”

---

# 29. VALIDATION BEFORE EXPANSION

Before generating the full dataset:

1. Define requirements.
2. Define business questions.
3. Define table grains.
4. Define relationships.
5. Define KPI dependencies.
6. Define analytical methods.
7. Define required fields.
8. Create a small prototype dataset.
9. Validate relationships.
10. Validate calculations.
11. Validate Power BI behavior.
12. Expand only after the model is proven.

This prevents generating large amounts of unusable data.

---

# 30. RECONCILIATION

Where practical, reconcile:

**Synthetic Source**
↔ **SQL**
↔ **Python**
↔ **Power BI**

Important metrics include:

- production quantity
- throughput
- downtime
- OEE
- FPY
- defect rate
- scrap
- rework
- inventory
- OTIF
- MORI
- OLI
- Data Trust Score
- forecast metrics
- scenario outputs

Define acceptable tolerances.

Investigate discrepancies rather than hiding them.

---

# 31. DATA PRODUCT DESIGN

Treat MEDNEXUS as a data product.

Document:

- purpose
- users
- business questions
- domains
- data sources
- refresh strategy
- data quality
- KPI catalog
- contracts
- lineage
- ownership concepts
- version
- limitations
- change management

The dataset is not merely raw material for charts.

It is the foundation of the MEDNEXUS enterprise decision system.

---

# 32. FINAL DATASET QUALITY STANDARD

The final dataset must allow MEDNEXUS to demonstrate:

**Finance**
→ **People**
→ **Recruitment**
→ **Workforce**
→ **Manufacturing**
→ **Quality**
→ **Maintenance**
→ **Supply Chain**
→ **Inventory**
→ **Logistics**
→ **Healthcare Customers**
→ **Technology**
→ **Risk**
→ **Forecast**
→ **Scenario**
→ **Decision**

The dataset should feel like a **coherent enterprise**, not a collection of unrelated datasets.

The final standard is:

> **Do not optimize for dataset size. Optimize for enterprise realism, analytical depth, traceability, decision usefulness, and computational efficiency.**

Every synthetic number must have a documented reason for existing.

Every analytical result must be traceable to data.

Every cross-domain relationship must be logically defensible.

Every model-derived result must be validated.

Every simulated scenario must be labelled.

Every unsupported assumption must remain explicitly identified as an assumption.

The objective is a **rich but manageable MEDNEXUS enterprise digital twin** capable of powering the Executive Command Center and demonstrating the complete:

**RAW DATA → DATA QUALITY → SQL → CURATED DATA → STATISTICS → ML / FORECAST → RISK → SCENARIO → POWER BI → DECISION → MONITORING**

lifecycle.
