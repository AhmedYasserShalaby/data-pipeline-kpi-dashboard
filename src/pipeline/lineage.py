from __future__ import annotations

from pathlib import Path

from pipeline.config import ensure_parent
from pipeline.paths import PROJECT_ROOT


LINEAGE_DOC = """# Data Lineage

This document shows how data moves from raw source exports to trusted marts and dashboards.

## Flow

```mermaid
flowchart LR
    raw_customers[raw customers.csv] --> contracts[YAML data contracts]
    raw_products[raw products.csv] --> contracts
    raw_orders[raw orders.csv] --> contracts
    raw_returns[raw returns.csv] --> contracts
    contracts --> cleaning[Python cleaning and validation]
    cleaning --> rejected[rejected rows and issue report]
    cleaning --> warehouse[SQLite trusted warehouse]
    warehouse --> staging[staging SQL views]
    staging --> intermediate[intermediate order-line view]
    intermediate --> marts[monthly/product/customer marts]
    warehouse --> kpis[dashboard KPI exports]
    marts --> dashboard[Streamlit dashboard]
    kpis --> dashboard
```

## Grain

| Asset | Grain | Purpose |
|---|---|---|
| `customers` | One row per customer | Customer dimension. |
| `products` | One row per product | Product dimension and unit economics. |
| `orders` | One row per order | Sales fact table. |
| `returns` | One row per return | Return/refund fact table. |
| `int_order_lines` | One row per valid order joined to customer/product | Business-ready order analysis. |
| `mart_monthly_revenue` | One row per order month | Revenue trend reporting. |
| `mart_product_performance` | One row per product | Product ranking and margin analysis. |
| `mart_customer_segments` | One row per segment/country | Segment performance analysis. |

## Controls

- Data contracts check schema, keys, ranges, dates, allowed values, duplicates, and relationships.
- Cleaning quarantines invalid records before loading trusted tables.
- Health checks compare dashboard exports against warehouse totals.
- Diagnosis reports explain root cause, severity, and remediation actions for quality issues.
"""


def write_lineage(output_path: Path = PROJECT_ROOT / "docs" / "lineage.md") -> Path:
    ensure_parent(output_path)
    output_path.write_text(LINEAGE_DOC, encoding="utf-8")
    return output_path
