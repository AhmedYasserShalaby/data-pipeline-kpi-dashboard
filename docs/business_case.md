# Business Case

## Scenario

A retail company wants a monthly executive dashboard, but the source data comes from multiple operational exports. The data is messy and cannot be trusted directly for decision-making.

## Problems Simulated

- Duplicate customer and order records
- Mixed date formats
- Inconsistent category casing
- Missing city values
- Invalid negative quantities
- Orders linked to missing customers
- Returned orders and refunded amounts

## Business Questions

- How much revenue did the business generate?
- Which months are growing or declining?
- Which products and categories drive performance?
- Which customers generate the most value?
- How much revenue is affected by returns?
- Which return reasons are most common?

## Project Outcome

The pipeline converts raw exports into clean SQL tables and dashboard-ready KPI files. It supports full refreshes and incremental reruns, records pipeline metadata, and keeps rejected-row evidence for analysts. The dashboard gives managers a clear view of revenue, margin, product performance, customer value, returns, and data quality.
