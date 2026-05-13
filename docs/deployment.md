# Streamlit Deployment Guide

Use Streamlit Community Cloud to create a public demo link for recruiters.

Live demo: https://ahmed-retail-kpi-dashboard.streamlit.app/

## Prerequisites

- GitHub repo is public: `https://github.com/HaloXD1/data-pipeline-kpi-dashboard`
- App file: `app/streamlit_dashboard.py`
- Python dependencies are installable from `requirements.txt`
- Runtime file: `runtime.txt`

The app bootstraps demo outputs when KPI CSV files are missing, so ignored generated files do not need to be committed.

## Deploy Steps

1. Go to `https://share.streamlit.io/`.
2. Sign in with GitHub.
3. Click `Create app`.
4. Choose `Deploy a public app from GitHub`.
5. Select repository:
   `HaloXD1/data-pipeline-kpi-dashboard`
6. Select branch:
   `main`
7. Set main file path:
   `app/streamlit_dashboard.py`
8. Click `Deploy`.

## After Deployment

The live URL is already added to:

- GitHub repo README
- GitHub profile README

Manual follow-up:

- Add it to LinkedIn featured/projects section.

## Suggested Demo Text

Retail KPI dashboard demo built with Python, pandas, SQL, SQLite, YAML data contracts, and Streamlit. The project generates messy retail exports, validates and cleans the data, loads KPI-ready warehouse tables, tracks pipeline run quality, and visualizes revenue, margin, customer, product, returns, and data-quality performance.

## Docker

Run dashboard:

```bash
docker compose up dashboard
```

Run pipeline:

```bash
docker compose run --rm pipeline retail-kpi run-pipeline --mode full
```
