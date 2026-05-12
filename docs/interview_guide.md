# Interview Guide

## 30-Second Pitch

I built a retail data pipeline that takes messy CSV exports, validates them with YAML data contracts, cleans the data with Python and pandas, loads trusted tables into SQLite, exports SQL KPI datasets, and visualizes the results in Streamlit. It supports full and incremental loading, tracks pipeline runs, reports rejected rows, and has CI checks for linting, tests, smoke runs, and export integrity.

## What To Emphasize

- The project is more than a dashboard: it has ingestion, validation, cleaning, loading, KPI exports, observability, and tests.
- YAML contracts make data quality rules visible and maintainable.
- Incremental mode is idempotent, so rerunning the pipeline does not double-count orders.
- The dashboard bootstraps demo data if outputs are missing, which makes public deployment safer.
- SQLite was chosen for portability, not because the design is limited to SQLite.

## Likely Questions

### Why not use PostgreSQL?

SQLite keeps the public demo simple and portable. The warehouse model and SQL transformations can move to PostgreSQL later without changing the project concept.

### What happens to bad rows?

Bad rows are either flagged by contracts or removed during cleaning. Issue details are exported to `data_quality_issues.csv`, and trusted tables only receive cleaned rows.

### What is incremental loading here?

Incremental mode checks existing primary keys in SQLite and inserts only new rows. This prevents duplicate loads when the same raw files are processed again.

### How do you know KPIs are correct?

Tests compare exported KPI CSV totals against SQLite totals, and the health checks fail if required exports are missing, quality drops below the threshold, or totals disagree.

### What would you improve next?

I would deploy the Streamlit demo, then consider PostgreSQL, orchestration, and slowly changing dimensions if the project needed to behave more like a production system.

## CV Bullet To Defend

Built a Python and SQL retail ETL pipeline with YAML data contracts, incremental SQLite loading, rejected-row reporting, KPI exports, CI checks, and a Streamlit executive dashboard.
