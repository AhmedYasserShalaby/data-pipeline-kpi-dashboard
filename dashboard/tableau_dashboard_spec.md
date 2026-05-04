# Tableau Dashboard Specification

Use the CSV files in `data/processed/dashboard_exports/` as Tableau data sources.

## Page 1: Executive Overview

Purpose: answer whether the retail business is growing and profitable.

Recommended visuals:

- KPI cards: total revenue, total orders, average order value, gross margin, return rate
- Monthly revenue line chart
- Revenue by category bar chart
- Top 10 products table

## Page 2: Sales Trends

Purpose: show monthly performance and growth.

Data source: `monthly_revenue.csv`

Recommended visuals:

- Revenue by month
- Orders by month
- Average order value by month
- Monthly growth percentage

## Page 3: Product Performance

Purpose: identify products and categories driving revenue and margin.

Data source: `product_performance.csv`

Recommended visuals:

- Revenue by product
- Gross margin by category
- Units sold by product
- Product ranking table

## Page 4: Customer Analysis

Purpose: identify high-value and repeat customers.

Data source: `customer_analysis.csv`

Recommended visuals:

- Top customers by revenue
- Revenue by customer segment
- Repeat vs one-time customers
- Revenue by country/city

## Page 5: Returns and Quality

Purpose: show refund exposure and return reasons.

Data source: `returns_quality.csv`

Recommended visuals:

- Refund amount by category
- Return count by reason
- Top return reasons
- Quality issue summary
