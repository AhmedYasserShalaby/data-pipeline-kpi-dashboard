# Data Quality Report

This report summarizes the validation checks applied during the retail KPI pipeline run.

## Row Summary

| table_name   |   raw_rows |   clean_rows |   removed_or_flagged_rows |   validation_issues |   clean_rate |
|:-------------|-----------:|-------------:|--------------------------:|--------------------:|-------------:|
| customers    |        121 |          120 |                         1 |                   0 |       0.9917 |
| products     |         30 |           30 |                         0 |                   0 |       1      |
| orders       |        902 |          875 |                        27 |                  25 |       0.9701 |
| returns      |         75 |           73 |                         2 |                   2 |       0.9733 |

## Issue Breakdown

| table_name   | issue_type                         |   issue_count |
|:-------------|:-----------------------------------|--------------:|
| orders       | invalid_order_or_missing_dimension |            25 |
| returns      | invalid_return_or_missing_order    |             2 |

## Interpretation

- Rows can be removed when they fail business rules such as invalid quantities, missing dimension links, or invalid dates.
- The pipeline keeps issue details in `data_quality_issues.csv` so analysts can review rejected records.
- A clean rate below 100% is intentional in this project because the raw exports simulate real operational data quality problems.
