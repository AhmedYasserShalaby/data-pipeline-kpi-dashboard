# KPI Definitions

## Executive KPIs

| KPI | Definition | Source |
| --- | --- | --- |
| Total revenue | Sum of order revenue after discounts | `orders.revenue` |
| Total orders | Distinct cleaned orders | `orders.order_id` |
| Total customers | Distinct customers with orders | `orders.customer_id` |
| Average order value | Total revenue divided by total orders | `orders` |
| Gross profit | Revenue minus product cost | `orders.gross_profit` |
| Gross margin | Gross profit divided by revenue | `orders` |
| Refunded amount | Sum of return refunds | `returns.refunded_amount` |
| Return rate | Return count divided by order count | `returns`, `orders` |

## Analytical KPIs

| KPI | Definition | Use |
| --- | --- | --- |
| Monthly growth | Month-over-month revenue change | Spot trend changes |
| Category revenue | Revenue grouped by product category | Find strongest categories |
| Product gross margin | Gross profit divided by revenue by product | Compare product profitability |
| Customer revenue | Revenue grouped by customer | Find high-value customers |
| Repeat customer flag | Customer has more than one order | Identify returning customers |
| Quality score | One minus issue rate | Monitor trusted data health |

## Data Quality KPIs

| KPI | Definition |
| --- | --- |
| Raw rows | Rows read from raw exports |
| Clean rows | Rows kept after cleaning |
| Rejected rows | Raw rows removed before warehouse load |
| Validation issues | Contract and cleaning issues found |
| Loaded rows | Rows inserted into SQLite for the run |
