# Pipeline Run Summary

Run ID: `20260512T190340816835Z`
Mode: `full`
Status: `success`
Started UTC: `2026-05-12T19:03:40.816835+00:00`
Finished UTC: `2026-05-12T19:03:40.879166+00:00`
Duration seconds: `0.062`

## Run Totals

| run_id                 | mode | started_at_utc                   | finished_at_utc                  | duration_seconds | status  | rows_read | rows_cleaned | rows_rejected | validation_issues | loaded_rows | exports_directory                |
| ---------------------- | ---- | -------------------------------- | -------------------------------- | ---------------- | ------- | --------- | ------------ | ------------- | ----------------- | ----------- | -------------------------------- |
| 20260512T190340816835Z | full | 2026-05-12T19:03:40.816835+00:00 | 2026-05-12T19:03:40.879166+00:00 | 0.062            | success | 1128      | 1098         | 30            | 55                | 1098        | data/processed/dashboard_exports |

## Table Counts

| table_name | raw_rows | clean_rows | rejected_rows | loaded_rows |
| ---------- | -------- | ---------- | ------------- | ----------- |
| customers  | 121      | 120        | 1             | 120         |
| products   | 30       | 30         | 0             | 30          |
| orders     | 902      | 875        | 27            | 875         |
| returns    | 75       | 73         | 2             | 73          |

## Output

- Dashboard exports: `data/processed/dashboard_exports`
- Quality report: `docs/data_quality_report.md`
- Latest run summary CSV: `data/processed/dashboard_exports/pipeline_run_summary.csv`
