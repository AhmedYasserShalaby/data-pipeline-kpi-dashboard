# Data Contracts

Data contracts live in `config/data_contracts.yaml`.

## What They Validate

- Required columns
- ID format patterns
- Duplicate primary keys
- Parseable date columns
- Date ranges
- Numeric ranges
- Allowed values
- Foreign key links between raw exports

## Current Contracts

| Table | Key checks |
| --- | --- |
| customers | Required customer fields, `C-0001` ID format, duplicate customers, signup date range, valid segment |
| products | Required product fields, `P-001` ID format, duplicate products, positive cost and price |
| orders | Required order fields, `O-00001` ID format, duplicate orders, valid dates, positive quantity and price, valid customer/product links |
| returns | Required return fields, `R-0001` ID format, valid dates, positive refund, valid order link |

## How Issues Are Used

Contract issues are written to `data_quality_issues.csv` with:

- source table
- issue type
- row reference
- affected column
- human-readable issue detail

Cleaning still decides which rows are removed from trusted warehouse tables. This separation makes it clear whether a problem came from contract validation or transformation logic.

## CLI

```bash
retail-kpi validate-contracts
```

Expected synthetic data contains some contract issues by design, so this command reports issues without failing unless a required schema column is missing.
