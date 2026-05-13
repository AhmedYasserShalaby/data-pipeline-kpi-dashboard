# Analytics Models

This project includes a lightweight dbt-style SQL layer under `models/`.

It is intentionally dependency-light: the SQL files are plain `SELECT` models, and `retail-kpi run-models` materializes them as SQLite views after the pipeline loads clean warehouse tables.

## Model Layers

| Layer | Files | Purpose |
|---|---|---|
| Staging | `models/staging/stg_*.sql` | Rename/cast cleaned source tables into analytics-friendly views. |
| Intermediate | `models/intermediate/int_order_lines.sql` | Join orders, customers, and products at order-line grain. |
| Marts | `models/marts/mart_*.sql` | Produce business-facing monthly, product, and segment metrics. |

## Run

```bash
retail-kpi generate-data
retail-kpi run-pipeline --mode full
retail-kpi run-models
```

## Why This Helps

- Shows analytics engineering structure, not only one-off KPI queries.
- Makes grain and business logic easier to explain in interviews.
- Mirrors dbt habits: staging, intermediate models, marts, schema docs, tests.
- Keeps the public portfolio easy to run without requiring a cloud warehouse.

## Production Next Step

Move these models into real dbt with a warehouse adapter such as Postgres, DuckDB, BigQuery, Snowflake, or Redshift.
