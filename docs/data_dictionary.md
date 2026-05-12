# Data Dictionary

## customers

| Column | Description |
| --- | --- |
| customer_id | Unique customer identifier |
| customer_name | Customer display name |
| segment | Consumer, Corporate, or Small Business |
| country | Customer country |
| city | Customer city |
| signup_date | Customer signup date |

## products

| Column | Description |
| --- | --- |
| product_id | Unique product identifier |
| product_name | Product display name |
| category | Product category |
| unit_cost | Internal cost per unit |
| unit_price | Default selling price per unit |

## orders

| Column | Description |
| --- | --- |
| order_id | Unique order identifier |
| order_date | Clean order date |
| order_month | Month extracted from order date |
| customer_id | Linked customer |
| product_id | Linked product |
| quantity | Units sold |
| discount | Discount percentage as decimal |
| unit_price | Selling price per unit |
| revenue | Quantity multiplied by unit price after discount |
| cost | Quantity multiplied by product unit cost |
| gross_profit | Revenue minus cost |
| margin | Gross profit divided by revenue |
| status | Completed or Returned |

## returns

| Column | Description |
| --- | --- |
| return_id | Unique return identifier |
| order_id | Linked order |
| return_date | Clean return date |
| reason | Return reason |
| refunded_amount | Amount refunded to customer |

## pipeline_runs

| Column | Description |
| --- | --- |
| run_id | Unique pipeline run identifier |
| mode | Full or incremental load mode |
| started_at_utc | Run start timestamp |
| finished_at_utc | Run finish timestamp |
| duration_seconds | Runtime in seconds |
| status | Run status |
| rows_read | Raw rows read across all sources |
| rows_cleaned | Clean rows produced across all tables |
| rows_rejected | Raw rows rejected during cleaning |
| validation_issues | Contract and cleaning issues written to issue exports |
| loaded_rows | Rows inserted into SQLite for this run |
| exports_directory | Dashboard export directory |

## data_quality_issues export

| Column | Description |
| --- | --- |
| table_name | Source table with the issue |
| issue_source | Contract or cleaning |
| issue_type | Validation or cleaning rule that failed |
| row_reference | Row identifier or source index |
| column_name | Column linked to the issue |
| issue_detail | Human-readable issue detail |
