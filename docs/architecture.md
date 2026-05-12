# Architecture

This project models a small retail analytics warehouse and reporting pipeline.

## Flow

```mermaid
flowchart LR
    A[Raw CSV exports] --> B[Python CLI]
    B --> C[YAML data contracts]
    C --> D[Cleaning rules]
    D --> E[SQLite warehouse]
    E --> F[SQL KPI exports]
    E --> G[Pipeline run metadata]
    F --> H[Streamlit dashboard]
    D --> I[Data quality reports]
```

## Warehouse Model

```mermaid
erDiagram
    customers ||--o{ orders : places
    products ||--o{ orders : contains
    orders ||--o| returns : may_have

    customers {
        text customer_id PK
        text customer_name
        text segment
        text country
        text city
        text signup_date
    }

    products {
        text product_id PK
        text product_name
        text category
        real unit_cost
        real unit_price
    }

    orders {
        text order_id PK
        text order_date
        text order_month
        text customer_id FK
        text product_id FK
        integer quantity
        real revenue
        real gross_profit
        text status
    }

    returns {
        text return_id PK
        text order_id FK
        text return_date
        text reason
        real refunded_amount
    }

    pipeline_runs {
        text run_id PK
        text mode
        text started_at_utc
        integer rows_read
        integer rows_cleaned
        integer rows_rejected
        integer loaded_rows
    }
```

## Design Choices

- `customers` and `products` act as dimensions.
- `orders` and `returns` act as fact-style operational tables.
- `pipeline_runs` stores operational metadata for observability.
- SQLite keeps the project easy to run locally and on a public demo.
- Full refresh mode rebuilds warehouse tables.
- Incremental mode inserts only unseen primary keys and keeps reruns idempotent.
- KPI exports are CSV files so Streamlit, Tableau, and Power BI can reuse the same outputs.
