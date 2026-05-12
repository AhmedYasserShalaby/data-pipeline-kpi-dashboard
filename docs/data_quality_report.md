# Data Quality Report

This report summarizes the validation checks applied during the retail KPI pipeline run.

Overall quality score: **97.7%**

## Row Summary

| table_name | raw_rows | clean_rows | rejected_rows | removed_or_flagged_rows | validation_issues | clean_rate | issue_rate | quality_score |
| ---------- | -------- | ---------- | ------------- | ----------------------- | ----------------- | ---------- | ---------- | ------------- |
| customers  | 121      | 120        | 1             | 1                       | 1                 | 0.9917     | 0.0083     | 0.9917        |
| products   | 30       | 30         | 0             | 0                       | 0                 | 1.0        | 0.0        | 1.0           |
| orders     | 902      | 875        | 27            | 27                      | 52                | 0.9701     | 0.0576     | 0.9424        |
| returns    | 75       | 73         | 2             | 2                       | 2                 | 0.9733     | 0.0267     | 0.9733        |

## Issue Breakdown

| table_name | issue_source | issue_type                         | column_name | issue_count |
| ---------- | ------------ | ---------------------------------- | ----------- | ----------- |
| customers  | contract     | duplicate_key                      | customer_id | 1           |
| orders     | cleaning     | invalid_order_or_missing_dimension |             | 25          |
| orders     | contract     | duplicate_key                      | order_id    | 2           |
| orders     | contract     | missing_foreign_key                | customer_id | 13          |
| orders     | contract     | numeric_below_min                  | quantity    | 12          |
| returns    | cleaning     | invalid_return_or_missing_order    |             | 2           |

## Interpretation

- Contract issues come from YAML rules for schema, IDs, ranges, dates, allowed values, duplicate keys, and foreign keys.
- Cleaning issues are rejected rows removed before loading trusted warehouse tables.
- The pipeline keeps rejected-row details in `data_quality_issues.csv` so analysts can review data quality failures.
- A clean rate below 100% is intentional because the raw exports simulate real operational data quality problems.
