# Recruiter Walkthrough

Use this when a recruiter, interviewer, or referral contact opens the repo.

## 20-Second Summary

This project turns messy retail CSV exports into trusted KPI tables and a Streamlit dashboard. The strongest parts are the pipeline, data contracts, incremental loading, rejected-row reporting, health checks, tests, Docker, and CI.

## 90-Second Demo Flow

1. Open the README and show the architecture diagram.
2. Show the dashboard GIF to make the result visible.
3. Explain that raw customer, product, order, and returns files are intentionally messy.
4. Open `config/data_contracts.yaml` and show required columns, ID patterns, ranges, duplicate checks, and foreign keys.
5. Open `sql/kpi_queries.sql` and show KPI logic for executive, monthly, product, customer, and returns analysis.
6. Show `tests/` and GitHub Actions badges to prove it is not just a screenshot project.
7. End with the production upgrade path: orchestration, dbt-style models, PostgreSQL, and monitoring.

## Strongest Interview Points

- Data contracts make quality rules explicit before loading.
- Rejected rows are preserved for debugging instead of silently disappearing.
- Incremental mode avoids duplicate loads by checking primary keys.
- KPI exports are checked against warehouse totals.
- Docker and CI make the project reproducible.
- SQLite was chosen for portability; the design can move to PostgreSQL.

## Questions To Be Ready For

| Question | Short answer |
|---|---|
| Why SQLite? | Portable demo warehouse; easy for recruiters to run. PostgreSQL would be the next production step. |
| What breaks in production? | Schema drift, late data, duplicate keys, bad joins, missing dimensions, failed schedules. |
| How do you validate correctness? | Contracts, rejected-row files, KPI/database reconciliation, tests, and health checks. |
| Why a dashboard? | It makes the pipeline output visible, but the pipeline is the core work. |
| What would you add next? | Airflow/Dagster orchestration, dbt-style SQL models, Postgres, freshness checks, alerts. |

## One-Minute Spoken Pitch

I built this as a practical data engineering project, not only a dashboard. It simulates a retail business with messy customer, product, order, and return exports. The pipeline validates raw data with YAML contracts, cleans it in Python, stores trusted tables in SQLite, exports SQL KPI datasets, and shows the results in Streamlit.

The project supports full and incremental loading, writes rejected-row reports, tracks run metadata, and has health checks to make sure KPI exports match the warehouse. I added tests, Ruff, Docker, GitHub Actions, and documentation so it behaves like a small production-style ETL project.
