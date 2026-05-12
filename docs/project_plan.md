# Project Plan

## Version 1

- Create small realistic sample datasets.
- Clean customer, product, and order data with pandas.
- Load data into SQLite.
- Write SQL KPI queries.
- Build dashboard from the SQLite database or exported CSVs.

## Version 2

- Add data validation tests.
- Add pipeline logging.
- Add currency/date standardization.
- Add monthly growth and repeat customer calculations.
- Add YAML data contracts for schemas, ID formats, dates, ranges, allowed values, duplicate keys, and foreign keys.
- Add full and incremental pipeline modes.
- Add pipeline run metadata and run summaries.

## Version 3

- Move from SQLite to PostgreSQL.
- Add orchestration with Prefect or Airflow.
- Add dashboard screenshots and final case-study README.

## Current CV-Ready Version

- Full refresh mode rebuilds trusted warehouse tables from raw exports.
- Incremental mode loads only unseen primary keys and keeps reruns idempotent.
- Data quality outputs show rejected rows, issue types, clean rates, and quality scores.
- Streamlit is the main recruiter dashboard; Tableau and Power BI remain optional later versions.
