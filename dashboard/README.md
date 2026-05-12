# Dashboard

Streamlit is the main recruiter dashboard. Tableau and Power BI remain optional secondary versions.

Use the exported CSV files from:

```text
data/processed/dashboard_exports/
```

Current Streamlit tabs:

- Executive Overview
- Sales Trends
- Product Performance
- Customer Analysis
- Data Quality

The dashboard calls the demo bootstrapper on startup. If exports are missing, it generates synthetic raw files, runs the pipeline, verifies the outputs, and then loads the dashboard CSVs.

Recommended Tableau or Power BI pages:

- Executive Overview
- Sales Trends
- Product Performance
- Customer Analysis
- Returns and Data Quality

Add screenshots to:

```text
dashboard/screenshots/
```

Current preview:

- `screenshots/streamlit_dashboard.png`
- `screenshots/executive_overview_preview.svg`

Power BI can be added later under:

```text
dashboard/powerbi/
```
