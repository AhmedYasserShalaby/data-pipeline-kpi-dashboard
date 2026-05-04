# Streamlit Deployment Guide

Use Streamlit Community Cloud to create a public demo link for recruiters.

## Prerequisites

- GitHub repo is public: `https://github.com/HaloXD1/data-pipeline-kpi-dashboard`
- App file: `app/streamlit_dashboard.py`
- Python dependencies are in `pyproject.toml`

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

Add the live URL to:

- GitHub repo README
- GitHub profile README
- CV project line if space allows
- LinkedIn featured/projects section

## Suggested Demo Text

Retail KPI Dashboard demo built with Python, pandas, SQL, SQLite, and Streamlit. The project generates messy retail exports, cleans and validates the data, loads KPI-ready tables, and visualizes revenue, margin, customer, product, and returns performance.
