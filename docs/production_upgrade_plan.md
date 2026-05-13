# Production Upgrade Plan

Goal: make the flagship project look closer to a junior data engineering work sample without overengineering it.

## Priority 1: Live Proof

- Deploy Streamlit demo.
- Add final demo URL to README.
- Add demo URL to GitHub profile README.
- Record a short walkthrough after deployment.

Done when: a recruiter can open one link and see the dashboard.

## Priority 2: dbt-Style SQL Layer

Status: first version added.

- Added a `models/` folder with staging, intermediate, and mart SQL files.
- Added `models/schema.yml` with dbt-style docs/tests.
- Added `retail-kpi run-models`.
- Added tests proving model views build and reconcile to warehouse revenue.
- Added `docs/analytics_models.md`.

Done when: SQL transformations look organized like analytics engineering work.

## Priority 3: Orchestration Example

- Added a lightweight Airflow example that runs:
  - generate data
  - validate contracts
  - run full pipeline
  - build analytics models
  - run KPI exports
- Keep it optional so the main project remains easy to run.

Done when: the repo shows scheduling concepts without making local setup painful.

## Priority 4: PostgreSQL Option

- Add a Docker Compose service for Postgres.
- Add a short design note comparing SQLite vs Postgres.
- Keep SQLite as default.

Done when: the project can explain production tradeoffs.

## Priority 5: Monitoring And Alerts

- Add freshness checks for KPI exports.
- Add row-count trend checks.
- Add a failure report example.
- Add a dashboard tile for latest pipeline status.

Done when: the project shows reliability, not only happy-path ETL.

## Resume Bullet After Upgrade

Extended a retail ETL project with dbt-style SQL models, optional orchestration, data freshness checks, Dockerized runs, and CI validation for KPI accuracy and pipeline reliability.
